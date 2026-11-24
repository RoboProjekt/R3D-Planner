#!/usr/bin/env python3
"""Export a dense structural view of a Z-up Hesai map using nearby, repeated measurements."""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import tempfile

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from correct_lio_drift import write_pcd


@dataclass
class Patch:
    kind: str
    normal: np.ndarray
    centre: np.ndarray
    samples: np.ndarray


def representatives(points, indices, ranges, spacing=.065):
    cells = np.floor(points[indices]/spacing).astype(np.int64)
    _, cell = np.unique(cells, axis=0, return_inverse=True)
    order = np.lexsort((ranges[indices], cell))
    return indices[order[np.r_[True, np.diff(cell[order]) != 0]]]


def fit_faces(points, rng):
    """Propose floors and walls separately, then estimate their unconstrained inclinations."""
    if len(points) < 28:
        return {}
    triples = points[rng.integers(len(points), size=(100, 3))]
    normals = np.cross(triples[:, 1]-triples[:, 0], triples[:, 2]-triples[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    valid = lengths > .025
    normals /= np.maximum(lengths, 1e-12)[:, None]
    proposals = {'horizontal': valid & (abs(normals[:, 2]) > .99),
                 'vertical': valid & (abs(normals[:, 2]) < .12)}
    faces = {}
    for kind, use in proposals.items():
        if not use.any():
            continue
        offsets = (normals[use]*triples[use, 0]).sum(axis=1)
        residual = abs(points @ normals[use].T-offsets)
        mask = residual[:, (residual < .023).sum(axis=0).argmax()] < .023
        for _ in range(3):
            if mask.sum() < max(24, .28*len(points)):
                break
            inliers = points[mask]
            centre = inliers.mean(axis=0)
            _, singular, axes = np.linalg.svd(inliers-centre, full_matrices=False)
            normal = axes[-1]
            mask = abs((points-centre) @ normal) < .029
        else:
            if singular[1]/np.sqrt(len(inliers)) < .135:
                continue
            if kind == 'horizontal' and abs(normal[2]) < np.cos(np.deg2rad(1.25)):
                continue
            if kind == 'vertical' and (abs(normal[2]) > np.sin(np.deg2rad(3.)) or np.ptp(inliers[:, 2]) < .5):
                continue
            faces[kind] = normal, centre
    return faces


def constrained_plane(points, kind):
    centre = np.median(points, axis=0)
    if kind == 'horizontal':
        return np.array([0., 0., 1.]), centre
    xy = points[:, :2]
    _, vectors = np.linalg.eigh(np.cov(xy.T))
    normal = np.r_[vectors[:, 0], 0.]
    centre += np.median((points-centre) @ normal)*normal
    return normal, centre


def collect_patches(points, half, sensors, size, shift, rng):
    _, cell = np.unique(np.floor(points/size+shift).astype(np.int64), axis=0, return_inverse=True)
    order = np.argsort(cell, kind='stable')
    patches = []
    for idx in np.split(order, np.flatnonzero(np.diff(cell[order]))+1):
        if len(idx) < 56:
            continue
        faces = fit_faces(points[idx[~half[idx]]], rng)
        if not faces:
            continue
        other = fit_faces(points[idx[half[idx]]], rng)
        for kind in sorted(faces.keys() & other.keys()):
            na, a = faces[kind]
            nb, b = other[kind]
            if (abs(na @ nb) < np.cos(np.deg2rad(2.))
                    or max(abs((a-b) @ na), abs((a-b) @ nb)) > .030):
                continue
            support = idx[(abs((points[idx]-a) @ na) < .04) & (abs((points[idx]-b) @ nb) < .04)]
            if len(support) < 48 or np.max(np.ptp(np.percentile(sensors[support], [10, 90], axis=0), axis=0)) < .6:
                continue
            centre = points[support].mean(axis=0)
            normal = np.linalg.eigh(np.cov(points[support].T))[1][:, 0]
            patches.append(Patch(kind, normal, centre, support))
    return patches


def build_planes(points, half, sensors):
    """Learn faces separately in two spatially interleaved sets of viewpoints."""
    rng = np.random.default_rng(723)
    patches = collect_patches(points, half, sensors, 1.25, 0., rng)
    patches += collect_patches(points, half, sensors, 1.9, .5, rng)
    labels = np.full(len(points), -1, dtype=np.int32)
    models = []
    if not patches:
        return labels, models
    centres = np.stack([p.centre for p in patches])
    edges = []
    for i, j in cKDTree(centres).query_pairs(2.3):
        a, b = patches[i], patches[j]
        delta = centres[i]-centres[j]
        if (a.kind == b.kind and abs(a.normal @ b.normal) > np.cos(np.deg2rad(2.))
                and max(abs(delta @ a.normal), abs(delta @ b.normal)) < .028):
            edges.append((i, j))
    if not edges:
        return labels, models
    graph = coo_matrix((np.ones(len(edges)), np.array(edges).T), shape=(len(patches),)*2)
    count, group = connected_components(graph, directed=False)
    for g in range(count):
        members = np.flatnonzero(group == g)
        if len(members) < 2:
            continue
        support = np.unique(np.concatenate([patches[j].samples for j in members]))
        kind = patches[members[0]].kind
        normal, centre = constrained_plane(points[support], kind)
        # Check the measured surface separately from the ideal plane. A valid
        # inclined observation can be several centimetres from its plumb target.
        limit = .09 if kind == 'vertical' else .055
        if np.percentile(abs((points[support]-centre) @ normal), 95) > limit:
            continue
        for j in members:
            p = patches[j]
            error = abs((points[p.samples]-centre) @ normal)
            if abs(p.normal @ normal) >= np.cos(np.deg2rad(3.)) and np.percentile(error, 95) <= limit:
                ids = p.samples[error <= limit]
                # Conflicting labels at edges and close parallel faces stay unmodelled.
                previous = labels[ids]
                labels[ids] = np.where((previous == -1) | (previous == len(models)), len(models), -2)
        models.append((kind, normal, centre))
    return labels, models


def structural_points(points, scan, origins, near_range, detail_range):
    """Keep original tangential coordinates. Never extrapolate a face across gaps."""
    ranges = np.linalg.norm(points-origins[scan], axis=1)
    view_half = (np.floor(origins/.9).astype(np.int64).sum(axis=1) % 2).astype(bool)
    near = ranges <= near_range
    sample = []
    for side in (False, True):
        ids = np.flatnonzero(near & (view_half[scan] == side))
        if len(ids):
            sample.append(representatives(points, ids, ranges))
    ref = np.concatenate(sample) if sample else np.empty(0, dtype=int)
    halves = view_half[scan[ref]]
    # With no independent views there is no evidence to regularize this map.
    if len(sample) < 2:
        raise ValueError('Insufficient nearby observations from different viewpoints')
    ref_points = points[ref].astype(float)
    labels, models = build_planes(ref_points, halves, origins[scan[ref]])
    halves_idx = [np.flatnonzero(halves == side) for side in (False, True)]
    trees = [cKDTree(ref_points[idx]) for idx in halves_idx]
    model_normals = np.asarray([m[1] for m in models])
    model_centres = np.asarray([m[2] for m in models])
    horizontal = np.array([m[0] == 'horizontal' for m in models], dtype=bool)
    output = points.copy()
    keep = ranges <= detail_range
    projected = np.zeros(len(points), dtype=np.int8)  # 1 horizontal, 2 vertical
    for start in range(0, len(points), 80000):
        sl = slice(start, min(start+80000, len(points)))
        q = points[sl]
        matches = []
        for tree, idx in zip(trees, halves_idx):
            dist, nn = tree.query(q, distance_upper_bound=.16)
            label = np.full(len(q), -1, dtype=np.int32)
            found = np.isfinite(dist)
            label[found] = labels[idx[nn[found]]]
            closest = idx[np.minimum(nn, len(idx)-1)]
            matches.append((dist, label, closest))
        (da, la, ia), (db, lb, ib) = matches
        # Unmodelled shapes can also confirm a distant point at its measured location.
        keep[sl] |= (da <= .095) & (db <= .095)
        candidate = np.flatnonzero((la >= 0) & (la == lb))
        if not len(candidate):
            continue
        ids = la[candidate]
        signed = np.einsum('ij,ij->i', q[candidate]-model_centres[ids], model_normals[ids])
        tolerance = np.minimum(.08, .020 + .002*ranges[sl][candidate])
        ref_a = np.einsum('ij,ij->i', q[candidate]-ref_points[ia[candidate]], model_normals[ids])
        ref_b = np.einsum('ij,ij->i', q[candidate]-ref_points[ib[candidate]], model_normals[ids])
        valid = (np.maximum(abs(ref_a), abs(ref_b)) <= tolerance) & (abs(signed) <= .10)
        # Both witnesses identify the same face: do not re-admit a conflicting
        # distant echo merely because the Euclidean distance is below 9.5 cm.
        keep[start+candidate] = ranges[sl][candidate] <= detail_range
        move = candidate[valid]
        normal = model_normals[ids[valid]]
        output[start+move] = q[move] - signed[valid, None]*normal
        projected[start+move] = np.where(horizontal[ids[valid]], 1, 2)
        keep[start+move] = True
    return output, keep, projected, ranges


def export(run, dest, near_range, detail_range):
    metadata = json.loads((run/'metrics.json').read_text())
    if metadata.get('map_frame') != 'building_level':
        raise ValueError('Use a map with a confirmed building_level frame')
    if not (0 < near_range < detail_range and np.isfinite(detail_range)):
        raise ValueError('Expected 0 < reference range < detail range')
    if dest.exists():
        raise FileExistsError(dest)
    with np.load(run/'outputs.npz') as data:
        points, trajectory = data['registered_points'], data['trajectory']
        stamps, offsets = data['cloud_stamps'], data['cloud_offsets']
    if (len(offsets) != len(stamps)+1 or offsets[0] != 0 or offsets[-1] != len(points)
            or (np.diff(offsets) < 0).any() or not np.isfinite(points).all()):
        raise ValueError('Invalid registered scan data')
    origins = np.column_stack([np.interp(stamps, trajectory[:, 0], x) for x in trajectory[:, 1:4].T])
    scan = np.repeat(np.arange(len(stamps)), np.diff(offsets))
    output, keep, model, ranges = structural_points(points, scan, origins, near_range, detail_range)
    far = ranges > detail_range
    report = dict(source=str(run.resolve()), map_frame='building_level', reference_range_m=near_range,
                  detail_range_m=detail_range, input_points=len(points), output_points=int(keep.sum()),
                  far_input=int(far.sum()), far_confirmed=int((far & keep).sum()),
                  projected_horizontal=int((model == 1).sum()), projected_vertical=int((model == 2).sum()))
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        stage = Path(tmp)/'result'
        stage.mkdir()
        write_pcd(stage/'karte_dicht.pcd', output[keep])
        (stage/'metrics.json').write_text(json.dumps(report, indent=2)+'\n')
        stage.rename(dest)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path, help='Directory with a Z-up map, outputs.npz and metrics.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reference-range', type=float, default=7., help='Radius for reference observations (m)')
    parser.add_argument('--detail-range', type=float, default=8., help='Radius beyond which corroboration is required (m)')
    args = parser.parse_args()
    export(args.run, args.output, args.reference_range, args.detail_range)
