"""Recover further sloped and vertical surfaces seen by the RGB-D camera."""
import cv2
import numpy as np
import open3d as o3d
from scipy import ndimage
from scipy.spatial import cKDTree

from build_building_contours import Panel, FINE, ROOT, JOB, spans, components
from check_fine_mesh import scene, query


def existing_scene(parts,b):
    verts=[];faces=[];count=0
    for part in parts:
        q=(part.grid@b.T).reshape(-1,3);ix=np.arange(len(q)).reshape(part.grid.shape[:2])
        t=np.stack([ix[:-1,:-1],ix[1:,:-1],ix[1:,1:],ix[:-1,1:]],axis=-1)[part.mask]
        faces.append(t[:,[0,1,2,0,2,3]].reshape(-1,3)+count);verts.append(q);count+=len(q)
    return scene(np.vstack(verts),np.vstack(faces))


def residual_points(reference,b):
    cfg=np.load(FINE/'cameras.npz');poses=np.load(ROOT/'photomesh_hd/aligned.npz')['color_poses']
    depth=np.load(FINE/'rgb_depth.npy',mmap_mode='r')
    k=cfg['color_k'].copy();k[:2]/=8
    yy,xx=np.indices((60,80));rays=np.stack([(xx-k[0,2])/k[0,0],(yy-k[1,2])/k[1,1],np.ones_like(xx)],-1)
    data=[]
    for i in range(0,len(poses),2):
        pose=poses[i]
        hit=query(reference,k,pose,(80,60))['t_hit'].numpy()
        z=depth[i,::4,::4]*.001;local=rays*z[:,:,None]
        n=np.cross(local[1:-1,2:]-local[1:-1,:-2],local[2:,1:-1]-local[:-2,1:-1])
        scale=np.linalg.norm(n,axis=2);n/=np.maximum(scale[:,:,None],1.e-8)
        mask=cv2.imread(str(JOB/'exclusion'/f'{i:04}.png'),0)[::8,::8]>0
        ok=(z>.32)&(z<6.1)&(z+.19+.015*z<hit)&~mask
        good=ok[1:-1,1:-1]&(scale>.0001)&(np.abs(z[1:-1,2:]-z[1:-1,:-2])<.16)&(np.abs(z[2:,1:-1]-z[:-2,1:-1])<.16)
        q=(local[1:-1,1:-1][good]@pose[:3,:3].T+pose[:3,3])@b
        normals=n[good]@pose[:3,:3].T@b
        data.append(np.c_[q,normals])
    raw=np.vstack(data);pc=o3d.geometry.PointCloud(o3d.utility.Vector3dVector(raw[:,:3]));pc.normals=o3d.utility.Vector3dVector(raw[:,3:])
    pc=pc.voxel_down_sample(.072)
    return np.asarray(pc.points).copy(),np.asarray(pc.normals).copy()


