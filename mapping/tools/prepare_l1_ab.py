#!/usr/bin/env python3
"""Build two scan-matched FAST-LIO inputs from a recorded Hesai/L1 fusion bag.

Both arms use the fused header, bag arrival time, point order and body IMU.
Arm A retains just the points verified against the source Hesai scan. Arm B
retains the complete recorded fused message. Unmatched scans are omitted in both.
"""
import argparse
from array import array
from bisect import bisect_left, bisect_right
from collections import Counter
from contextlib import closing
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sqlite3
import struct
import tempfile

import numpy as np
from rclpy.serialization import deserialize_message, serialize_message
from sensor_msgs.msg import PointCloud2
import yaml

from inspect_bags import field_array

HESAI = '/hesai_ros_driver/hesai/lidar_points'
FUSION = '/lidar_fusion/point_cloud'
CONTROL = '/comparison/hesai_only'
IMU = '/imu/data'
POINT_FIELDS = ('x', 'y', 'z', 'intensity', 'ring', 'timestamp')


def open_bag(directory):
    meta = yaml.safe_load((directory / 'metadata.yaml').read_text())
    info = meta['rosbag2_bagfile_information']
    if info['storage_identifier'] != 'sqlite3' or len(info['relative_file_paths']) != 1:
        raise ValueError('Expected one SQLite database')
    path = (directory / info['relative_file_paths'][0]).resolve()
    wal = Path(str(path) + '-wal')
    if wal.exists() and wal.stat().st_size:
        raise ValueError('Source has pending WAL records')
    return sqlite3.connect(path.as_uri() + '?mode=ro&immutable=1', uri=True), info


def point_arrays(msg):
    fields = {f.name: f for f in msg.fields}
    return {name: field_array(msg, fields[name]) for name in POINT_FIELDS}


def packed_points(fields, mask):
    records = np.rec.fromarrays([fields[name][mask] for name in POINT_FIELDS], names=POINT_FIELDS)
    return records.view(np.dtype((np.void, records.dtype.itemsize)))


def select_hesai(fused, source):
    # Point timestamps survive fusion exactly. A coincident L1 firing can
    # share that timestamp, so verify coordinates, ring and intensity too.
    mask = np.isin(fused['timestamp'], np.unique(source['timestamp']))
    if mask.sum() < len(source['x']):
        return None
    if all(np.array_equal(fused[k][mask], source[k]) for k in POINT_FIELDS):
        return mask
    source_keys = packed_points(source, slice(None))
    locations = np.flatnonzero(mask)
    nearby_keys = packed_points(fused, locations)
    selected = np.isin(nearby_keys, source_keys)
    if not np.array_equal(np.sort(nearby_keys[selected]), np.sort(source_keys)):
        return None
    mask[locations] = selected
    return mask


def indexed_cloud_headers(db, topic_id):
    headers = []
    for ident, prefix in db.execute('SELECT id,substr(data,1,12) FROM messages WHERE topic_id=?',
                                    (topic_id,)):
        sec, ns = struct.unpack(('<' if prefix[1] == 1 else '>') + 'iI', prefix[4:12])
        headers.append((sec + ns * 1e-9, ident))
    return sorted(headers)


def verify_inputs(source_bag, paired_bag):
    """Read the exported bag back and compare the serialized inputs to the source."""
    with closing(open_bag(source_bag)[0]) as src, closing(open_bag(paired_bag)[0]) as dst:
        src_ids = dict(src.execute('SELECT name,id FROM topics'))
        dst_ids = dict(dst.execute('SELECT name,id FROM topics'))
        sql = 'SELECT timestamp,data FROM messages WHERE topic_id=? ORDER BY timestamp,id'
        imu_digest = hashlib.sha256()
        imu_count = 0
        for original, exported in zip(src.execute(sql, (src_ids[IMU],)),
                                      dst.execute(sql, (dst_ids[IMU],)), strict=True):
            if original != exported:
                raise ValueError('Body IMU record changed')
            stamp, raw = exported
            imu_digest.update(struct.pack('<qQ', stamp, len(raw)))
            imu_digest.update(raw)
            imu_count += 1
        end_differences_ms = []
        for (ta, a), (tb, b) in zip(dst.execute(sql, (dst_ids[CONTROL],)),
                                    dst.execute(sql, (dst_ids[FUSION],)), strict=True):
            originals = src.execute('SELECT data FROM messages WHERE timestamp=? AND topic_id=?',
                                    (tb, src_ids[FUSION]))
            if ta != tb or not any(b == row[0] for row in originals):
                raise ValueError('Fusion payload or matched scan arrival time changed')
            control = deserialize_message(a, PointCloud2)
            fused = deserialize_message(b, PointCloud2)
            if (control.header != fused.header or control.fields != fused.fields
                    or control.point_step != fused.point_step or control.is_bigendian != fused.is_bigendian):
                raise ValueError('Control cloud header or point layout changed')
            full_fields = point_arrays(fused)
            control_fields = point_arrays(control)
            mask = select_hesai(full_fields, control_fields)
            full = np.frombuffer(fused.data, dtype='u1').reshape(fused.width, fused.point_step)
            if mask is None or full[mask].tobytes() != bytes(control.data):
                raise ValueError('Control points differ in timing, order, or bytes')
            end_differences_ms.append(1000 * (full_fields['timestamp'].max() - control_fields['timestamp'].max()))
    if not end_differences_ms:
        raise ValueError('No paired scans to verify')
    return {'verified_pairs': len(end_differences_ms), 'verified_body_imu_records': imu_count,
            'last_point_time_fusion_minus_control_ms_p50_p95_max':
                np.percentile(end_differences_ms, [50, 95, 100]).tolist(),
            'verified_imu_sequence_sha256': imu_digest.hexdigest()}


