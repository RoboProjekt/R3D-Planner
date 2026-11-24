"""Build a body-pose constraint from four raw Hesai scans at a confirmed revisit."""
from contextlib import closing
import json
from pathlib import Path

import numpy as np
from rclpy.serialization import deserialize_message
from scipy.spatial.transform import Rotation
from sensor_msgs.msg import PointCloud2

from correct_lio_drift import align, apply_pose, distances, voxel
from evaluate_l1_ab import sensor_poses
from prepare_l1_ab import HESAI, IMU, open_bag, point_arrays


def raw_scans(bag, replay_bag, timestamps, replay_origin):
    scans = {}
    with closing(open_bag(bag)[0]) as db:
        # A filtered replay can begin later than its parent bag. Look up scans by
        # absolute bag timestamp so the protocol uses the same epoch as the graph.
        origin = round(replay_origin * 1e9)
        if bag.resolve() != replay_bag.resolve():
            # Confirm a derived bag is from this recording using shared Body-IMU messages.
            query = ('SELECT m.timestamp, m.data FROM messages m JOIN topics t ON t.id=m.topic_id '
                     'WHERE t.name=? AND m.timestamp >= ? ORDER BY m.timestamp LIMIT 1')
            with closing(open_bag(replay_bag)[0]) as replay_db:
                for stamp in (min(timestamps), max(timestamps)):
                    args = (IMU, origin + round(stamp * 1e9))
                    sample = replay_db.execute(query, args).fetchone()
                    if sample is None or db.execute(query, args).fetchone() != sample:
                        raise ValueError('Replay and raw bag have different Body-IMU data at the revisit')
        row = db.execute('SELECT id FROM topics WHERE name=?', (HESAI,)).fetchone()
        if not row:
            raise ValueError('Raw Hesai topic missing')
        for t in timestamps:
            target = origin + round(t * 1e9)
            # Restrict the search before ordering by distance to the desired bag time.
            hit = db.execute('SELECT data FROM messages WHERE topic_id=? AND timestamp BETWEEN ? AND ? '
                             'ORDER BY abs(timestamp - ?) LIMIT 1',
                             (row[0], target - 150000000, target + 150000000, target)).fetchone()
            if hit is None:
                raise ValueError(f'Missing raw Hesai scan near {t:g} s')
            fields = point_arrays(deserialize_message(hit[0], PointCloud2))
            xyz = np.column_stack([fields[k] for k in 'xyz']).astype(float)
            r = np.linalg.norm(xyz, axis=1)
            scans[t] = (float(np.max(fields['timestamp'])), voxel(xyz[(r > .8) & (r < 8.)], .07))
    return scans


def checked_pair(a, b):
    forward = align(a, b, np.eye(4))
    reverse = align(b, a, np.eye(4))
    scores = distances(a, apply_pose(forward, b))
    discrepancy = reverse @ forward
    dt = float(np.linalg.norm(discrepancy[:3, 3]))
    dr = float(np.degrees(Rotation.from_matrix(discrepancy[:3, :3]).magnitude()))
    valid = min(scores['overlap_each_direction']) >= .6 and scores['median_cm'] <= 11 and dt <= .08 and dr <= 1.3
    return forward, dict(accepted=valid, roundtrip_m=dt, roundtrip_deg=dr, **scores)


def raw_revisit(replay, run_path, bag, revisit):
    (a0, b0), (a1, b1) = revisit['pairs']
    report = dict(revisit, source='raw_hesai', accepted=False, registrations=[])
    replay_bag = Path(json.loads((run_path/'manifest.json').read_text())['bag'])
    scans = raw_scans(bag, replay_bag, [a0, b0, a1, b1], replay.origin)
    transforms = []
    for i, j in [(a0, b0), (a1, b1), (a0, a1), (b0, b1)]:
        try:
            pose, check = checked_pair(scans[i][1], scans[j][1])
        except ValueError as exc:
            return dict(report, reason=str(exc)), None
        report['registrations'].append(dict(times=[i, j], **check))
        if not check['accepted']:
            return dict(report, reason='Raw scan registration failed verification'), None
        transforms.append(pose)
    first, second, across_start, across_return = transforms
    # Both paths map the second return scan to the first start scan.
    cycle = np.linalg.inv(first @ across_return) @ across_start @ second
    delta = float(np.linalg.norm(cycle[:3, 3]))
    angle = float(np.degrees(Rotation.from_matrix(cycle[:3, :3]).magnitude()))
    report.update(cycle_m=delta, cycle_deg=angle)
    if delta > .12 or angle > 1.5:
        return dict(report, reason='Four-scan cycle failed verification'), None
    _, _, lidar_poses, _, _ = sensor_poses(run_path, {a0: scans[a0], b0: scans[b0]})
    times = np.array([scans[t][0] - replay.origin for t in [a0, b0]])
    body = replay.at(times)
    extrinsics = np.linalg.inv(body) @ np.stack([lidar_poses[a0], lidar_poses[b0]])
    relative = extrinsics[0] @ first @ np.linalg.inv(extrinsics[1])
    return dict(report, accepted=True, body_times_s=times.tolist(), relative_body_pose=relative.tolist()), (
        times[0], times[1], relative)
