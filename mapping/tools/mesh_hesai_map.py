#!/usr/bin/env python3
"""Fuse measured LiDAR ranges and camera depths in the corrected building frame."""
import argparse
import json
from pathlib import Path
import tempfile

import cv2
import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation


def initial_view(run, meta):
    """Place the viewer at a recorded camera position halfway through the route."""
    with np.load(run / 'outputs.npz') as data:
        track = data['trajectory']
    i = np.searchsorted(track[:, 0], .5*(track[0, 0] + track[-1, 0]))
    pose = np.eye(4)
    pose[:3, :3] = Rotation.from_quat(track[i, 4:]).as_matrix()
    pose[:3, 3] = track[i, 1:4]
    camera = pose @ np.asarray(meta['lidar_from_color'])
    return dict(eye=camera[:3, 3].tolist(), forward=camera[:3, 2].tolist())


def validate(mesh, xyz):
    verts, faces = np.asarray(mesh.vertices), np.asarray(mesh.triangles)
    if (not np.isfinite(verts).all() or not mesh.has_vertex_colors() or not len(faces)
            or faces.min() < 0 or faces.max() >= len(verts)):
        raise ValueError('Invalid mesh export')
    rng = np.random.default_rng(20261123)
    sample = xyz[rng.choice(len(xyz), min(120000, len(xyz)), replace=False)]
    scene = o3d.t.geometry.RaycastingScene()
    scene.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(mesh))
    distance = scene.compute_distance(o3d.core.Tensor(sample.astype('f4'))).numpy()
    if not np.isfinite(distance).all():
        raise ValueError('Invalid point-to-surface distance')
    max_edge = max(np.linalg.norm(verts[faces[:,i]]-verts[faces[:,i-1]], axis=1).max() for i in range(3))
    return dict(sample_points=len(sample), sample_within_5cm_pct=float(100*np.mean(distance <= .05)),
                median_cm=float(100*np.median(distance)), p95_cm=float(100*np.percentile(distance, 95)),
                max_triangle_edge_m=float(max_edge))


def complete_depth(depth):
    """Fill one missing pixel only between two consistent opposite range samples."""
    source = np.pad(depth, 1)
    for a, b in ((source[:-2, 1:-1], source[2:, 1:-1]),
                 (source[1:-1, :-2], source[1:-1, 2:])):
        supported = (depth == 0) & (a > 0) & (b > 0) & (abs(a-b) < .08 + .012*np.minimum(a,b))
        depth[supported] = .5*(a[supported]+b[supported])
    return depth


def integrate(volume, depth_mm, intrinsic, pose, max_z, trunc_voxels=3.):
    depth = o3d.t.geometry.Image(o3d.core.Tensor.from_numpy(np.ascontiguousarray(depth_mm)))
    extrinsic = o3d.core.Tensor(np.linalg.inv(pose), o3d.core.float64)
    try:
        blocks = volume.compute_unique_block_coordinates(depth, intrinsic, extrinsic, 1000., max_z, trunc_voxels)
    except RuntimeError as exc:
        # Sparse LiDAR cube faces can miss every pixel used to activate blocks.
        if 'No block is touched' in str(exc):
            return False
        raise
    if blocks.shape[0] > 0:
        volume.integrate(blocks, depth, intrinsic, extrinsic, 1000., max_z, trunc_voxels)
        return True
    return False


