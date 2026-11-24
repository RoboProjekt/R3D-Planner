"""Bake real photographs onto continuous measured corridor and stair surfaces."""
from functools import lru_cache
import json
from pathlib import Path
import shutil

import cv2
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

from build_aligned_photomesh import FINE,WORK
from publish_fine_mesh import write_glb,write_isaac

BASE=WORK/'charts'; OUT=WORK/'planes'
A=np.load('.runtime/scan1123/architecture/scene.npz');B=A['b'].astype('f4')
STEPS=A['steps'];L,R,LOW=A['stair_bounds'];TOP=STEPS[-1,1]
CAM=np.load(FINE/'cameras.npz');POSE=np.load(WORK/'aligned.npz')['color_poses'].astype('f4')
K=CAM['color_k'].astype('f4'); SHARP=np.clip((CAM['sharpness']/65.)**.43,.40,1.7)
DEPTH=np.load(FINE/'rgb_depth.npy',mmap_mode='r');VISIBLE=np.load(WORK/'solid/render_depth.npy',mmap_mode='r')
@lru_cache(maxsize=90)
def photo(i):
    return cv2.imread(str(_PHOTO_DIR/f'{i:04}.jpg'))

_PHOTO_DIR=FINE/'photos'
_MASK_DIR=None

@lru_cache(maxsize=90)
def exclusion(i):
    return cv2.imread(str(_MASK_DIR/f'{i:04}.png'),cv2.IMREAD_GRAYSCALE)

def evidence(world,normal,i):
    q=(world-POSE[i,:3,3])@POSE[i,:3,:3];z=q[...,2]
    u=q[...,0]*K[0,0]/np.maximum(z,.1)+K[0,2];v=q[...,1]*K[1,1]/np.maximum(z,.1)+K[1,2]
    xy=np.stack([u,v],axis=-1).astype('f4');px=np.rint(xy*.5).astype(int)
    row=px[...,1].clip(0,239);col=px[...,0].clip(0,319)
    observed=DEPTH[i,row,col]*.001; vis=VISIBLE[i,row,col]*.001
    inside=(z>.19)&(z<14.)&(u>=1)&(u<638)&(v>=1)&(v<478)
    incidence=np.abs((world-POSE[i,:3,3])@normal)/np.maximum(.1,np.linalg.norm(world-POSE[i,:3,3],axis=-1))
    border=np.minimum.reduce([u/640.,(639.-u)/640.,v/480.,(479.-v)/480.])
    depth=np.maximum(z,.1)
    measured=np.where(observed>.3,.16+.84*np.exp(-abs(z-observed)/(.12+.028*depth)),.63)
    visibility=np.where(vis>.22,np.where(z>vis+.09+.025*depth,np.exp(-np.maximum(0,z-vis-.09-.025*depth)/(.16+.025*depth)),1.),.68)
    w=(inside*np.clip(border*8.,.025,1.)*np.maximum(incidence,.05)**.65*SHARP[i]*measured*visibility/(.45+.38*np.maximum(z,.1))).astype('f4')
    w[(observed>.3)&(z>observed+.48+.08*z)]=0.
    if _MASK_DIR is not None:
        blocked=exclusion(i)
        if blocked is None: raise FileNotFoundError(_MASK_DIR/f'{i:04}.png')
        w[blocked[np.rint(v).astype(int).clip(0,479),np.rint(u).astype(int).clip(0,639)]>0]=0
    return xy,w

