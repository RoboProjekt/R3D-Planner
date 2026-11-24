"""Color a saved Hesai XYZ map using synchronized RGB images and measured camera depth."""
import argparse
from collections import defaultdict
from contextlib import closing
import json
from pathlib import Path
import struct
import tempfile

import cv2
import numpy as np
from rclpy.serialization import deserialize_message
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import CameraInfo, Image, PointCloud2
from tf2_msgs.msg import TFMessage

from correct_lio_drift import PoseTrack, apply_pose
from inspect_bags import field_array, stamp_ns
from prepare_l1_ab import open_bag


def load_xyz(path):
    with path.open('rb') as file:
        header = {}
        for line in file:
            key, _, value = line.rstrip().partition(b' ')
            header[key] = value
            if key == b'DATA':
                break
        if any(header.get(key) != val for key, val in {
                b'FIELDS': b'x y z', b'SIZE': b'4 4 4', b'TYPE': b'F F F',
                b'COUNT': b'1 1 1', b'DATA': b'binary'}.items()):
            raise ValueError('Expected the binary XYZ PCD exported by the mapper')
        xyz = np.fromfile(file, '<f4').reshape(int(header[b'POINTS']), 3)
    if not np.isfinite(xyz).all() or not len(xyz):
        raise ValueError('Map has invalid XYZ')
    return xyz


def write_rgb(path, xyz, rgb, views):
    fields = [('x','<f4'),('y','<f4'),('z','<f4'),('rgb','<f4'),('views','<u2')]
    data = np.empty(len(xyz), dtype=fields)
    for i, name in enumerate('xyz'):
        data[name] = xyz[:,i]
    rgb = rgb.astype(np.uint32)
    data['rgb'] = ((rgb[:,0] << 16) | (rgb[:,1] << 8) | rgb[:,2]).view('f4')
    data['views'] = views
    with path.open('wb') as file:
        file.write(('# .PCD v0.7\nVERSION 0.7\nFIELDS x y z rgb views\nSIZE 4 4 4 4 2\n'
                    'TYPE F F F F U\nCOUNT 1 1 1 1 1\n'
                    f'WIDTH {len(xyz)}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n'
                    f'POINTS {len(xyz)}\nDATA binary\n').encode())
        data.tofile(file)


def static_tree(db, topic):
    edges = defaultdict(dict)
    for (payload,) in db.execute('SELECT data FROM messages WHERE topic_id=?', (topic,)):
        for tr in deserialize_message(payload, TFMessage).transforms:
            a, b = tr.header.frame_id, tr.child_frame_id
            q, v = tr.transform.rotation, tr.transform.translation
            transform = np.eye(4)
            transform[:3,:3] = Rotation.from_quat([q.x,q.y,q.z,q.w]).as_matrix()
            transform[:3,3] = [v.x,v.y,v.z]
            if b in edges[a] and not np.allclose(edges[a][b], transform, atol=1e-6):
                raise ValueError(f'Conflicting static transforms for {b}')
            edges[a][b] = transform
            edges[b][a] = np.linalg.inv(transform)
    return edges


def relative(edges, parent, child):
    pending = [(parent, np.eye(4))]
    seen = {parent}
    for frame, transform in pending:
        if frame == child:
            return transform
        for neighbour, edge in edges[frame].items():
            if neighbour not in seen:
                seen.add(neighbour)
                pending.append((neighbour, transform @ edge))
    raise ValueError(f'No recorded TF chain from {parent} to {child}')


def frame_index(db, topic, start_ns, end_ns):
    # Only read the fixed CDR prefix of messages beginning with std_msgs/Header.
    rows = []
    for row, header in db.execute('SELECT id,substr(data,1,12) FROM messages WHERE topic_id=?', (topic,)):
        if header[:2] not in (b'\x00\x01', b'\x00\x00'):
            raise ValueError('Expected ROS 2 CDR header')
        sec, ns = struct.unpack_from('<iI' if header[1] else '>iI', header, 4)
        stamp = sec*1000000000+ns
        if start_ns <= stamp <= end_ns:
            rows.append((stamp,row))
    return sorted(rows)


def synchronize(rgb, depth, max_skew_ns=20_000_000):
    if not rgb or not depth:
        return []
    times = np.array([t for t,_ in rgb], dtype='i8')
    pairs = []
    for td, key in depth:
        i = int(np.searchsorted(times, td))
        j = min(range(max(0,i-1),min(i+1,len(rgb))), key=lambda k: abs(int(times[k])-td))
        if abs(td-rgb[j][0]) <= max_skew_ns:
            pairs.append((td,key,*rgb[j]))
    return pairs


