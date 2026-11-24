"""Bake continuous clean photographs onto the measured walls around the stair."""
import cv2
import numpy as np
from scipy import ndimage
import bake_building_photo_planes as bake
from clean_building_photos import ROOT, JOB


def apply(v,f,uv,pages,colors,out,measured_rays):
    bake._PHOTO_DIR=JOB/'photos';bake._MASK_DIR=JOB/'exclusion'
    arch=np.load(ROOT/'architecture/scene.npz');b=arch['b']
    with (ROOT/'mapped/measured.pcd').open('rb') as stream:
        while stream.readline()!=b'DATA binary\n':pass
        pts=np.fromfile(stream,'<f4').reshape(-1,3)@b
    orig,end=measured_rays(b);delta=end-orig
    tri=v[f]@b;center=tri.mean(1);axis=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    orientation=abs(axis[:,0])/np.maximum(1.e-9,np.linalg.norm(axis,axis=1))
    keep=np.ones(len(f),bool)
    verts=[];faces=[];coords=[];labels=[]
    nextv=len(v);page=int(max(pages))+1;area=0.
    for x,yl,yr,zl,zr,side in [(-6.13,-21.,-14.,-1.30,2.30,-1.),(-12.13,-17.5,-9.15,-.80,4.8,1.)]:
        ys=np.linspace(yl,yr,int(np.ceil((yr-yl)/.12))+1)
        zs=np.linspace(zl,zr,int(np.ceil((zr-zl)/.12))+1)
        surf=pts[abs(pts[:,0]-x)<.095]
        ends=np.histogram2d(surf[:,1],surf[:,2],bins=(ys,zs))[0]
        crossing=((orig[:,0]-x)*(end[:,0]-x)<0)&(abs(end[:,0]-x)>.40)&(abs(orig[:,0]-x)>.30)
        start=orig[crossing];d=delta[crossing];hit=start+d*((x-start[:,0])/d[:,0])[:,None]
        through=np.histogram2d(hit[:,1],hit[:,2],bins=(ys,zs))[0]
        support=ndimage.gaussian_filter(ends,.7)
        passed=ndimage.gaussian_filter(through,.8)
        solid=ndimage.binary_closing(support>1.35,structure=np.ones((3,3)))|(support>2.8)
        solid &= ~((passed>2.)&(passed>support*.7))
        def supported(y,z):
            yi=np.searchsorted(ys,y,side='right')-1;zi=np.searchsorted(zs,z,side='right')-1
            inside=(yi>=0)&(yi<len(ys)-1)&(zi>=0)&(zi<len(zs)-1)
            return inside&solid[yi.clip(0,len(ys)-2),zi.clip(0,len(zs)-2)]
        keep &= ~((abs(center[:,0]-x)<.17)&(orientation>.46)&supported(center[:,1],center[:,2]))
        for y0 in range(0,len(ys)-1,18):
            y1=min(y0+18,len(ys)-1)
            for z0 in range(0,len(zs)-1,17):
                z1=min(z0+17,len(zs)-1);use=solid[y0:y1,z0:z1]
                if not use.any():continue
                # Each chart uses the identical continuous world plane for texture and geometry.
                def surf_fn(u,w):
                    return np.stack([np.full_like(u,x),ys[y0]+u*(ys[y1]-ys[y0]),zs[z0]+w*(zs[z1]-zs[z0])],-1)
                size=512
                image=bake.planar_image(surf_fn,[side,0.,0.],size,size)
                cv2.imwrite(str(out/'textures'/f'detail_{page:02}.jpg'),image,[cv2.IMWRITE_JPEG_QUALITY,97])
                y,z=np.meshgrid(ys[y0:y1+1],zs[z0:z1+1],indexing='ij')
                q=np.stack([np.full_like(y,x),y,z],-1)
                ids=np.arange(y.size).reshape(y.shape)
                quads=np.stack([ids[:-1,:-1],ids[1:,:-1],ids[1:,1:],ids[:-1,1:]],axis=2)[use]
                t=quads[:,[0,1,2,0,2,3]].reshape(-1,3)
                if side<0:t=t[:,::-1]
                st=np.stack([(y-ys[y0])/(ys[y1]-ys[y0]),1-(z-zs[z0])/(zs[z1]-zs[z0])],-1).reshape(-1,2)
                verts.append(q.reshape(-1,3)@b.T);faces.append(t+nextv);nextv+=y.size
                coords.append(st[t]);labels.append(np.full(len(t),page,'i4'));page+=1
                area+=use.sum()*(ys[1]-ys[0])*(zs[1]-zs[0])
    xyz=np.vstack(verts).astype('f4')
    return (np.vstack((v,xyz)),np.vstack([f[keep],*faces]).astype('i4'),
            np.concatenate([uv[keep],*coords]).astype('f4'),np.concatenate([pages[keep],*labels]),
            np.vstack((colors,np.full(xyz.shape,125,'u1'))),float(area))
