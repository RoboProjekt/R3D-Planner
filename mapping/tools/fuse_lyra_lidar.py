"""Map localized Lyra splats onto measured LiDAR surface patches of the same building."""
import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from plyfile import PlyData, PlyElement
from scipy.spatial import cKDTree

from reconstruct_lyra_route import registered_depth


BASE = np.dtype([(k, '<f4') for k in ('x', 'y', 'z', 'rgb')] + [('views', '<u2')])
OUTPUT = np.dtype(BASE.descr + [('source', 'u1'), ('color_source', 'u1'), ('lyra_support', '<u2')])
VOXEL = .02
MAX_NEAREST = .05
MAX_PLANE = .025


def read_pcd(path, dtype):
    with path.open('rb') as file:
        header = {}
        for line in file:
            key, _, value = line.strip().partition(b' ')
            header[key] = value
            if key == b'DATA':
                break
        names = tuple(header[b'FIELDS'].decode().split())
        expected_sizes = [dtype[k].itemsize for k in names] if names == dtype.names else []
        expected_types = ['F' if dtype[k].kind == 'f' else 'U' for k in dtype.names]
        if (names != dtype.names or header[b'DATA'] != b'binary' or
                list(map(int, header[b'SIZE'].split())) != expected_sizes or
                header[b'TYPE'].decode().split() != expected_types or
                any(int(x) != 1 for x in header[b'COUNT'].split())):
            raise ValueError(f'Unexpected PCD layout in {path}')
        count = int(header[b'POINTS'])
        if path.stat().st_size - file.tell() != count*dtype.itemsize:
            raise ValueError(f'Incorrect PCD payload size in {path}')
        return np.memmap(path, mode='r', offset=file.tell(), dtype=dtype, shape=(count,))


def write_pcd(path, data):
    names = data.dtype.names
    lines = ['# .PCD v0.7', 'VERSION 0.7', 'FIELDS '+' '.join(names),
             'SIZE '+' '.join(str(data.dtype[n].itemsize) for n in names),
             'TYPE '+' '.join('F' if data.dtype[n].kind=='f' else 'U' for n in names),
             'COUNT '+' '.join('1' for _ in names), f'WIDTH {len(data)}', 'HEIGHT 1',
             'VIEWPOINT 0 0 0 1 0 0 0', f'POINTS {len(data)}', 'DATA binary']
    with path.open('wb') as file:
        file.write(('\n'.join(lines)+'\n').encode())
        data.tofile(file)


def xyz(records):
    return np.column_stack([records[k] for k in 'xyz'])


def splat_rgb(splats, indices):
    sh = np.column_stack([splats[f'f_dc_{j}'][indices] for j in range(3)])
    return np.rint(255*np.clip(.5 + .28209479177387814*sh, 0, 1)).astype('u1')


def write_centers(path, splats):
    """Plain XYZ/RGB PLY for inspecting all centres in conventional point-cloud viewers."""
    schema = [(k, '<f4') for k in 'xyz'] + [(k, 'u1') for k in ('red','green','blue')] + [('opacity','<f4')]
    points = np.empty(len(splats), dtype=schema)
    for k in 'xyz':
        points[k] = splats[k]
    rgb = splat_rgb(splats, slice(None))
    for i,k in enumerate(('red','green','blue')):
        points[k] = rgb[:,i]
    points['opacity'] = 1/(1+np.exp(-splats['opacity']))
    PlyData([PlyElement.describe(points,'vertex')], byte_order='<',
            comments=['frame building_level, units m', 'Estimated Gaussian centres, RGB from SH0']).write(str(path))