def fuse_lidar(volume, run, tree, xyz, size=112, trunc_voxels=3.):
    with np.load(run/'outputs.npz') as data:
        raw, stamps, offsets = data['registered_points'], data['cloud_stamps'], data['cloud_offsets']
        track = data['trajectory']
    origins = np.column_stack([np.interp(stamps, track[:,0], c) for c in track[:,1:4].T])
    # The structural exporter can correct a return by up to 10 cm. Put each accepted
    # return on its observed map surface before rendering it from the sensor position.
    nearest = tree.query(raw, distance_upper_bound=.105, workers=6)[1]
    f, c = size/2, (size-1)/2
    intrinsic = o3d.core.Tensor([[f,0,c],[0,f,c],[0,0,1]], o3d.core.float64)
    axes = []
    for forward in np.r_[np.eye(3), -np.eye(3)]:
        up = [0, 0, 1] if forward[2] == 0 else [0, 1, 0]
        right = np.cross(forward, up)
        axes.append(np.column_stack((right, np.cross(forward, right), forward)))
    indices = np.arange(0, len(origins), 2)
    used = 0
    for j in indices:
        # Pool adjacent scans only while their origins remain within 25 cm.
        neighbors = np.arange(max(0, j-2), min(len(stamps), j+3))
        neighbors = neighbors[np.linalg.norm(origins[neighbors]-origins[j], axis=1) <= .25]
        ids = np.concatenate([nearest[offsets[s]:offsets[s+1]] for s in neighbors])
        deltas = xyz[ids[ids < len(xyz)]] - origins[j]
        deltas = deltas[np.einsum('ij,ij->i', deltas, deltas) <= 8.**2]
        pose = np.eye(4)
        pose[:3,3] = origins[j]
        integrated = False
        for axes_to_map in axes:
            optical = deltas @ axes_to_map
            z = optical[:,2]
            valid = (z > .25) & (np.abs(optical[:,0]) < z) & (np.abs(optical[:,1]) < z)
            if np.count_nonzero(valid) < 20:
                continue
            z = z[valid]
            uv = np.rint(optical[valid,:2] * (f/z[:,None]) + c).astype(int)
            depth = np.full((size,size), np.inf, dtype='f4')
            np.minimum.at(depth, (uv[:,1], uv[:,0]), z)
            depth[~np.isfinite(depth)] = 0
            pose[:3,:3] = axes_to_map
            integrated |= integrate(volume, np.rint(1000*complete_depth(depth)).astype('u2'), intrinsic, pose, 8.01, trunc_voxels)
        used += int(integrated)
    return used


def fuse_camera(volume, cache, run, report):
    with np.load(cache) as data:
        if Path(str(data['run'])) != run.resolve() or Path(str(data['color_report'])) != report.resolve():
            raise ValueError('Depth poses and map provenance differ')
        depths, poses, k = data['depth_mm'], data['poses'], data['K']
    intrinsic = o3d.core.Tensor(k, o3d.core.float64)
    used = 0
    for frame, pose in zip(depths, poses):
        # Limit camera range to 4 m for geometry, especially at depth discontinuities.
        used += integrate(volume, frame, intrinsic, pose, 4.)
    return used


def map_colors(mesh, tree, xyz, rgb, seen):
    centers, normals = np.asarray(mesh.vertices), np.asarray(mesh.vertex_normals)
    colored_xyz, colored_rgb = xyz[seen], rgb[seen]
    color_tree = cKDTree(colored_xyz)
    colors = np.full(centers.shape, 128./255.)
    supported = np.zeros(len(centers), dtype=bool)
    for start in range(0, len(centers), 16000):
        sl = slice(start, start+16000)
        vertices = centers[sl]
        surface_dist = tree.query(vertices, workers=4)[0]
        dist, ids = color_tree.query(vertices, k=4, workers=4)
        offsets = colored_xyz[ids] - vertices[:,None,:]
        across = np.abs(np.einsum('ijk,ik->ij', offsets, normals[sl]))
        valid = (dist < .10) & (dist <= surface_dist[:,None] + .04) & (across < .05)
        weights = valid / (.01 + dist)**2
        sums = weights.sum(axis=1)
        active = sums > 0
        colors[sl][active] = np.einsum('ij,ijk->ik', weights[active], colored_rgb[ids[active]]) / (255.*sums[active,None])
        supported[sl] = active
    return colors, supported


def color_mesh(mesh, tree, xyz, rgb, seen, cache):
    colors, supported = map_colors(mesh, tree, xyz, rgb, seen)
    vertices, normals = np.asarray(mesh.vertices), np.asarray(mesh.vertex_normals)
    mesh_tree = cKDTree(vertices)
    best = np.full(len(vertices), np.inf)
    direct_frames = 0
    with np.load(cache) as data:
        k, rgba, depths, poses = data['K'], data['rgba'], data['depth_mm'], data['poses']
    for image, depth, pose in zip(rgba, depths, poses):
        if not np.any(image[:,:,3]):
            continue
        direct_frames += 1
        ids = np.asarray(mesh_tree.query_ball_point(pose[:3,3], 6.), dtype=int)
        q = (vertices[ids] - pose[:3,3]) @ pose[:3,:3]
        forward = (q[:,2] > .3) & (q[:,2] < 4.)
        ids, q = ids[forward], q[forward]
        uv = np.rint(q[:,:2] / q[:,2,None] * [k[0,0], k[1,1]] + k[:2,2]).astype(int)
        inside = (uv[:,0] >= 0) & (uv[:,0] < depth.shape[1]) & (uv[:,1] >= 0) & (uv[:,1] < depth.shape[0])
        u, v = uv[inside].T
        ids, q = ids[inside], q[inside]
        depth_m = depth.astype('f4')*.001
        depth_m[depth == 0] = np.inf
        near = cv2.erode(depth_m, np.ones((3,3), dtype='u1'))
        tol = .032 + .014*q[:,2]
        error = abs(depth_m[v,u] - q[:,2])
        visible = (image[v,u,3] > 0) & (error < tol) & (q[:,2] <= near[v,u]+tol)
        ids, q, u, v = ids[visible], q[visible], u[visible], v[visible]
        direction = vertices[ids] - pose[:3,3]
        incidence = abs(np.einsum('ij,ij->i', direction, normals[ids])) / np.linalg.norm(direction, axis=1)
        cost = (error[visible]/tol[visible] + .16*q[:,2]
                + .45*np.linalg.norm(q[:,:2], axis=1)/q[:,2] + .4*(1.-incidence))
        update = cost < best[ids]
        best[ids[update]] = cost[update]
        colors[ids[update]] = image[v[update], u[update], :3]/255.
    direct = np.isfinite(best)
    mesh.vertex_colors = o3d.utility.Vector3dVector(np.clip(colors, 0., 1.))
    return dict(rgb_vertices=int((direct | supported).sum()), direct_rgb_vertices=int(direct.sum()),
                rgb_frames=direct_frames, fallback_map_rgb_vertices=int((supported & ~direct).sum()))


