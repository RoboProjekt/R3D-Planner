"""Refine a recorded RGB-D mount using same-time Hesai scans and held-out depth frames."""

import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

from correct_lio_drift import apply_pose


def surface_samples(grid):
    centre = grid[2:-2:3, 2:-2:3]
    du = grid[2:-2:3, 4::3] - grid[2:-2:3, :-4:3]
    dv = grid[4::3, 2:-2:3] - grid[:-4:3, 2:-2:3]
    normals = np.cross(du, dv)
    lengths = np.linalg.norm(normals, axis=2)
    valid = (np.isfinite(centre).all(axis=2) & np.isfinite(lengths) & (lengths > 1e-5)
             & (centre[:, :, 2] > .35) & (centre[:, :, 2] < 6.)
             & (np.linalg.norm(du, axis=2) < .22) & (np.linalg.norm(dv, axis=2) < .22))
    return centre[valid], normals[valid] / lengths[valid, None]


def geometry_sample(query, grid, depth):
    surface, normals = surface_samples(grid)
    x, y, z = query.T
    query = query[(z > .3) & (z < 6.5) & (abs(x) < 1.05*z) & (abs(y) < .75*z)]
    if len(surface) < 150 or len(query) < 70:
        return None
    return query, surface, normals, cKDTree(surface), depth


def fit_transform(scans):
    transform = np.eye(4)
    for iteration in range(30):
        jacobians, residuals = [], []
        limit = max(.11, .45 * .91**iteration)
        for query, surface, normals, tree, _ in scans:
            moved = apply_pose(transform, query)
            distances, nearest = tree.query(moved, distance_upper_bound=limit)
            matched = np.isfinite(distances)
            if matched.sum() < 40:
                continue
            xyz = moved[matched]
            n = normals[nearest[matched]]
            err = np.einsum('ij,ij->i', xyz - surface[nearest[matched]], n)
            weight = np.sqrt(np.minimum(1., .035 / np.maximum(abs(err), 1e-6)) / len(err))
            jacobians.append(weight[:, None] * np.column_stack([np.cross(xyz, n), n]))
            residuals.append(-weight * err)
        if len(jacobians) < 5:
            return None
        step, _, rank, _ = np.linalg.lstsq(np.vstack(jacobians), np.concatenate(residuals), rcond=None)
        if rank < 6:
            return None
        increment = np.eye(4)
        increment[:3, :3] = Rotation.from_rotvec(step[:3]).as_matrix()
        increment[:3, 3] = step[3:]
        transform = increment @ transform
        if np.linalg.norm(step) < .00008:
            break
    return transform


def ray_errors(query, depth, intrinsics):
    width, height, k, _ = intrinsics
    err = np.full(len(query), np.nan)
    indices = np.flatnonzero(query[:, 2] > .3)
    x, y, z = query[indices].T
    u = np.rint(k[0, 0] * x / z + k[0, 2]).astype(int)
    v = np.rint(k[1, 1] * y / z + k[1, 2]).astype(int)
    ok = (u >= 0) & (u < width) & (v >= 0) & (v < height)
    err[indices[ok]] = abs(depth[v[ok], u[ok]] - z[ok])
    return err


def validate(scans, camera, transform):
    pairs = []
    for query, _, _, _, depth in scans:
        before = ray_errors(query, depth, camera)
        after = ray_errors(apply_pose(transform, query), depth, camera)
        common = np.isfinite(before) & np.isfinite(after)
        if common.sum() >= 40:
            pairs.append([np.median(before[common]), np.median(after[common])])
    return pairs


def modest(transform, metres, degrees):
    return (transform is not None and np.linalg.norm(transform[:3, 3]) <= metres
            and Rotation.from_matrix(transform[:3, :3]).magnitude() <= np.deg2rad(degrees))


def refine_mount(scans, camera):
    """Return a correction in depth-optical coordinates or identity on weak evidence."""
    report = {'applied': False, 'calibration_pairs': len(scans), 'validation': []}
    if len(scans) < 24:
        return np.eye(4), report
    fits = []
    for fold in (0, 1):
        transform = fit_transform(scans[fold::2])
        if not modest(transform, .16, 5.):
            return np.eye(4), report
        pairs = np.asarray(validate(scans[1-fold::2], camera, transform))
        if len(pairs) < 10:
            return np.eye(4), report
        before, after = np.median(pairs, axis=0)
        improved = int(np.count_nonzero(pairs[:, 1] < pairs[:, 0]))
        report['validation'].append(dict(frames=len(pairs), improved=improved,
                                        median_before_cm=100*before, median_after_cm=100*after))
        if after > min(.9*before, before-.01) or improved < .66*len(pairs):
            return np.eye(4), report
        fits.append(transform)
    if not modest(fits[0] @ np.linalg.inv(fits[1]), .08, 2.5):
        return np.eye(4), report
    transform = fit_transform(scans)
    if not modest(transform, .16, 5.):
        return np.eye(4), report
    report.update(applied=True, optical_correction=transform.tolist())
    return transform, report
