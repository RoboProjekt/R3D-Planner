#!/usr/bin/env python3
"""Compare FAST-LIO poses to the same independently registered Hesai return.

The reference JSON provides the bag timestamps and rigid scan match for this
round trip. Use the original Hesai scans for evaluation in every replay arm.
"""
import argparse
from contextlib import closing
import json
from pathlib import Path

import numpy as np
from rclpy.serialization import deserialize_message
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation, Slerp
from sensor_msgs.msg import PointCloud2

from compare_extrinsic_ab import load_states
from measure_l1_walls import voxel_centres
from prepare_l1_ab import HESAI, IMU, indexed_cloud_headers, open_bag, point_arrays


def matrix(rotation, translation):
    pose = np.eye(4)
    pose[:3, :3] = rotation.as_matrix()
    pose[:3, 3] = translation
    return pose


def transform(pose, points):
    return points @ pose[:3, :3].T + pose[:3, 3]


def read_reference(bag, reference):
    match = json.loads(reference.read_text())['streams'][HESAI]
    anchor = match['fit_pair_bag_seconds_start_return']
    held_out = [pair['bag_seconds_start_return'] for pair in match['held_out']]
    scans = {}
    with closing(open_bag(bag)[0]) as db:
        origin = db.execute('SELECT min(timestamp) FROM messages').fetchone()[0]
        topic_id, = db.execute('SELECT id FROM topics WHERE name=?', (HESAI,)).fetchone()
        for begin, end in [anchor, *held_out]:
            for key in (begin, end):
                rec = origin + round(key * 1e9)
                row = db.execute('SELECT data FROM messages WHERE timestamp=? AND topic_id=?',
                                 (rec, topic_id)).fetchone()
                if row is None:
                    raise ValueError(f'Reference at {key} s is missing from the source bag')
                msg = deserialize_message(row[0], PointCloud2)
                fields = point_arrays(msg)
                points = np.column_stack([fields[k] for k in 'xyz']).astype(float)
                radius = np.linalg.norm(points, axis=1)
                scans[key] = (float(np.max(fields['timestamp'])),
                              voxel_centres(points[(radius > .7) & (radius < 8)], .05))
    return scans, anchor, np.asarray(match['return_to_start_sensor_transform']), held_out


