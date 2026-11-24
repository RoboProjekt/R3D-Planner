"""Measure held-out appearance and edge alignment in the final exported building GLB."""
import functools
import json
from pathlib import Path
import struct

import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from check_fine_mesh import scene,query,render
from compare_lyra_views import ssim

FINE=Path('.runtime/scan1123/fine'); WORK=Path('.runtime/scan1123/photomesh_hd')
OUT=Path('reports/20261124_fotomesh_hd'); OLD=Path('.runtime/scan1123/lyra_world')

class Model:
    def __init__(self,path):
        with path.open('rb') as stream:
            magic,ver,_=struct.unpack('<4sII',stream.read(12)); assert (magic,ver)==(b'glTF',2)
            length,_=struct.unpack('<II',stream.read(8)); self.doc=json.loads(stream.read(length))
            length,_=struct.unpack('<II',stream.read(8)); self.blob=stream.read(length)
        def acc(i):
            a=self.doc['accessors'][i]; view=self.doc['bufferViews'][a['bufferView']]
            width={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']]
            return np.frombuffer(self.blob,{5125:'<u4',5126:'<f4'}[a['componentType']],a['count']*width,
                         view['byteOffset']+a.get('byteOffset',0)).reshape(-1,width)
        pos=[];tri=[];tex=[];coords=[];color=[];offset=0
        for p in self.doc['meshes'][0]['primitives']:
            a=p['attributes'];v=acc(a['POSITION']);f=acc(p['indices']).reshape(-1,3);n=len(v)
            pos.append(np.column_stack([v[:,0],-v[:,2],v[:,1]]));tri.append((f+offset).astype('i4'));offset+=n
            if 'TEXCOORD_0' in a:
                uv=acc(a['TEXCOORD_0'])[f].copy();uv[:,:,1]=1-uv[:,:,1]
                idx=self.doc['materials'][p['material']]['pbrMetallicRoughness']['baseColorTexture']['index']
                page=self.doc['textures'][idx]['source'];c=np.zeros((n,3),'u1')
            else:
                uv=np.zeros((len(f),3,2),'f4');page=-1
                lin=acc(a['COLOR_0']);c=np.rint(255*np.where(lin<=.0031308,12.92*lin,1.055*lin**(1/2.4)-.055)).clip(0,255).astype('u1')
            tex.append(np.full(len(f),page,'i4'));coords.append(uv);color.append(c)
        self.f=np.concatenate(tri);self.scene=scene(np.concatenate(pos),self.f)
        self.uv=np.concatenate(coords);self.pages=np.concatenate(tex);self.colors=np.concatenate(color)
    @functools.lru_cache(maxsize=18)
    def __getitem__(self,page):
        v=self.doc['bufferViews'][self.doc['images'][page]['bufferView']]
        raw=np.frombuffer(self.blob,'u1',v['byteLength'],v['byteOffset'])
        return cv2.imdecode(raw,cv2.IMREAD_COLOR)[:,:,::-1]
    def frame(self,k,pose,override=None):
        hits=query(self.scene,k,pose,(640,480))
        return render(hits,self.f,self.colors,self.uv,self.pages,self if override is None else override)[0]

def scores(truth,im):
    def edge(a):
        a=cv2.GaussianBlur(cv2.cvtColor(a,cv2.COLOR_RGB2GRAY),(3,3),.65)
        return cv2.Canny(a,38,90,L2gradient=True)>0
    gt=edge(truth);out=edge(im)
    def match(a,b):
        dt=cv2.distanceTransform((~b).astype('u1'),cv2.DIST_L2,5)
        return float((dt[a]<=2.).mean()) if a.any() else 0.
    recall=match(gt,out);precision=match(out,gt)
    return dict(psnr_db=float(cv2.PSNR(truth,im)),ssim=ssim(truth,im),edge_recall=recall,edge_precision=precision,
                edge_f1=float(2*recall*precision/max(recall+precision,1e-8)))

def main():
    cv2.setNumThreads(1)
    h=np.load(FINE/'hold.npz');model=Model(OUT/'Gebaeude.glb');rows=[]
    pics=WORK/'check';pics.mkdir(exist_ok=True)
    for j,pose in enumerate(h['color_poses']):
        im=model.frame(h['color_k'],pose)
        Image.fromarray(im).save(pics/f'{j:03d}.png')
        truth=np.array(Image.open(FINE/'holdout'/f'{j:04}.jpg').convert('RGB'))
        row={'view':j}
        for label,img in [('photo_mesh',im),('lyra',np.array(Image.open(OLD/'held'/f'{j:03}.png'))),('previous_mesh',np.array(Image.open(OLD/'glb'/f'{j:03}.png')))]:
            row[label]=scores(truth,img)
        rows.append(row)
    means={name:{k:float(np.mean([r[name][k] for r in rows])) for k in rows[0][name]} for name in ('photo_mesh','previous_mesh','lyra')}
    info={'source':'fusion_scan_2026_11_23_16_30_00','pose_test':json.loads((WORK/'align.json').read_text()),'geometry':json.loads((WORK/'model.json').read_text()),'test':'53 RGB photos excluded from reconstruction; all methods rendered at the identical original measured camera poses. Edge precision and recall use a 2-pixel tolerance.','means':means,'views':rows}
    geom=np.load('.runtime/scan1123/architecture/scene.npz')
    x,y,z=(h['color_poses'][:,:3,3]@geom['b']).T
    l,r,_=geom['stair_bounds']
    masks={'treppe':(x>l-.45)&(x<r+.45)&(y>geom['steps'][0,0]-1.)&(y<geom['steps'][-1,0]+.5),
           'flur_1og':(x>-3.45)&(x<32.15)&(y>-9.4)&(y<-6.2)&(z>2.45)}
    info['regions']={}
    for region,mask in masks.items():
        ids=np.flatnonzero(mask).tolist()
        if ids:
            info['regions'][region]={'views':ids,'means':{name:{k:float(np.mean([rows[i][name][k] for i in ids])) for k in means[name]} for name in means}}
    (OUT/'Bildpruefung.json').write_text(json.dumps(info,indent=2)+'\n')
    print('METRICS',means,flush=True)
    draw_comparison(pics)

def draw_comparison(pics):
    font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
    gap=10;margin=14;w,h=480,360
    canvas=Image.new('RGB',(2*margin+3*w+2*gap,54+3*(h+30)), '#172029');d=ImageDraw.Draw(canvas)
    for n,name in enumerate(('Kameraaufnahme','Lyra-Flythrough','Fototexturiertes Dreiecksmodell')):
        d.text((margin+n*(w+gap),12),name,font=font(22),fill='white')
    for r,(i,label) in enumerate(((15,'Treppenfuß'),(18,'Podest'),(36,'Flur im 1. OG'))):
        y=49+r*(h+30);d.text((margin,y),label,font=font(16),fill='#ced9e2')
        for n,p in enumerate((FINE/'holdout'/f'{i:04}.jpg',OLD/'held'/f'{i:03}.png',pics/f'{i:03}.png')):
            canvas.paste(Image.open(p).resize((w,h),Image.Resampling.LANCZOS),(margin+n*(w+gap),y+23))
    canvas.save(OUT/'Treppe_Flur.jpg',quality=95,subsampling=0)
if __name__=='__main__':main()
