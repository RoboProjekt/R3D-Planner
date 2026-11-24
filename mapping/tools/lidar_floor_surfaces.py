"""Optional scan-pose correction on connected, wall-confirmed level indoor floors."""
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import median_filter
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

from correct_lio_drift import PoseTrack, apply_pose
from lidar_planes import fit_plane, wall_vertical


def rotation_to_vertical(normals):
    axes = np.cross(normals, [0., 0., 1.])
    sine = np.linalg.norm(axes, axis=-1)
    angles = np.arctan2(sine, normals[..., 2])
    return Rotation.from_rotvec(axes * np.expand_dims(angles/np.maximum(sine, 1e-12), -1))


@dataclass
class FloorPatch:
    scan: int
    normal: np.ndarray
    centre: np.ndarray
    points: np.ndarray
    xy_tree: cKDTree
    # Measured inclination relative to two intersecting walls, independent of pose tilt.
    normal_from_walls: np.ndarray | None


def scan_patch(index, cloud, pose, rng):
    local = apply_pose(np.linalg.inv(pose), cloud)
    radius = np.linalg.norm(local[:, :2], axis=1)
    near = local[(radius > .85) & (radius < 7.)]
    floor = fit_plane(near[(near[:, 2] < -.25) & (near[:, 2] > -1.5)], rng)
    if floor is None:
        return None
    normal = pose[:3, :3] @ floor[0]
    if normal[2] < .975:
        return None
    wall_up = wall_vertical(near, rng)
    plumb = None if wall_up is None else rotation_to_vertical(pose[:3, :3] @ wall_up).apply(normal)
    points = apply_pose(pose, floor[2])
    return FloorPatch(index, normal, points.mean(axis=0), points, cKDTree(points[:, :2]), plumb)


def common_floor(a, b):
    if a.normal @ b.normal < np.cos(np.deg2rad(3.)):
        return False
    p = b.points[a.xy_tree.query(b.points[:, :2])[0] < .30]
    if len(p) < max(35, .18*len(b.points)):
        return False
    centred = p[:, :2] - p[:, :2].mean(axis=0)
    if np.linalg.svd(centred, compute_uv=False)[1]/np.sqrt(len(p)) < .25:
        return False
    distances = (p-a.centre) @ a.normal
    offset = np.median(distances)
    return abs(offset) < .065 and np.percentile(abs(distances-offset), 85) < .055


def floor_components(patches, poses, times, loops):
    indices = [p.scan for p in patches]
    stamps = times[indices]
    xy = poses[indices, :2, 3]
    edges = []
    for j, patch in enumerate(patches):
        for i in range(np.searchsorted(stamps, stamps[j]-2.5), j):
            if np.linalg.norm(xy[j]-xy[i]) <= 2.5 and common_floor(patches[i], patch):
                edges.append((i, j))
    # A similar floor on another storey is insufficient evidence of a revisit.
    for first, second in loops:
        i = np.argmin(abs(stamps-first))
        j = np.argmin(abs(stamps-second))
        if (max(abs(stamps[i]-first), abs(stamps[j]-second)) < .65 and
                np.linalg.norm(xy[j]-xy[i]) < 2. and common_floor(patches[i], patches[j])):
            edges.append((i, j))
    if not edges:
        return []
    graph = coo_matrix((np.ones(len(edges)), np.array(edges).T), shape=(len(patches), len(patches)))
    count, labels = connected_components(graph, directed=False)
    return [[patches[i] for i in np.flatnonzero(labels == label)] for label in range(count)]


