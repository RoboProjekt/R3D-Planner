"""Align the latest RGB-D training views to each other with a LiDAR pose prior."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import cv2
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from align_lyra_cameras import detect, relative_constraint, fit_pose_graph

FINE=Path('.runtime/scan1123/fine')
WORK=Path('.runtime/scan1123/photomesh_hd')

def main():
    cv2.setNumThreads(1)
    cameras=np.load(FINE/'cameras.npz'); held=np.load(FINE/'hold.npz')
    depth=np.load(FINE/'rgb_depth.npy',mmap_mode='r')
    k=cameras['color_k']; kinv=np.linalg.inv(k); poses=cameras['color_poses']; stamps=cameras['stamps']
    assert np.intersect1d(stamps,held['stamps']).size==0
    count=len(stamps); tree=cKDTree(poses[:,:3,3])
    pool=ThreadPoolExecutor(10)
    images=[cv2.imread(str(FINE/'photos'/f'{i:04}.jpg'),0) for i in range(count)]
    ft=list(pool.map(detect,[FINE/'photos'/f'{i:04}.jpg' for i in range(count)]))
    def edges_for(i):
        d=depth[i].astype('f4')*.001
        smooth=(cv2.dilate(d,np.ones((3,3),'u1'))-cv2.erode(d,np.ones((3,3),'u1'))<.075+.022*d)&(d>.38)&(d<6.4)
        mask=cv2.resize(smooth.astype('u1'),(640,480),interpolation=cv2.INTER_NEAREST)
        points=cv2.goodFeaturesToTrack(images[i],650,.006,6,mask=mask,blockSize=5)
        if points is None:return []
        uv=points.reshape(-1,2); px=np.rint(uv/2).astype(int).clip(0,[319,239])
        xyz=(np.column_stack((uv,np.ones(len(uv))))@kinv.T)*d[px[:,1],px[:,0],None]
        neighbors=[j for j in (i+1,i+2,i+4,i+8) if j<count and cameras['segment'][i]==cameras['segment'][j] and (stamps[j]-stamps[i])<2.6e9]
        near=tree.query_ball_point(poses[i,:3,3],1.4)
        loops=sorted([j for j in near if j>i+15 and poses[j,:3,2]@poses[i,:3,2]>.76],key=lambda j:np.linalg.norm(poses[i,:3,3]-poses[j,:3,3]))
        for j in loops:
            if len(neighbors)>=7:break
            if all(abs(j-kk)>7 for kk in neighbors):neighbors.append(j)
        edges=[]
        for j in neighbors:
            prior=np.linalg.solve(poses[j],poses[i])
            obs=None
            if j-i<9:
                p1,st,_=cv2.calcOpticalFlowPyrLK(images[i],images[j],points,None,winSize=(23,23),maxLevel=3)
                rev,s2,_=cv2.calcOpticalFlowPyrLK(images[j],images[i],p1,None,winSize=(23,23),maxLevel=3)
                ok=(st[:,0]>0)&(s2[:,0]>0)&(np.linalg.norm(rev[:,0]-uv,axis=1)<.7)
                X=xyz[ok]; y=p1[ok,0]
                if len(X)>=24:
                    success,rv,tv,m=cv2.solvePnPRansac(X,y,k,None,iterationsCount=100,reprojectionError=2.,confidence=.995,flags=cv2.SOLVEPNP_EPNP)
                    if success and m is not None and len(m)>=max(22,.49*len(X)):
                        X=X[m[:,0]];y=y[m[:,0]]
                        rv,tv=cv2.solvePnPRefineLM(X,y,k,None,rv,tv)
                        R=cv2.Rodrigues(rv)[0];t=tv[:,0]
                        if Rotation.from_matrix(R.T@prior[:3,:3]).magnitude()<.18 and np.linalg.norm(t-prior[:3,3])<.28:
                            def err(r,tr):
                                q=(X@r.T+tr)@k.T
                                return np.median(np.linalg.norm(q[:,:2]/q[:,2,None]-y,axis=1))
                            obs=(R,t,len(m),err(prior[:3,:3],prior[:3,3]),err(R,t))
            if obs is None:
                a,desc=ft[i]
                if desc is None:continue
                pp=np.rint(a/2).astype(int).clip(0,[319,239]);good=smooth[pp[:,1],pp[:,0]]
                if sum(good)<18:continue
                X=(np.column_stack((a[good],np.ones(sum(good))))@kinv.T)*d[pp[good,1],pp[good,0],None]
                obs=relative_constraint(X,desc[good],ft[j],prior,k)
            if obs is not None:edges.append((i,j,*obs))
        return edges
    edges=[pair for e in pool.map(edges_for,range(count)) for pair in e]
    pool.shutdown()
    print('CONSTRAINTS',len(edges),flush=True)
    # Save a cross-view test split of edges before fitting the global graph.
    test=[e for e in edges if e[1]-e[0]>=2 and (e[0]*31+e[1]*7)%11==0]
    test_ids={(e[0],e[1]) for e in test}
    train=[e for e in edges if (e[0],e[1]) not in test_ids]
    updated,*_=fit_pose_graph(poses,train)
    def eval_edges(P):
        tr=[];rot=[]
        for i,j,r,t,*_ in test:
            u=np.linalg.solve(P[j],P[i]);tr.append(np.linalg.norm(u[:3,3]-t));rot.append(Rotation.from_matrix(u[:3,:3].T@r).magnitude()*180/np.pi)
        return dict(median_relative_translation_m=float(np.median(tr)),median_relative_rotation_deg=float(np.median(rot)))
    stats=dict(train_views=count,pairs=len(train),excluded_pairs=len(test),connected_views=len({j for e in train for j in e[:2]}),before=eval_edges(poses),after=eval_edges(updated))
    print(stats,flush=True)
    correction=updated@np.linalg.inv(poses)
    np.savez(WORK/'aligned.npz',color_poses=updated,depth_poses=correction@cameras['depth_poses'])
    (WORK/'align.json').write_text(json.dumps(stats,indent=2))
if __name__=='__main__':main()
