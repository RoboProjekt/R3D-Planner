#!/usr/bin/env python3
"""Build a 3D map directly from a Hesai PointCloud2 stream using LiDAR-only odometry."""
import argparse
from contextlib import closing
from importlib.metadata import version
import json
from pathlib import Path
import tempfile

import numpy as np
from scipy.spatial.transform import Rotation
from kiss_icp.config import load_config
from kiss_icp.kiss_icp import KissICP
from kiss_icp.voxelization import voxel_down_sample
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import PointCloud2

from correct_lio_drift import PoseTrack, apply_pose, write_pcd
from inspect_bags import field_array
from prepare_l1_ab import HESAI, open_bag


def rotational_phase(xyz, rings):
    """Estimate firing order only for complete, ordered Hesai XT16 firing blocks."""
    if not len(rings) or len(rings) % 16 or not np.all(rings.reshape(-1, 16) == np.arange(16)):
        return np.empty(0)
    xy = xyz[:, :2].reshape(-1, 16, 2)
    radii = np.nan_to_num(np.linalg.norm(xy, axis=2), nan=0., posinf=0.)
    best = radii.argmax(axis=1)
    block = np.flatnonzero(radii.max(axis=1) > .65)
    if len(block) < len(xy)*.7 or np.max(np.diff(block), initial=0) > len(xy)*.05:
        return np.empty(0)
    rays = xy[block, best[block]]
    azimuth = np.unwrap(np.arctan2(rays[:, 1], rays[:, 0]))
    span = azimuth[-1] - azimuth[0]
    if not (np.pi < abs(span) < 2.2*np.pi):
        return np.empty(0)
    progress = (azimuth-azimuth[0])/span
    if np.mean(np.diff(progress) < -.0001) > .025:
        return np.empty(0)
    return np.repeat(np.interp(np.arange(len(xy)), block, np.maximum.accumulate(progress)), 16)


def unpack_scan(msg):
    fields = {f.name: f for f in msg.fields}
    if any(k not in fields or fields[k].count != 1 for k in 'xyz'):
        raise ValueError('The LiDAR cloud must contain scalar x, y and z fields')
    xyz = np.column_stack([field_array(msg, fields[k]).ravel() for k in 'xyz'])
    valid = np.isfinite(xyz).all(axis=1)
    stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
    times = np.empty(0)
    timing = 'recorded'
    if 'timestamp' in fields:
        point_time = field_array(msg, fields['timestamp']).ravel()
        valid &= np.isfinite(point_time)
        if np.any(valid):
            times = point_time[valid].astype(float)
            lo, hi = float(times.min()), float(times.max())
            # These Hesai packets encode absolute firing time in seconds.
            if abs(hi - stamp) < .5:
                stamp = hi
            times = times - lo if 0 < hi - lo < .5 else np.empty(0)
    if not len(times):
        timing = 'rigid'
        if 'ring' in fields:
            phase = rotational_phase(xyz, field_array(msg, fields['ring']).ravel())
            if len(phase) and np.any(valid) and np.ptp(phase[valid]) > 0:
                times = phase[valid]
                timing = 'azimuth'
    return stamp, xyz[valid].astype(float), times, timing


class Mapper:
    def __init__(self, config):
        self.odometry = KissICP(config)
        self.config = config
        self.poses, self.clouds, self.cloud_times = [], [], []
        self.last_stamp = None
        self.frame = None
        self.skipped = 0
        self.rigid_scans = 0
        self.azimuth_scans = 0

    def add(self, msg):
        stamp, points, times, timing = unpack_scan(msg)
        if self.last_stamp is not None and stamp <= self.last_stamp:
            self.skipped += 1
            return None
        if self.frame is not None and msg.header.frame_id != self.frame:
            raise ValueError('LiDAR frame changed during mapping')
        radius = np.einsum('ij,ij->i', points, points)
        if np.count_nonzero((radius > self.config.data.min_range**2) &
                            (radius < self.config.data.max_range**2)) < 32:
            self.skipped += 1
            return None
        deskewed, _ = self.odometry.register_frame(points, times)
        pose = self.odometry.last_pose.copy()
        if not np.isfinite(pose).all():
            raise ValueError('Nonfinite LiDAR pose')
        self.frame, self.last_stamp = msg.header.frame_id, stamp
        self.rigid_scans += int(timing == 'rigid')
        self.azimuth_scans += int(timing == 'azimuth')
        self.poses.append(np.r_[stamp, pose[:3, 3], Rotation.from_matrix(pose[:3, :3]).as_quat()])
        if not self.cloud_times or stamp - self.cloud_times[-1] >= .24:
            xyz = voxel_down_sample(np.asarray(deskewed), .085)
            self.clouds.append(apply_pose(pose, xyz).astype('f4'))
            self.cloud_times.append(stamp)
        return pose

    def save(self, output, metadata, use_loops=True, level_floors=False):
        report = dict(metadata, estimator='kiss-icp', version=version('kiss-icp'),
                      parameters=self.config.model_dump(), frame=self.frame, scans=len(self.poses),
                      skipped=self.skipped, rigid_scans=self.rigid_scans, azimuth_scans=self.azimuth_scans,
                      recorded_timing_scans=len(self.poses)-self.azimuth_scans-self.rigid_scans,
                      sampled_clouds=len(self.clouds), map_frame='first_lidar_scan')
        export_map(output, report, np.asarray(self.poses), self.clouds, self.cloud_times, use_loops, level_floors)


