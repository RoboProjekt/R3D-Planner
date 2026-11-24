"""Anchor a floor revisit to its first supported observations in the building frame."""
from functools import lru_cache

import numpy as np
from scipy.ndimage import median_filter
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

from correct_lio_drift import PoseTrack, apply_pose
from lidar_planes import fit_plane


def visit_windows(stamps, xyz, loops):
    travel = np.r_[0., np.cumsum(np.linalg.norm(np.diff(xyz, axis=0), axis=1))]
    # A climb or descent separates two floor visits, including when their XY footprints coincide.
    left = np.searchsorted(stamps, stamps - 1.)
    right = np.minimum(np.searchsorted(stamps, stamps + 1.), len(stamps)-1)
    steep = abs(xyz[right, 2]-xyz[left, 2]) > np.maximum(.18, .15*(travel[right]-travel[left]))
    segment = np.cumsum(np.r_[False, steep[1:] != steep[:-1]])
    candidates = {}

    def window(centre):
        return np.flatnonzero((segment == segment[centre]) & (abs(travel-travel[centre]) < 28.)
                              & (abs(stamps-stamps[centre]) < 40.))
    for first, later in loops:
        a, b = [np.argmin(abs(stamps-t)) for t in sorted((first, later))]
        if b <= a or steep[a] or steep[b]:
            continue
        excursion = np.linalg.norm(xyz[a:b+1]-xyz[a], axis=1)
        if excursion.max() < 4.:
            continue
        split = a + int(np.argmax(excursion))
        earlier, later_scans = window(a), window(b)
        earlier = earlier[earlier < split]
        for j in later_scans[later_scans > split]:
            near = earlier[(stamps[j]-stamps[earlier] > 18.) &
                           (np.linalg.norm(xyz[earlier, :2]-xyz[j, :2], axis=1) < 2.6) &
                           (abs(xyz[earlier, 2]-xyz[j, 2]) < .65)]
            if len(near):
                candidates.setdefault(j, set()).update(near.tolist())
    return candidates, segment


def revisit_floor(points, centre, scan):
    delta = points-centre
    radius = np.linalg.norm(delta[:, :2], axis=1)
    near = points[(radius > .8) & (radius < 4.8) & (delta[:, 2] > -1.45) & (delta[:, 2] < -.28)]
    floor = fit_plane(near, np.random.default_rng(912+scan))
    if floor is None or floor[0][2] < .985:
        return None
    normal, origin, inliers = floor
    # Use nearby contacts to refine inclination; retain the full observed
    # footprint to check that the two scans actually cover the same ground.
    close = inliers[np.linalg.norm(inliers[:, :2]-centre[:2], axis=1) < 3.3]
    if len(close) >= 65:
        local_origin = close.mean(axis=0)
        _, spans, axes = np.linalg.svd(close-local_origin, full_matrices=False)
        up = axes[-1]*np.sign(axes[-1, 2])
        if spans[1]/np.sqrt(len(close)) > .45 and up @ normal > np.cos(np.deg2rad(1.5)):
            normal, origin = up, local_origin
    return normal, origin, inliers, cKDTree(inliers[:, :2])


def match_floor(reference, current, pivot):
    n, c, _, tree = reference
    m, _, points, _ = current
    if n @ m < np.cos(np.deg2rad(6.)):
        return None
    shared = points[tree.query(points[:, :2])[0] < .24]
    if len(shared) < max(45, .20*len(points)):
        return None
    spread = np.linalg.svd(shared[:, :2]-shared[:, :2].mean(axis=0), compute_uv=False)
    if spread[1]/np.sqrt(len(shared)) < .30:
        return None
    axis = np.cross(m, n)
    sine = np.linalg.norm(axis)
    rv = axis * (np.arctan2(sine, np.dot(m, n))/max(sine, 1e-12))
    rot = Rotation.from_rotvec(rv)
    residual = (c-(rot.apply(shared-pivot)+pivot)) @ n/n[2]
    shift = (c-(rot.apply(current[1]-pivot)+pivot)) @ n/n[2]
    if abs(shift) > .55 or np.percentile(abs(residual-shift), 85) > .045:
        return None
    return np.r_[rv, shift]


