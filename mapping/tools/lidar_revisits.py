"""Recognize and verify overlapping LiDAR scans without room labels or route times."""
from functools import lru_cache

import numpy as np
from scipy.spatial.transform import Rotation
from scipy.spatial import cKDTree

from correct_lio_drift import Correction, PoseTrack, align, apply_pose, distances, matrices, optimize, voxel


def profile(cloud):
    """Azimuthal range profiles in height bands, measured in the sensor frame."""
    angle = np.arctan2(cloud[:, 1], cloud[:, 0])
    bins = (np.floor(angle * 36 / (2*np.pi)).astype(int) % 36)
    radius = np.linalg.norm(cloud[:, :2], axis=1)
    # Use physical ranges: a repeated wall at a different distance is evidence against a match.
    result = np.zeros((3, 36))
    bands = np.digitize(cloud[:, 2], [-.35, .45])
    for band in range(3):
        selected = bands == band
        np.maximum.at(result[band], bins[selected], np.minimum(radius[selected], 12.))
    return result


def propose(times, poses, signatures, odometry=None):
    xyz = poses[:, :3, 3]
    rotated = np.stack([np.roll(signatures, shift, axis=2) for shift in range(36)])
    for j in range(len(times)):
        distance = np.linalg.norm(xyz[:j] - xyz[j], axis=1)
        eligible = [i for i in np.flatnonzero(times[j] - times[:j] >= 18)
                    if np.max(np.linalg.norm(xyz[i:j+1] - xyz[j], axis=1)) > 4.]
        if not eligible:
            continue
        errors = np.abs(rotated[:, j:j+1] - signatures[eligible]).mean(axis=(2, 3))
        nearest = sorted(eligible, key=lambda i: distance[i])
        appearance = sorted(zip(eligible, errors.min(axis=0)), key=lambda item: item[1])
        picks = [i for i in nearest[:2] if distance[i] <= 4.]
        if odometry is not None:
            raw_distance = np.linalg.norm(odometry[eligible, :3, 3] - odometry[j, :3, 3], axis=1)
            picks.extend(eligible[k] for k in np.argsort(raw_distance)[:2] if raw_distance[k] <= 4.)
        picks.extend(i for i, score in appearance[:2] if score < 1.4)
        for i in dict.fromkeys(picks):
            yaw = np.argmin(errors[:, eligible.index(i)]) * (2*np.pi/36)
            yield i, j, yaw, distance[i]


def compare_at(a, b, relative):
    return distances(a, apply_pose(relative, b))


def compatible_motion(displacement, rotation_error, travel):
    return (np.linalg.norm(displacement) <= min(6., .35 + .055 * travel)
            and abs(displacement[2]) <= min(1.2, .2 + .025 * travel)
            and np.rad2deg(rotation_error) <= min(25., 4. + .5 * travel))


