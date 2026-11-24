"""Reconstruct a recorded, calibrated route with NVIDIA Lyra 2's fine-tuned DA3 GS head."""
import argparse
import hashlib
from pathlib import Path
import sys

import cv2
import numpy as np
import torch
from scipy.spatial.transform import Rotation


def rebase_splats(points, rotations, transform):
    """Apply a camera-pose correction to world centres and their wxyz orientations."""
    xyz = points @ transform[:3, :3].T + transform[:3, 3]
    q = Rotation.from_matrix(transform[:3, :3]).as_quat()
    w = q[3] * rotations[:, :1] - rotations[:, 1:] @ q[:3, None]
    v = q[3]*rotations[:, 1:] + rotations[:, :1]*q[:3] + np.cross(q[:3], rotations[:, 1:])
    return xyz, np.column_stack((w, v))


def registered_depth(depth, depth_k, color_k, depth_in_color, size):
    """Z-buffer measured depth into the RGB camera at half resolution."""
    h, w = size[1] // 2, size[0] // 2
    y, x = np.nonzero((depth > 250) & (depth < 7000))
    xyz = np.column_stack([x, y, np.ones(len(x))]) @ np.linalg.inv(depth_k).T
    xyz *= depth[y, x, None] * .001
    xyz = xyz @ depth_in_color[:3, :3].T + depth_in_color[:3, 3]
    z = xyz[:, 2]
    pixels = xyz @ color_k.T
    u, v = np.rint(pixels[:, :2] / z[:, None] / 2).astype(int).T
    keep = (u >= 0) & (u < w) & (v >= 0) & (v < h) & (z > .2)
    result = np.full((h, w), np.inf, np.float32)
    np.minimum.at(result, (v[keep], u[keep]), z[keep])
    # A depth pixel covers about 1.56 output pixels with this camera pair. Fill
    # its projected footprint using the closest sample before rejecting edges.
    result = cv2.erode(result, np.ones((3, 3), np.uint8), borderType=cv2.BORDER_REPLICATE)
    result[~np.isfinite(result)] = 0
    # Reject depth boundaries where small timing or calibration errors swap surfaces.
    smooth = cv2.medianBlur(result, 3)
    stable = cv2.dilate(smooth, np.ones((3,3), np.uint8)) - cv2.erode(smooth, np.ones((3,3), np.uint8))
    return np.where((smooth > .3) & (stable < .16 + .025*smooth), smooth, 0)


def constrain_to_depth(points, scales, w2c, intrinsics, depth):
    center = np.linalg.inv(w2c)[:3, 3]
    camera = points @ w2c[:3, :3].T + w2c[:3, 3]
    z = camera[:, 2]
    uvw = camera @ intrinsics.T
    with np.errstate(invalid='ignore', divide='ignore'):
        pixels = np.nan_to_num(uvw[:, :2] / np.maximum(z[:, None], .001) / 2)
    u, v = np.rint(np.clip(pixels, -100000, 100000)).astype(int).T
    h, w = depth.shape
    d = depth[np.clip(v, 0, h-1), np.clip(u, 0, w-1)]
    inside = (u >= 0) & (u < w) & (v >= 0) & (v < h) & (z > .15)
    reliable = inside & (d > 0)
    ratios = d / np.maximum(z, .001)
    agreed = reliable & (ratios > .5) & (ratios < 2.)
    factor = np.clip(np.median(ratios[agreed]), .65, 1.5) if agreed.sum() > 250 else 1.
    correction = np.full(len(z), factor)
    # Along the source ray, measured smooth surfaces anchor the predictions in meters.
    correction[agreed] = .97*ratios[agreed] + .03*factor
    keep = inside & (z*correction < 18) & (~reliable | agreed)
    return center + (points-center)*correction[:,None], scales*correction[:,None], keep


def load_model(checkpoint, upstream):
    sys.path.insert(0, str(upstream/'Lyra-2/lyra_2/_src/inference/depth_anything_3/src'))
    from depth_anything_3.api import DepthAnything3
    model = DepthAnything3('da3nested-giant-large')
    state = torch.load(checkpoint, mmap=True, weights_only=True, map_location='cpu')
    state = state.get('module', state.get('model', state))
    values = {k.removeprefix('model.'): v for k,v in state.items() if k.startswith('model.')}
    result = model.model.load_state_dict(values, strict=False, assign=True)
    missing = set(result.missing_keys) & set(dict(model.model.named_parameters()))
    if missing:
        raise ValueError(f'Incomplete Lyra weights: {sorted(missing)[:10]}')
    print('Lyra checkpoint loaded',len(values),'tensors',flush=True)
    return model.eval().to('cuda')


