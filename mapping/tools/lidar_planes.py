"""Estimate building verticals from mutually consistent indoor walls and floors."""
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

from correct_lio_drift import PoseTrack, apply_pose


def fit_plane(points, rng, vertical=False):
    limit = 1400 if vertical else 900
    if len(points) < 100:
        return None
    sample = points if len(points) <= limit else points[rng.choice(len(points), limit, replace=False)]
    triples = sample[rng.integers(len(sample), size=(160 if vertical else 70, 3))]
    normals = np.cross(triples[:, 1]-triples[:, 0], triples[:, 2]-triples[:, 0])
    norms = np.linalg.norm(normals, axis=1)
    normals /= np.maximum(norms, 1e-10)[:, None]
    eligible = abs(normals[:, 2]) < .27 if vertical else abs(normals[:, 2]) > .93
    eligible &= norms > .05
    if not eligible.any():
        return None
    normals = normals[eligible]
    offsets = np.einsum('ij,ij->i', triples[eligible, 0], normals)
    masks = abs(sample @ normals.T - offsets) < .035
    winner = masks.sum(axis=0).argmax()
    inliers = masks[:, winner]
    if inliers.sum() < 65 or (not vertical and inliers.mean() < .28):
        return None
    selected = sample[inliers]
    centre = selected.mean(axis=0)
    _, singular, axes = np.linalg.svd(selected-centre, full_matrices=False)
    spread = singular / np.sqrt(len(selected))
    if spread[1] < (.18 if vertical else .48) or spread[2] > .025:
        return None
    if vertical and np.ptp(selected[:, 2]) < .65:
        return None
    normal = axes[-1] if axes[-1, 2] >= 0 else -axes[-1]
    return normal, centre, selected


def wall_vertical(points, rng):
    remaining = points[(points[:, 2] > -.2) & (points[:, 2] < 1.4)]
    normals = []
    for _ in range(4):
        fit = fit_plane(remaining, rng, vertical=True)
        if fit is None:
            break
        normal, centre, _ = fit
        for other in normals:
            axis = np.cross(other, normal)
            length = np.linalg.norm(axis)
            if length > .65:
                return axis * np.sign(axis[2])/length
        normals.append(normal)
        remaining = remaining[abs((remaining-centre) @ normal) > .045]
    return None


def plane_height(patch, xy, up):
    normal, centre, _ = patch
    return (centre @ normal - xy @ normal)/(normal @ up)


def largest_vertical_gap(trajectory, windows):
    """Distance travelled with no confirmed building vertical, on a 1 s polyline."""
    time = trajectory[:, 0] - trajectory[0, 0]
    ends = [0.] + [end for _, end in windows]
    starts = [start for start, _ in windows] + [time[-1]]
    longest = None
    for start, end in zip(ends, starts):
        if end <= start:
            continue
        samples = np.r_[np.arange(start, end, 1.), end]
        xyz = np.column_stack([np.interp(samples, time, col) for col in trajectory[:, 1:4].T])
        distance = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
        if longest is None or distance > longest['travel_m']:
            longest = {'start_s': float(start), 'end_s': float(end), 'travel_m': distance}
    return longest


def level_map(trajectory, clouds, up):
    """Rotate the exported coordinates and poses together, keeping the first origin."""
    axis = np.cross(up, [0., 0., 1.])
    sine = np.linalg.norm(axis)
    rot = Rotation.from_rotvec(axis * (np.arctan2(sine, up[2])/max(sine, 1e-12)))
    origin = trajectory[0, 1:4]
    transform = np.eye(4)
    transform[:3, :3] = rot.as_matrix()
    transform[:3, 3] = origin-rot.apply(origin)
    leveled = trajectory.copy()
    leveled[:, 1:4] = apply_pose(transform, trajectory[:, 1:4])
    leveled[:, 4:8] = (rot*Rotation.from_quat(trajectory[:, 4:8])).as_quat()
    return leveled, [apply_pose(transform, cloud).astype('f4') for cloud in clouds], transform


