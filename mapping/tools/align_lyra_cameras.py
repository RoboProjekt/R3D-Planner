"""Refine training cameras from cross-view RGB features and metric depth, anchored to LiDAR."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
from scipy.spatial.transform import Rotation

from reconstruct_lyra_route import registered_depth


def detect(path):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(path)
    points, descriptors = cv2.SIFT_create(nfeatures=1100, contrastThreshold=.012).detectAndCompute(image, None)
    return np.array([pt.pt for pt in points]).reshape(-1,2), descriptors


def relative_constraint(xyz, descriptors, target, prior, k):
    uv, other = target
    if other is None or len(other)<2:
        return None
    matches = cv2.BFMatcher().knnMatch(descriptors, other, k=2)
    good = [a for a,b in matches if a.distance < .75*b.distance]
    if len(good)<18:
        return None
    points = xyz[[m.queryIdx for m in good]]
    pixels = uv[[m.trainIdx for m in good]]
    ok, rv, tv, inliers = cv2.solvePnPRansac(points, pixels, k, None, iterationsCount=120,
                                             reprojectionError=2.4, confidence=.98, flags=cv2.SOLVEPNP_EPNP)
    if not ok or len(inliers)<max(15, .34*len(good)):
        return None
    points,pixels = points[inliers[:,0]],pixels[inliers[:,0]]
    rv,tv = cv2.solvePnPRefineLM(points,pixels,k,None,rv,tv)
    rot = cv2.Rodrigues(rv)[0]
    if Rotation.from_matrix(prior[:3,:3].T@rot).magnitude()>.25 or np.linalg.norm(prior[:3,3]-tv[:,0])>.5:
        return None
    def pixel_error(rotation, translation):
        p = (points@rotation.T + translation)@k.T
        return np.median(np.linalg.norm(p[:,:2]/p[:,2,None]-pixels, axis=1))
    return rot, tv[:,0], len(points), pixel_error(prior[:3,:3],prior[:3,3]), pixel_error(rot,tv[:,0])


def fit_pose_graph(initial, edges):
    i,j,observed_r,observed_t,counts,prior_px,fit_px = map(np.array, zip(*edges))
    weight = np.sqrt(np.clip(counts/35., .45, 2.))
    n = len(initial)
    def poses(params):
        delta = params.reshape(n,6)
        rotation = initial[:,:3,:3]@Rotation.from_rotvec(delta[:,:3]).as_matrix()
        position = initial[:,:3,3]+(initial[:,:3,:3]@delta[:,3:,None])[:,:,0]
        return rotation,position
    def residual(params):
        r,t = poses(params)
        rj = r[j].transpose(0,2,1)
        delta_r = Rotation.from_matrix(observed_r.transpose(0,2,1) @ rj @ r[i]).as_rotvec()
        delta_t = (rj@(t[i]-t[j])[:,:,None])[:,:,0]-observed_t
        pair = np.column_stack((delta_r/.010,delta_t/.025))*weight[:,None]
        anchor = params.reshape(n,6)/np.array([.04,.04,.04,.07,.07,.07])
        return np.r_[pair.ravel(),anchor.ravel()]
    sparsity = lil_matrix((6*(len(i)+n),6*n),dtype='i1')
    for a in range(6):
        rows = 6*np.arange(len(i))+a
        for b in range(6):
            sparsity[rows,6*i+b]=1
            sparsity[rows,6*j+b]=1
        cols=6*np.arange(n)+a
        sparsity[6*len(i)+cols,cols]=1
    fit=least_squares(residual,np.zeros(6*n),jac_sparsity=sparsity.tocsr(),loss='soft_l1',
                      f_scale=1.3,max_nfev=35,ftol=1e-5)
    updated=initial.copy()
    updated[:,:3,:3],updated[:,:3,3] = poses(fit.x)
    return updated, counts, prior_px, fit_px


def align(args):
    cv2.setNumThreads(1)
    route=np.load(args.route/'Kameraposen.npz')
    extra=np.load(args.extra/'views.npz')
    training=np.load(args.split)['train']
    indices=route['source_frame_id'][training]
    initial=np.linalg.inv(np.concatenate([route['w2c'][training],extra['w2c']]))
    stamps=np.r_[route['stamp_ns'][training],extra['stamp_ns']]
    held=route['stamp_ns'][np.load(args.split)['test']]
    if np.intersect1d(held,stamps).size:
        raise ValueError('Test view entered camera registration')
    k=route['intrinsics'][0]
    paths=[args.photos/f'{i:04d}.jpg' for i in indices] + [args.extra/f'{t}.png' for t in extra['stamp_ns']]
    with ThreadPoolExecutor(args.workers) as pool:
        features=list(pool.map(detect, paths))
    with np.load(args.depth) as depth:
        raw=depth['depth_mm'][indices]
        depth_k=depth['K']
        depth_poses=depth['poses'][indices]
    size=int(route['image_width']),int(route['image_height'])
    def edges_for(i):
        uv,desc=features[i]
        d=registered_depth(raw[i],depth_k,k,np.linalg.inv(initial[i])@depth_poses[i],size)
        u,v=np.rint(uv.T/2).astype(int)
        z=d[v.clip(0,d.shape[0]-1),u.clip(0,d.shape[1]-1)]
        valid=(z>.32)&(z<6.7)
        if valid.sum()<15:
            return []
        points=(np.column_stack([uv[valid],np.ones(valid.sum())])@np.linalg.inv(k).T)*z[valid,None]
        edges=[]
        for j in np.flatnonzero((abs(stamps-stamps[i])<1_450_000_000)&(stamps!=stamps[i])):
            prior=np.linalg.solve(initial[j],initial[i])
            measurement=relative_constraint(points,desc[valid],features[j],prior,k)
            if measurement is not None:
                edges.append((i,j,*measurement))
        return edges
    with ThreadPoolExecutor(args.workers) as pool:
        edges=[edge for group in pool.map(edges_for,range(len(training))) for edge in group]
    if not edges:
        raise ValueError('No cross-view constraints survived feature and depth validation')
    updated,counts,prior_px,fit_px=fit_pose_graph(initial, edges)
    np.savez(args.output,stamp_ns=stamps,w2c=np.linalg.inv(updated),prior=initial,
             edges=counts,prior_px=prior_px,pnp_px=fit_px)
    print(f'{len(edges)} training camera pairs, median reprojection at LiDAR pose {np.median(prior_px):.2f} px')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('route','extra','split','output'):p.add_argument(key,type=Path)
    p.add_argument('--photos',type=Path,default=Path('.runtime/isaac_building/photos'))
    p.add_argument('--depth',type=Path,default=Path('.runtime/mesh_fusion/rgbd_1118.npz'))
    p.add_argument('--workers',type=int,default=6)
    align(p.parse_args())