def export(source, run, cache, output, voxel):
    if output.exists():
        raise FileExistsError(output)
    if not .02 <= voxel <= .10:
        raise ValueError('Expected a voxel size between 2 and 10 cm')
    report_path = source.with_name('metrics.json')
    meta = json.loads(report_path.read_text())
    if meta['map_frame'] != 'building_level' or json.loads((run/'metrics.json').read_text())['map_frame'] != meta['map_frame']:
        raise ValueError('Expected both maps in building_level')
    points = o3d.t.io.read_point_cloud(str(source)).point
    xyz, rgb, seen = points.positions.numpy(), points.colors.numpy(), points.views.numpy().ravel() > 0
    if len(xyz) != meta['points'] or not np.isfinite(xyz).all() or not seen.any():
        raise ValueError('Invalid camera-colored map')
    tree = cKDTree(xyz)
    volume = o3d.t.geometry.VoxelBlockGrid(attr_names=['tsdf', 'weight'],
        attr_dtypes=[o3d.core.float32, o3d.core.float32], attr_channels=[(1,), (1,)],
        voxel_size=voxel, block_resolution=8, block_count=16000)
    print('Integrating registered LiDAR scans.', flush=True)
    lidar_count = fuse_lidar(volume, run, tree, xyz)
    print('Integrating measured camera depths.', flush=True)
    camera_count = fuse_camera(volume, cache, run, report_path)
    mesh = volume.extract_triangle_mesh(weight_threshold=2.).to_legacy()
    if not mesh.has_triangles():
        raise ValueError('Empty TSDF surface')
    labels, sizes, _ = mesh.cluster_connected_triangles()
    mesh.remove_triangles_by_mask(np.asarray(sizes)[np.asarray(labels)] < 24)
    mesh.remove_unreferenced_vertices()
    mesh.compute_vertex_normals()
    print('Projecting camera colors onto mesh vertices.', flush=True)
    color_stats = color_mesh(mesh, tree, xyz, rgb, seen, cache)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        stage = Path(tmp)/'result'
        stage.mkdir()
        path = stage/'karte_mesh.ply'
        if not o3d.io.write_triangle_mesh(str(path), mesh):
            raise OSError(f'Could not write {path}')
        saved = o3d.io.read_triangle_mesh(str(path))
        if (len(mesh.vertices) != len(saved.vertices)
                or not np.array_equal(np.asarray(mesh.triangles), np.asarray(saved.triangles))):
            raise ValueError('PLY round-trip changed the topology')
        checks = validate(saved, xyz)
        report = dict(method='projective_tsdf', map_frame=meta['map_frame'], source=str(source.resolve()),
                      registered_run=str(run.resolve()), source_points=len(xyz), voxel_m=voxel,
                      truncation_m=3*voxel, lidar_views=lidar_count, camera_depth_views=camera_count,
                      camera_depth_limit_m=4., lidar_range_limit_m=8., vertices=len(saved.vertices),
                      triangles=len(saved.triangles), initial_view=initial_view(run, meta), **color_stats, **checks)
        (stage/'metrics.json').write_text(json.dumps(report, indent=2)+'\n')
        stage.rename(output)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('map', type=Path)
    parser.add_argument('run', type=Path)
    parser.add_argument('depth_cache', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--voxel', type=float, default=.05)
    a = parser.parse_args()
    export(a.map, a.run, a.depth_cache, a.output, a.voxel)
