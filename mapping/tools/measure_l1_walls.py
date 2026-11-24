#!/usr/bin/env python3
"""Measure L1 returns against local Hesai wall patches before FAST-LIO deskew.

Window times are camera labels for the 2026-11-18 round trip. One paired scan
is sampled every 0.25 seconds. All geometry is in the recorded Hesai frame.
"""
import argparse
from contextlib import closing
import json
from pathlib import Path

import numpy as np
from rclpy.serialization import deserialize_message
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from sensor_msgs.msg import Imu, PointCloud2

from inspect_bags import stamp_ns
from prepare_l1_ab import CONTROL, FUSION, IMU, open_bag, point_arrays, select_hesai

WINDOWS = {'start_room': (3, 10), 'stair_foot': (58, 63), 'ascent': (64, 84),
           'descent': (172, 186), 'return_room': (230, 237)}


def voxel_centres(points, size):
    _, indices = np.unique(np.floor(points / size).astype(np.int64), axis=0, return_inverse=True)
    counts = np.bincount(indices)
    return np.column_stack([np.bincount(indices, weights=x) / counts for x in points.T])


def in_range(points):
    radii = np.linalg.norm(points, axis=1)
    return points[(radii >= .8) & (radii <= 6) & np.isfinite(points).all(axis=1)]


def wall_residuals(hesai, unitree):
    """Return unsigned point-to-plane distances only inside supported wall patches."""
    reference = voxel_centres(in_range(hesai), .04)
    queries = in_range(unitree)
    if len(queries) == 0 or len(reference) < 16:
        return np.array([]), len(queries)
    distances, indices = cKDTree(reference).query(queries, k=16)
    close = distances[:, -1] < .5
    if not np.any(close):
        return np.array([]), len(queries)
    neighbours = reference[indices[close]]
    centres = neighbours.mean(axis=1)
    offsets = neighbours - centres[:, None, :]
    cov = offsets.transpose(0, 2, 1) @ offsets / neighbours.shape[1]
    eig, axes = np.linalg.eigh(cov)
    normal = axes[:, :, 0]
    # Require an extended surface in two directions and a nearly vertical wall
    # (within 30 degrees in the sensor frame). Exclude tangent extrapolation.
    planar = ((eig[:, 1] >= .04**2) & (eig[:, 0] <= .025**2)
              & (eig[:, 0] <= .08 * eig[:, 1]) & (abs(normal[:, 2]) <= .5))
    patch = offsets @ axes[:, :, 1:]
    displacement = queries[close] - centres
    projected = np.einsum('ni,nij->nj', displacement, axes[:, :, 1:])
    inside = np.all((projected >= patch.min(axis=1)-.04) & (projected <= patch.max(axis=1)+.04), axis=1)
    distances = abs(np.einsum('ij,ij->i', displacement, normal))
    return distances[planar & inside], len(queries)


def gyro_streams(db, origin):
    traces = {}
    for name, ident in db.execute('SELECT name,id FROM topics WHERE name IN (?,?)', (IMU, '/utlidar/imu')):
        rows = []
        for rec, data in db.execute('SELECT timestamp,data FROM messages WHERE topic_id=? ORDER BY timestamp',
                                    (ident,)):
            msg = deserialize_message(data, Imu)
            rate = msg.angular_velocity
            rows.append(((rec-origin)/1e9, (stamp_ns(msg.header.stamp)-origin)/1e9,
                         np.degrees(np.linalg.norm([rate.x, rate.y, rate.z])), np.degrees(abs(rate.y))))
        traces[name] = np.array(rows)
    return traces


def clock_offset(trace):
    initial = trace[trace[:, 0] < 45]
    return float(np.median(initial[:, 0]-initial[:, 1]))