def level_floor_target(group, poses):
    indices = np.array([p.scan for p in group])
    xyz = poses[indices, :3, 3]
    if np.max(np.ptp(xyz[:, :2], axis=0)) < 5.:
        return None
    walls = [p for p in group if p.normal_from_walls is not None]
    if len(walls) < 6:
        return None
    xy = xyz[:, :2] - xyz[:, :2].mean(axis=0)
    axis = np.linalg.svd(xy, full_matrices=False)[2][0]
    measured = np.stack([p.normal_from_walls for p in walls])
    along = (poses[[p.scan for p in walls], :2, 3]-xyz[:, :2].mean(axis=0)) @ axis
    bins = np.floor(along/4.)
    supported = []
    for cell in np.unique(bins):
        selected = bins == cell
        if selected.sum() < 4:
            continue
        n = np.median(measured[selected], axis=0)
        tilt = np.arctan2(np.linalg.norm(n[:2]), n[2])
        if tilt > np.deg2rad(1.):
            return None
        supported.append(np.median(along[selected]))
    if len(supported) < 2 or np.ptp(supported) < .55*np.ptp(xy @ axis):
        return None
    centres = np.stack([p.centre for p in group])
    normals = np.stack([p.normal for p in group])
    floor_z = centres[:, 2] - ((xyz[:, :2]-centres[:, :2])*normals[:, :2]).sum(axis=1)/normals[:, 2]
    # The earliest consecutive floor patches set the datum. Later traversals
    # may contain many more scans and must not move the initial height.
    runs = np.split(np.arange(len(indices)), np.flatnonzero(np.diff(indices) > 3)+1)
    initial = next((run[:5] for run in runs if len(run) >= 3), None)
    if initial is None:
        return None
    height = np.median(floor_z[initial])
    if max(abs(np.percentile(floor_z, [1, 99])-np.median(floor_z))) > .38:
        return None
    rotations = rotation_to_vertical(normals)
    rotated = rotations.apply(centres-xyz) + xyz
    shifts = height-rotated[:, 2]
    # Do not partially flatten steps or extreme outliers within an accepted component.
    # Either end of a supported surface may set the datum, allowing its full height span.
    supported_scans = (rotations.magnitude() < np.deg2rad(5.)) & (abs(shifts) < .76)
    params = np.column_stack([rotations.as_rotvec(), shifts])
    return indices, params, supported_scans, float(height)


def align_floor_surfaces(trajectory, clouds, stamps, loops):
    """Input and output are Z-up. Each cloud and its acquisition pose move rigidly together."""
    origin = trajectory[0, 0]
    times = np.asarray(stamps) - origin
    poses = PoseTrack(trajectory, origin).at(times)
    rng = np.random.default_rng(306)
    patches = [p for i, c in enumerate(clouds) if (p := scan_patch(i, c, poses[i], rng)) is not None]
    summary = {'applied': False, 'floor_patches': len(patches), 'surfaces': []}
    if len(patches) < 6:
        return trajectory, clouds, summary
    params = np.zeros((len(stamps), 4))
    # Track actual membership so interpolation cannot bridge a different floor surface.
    owner = np.full(len(stamps), -1)
    groups = floor_components(patches, poses, times, loops)
    for label, group in enumerate(groups):
        owner[[p.scan for p in group]] = label
    for label, group in enumerate(groups):
        target = level_floor_target(group, poses)
        if target is None:
            continue
        indices, values, use, height = target
        selected = indices[use]
        blocks = np.split(np.flatnonzero(use), np.flatnonzero(np.diff(times[selected]) > 1.)+1)
        count = 0
        for block in blocks:
            if len(block) < 3:
                continue
            anchors = indices[block]
            samples = np.arange(anchors[0], anchors[-1]+1)
            segment = np.column_stack([np.interp(times[samples], times[anchors], v) for v in values[block].T])
            segment = median_filter(segment, size=(3, 1), mode='nearest')
            allowed = (owner[samples] == -1) | np.isin(samples, anchors)
            # Blend into the uncorrected pose at a change of surface.
            gain = np.minimum(1., (times[samples]-times[samples[0]])/.55)
            if samples[-1] < len(times)-1:
                gain = np.minimum(gain, (times[samples[-1]]-times[samples])/.55)
            params[samples[allowed]] = segment[allowed]*gain[allowed, None]
            count += int(np.count_nonzero(allowed & (gain > 0)))
        if count:
            summary['surfaces'].append({'height_m': height, 'corrected_scans': count})
    if not summary['surfaces']:
        return trajectory, clouds, summary
    correction = np.column_stack([np.interp(trajectory[:, 0]-origin, times, v) for v in params.T])
    fixed = trajectory.copy()
    fixed[:, 3] += correction[:, 3]
    fixed[:, 4:8] = (Rotation.from_rotvec(correction[:, :3])*Rotation.from_quat(trajectory[:, 4:8])).as_quat()
    change = PoseTrack(fixed, origin).at(times) @ np.linalg.inv(poses)
    summary.update(applied=True, max_height_shift_m=float(np.max(abs(params[:, 3]))),
                   max_tilt_deg=float(np.rad2deg(np.linalg.norm(params[:, :3], axis=1)).max()))
    return fixed, [apply_pose(m, c).astype('f4') for m, c in zip(change, clouds)], summary
