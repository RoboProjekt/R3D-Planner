#!/usr/bin/env python3
"""Correct a completed FAST-LIO replay using verified revisits in an SE(3) pose graph.

Input timestamps in the protocol are seconds since the first ROS bag record.
Each loop is a candidate observation, not a requirement that the poses coincide.
"""
import argparse
import json
from pathlib import Path
import tempfile

import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation, Slerp


def apply_pose(pose, xyz):
    return xyz @ pose[:3, :3].T + pose[:3, 3]


def matrices(xyz, rotations):
    poses = np.tile(np.eye(4), (len(xyz), 1, 1))
    poses[:, :3, :3] = rotations.as_matrix()
    poses[:, :3, 3] = xyz
    return poses


def interpolate(times, positions, rotations, query):
    query = np.clip(query, times[0], times[-1])
    xyz = np.column_stack([np.interp(query, times, col) for col in positions.T])
    return xyz, Slerp(times, rotations)(query)


def voxel(points, size):
    keys = np.floor(points / size).astype(np.int64)
    _, idx = np.unique(keys, axis=0, return_inverse=True)
    counts = np.bincount(idx)
    return np.column_stack([np.bincount(idx, weights=col)/counts for col in points.T])


class PoseTrack:
    def __init__(self, trajectory, origin):
        self.time = trajectory[:, 0] - origin
        self.positions = trajectory[:, 1:4]
        self.rotations = Rotation.from_quat(trajectory[:, 4:8])

    def at(self, times):
        xyz, rot = interpolate(self.time, self.positions, self.rotations, times)
        return matrices(xyz, rot)


class Replay(PoseTrack):
    def __init__(self, path):
        manifest = json.loads((path/'manifest.json').read_text())
        if (manifest['status'] != 'replayed' or not manifest['verified_use_sim_time']
                or manifest['nonfinite_posterior_values'] or manifest['player_exit_code'] != 0
                or manifest['estimator_exit_code'] != 0):
            raise ValueError('A completed native-clock replay is required')
        self.origin = manifest['first_record_ns'] / 1e9
        with np.load(path/'outputs.npz') as data:
            self.trajectory = data['trajectory']
            self.points = data['registered_points']
            self.offsets = data['cloud_offsets']
            self.stamps = data['cloud_stamps'] - self.origin
        super().__init__(self.trajectory, self.origin)
        if (len(self.time) < 2 or not np.isfinite(self.trajectory).all() or not np.isfinite(self.stamps).all()
                or not np.isfinite(self.points).all() or np.any(np.diff(self.time) <= 0)
                or np.any(np.diff(self.stamps) <= 0) or len(self.offsets) != len(self.stamps)+1
                or self.offsets[0] != 0 or np.any(np.diff(self.offsets) < 0)
                or self.offsets[-1] != len(self.points)):
            raise ValueError('Invalid replay timestamps or point-cloud offsets')

    def local_cloud(self, centre, half_width=.6, correction=None):
        indices = np.flatnonzero(abs(self.stamps-centre) <= half_width)
        if len(indices) < 2:
            raise ValueError(f'Insufficient registered scans near {centre:g} s')
        chunks = []
        centres = self.at(self.stamps[indices])[:, :3, 3]
        transforms = correction.at(self.stamps[indices]) if correction is not None else None
        for k, (idx, sensor) in enumerate(zip(indices, centres)):
            xyz = self.points[self.offsets[idx]:self.offsets[idx+1]]
            distance = np.linalg.norm(xyz-sensor, axis=1)
            selected = xyz[(distance >= .8) & (distance <= 8.)]
            chunks.append(apply_pose(transforms[k], selected) if transforms is not None else selected)
        cloud = voxel(np.concatenate(chunks), .07)
        if len(cloud) < 32:
            raise ValueError(f'Insufficient nearby points at {centre:g} s')
        return cloud


def distances(a, b):
    neighbours = [cKDTree(x).query(y)[0] for x, y in ((a, b), (b, a))]
    return {'median_cm': float(100*np.mean([np.median(v) for v in neighbours])),
            'overlap_20cm': float(np.mean([(v < .2).mean() for v in neighbours])),
            'overlap_each_direction': [float((v < .2).mean()) for v in neighbours]}