def constrain_planes(trajectory, clouds, cloud_stamps):
    origin = trajectory[0, 0]
    track = PoseTrack(trajectory, origin)
    stamps = np.asarray(cloud_stamps) - origin
    poses = track.at(stamps)
    rng = np.random.default_rng(701)
    observations, patches = [], {}
    for index in range(0, len(stamps), 2):
        local = apply_pose(np.linalg.inv(poses[index]), clouds[index])
        radius = np.linalg.norm(local[:, :2], axis=1)
        local = local[(radius > 1.) & (radius < 9.)]
        floor = fit_plane(local[(local[:, 2] < -.25) & (local[:, 2] > -1.7)], rng)
        if floor is None:
            continue
        patches[index] = floor
        up = wall_vertical(local, rng)
        if up is not None and up @ floor[0] >= np.cos(np.deg2rad(3)):
            # A gently sloping real floor can also pass the agreement check.
            # Use the wall intersection as the plumb line and keep the floor's grade.
            normal = poses[index, :3, :3] @ up
            observations.append((stamps[index], normal/np.linalg.norm(normal)))
    report = {'applied': False, 'wall_floor_observations': len(observations)}
    if len(observations) < 5 or observations[-1][0]-observations[0][0] < 8:
        return trajectory, clouds, dict(report, reason='Too few independent building vertical observations')
    times = np.array([t for t, _ in observations])
    normals = np.stack([n for _, n in observations])
    trusted_times, estimates = [], []
    for t in times:
        nearby = normals[abs(times-t) < 4]
        if len(nearby) < 3:
            continue
        median = np.median(nearby, axis=0)
        median /= np.linalg.norm(median)
        if np.percentile(nearby @ median, 25) >= np.cos(np.deg2rad(3)):
            trusted_times.append(t)
            estimates.append(median)
    if len(estimates) < 5:
        return trajectory, clouds, dict(report, reason='Insufficient agreement between neighbouring wall observations')
    times = np.asarray(trusted_times)
    filtered = np.stack(estimates)
    filtered /= np.linalg.norm(filtered, axis=1, keepdims=True)
    up = np.median(filtered[times < times[0]+6], axis=0)
    up /= np.linalg.norm(up)
    axes = np.cross(filtered, up)
    sine = np.linalg.norm(axes, axis=1)
    angles = np.arctan2(sine, filtered @ up)
    report['confirmed_verticals'] = len(times)
    report['max_tilt_correction_deg'] = float(np.degrees(angles.max()))
    if np.max(angles) > np.deg2rad(45):
        return trajectory, clouds, dict(report, reason='Inconsistent building axes')
    vectors = axes * (angles/np.maximum(sine, 1e-10))[:, None]
    rotations = Rotation.from_rotvec(np.column_stack([np.interp(track.time, times, v) for v in vectors.T]))
    deltas = np.diff(track.positions, axis=0)
    deltas = .5 * (rotations[:-1].apply(deltas) + rotations[1:].apply(deltas))
    xyz = track.positions[0] + np.vstack([np.zeros(3), np.cumsum(deltas, axis=0)])
    tilted = np.column_stack([trajectory[:, 0], xyz, (rotations*track.rotations).as_quat()])
    level_poses = PoseTrack(tilted, origin).at(stamps)
    previous = None
    shifts = np.zeros(len(stamps))
    shared_patches = 0
    for idx, (normal, centre, points) in patches.items():
        pose = level_poses[idx]
        n = pose[:3, :3] @ normal
        if n @ up < np.cos(np.deg2rad(5)) or np.min(abs(times-stamps[idx])) > 8:
            previous = None
            continue
        surface = apply_pose(pose, points)
        flat = surface - np.outer(surface @ up, up)
        current = (n, apply_pose(pose, centre), flat)
        if previous is not None:
            last, old = previous
            if stamps[idx]-stamps[last] < 1.1 and old[0] @ n > np.cos(np.deg2rad(3)):
                near = cKDTree(old[2]).query(flat)[0] < .25
                if near.sum() >= 45 and near.mean() > .25:
                    query = flat[near].mean(axis=0)
                    error = plane_height(current, query, up) - plane_height(old, query, up)
                    # An actual step or landing transition may change the plane's height.
                    if abs(error) < .07:
                        shifts[last+1:idx+1] -= error / (idx-last)
                        shared_patches += 1
        previous = idx, current
    xyz += np.outer(np.interp(track.time, stamps, np.cumsum(shifts)), up)
    tilted[:, 1:4] = xyz
    change = PoseTrack(tilted, origin).at(stamps) @ np.linalg.inv(poses)
    # The graph may change yaw freely. Preserve measured inclinations only near
    # actual observations, with no vertical prior across a stairwell or long gap.
    groups = np.split(times, np.flatnonzero(np.diff(times) > 2.) + 1)
    report.update(applied=True, shared_floor_intervals=shared_patches,
                  building_up=up.tolist(),
                  vertical_windows_s=[[float(g[0]), float(g[-1])] for g in groups])
    return tilted, [apply_pose(m, c).astype('f4') for m,c in zip(change, clouds)], report