def project_patches(points, lidar, tree):
    """Interpolate only inside the support polygon of one locally flat LiDAR patch."""
    ids, projected = [], []
    for start in range(0, len(points), 20000):
        chunk = points[start:start+20000]
        dist, idx = tree.query(chunk, k=12, distance_upper_bound=.12, workers=6)
        keep = np.flatnonzero((dist[:, 0] <= MAX_NEAREST) & np.isfinite(dist[:, -1]))
        if not len(keep):
            continue
        support = lidar[idx[keep]].astype('f8')
        mean = support.mean(axis=1)
        centered = support - mean[:, None]
        values, axes = np.linalg.eigh(centered.transpose(0,2,1) @ centered / support.shape[1])
        normal = axes[:,:,0]
        delta = np.sum((chunk[keep]-mean)*normal, axis=1)
        target = chunk[keep] - delta[:,None]*normal
        # Angular coverage excludes extrapolation across a step edge or wall ending.
        tangent = (support - target[:,None]) @ axes[:,:,1:]
        angles = np.sort(np.arctan2(tangent[:,:,1], tangent[:,:,0]), axis=1)
        largest_gap = np.diff(angles, axis=1, append=angles[:,:1]+2*np.pi).max(axis=1)
        valid = ((values[:,1] > 1e-6) & (values[:,1] > .09*values[:,2]) &
                 (values[:,0] < .10*values[:,1]) &
                 (abs(centered @ normal[:,:,None]).max(axis=(1,2)) <= .018) &
                 (abs(delta) <= MAX_PLANE) & (largest_gap < np.pi))
        ids.append(start+keep[valid])
        projected.append(target[valid].astype('f4'))
    if not ids or not any(len(x) for x in ids):
        raise ValueError('No measured surface patches overlap the supplied splats')
    return np.concatenate(ids), np.concatenate(projected)


def depth_support(points, cameras, depth):
    """Confirm a surface against separated RGB-D viewpoints in the LiDAR map frame."""
    indices = cameras['source_frame_id']
    w2c = cameras['w2c']
    intr = cameras['intrinsics']
    size = (int(cameras['image_width']), int(cameras['image_height']))
    raw, poses, kd = depth['depth_mm'], depth['poses'], depth['K']
    hits = np.zeros(len(points), np.uint16)
    last_eye = np.full_like(points, np.nan)
    tree = cKDTree(points)
    for i in range(len(indices)):
        if i % 10 == 5:  # The Lyra evaluation frames remain unused.
            continue
        frame = indices[i]
        measured = registered_depth(raw[frame], kd, intr[i], w2c[i]@poses[frame], size)
        eye = np.linalg.inv(w2c[i])[:3,3]
        ids = np.asarray(tree.query_ball_point(eye, 6.), dtype=np.intp)
        camera = points[ids] @ w2c[i,:3,:3].T + w2c[i,:3,3]
        keep = (camera[:,2] > .35) & (camera[:,2] < 5.)
        ids, camera = ids[keep], camera[keep]
        uvz = camera @ intr[i].T
        u, v = np.rint(uvz[:,:2] / uvz[:,2,None] / 2).astype(int).T
        valid = (u>=0)&(v>=0)&(u<measured.shape[1])&(v<measured.shape[0])
        ids, z = ids[valid], camera[valid,2]
        dz = measured[v[valid], u[valid]]
        ids = ids[(dz>0) & (abs(dz-z) <= .04 + .01*z)]
        # Adjacent frames at one stationary position count as one observation.
        separated = (hits[ids]==0) | (np.linalg.norm(eye-last_eye[ids], axis=1) >= .15)
        accepted = ids[separated]
        hits[accepted] += 1
        last_eye[accepted] = eye
    return hits


def cell_ids(points):
    cells = np.ascontiguousarray(np.floor(points/VOXEL).astype('<i4'))
    return cells.view('V12').ravel()


def quantiles(values):
    return dict(zip(('p50','p90'), map(float,np.percentile(values,[50,90]))))


