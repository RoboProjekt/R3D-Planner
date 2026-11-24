"""Prepare clean photo atlases and depth-supported 3D foreground from people masks."""
from pathlib import Path
import json
import os

import cv2
import numpy as np
from scipy.spatial import cKDTree
from texture_isaac_scan import project, pack

ROOT = Path(os.environ.get('R3D_SCAN_ROOT', '.runtime/scan1123'))
FINE = ROOT / 'fine'
HD = ROOT / 'photomesh_hd'
JOB = ROOT / 'clean_building'


def masks_and_depth():
    cfg = np.load(FINE/'cameras.npz')
    k = cfg['color_k']
    poses = np.load(HD/'aligned.npz')['color_poses']
    depth = np.load(FINE/'rgb_depth.npy', mmap_mode='r')
    masks = JOB/'exclusion'
    photos = JOB/'photos'
    for dest in masks, photos:
        dest.mkdir(exist_ok=True)
    grays, originals = [], []
    paths = sorted((FINE/'photos').glob('*.jpg'))
    for p in paths:
        grays.append(cv2.resize(cv2.imread(str(p),0),(320,240)))
        raw = cv2.imread(str(JOB/'masks'/p.with_suffix('.png').name),0)
        if raw is None: raise FileNotFoundError(p.stem)
        originals.append(raw)
    points = []
    totals = []
    for i,path in enumerate(paths):
        mask = originals[i].copy()
        # A shoe was visible at the left image boundary before the torso entered.
        if 69 <= i <= 75:
            mask[345:425,:71]=255
        for j in (i-1,i+1):
            if j<0 or j>=len(paths) or cfg['segment'][j]!=cfg['segment'][i] or not originals[j].any():
                continue
            delta = np.linalg.norm(poses[i,:3,3]-poses[j,:3,3])
            angle = np.trace(poses[i,:3,:3].T@poses[j,:3,:3])
            if delta>.25 or angle < 2.88: continue
            flow=cv2.calcOpticalFlowFarneback(grays[i],grays[j],None,.5,3,19,3,5,1.2,0)
            yy,xx=np.indices(mask.shape,dtype='f4')
            uv=np.stack([xx,yy],axis=2)+2*cv2.resize(flow,(640,480))
            mask |= cv2.remap(originals[j],uv,None,cv2.INTER_NEAREST)
        blocked = cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(19,19)))
        cv2.imwrite(str(masks/(path.stem+'.png')),blocked)
        dest=photos/path.name
        if blocked.any():
            im=cv2.imread(str(path))
            # Sanitize even unused pixels inside the crops stored in the portable asset.
            clean=cv2.inpaint(im,blocked,5,cv2.INPAINT_TELEA)
            cv2.imwrite(str(dest),clean,[cv2.IMWRITE_JPEG_QUALITY,97])
        elif not dest.exists():
            dest.symlink_to(path.resolve())
        totals.append(int(np.count_nonzero(blocked)))
        interior=cv2.erode(originals[i],np.ones((7,7),'u1'))[::2,::2]>0
        dm=depth[i]*.001
        select=interior & (dm>.24) & (dm<9.)
        y,x=np.where(select);x=x[::3];y=y[::3];z=dm[y,x]
        p=np.column_stack([(2*x-k[0,2])*z/k[0,0],(2*y-k[1,2])*z/k[1,1],z])@poses[i,:3,:3].T+poses[i,:3,3]
        if len(p):
            cells=np.unique(np.floor(p/.055).astype('i4'),axis=0)
            points.append(cells)
    all_cells=np.concatenate(points)
    cells,count=np.unique(all_cells,axis=0,return_counts=True)
    body=(cells[count>=2]+.5)*.055
    np.save(JOB/'body.npy',body.astype('f4'))
    summary=dict(frames=len(paths),detected_frames=sum(bool(np.any(m)) for m in originals),
                 excluded_frames=sum(a>0 for a in totals),supported_body_voxels=len(body))
    print('MASKS', summary,flush=True)
    return summary


def clean_chart():
    source=HD/'charts'
    dest=JOB/'charts'
    dest.mkdir(exist_ok=True)
    cfg=np.load(FINE/'cameras.npz');k=cfg['color_k'];poses=np.load(HD/'aligned.npz')['color_poses']
    geom=np.load(HD/'solid/surface.npz');v,f=geom['v'],geom['f']
    lab=np.load(source/'materials.npz')['labels'].copy()
    original=lab.copy()
    # A bounding rectangle conservatively covers all three triangle edges, including
    # the interior of large triangles to which a silhouette can otherwise be baked.
    def overlaps(i, ids, integral):
        xy,_=project(v[f[ids]],poses[i],k)
        lo=np.floor(xy.min(1)).astype(int).clip([0,0],[639,479])
        hi=(np.ceil(xy.max(1)).astype(int)+1).clip([1,1],[640,480])
        x,y=lo.T;u,w=hi.T
        return (integral[w,u]-integral[w,x]-integral[y,u]+integral[y,x])>0
    integrals={}
    for i in range(len(poses)):
        mask=cv2.imread(str(JOB/'exclusion'/f'{i:04}.png'),0)
        if mask.any():
            integ=cv2.integral((mask>0).astype('u1'))
            integrals[i]=integ
            ids=np.flatnonzero(lab==i); lab[ids[overlaps(i,ids,integ)]]=-1
    damaged=(original>=0)&(lab==-1)
    best=np.zeros(len(f),'f4')
    for i in range(len(poses)):
        view=np.load(source/'views'/f'{i:04}.npz');ids=view['ids']
        use=damaged[ids];score=view['score'][use];ids=ids[use]
        if len(ids)==0:continue
        clear=score>best[ids]
        if i in integrals:clear &= ~overlaps(i,ids,integrals[i])
        ids=ids[clear];lab[ids]=i;best[ids]=score[clear]
    uv,at,_=pack(v,f,lab,np.arange(len(poses)),poses,k,JOB/'photos',dest/'textures')
    np.savez(dest/'materials.npz',uv=uv,atlas=at,labels=lab)
    # Also replace vertex colours at problematic surfaces with unaffected nearby colours.
    colors=np.load(source/'rgb.npy')
    affected=np.unique(f[damaged])
    body=cKDTree(np.load(JOB/'body.npy'))
    near=body.query(v,workers=5,distance_upper_bound=.20)[0]<.20
    plausible=np.ones(len(v),bool);plausible[affected]=False;plausible &=~near
    replace=~plausible
    if replace.any():
        clean=np.flatnonzero(plausible)
        tree=cKDTree(v[clean])
        for ids in np.array_split(np.flatnonzero(replace),15):
            nbr=tree.query(v[ids],k=7,workers=5)[1]
            colors[ids]=np.median(colors[clean[nbr]],axis=1)
    np.save(dest/'rgb.npy',colors)
    stats={'faces_excluding_masked_source':int(damaged.sum()),'reassigned_to_clean_view':int((damaged & (lab>=0)).sum())}
    print('CHARTS',stats,flush=True)
    return stats


if __name__=='__main__':
    cv2.setNumThreads(1)
    report={**masks_and_depth(), **clean_chart()}
    (JOB/'photos.json').write_text(json.dumps(report,indent=2))
