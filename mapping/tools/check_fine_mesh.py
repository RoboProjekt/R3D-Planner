"""Compare polygonal renders and measured depth from identical held-out building cameras."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import open3d as o3d
from PIL import Image, ImageDraw, ImageFont


def scene(v, f):
    obj = o3d.t.geometry.RaycastingScene(nthreads=5)
    obj.add_triangles(o3d.core.Tensor(v.astype('f4',copy=False)),o3d.core.Tensor(f.astype('u4')))
    return obj


def query(obj, k, c2w, size):
    rays = obj.create_rays_pinhole(o3d.core.Tensor(k), o3d.core.Tensor(np.linalg.inv(c2w)), *size)
    return obj.cast_rays(rays,nthreads=5)


def render(hits, f, colors, uv=None, labels=None, pages=None):
    z=hits['t_hit'].numpy()
    ok=np.isfinite(z)
    ids=hits['primitive_ids'].numpy()[ok]
    bary=hits['primitive_uvs'].numpy()[ok]
    bary=np.column_stack((1-bary.sum(1),bary))
    rgb=(colors[f[ids]]*bary[:,:,None]).sum(1)
    if labels is not None:
        for page in np.unique(labels[ids]):
            if page<0:continue
            select=labels[ids]==page
            st=(uv[ids[select]]*bary[select,:,None]).sum(1)
            img=pages[page]
            st[:,1]=1-st[:,1]
            pix=np.clip(st*img.shape[0]-.5,0,img.shape[0]-1.001)
            x,y=pix.astype(int).T
            dx,dy=(pix-np.floor(pix)).T
            rgb[select]=((1-dy)[:,None]*((1-dx)[:,None]*img[y,x]+dx[:,None]*img[y,x+1])
                         +dy[:,None]*((1-dx)[:,None]*img[y+1,x]+dx[:,None]*img[y+1,x+1]))
    out=np.full((*ok.shape,3),[35,36,39],'u1')
    out[ok]=np.rint(rgb).clip(0,255).astype('u1')
    return out,ok


def summarize(errs, denom):
    vals=np.concatenate(errs)
    return dict(coverage=len(vals)/denom,median_absolute_cm=float(np.median(abs(vals))*100),
                p90_absolute_cm=float(np.percentile(abs(vals),90)*100),
                in_front_by_over_20cm=float(np.mean(vals<-.20)),within_10cm=float(np.mean(abs(vals)<=.10)))


def image_comparison(rows, output):
    w,h=424,318
    names=['Originalaufnahme','Bisheriges 5-cm-Mesh','Neues Fotomesh']
    labels=['Treppe','Flur im 1. OG','Gegenrichtung']
    margin=16; gap=10
    canvas=Image.new('RGB',(2*margin+3*w+2*gap,54+len(rows)*(h+32)+margin),'#23262a')
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
    sub=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    for col,name in enumerate(names):draw.text((margin+col*(w+gap),12),name,font=font,fill='white')
    for r,imgs in enumerate(rows):
        y=53+r*(h+32)
        draw.text((margin,y),labels[r],font=sub,fill='#c9d5db')
        for c,img in enumerate(imgs):
            canvas.paste(Image.fromarray(img).resize((w,h), Image.Resampling.LANCZOS),(margin+c*(w+gap),y+24))
    canvas.save(output,quality=94,subsampling=0)


def check(work,output):
    cv2.setNumThreads(1)
    photos=Path('.runtime/isaac_building/photos')
    cache=np.load('.runtime/mesh_fusion/rgbd_1118.npz')
    depth=cache['depth_mm']
    cameras=np.load(photos/'cameras.npz')
    held=np.load(work/'cameras.npz')['held_ids']
    old=o3d.io.read_triangle_mesh('reports/20261123_lidar_rgbd_mesh/karte_mesh.ply')
    oldf=np.asarray(old.triangles);oldc=np.round(np.asarray(old.vertex_colors)*255).astype('u1')
    oldscene=scene(np.asarray(old.vertices),oldf)
    with np.load(work/'surface.npz') as s:v,f=s['v'],s['f']
    newscene=scene(v,f)
    colors=np.load(work/'fallback.npy')
    with np.load(work/'materials.npz') as mat:uv,labels=mat['uv'],mat['atlas']
    pages=[cv2.imread(str(work/'textures'/f'detail_{i:02d}.jpg'))[:,:,::-1] for i in range(labels.max()+1)]
    rgb_scores=[[],[]];errs=[[],[]];shared=[[],[]];valid_depth=0;comparison={}
    for fid in held:
        idx=int(np.searchsorted(cameras['ids'],fid))
        assert cameras['ids'][idx]==fid
        target=depth[fid].astype('f4')*.001
        good=(target>.35)&(target<4)
        valid_depth+=int(good.sum())
        depths=[query(obj,cameras['depth_k'],cameras['depth_poses'][idx],(320,240))['t_hit'].numpy() for obj in (oldscene,newscene)]
        common=good&np.isfinite(depths[0])&np.isfinite(depths[1])
        for i,z in enumerate(depths):
            mask=good&np.isfinite(z);errs[i].append(z[mask]-target[mask]);shared[i].append(z[common]-target[common])
        truth=cv2.imread(str(photos/f'{fid:04d}.jpg'))[:,:,::-1]
        rgbhits=[query(obj,cameras['color_k'],cameras['color_poses'][idx],(640,480)) for obj in (oldscene,newscene)]
        (old_im,ma),(new_im,mb)=render(rgbhits[0],oldf,oldc),render(rgbhits[1],f,colors,uv,labels,pages)
        rgbmask=ma&mb
        for i,im in enumerate((old_im,new_im)):
            delta=im[rgbmask].astype('f4')-truth[rgbmask]
            rgb_scores[i].append(dict(psnr=float(-10*np.log10(np.mean(delta**2)/255**2)),
                mae=float(abs(delta).mean()),common_fraction=float(rgbmask.mean())))
        if fid in (196,298,629):comparison[int(fid)]=[truth,old_im,new_im]
    metrics={'held_original_ids':held.tolist(),'depth_range_m':[.35,4.], 'valid_sensor_depth_pixels':valid_depth}
    for i,name in enumerate(('old_5cm','new_fine')):
        metrics[name]={'all_measured_rays':summarize(errs[i],valid_depth),'shared_measured_rays':summarize(shared[i],valid_depth),
            'rgb_mean_over_views':{key:float(np.mean([r[key] for r in rgb_scores[i]])) for key in rgb_scores[i][0]}}
    metrics['validation_scope']='Original sensor poses, same recording. Fine RGB-D keyframes with validation exclusion; coarser supports, LiDAR and prior reconstructions reuse the recording.'
    for key in ('surface','texture','tsdf'):
        metrics[key]=json.loads((work/(key+'.json')).read_text())
    (output/'Pruefung.json').write_text(json.dumps(metrics,indent=2)+'\n')
    image_comparison([comparison[i] for i in (196,298,629)],output/'Vergleich.jpg')
    print(json.dumps({k:metrics[k] for k in ('old_5cm','new_fine')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('work',type=Path);p.add_argument('output',type=Path)
    args=p.parse_args();check(args.work,args.output)