def align(target, source, initial):
    pose = initial.copy()
    for width, max_dist in ((.22, .95), (.12, .55), (.075, .30)):
        ref, src = voxel(target, width), voxel(source, width)
        if min(len(ref), len(src)) < 32:
            raise ValueError('Insufficient geometry for registration')
        tree = cKDTree(ref)
        neighbours = ref[tree.query(ref, k=12)[1]]
        offsets = neighbours - neighbours.mean(axis=1, keepdims=True)
        eig, axes = np.linalg.eigh(offsets.transpose(0, 2, 1) @ offsets / 12)
        usable = (eig[:, 0] < .18*eig[:, 1]) & (eig[:, 1] > (.15*width)**2)
        for _ in range(35):
            p = apply_pose(pose, src)
            dist, idx = tree.query(p)
            ok = (dist < max_dist) & usable[idx]
            if np.count_nonzero(ok) < 30:
                raise ValueError('Insufficient overlapping surface normals')
            p, q, n = p[ok], ref[idx[ok]], axes[idx[ok], :, 0]
            residual = np.einsum('ij,ij->i', n, p-q)
            pivot = p.mean(axis=0)
            J = np.column_stack([n, np.cross(p-pivot, n)])
            weights = np.sqrt(np.minimum(1., (.45*width)/np.maximum(abs(residual), 1e-9)))
            delta, _, rank, _ = np.linalg.lstsq(J*weights[:, None], -residual*weights, rcond=1e-5)
            if rank != 6:
                raise ValueError('Underconstrained scan match')
            rot = Rotation.from_rotvec(delta[3:]).as_matrix()
            step = np.eye(4)
            step[:3, :3], step[:3, 3] = rot, pivot+delta[:3]-rot@pivot
            pose = step @ pose
            if np.linalg.norm(delta) < .0002:
                break
    return pose


def verify_loop(replay, spec, discovered=False, centre_seed=False):
    first, last = spec['times']
    result = dict(spec, accepted=False)
    try:
        a, b = replay.local_cloud(first), replay.local_cloud(last)
        poses = replay.at([first, last])
        before = distances(a, b)
        result['before'] = before
        seed = np.eye(4)
        if centre_seed:
            seed[:3, 3] = poses[0, :3, 3] - poses[1, :3, 3]
        forward = align(a, b, seed)
        reverse = align(b, a, np.linalg.inv(seed))
    except ValueError as e:
        return dict(result, reason=str(e)), None
    fixed = apply_pose(forward, b)
    after = distances(a, fixed)
    check = reverse @ forward
    centre = poses[1, :3, 3]
    roundtrip = float(np.linalg.norm(apply_pose(check, centre)-centre))
    angle = float(np.degrees(Rotation.from_matrix(check[:3, :3]).magnitude()))
    correction = float(np.linalg.norm(apply_pose(forward, centre)-centre))
    correction_angle = float(np.degrees(Rotation.from_matrix(forward[:3, :3]).magnitude()))
    result.update(after=after, roundtrip_m=roundtrip, roundtrip_deg=angle,
                  correction_m=correction, correction_deg=correction_angle)
    # Conservative checks for this indoor replay. A poorly constrained or
    # incompatible match must not connect distinct floors of a staircase.
    if (min(after['overlap_each_direction']) < .42 or after['median_cm'] > 18
            or roundtrip > .15 or angle > 2 or correction > (12. if centre_seed else 2.5) or correction_angle > 20
            or after['median_cm'] > before['median_cm'] + 1):
        return dict(result, reason='Geometric consistency gate'), None
    if discovered and (min(after['overlap_each_direction']) < .60 or after['median_cm'] > 11
                       or roundtrip > .08 or angle > 1.3):
        return dict(result, reason='Insufficient support for automatic loop'), None
    measurement = np.linalg.inv(poses[0]) @ forward @ poses[1]
    return dict(result, accepted=True, relative_body_pose=measurement.tolist()), measurement