def fuse(args):
    base = read_pcd(args.lidar, BASE)
    lidar = xyz(base)
    splats = PlyData.read(str(args.splats))['vertex']
    centers = xyz(splats)
    if not np.isfinite(lidar).all() or not np.isfinite(centers).all():
        raise ValueError('Invalid coordinates in inputs')
    tree = cKDTree(lidar)
    probe = np.random.default_rng(23).choice(len(centers), min(50000,len(centers)), replace=False)
    raw_dist = tree.query(centers[probe], workers=6)[0]
    opacity = 1/(1 + np.exp(-splats['opacity']))
    log_radius = np.maximum.reduce([splats[f'scale_{j}'] for j in range(3)])
    candidates = np.flatnonzero((opacity>=.12) & (log_radius<=np.log(.10)))
    local, projected = project_patches(centers[candidates], lidar, tree)
    with np.load(args.cameras) as cameras, np.load(args.depth) as depth:
        support = depth_support(projected, cameras, depth)
    valid = support>=2
    ids, points, hits = candidates[local[valid]], projected[valid], support[valid]
    if not len(points):
        raise ValueError('No overlapping points confirmed by two depth views')
    rgb = splat_rgb(splats, ids).astype(np.uint32)
    packed = ((rgb[:,0]<<16) | (rgb[:,1]<<8) | rgb[:,2]).view('<f4')
    nearest, neighbor = tree.query(points, workers=6)
    # Do not create another point in a measured cell, or within 12 mm of a return.
    cell = cell_ids(points)
    low, high = points.min(axis=0)-VOXEL, points.max(axis=0)+VOXEL
    local_lidar = lidar[((lidar>=low)&(lidar<=high)).all(axis=1)]
    empty = ~np.isin(cell, np.unique(cell_ids(local_lidar)))
    available = np.flatnonzero(empty & (nearest>=.012) & (nearest<=MAX_NEAREST))
    ranking = np.lexsort((-opacity[ids[available]], -hits[available].astype(int)))
    available = available[ranking]
    _, unique = np.unique(cell[available], return_index=True)
    added = available[unique]
    # Measured RGB wins. Only fill an uncolored measured return from the closest confirmed splat.
    color = np.flatnonzero((base['views'][neighbor]==0) & (nearest<=.020))
    color = color[np.argsort(nearest[color], kind='stable')]
    _, first = np.unique(neighbor[color], return_index=True)
    color = color[first]
    target = neighbor[color]
    result = np.zeros(len(base)+len(added), dtype=OUTPUT)
    original, extra = result[:len(base)], result[len(base):]
    for key in BASE.names:
        original[key] = base[key]
    original['color_source'] = base['views']>0
    original['rgb'][target] = packed[color]
    original['color_source'][target] = 2
    original['lyra_support'][target] = hits[color]
    for j, key in enumerate('xyz'):
        extra[key] = points[added,j]
    extra['source'], extra['color_source'] = 1, 2
    extra['rgb'], extra['lyra_support'] = packed[added], hits[added]
    report = dict(map_frame='building_level',map_units='m',lidar=str(args.lidar),splat_ply=str(args.splats),
                  lidar_points=len(base),splats=len(centers),shape_opacity_candidates=len(candidates),
                  on_measured_patches=len(projected),also_depth_confirmed=len(points),
                  lidar_recolored_only_if_no_camera_rgb=len(color),interpolated_points=len(added),
                  output_points=len(result),raw_center_to_lidar_sample_size=len(probe),
                  raw_center_to_lidar_m=quantiles(raw_dist),raw_centers_within_5cm=float(np.mean(raw_dist<=.05)),
                  source={'0':'LiDAR map point','1':'Lyra centre projected onto a locally supported LiDAR plane'},
                  color_source={'0':'no measured color','1':'previous RGB camera color','2':'Lyra SH0 color'},
                  views='Original camera RGB observation count for measured LiDAR points; zero for interpolated points.',
                  lyra_support='Matching depth views for accepted Lyra color or geometry; successive counted camera positions at least 0.15 m apart.',
                  filters=dict(min_opacity=.12, max_splat_std_m=.10,max_nearest_m=MAX_NEAREST,
                               local_lidar_points=12, max_patch_radius_m=.12,max_neighbor_plane_residual_m=.018,
                               max_projection_m=MAX_PLANE, min_depth_views=2,max_camera_depth_m=5.,
                               depth_tolerance_m='0.04 + 0.01*z', cell_m=VOXEL))
    if len(added):
        report['added_to_nearest_lidar_m'] = quantiles(nearest[added])
        report['added_projection_m'] = quantiles(np.linalg.norm(points[added]-centers[ids[added]],axis=1))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with TemporaryDirectory(dir=args.output.parent) as folder:
        tmp = Path(folder)/'fusion'
        tmp.mkdir()
        cloud = tmp/'karte_fusion.pcd'
        write_pcd(cloud, result)
        write_centers(tmp/'lyra_zentren_rgb.ply', splats)
        check = read_pcd(cloud, OUTPUT)
        if len(check)!=len(result) or not np.array_equal(check,result):
            raise ValueError('Export validation failed')
        (tmp/'Pruefung.json').write_text(json.dumps(report,indent=2)+'\n')
        tmp.rename(args.output)
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    p.add_argument('--lidar',type=Path,default=Path('reports/20261123_kamerakarte/karte_rgb.pcd'))
    p.add_argument('--splats',type=Path,default=Path('reports/20261123_lyra_detail/Treppe_Flur.ply'))
    p.add_argument('--cameras',type=Path,default=Path('reports/20261123_lyra_detail/Kameraposen.npz'))
    p.add_argument('--depth',type=Path,default=Path('.runtime/mesh_fusion/rgbd_1118.npz'))
    args=p.parse_args()
    if args.output.exists():
        p.error('Use a fresh output directory')
    fuse(args)
