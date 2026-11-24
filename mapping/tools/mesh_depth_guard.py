"""Test proposed mesh removals against the first surface visible in measured depth images."""
import numpy as np
import warp as wp


@wp.kernel
def compare_depth(full_mesh: wp.uint64, filtered_mesh: wp.uint64,
                  owners: wp.array(dtype=wp.int32), origins: wp.array(dtype=wp.vec3),
                  directions: wp.array(dtype=wp.vec3), norms: wp.array(dtype=wp.float32),
                  depths: wp.array(dtype=wp.float32), votes: wp.array(dtype=wp.int32)):
    i = wp.tid()
    observed = depths[i]
    if observed < 0.35 or observed > 4.0:
        return
    direction = directions[i] / norms[i]
    first = wp.mesh_query_ray(full_mesh, origins[i], direction, 30.0)
    if not first.result:
        return
    owner = owners[first.face]
    if owner < 0:
        return
    before = first.t / norms[i]
    second = wp.mesh_query_ray(filtered_mesh, origins[i], direction, 30.0)
    after = float(30.0)
    if second.result:
        after = second.t / norms[i]
    gain = wp.abs(before - observed) - wp.abs(after - observed)
    # Keep a component when deleting it exposes a hole or a more distant surface
    # in clear disagreement with the depth image. Ignore small depth differences.
    if gain < -0.10:
        votes[i] = -owner - 1
    elif gain > 0.08:
        votes[i] = owner + 1


def visible_surface_guard(vertices, faces, component, removed, work):
    """Accumulate an independent vote per training image and affected component."""
    wp.init()
    points = wp.array(vertices, dtype=wp.vec3, device='cpu')
    original = wp.Mesh(points=points, indices=wp.array(faces.ravel(),dtype=wp.int32,device='cpu'))
    filtered = wp.Mesh(points=points, indices=wp.array(faces[~removed[component]].ravel(),dtype=wp.int32,device='cpu'))
    owners = wp.array(np.where(removed[component],component,-1),dtype=wp.int32,device='cpu')
    with np.load(work/'cameras.npz') as d:
        k, prior = d['depth_k'],d['depth_poses']
    poses = prior
    if (work/'poses.npz').exists():
        with np.load(work/'poses.npz') as d:poses = d['depth_poses']
    depth = np.load(work/'depth.npy',mmap_mode='r')
    pos = np.zeros(len(removed),'i4')
    neg = np.zeros_like(pos)
    h,w = depth.shape[1:]
    for i in range(0,len(poses),3):
        # Stagger the sample grid to catch sub-pixel islands across the route.
        sy,sx=(i//3)%2,(i//6)%2
        yy,xx = np.mgrid[sy:h:2,sx:w:2]
        measured = (depth[i,sy::2,sx::2].ravel()*.001).astype('f4')
        ray = np.column_stack(((xx.ravel()-k[0,2])/k[0,0],(yy.ravel()-k[1,2])/k[1,1],np.ones(xx.size)))
        pose = poses[i]
        directions = (ray @ pose[:3,:3].T).astype('f4')
        origins = np.broadcast_to(pose[:3,3].astype('f4'),directions.shape).copy()
        votes = wp.zeros(len(ray), dtype=wp.int32, device='cpu')
        wp.launch(compare_depth,dim=len(ray),inputs=[original.id,filtered.id,owners,
                  wp.array(origins,dtype=wp.vec3,device='cpu'),wp.array(directions,dtype=wp.vec3,device='cpu'),
                  wp.array(np.linalg.norm(directions,axis=1),device='cpu'),wp.array(measured,device='cpu'),votes],device='cpu')
        result = votes.numpy()
        p = np.bincount(result[result>0]-1,minlength=len(pos))
        n = np.bincount(-result[result<0]-1,minlength=len(pos))
        pos += p>n
        neg += n>p
    return (neg>=2)&(neg>pos)