def log_time_origin(states, headers):
    # FAST-LIO's mat_pre log is relative to its first synchronized cloud.
    # Locate that input by matching the log across the run, including dropped scans.
    probe = states[::max(1, len(states)//250), 0]
    best_error = float('inf')
    best_header = None
    for candidate in headers[:30]:
        absolute = probe + candidate
        index = np.clip(np.searchsorted(headers, absolute), 1, len(headers)-1)
        residual = np.minimum(abs(absolute-headers[index-1]), abs(absolute-headers[index]))
        error = np.percentile(residual, 90)
        if error < best_error:
            best_error, best_header = error, candidate
    if best_error > .001:
        raise ValueError(f'Could not align FAST-LIO state log (p90 {best_error:.4f} s)')
    return best_header, best_error


def sensor_poses(directory, scans):
    manifest = json.loads((directory/'manifest.json').read_text())
    if (manifest['status'] != 'replayed' or not manifest['verified_use_sim_time']
            or manifest['nonfinite_posterior_values'] or manifest['player_exit_code'] != 0
            or manifest['estimator_exit_code'] != 0):
        raise ValueError(f'Incomplete replay: {directory}')
    topic = manifest.get('lidar_topic')
    if topic is None:
        # Older native-clock captures recorded the input only in the rosbag command.
        command = manifest['native_player_command']
        topic = command[command.index('--topics') + 1]
        manifest['lidar_topic'] = topic
    with closing(open_bag(Path(manifest['bag']))[0]) as db:
        topic_id, = db.execute('SELECT id FROM topics WHERE name=?', (topic,)).fetchone()
        headers = np.array([h for h, _ in indexed_cloud_headers(db, topic_id)])
    with np.load(directory/'outputs.npz') as output:
        poses = output['trajectory']
    if len(poses) < 2 or np.any(np.diff(poses[:, 0]) <= 0):
        raise ValueError('Need strictly increasing posterior pose times')
    states = load_states(directory/'runtime_logs'/'mat_pre.txt')
    state_zero, alignment_error = log_time_origin(states, headers)
    world = {}
    associations = {}
    for key, (end, _) in scans.items():
        idx = np.searchsorted(poses[:, 0], end)
        if not 0 < idx < len(poses):
            raise ValueError('Reference scan falls outside trajectory')
        bracket = poses[idx-1:idx+1]
        gap = np.ptp(bracket[:, 0])
        if gap > .25:
            raise ValueError(f'Pose gap at reference scan {key}: {gap:.3f} s')
        w = (end-bracket[0, 0])/gap
        rot = Slerp([0, 1], Rotation.from_quat(bracket[:, 4:]))([w])[0]
        body_pose = matrix(rot, (1-w)*bracket[0, 1:4]+w*bracket[1, 1:4])
        # Extrinsics have no process motion. The pre-update calibration from
        # the next input scan includes the preceding posterior correction.
        next_idx = np.searchsorted(states[:, 0], end-state_zero)
        if next_idx >= len(states):
            raise ValueError('No calibration state at reference scan')
        state = states[next_idx]
        state_delay = state[0] - (end-state_zero)
        if state_delay > .25:
            raise ValueError('Missing calibration near reference scan')
        extrinsic = matrix(Rotation.from_euler('xyz', state[7:10]/57.3), state[10:13])
        world[key] = body_pose @ extrinsic
        associations[key] = {'pose_bracket_s': float(gap), 'calibration_delay_s': float(state_delay)}
    return manifest, poses, world, associations, alignment_error


def read_run(directory, scans, anchor_times, relative_anchor, holdouts, map_corrections=None):
    manifest, poses, world, associations, alignment_error = sensor_poses(directory, scans)
    topic = manifest['lidar_topic']
    if map_corrections is not None:
        world = {key: map_corrections[key] @ pose for key, pose in world.items()}
    first, last = anchor_times
    expected = world[first] @ relative_anchor
    delta = world[last][:3, 3]-expected[:3, 3]
    angle = Rotation.from_matrix(expected[:3, :3].T @ world[last][:3, :3]).magnitude()
    held_metrics = []
    for before, after in holdouts:
        a = transform(world[before], scans[before][1])
        b = transform(world[after], scans[after][1])
        d = [cKDTree(x).query(y)[0] for x, y in ((a,b), (b,a))]
        held_metrics.append({'bag_s': [before, after],
                             'symmetric_median_nn_cm': float(100*np.mean([np.median(v) for v in d])),
                             'overlap_within_15cm': float(np.mean([(v < .15).mean() for v in d]))})
    return dict(lidar_topic=topic, start_lidar_world=world[first].tolist(),
                position_disagreement_m=float(np.linalg.norm(delta)),
                angle_disagreement_deg=float(np.degrees(angle)), xyz_disagreement_m=delta.tolist(),
                held_out=held_metrics, state_time_alignment_p90_ms=1000*alignment_error,
                associations=associations, poses=len(poses), lidar_observed=manifest['received_input_counts']['lidar'],
                lidar_expected=manifest['expected_input_counts'][topic],
                imu_observed=manifest['received_input_counts']['imu'],
                imu_expected=manifest['expected_input_counts'][IMU], config_sha256=manifest['config_sha256'],
                binary_sha256=manifest['binary_sha256'], bag=manifest['bag'], rate=manifest['rate'])


def evaluate(source, reference, output, runs):
    ref = read_reference(source, reference)
    results = {run.name: read_run(run, *ref) for run in runs}
    if len({(r['binary_sha256'],r['config_sha256'],r['rate']) for r in results.values()}) != 1:
        raise ValueError('Mixed replay binary, estimator configuration or rate')
    output.write_text(json.dumps(results, indent=2, allow_nan=False)+'\n')
    for name, run in results.items():
        print(f"{name}: {run['position_disagreement_m']:.3f} m, {run['angle_disagreement_deg']:.2f} deg")
    return results


def export_first_pair(trials, results, output):
    """Export both first-run maps in the same start-scan convention (metres)."""
    for arm in ('hesai', 'hesai_l1'):
        name = '01_' + arm
        with np.load(trials/name/'outputs.npz') as data:
            points = data['registered_points']
        to_start = np.linalg.inv(results[name]['start_lidar_world'])
        centres = voxel_centres(transform(to_start, points), .08).astype('<f4')
        with (output/(name+'.pcd')).open('wb') as f:
            header = ('# .PCD v0.7\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\n'
                      'TYPE F F F\nCOUNT 1 1 1\n'
                      f'WIDTH {len(centres)}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n'
                      f'POINTS {len(centres)}\nDATA binary\n')
            f.write(header.encode('ascii'))
            centres.tofile(f)


def plot_comparison(trials, results, output):
    import matplotlib.pyplot as plt

    fig, (error_ax, height_ax) = plt.subplots(1, 2, figsize=(10.8, 4.5),
                                               gridspec_kw={'width_ratios': [1, 1.6]})
    colours = ['#305d83', '#c26534']
    names = sorted(k for k in results if k.endswith('_hesai') and k[:2].isdigit())
    for i, name in enumerate(names):
        pair = [results[name], results[name+'_l1']]
        errors = [run['position_disagreement_m'] for run in pair]
        x = np.array([0., 1.]) + .035*(i-(len(names)-1)/2)/max(1, (len(names)-1)/2)
        error_ax.plot(x, errors, color='#a5adb4', lw=1.2, zorder=1)
        error_ax.scatter(x, errors, color=colours, s=38, zorder=2, clip_on=False)
    error_ax.set(xticks=[0, 1], xticklabels=['Hesai', 'Hesai + L1'], xlim=(-.25, 1.25),
                 ylabel='Abweichung vom Scanabgleich (m)', title='Rückkehr in den Startraum')
    error_ax.set_ylim(bottom=0)
    origin = json.loads((trials/'pairing.json').read_text())['source_origin_ns']/1e9
    for idx, (arm, label) in enumerate([('hesai', 'Hesai'), ('hesai_l1', 'Hesai + L1')]):
        with np.load(trials/('01_' + arm)/'outputs.npz') as data:
            poses = data['trajectory']
        height_ax.plot(poses[:, 0]-origin, poses[:, 3]-poses[0, 3], color=colours[idx],
                       label=label, lw=1.3)
    for lo, hi, label in [(64, 84, 'Aufstieg'), (172, 186, 'Abstieg')]:
        height_ax.axvspan(lo, hi, color='#829989', alpha=.16, lw=0)
        height_ax.text((lo+hi)/2, .97, label, ha='center', va='top',
                       transform=height_ax.get_xaxis_transform(), fontsize=9)
    height_ax.legend(frameon=False, loc='upper left')
    height_ax.set(xlabel='Zeit seit Aufnahmebeginn (s)', ylabel='Relative Höhe (m)',
                  title='FAST-LIO-Höhe im ersten Laufpaar')
    for ax in (error_ax, height_ax):
        ax.grid(axis='y', alpha=.2)
        ax.spines[['right', 'top']].set_visible(False)
    fig.suptitle('Treppenfahrt mit und ohne Unitree-L1-Punkte', x=.08, ha='left', weight='bold')
    fig.text(.08, .025, 'Links verbindet jede Linie zwei Replays derselben Fahrt. Beide Varianten verwenden die Body-IMU.',
             fontsize=9)
    fig.subplots_adjust(left=.08, right=.98, top=.80, bottom=.20, wspace=.33)
    fig.savefig(output/'vergleich.png', dpi=150)
    plt.close(fig)


def map_corrections_at(run, scans, corrected_trajectory):
    from correct_lio_drift import Correction, Replay
    replay = Replay(run)
    with np.load(corrected_trajectory) as data:
        times = data['node_times_s']
        base = data['original_nodes']
        if not np.allclose(base, replay.at(times), atol=1e-7, rtol=0):
            raise ValueError('Correction belongs to a different input trajectory')
        corr = Correction(replay, times, base, data['corrected_nodes'])
    scan_times = np.array([end - replay.origin for end, _ in scans.values()])
    return dict(zip(scans, corr.at(scan_times)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--reference', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--corrected-trajectory', type=Path,
                   help='Compare a single replay before and after pose-graph correction')
    p.add_argument('runs', type=Path, nargs='+')
    args = p.parse_args()
    if args.corrected_trajectory is None:
        evaluate(args.source, args.reference, args.output, args.runs)
        return
    if len(args.runs) != 1:
        p.error('--corrected-trajectory requires exactly one run')
    run = args.runs[0]
    ref = read_reference(args.source, args.reference)
    corrections = map_corrections_at(run, ref[0], args.corrected_trajectory)
    result = {'before': read_run(run, *ref), 'after': read_run(run, *ref, map_corrections=corrections)}
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
