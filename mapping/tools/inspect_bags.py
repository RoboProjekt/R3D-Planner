#!/usr/bin/env python3
"""Read-only ROS 2 sqlite bag audit; source databases must have no pending WAL.

Run with /opt/ros/humble/setup.bash sourced and /usr/bin/python3.
No ROS node, publisher, driver, or estimator is started.
"""
import argparse
import datetime
import hashlib
import json
import sqlite3
from pathlib import Path

import numpy as np
import yaml
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Imu, PointCloud2
from tf2_msgs.msg import TFMessage


TOPICS = {
    '/hesai_ros_driver/hesai/lidar_points': PointCloud2,
    '/utlidar/cloud': PointCloud2,
    '/lidar_fusion/point_cloud': PointCloud2,
    '/imu/data': Imu,
    '/utlidar/imu': Imu,
    '/tf_static': TFMessage,
}
DTYPES = {1: 'i1', 2: 'u1', 3: 'i2', 4: 'u2', 5: 'i4',
          6: 'u4', 7: 'f4', 8: 'f8'}


def summary(values):
    a = np.asarray(values, dtype=np.float64)
    a = a[np.isfinite(a)]
    if not len(a):
        return {'finite_count': 0}
    return dict(zip(('min', 'p01', 'median', 'p99', 'max'),
                    map(float, np.percentile(a, [0, 1, 50, 99, 100]))),
                finite_count=int(len(a)))


def stamp_ns(stamp):
    return stamp.sec * 1000000000 + stamp.nanosec


def inventory(root):
    result = []
    for meta in sorted(root.glob('*/metadata.yaml')):
        d = yaml.safe_load(meta.read_text())['rosbag2_bagfile_information']
        result.append({
            'path': str(meta.parent),
            'duration_s': d['duration']['nanoseconds'] / 1e9,
            'metadata_message_count': d['message_count'],
            'metadata_sha256': hashlib.sha256(meta.read_bytes()).hexdigest(),
            'files': [{'name': f.name, 'bytes': f.stat().st_size,
                       'mtime_ns': f.stat().st_mtime_ns}
                      for f in sorted(meta.parent.iterdir()) if f.is_file()],
            'topics': [{'name': t['topic_metadata']['name'],
                        'type': t['topic_metadata']['type'],
                        'metadata_count': t['message_count']}
                       for t in d['topics_with_message_count']],
        })
    return result


def field_array(msg, field):
    dtype = np.dtype(('>' if msg.is_bigendian else '<') + DTYPES[field.datatype])
    return np.ndarray((msg.height, msg.width, field.count), dtype=dtype,
                      buffer=msg.data, offset=field.offset,
                      strides=(msg.row_step, msg.point_step, dtype.itemsize)).reshape(-1)


def cloud_sample(timestamp, data):
    msg = deserialize_message(data, PointCloud2)
    out = {'record_ns': timestamp, 'header_ns': stamp_ns(msg.header.stamp),
           'frame': msg.header.frame_id, 'width': msg.width, 'height': msg.height,
           'point_step': msg.point_step, 'row_step': msg.row_step,
           'fields': [{'name': f.name, 'offset': f.offset, 'datatype': f.datatype,
                       'count': f.count} for f in msg.fields], 'point_fields': {}}
    for field in msg.fields:
        if field.name not in ('x', 'y', 'z', 'time', 'timestamp', 't', 'ring', 'intensity'):
            continue
        a = field_array(msg, field)
        out['point_fields'][field.name] = summary(a)
        out['point_fields'][field.name]['unique_count'] = int(len(np.unique(a)))
        if field.name == 'timestamp':
            header_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
            offset = a.astype(float) - header_time
            out['timestamp_minus_header_seconds'] = summary(offset)
            out['negative_timestamp_offset_fraction'] = float(np.mean(offset < 0))
            out['ssd_parser_clamped_offset_seconds'] = summary(np.maximum(offset, 0))
        elif field.name == 'time':
            out['negative_time_fraction'] = float(np.mean(a < 0))
            out['ssd_parser_clamped_offset_seconds'] = summary(np.maximum(a, 0))
    return out


