"""Project visibility-tested RGB photographs onto coherent surface patches and bake UV atlases."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import open3d as o3d
from scipy import sparse

from texture_isaac_scan import project, pack
from reconstruct_lyra_route import registered_depth


def prepare_views(work):
    cameras=np.load(work/'cameras.npz');adjusted=np.load(work/'poses.npz')
    poses=adjusted['color_poses'];dposes=adjusted['depth_poses'];k=cameras['color_k'];dk=cameras['depth_k']
    depths=np.load(work/'depth.npy',mmap_mode='r');real=len(poses)
    lyra=np.load(work/'lyra.npz') if (work/'lyra.npz').is_file() else None
    virtual=lyra['poses'] if lyra is not None else poses[:0]
    n=real+len(virtual)
    depth=np.lib.format.open_memmap(work/'rgb_depth.npy',mode='w+',dtype='u2',shape=(n,240,320))
    for i in range(real):
        m=registered_depth(depths[i],dk,k,np.linalg.solve(poses[i],dposes[i]),(640,480))
        depth[i]=np.rint(1000*m).astype('u2')
    if lyra is not None:
        depth[real:]=lyra['depth_mm']
    for i,im in enumerate(lyra['rgb'] if lyra is not None else (),real):
        if not cv2.imwrite(str(work/'photos'/f'{i:04d}.jpg'),cv2.resize(im[:,:,::-1],(640,480)),[cv2.IMWRITE_JPEG_QUALITY,96]):
            raise OSError('Could not write the Lyra fallback texture')
    return np.concatenate([poses,virtual]),k,depth,np.r_[np.clip(np.sqrt(cameras['sharpness']/95.),.38,1.7),
                                                         np.full(len(virtual),.48)],real


def face_properties(v,f):
    cent=np.empty((len(f),3),'f4');norm=np.empty_like(cent)
    for s in range(0,len(f),150000):
        p=v[f[s:s+150000]];cent[s:s+len(p)]=p.mean(axis=1)
        x=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);norm[s:s+len(p)]=x/np.maximum(np.linalg.norm(x,axis=1,keepdims=True),1.e-9)
    grid=np.floor(cent/.48).astype('i4')
    signature=np.column_stack((grid,np.argmax(abs(norm),axis=1).astype('i4')))
    _,patch=np.unique(np.ascontiguousarray(signature).view('V16').ravel(),return_inverse=True)
    return cent,norm,patch.astype('i4')


def view_votes(scene,cent,norm,patch,poses,k,depth,sharp,real,work):
    nk=k.copy();nk[:2]/=2;intr=o3d.core.Tensor(nk)
    h,w=240,320;n=len(poses)
    rendered=np.lib.format.open_memmap(work/'render_depth.npy',mode='w+',dtype='u2',shape=(n,h,w))
    groups=[];columns=[];votes=[];lum=[]
    yy,xx=np.indices((h,w))
    margin=np.minimum.reduce([xx/w,(w-1-xx)/w,yy/h,(h-1-yy)/h])
    for i,pose in enumerate(poses):
        ray=scene.create_rays_pinhole(intr,o3d.core.Tensor(np.linalg.inv(pose)),w,h)
        hits=scene.cast_rays(ray,nthreads=5);z=hits['t_hit'].numpy()
        valid=(z>.30)&(z<9.) & (margin>.009)
        rendered[i]=np.rint(1000*np.where(np.isfinite(z)&(z<30),z,0.)).astype('u2')
        dz=depth[i].astype('f4')*.001; measured=dz>0
        good=valid&(~measured|(abs(z-dz)<.12+.035*z)) if i<real else valid&measured&(abs(z-dz)<.07+.02*z)
        if good.sum()<10:continue
        ix=hits['primitive_ids'].numpy()[good].astype('i4');g=patch[ix]
        eye=pose[:3,3].astype('f4');direction=eye-cent[ix]
        cosine=abs(np.einsum('ij,ij->i',direction,norm[ix]))/np.maximum(np.linalg.norm(direction,axis=1),.1)
        weight=(np.sqrt(np.maximum(cosine,.025))*np.clip(margin[good]*6,.08,1.)*sharp[i]/(.6+.44*z[good])*
                np.where(measured[good],1.,.44))
        if i>=real:weight*=.23
        u,rev=np.unique(g,return_inverse=True)
        score=np.bincount(rev,weights=weight)
        rgb=cv2.imread(str(work/'photos'/f'{i:04d}.jpg'),cv2.IMREAD_GRAYSCALE)
        brightness=cv2.resize(rgb,(w,h),interpolation=cv2.INTER_AREA)[good]
        groups.append(u);columns.append(np.full(len(u),i));votes.append(score)
        lum.append(np.bincount(rev,weights=weight*np.log(np.maximum(brightness,10.)))/np.maximum(score,1.e-9))
        if i%300==0:print('Visibility',i,'/',n,flush=True)
    groups=np.concatenate(groups);columns=np.concatenate(columns);votes=np.concatenate(votes);lum=np.concatenate(lum)
    table=sparse.csr_matrix((votes,(groups,columns)),shape=(int(patch.max())+1,n))
    # Correct modest exposure jumps between overlapping source photographs.
    valid=(votes>6)&(columns<real);g=groups[valid];img=columns[valid];weight=np.sqrt(votes[valid])
    avg=np.bincount(g,weights=weight*lum[valid],minlength=table.shape[0])/np.maximum(np.bincount(g,weights=weight,minlength=table.shape[0]),1e-6)
    # Estimate only a per-photo scale; do not change scene contrast.
    scale=np.ones(n)
    for i in range(real):
        ok=img==i
        if ok.sum()>=12:scale[i]=np.exp(np.clip(np.median(avg[g[ok]]-lum[valid][ok]),-.105,.105))
    return table,rendered,scale


def select_faces(v,f,cent,norm,patch,poses,k,depth,sharp,real,table,rendered):
    count=table.shape[0];choices=[[] for _ in poses]
    for p in range(count):
        a,b=table.indptr[p:p+2];ids=table.indices[a:b];val=table.data[a:b]
        if not len(ids):continue
        order=np.argsort(val)[::-1];top=order[:10]
        # Reserve a backup slot for supported Lyra views in the stair region.
        virtual=order[ids[order]>=real][:2]
        for j in np.unique(np.r_[top,virtual]):
            choices[ids[j]].append((p,val[j]/val[order[0]]))
    sorted_faces=patch.argsort(kind='stable');starts=np.r_[0,np.cumsum(np.bincount(patch,minlength=count))]
    label=np.full(len(f),-1,'i4');best=np.zeros(len(f),'f4');pref=np.zeros(count,'f4')
    for i,selected in enumerate(choices):
        if not selected:continue
        cells=np.array([a for a,_ in selected],dtype=int)
        pref[cells]=[b for _,b in selected]
        ids=np.concatenate([sorted_faces[starts[p]:starts[p+1]] for p in cells])
        for start in range(0,len(ids),65000):
            ix=ids[start:start+65000];p=poses[i]
            uv,z=project(cent[ix],p,k)
            valid=(z>.25)&(z<9.)&(uv[:,0]>=2)&(uv[:,0]<638)&(uv[:,1]>=2)&(uv[:,1]<478)
            ix,uv,z=ix[valid],uv[valid],z[valid]
            if not len(ix):continue
            u,vv=np.floor(uv.T/2).astype('i4')
            expected=rendered[i,vv,u]*.001; measured=depth[i,vv,u]*.001
            valid=(expected>0)&(z<=expected+.045+.012*z)
            if i<real:
                valid&=(measured==0)|(abs(z-measured)<.12+.035*z)
            else:
                valid&=(measured>0)&(abs(z-measured)<.07+.02*z)
            ix,uv,z,measured=ix[valid],uv[valid],z[valid],measured[valid]
            if not len(ix):continue
            pix,zz=project(v[f[ix]],p,k)
            valid=((zz>.20)&(pix[:,:,0]>=1)&(pix[:,:,0]<639)&(pix[:,:,1]>=1)&(pix[:,:,1]<479)).all(axis=1)
            ix,uv,z,measured=ix[valid],uv[valid],z[valid],measured[valid]
            dr=cent[ix]-p[:3,3];inc=abs(np.einsum('ij,ij->i',dr,norm[ix]))/np.maximum(np.linalg.norm(dr,axis=1),.1)
            border=np.minimum.reduce([uv[:,0]/640,(640-uv[:,0])/640,uv[:,1]/480,(480-uv[:,1])/480])
            quality=(np.sqrt(np.maximum(inc,.035))*np.clip(border*7,.07,1.)*sharp[i]/(.7+.48*z)*
                     np.where(measured>0,.70+.30*np.exp(-abs(z-measured)/.07),.47))
            if i>=real:quality*=.16
            quality*=.27+.73*np.sqrt(pref[patch[ix]])
            update=quality>best[ix];label[ix[update]]=i;best[ix[update]]=quality[update]
    return label


def texture(work):
    cv2.setNumThreads(1)
    with np.load(work/'surface.npz') as d:v,f=d['v'],d['f']
    poses,k,depth,sharp,real=prepare_views(work);cent,norm,patch=face_properties(v,f)
    scene=o3d.t.geometry.RaycastingScene(nthreads=5)
    scene.add_triangles(o3d.core.Tensor(v),o3d.core.Tensor(f.astype('u4')))
    table,rendered,gain=view_votes(scene,cent,norm,patch,poses,k,depth,sharp,real,work)
    labels=select_faces(v,f,cent,norm,patch,poses,k,depth,sharp,real,table,rendered)
    src=work/'balanced_photos';src.mkdir(exist_ok=True)
    for i in np.unique(labels[labels>=0]):
        name=f'{i:04d}.jpg';im=cv2.imread(str(work/'photos'/name))
        if not cv2.imwrite(str(src/name),np.clip(im*gain[i],0,255).astype('u1'),[cv2.IMWRITE_JPEG_QUALITY,97]):
            raise OSError(name)
    tex=work/'textures';tex.mkdir(exist_ok=True)
    uv,atlas,nphotos=pack(v,f,labels,np.arange(len(poses)),poses,k,src,tex)
    print('Atlases',nphotos,int(atlas.max()+1),'textured faces',int((atlas>=0).sum()),len(f),flush=True)
    np.savez(work/'materials.npz',uv=uv,atlas=atlas,labels=labels)
    areas=np.empty(len(f),'f4')
    for s in range(0,len(f),150000):
        q=v[f[s:s+150000]];areas[s:s+len(q)]=.5*np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1)
    def fraction(mask):return float(areas[mask].sum(dtype='f8')/areas.sum(dtype='f8'))
    (work/'texture.json').write_text(json.dumps(dict(real_photo_views=int(len(np.unique(labels[(labels>=0)&(labels<real)]))),
        lyra_texture_views=int(len(np.unique(labels[labels>=real]))),atlases=int(atlas.max()+1),
        photo_surface_fraction=fraction((labels>=0)&(labels<real)),lyra_surface_fraction=fraction(labels>=real),
        fallback_surface_fraction=fraction(labels<0)),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('work',type=Path);texture(p.parse_args().work)