def confirm_known_revisit(replay, revisit):
    pairs = revisit['pairs']
    if len(pairs) != 2 or any(abs(x-y) <= 1.2 for x, y in zip(*pairs)):
        raise ValueError('Provide two separate, nonoverlapping scan pairs for a known revisit')
    matches, estimates = [], []
    for first, last in pairs:
        spec = {'name': revisit['name'], 'times': [first, last]}
        result, relative = verify_loop(replay, spec, discovered=True, centre_seed=True)
        matches.append(result)
        if relative is not None:
            a, b = replay.at([first, last])
            estimates.append(a @ relative @ np.linalg.inv(b))
    report = dict(revisit, accepted=False, matches=matches)
    if len(estimates) != 2:
        return dict(report, reason='Both registrations must pass'), None
    pivot = replay.at([pairs[1][1]])[0, :3, 3]
    delta = np.linalg.norm(apply_pose(estimates[0], pivot) - apply_pose(estimates[1], pivot))
    angle = np.degrees(Rotation.from_matrix(estimates[0][:3,:3].T @ estimates[1][:3,:3]).magnitude())
    report.update(disagreement_m=float(delta), disagreement_deg=float(angle))
    if delta > .20 or angle > 2:
        return dict(report, reason='Two registrations disagree'), None
    first, last = pairs[0]
    return dict(report, accepted=True), (first, last, np.asarray(matches[0]['relative_body_pose']))


def revisit_candidates(replay, reserved_times):
    """Propose spatially nearby keyframes separated by a substantial excursion."""
    times = np.arange(np.ceil(replay.time[0]), replay.time[-1], 3.)
    # Keep evaluation scans out of both visits, including their aggregation windows.
    times = np.array([t for t in times if all(abs(t - check) > 1.2 for check in reserved_times)])
    if len(times) < 2:
        return
    points = replay.at(times)[:, :3, 3]
    for i, t in enumerate(times):
        distance = np.linalg.norm(points - points[i], axis=1)
        nearby = np.flatnonzero((times < t - 24) & (distance < 3)
                                & (abs(points[:, 2] - points[i, 2]) < 1.1))
        proposed = []
        for j in sorted(nearby, key=lambda j: distance[j]):
            if any(abs(times[j] - prev) < 6 for prev in proposed):
                continue
            excursion = np.linalg.norm(points[j:i+1] - points[i], axis=1)
            if max(excursion) < 5:
                continue
            yield {'name': f'Automatisch {times[j]:g}/{t:g} s', 'times': [float(times[j]), float(t)]}
            proposed.append(times[j])
            if len(proposed) == 3:
                break


