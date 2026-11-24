#!/usr/bin/env python3
"""Compare one-parameter native-clock replays using posterior scans and states.

Floor metrics are self-consistency checks between initial and final observations
of the returning room's floor. They are not surveyed map/trajectory accuracy.
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/r3d-matplotlib')
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.transform import Rotation


def voxel(points, size=0.05):
    keys = np.floor(points / size).astype(np.int64)
    _, indices = np.unique(keys, axis=0, return_index=True)
    return points[np.sort(indices)]


def fit_floor(points, seed=20261111):
    rng = np.random.default_rng(seed)
    points = np.asarray(points, dtype=float)
    if len(points) > 20000:
        points = points[rng.choice(len(points), 20000, replace=False)]
    if len(points) < 300:
        raise ValueError('Too few candidate floor points')
    best, best_count = None, 0
    for _ in range(160):
        a, b, c = points[rng.choice(len(points), 3, replace=False)]
        n = np.cross(b-a, c-a)
        length = np.linalg.norm(n)
        if length < 1e-8:
            continue
        n /= length
        if n[2] < 0:
            n = -n
        if n[2] < np.cos(np.radians(20)):
            continue
        d = -n @ a
        mask = np.abs(points @ n + d) < 0.025
        count = int(mask.sum())
        if count > best_count:
            best, best_count = mask, count
    if best is None or best_count < 300:
        raise ValueError('No sufficiently supported near-horizontal floor plane')
    for _ in range(3):
        centroid = points[best].mean(axis=0)
        _, _, v = np.linalg.svd(points[best] - centroid, full_matrices=False)
        n = v[-1]
        if n[2] < 0:
            n = -n
        d = -n @ centroid
        best = np.abs(points @ n + d) < 0.025
    inliers = points[best]
    if min(np.ptp(inliers[:, :2], axis=0)) < 1:
        raise ValueError('Floor support does not span at least 1 m in both XY axes')
    return {'normal': n, 'offset': float(d), 'inliers': inliers,
            'candidate_count': len(points), 'inlier_fraction': float(best.mean()),
            'inlier_span_xy_m': np.ptp(inliers[:, :2], axis=0).tolist()}


def pair_metrics(first, last, query):
    a, b = first['normal'], last['normal']
    height_a = -(a[:2] @ query + first['offset']) / a[2]
    height_b = -(b[:2] @ query + last['offset']) / b[2]
    residual = last['inliers'] @ a + first['offset']
    return {'normal_disagreement_deg': float(np.degrees(np.arccos(np.clip(a @ b, -1, 1)))),
            'signed_height_difference_at_common_xy_cm': float(100 * (height_b-height_a)),
            'end_points_distance_to_initial_plane_median_abs_cm': float(100*np.median(np.abs(residual))),
            'end_points_distance_to_initial_plane_p95_abs_cm': float(100*np.percentile(np.abs(residual), 95)),
            'common_query_xy_m': query.tolist()}


def validation():
    rng = np.random.default_rng(7)
    xy = rng.uniform(-3, 3, (6000, 2))
    first = np.column_stack([xy, rng.normal(0, .003, len(xy))])
    last = np.column_stack([xy, .12 + np.tan(np.radians(1))*xy[:, 0] + rng.normal(0, .003, len(xy))])
    outliers = rng.uniform([-3, -3, -.8], [3, 3, .8], (1500, 3))
    a, b = fit_floor(np.concatenate([first, outliers])), fit_floor(np.concatenate([last, outliers]))
    metrics = pair_metrics(a, b, np.zeros(2))
    passed = abs(metrics['normal_disagreement_deg']-1) < .1 and abs(metrics['signed_height_difference_at_common_xy_cm']-12) < .3
    if not passed:
        raise AssertionError(metrics)
    return {'synthetic_known_tilt_deg': 1, 'synthetic_known_offset_cm': 12,
            'outlier_fraction': .2, 'measured': metrics, 'passed': passed}


def floor_pools(data, begin):
    poses, points, offsets, stamps = (data[k] for k in ['trajectory', 'registered_points', 'cloud_offsets', 'cloud_stamps'])
    pools = {'start': [], 'end': []}
    for i, stamp in enumerate(stamps):
        relative = stamp-begin
        group = 'start' if 10 <= relative <= 25 else ('end' if 450 <= relative <= 505 else None)
        if group is None:
            continue
        body = np.array([np.interp(stamp, poses[:, 0], poses[:, j]) for j in [1, 2, 3]])
        p = points[offsets[i]:offsets[i+1]].astype(float)
        radius = np.linalg.norm(p[:, :2]-body[:2], axis=1)
        mask = (radius > .5) & (radius < 5) & (p[:, 2] < body[2]-.18) & (p[:, 2] > body[2]-1.4)
        pools[group].append(p[mask])
    return {name: voxel(np.concatenate(chunks)) if chunks else np.empty((0, 3)) for name, chunks in pools.items()}


def load_states(path):
    rows = []
    for line in path.read_text().splitlines():
        try:
            values = list(map(float, line.split()))
            if len(values) == 25:
                rows.append(values)
        except ValueError:
            pass
    return np.asarray(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    root = args.root
    result = {'metric_validation': validation(), 'cases': {},
              'scope': 'Same full bag, native clock, rate 2; only initial extrinsic_T differs. Online extrinsic estimation remains enabled.',
              'floor_metric_assumption': 'Initial and final observations are of the same flat floor level in the returning room. Plane consistency is not ground-truth accuracy.',
              'limitations': ['Missing original intra-scan times remain unchanged.',
                             'Recorded input observation counts do not measure the estimator internal IMU callback.',
                             'No surveyed map, ground-truth trajectory or externally measured sensor calibration.']}
    cases = ['baseline', 'urdf_translation']
    loaded, fitted = {}, {}
    manifests = {case: json.loads((root/case/'manifest.json').read_text()) for case in cases}
    loaded = {case: np.load(root/case/'outputs.npz') for case in cases}
    all_pools = {case: floor_pools(loaded[case], manifests[case]['first_record_ns']/1e9) for case in cases}
    shared_bounds_error = None
    try:
        pools = [p for case in cases for p in all_pools[case].values()]
        lo = np.max([np.percentile(p[:, :2], 5, axis=0) for p in pools], axis=0)
        hi = np.min([np.percentile(p[:, :2], 95, axis=0) for p in pools], axis=0)
        if np.any(hi-lo < 1):
            raise ValueError('Insufficient shared floor observation area across both cases')
    except (ValueError, IndexError) as exc:
        shared_bounds_error = str(exc)
    for case in cases:
        directory = root/case
        manifest = manifests[case]
        data = loaded[case]
        poses = data['trajectory']
        states = load_states(directory/'runtime_logs/mat_pre.txt')
        dt = np.linalg.norm(states[:, 10:13]-states[0, 10:13], axis=1)
        rotations = Rotation.from_euler('xyz', states[:, 7:10]/57.3)
        dr = np.degrees((rotations[0].inv()*rotations).magnitude())
        quality = {'status_replayed': manifest['status']=='replayed',
                   'verified_use_sim_time': manifest.get('verified_use_sim_time') is True,
                   'logged_initial_translation_matches_requested': bool(np.allclose(states[0,10:13], manifest['mapping_parameters']['extrinsic_T'], atol=1e-6)),
                   'all_posterior_values_finite': bool(np.isfinite(poses).all()),
                   'input_lidar_fraction_observed': manifest['received_input_counts']['lidar']/manifest['expected_input_counts']['/hesai_ros_driver/hesai/lidar_points'],
                   'input_imu_fraction_observed': manifest['received_input_counts']['imu']/manifest['expected_input_counts']['/imu/data'],
                   'posterior_fraction_of_input_lidar': len(poses)/manifest['expected_input_counts']['/hesai_ros_driver/hesai/lidar_points']}
        quality['sufficient_capture_for_diagnostic_comparison'] = (
            quality['status_replayed'] and quality['verified_use_sim_time'] and
            quality['logged_initial_translation_matches_requested'] and quality['all_posterior_values_finite'] and
            quality['input_lidar_fraction_observed'] >= .995 and
            quality['input_imu_fraction_observed'] >= .995 and
            quality['posterior_fraction_of_input_lidar'] >= .995)
        result['cases'][case] = {'quality': quality, 'manifest': manifest,
            'estimated_translation_start_m': states[0, 10:13].tolist(),
            'estimated_translation_end_m': states[-1, 10:13].tolist(),
            'estimated_translation_final_adjustment_cm': float(dt[-1]*100),
            'estimated_translation_max_adjustment_cm': float(dt.max()*100),
            'estimated_rotation_max_adjustment_deg': float(dr.max()),
            'estimated_rotation_final_adjustment_deg': float(dr[-1]),
            'posterior_start_position_m': poses[0, 1:4].tolist(),
            'posterior_end_position_m': poses[-1, 1:4].tolist(),
            'posterior_count': len(poses)}
        pools = all_pools[case]
        try:
            if shared_bounds_error is not None:
                raise ValueError(shared_bounds_error)
            planes = {}
            for name, p in pools.items():
                mask = np.all((p[:, :2] >= lo) & (p[:, :2] <= hi), axis=1)
                planes[name] = fit_floor(p[mask])
            metrics = pair_metrics(planes['start'], planes['end'], (lo+hi)/2)
            metrics['fits'] = {name: {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in d.items() if k!='inliers'} for name, d in planes.items()}
            metrics['shared_xy_bounds_m'] = [lo.tolist(), hi.tolist()]
            result['cases'][case]['floor_consistency'] = metrics
            fitted[case] = planes
        except ValueError as exc:
            result['cases'][case]['floor_consistency'] = {'unavailable': str(exc)}
        # Persist the diagnostic curves for review without reprocessing ROS data.
        np.savez_compressed(directory/'calibration_curves.npz', time_s=states[:, 0],
                            translation_change_cm=dt*100, rotation_change_deg=dr)
    baseline, candidate = [result['cases'][case] for case in cases]
    if all('unavailable' not in result['cases'][case]['floor_consistency'] for case in cases):
        a = baseline['floor_consistency'];b = candidate['floor_consistency']
        result['floor_changes_candidate_minus_baseline'] = {k: b[k]-a[k] for k in [
            'normal_disagreement_deg','end_points_distance_to_initial_plane_median_abs_cm',
            'end_points_distance_to_initial_plane_p95_abs_cm']}
    (root/'comparison.json').write_text(json.dumps(result, indent=2)+'\n')
    colors = ['#176ba0','#d46a17']
    labels = ['Bisherige Translation','Translation aus URDF + TF']
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    for case, label, color in zip(cases, labels, colors):
        c = np.load(root/case/'calibration_curves.npz')
        axes[0,0].plot(c['time_s'], c['translation_change_cm'], label=label, color=color)
        axes[0,1].plot(c['time_s'], c['rotation_change_deg'], label=label, color=color)
    axes[0,0].set(title='Nachkalibrierung gegenüber dem jeweiligen Startwert', ylabel='Änderung Translation [cm]', xlabel='Bag-Zeit [s]')
    axes[0,1].set(title='Änderung der geschätzten Sensorrotation', ylabel='Winkeländerung [Grad]', xlabel='Bag-Zeit [s]')
    for col, case in enumerate(cases):
        ax = axes[1,col]
        if case in fitted:
            planes = fitted[case]
            n, d = planes['start']['normal'], planes['start']['offset']
            for name, color, label in [('start','#777777','Anfang: 10–25 s'),('end',colors[col],'Ende: 450–505 s')]:
                p = planes[name]['inliers'][::max(1,len(planes[name]['inliers'])//4000)]
                ax.scatter(p[:,0], 100*(p@n+d), s=1, alpha=.3, color=color, label=label)
            ax.axhline(0, color='black', lw=.5)
            ax.set(xlabel='Karten-X [m]', ylabel='Abstand zur Anfangs-Bodenebene [cm]')
        else:
            ax.text(.1,.5,'Kein belastbarer Bodenflächenvergleich',transform=ax.transAxes)
        ax.set_title(labels[col]+'\nBoden-Konsistenz im gemeinsam beobachteten Bereich')
    for ax in axes.flat:
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle('Kontrollierter Vergleich: nur extrinsic_T geändert; native --clock, beide 2×\n'
                 'Online-Kalibrierung aktiv. Bodenvergleich ist Konsistenzprüfung, keine Ground-Truth-Genauigkeit.',fontsize=12)
    fig.savefig(root/'comparison_diagnostics.png',dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(2, 2, figsize=(13, 10), constrained_layout=True)
    all_poses = np.concatenate([loaded[c]['trajectory'] for c in cases])
    lo, hi = all_poses[:,1:3].min(axis=0)-5, all_poses[:,1:3].max(axis=0)+5
    for col, case in enumerate(cases):
        data = loaded[case];poses=data['trajectory'];points=data['registered_points']
        p = points[::max(1,int(np.ceil(len(points)/200000)))]
        axes[0,col].scatter(p[:,0],p[:,1],c=p[:,2],s=.15,cmap='viridis',vmin=-1,vmax=5,alpha=.4,rasterized=True)
        axes[0,col].plot(poses[:,1],poses[:,2],color='#c81d25',lw=.7)
        axes[0,col].set(xlabel='Karten-X [m]',ylabel='Karten-Y [m]',title=labels[col]+'\nRegistrierte Scans und korrigierte Trajektorie',xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]))
        axes[0,col].set_aspect('equal',adjustable='box')
        axes[1,col].scatter(p[:,0],p[:,2],color=colors[col],s=.15,alpha=.3,rasterized=True)
        axes[1,col].plot(poses[:,1],poses[:,3],color='#c81d25',lw=.7)
        axes[1,col].set(xlabel='Karten-X [m]',ylabel='Karten-Z [m]',xlim=(lo[0],hi[0]),ylim=(-2,8))
        axes[1,col].set_aspect('equal',adjustable='box')
    fig.suptitle('Vollständiger Bag: identische Eingabedaten, native ROS-Zeit, nur Starttranslation geändert\n'
                 'Punktwolken sind zeitlich gleichmäßig abgetastet; kein vermessener Genauigkeitsvergleich.',fontsize=12)
    fig.savefig(root/'maps_comparison.png',dpi=170)
    plt.close(fig)
    print(json.dumps({case:{k:v for k,v in result['cases'][case].items() if k not in ['manifest']} for case in cases},indent=2))


if __name__ == '__main__':
    main()