def extend(parts,b,arch,report):
    base=existing_scene(parts,b);points,norm=residual_points(base,b)
    raw_count=len(points);rng=np.random.default_rng(392)
    track=arch['trajectory'][:,1:4]@b;route=cKDTree(track/[.58,.58,.70])
    additions=[];geometries=[]
    # Angularly consistent large planes only. Visible surfaces commonly touch an
    # existing plane at one edge while the rest was outside the LiDAR field of view.
    for attempt in range(55):
        if len(points)<220:break
        sample=rng.choice(len(points),min(2200,len(points)),replace=False)
        subset=points[sample];ns=norm[sample]
        usable=np.flatnonzero(np.linalg.norm(ns,axis=1)>.80)
        if len(usable)<12:break
        seeds=rng.choice(usable,min(380,len(usable)),replace=False)
        n=ns[seeds]/np.linalg.norm(ns[seeds],axis=1,keepdims=True)
        d=(subset[seeds]*n).sum(1)
        agree=(abs(subset@n.T-d)<.080)&(abs(ns@n.T)>.83)
        winner=np.argmax(agree.sum(0));normal=n[winner];level=d[winner]
        inlier=(abs(points@normal-level)<.106)&(abs(norm@normal)>.77)
        if inlier.sum()<145:break
        for _ in range(2):
            q=points[inlier];c=q.mean(0);_,_,vh=np.linalg.svd(q-c,full_matrices=False)
            normal=vh[-1];level=float(normal@c)
            inlier=(abs(points@normal-level)<.095)&(abs(norm@normal)>.79)
        q=points[inlier];points=points[~inlier];norm=norm[~inlier]
        if len(q)<145:continue
        # Snap only nearly plumb/horizontal fits.
        dominant=abs(normal).argmax()
        if abs(normal[dominant])>.9985:
            normal=np.eye(3)[dominant]*np.sign(normal[dominant]);level=float(np.median(q@normal))
        if abs(normal[2])<.85:
            u=np.cross([0,0,1],normal);u/=np.linalg.norm(u);w=np.cross(normal,u)
        else:
            u=np.array([1.,0,0])-normal*normal[0];u/=np.linalg.norm(u);w=np.cross(normal,u)
        uv=np.c_[q@u,q@w];lo=uv.min(0);hi=uv.max(0)
        if np.min(hi-lo)<.64:continue
        us=spans(lo[0]-.1,hi[0]+.1,.14);ws=spans(lo[1]-.1,hi[1]+.1,.14)
        h=np.histogram2d(uv[:,0],uv[:,1],bins=(us,ws))[0]
        measured=(h>0)&(ndimage.gaussian_filter(h,.9)>.44)
        mask=ndimage.binary_closing(measured,structure=np.ones((5,5)))|measured
        # Interpolate just bounded voids smaller than an ordinary doorway.
        hole=ndimage.binary_fill_holes(mask)&~mask
        lab,num=ndimage.label(hole);size=np.bincount(lab.ravel())
        mask |= hole&(size[lab]<22)
        mask &= ndimage.maximum_filter(ndimage.binary_opening(mask,structure=np.ones((4,4))),size=5)
        U,W=np.meshgrid(us,ws,indexing='ij');grid=(U[:,:,None]*u+W[:,:,None]*w+normal*level).astype('f4')
        center=(grid[:-1,:-1]+grid[1:,1:])*.5
        mask &= route.query(center.reshape(-1,3)/[.58,.58,.70],workers=4)[0].reshape(mask.shape)>1.08
        # Preserve clear space above the driven staircase and first-floor corridor.
        x,y,z=center.transpose(2,0,1);steps=arch['steps'];l,r,low=arch['stair_bounds'];ht=np.r_[low,steps[:,1]][np.searchsorted(steps[:,0],y,side='right')]
        stair=(x>l+.025)&(x<r-.025)&(y>steps[0,0]-.49)&(y<steps[-1,0]+.50)
        mask &= ~(stair&(z>ht+.02)&(z<ht+1.98))
        mask &= ~((x>-5.92)&(x<32.55)&(y>-8.95)&(y<-6.62)&(z>steps[-1,1]+.03)&(z<steps[-1,1]+2.05))
        mask=components(mask,67)
        if not mask.any():continue
        # Reject duplicates that became coincident after the normal was snapped.
        world=(center[mask]@b.T).astype('f4')
        ds=base.compute_distance(o3d.core.Tensor(world),nthreads=4).numpy()
        if np.median(ds)<.12:continue
        group=3 if abs(normal[2])<.65 else 4 if np.median(center[mask][:,2])>1.8 else 0
        additions.append(Panel('Zusatzfläche_gemessen',group,grid,mask,normal.astype('f4'),.055))
        geometries.append(dict(area_m2=round(mask.sum()*np.mean(np.diff(us))*np.mean(np.diff(ws)),2),normal=normal.round(3).tolist()))
    parts.extend(additions)
    report['additional_planes_from_rgbd']=geometries;report['residual_rgbd_voxels']=raw_count
