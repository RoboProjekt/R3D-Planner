"""Verify the final GLB against original test poses, measured depth, and door clearance."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import open3d as o3d
from PIL import Image,ImageDraw,ImageFont
from build_building_contours import ROOT,OUT,FINE
from check_building_photos import Model
from check_fine_mesh import query


def assess(geometry,cams,samples):
    k=cams['depth_k'].copy();shape=samples.shape[1:][::-1]
    counts=[];errors=[]
    for pose,dm in zip(cams['depth_poses'],samples):
        z=query(geometry,k,pose,shape)['t_hit'].numpy()
        depth=dm.astype('f4')*.001;valid=(depth>.28)&(depth<5.8)
        hit=np.isfinite(z)&valid
        counts.append([int(valid.sum()),int(hit.sum()),int((abs(z[hit]-depth[hit])<.15).sum())])
        errors.extend(abs(z[hit]-depth[hit])[::20])
    total,hit,close=np.sum(counts,axis=0)
    return dict(valid_depth_rays=int(total),rays_hitting_mesh=int(hit),hit_fraction=float(hit/total),
                within_15cm_fraction=float(close/total),median_error_on_hits_m=float(np.median(errors)))


def check(out,previous):
    cv2.setNumThreads(1)
    data=np.load(FINE/'hold.npz');dm=np.load(FINE/'hold_depth.npy',mmap_mode='r')
    before=Model(previous)
    initial=assess(before.scene,data,dm);del before
    model=Model(out/'Gebaeude.glb');validation=assess(model.scene,data,dm)
    stats=json.loads((OUT/'geometry.json').read_text())
    if stats['open_architectural_boundary_edges'] or stats['nonmanifold_edges']:
        raise ValueError('The exported architectural sheets must form closed solids')
    # Check actual glTF surfaces on both sides of the measured distinction between
    # a recessed leaf and an open doorway. The offset origin is 30 cm inside the hall.
    a=np.load(ROOT/'architecture/scene.npz');b=a['b'];floor=a['steps'][-1,1]
    probes=[]
    for info in stats['door_and_passage_measurements']:
        if 'wall_y' not in info:continue
        y=info['wall_y'];x=(info['start_x']+info['end_x'])/2
        side=1 if y>-8 else -1
        origins=np.array([[x+du,y-side*.3,floor+h] for du in (-.22,0,.22) for h in (.22,.8,1.32,1.75)])
        dirs=np.tile([0,side,0],(len(origins),1))
        hits=model.scene.cast_rays(o3d.core.Tensor(np.c_[origins@b.T,dirs@b.T].astype('f4')))['t_hit'].numpy()
        if info['kind']=='measured_opening':
            passed=bool((hits>.62).all())
        else:
            passed=bool((abs(hits-.3-info['depth'])<.05).all())
        if not passed:raise AssertionError((info,hits))
        probes.append(dict(kind=info['kind'],number=len(origins),passed=passed))
    report=dict(geometry=stats,old_mesh_depth_test=initial,new_mesh_depth_test=validation,
                held_out_poses=len(dm),door_clearance_checks=probes)
    thumb=Image.new('RGB',(1080,3*434),'#25262a');draw=ImageDraw.Draw(thumb)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    for n,(i,title) in enumerate([(7,'Eingang im Erdgeschoss'),(15,'Treppenfuß'),(19,'Treppenlauf und Geländer'),(23,'Aufzug am Podest'),(36,'Flur im 1. OG'),(39,'Tür und Flurende')]):
        im=Image.fromarray(model.frame(data['color_k'],data['color_poses'][i]))
        x=(n%2)*540;y=(n//2)*434;thumb.paste(im.resize((540,405),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+7,y+407),title,fill='white',font=font)
    thumb.save(out/'Ansichten.jpg',quality=95,subsampling=0)
    (out/'Geometriepruefung.json').write_text(json.dumps(report,indent=2))
    print('DEPTH',initial,validation,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('output',type=Path)
    parser.add_argument('--previous',type=Path,required=True);args=parser.parse_args()
    check(args.output,args.previous)
