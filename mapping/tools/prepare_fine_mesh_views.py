"""Export sharp synchronized RGB/depth keyframes and metric poses for a textured building mesh."""
import argparse
import json
from pathlib import Path
from contextlib import closing

import cv2
import numpy as np
from sensor_msgs.msg import Image
from scipy.spatial.transform import Rotation

from color_hesai_map import PoseTrack, calibration, frame_index, rgb_array, read_message
from prepare_l1_ab import open_bag


def prepare(work):
    cache=np.load('.runtime/mesh_fusion/rgbd_1118.npz')
    metadata=json.loads(Path(str(cache['color_report'])).read_text())
    original=np.load('.runtime/isaac_building/photos/cameras.npz')
    pilot=np.load('reports/20261123_lyra_detail/Kameraposen.npz')
    tests=np.unique(np.r_[pilot['source_frame_id'][5::10],
                  original['ids'][np.linspace(10,len(original['ids'])-12,15).astype(int)],
                  [629,648,674]])
    tests=tests[np.isin(tests,original['ids'])]
    held=cache['stamps'][tests]
    tr=np.load(Path(str(cache['run']))/'outputs.npz')['trajectory']
    track=PoseTrack(tr,tr[0,0]);bounds=(int(np.ceil(tr[0,0]*1e9)),int(np.floor(tr[-1,0]*1e9)))
    work.mkdir(exist_ok=True,parents=True);photos=work/'photos';photos.mkdir(exist_ok=True)
    cv2.setNumThreads(1)
    with closing(open_bag(Path(metadata['bag']))[0]) as db:
        topics=dict(db.execute('select name,id from topics'))
        prefix='/go2_unit_14082'
        cf,(w,h,k,distortion)=calibration(db,topics[prefix+'/color/camera_info'],bounds=bounds)
        df,(dw,dh,dk,_)=calibration(db,topics[prefix+'/depth/camera_info'],True,bounds)
        if distortion is not None:raise ValueError('Unexpected RGB distortion')
        photos_idx=frame_index(db,topics[prefix+'/color/image_raw'],*bounds)
        depths=frame_index(db,topics[prefix+'/depth/image_rect_raw'],*bounds)
        ds,rows=np.asarray(depths).T
        eligible={}
        for stamp,row in photos_idx:
            if np.min(abs(held-stamp))<85_000_000:continue
            j=np.searchsorted(ds,stamp).clip(0,len(ds)-1)
            if j and abs(ds[j-1]-stamp)<abs(ds[j]-stamp):j-=1
            if abs(ds[j]-stamp)>34_000_000 or np.min(abs(held-ds[j]))<65_000_000:continue
            eligible.setdefault((stamp-bounds[0])//105_000_000,[]).append((stamp,row,j))
        kept=[];depths_mm=[]; last=None
        for group in eligible.values():
            t=group[len(group)//2][0]
            pose=track.at(np.array([t*1e-9-tr[0,0]]))[0]
            if last is not None and t-last[0]<650_000_000:
                move=np.linalg.norm(pose[:3,3]-last[1][:3,3])
                angle=Rotation.from_matrix(last[1][:3,:3].T@pose[:3,:3]).magnitude()
                if move<.065 and angle<np.deg2rad(3):continue
            best=None
            for stamp,row,j in group:
                msg=read_message(db,row,Image)
                if msg.header.frame_id!=cf or (msg.width,msg.height)!=(w,h):raise ValueError('RGB frame mismatch')
                rgb=rgb_array(msg)
                score=float(cv2.Laplacian(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),cv2.CV_32F).var())
                rank=np.log1p(score)-.20*abs(stamp-ds[j])/34_000_000
                if best is None or rank>best[0]:best=(rank,stamp,j,score,rgb)
            _,stamp,j,score,rgb=best
            dm=read_message(db,int(rows[j]),Image)
            if dm.header.frame_id!=df or dm.encoding!='16UC1' or (dm.width,dm.height)!=(dw,dh):
                raise ValueError('Depth frame mismatch')
            depth=np.frombuffer(dm.data,dtype='>u2' if dm.is_bigendian else '<u2').reshape(dh,dm.step//2)[:,:dw].copy()
            if (depth>0).mean()<.04:continue
            if not cv2.imwrite(str(photos/f'{len(kept):04d}.jpg'),rgb[:,:,::-1],[cv2.IMWRITE_JPEG_QUALITY,97]):
                raise OSError('Image write failed')
            kept.append((stamp,ds[j],score));depths_mm.append(depth);last=(t,pose)
    stamps=np.array([i[0] for i in kept],dtype='i8');depth_stamps=np.array([i[1] for i in kept],dtype='i8')
    c2w=track.at(stamps*1e-9-tr[0,0])@metadata['lidar_from_color']
    d2w=track.at(depth_stamps*1e-9-tr[0,0])@metadata['lidar_from_depth']
    np.save(work/'depth.npy',np.stack(depths_mm))
    np.savez(work/'cameras.npz',stamps=stamps,depth_stamps=depth_stamps,color_poses=c2w,depth_poses=d2w,
             color_k=k,depth_k=dk,size=[w,h],sharpness=[i[2] for i in kept],held_ids=tests)
    print(f'{len(stamps)} training RGB-D views, {len(tests)} evaluation views',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('work',type=Path)
    prepare(p.parse_args().work)
