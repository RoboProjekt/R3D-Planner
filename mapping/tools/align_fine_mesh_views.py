"""Tie textured RGB-D keyframes together across traversals while anchoring them to the LiDAR map."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from scipy.spatial import cKDTree

from align_lyra_cameras import detect, fit_pose_graph, relative_constraint
from reconstruct_lyra_route import registered_depth


def align(work, workers):
    data=np.load(work/'cameras.npz');raw=np.load(work/'depth.npy',mmap_mode='r')
    c2w=data['color_poses'];d2w=data['depth_poses'];k=data['color_k'];dk=data['depth_k']
    size=tuple(data['size']);n=len(c2w);centers=c2w[:,:3,3];directions=c2w[:,:3,2]
    tree=cKDTree(centers); inv_k=np.linalg.inv(k);w2c=np.linalg.inv(c2w)
    cv2.setNumThreads(1)
    with ThreadPoolExecutor(workers) as pool:
        features=list(pool.map(detect,[work/'photos'/f'{i:04d}.jpg' for i in range(n)]))
    print('RGB keyframes',n,flush=True)
    def edges(i):
        uv,desc=features[i]
        if desc is None:return []
        m=registered_depth(raw[i],dk,k,w2c[i]@d2w[i],size)
        u,v=np.rint(uv.T/2).astype(int);z=m[v.clip(0,m.shape[0]-1),u.clip(0,m.shape[1]-1)]
        valid=(z>.35)&(z<5.5)
        if valid.sum()<17:return []
        points=np.column_stack([uv[valid],np.ones(valid.sum())])@inv_k.T*z[valid,None]
        near=np.array(tree.query_ball_point(centers[i],1.8),dtype=int)
        real_loop=(abs(data_stamps[near]-data_stamps[i])>3_000_000_000)&(directions[near]@directions[i]>.50)
        near=near[real_loop]
        rank=np.linalg.norm(centers[near]-centers[i],axis=1)+.7*(1.-directions[near]@directions[i])
        cross=near[np.argsort(rank)[:3]]
        neighbors=np.unique(np.r_[i+np.array([-2,1,3,6]),cross])
        found=[]
        for j in neighbors[(neighbors>=0)&(neighbors<n)]:
            measure=relative_constraint(points,desc[valid],features[j],w2c[j]@c2w[i],k)
            if measure is not None:found.append((i,j,*measure))
        return found
    data_stamps=data['stamps']
    with ThreadPoolExecutor(workers) as pool:
        measurements=[e for group in pool.map(edges,range(n)) for e in group]
    if not measurements:raise RuntimeError('No metric RGB-D camera constraints')
    corrected,counts,prior_px,fit_px=fit_pose_graph(c2w,measurements)
    dd=corrected @ w2c @ d2w
    np.savez(work/'poses.npz',color_poses=corrected,depth_poses=dd,edges=len(measurements),
             loop_edges=sum(abs(data_stamps[e[0]]-data_stamps[e[1]])>3e9 for e in measurements),
             prior_px=prior_px,fit_px=fit_px)
    print('Edges',len(measurements),'median pairwise residual px',np.median(prior_px),np.median(fit_px),
          'pose shift m',np.percentile(np.linalg.norm(corrected[:,:3,3]-centers,axis=1),[50,95]),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('work',type=Path);p.add_argument('--workers',type=int,default=7)
    a=p.parse_args();align(a.work,a.workers)