def measure(source_bag, paired_bag, output):
    with closing(open_bag(source_bag)[0]) as source, closing(open_bag(paired_bag)[0]) as paired:
        pairing = json.loads((paired_bag / 'pairing.json').read_text())
        origin = pairing['source_origin_ns']
        gyros = gyro_streams(source, origin)
        body, l1 = gyros[IMU], gyros['/utlidar/imu']
        shift = clock_offset(l1) - clock_offset(body)
        ids = dict(paired.execute('SELECT name,id FROM topics'))
        rows = []
        for phase, (start, end) in WINDOWS.items():
            for sec in np.arange(start, end, .25):
                stamp = paired.execute('SELECT min(timestamp) FROM messages WHERE timestamp>=? AND topic_id=?',
                                       (origin + round(sec*1e9), ids[FUSION])).fetchone()[0]
                if stamp is None or (stamp-origin)/1e9 >= min(sec+.25, end):
                    continue
                raw = dict(paired.execute('SELECT topic_id,data FROM messages WHERE timestamp=? '
                                          'AND topic_id IN (?,?)', (stamp, ids[CONTROL], ids[FUSION])))
                fus = deserialize_message(raw[ids[FUSION]], PointCloud2)
                fields = point_arrays(fus)
                a = point_arrays(deserialize_message(raw[ids[CONTROL]], PointCloud2))
                mask = select_hesai(fields, a)
                if mask is None:
                    raise ValueError('Control cloud no longer matches the fusion cloud')
                xyz = np.column_stack([fields[axis] for axis in 'xyz'])
                residuals, candidates = wall_residuals(xyz[mask], xyz[~mask])
                rec = {'phase': phase, 'bag_s': (stamp-origin)/1e9, 'in_range_l1_points': candidates,
                       'wall_points': len(residuals)}
                if len(residuals) >= 8:
                    rec['median_cm'], rec['p90_cm'] = np.percentile(100*residuals, [50, 90]).tolist()
                # Body Y is reported as a sensor axis. The L1 IMU contributes
                # only angular-speed magnitude, independent of its mounting axes.
                when = (stamp_ns(fus.header.stamp)-origin)/1e9
                for label, trace, offset in [('body', body, 0), ('l1', l1, shift)]:
                    window = trace[abs(trace[:, 1]+offset-when) <= .075]
                    if len(window):
                        rec[label+'_gyro_norm_deg_s'] = float(np.median(window[:, 2]))
                        if label == 'body':
                            rec['body_abs_gyro_y_deg_s'] = float(np.median(window[:, 3]))
                rows.append(rec)
    phases = {}
    for phase in WINDOWS:
        samples = [r for r in rows if r['phase'] == phase]
        usable = [r for r in samples if 'median_cm' in r]
        angles = [r for r in usable if 'body_abs_gyro_y_deg_s' in r]
        result = {'sampled': len(samples), 'usable': len(usable),
                  'total_in_range_l1_returns': sum(r['in_range_l1_points'] for r in samples),
                  'wall_returns': sum(r['wall_points'] for r in samples)}
        if usable:
            result.update(median_of_scan_medians_cm=float(np.median([r['median_cm'] for r in usable])),
                          median_of_scan_p90_cm=float(np.median([r['p90_cm'] for r in usable])))
        if len(angles) >= 5:
            pitch = [r['body_abs_gyro_y_deg_s'] for r in angles]
            result['median_abs_body_y_deg_s'] = float(np.median(pitch))
            rho = spearmanr(pitch, [r['median_cm'] for r in angles])[0]
            result['spearman_abs_body_y_vs_wall_distance'] = float(rho) if np.isfinite(rho) else None
        common = [r for r in samples if 'body_gyro_norm_deg_s' in r and 'l1_gyro_norm_deg_s' in r]
        if len(common) >= 5:
            body_norm = [r['body_gyro_norm_deg_s'] for r in common]
            l1_norm = [r['l1_gyro_norm_deg_s'] for r in common]
            rho = spearmanr(body_norm, l1_norm)[0]
            result['paired_gyro_samples'] = len(common)
            result['spearman_body_vs_l1_gyro_norm'] = float(rho) if np.isfinite(rho) else None
        phases[phase] = result
    result = {'source': str(source_bag.resolve()), 'paired': str(paired_bag.resolve()),
              'l1_imu_to_body_header_shift_s_for_diagnostics': shift, 'windows_s': WINDOWS,
              'phases': phases, 'samples': rows}
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(phases, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'paired', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    measure(args.source, args.paired, args.output)