def planar_image(surface,normal,nu,nv):
    axis_u=(np.arange(nu,dtype='f4')+.5)/nu;axis_v=(np.arange(nv,dtype='f4')+.5)/nv
    U,V=np.meshgrid(axis_u,axis_v);world=(surface(U,V)@B.T).astype('f4');normal=B@np.asarray(normal,'f4')
    coarse=world[::15,::15];mid=coarse.reshape(-1,3).mean(0);near=np.flatnonzero(np.linalg.norm(POSE[:,:3,3]-mid,axis=1)<16.)
    ranking=[]
    for i in near:
        _,w=evidence(coarse,normal,int(i))
        cov=float(np.mean(w>.028));val=float(np.mean(w))*(.22+.78*cov)
        if val>.0008:ranking.append((val,int(i)))
    ranking.sort(reverse=True)
    # Select a spatially diverse shortlist and retain a master image for sharp, uninterrupted features.
    ids=[]
    for _,i in ranking:
        if all(abs(i-j)>=2 for j in ids):ids.append(i)
        if len(ids)==18:break
    if not ids: return np.full((nv,nu,3),125,'u1')
    coarse2=world[::3,::3]; shape=(coarse2.shape[1],coarse2.shape[0])
    best=np.zeros(coarse2.shape[:2],'f4');master=np.zeros((*best.shape,3),'u1')
    for j,i in enumerate(ids):
        xy,w=evidence(coarse2,normal,i)
        val=w*(1. if j==0 else .35)
        sample=cv2.remap(photo(i),xy,None,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
        yes=val>best;master[yes]=sample[yes];best[yes]=val[yes]
    mg=cv2.cvtColor(master,cv2.COLOR_BGR2GRAY)
    xx,yy=np.meshgrid(np.arange(nu,dtype='f4'),np.arange(nv,dtype='f4'));grid=np.stack([xx,yy],-1)
    base=np.zeros((nv,nu,3),'f4');detail=np.zeros_like(base);xb=np.zeros((nv,nu),'f4');xd=np.zeros_like(xb)
    for j,i in enumerate(ids):
        xy,w=evidence(world,normal,i)
        im=cv2.remap(photo(i),xy,None,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
        if j and min(shape)>=16:
            sg=cv2.resize(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),shape,interpolation=cv2.INTER_AREA)
            ok=cv2.resize(w,shape)>.03
            flow=cv2.calcOpticalFlowFarneback(mg,np.where(ok,sg,mg).astype('u1'),None,.5,3,15,3,5,1.1,0)
            mag=np.linalg.norm(flow,axis=2)
            flow*=np.where(ok,np.clip(1-(mag-3.)/4.,0,1),0)[:,:,None]
            lookup=grid+cv2.resize(flow,(nu,nv))*3.
            im=cv2.remap(im,lookup,None,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
            w=cv2.remap(w,lookup,None,cv2.INTER_LINEAR)
        im=im.astype('f4'); low=cv2.GaussianBlur(im,(0,0),7.)
        wb=w**2
        # High spatial frequencies come predominantly from one sharp, well-supported camera.
        wd=(w*(1.55 if j==0 else 1.))**5
        base+=low*wb[:,:,None];detail+=(im-low)*wd[:,:,None];xb+=wb;xd+=wd
    output=base/np.maximum(xb[:,:,None],1e-10)+detail/np.maximum(xd[:,:,None],1.e-13)
    good=xb>.0001
    if not good.all() and good.any():
        nearest=ndimage.distance_transform_edt(~good,return_distances=False,return_indices=True)
        output[~good]=output[tuple(nearest[:,~good])]
    if not good.any():output[:]=124
    return np.rint(output).clip(0,255).astype('u1')

def main(postprocess=None):
    cv2.setNumThreads(1);OUT.mkdir(exist_ok=True);tex=OUT/'textures';tex.mkdir(exist_ok=True)
    for p in (BASE/'textures').glob('*.jpg'):
        target=tex/p.name
        if not target.exists():target.symlink_to(p.resolve())
    if not (OUT/'rail.npz').exists():(OUT/'rail.npz').symlink_to((FINE/'rail.npz').resolve())
    with open('.runtime/scan1123/mapped/measured.pcd','rb') as stream:
        while stream.readline()!=b'DATA binary\n':pass
        pos=np.fromfile(stream,'<f4').reshape(-1,3)@B
    x0=-3.45;x1=32.15;gx=np.arange(x0,x1+.15,.12);X,Y,Z=pos.T
    yl=np.zeros(len(gx));yr=yl.copy()
    for j,x in enumerate(gx):
        sl=(abs(X-x)<.25)&(Z>TOP+.08)&(Z<TOP+.93)
        for array,lo,hi in ((yl,-9.55,-8.85),(yr,-6.95,-6.12)):
            edges=np.arange(lo,hi+.024,.025)
            counts,_=np.histogram(Y[sl],edges)
            array[j]=edges[np.argmax(counts)]+.0125 if counts.max()>=3 else np.nan
    for array in (yl,yr):
        good=np.isfinite(array);array[:]=ndimage.median_filter(np.interp(gx,gx[good],array[good]),size=5)
    ceiling=float(np.median(A['v'][A['f'][A['g']==4],2]))
    side_masks=[]
    for side,array in enumerate((yl,yr)):
        match=(abs(Y-np.interp(X,gx,array))<.16)&(X>=x0)&(X<x1)&(Z>=TOP)&(Z<ceiling+.12)
        xi=((X[match]-x0)/.12).astype(int).clip(0,len(gx)-1);zi=((Z[match]-TOP)/.12).astype(int)
        bins=np.zeros((len(gx),int((ceiling-TOP)/.12)+2),'i4')
        np.add.at(bins,(xi,zi.clip(0,bins.shape[1]-1)),1)
        mask=ndimage.binary_closing(ndimage.gaussian_filter(bins.astype('f4'),.80)>.52,structure=np.ones((3,3)),border_value=0)
        mask[:,0]=mask[:,1];mask[:,-1]=mask[:,-2];side_masks.append(mask)
    def side_ok(x,z,side):
        mask=side_masks[side]
        return mask[np.floor((x-x0)/.12).astype(int).clip(0,len(gx)-1),np.floor((z-TOP)/.12).astype(int).clip(0,mask.shape[1]-1)]
    g=np.load(WORK/'solid/surface.npz');v=g['v'];f=g['f']
    old=np.load(BASE/'materials.npz');col=np.load(BASE/'rgb.npy');loc=v[f].mean(1)@B;x,y,z=loc.T
    ly=np.interp(x,gx,yl);ry=np.interp(x,gx,yr); longitudinal=(x>=x0)&(x<=x1)
    cross=(y>=ly-.045)&(y<=ry+.045)
    near_floor=abs(z-TOP)<.28;near_ceil=abs(z-ceiling)<.15
    remove=longitudinal&cross&(near_floor|near_ceil)
    for side,dist in enumerate((y-ly,ry-y)):
        remove|=longitudinal&(dist>-.13)&(dist<.25)&(z>=TOP-.045)&(z<=ceiling+.045)&side_ok(x,z,side)
    which=np.searchsorted(STEPS[:,0],y+.0005,side='right')-1
    height=np.r_[LOW,STEPS[:,1]][which+1]
    remove|=(x>=L-.002)&(x<=R+.002)&(y>=STEPS[0,0]-.39)&(y<STEPS[-1,0]+.301)&(abs(z-height)<.21)
    V=[v];F=[f[~remove]];UV=[old['uv'][~remove]];P=[old['atlas'][~remove]];colors=[col]
    n=len(v);page=int(old['atlas'].max());edge=2048;px=py=rowh=0;sheet=None;pad=5;tiles=0
    def add(surface,normal,usize,vsize,density,maskfun=None):
        nonlocal n,page,px,py,rowh,sheet,tiles
        nu=max(14,round(usize*density));nv=max(14,round(vsize*density))
        parts=OUT/'plane_tiles';parts.mkdir(exist_ok=True)
        tile_path=parts/f'{tiles:03}.png'
        if tile_path.exists():
            pic=cv2.imread(str(tile_path))
        else:
            pic=planar_image(surface,normal,nu,nv)
            if not cv2.imwrite(str(tile_path),pic):raise OSError(tile_path)
        if tiles%12==0:print('TILE',tiles,nu,nv,flush=True)
        if px+nu+2*pad>edge:px=0;py+=rowh;rowh=0
        if sheet is None or py+nv+2*pad>edge:
            if sheet is not None:cv2.imwrite(str(tex/f'detail_{page:02}.jpg'),sheet,[cv2.IMWRITE_JPEG_QUALITY,97])
            page+=1;sheet=np.zeros((edge,edge,3),'u1');px=py=rowh=0
        sheet[py:py+nv+2*pad,px:px+nu+2*pad]=cv2.copyMakeBorder(pic,pad,pad,pad,pad,cv2.BORDER_REPLICATE)
        U,VV=np.meshgrid(np.linspace(0,1,max(2,int(np.ceil(usize/.12))+1)),np.linspace(0,1,max(2,int(np.ceil(vsize/.12))+1)))
        q=surface(U,VV);ix=np.arange(U.size).reshape(U.shape)
        tri=np.concatenate([np.stack([ix[:-1,:-1],ix[:-1,1:],ix[1:,1:]],-1).reshape(-1,3),
                            np.stack([ix[:-1,:-1],ix[1:,1:],ix[1:,:-1]],-1).reshape(-1,3)])
        q=q.reshape(-1,3)
        if maskfun is not None:tri=tri[maskfun(q[tri].mean(1))]
        if len(tri):
            crossn=np.cross(q[tri[0,1]]-q[tri[0,0]],q[tri[0,2]]-q[tri[0,0]])
            if np.dot(crossn,normal)<0:tri=tri[:,::-1]
            V.append((q@B.T).astype('f4'));F.append((tri+n).astype('i4'));colors.append(np.full((len(q),3),125,'u1'));n+=len(q)
            uv=np.stack([(px+pad+U*nu)/edge,1-(py+pad+VV*nv)/edge],axis=-1).reshape(-1,2)
            UV.append(uv[tri].astype('f4'));P.append(np.full(len(tri),page,'i4'))
        px+=nu+2*pad;rowh=max(rowh,nv+2*pad);tiles+=1
    for left,right in zip(np.linspace(x0,x1,13)[:-1],np.linspace(x0,x1,13)[1:]):
        for kind in ('floor','ceiling','left','right'):
            def surf(u,v,kind=kind):
                x=left+u*(right-left); l=np.interp(x,gx,yl);r=np.interp(x,gx,yr)
                if kind in ('left','right'):y=l if kind=='left' else r;z=TOP+v*(ceiling-TOP)
                else:y=l+v*(r-l);z=np.full_like(x,TOP if kind=='floor' else ceiling)
                return np.stack((x,y,z),axis=-1)
            floor=kind in ('floor','ceiling');side=int(kind=='right')
            norm=([0,0,1] if kind=='floor' else [0,0,-1]) if floor else ([0,1,0] if side==0 else [0,-1,0])
            add(surf,norm,right-left,2.8 if floor else ceiling-TOP,230,None if floor else lambda q:side_ok(q[:,0],q[:,2],side))
    for j,(y,z) in enumerate(STEPS):
        end=STEPS[j+1,0] if j<len(STEPS)-1 else y+.30
        low=STEPS[j-1,1] if j else LOW
        add(lambda u,v:np.stack([L+(R-L)*u,y+v*(end-y),np.full_like(u,z)],-1),[0,0,1],R-L,end-y,530)
        add(lambda u,v:np.stack([L+(R-L)*u,np.full_like(u,y),low+v*(z-low)],-1),[0,-1,0],R-L,z-low,530)
    y=STEPS[0,0]
    add(lambda u,v:np.stack([L+(R-L)*u,y-.38+v*.38,np.full_like(u,LOW)],-1),[0,0,1],R-L,.38,400)
    cv2.imwrite(str(tex/f'detail_{page:02}.jpg'),sheet,[cv2.IMWRITE_JPEG_QUALITY,97])
    vv=np.concatenate(V);ff=np.concatenate(F);uv=np.concatenate(UV);at=np.concatenate(P);cols=np.concatenate(colors)
    stats=dict(triangles=len(ff),photo_textured_faces=int((at>=0).sum()),atlas_pages=len(np.unique(at[at>=0])),planar_photo_tiles=tiles,plane_texels_per_m={'corridor':230,'stairs':530},source_resolution=[640,480])
    (OUT/'stats.json').write_text(json.dumps(stats,indent=2));print('PLANES',stats,flush=True)
    collision=Path('.runtime/scan1123/architecture/final_collision.npz')
    if postprocess is not None:
        vv,ff,uv,at,cols,collision=postprocess(vv,ff,uv,at,cols)
    args=(OUT,OUT,vv,ff,uv,at,cols);write_glb(*args);write_isaac(*args,collision)
if __name__=='__main__':main()