def create_inputs(bag, destination):
    db, source_info = open_bag(bag)
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with db, tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
        stage = Path(tmp) / destination.name
        stage.mkdir()
        name = destination.name + '_0.db3'
        out = sqlite3.connect(stage / name)
        for table in ('topics', 'messages'):
            out.execute(db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                                   (table,)).fetchone()[0])
        topic_rows = {r[1]: r for r in db.execute('SELECT * FROM topics')}
        topic_ids = {n: r[0] for n, r in topic_rows.items()}
        control_id = max(topic_ids.values()) + 1
        out.executemany('INSERT INTO topics VALUES (?,?,?,?,?)',
                        [topic_rows[FUSION], topic_rows[IMU], (control_id, CONTROL, *topic_rows[FUSION][2:])])
        headers = indexed_cloud_headers(db, topic_ids[HESAI])
        header_times = [h for h, _ in headers]

        @lru_cache(maxsize=10)
        def source_cloud(ident):
            data, = db.execute('SELECT data FROM messages WHERE id=?', (ident,)).fetchone()
            msg = deserialize_message(data, PointCloud2)
            return msg.header.frame_id, point_arrays(msg)

        totals = Counter()
        omitted = []
        stamps = []
        body_payloads = hashlib.sha256()
        origin = db.execute('SELECT min(timestamp) FROM messages').fetchone()[0]
        rows = db.execute('SELECT topic_id,timestamp,data FROM messages WHERE topic_id IN (?,?) '
                          'ORDER BY timestamp,id', (topic_ids[FUSION], topic_ids[IMU]))
        insert = 'INSERT INTO messages(topic_id,timestamp,data) VALUES(?,?,?)'
        for topic, stamp, raw in rows:
            if topic == topic_ids[IMU]:
                out.execute(insert, (topic, stamp, raw))
                body_payloads.update(struct.pack('<qQ', stamp, len(raw)))
                body_payloads.update(raw)
                totals['imu'] += 1
                continue
            msg = deserialize_message(raw, PointCloud2)
            if msg.height != 1 or msg.row_step != msg.point_step * msg.width:
                raise ValueError('Expected packed, unorganized fused clouds')
            fields = point_arrays(msg)
            # Rings 12-15 identify Hesai firings in this 16-ring Hesai / 12-ring L1 recording.
            high_rings = fields['timestamp'][fields['ring'] >= 12]
            masks = []
            if len(high_rings):
                earliest = high_rings.min()
                lower = bisect_left(header_times, earliest - .12)
                upper = bisect_right(header_times, earliest + .00001)
                for _, ident in headers[lower:upper]:
                    frame, original = source_cloud(ident)
                    if frame == msg.header.frame_id:
                        match = select_hesai(fields, original)
                        if match is not None:
                            masks.append(match)
            if len(masks) != 1 or masks[0].all():
                omitted.append((stamp - origin) / 1e9)
                continue
            mask = masks[0]
            original_bytes = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.width, msg.point_step)
            msg.width = int(mask.sum())
            msg.row_step = msg.width * msg.point_step
            msg.data = array('B', original_bytes[mask].tobytes())
            out.execute(insert, (control_id, stamp, serialize_message(msg)))
            out.execute(insert, (topic, stamp, raw))
            totals['matched_scans'] += 1
            totals['hesai_points'] += msg.width
            totals['added_points'] += len(mask) - msg.width
            stamps.append(stamp)
        if len(stamps) < 2 or not totals['imu']:
            raise ValueError('Insufficient matched input')
        out.execute('CREATE INDEX timestamp_idx ON messages(timestamp)')
        out.commit()
        start, end, count = out.execute('SELECT min(timestamp),max(timestamp),count(*) FROM messages').fetchone()
        out.close()
        meta_topics = {v['topic_metadata']['name']: v['topic_metadata']
                       for v in source_info['topics_with_message_count']}
        topics = [{'topic_metadata': dict(meta_topics[IMU]), 'message_count': totals['imu']}]
        for topic_name in (CONTROL, FUSION):
            topics.append({'topic_metadata': dict(meta_topics[FUSION], name=topic_name),
                           'message_count': len(stamps)})
        info = dict(source_info, relative_file_paths=[name], starting_time={'nanoseconds_since_epoch': start},
                    duration={'nanoseconds': end - start}, message_count=count, topics_with_message_count=topics)
        if 'files' in info:
            info['files'] = [dict(path=name, starting_time=info['starting_time'], duration=info['duration'],
                                  message_count=count)]
        (stage / 'metadata.yaml').write_text(yaml.safe_dump({'rosbag2_bagfile_information': info}, sort_keys=False))
        report = dict(totals, source=str(bag.resolve()), source_origin_ns=origin,
                      first_pair_s=(stamps[0]-origin)/1e9, last_pair_s=(stamps[-1]-origin)/1e9,
                      max_pair_record_gap_s=float(np.diff(stamps).max()/1e9),
                      omitted_fusion_bag_times_s=omitted, imu_sequence_sha256=body_payloads.hexdigest())
        verification = verify_inputs(bag, stage)
        report.update(verification)
        (stage / 'pairing.json').write_text(json.dumps(report, indent=2) + '\n')
        stage.rename(destination)
        print(json.dumps({k: v for k, v in report.items() if k != 'omitted_fusion_bag_times_s'}),
              'omitted:', len(omitted))
    db.close()
    return verification


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bag', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    create_inputs(args.bag, args.output)
