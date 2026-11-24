"""Extract supported TSDF cells in tiles, welding their shared edges in the global grid."""
from itertools import product

import numpy as np
import mcubes


def store_blocks(volume, work):
    hashmap=volume.hashmap()
    active=hashmap.active_buf_indices().numpy()
    keys=hashmap.key_tensor().numpy()[active]
    np.save(work/'block_keys.npy',keys)
    values=np.lib.format.open_memmap(work/'block_samples.npy',mode='w+',dtype='f4',shape=(len(active),8,8,8))
    tsdf=volume.attribute('tsdf').numpy()[...,0];weights=volume.attribute('weight').numpy()[...,0]
    for s in range(0,len(active),4000):
        ix=active[s:s+4000]
        values[s:s+len(ix)]=np.where(weights[ix]>=2.,tsdf[ix],np.nan)
    values.flush()


def extract(work, voxel):
    blocks=np.load(work/'block_keys.npy');dist=np.load(work/'block_samples.npy',mmap_mode='r')
    # Dense lookup of block indices is small compared to the sparse voxel payload.
    lower=blocks.min(axis=0);upper=blocks.max(axis=0)
    lookup=np.full(tuple(upper-lower+2),-1,'i4')
    lookup[tuple((blocks-lower).T)]=np.arange(len(blocks),dtype='i4')
    block_tile=12; tiles=np.unique((blocks-lower)//block_tile,axis=0)
    offsets=np.array(list(product(range(block_tile+1),repeat=3)),dtype='i4')
    vertices=[];triangles=[];nverts=0
    for tile in tiles:
        start=tile*block_tile;ix=start+offsets
        valid=(ix<np.array(lookup.shape)).all(axis=1);buf=np.full(len(ix),-1,'i4')
        buf[valid]=lookup[tuple(ix[valid].T)];good=buf>=0
        if not good.any():continue
        side=(block_tile+1)*8
        vol=np.full((side,side,side),np.nan,dtype='f4')
        # Storage within each Open3D block is [z,y,x].
        tiled=vol.reshape(block_tile+1,8,block_tile+1,8,block_tile+1,8).transpose(0,2,4,1,3,5)
        x,y,z=offsets[good].T;tiled[z,y,x]=dist[buf[good]]
        side=block_tile*8+1;vol=vol[:side,:side,:side]
        finite=np.isfinite(vol)
        all_corners=np.ones((side-1,)*3,dtype=bool)
        for a,b,c in product((0,1),repeat=3):
            all_corners &= finite[a:a+side-1,b:b+side-1,c:c+side-1]
        if not all_corners.any():continue
        vs,fs=mcubes.marching_cubes(np.nan_to_num(vol,nan=1.),0.)
        if not len(fs):continue
        center=np.minimum(np.floor(vs[fs].mean(axis=1)).astype('i4'),side-2)
        fs=fs[all_corners[tuple(center.T)]]
        if not len(fs):continue
        used,remap=np.unique(fs,return_inverse=True)
        vertices.append(((vs[used,::-1]+(start+lower)*8)*voxel).astype('f4'))
        triangles.append(remap.reshape(-1,3).astype('i4')+nverts);nverts+=len(used)
    verts=np.concatenate(vertices);faces=np.concatenate(triangles)
    # An index maps only identical edge vertices (rounded at 1 micrometre) across adjacent tiles.
    keys=np.ascontiguousarray(np.rint(verts*1e6).astype('i4')).view('V12').ravel()
    _,use,remap=np.unique(keys,return_index=True,return_inverse=True)
    verts=verts[use];faces=remap.astype('i4')[faces]
    faces=faces[(faces[:,0]!=faces[:,1])&(faces[:,0]!=faces[:,2])&(faces[:,1]!=faces[:,2])]
    return verts,faces