def calibration(db, topic, depth=False, bounds=None):
    info = None
    signature = None
    for payload, in db.execute('SELECT data FROM messages WHERE topic_id=?', (topic,)):
        msg = deserialize_message(payload, CameraInfo)
        if bounds and not bounds[0] <= stamp_ns(msg.header.stamp) <= bounds[1]:
            continue
        current = (msg.header.frame_id, msg.width, msg.height, msg.distortion_model,
                   tuple(msg.k), tuple(msg.p), tuple(msg.d), msg.binning_x, msg.binning_y,
                   msg.roi.x_offset, msg.roi.y_offset, msg.roi.width, msg.roi.height)
        if signature is not None and current != signature:
            raise ValueError('Camera intrinsics changed during the selected trajectory')
        info, signature = msg, current
        if bounds is None:
            break
    if info is None:
        raise ValueError('Missing camera intrinsics in the mapping interval')
    k = np.array(info.p).reshape(3,4)[:,:3] if depth else np.array(info.k).reshape(3,3)
    if k[0,0] <= 0 or k[1,1] <= 0 or info.width <= 0 or info.height <= 0:
        raise ValueError('Invalid camera intrinsics')
    if not depth and info.distortion_model not in ('plumb_bob', 'rational_polynomial', ''):
        raise ValueError(f'Unsupported RGB distortion: {info.distortion_model}')
    return info.header.frame_id, (info.width, info.height, k, None if depth or not np.any(info.d) else np.asarray(info.d))


def pixels(pts, camera):
    _, _, k, distortion = camera
    if not len(pts):
        return np.empty((0, 2))
    if distortion is None:
        u = pts[:,0]*k[0,0]/pts[:,2] + k[0,2]
        v = pts[:,1]*k[1,1]/pts[:,2] + k[1,2]
        return np.column_stack((u,v))
    uv,_ = cv2.projectPoints(pts, np.zeros(3), np.zeros(3), k, distortion)
    return uv.reshape(-1,2)


def inside(uv, width, height):
    return (uv[:,0]>=0)&(uv[:,0]<width)&(uv[:,1]>=0)&(uv[:,1]<height)