def reconstruct(args):
    with np.load(args.route/'Kameraposen.npz') as d:
        ids, w2c, intrinsics, size = d['source_frame_id'], d['w2c'], d['intrinsics'], (int(d['image_width']), int(d['image_height']))
        stamps = d['stamp_ns']
    with np.load(args.depth) as d:
        depth, depth_k, depth_pose = d['depth_mm'][ids], d['K'], d['poses'][ids]
    held = np.arange(5,len(ids),10)
    training = np.setdiff1d(np.arange(len(ids)), held)
    corrections = {}
    if args.visual_poses:
        with np.load(args.visual_poses) as adjusted:
            lookup = dict(zip(adjusted['stamp_ns'], np.linalg.inv(adjusted['w2c'])))
        if any(stamps[i] in lookup for i in held):
            raise ValueError('Test image used for camera refinement')
        corrections = {i: lookup[stamps[i]] @ w2c[i] for i in training}
    args.cache.mkdir(exist_ok=True,parents=True)
    # An older cache can have identical filenames but different depth handling,
    # camera corrections, or raster resolution.
    sources = [args.route/'Kameraposen.npz', args.depth, args.checkpoint]
    sources.extend(args.photos/f'{ids[i]:04d}.jpg' for i in training)
    if args.visual_poses:
        sources.append(args.visual_poses)
    fingerprint = hashlib.sha256(Path(__file__).read_bytes())
    fingerprint.update(str((args.chunk, args.resolution, args.gs_down_ratio)).encode())
    for path in sources:
        stat = path.stat()
        fingerprint.update(str((path.resolve(), stat.st_size, stat.st_mtime_ns)).encode())
    signature = fingerprint.hexdigest()
    chunk_names = [f'chunk_{i:03d}.npz' for i in range(0, len(training), args.chunk)]
    np.savez(args.cache/'split.npz', train=training, test=held, ids=ids, chunks=chunk_names)
    model = load_model(args.checkpoint, args.upstream)
    for start in range(0,len(training),args.chunk):
        dest = args.cache/f'chunk_{start:03d}.npz'
        if dest.exists():
            with np.load(dest) as cached:
                if 'signature' in cached and str(cached['signature']) == signature:
                    continue
        core = training[start:start+args.chunk]
        views = training[max(0,start-3):start+len(core)+3]
        anchor = np.linalg.inv(w2c[views[0]])[:3,3]
        poses = w2c[views].copy()
        poses[:,:3,3] += poses[:,:3,:3] @ anchor
        paths = [str(args.photos/f'{ids[i]:04d}.jpg') for i in views]
        with torch.inference_mode():
            pred = model.inference(image=paths, extrinsics=poses.astype('f4'),
                intrinsics=intrinsics[views].astype('f4'), align_to_input_extrinsics=False,
                use_aligned_pred_cam=False, infer_gs=True, process_res=args.resolution,
                process_res_method='upper_bound_resize', gs_down_ratio=args.gs_down_ratio,gs_ds_feature_mode=True)
        gauss=pred.gaussians
        arrays={}
        for name in ('means','scales','rotations','opacities','harmonics'):
            x=getattr(gauss,name)[0].detach().float().cpu().numpy()
            arrays[name]=x.reshape(len(views),-1,*x.shape[1:])
        out=[]
        for i in core:
            j=int(np.searchsorted(views,i))
            z=registered_depth(depth[i],depth_k,intrinsics[i],w2c[i]@depth_pose[i],size)
            xyz,scales,valid=constrain_to_depth(arrays['means'][j]+anchor,arrays['scales'][j],w2c[i],intrinsics[i],z)
            rotations = arrays['rotations'][j]
            if corrections:
                xyz, rotations = rebase_splats(xyz, rotations, corrections[i])
            op=arrays['opacities'][j].reshape(-1,1)
            sh=arrays['harmonics'][j]
            data=np.column_stack([xyz,scales,rotations,op,sh[:,:,0]])
            valid &= np.isfinite(data).all(1) & (op[:,0]>.035) & (scales.min(1)>0) & (scales.max(1)<1.)
            out.append(data[valid].astype('f4'))
        splats=np.concatenate(out)
        temp=dest.with_suffix('.partial.npz')
        np.savez(temp, splats=splats,views=core,signature=signature)
        temp.replace(dest)
        print('LYRA_CHUNK',start,len(core),len(splats),flush=True)
        del pred,gauss,arrays
        torch.cuda.empty_cache()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--route',type=Path,default=Path('reports/20261123_lyra_test'))
    p.add_argument('--depth',type=Path,default=Path('.runtime/mesh_fusion/rgbd_1118.npz'))
    p.add_argument('--photos',type=Path,default=Path('.runtime/isaac_building/photos'))
    p.add_argument('--upstream',type=Path,default=Path('.runtime/lyra/repo'))
    p.add_argument('--checkpoint',type=Path,default=Path('.runtime/lyra/model.pt'))
    p.add_argument('--cache',type=Path,default=Path('.runtime/lyra/results'))
    p.add_argument('--chunk',type=int,default=10)
    p.add_argument('--resolution',type=int,default=448)
    p.add_argument('--gs-down-ratio',type=int,choices=(1,2),default=2)
    p.add_argument('--visual-poses',type=Path)
    reconstruct(p.parse_args())