def export_map(output, report, local_trajectory, clouds, cloud_times, use_loops, level_floors=False):
    if len(local_trajectory) < 2 or not len(clouds):
        raise ValueError('Too few valid scans to export a map')
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    trajectory = local_trajectory
    planes = {'applied': False}
    loops = {'status': 'disabled', 'loops': []}
    if use_loops:
        from lidar_revisits import close_loops
        if np.max(np.linalg.norm(trajectory[:, 1:4]-trajectory[0, 1:4], axis=1)) >= 3:
            from lidar_planes import constrain_planes, largest_vertical_gap
            trajectory, clouds, planes = constrain_planes(trajectory, clouds, cloud_times)
            planes['largest_vertical_gap'] = largest_vertical_gap(trajectory, planes.get('vertical_windows_s', []))
        trajectory, clouds, loops = close_loops(trajectory, clouds, cloud_times, planes,
                                                local_trajectory if planes['applied'] else None)
    alignment = 'pose_graph' if loops['status'] == 'pose_graph' else (
        'local_planes' if planes['applied'] else 'local_odometry')
    frame, map_from_first = 'first_lidar_scan', np.eye(4)
    floors = {'applied': False}
    if planes['applied']:
        from lidar_planes import level_map
        trajectory, clouds, map_from_first = level_map(trajectory, clouds, planes['building_up'])
        frame = 'building_level'
        if level_floors:
            from lidar_first_visit import first_visit_anchors
            from lidar_floor_surfaces import align_floor_surfaces
            revisits = loops['loops'] if loops['status'] == 'pose_graph' else []
            trajectory, clouds, floors = align_floor_surfaces(trajectory, clouds, cloud_times, revisits)
            trajectory, clouds, anchor_report = first_visit_anchors(trajectory, clouds, cloud_times, revisits)
            floors['first_visit'] = anchor_report
            floors['applied'] = floors['applied'] or anchor_report['applied']
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        stage = Path(tmp)/'result'
        stage.mkdir()
        points = np.concatenate(clouds)
        offsets = np.cumsum([0] + [len(c) for c in clouds])
        np.savez_compressed(stage/'outputs.npz', registered_points=points, cloud_offsets=offsets,
                            cloud_stamps=cloud_times, trajectory=trajectory, local_trajectory=local_trajectory)
        write_pcd(stage/'karte.pcd', voxel_down_sample(points.astype(float), .08))
        report = dict(report, loop_closure=loops, plane_constraints=planes, alignment=alignment,
                      floor_surfaces=dict(floors, enabled=level_floors),
                      map_frame=frame, local_trajectory_frame='first_lidar_scan',
                      map_from_first_lidar_scan=map_from_first.tolist())
        (stage/'metrics.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
        stage.rename(output)
    print(f"Saved {output/'karte.pcd'} from {len(trajectory)} scans ({alignment}).", flush=True)
    gap = planes.get('largest_vertical_gap')
    if gap:
        print(f"Longest path without a confirmed building vertical: {gap['travel_m']:.1f} m "
              f"({gap['start_s']:.1f} to {gap['end_s']:.1f} s).", flush=True)


def rebuild(run, output, use_loops, level_floors=False):
    report = json.loads((run/'metrics.json').read_text())
    if report.get('estimator') != 'kiss-icp' or 'recorded_timing_scans' not in report:
        raise ValueError('Rebuild needs a map exported by this Hesai mapper')
    with np.load(run/'outputs.npz') as data:
        local, previous = data['local_trajectory'], data['trajectory']
        stamps, points, offsets = data['cloud_stamps'], data['registered_points'], data['cloud_offsets']
    clouds = [points[a:b] for a, b in zip(offsets[:-1], offsets[1:])]
    if not np.array_equal(local, previous):
        origin = local[0, 0]
        restore = PoseTrack(local, origin).at(stamps-origin) @ np.linalg.inv(
            PoseTrack(previous, origin).at(stamps-origin))
        clouds = [apply_pose(m, c).astype('f4') for m, c in zip(restore, clouds)]
    export_map(output, report, local, clouds, stamps, use_loops, level_floors)


def map_bag(bag, output, config, topic=HESAI, gap=3.0, use_loops=True, level_floors=False):
    mapper = Mapper(config)
    with closing(open_bag(bag)[0]) as db:
        origin, = db.execute('SELECT min(timestamp) FROM messages').fetchone()
        row = db.execute('SELECT id,type FROM topics WHERE name=?', (topic,)).fetchone()
        if row is None or row[1] != 'sensor_msgs/msg/PointCloud2':
            raise ValueError(f'Missing PointCloud2 topic {topic}')
        # Iterate by storage time through SQLite's timestamp index. Only LiDAR payloads are read.
        sql = 'SELECT timestamp,data FROM messages WHERE topic_id=? ORDER BY timestamp,id'
        previous = None
        stopped = None
        for received, payload in db.execute(sql, (row[0],)):
            if previous is not None and (received - previous) / 1e9 > gap:
                stopped = (received - previous) / 1e9
                break
            previous = received
            mapper.add(deserialize_message(payload, PointCloud2))
            if len(mapper.poses) and len(mapper.poses) % 500 == 0:
                print(f'{len(mapper.poses)} scans', flush=True)
    mapper.save(output, dict(bag=str(bag.resolve()), topic=topic, origin_ns=origin,
                             stop_gap_s=stopped, gap_limit_s=gap), use_loops, level_floors)


def map_live(output, config, topic, gap, use_loops, level_floors=False):
    import rclpy
    from nav_msgs.msg import Odometry
    from rclpy.executors import ExternalShutdownException
    from rclpy.qos import qos_profile_sensor_data
    from rclpy.time import Time

    mapper = Mapper(config)
    rclpy.init(args=[])
    node = rclpy.create_node('hesai_mapping')
    publisher = node.create_publisher(Odometry, '/hesai_mapping/odometry', 10)
    stopped_gap = None

    def consume(msg):
        nonlocal stopped_gap
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if mapper.last_stamp is not None and stamp - mapper.last_stamp > gap:
            stopped_gap = stamp - mapper.last_stamp
            return
        if mapper.add(msg) is None:
            return
        pose = mapper.poses[-1]
        odom = Odometry()
        odom.header.frame_id, odom.child_frame_id = 'hesai_odom', mapper.frame
        odom.header.stamp = Time(nanoseconds=round(pose[0]*1e9)).to_msg()
        p, q = odom.pose.pose.position, odom.pose.pose.orientation
        p.x, p.y, p.z = pose[1:4]
        q.x, q.y, q.z, q.w = pose[4:]
        publisher.publish(odom)

    node.create_subscription(PointCloud2, topic, consume, qos_profile_sensor_data)
    node.get_logger().info(f'Mapping {topic}. Stop with Ctrl+C to build the final map.')
    try:
        while rclpy.ok() and stopped_gap is None:
            rclpy.spin_once(node, timeout_sec=.25)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
    mapper.save(output, dict(topic=topic, input='live', stop_gap_s=stopped_gap, gap_limit_s=gap),
                use_loops, level_floors)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--bag', type=Path)
    source.add_argument('--rebuild', type=Path, help='Reapply the map correction to saved local odometry')
    source.add_argument('--live', action='store_true', help='Subscribe to the sensor and export on shutdown')
    p.add_argument('--output', type=Path, required=True)
    tuning = p.add_mutually_exclusive_group()
    tuning.add_argument('--config', type=Path, help='Use this complete KISS-ICP configuration')
    tuning.add_argument('--profile', choices=('map', 'live'), help='Default follows the input mode')
    p.add_argument('--topic', default=HESAI)
    corrections = p.add_mutually_exclusive_group()
    corrections.add_argument('--odometry-only', action='store_true', help='Skip automatic revisit correction at export')
    corrections.add_argument('--level-floors', action='store_true',
                             help='Align supported indoor floors and anchor revisits to the first pass at export')
    p.add_argument('--gap', type=float, default=3., help='End the segment at a longer recording gap (seconds)')
    args = p.parse_args()
    if args.output.exists() or not np.isfinite(args.gap) or args.gap <= 0:
        p.error('Provide a new output directory and a positive gap threshold')
    if args.rebuild is not None:
        if args.config or args.profile:
            p.error('Rebuilding uses the recorded local odometry and its original profile')
        rebuild(args.rebuild, args.output, not args.odometry_only, args.level_floors)
        return
    config = load_config(args.config or Path(__file__).with_name('hesai_indoor.yaml'))
    if args.config is None and (args.profile or ('live' if args.live else 'map')) == 'live':
        config.registration.max_num_threads = 4
        config.registration.convergence_criterion = .001
    if args.live:
        map_live(args.output, config, args.topic, args.gap, not args.odometry_only, args.level_floors)
    else:
        map_bag(args.bag, args.output, config, args.topic, args.gap, not args.odometry_only, args.level_floors)


if __name__ == '__main__':
    main()
