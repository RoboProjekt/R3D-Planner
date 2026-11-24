"""Fuse LiDAR, pose-refined RGB-D and multi-view-validated Lyra depths in one metric TSDF."""
import argparse
import json
import os
from pathlib import Path

import cv2
import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree

from mesh_hesai_map import fuse_lidar, integrate
from extract_sparse_surface import store_blocks, extract


def fuse(work, voxel):
    c=np.load(work/'cameras.npz');p=np.load(work/'poses.npz');raw=np.load(work/'depth.npy',mmap_mode='r')
    lyra=np.load(work/'lyra.npz');rgb_map=Path('reports/20261123_kamerakarte')
    run=Path('reports/20261123_erste_bodenbeobachtung')
    for root in (run,rgb_map):
        if json.loads((root/'metrics.json').read_text())['map_frame']!='building_level':
            raise ValueError('Map frame mismatch')
    xyz=o3d.t.io.read_point_cloud(str(rgb_map/'karte_rgb.pcd')).point.positions.numpy()
    v=o3d.t.geometry.VoxelBlockGrid(attr_names=['tsdf','weight'],attr_dtypes=[o3d.core.float32]*2,
         attr_channels=[(1,),(1,)],voxel_size=voxel,block_resolution=8,block_count=48000)
    trunc=.060/voxel
    n=fuse_lidar(v,run,cKDTree(xyz),xyz,size=144,trunc_voxels=trunc)
    print('LiDAR',n,'blocks',v.hashmap().size(),flush=True)
    k=o3d.core.Tensor(c['depth_k'],o3d.core.float64)
    filtered=0
    for i,(dm,pose) in enumerate(zip(raw,p['depth_poses'])):
        dm=dm.copy();median=cv2.medianBlur(dm,3)
        close=(dm>0)&(median>0)&(abs(dm.astype('i4')-median)<12)
        dm[close]=median[close]
        dm[(median>0)&(abs(dm.astype('i4')-median)>90+.025*dm)]=0
        filtered+=integrate(v,dm,k,pose,4.2,trunc)
    print('RGB-D',filtered,'blocks',v.hashmap().size(),flush=True)
    lk=o3d.core.Tensor(lyra['K'],o3d.core.float64);layers=0
    for dm,pose in zip(lyra['depth_mm'],lyra['poses']):
        layers+=integrate(v,dm,lk,pose,4.21,trunc)
    print('Lyra',layers,'extracting',v.hashmap().size(),flush=True)
    store_blocks(v,work);del v
    print('Extracting supported TSDF tiles',flush=True)
    xyz,faces=extract(work,voxel)
    if len(faces)==0 or not np.isfinite(xyz).all():raise ValueError('Invalid TSDF')
    np.save(work/'vertices.npy',xyz);np.save(work/'faces.npy',faces)
    (work/'tsdf.json').write_text(json.dumps(dict(lidar_scans=os.path.relpath(run/'outputs.npz',work),voxel_m=voxel,truncation_m=.060,lidar_views=n,depth_views=filtered,
            lyra_supported_views=layers,lyra_supported_pixels=int(np.count_nonzero(lyra['depth_mm'])),
            vertices=len(xyz),faces=len(faces)),indent=2))
    print('Surface',len(xyz),len(faces),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('work',type=Path)
    p.add_argument('--voxel',type=float,default=.0125);a=p.parse_args();fuse(a.work,a.voxel)