def audit(bag, artifact_dir):
    files = sorted(bag.glob('*.db3'))
    if len(files) != 1:
        raise ValueError('This audit expects one sqlite database per bag')
    db = files[0]
    wal = Path(str(db) + '-wal')
    if wal.exists() and wal.stat().st_size:
        raise ValueError('Pending WAL: immutable access would omit records; use a safe snapshot')
    before = {str(f): (f.stat().st_size, f.stat().st_mtime_ns)
              for f in bag.iterdir() if f.is_file()}
    # immutable=1 prevents journal/shared-memory creation on the source SSD.
    c = sqlite3.connect(db.as_uri() + '?mode=ro&immutable=1', uri=True)
    c.execute('PRAGMA query_only=ON')
    topics = c.execute('SELECT id,name,type FROM topics').fetchall()
    begin, end = c.execute('SELECT MIN(timestamp),MAX(timestamp) FROM messages').fetchone()
    out = {'path': str(bag), 'source_db': str(db),
           'access': 'sqlite mode=ro immutable=1; WAL absent or empty',
           'db_sha256': 'not computed; large source identified by path, size, mtime and metadata hash',
           'record_start_ns': begin, 'record_end_ns': end,
           'cloud_samples': {}, 'imu': {}, 'static_transforms': []}
    for topic_id, topic, msg_type in topics:
        if topic not in TOPICS:
            continue
        if TOPICS[topic] is PointCloud2:
            samples = []
            seen = set()
            for fraction in (0, 0.25, 0.5, 0.75, 0.95):
                threshold = begin + int((end - begin) * fraction)
                row = c.execute('SELECT timestamp,data FROM messages WHERE timestamp>=? '
                                'AND topic_id=? ORDER BY timestamp LIMIT 1',
                                (threshold, topic_id)).fetchone()
                if row is not None and row[0] not in seen:
                    samples.append(cloud_sample(*row))
                    seen.add(row[0])
            out['cloud_samples'][topic] = samples
        elif TOPICS[topic] is TFMessage:
            for _, data in c.execute('SELECT timestamp,data FROM messages WHERE topic_id=?', (topic_id,)):
                msg = deserialize_message(data, TFMessage)
                for t in msg.transforms:
                    out['static_transforms'].append({
                        'parent': t.header.frame_id, 'child': t.child_frame_id,
                        'translation': [t.transform.translation.x, t.transform.translation.y, t.transform.translation.z],
                        'rotation_xyzw': [t.transform.rotation.x, t.transform.rotation.y,
                                          t.transform.rotation.z, t.transform.rotation.w]})
    imu_ids = {i: name for i, name, typ in topics if name in TOPICS and TOPICS[name] is Imu}
    rows = {name: [] for name in imu_ids.values()}
    frames = {name: set() for name in imu_ids.values()}
    if imu_ids:
        placeholders = ','.join('?' for _ in imu_ids)
        for rec, topic_id, data in c.execute(
                f'SELECT timestamp,topic_id,data FROM messages WHERE topic_id IN ({placeholders}) '
                'ORDER BY timestamp', tuple(imu_ids)):
            msg = deserialize_message(data, Imu)
            name = imu_ids[topic_id]
            frames[name].add(msg.header.frame_id)
            a = msg.linear_acceleration
            w = msg.angular_velocity
            q = msg.orientation
            rows[name].append([rec, stamp_ns(msg.header.stamp),
                               a.x, a.y, a.z, w.x, w.y, w.z, q.x, q.y, q.z, q.w])
    for name, values in rows.items():
        if not values:
            out['imu'][name] = {'count': 0}
            continue
        a = np.array(values, dtype=np.float64)
        rec_ns = np.array([v[0] for v in values], dtype=np.int64)
        hdr_ns = np.array([v[1] for v in values], dtype=np.int64)
        delta = np.diff(hdr_ns) / 1e9
        trace_path = artifact_dir / (bag.name + '_' + name.strip('/').replace('/', '_') + '.npz')
        np.savez_compressed(trace_path, record_ns=rec_ns, header_ns=hdr_ns,
                            accel=a[:, 2:5], gyro=a[:, 5:8], quaternion_xyzw=a[:, 8:12])
        out['imu'][name] = {
            'count': len(a), 'frames': sorted(frames[name]),
            'first_header_ns': int(hdr_ns[0]), 'last_header_ns': int(hdr_ns[-1]),
            'header_step_seconds': summary(delta),
            'nonpositive_header_steps': int(np.sum(delta <= 0)),
            'header_gaps_over_50ms': int(np.sum(delta > 0.05)),
            'record_minus_header_seconds': summary((rec_ns - hdr_ns) / 1e9),
            'acceleration_norm': summary(np.linalg.norm(a[:, 2:5], axis=1)),
            'gyro_norm': summary(np.linalg.norm(a[:, 5:8], axis=1)),
            'quaternion_norm': summary(np.linalg.norm(a[:, 8:12], axis=1)),
            'nonfinite_values': int(np.sum(~np.isfinite(a))),
            'trace_path': str(trace_path),
        }
    c.close()
    after = {str(f): (f.stat().st_size, f.stat().st_mtime_ns)
             for f in bag.iterdir() if f.is_file()}
    out['source_size_mtime_and_file_set_unchanged'] = before == after
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--bag', action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = {'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'method': 'Metadata inventory; five cloud samples across record time; '
                        'all IMU records in selected bags. No pose or mapping accuracy measured.',
              'inventory': inventory(args.root), 'audits': []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for name in args.bag:
        print('Auditing ' + name, flush=True)
        result['audits'].append(audit(args.root / name, args.output.parent))
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(str(args.output), flush=True)


if __name__ == '__main__':
    main()