def scene_score(points, references, centre, value):
    """Compare the rigid floor correction on returns above the floor."""
    if len(points) < 45 or len(references) < 45:
        return None
    query = points[::max(1, len(points)//350)]
    shifted = Rotation.from_rotvec(value[:3]).apply(query-centre)+centre
    shifted[:, 2] += value[3]
    tree = cKDTree(references)
    before = tree.query(query)[0]
    after = tree.query(shifted)[0]
    common = np.minimum(before, after) < .25
    if common.sum() < max(40, .25*len(query)):
        return None
    return np.mean(np.minimum(before[common], .35)), np.mean(np.minimum(after[common], .35))


def first_visit_anchors(trajectory, clouds, cloud_stamps, loops):
    origin = trajectory[0, 0]
    stamps = np.asarray(cloud_stamps)-origin
    summary = dict(applied=False, corrected_scans=0)
    if not loops or len(stamps) < 3:
        return trajectory, clouds, summary
    track = PoseTrack(trajectory, origin)
    poses = track.at(stamps)
    xyz = poses[:, :3, 3]
    candidates, segment = visit_windows(stamps, xyz, loops)

    @lru_cache(maxsize=512)
    def patch(i):
        return revisit_floor(clouds[i], xyz[i], int(i))

    @lru_cache(maxsize=160)
    def surroundings(i):
        d = clouds[i]-xyz[i]
        radius = np.linalg.norm(d[:, :2], axis=1)
        return clouds[i][(radius > 1.2) & (radius < 6.) & (d[:, 2] > -.12) & (d[:, 2] < 2.5)]

    estimates = np.zeros((len(stamps), 4))
    matched = np.zeros(len(stamps), dtype=bool)
    veto = np.zeros(len(stamps), dtype=bool)
    for j, choices in sorted(candidates.items()):
        current = patch(j)
        if current is None:
            continue
        ordered = np.array(sorted(choices))
        # Older visits define the reference. A corrected later pass cannot become a new datum.
        splits = np.flatnonzero(np.diff(stamps[ordered]) > 4.)+1
        for visit in np.split(ordered, splits):
            visit = visit[~matched[visit]]
            visit = sorted(visit, key=lambda i: np.linalg.norm(xyz[i, :2]-xyz[j, :2]))[:16]
            votes, witnesses = [], []
            for i in visit:
                ref = patch(i)
                value = None if ref is None else match_floor(ref, current, xyz[j])
                if value is not None:
                    votes.append(value)
                    witnesses.append(i)
            if len(votes) < 3:
                continue
            values = np.asarray(votes)
            median = np.median(values, axis=0)
            agree = (abs(values[:, 3]-median[3]) < .045) & (np.linalg.norm(
                values[:, :3]-median[:3], axis=1) < np.deg2rad(2.))
            if np.count_nonzero(agree) < max(3, .65*len(votes)) or np.ptp(stamps[np.asarray(witnesses)[agree]]) < .45:
                continue
            value = np.median(values[agree], axis=0)
            support = np.asarray(witnesses)[agree]
            scene = np.concatenate([surroundings(i)[::2] for i in support[:5]])
            scores = scene_score(surroundings(j), scene, xyz[j], value)
            if scores is None:
                continue
            if scores[1] > scores[0]+.012:
                veto[j] = True
                continue
            estimates[j] = value
            matched[j] = True
            break
    params = np.zeros_like(estimates)
    anchors = np.flatnonzero(matched)
    cuts = ((np.diff(stamps[anchors]) > 1.6) | (np.diff(segment[anchors]) != 0) |
            (np.diff(np.cumsum(veto & ~matched)[anchors]) != 0))
    for block in np.split(anchors, np.flatnonzero(cuts)+1):
        if len(block) < 4 or np.ptp(stamps[block]) < 1.:
            continue
        samples = np.arange(block[0], block[-1]+1)
        filtered = median_filter(estimates[block], size=(3, 1), mode='nearest')
        fit = np.column_stack([np.interp(stamps[samples], stamps[block], col) for col in filtered.T])
        gain = np.minimum(1.,(stamps[samples]-stamps[block[0]])/.8)
        if block[-1] != len(stamps)-1:
            gain = np.minimum(gain,(stamps[block[-1]]-stamps[samples])/.8)
        params[samples] = fit*gain[:, None]
    use = np.flatnonzero(np.any(params != 0., axis=1))
    if not len(use):
        return trajectory, clouds, summary
    correction = np.column_stack([np.interp(track.time, stamps, v) for v in params.T])
    fixed = trajectory.copy()
    moving = np.any(correction != 0., axis=1)
    fixed[moving, 3] += correction[moving, 3]
    fixed[moving, 4:] = (Rotation.from_rotvec(correction[moving, :3]) *
                         Rotation.from_quat(trajectory[moving, 4:])).as_quat()
    change = PoseTrack(fixed, origin).at(stamps[use]) @ np.linalg.inv(poses[use])
    new_clouds = list(clouds)
    for i, transform in zip(use, change):
        new_clouds[i] = apply_pose(transform, clouds[i]).astype('f4')
    summary.update(applied=True, corrected_scans=len(use), matched_scans=int(matched.sum()),
                   first_correction_s=float(stamps[use[0]]), max_shift_m=float(abs(params[:,3]).max()),
                   max_tilt_deg=float(np.rad2deg(np.linalg.norm(params[:,:3], axis=1).max())))
    return fixed, new_clouds, summary