def depth_buffer(points, camera, scale=1):
    width,height = camera[:2]
    buf = np.full(((height+scale-1)//scale,(width+scale-1)//scale), np.inf, dtype='f4')
    points = points[points[:,2]>.1]
    if len(points):
        uv = np.rint(pixels(points,camera)).astype('i4')
        ok = inside(uv,width,height)
        u,v = (uv[ok]//scale).T
        np.minimum.at(buf,(v,u),points[ok,2])
    return buf


class ColorMap:
    def __init__(self, points):
        self.points = points
        spacing = .65
        cells,inverse = np.unique(np.floor(points/spacing).astype('i4'),axis=0,return_inverse=True)
        self.centres = (cells+.5)*spacing
        self.cell_radius = .5*np.sqrt(3)*spacing
        order = np.argsort(inverse,kind='stable')
        self.buckets = np.split(order,np.cumsum(np.bincount(inverse))[:-1])
        self.rgb = np.full((len(points),3),128,dtype='u1')
        self.views = np.zeros(len(points),dtype='u2')
        self.best = np.full(len(points),np.inf,dtype='f4')

    def observe(self, depth, picture, world_depth, world_color, dcam, ccam, max_range):
        # Frustum test on bounding spheres first. Always project the original map points.
        depth_world = np.linalg.inv(world_depth)
        color_world = np.linalg.inv(world_color)
        centres = apply_pose(depth_world,self.centres)
        x,y,z = centres.T
        pad = self.cell_radius
        w,h,k,_ = dcam
        slope_x = max(k[0,2],w-k[0,2])/k[0,0]
        slope_y = max(k[1,2],h-k[1,2])/k[1,1]
        use = ((z+pad>.30)&(z-pad<max_range)&(abs(x)<slope_x*(z+pad)+pad)&
               (abs(y)<slope_y*(z+pad)+pad))
        if not use.any() or not len(depth):
            return
        ids = np.concatenate([self.buckets[i] for i in np.flatnonzero(use)])
        q = apply_pose(depth_world,self.points[ids])
        good = (q[:,2]>.30)&(q[:,2]<max_range)
        ids,q = ids[good],q[good]
        if not len(q):
            return
        uv = np.rint(pixels(q,dcam)).astype('i4')
        good = inside(uv,w,h)
        uv,q,ids = uv[good],q[good],ids[good]
        u,v = uv.T
        buf = depth_buffer(depth,dcam)
        error = abs(buf[v,u]-q[:,2])
        tol = .032+.014*q[:,2]
        near = cv2.erode(buf,np.ones((3,3),'u1'))[v,u]
        good = (error<=tol)&(q[:,2]<=near+tol)
        ids,q,error,tol = ids[good],q[good],error[good],tol[good]
        if not len(ids):
            return
        color_depth = color_world @ world_depth
        qc = apply_pose(color_depth,q)
        forward = qc[:,2]>.1
        ids,qc,error,tol = ids[forward],qc[forward],error[forward],tol[forward]
        uv = np.rint(pixels(qc,ccam)).astype('i4')
        good = inside(uv,*ccam[:2])
        ids,qc,uv,error,tol = ids[good],qc[good],uv[good],error[good],tol[good]
        if not len(ids):
            return
        # A separate z-buffer catches silhouettes displaced by the RGB/depth baseline.
        rgb_depth = depth_buffer(apply_pose(color_depth,depth),ccam,scale=3)
        u,v = uv.T
        nearest = cv2.erode(rgb_depth,np.ones((3,3),'u1'))[v//3,u//3]
        good = np.isfinite(nearest)&(qc[:,2]<=nearest+tol)
        ids,uv,qc,error,tol = ids[good],uv[good],qc[good],error[good],tol[good]
        self.views[ids] = np.minimum(self.views[ids].astype('i4')+1,65535)
        off_axis = np.linalg.norm(qc[:,:2],axis=1)/qc[:,2]
        cost = error/tol + .16*qc[:,2]+.45*off_axis
        win = cost<self.best[ids]
        u,v = uv[win].T
        self.rgb[ids[win]] = picture[v,u]
        self.best[ids[win]] = cost[win]


def camera_points(msg):
    xyz = {f.name:f for f in msg.fields}
    points = np.column_stack([field_array(msg,xyz[n]).ravel() for n in 'xyz'])
    return points[np.isfinite(points).all(axis=1)&(points[:,2]>.1)]


def rgb_array(msg):
    if msg.encoding not in ('rgb8','bgr8'):
        raise ValueError(f'Unsupported image encoding: {msg.encoding}')
    image = np.ndarray((msg.height,msg.width,3),dtype='u1',buffer=msg.data,strides=(msg.step,3,1))
    return image if msg.encoding=='rgb8' else image[:,:,::-1]


def read_message(db, row, cls):
    payload, = db.execute('SELECT data FROM messages WHERE id=?', (int(row),)).fetchone()
    return deserialize_message(payload, cls)


def projection_calibration(run, db, track, start, depths, dcam, dframe, lidar_depth):
    from lidar_camera_calibration import geometry_sample, refine_mount
    with np.load(run/'outputs.npz') as data:
        scans = data['registered_points']
        offsets = data['cloud_offsets']
        stamps = data['cloud_stamps']
    times = np.array([td for td, _ in depths])*1e-9
    near = np.searchsorted(stamps, times).clip(0, len(stamps)-1)
    prev = np.maximum(0, near-1)
    near = np.where(abs(stamps[prev]-times) < abs(stamps[near]-times), prev, near)
    skew = abs(stamps[near]-times)
    records = []
    candidates = set()
    for centre in np.linspace(times[0], times[-1], min(64, len(times))):
        window = np.flatnonzero((abs(times-centre) < .45) & (skew < .04))
        if len(window):
            candidates.add(int(window[skew[window].argmin()]))
    for i in sorted(candidates):
        msg = read_message(db, depths[i][1], PointCloud2)
        if msg.header.frame_id != dframe or (msg.width, msg.height) != dcam[:2]:
            continue
        fields = {f.name: f for f in msg.fields}
        grid = np.stack([field_array(msg,fields[k]) for k in 'xyz'],axis=1).reshape(msg.height,msg.width,3)
        valid = grid[np.isfinite(grid).all(axis=2)]
        world_depth = track.at([times[i]-start])[0] @ lidar_depth
        j = near[i]
        query = apply_pose(np.linalg.inv(world_depth), scans[offsets[j]:offsets[j+1]])
        sample = geometry_sample(query, grid, depth_buffer(valid, dcam))
        if sample is not None:
            records.append(sample)
    return refine_mount(records, dcam)


def colorize(run, map_file, output, bag, prefix, max_range, refine=False):
    if output.exists():
        raise FileExistsError(output)
    metadata = json.loads((run/'metrics.json').read_text())
    if metadata.get('map_frame') != 'building_level' or not 0.3 < max_range <= 20:
        raise ValueError('Expected a building-level map and a camera depth limit between 0.3 and 20 m')
    with np.load(run/'outputs.npz') as data:
        trajectory = data['trajectory']
    start,end = trajectory[[0,-1],0]
    atlas = ColorMap(load_xyz(map_file))
    track = PoseTrack(trajectory,start)
    bag = bag or Path(metadata['bag'])
    with closing(open_bag(bag)[0]) as db:
        topics = dict(db.execute('SELECT name,id FROM topics'))
        edges = static_tree(db,topics['/tf_static'])
        bounds = (int(np.ceil(start*1e9)),int(np.floor(end*1e9)))
        dframe,dcam = calibration(db,topics[prefix+'/depth/camera_info'],True,bounds)
        cframe,ccam = calibration(db,topics[prefix+'/color/camera_info'],bounds=bounds)
        lidar_depth = relative(edges,metadata['frame'],dframe)
        lidar_color = relative(edges,metadata['frame'],cframe)
        depths = frame_index(db,topics[prefix+'/depth/points'],*bounds)
        photos = frame_index(db,topics[prefix+'/color/image_raw'],*bounds)
        pairs = synchronize(photos,depths)
        if not pairs:
            raise ValueError('No synchronized RGB and depth observations on this trajectory')
        calibration_report = {'applied':False}
        if refine:
            correction, calibration_report = projection_calibration(run, db, track, start, depths, dcam,
                                                                    dframe, lidar_depth)
            depth_color = np.linalg.solve(lidar_depth, lidar_color)
            lidar_depth = lidar_depth @ np.linalg.inv(correction)
            lidar_color = lidar_depth @ depth_color
        print(f'{len(pairs)} synchronized pairs; projection calibration: {calibration_report}', flush=True)
        times = np.array([td for td,_,_,_ in pairs])*1e-9-start
        rgb_times = np.array([tc for _,_,tc,_ in pairs])*1e-9-start
        poses = track.at(times); rgb_poses = track.at(rgb_times)
        used = []; last = None
        for i,(td,depth_id,tc,img_id) in enumerate(pairs):
            if last is not None:
                dt = times[i]-times[last]
                rotation = Rotation.from_matrix(poses[i,:3,:3].T @ poses[last,:3,:3]).magnitude()
                move = np.linalg.norm(poses[i,:3,3]-poses[last,:3,3])
                if dt<.10 or (dt<1.5 and move<.10 and rotation<np.deg2rad(4.)):
                    continue
            depth_msg = read_message(db,depth_id,PointCloud2)
            image_msg = read_message(db,img_id,Image)
            if (depth_msg.header.frame_id != dframe or image_msg.header.frame_id != cframe or
                    stamp_ns(depth_msg.header.stamp)!=td or stamp_ns(image_msg.header.stamp)!=tc or
                    (image_msg.width,image_msg.height)!=ccam[:2]):
                raise ValueError('Image/cloud frame, timestamp or camera resolution mismatch')
            atlas.observe(camera_points(depth_msg),rgb_array(image_msg),poses[i]@lidar_depth,
                          rgb_poses[i]@lidar_color,dcam,ccam,max_range)
            last=i
            used.append(abs(td-tc)*1e-6)
            if len(used)%200==0:
                print(f'{len(used)} RGB-D views, {np.count_nonzero(atlas.views):,} colored points',flush=True)
    painted = atlas.views>0
    if not painted.any():
        raise ValueError('Camera depth did not agree with the map in any view')
    report = dict(source=str(map_file.resolve()), bag=str(bag.resolve()), map_frame='building_level',
                  points=len(atlas.points), rgb_points=int(painted.sum()), unseen_gray=int((~painted).sum()),
                  multiple_views=int((atlas.views>=2).sum()), rgb_images=len(photos),depth_clouds=len(depths),
                  paired=len(pairs),used=len(used),max_skew_ms=max(used),median_skew_ms=float(np.median(used)),
                  max_camera_z_m=max_range, lidar_frame=metadata['frame'], color_frame=cframe,depth_frame=dframe,
                  projection_calibration=calibration_report,
                  lidar_from_depth=lidar_depth.tolist(),lidar_from_color=lidar_color.tolist())
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        stage = Path(tmp)/'result'; stage.mkdir()
        write_rgb(stage/'karte_rgb.pcd',atlas.points,atlas.rgb,atlas.views)
        (stage/'metrics.json').write_text(json.dumps(report,indent=2)+'\n')
        stage.rename(output)
    print(json.dumps({k:report[k] for k in ('points','rgb_points','unseen_gray','paired','used','max_skew_ms')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path,help='Mapper run with trajectory and metrics')
    parser.add_argument('map_file',type=Path,help='Its dense XYZ map in building coordinates')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--bag',type=Path,help='Override the bag location stored in the run')
    parser.add_argument('--camera',default='/go2_unit_14082')
    parser.add_argument('--max-depth',type=float,default=6.)
    parser.add_argument('--refine-extrinsics', action='store_true',
                        help='Refine the RGB overlay only if held-out camera depths agree better with the LiDAR')
    args=parser.parse_args()
    colorize(args.run,args.map_file,args.output,args.bag,args.camera.rstrip('/'),args.max_depth,args.refine_extrinsics)
