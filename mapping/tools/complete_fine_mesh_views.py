"""Recover small visual holes only when real photographs and separated Lyra depth views agree."""
import argparse
from functools import lru_cache
import json
from pathlib import Path

import cv2
import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree


def project(p,pose,k):
    q=(p-pose[:3,3])@pose[:3,:3]
    pix=q@k.T
    uv=np.rint(pix[:,:2]/np.maximum(pix[:,2,None],.01)).astype('i4')
    good=(q[:,2]>.3)&(uv[:,0]>=1)&(uv[:,0]<319)&(uv[:,1]>=1)&(uv[:,1]<239)
    u,v=np.clip(uv,[0,0],[319,239]).T
    return u,v,q[:,2],good


def neighbours(poses,tree,p,minimum,limit):
    _,ds=tree.query(p[:3,3],k=min(105,len(poses)))
    chosen=[]
    for j in ds:
        d=np.linalg.norm(poses[j,:3,3]-p[:3,3])
        if d<minimum or d>1.35 or poses[j,:3,2]@p[:3,2]<.69:continue
        if any(np.linalg.norm(poses[j,:3,3]-poses[a,:3,3])<.075 for a in chosen):continue
        chosen.append(j)
        if len(chosen)==limit:break
    return chosen


def build(work):
    wide=np.load(work/'lyra_wide.npz')
    depths,rgbs,poses,k=[wide[key] for key in ('depth','rgb','poses','k')]
    verts=[];faces=[];colors=[];offset=0;filled=set()
    pixel_grid=np.arange(240*320,dtype='i4').reshape(240,320)
    nw,ne,sw,se=pixel_grid[:-1,:-1],pixel_grid[:-1,1:],pixel_grid[1:,:-1],pixel_grid[1:,1:]
    cells=np.r_[np.stack((nw,sw,ne),-1).reshape(-1,3),np.stack((ne,sw,se),-1).reshape(-1,3)]
    views=np.load(work/'poses.npz')['color_poses']
    actual=np.load(work/'rgb_depth.npy',mmap_mode='r')
    candtree=cKDTree(poses[:,:3,3]);real_tree=cKDTree(views[:,:3,3])
    rk=np.load(work/'cameras.npz')['color_k'];rk[:2]/=2
    with np.load(work/'final/surface.npz') as surf:v,f=surf['v'],surf['f']
    geo=o3d.t.geometry.RaycastingScene(nthreads=5)
    geo.add_triangles(o3d.core.Tensor(v),o3d.core.Tensor(f.astype('u4')))
    yy,xx=np.indices((240,320))
    rays=np.stack(((xx-k[0,2])/k[0,0],(yy-k[1,2])/k[1,1],np.ones_like(yy)),-1)
    @lru_cache(maxsize=80)
    def photo(i):
        im=cv2.imread(str(work/'photos'/f'{i:04d}.jpg'))[:,:,::-1]
        return cv2.resize(im,(320,240),interpolation=cv2.INTER_AREA)
    accepted=0;usable_views=0;counts=np.zeros(6,dtype=int)
    for i,pose in enumerate(poses):
        z=depths[i]*.001
        hits=geo.cast_rays(geo.create_rays_pinhole(o3d.core.Tensor(k),o3d.core.Tensor(np.linalg.inv(pose)),320,240),nthreads=4)
        existing=hits['t_hit'].numpy()
        # An additional surface may only appear where the verified mesh leaves a gap.
        mask=(z>.4)&(z<9)&(existing>z+.15+.025*z)
        mask=cv2.dilate(mask.astype('u1'),np.ones((3,3),'u1')).astype(bool)&(z>.4)
        if not mask.any():continue
        ids=np.flatnonzero(mask)
        pts=(rays.reshape(-1,3)[ids]*z.ravel()[ids,None])@pose[:3,:3].T+pose[:3,3]
        ref=rgbs[i].reshape(-1,3)[ids].astype('f4')
        stable=np.zeros(len(ids),'i2');agree=np.zeros_like(stable);veto=np.zeros_like(stable)
        for j in neighbours(poses,candtree,pose,.16,5):
            u,vv,d,ok=project(pts,poses[j],k);d2=depths[j,vv,u]*.001
            stable+=ok&(abs(d-d2)<.065+.027*d)
        for j in neighbours(views,real_tree,pose,.12,9):
            u,vv,d,ok=project(pts,views[j],rk)
            dm=actual[j,vv,u]*.001;known=(dm>.3)&(dm<5.)
            value=photo(j)[vv,u].astype('f4')
            colour=np.mean(abs(value-ref),axis=1)
            agree+=ok&(~known|(abs(dm-d)<.10+.027*d))&(colour<20)
            veto+=ok&known&(dm>d+.16+.022*d)
        use=(stable>=2)&(agree>=3)&(veto==0)
        counts+=np.array([len(ids),(stable>=2).sum(),(agree>=3).sum(),(veto>0).sum(),use.sum(),len(neighbours(views,real_tree,pose,.12,9))])
        if use.sum()<20:continue
        final_ids=ids[use]
        support=np.zeros(240*320,bool);support[final_ids]=True
        triangles=cells[support[cells].all(1)]
        if not len(triangles):continue
        point_world=(rays.reshape(-1,3)*z.ravel()[:,None])@pose[:3,:3].T+pose[:3,3]
        # A measured sightline from another view can supply a missing tile. Use just one
        # reconstructed skin per small spatial cell to avoid layered depth sheets.
        cent=point_world[triangles].mean(1)
        keys=np.floor(cent/.060).astype('i8')+4000
        codes=(keys[:,0]*8192+keys[:,1])*8192+keys[:,2]
        allowed=np.array([c not in filled for c in np.unique(codes)])
        chosen=np.unique(codes)[allowed];filled.update(chosen)
        triangles=triangles[np.isin(codes,chosen)]
        if not len(triangles):continue
        used,remap=np.unique(triangles,return_inverse=True)
        verts.append(point_world[used]);faces.append(remap.reshape(-1,3)+offset)
        colors.append(rgbs[i].reshape(-1,3)[used]);offset+=len(used)
        accepted+=use.sum();usable_views+=1
    print('Validation rays, consistent model, consistent photographs, depth veto, joint, available views:',counts.tolist(),flush=True)
    print('Candidate rays integrated',accepted,usable_views,flush=True)
    mesh=o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(np.concatenate(verts)),o3d.utility.Vector3iVector(np.concatenate(faces)))
    mesh.vertex_colors=o3d.utility.Vector3dVector(np.concatenate(colors)/255.)
    mesh=mesh.simplify_vertex_clustering(.015);mesh.remove_degenerate_triangles();mesh.remove_duplicated_triangles()
    cv=np.asarray(mesh.vertices).astype('f4');cf=np.asarray(mesh.triangles).astype('i4')
    if not len(cf):raise ValueError('No independently supported additional polygons')
    # Require local measured support even where image evidence spans a larger open region.
    mid=cv[cf].mean(1)
    measured=o3d.t.io.read_point_cloud('reports/20261123_kamerakarte/karte_rgb.pcd').point.positions.numpy()
    dist=cKDTree(measured).query(mid,workers=4)[0]
    surface_dist=geo.compute_distance(o3d.core.Tensor(mid),nthreads=5).numpy()
    good=(dist<.27)&(surface_dist>.024)
    mesh.remove_triangles_by_mask(~good)
    groups,counts,_=mesh.cluster_connected_triangles()
    mesh.remove_triangles_by_mask(np.asarray(counts)[np.asarray(groups)]<14);mesh.remove_unreferenced_vertices()
    rgb=np.rint(np.asarray(mesh.vertex_colors)*255).clip(0,255).astype('u1')
    cv=np.asarray(mesh.vertices).astype('f4');cf=np.asarray(mesh.triangles).astype('i4')
    np.savez(work/'completion.npz',v=cv,f=cf,colors=rgb)
    print(json.dumps(dict(views=usable_views,confirmed_rays=int(accepted),extra_triangles=len(cf))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('work',type=Path);build(p.parse_args().work)