def optimize(times, baseline, loops, *, vertical_nodes=(), building_up=None):
    count = len(times)
    xyz = baseline[:, :3, 3]
    base = Rotation.from_matrix(baseline[:, :3, :3])
    i, j = np.arange(count-1), np.arange(1, count)
    step = np.linalg.norm(np.diff(xyz, axis=0), axis=1)
    turn = (base[:-1].inv()*base[1:]).magnitude()
    # Distance, rotation and elapsed time allocate relative odometry uncertainty.
    scale = np.sqrt(np.maximum(.02, step+.35*turn+.015*np.diff(times)))
    sigma_t, sigma_r = .07*scale, np.deg2rad(1.4)*scale
    measures = np.linalg.inv(baseline[:-1]) @ baseline[1:]
    if loops:
        i = np.r_[i, [edge[0] for edge in loops]]
        j = np.r_[j, [edge[1] for edge in loops]]
        measures = np.concatenate([measures, np.array([edge[2] for edge in loops])])
        sigma_t = np.r_[sigma_t, np.full(len(loops), .06)]
        sigma_r = np.r_[sigma_r, np.full(len(loops), np.deg2rad(1.0))]
    relative_inv = Rotation.from_matrix(measures[:, :3, :3]).inv()
    vertical_nodes = np.asarray(vertical_nodes, dtype=int)
    if len(vertical_nodes):
        local_up = base[vertical_nodes].inv().apply(building_up)

    def decode(flat):
        change = np.vstack([np.zeros(6), flat.reshape(-1, 6)])
        return xyz+change[:, :3], Rotation.from_rotvec(change[:, 3:])*base

    def residual(flat):
        pos, rotation = decode(flat)
        inv = rotation[i].inv()
        dt = inv.apply(pos[j]-pos[i])-measures[:, :3, 3]
        dr = (relative_inv*inv*rotation[j]).as_rotvec()
        relative = np.column_stack([dt/sigma_t[:, None], dr/sigma_r[:, None]]).ravel()
        if not len(vertical_nodes):
            return relative
        tilt = rotation[vertical_nodes].apply(local_up) - building_up
        return np.r_[relative, tilt.ravel()/np.deg2rad(1.)]

    pattern = lil_matrix((len(i)*6 + len(vertical_nodes)*3, (count-1)*6), dtype=np.int8)
    for e, ends in enumerate(zip(i, j)):
        for node in ends:
            if node:
                pattern[6*e:6*e+6, 6*(node-1):6*node] = 1
    for row, node in enumerate(vertical_nodes):
        if node:
            start = len(i)*6 + row*3
            pattern[start:start+3, 6*(node-1)+3:6*node] = 1
    fit = least_squares(residual, np.zeros((count-1)*6), jac_sparsity=pattern.tocsr(),
                        tr_options={'atol': 1e-8, 'btol': 1e-8, 'maxiter': 2000},
                        max_nfev=100, ftol=1e-7, xtol=1e-8)
    if not fit.success or not np.isfinite(fit.x).all():
        raise ValueError(f'Pose graph did not converge: {fit.message}')
    return matrices(*decode(fit.x))


class Correction:
    def __init__(self, replay, times, before, after):
        self.replay, self.times = replay, times
        self.translation = after[:, :3, 3]-before[:, :3, 3]
        self.rotation = Rotation.from_matrix(after[:, :3, :3]) * Rotation.from_matrix(before[:, :3, :3]).inv()

    def at(self, times):
        offset, rot = interpolate(self.times, self.translation, self.rotation, times)
        pivot = self.replay.at(times)[:, :3, 3]
        return matrices(pivot+offset-rot.apply(pivot), rot)

def write_pcd(path, xyz):
    with path.open('wb') as f:
        f.write(('# .PCD v0.7\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\n'
                 f'WIDTH {len(xyz)}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {len(xyz)}\nDATA binary\n').encode())
        xyz.astype('<f4').tofile(f)


