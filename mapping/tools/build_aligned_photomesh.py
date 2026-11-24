"""Build a photo-textured RGB-D mesh in the measured LiDAR frame."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import open3d as o
from scipy.spatial import cKDTree

FINE=Path('.runtime/scan1123/fine')
WORK=Path('.runtime/scan1123/photomesh_hd')
OUT=Path('reports/20261124_fotomesh_hd')

def fuse():
    c=np.load(FINE/'cameras.npz'); a=np.load(WORK/'aligned.npz'); depth=np.load(FINE/'depth.npy',mmap_mode='r')
    poses=a['depth_poses']; rgb=a['color_poses']; dk=c['depth_k'];k=c['color_k']
    w,h=320,240
    from mesh_hesai_map import integrate
    from extract_sparse_surface import store_blocks,extract
    from prepare_textured_surface import compact,thin_components,simplify_tiles
    from color_fine_mesh_fallback import fallback
    intr=o.core.Tensor(dk,o.core.float64)
    vol=o.t.geometry.VoxelBlockGrid(attr_names=['tsdf','weight'],attr_dtypes=[o.core.float32]*2,attr_channels=[(1,),(1,)],voxel_size=.012,block_resolution=8,block_count=60000)
    yy,xx=np.indices((h,w),dtype='f4')
    ray=np.stack(((xx-dk[0,2])/dk[0,0],(yy-dk[1,2])/dk[1,1],np.ones_like(xx)),axis=-1)
    kernel=np.ones((3,3),'u1')
    for i,p in enumerate(poses):
        original=depth[i].copy()
        med=cv2.medianBlur(original,3)
        ok=(original>260)&(original<6400)&(abs(original.astype('i4')-med)<32+.018*med)
        dm=original*.001
        xyz=ray*dm[:,:,None];agree=np.zeros((h,w),'u1');free=agree.copy()
        for j in (i-4,i-2,i-1,i+1,i+2,i+4):
            if not 0<=j<len(poses) or c['segment'][i]!=c['segment'][j]:continue
            rel=np.linalg.solve(poses[j],p).astype('f4')
            q=xyz@rel[:3,:3].T+rel[:3,3];z=q[:,:,2]
            u=np.rint(q[:,:,0]*dk[0,0]/np.maximum(z,.05)+dk[0,2]).astype(int)
            v=np.rint(q[:,:,1]*dk[1,1]/np.maximum(z,.05)+dk[1,2]).astype(int)
            observed=depth[j,v.clip(0,h-1),u.clip(0,w-1)]*.001
            valid=(u>=0)&(v>=0)&(u<w)&(v<h)&(z>.22)&(observed>.25)&(observed<6.45)
            agree+=valid&(abs(observed-z)<.065+.023*z)
            free+=valid&(observed-z>.13+.035*z)
        ok &= (agree>=1)&(free<=agree+1)
        D=np.where(ok,original,0).astype('u2')
        integrate(vol,D,intr,p,6.4,.045/.012)
        if i%200==0:print('DEPTH',i,int(ok.sum()),vol.hashmap().size(),flush=True)
    store_blocks(vol,WORK);del vol
    v,f=extract(WORK,.012)
    print('RAW TRIANGLES',len(f),flush=True)
    f=thin_components(f,len(v))
    v,f=simplify_tiles(*compact(v,f))
    np.savez(WORK/'surface.npz',v=v,f=f)
    fallback(WORK,Path('.runtime/scan1123/mapped/rgb.pcd'))
    (WORK/'fallback.npy').replace(WORK/'rgb.npy')
    print('FUSED',len(v),len(f),flush=True)

def texture():
    from texture_fine_mesh import face_properties,view_votes,select_faces
    from texture_isaac_scan import pack
    from check_fine_mesh import scene
    c=np.load(FINE/'cameras.npz');poses=np.load(WORK/'aligned.npz')['color_poses']; k=c['color_k']
    raw=np.load(WORK/'surface.npz');v,f=raw['v'],raw['f']; cent,norm,patch=face_properties(v,f)
    if not (WORK/'photos').exists():(WORK/'photos').symlink_to((FINE/'photos').resolve())
    depth=np.load(FINE/'rgb_depth.npy',mmap_mode='r')
    sharp=np.clip((c['sharpness']/60.)**.65,.24,2.15); real=len(poses)
    obj=scene(v,f)
    votes,rendered,gain=view_votes(obj,cent,norm,patch,poses,k,depth,sharp,real,WORK)
    labels=select_faces(v,f,cent,norm,patch,poses,k,depth,sharp,real,votes,rendered)
    uv,pages,n=pack(v,f,labels,np.arange(real),poses,k,FINE/'photos',WORK/'textures')
    np.savez(WORK/'materials.npz',uv=uv,atlas=pages,labels=labels)
    if (WORK/'detail.json').exists():
        uv2,page2,_=pack(v,f,labels,np.arange(real),poses,k,WORK/'multiview_photos',WORK/'textures2x',photo_scale=2)
        assert np.array_equal(pages,page2) and np.array_equal(uv,uv2)
    print('TEXTURED',n,len(np.unique(pages)),float((labels>=0).mean()),flush=True)

def combine():
    from publish_fine_mesh import write_glb,write_isaac
    from texture_isaac_scan import project
    raw=np.load(WORK/'surface.npz');v,f=raw['v'],raw['f'];m=np.load(WORK/'materials.npz')
    old=np.load(FINE/'surface.npz');ov=old['v'];of=old['f'];keep=np.flatnonzero(np.load(FINE/'final_keep.npy'))
    src=np.load(FINE/'materials.npz');prev_atlas=src['atlas'][keep];of=of[keep]
    mid=ov[of].mean(1)
    gt=cKDTree(v)
    # Original measured geometry covers areas outside the RGB-D field or range.
    # Discard its faces wherever the aligned reconstruction already occupies the surface.
    dist=gt.query(mid,workers=6)[0]
    candidate=np.flatnonzero(dist>.22)
    cc=np.load(FINE/'cameras.npz');poses=np.load(WORK/'aligned.npz')['color_poses'];k=cc['color_k']
    rendered=np.load(WORK/'render_depth.npy',mmap_mode='r')
    tree=cKDTree(mid[candidate]); conflicts=np.zeros(len(candidate),'i4'); supports=conflicts.copy()
    for i,p in enumerate(poses):
        nearby=np.asarray(tree.query_ball_point(p[:3,3],6.7),dtype=int)
        uv,z=project(mid[candidate[nearby]],p,k)
        vis=(z>.28)&(uv[:,0]>=4)&(uv[:,0]<636)&(uv[:,1]>=4)&(uv[:,1]<476)
        xy=(uv[vis]/2).astype(int);z=z[vis]; ids=nearby[vis]
        d=rendered[i,xy[:,1],xy[:,0]]*.001
        conflicts[ids]+=(d>z+.16+.022*z)
        supports[ids]+=(d>.2)&(abs(d-z)<.11+.02*z)
    use=candidate[conflicts<2+supports]
    olduv=src['uv'][keep[use]];pages=prev_atlas[use].copy()
    dst=int(m['atlas'].max())+1
    for page in np.unique(pages[pages>=0]):
        link=WORK/'textures'/f'detail_{int(page)+dst:02d}.jpg'
        if not link.exists():link.symlink_to((FINE/'textures'/f'detail_{page:02d}.jpg').resolve())
    pages[pages>=0]+=dst
    vv=np.vstack((v,ov));ff=np.vstack((f,of[use]+len(v)))
    uv=np.concatenate((m['uv'],olduv));at=np.r_[m['atlas'],pages];cols=np.vstack((np.load(WORK/'rgb.npy'),np.load(FINE/'fallback.npy')))
    if not (WORK/'rail.npz').exists():(WORK/'rail.npz').symlink_to((FINE/'rail.npz').resolve())
    write_glb(WORK,OUT,vv,ff,uv,at,cols)
    write_isaac(WORK,OUT,vv,ff,uv,at,cols,Path('.runtime/scan1123/architecture/final_collision.npz'))
    metrics=dict(rgbd_triangles=len(f),retained_wide_area_triangles=len(use),triangles=len(ff),photo_textured_faces=int((at>=0).sum()),
        atlas_pages=len(np.unique(at[at>=0])),rgbd_atlas_source_photos=len(np.unique(m['labels'][m['labels']>=0])),voxel_m=.012)
    (WORK/'model.json').write_text(json.dumps(metrics,indent=2))

if __name__=='__main__':
    cv2.setNumThreads(1)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['fuse','texture','combine'])
    {'fuse':fuse,'texture':texture,'combine':combine}[p.parse_args().action]()
