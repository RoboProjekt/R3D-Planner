"""Project full camera photographs onto the building surfaces and pack portable UV atlases."""
import cv2
import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree

TILE_W, TILE_H, PAD = 640,480,4
COLS,ROWS=6,8


def project(p,pose,k):
    q=(p-pose[:3,3])@pose[:3,:3]
    uv=q[...,:2]/np.maximum(.01,q[...,2:])*[k[0,0],k[1,1]]+k[:2,2]
    return uv,q[...,2]


def assign(v,f,groups,photos,depth_cache):
    with np.load(photos/'cameras.npz') as data:
        files=data['ids']; poses=data['color_poses']; dposes=data['depth_poses']; k=data['color_k']; dk=data['depth_k']
        sharp=data['sharpness']; w,h=data['size']
    with np.load(depth_cache) as data:
        depth=data['depth_mm'][files]
    if (w,h)!=(TILE_W,TILE_H):
        raise ValueError('Unsupported atlas image size')
    corners=v[f]; mid=corners.mean(axis=1); tree=cKDTree(mid)
    normals=np.cross(corners[:,1]-corners[:,0],corners[:,2]-corners[:,0])
    normals/=np.maximum(1.e-12,np.linalg.norm(normals,axis=1,keepdims=True))
    patches=np.column_stack((np.floor(mid/.72).astype(int),groups,np.argmax(abs(normals),axis=1)))
    _,patch=np.unique(patches,axis=0,return_inverse=True)
    votes=np.zeros((patch.max()+1,len(files)),dtype='f4')
    scores=np.zeros((len(f),len(files)),dtype='f2')
    geometry=o3d.t.geometry.RaycastingScene(nthreads=5)
    geometry.add_triangles(o3d.core.Tensor(v.astype('f4')),o3d.core.Tensor(f.astype('u4')))
    scale=4
    small_k=k.copy(); small_k[:2]/=scale
    intrinsic=o3d.core.Tensor(small_k)
    for i,pose in enumerate(poses):
        ids=np.array(tree.query_ball_point(pose[:3,3],10),dtype=int)
        if not len(ids): continue
        uv,z=project(mid[ids],pose,k)
        ok=(z>.25)&(uv[:,0]>2)&(uv[:,0]<w-3)&(uv[:,1]>2)&(uv[:,1]<h-3)
        uv,z,ids=uv[ok],z[ok],ids[ok]
        if not len(ids): continue
        tri_uv,tri_z=project(corners[ids],pose,k)
        ok=((tri_z>.18)&(tri_uv[:,:,0]>=1)&(tri_uv[:,:,0]<=w-2)&(tri_uv[:,:,1]>=1)&(tri_uv[:,:,1]<=h-2)).all(axis=1)
        uv,z,ids=uv[ok],z[ok],ids[ok]
        rays=geometry.create_rays_pinhole(intrinsic,o3d.core.Tensor(np.linalg.inv(pose)),int(w//scale),int(h//scale))
        expected=geometry.cast_rays(rays,nthreads=5)['t_hit'].numpy()
        u,vv=(uv/scale).astype(int).T
        visible=(z<=expected[vv,u]+.10+.018*z)
        duv,dz=project(mid[ids],dposes[i],dk); du,dv=np.rint(duv).astype(int).T
        dh,dw=depth[i].shape
        in_depth=(du>=0)&(du<dw)&(dv>=0)&(dv<dh)
        measured=depth[i,dv.clip(0,dh-1),du.clip(0,dw-1)]*.001
        valid_depth=in_depth&(measured>.2)&(measured<5.99)
        delta=dz-measured
        ok=visible&(~valid_depth|((delta<.12+.025*dz)&(delta>-.26-.035*dz)))
        ids,uv,z,delta,valid_depth=ids[ok],uv[ok],z[ok],delta[ok],valid_depth[ok]
        if not len(ids): continue
        dirn=pose[:3,3]-mid[ids]
        dist=np.linalg.norm(dirn,axis=1)
        cosine=np.abs(np.einsum('ij,ij->i',dirn,normals[ids]))/dist
        border=np.minimum.reduce([uv[:,0]/w,(w-1-uv[:,0])/w,uv[:,1]/h,(h-1-uv[:,1])/h])
        sharpness=np.clip(np.sqrt(sharp[i]/95.),.30,1.5)
        score=(np.maximum(cosine,.04)**.72*np.clip(border*5,.12,1.)*sharpness/(1.+.48*dist)
               *np.where(valid_depth,.60+.40*np.exp(-abs(delta)/.10),.40))
        scores[ids,i]=score
        votes[:,i]=np.bincount(patch[ids],weights=score,minlength=len(votes))
    best=scores.argmax(axis=1); ar=np.arange(len(f)); bestscore=scores[ar,best]
    preferred=votes.argmax(axis=1)[patch]
    best=np.where(scores[ar,preferred]>=.42*bestscore,preferred,best)
    best[bestscore<.006]=-1
    return best,files,poses,k


def pack(verts,faces,labels,files,poses,k,photos,output,photo_scale=1):
    """Pack only the parts of each original photograph used by detail faces."""
    output.mkdir(exist_ok=True)
    edge=2048
    uv=np.zeros((len(faces),3,2),'f4')
    atlas=np.full(len(faces),-1,'i4')
    patches=[]
    order=np.argsort(labels)
    for i in np.unique(labels[labels>=0]):
        ids=order[np.searchsorted(labels,i,sorter=order):np.searchsorted(labels,i,side='right',sorter=order)]
        px,_=project(verts[faces[ids]],poses[i],k)
        left,top=np.floor(px.min(axis=(0,1))).astype(int)
        right,bottom=np.ceil(px.max(axis=(0,1))).astype(int)+1
        patches.append((bottom-top,right-left,i,left,top,ids,px))
    page=-1; x=y=row_h=0; sheet=None
    def save(idx,img):
        if not cv2.imwrite(str(output/f'detail_{idx:02d}.jpg'),img,[cv2.IMWRITE_JPEG_QUALITY,96]):
            raise OSError('Could not write photo atlas')
    for h,w,i,left,top,ids,px in sorted(patches,key=lambda p:-p[0]):
        if x+w+2*PAD>edge: x=0; y+=row_h; row_h=0
        if sheet is None or y+h+2*PAD>edge:
            if sheet is not None: save(page,sheet)
            page+=1;sheet=np.full((edge*photo_scale,edge*photo_scale,3),128,'u1'); x=y=row_h=0
        s=photo_scale
        img=cv2.imread(str(photos/f'{files[i]:04d}.jpg'))[top*s:(top+h)*s,left*s:(left+w)*s]
        sheet[y*s:(y+h+2*PAD)*s,x*s:(x+w+2*PAD)*s]=cv2.copyMakeBorder(img,PAD*s,PAD*s,PAD*s,PAD*s,cv2.BORDER_REPLICATE)
        uv[ids,:,0]=(x+PAD+px[:,:,0]-left+.5)/edge
        uv[ids,:,1]=1-(y+PAD+px[:,:,1]-top+.5)/edge
        atlas[ids]=page
        x+=w+2*PAD;row_h=max(row_h,h+2*PAD)
    if sheet is not None: save(page,sheet)
    return uv,atlas,len(patches)