def run(run_path, protocol, output, discover=False, trajectory_only=False, raw_room_bag=None):
    if output.exists():
        raise FileExistsError(output)
    config = json.loads(protocol.read_text()) if protocol else {}
    loops, checks = config.get('loops', []), config.get('checks', [])
    replay = Replay(run_path)
    candidates = list(loops)
    known = config.get('known_revisit')
    if raw_room_bag is not None and known is None:
        raise ValueError('--raw-room-bag needs a confirmed revisit in the protocol')
    reserved = [t for check in checks for t in check['times']] + config.get('reference_times', [])
    if known:
        pairs = np.asarray(known['pairs'], dtype=float)
        if (pairs.shape != (2, 2) or not np.isfinite(pairs).all() or np.any(pairs[:, 0] >= pairs[:, 1])
                or np.any(abs(pairs[0] - pairs[1]) <= 1.2)):
            raise ValueError('A known revisit needs two distinct, ordered pairs of scan times')
        if any(abs(t - check) <= 1.2 for t in pairs.ravel() for check in reserved):
            raise ValueError('Known revisit overlaps a reserved evaluation window')
    if discover:
        candidates.extend(revisit_candidates(replay, reserved))
    endpoints = [t for loop in candidates for t in loop['times']]
    if known:
        endpoints.extend(t for pair in known['pairs'] for t in pair)
    if not endpoints or any(t < replay.time[0] or t > replay.time[-1] for t in endpoints):
        raise ValueError('Candidate times outside replay or no candidates')
    matches, measurements, checks_out = [], [], {}
    for idx, loop in enumerate(candidates):
        first, last = loop['times']
        automatic = idx >= len(loops)
        if automatic and any(abs(first - a) < 5 and abs(last - b) < 5 for a, b, _ in measurements):
            continue
        result, relative = verify_loop(replay, loop, discovered=automatic)
        result['automatic'] = automatic
        matches.append(result)
        if relative is not None:
            measurements.append((first, last, relative))
        print(loop['name'], result['accepted'], result.get('reason', ''), flush=True)
    known_result = None
    if known:
        first, last = known['pairs'][0]
        already_matched = any(abs(a - first) < 16 and abs(b - last) < 16 for a, b, _ in measurements)
        if already_matched:
            known_result = dict(known, accepted=False, reason='Revisit already matched nearby')
        else:
            if raw_room_bag is None:
                known_result, edge = confirm_known_revisit(replay, known)
            else:
                from raw_lio_revisit import raw_revisit
                known_result, edge = raw_revisit(replay, run_path, raw_room_bag, known)
            if edge is not None:
                measurements.append(edge)
    if not measurements:
        raise ValueError('No verified loop. No corrected map produced.')
    used_times = [t for a, b, _ in measurements for t in (a, b)]
    times = np.unique(np.r_[np.arange(replay.time[0], replay.time[-1], 2.), used_times, replay.time[-1]])
    base = replay.at(times)
    edges = [(np.searchsorted(times, a), np.searchsorted(times, b), rel) for a, b, rel in measurements]
    nodes = optimize(times, base, edges)
    corr = Correction(replay, times, base, nodes)
    for spec in checks:
        a, b = spec['times']
        try:
            before = distances(replay.local_cloud(a), replay.local_cloud(b))
            after = distances(replay.local_cloud(a, correction=corr), replay.local_cloud(b, correction=corr))
            checks_out[spec['name']] = dict(times=[a, b], before=before, after=after)
        except ValueError as exc:
            checks_out[spec['name']] = dict(times=[a, b], reason=str(exc))
    output.parent.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        stage = Path(tmp)/output.name
        stage.mkdir()
        if not trajectory_only:
            mats = corr.at(replay.stamps)
            adjusted = np.concatenate([apply_pose(m, replay.points[a:b])
                                       for m, a, b in zip(mats, replay.offsets[:-1], replay.offsets[1:])])
            write_pcd(stage/'karte.pcd', voxel(adjusted, .08))
            write_pcd(stage/'karte_vorher.pcd', voxel(replay.points, .08))
        c = corr.at(replay.time)
        corrected_poses = c @ matrices(replay.positions, replay.rotations)
        trajectory = np.column_stack([replay.trajectory[:, 0], corrected_poses[:, :3, 3],
                                      Rotation.from_matrix(corrected_poses[:, :3, :3]).as_quat()])
        np.savez_compressed(stage/'trajectory.npz', trajectory=trajectory, node_times_s=times,
                            original_nodes=base, corrected_nodes=nodes)
        report = dict(run=str(run_path.resolve()), protocol=config, discover=discover, origin_unix_s=replay.origin,
                      loops=matches, known_revisit=known_result, validation=checks_out, nodes=len(times))
        (stage/'metrics.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
        stage.rename(output)
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True, help='Completed replay directory')
    p.add_argument('--output', type=Path, required=True, help='New output directory')
    p.add_argument('--protocol', type=Path, help='Optional proposed loop times and validation windows')
    p.add_argument('--discover', action='store_true', help='Search the trajectory for additional verified revisits')
    p.add_argument('--raw-room-bag', type=Path, help='Use raw Hesai scans for the optional known-room fallback')
    p.add_argument('--trajectory-only', action='store_true', help='Skip writing the two point-cloud files')
    args = p.parse_args()
    if not args.protocol and not args.discover:
        p.error('Provide --discover or a protocol with candidate loops')
    run(args.run, args.protocol, args.output, args.discover, args.trajectory_only, args.raw_room_bag)