def close_loops(trajectory, world_clouds, cloud_stamps, planes=None, odometry=None):
    origin = trajectory[0, 0]
    track = PoseTrack(trajectory, origin)
    stamps = np.asarray(cloud_stamps) - origin
    if len(stamps) < 3:
        return trajectory, world_clouds, {'status': 'local_odometry', 'loops': []}
    poses = track.at(stamps)
    inv = np.linalg.inv(poses)
    raw = PoseTrack(odometry, origin).at(stamps) if odometry is not None else None
    key_poses = poses if raw is None else raw

    @lru_cache(maxsize=512)
    def scan(i):
        xyz = apply_pose(inv[i], world_clouds[i])
        radius = np.linalg.norm(xyz, axis=1)
        return voxel(xyz[(radius > .8) & (radius < 12.)], .12)

    keys = []
    for i, t in enumerate(stamps):
        if i + 2 >= len(stamps) or stamps[i+2] - t > .85:
            continue
        if keys:
            last = keys[-1]
            dt = t - stamps[last]
            step = np.linalg.solve(key_poses[last], key_poses[i])
            if (dt < 1. or (dt < 4. and np.linalg.norm(step[:3, 3]) < .55 and
                             Rotation.from_matrix(step[:3, :3]).magnitude() < np.deg2rad(15))):
                continue
        if len(scan(i)) >= 120:
            keys.append(i)
    if len(keys) < 2:
        return trajectory, world_clouds, {'status': 'local_odometry', 'loops': []}
    signatures = np.stack([profile(scan(i)) for i in keys])
    path_length = np.r_[0., np.cumsum(np.linalg.norm(np.diff(poses[:, :3, 3], axis=0), axis=1))]
    accepted, checks, rejected, preservation_checks = [], [], [], {}
    for ik, jk, yaw, distance in propose(stamps[keys], poses[keys], signatures,
                                         None if raw is None else raw[keys]):
        i, j = keys[ik], keys[jk]
        if any(abs(stamps[i]-stamps[a]) < 3 and abs(stamps[j]-stamps[b]) < 3 for a,b,_ in accepted):
            continue
        a, b = scan(i), scan(j)
        prior = inv[i] @ poses[j]
        # Sample pre-existing overlaps on *other* scans, including candidates
        # that ICP may later reject. They can veto a harmful global deformation.
        u, v = i+1, j+1
        if distance < 3 and min(len(scan(u)), len(scan(v))) >= 120 and (u, v) not in preservation_checks:
            prior_score = compare_at(scan(u), scan(v), inv[u] @ poses[v])
            if prior_score['median_cm'] < 15 and min(prior_score['overlap_each_direction']) > .50:
                preservation_checks[u, v] = prior_score['median_cm']
        # Odometry retains the viewpoint offset. The second seed permits finding a
        # matching orientation even when drift moved the poses outside the local search.
        descriptor_seed = np.eye(4)
        descriptor_seed[:3,:3] = Rotation.from_euler('z', yaw).as_matrix()
        seeds = [prior, descriptor_seed] if distance <= 5 else [descriptor_seed]
        if raw is not None and np.linalg.norm(raw[i, :3, 3]-raw[j, :3, 3]) <= 5.:
            seeds.append(np.linalg.solve(raw[i], raw[j]))
        tree = cKDTree(a)
        scores = [np.mean(np.minimum(tree.query(apply_pose(seed, b[::3]))[0], .6)) for seed in seeds]
        best = int(np.argmin(scores))
        if scores[best] > .34:
            continue
        seed = seeds[best]
        try:
            forward = align(a, b, seed)
            backward = align(b, a, np.linalg.inv(seed))
        except ValueError:
            continue
        cycle = backward @ forward
        if (np.linalg.norm(cycle[:3,3]) > .09 or
                Rotation.from_matrix(cycle[:3,:3]).magnitude() > np.deg2rad(1.5)):
            continue
        fitted = compare_at(a, b, forward)
        if min(fitted['overlap_each_direction']) < .58 or fitted['median_cm'] > 13:
            continue
        displacement = (poses[i] @ forward)[:3, 3] - poses[j, :3, 3]
        travel = path_length[j] - path_length[i]
        rotation_error = Rotation.from_matrix(prior[:3, :3].T @ forward[:3, :3]).magnitude()
        # Repeated corridors can match on another storey. Bound the correction by
        # the intervening travel before accepting even a geometrically tight fit.
        if not compatible_motion(displacement, rotation_error, travel):
            rejected.append([float(stamps[i]), float(stamps[j]), displacement.tolist()])
            continue
        # Recheck geometry on two later scans that were not used to fit this transform.
        u, v = i+2, j+2
        if min(len(scan(u)), len(scan(v))) < 120:
            continue
        predicted = inv[u] @ poses[i] @ forward @ inv[j] @ poses[v]
        before = compare_at(scan(u), scan(v), inv[u] @ poses[v])
        after = compare_at(scan(u), scan(v), predicted)
        if (min(after['overlap_each_direction']) < .50 or after['median_cm'] > 16
                or after['median_cm'] > before['median_cm'] + 1.5):
            continue
        accepted.append((i, j, forward))
        checks.append((u, v, before['median_cm']))
    report = {'status': 'local_odometry', 'loops': [[float(stamps[a]), float(stamps[b])] for a,b,_ in accepted],
              'rejected_displacement': rejected}
    if not accepted:
        return trajectory, world_clouds, report
    nodes = np.unique(np.r_[track.time[0], np.arange(track.time[0], track.time[-1], 2.), track.time[-1],
                            [stamps[k] for a,b,_ in accepted for k in (a,b)]])
    base = track.at(nodes)
    edges = [(np.searchsorted(nodes, stamps[a]), np.searchsorted(nodes, stamps[b]), pose) for a,b,pose in accepted]
    windows = (planes or {}).get('vertical_windows_s', [])
    supported = np.zeros(len(nodes), dtype=bool)
    for start, end in windows:
        supported |= (nodes >= start-.25) & (nodes <= end+.25)
    report['vertical_prior_nodes'] = int(supported.sum())
    try:
        fitted = optimize(nodes, base, edges, vertical_nodes=np.flatnonzero(supported),
                          building_up=(planes or {}).get('building_up'))
    except ValueError as exc:
        report['reason'] = str(exc)
        return trajectory, world_clouds, report
    if supported.any():
        up = np.asarray(planes['building_up'])
        local_up = Rotation.from_matrix(base[supported, :3, :3]).inv().apply(up)
        corrected_up = Rotation.from_matrix(fitted[supported, :3, :3]).apply(local_up)
        max_change = np.rad2deg(np.arccos(np.clip(corrected_up @ up, -1., 1.))).max()
        report['max_vertical_change_deg'] = float(max_change)
        if max_change > 3.:
            report['reason'] = 'Loop correction conflicts with confirmed building verticals'
            return trajectory, world_clouds, report
    correction = Correction(track, nodes, base, fitted)
    moved = correction.at(stamps) @ poses
    reference_scores = np.array([s for _,_,s in checks])
    final_scores = np.array([compare_at(scan(u), scan(v), np.linalg.inv(moved[u]) @ moved[v])['median_cm']
                             for u,v,_ in checks])
    report['check_before_cm'] = reference_scores.tolist()
    report['check_after_cm'] = final_scores.tolist()
    guards = []
    for (u, v), before in preservation_checks.items():
        after = compare_at(scan(u), scan(v), np.linalg.inv(moved[u]) @ moved[v])['median_cm']
        guards.append({'times': [float(stamps[u]), float(stamps[v])], 'before_cm': before, 'after_cm': after})
    report['preservation_checks'] = guards
    # Keep good places usable and require an overall benefit across confirmed visits.
    if (np.mean(np.minimum(reference_scores, 100.) - np.minimum(final_scores, 100.)) < 1.
            or np.any((reference_scores <= 8.) & (final_scores > reference_scores + 3.))
            or any(g['after_cm'] > g['before_cm'] + 4. for g in guards)):
        report['reason'] = 'Insufficient gain or degraded pre-existing overlap'
        return trajectory, world_clouds, report
    report['status'] = 'pose_graph'
    fixed = correction.at(track.time) @ matrices(track.positions, track.rotations)
    trajectory = np.column_stack([trajectory[:,0], fixed[:,:3,3], Rotation.from_matrix(fixed[:,:3,:3]).as_quat()])
    clouds = [apply_pose(m, c).astype('f4') for m,c in zip(correction.at(stamps), world_clouds)]
    return trajectory, clouds, report
