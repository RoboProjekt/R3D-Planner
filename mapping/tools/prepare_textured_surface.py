"""Reduce redundant TSDF triangles, retain fine edges, and support gaps with coarser measured surfaces."""
import argparse
import json
from pathlib import Path

import fast_simplification
from numba import njit
import numpy as np
import open3d as o3d


@njit
def roots(faces,n):
    par=np.arange(n,dtype=np.int32)
    def root(x):
        while par[x]!=x:
            par[x]=par[par[x]];x=par[x]
        return x
    for a,b,c in faces:
        ra=root(a);rb=root(b);rc=root(c);m=min(ra,rb,rc)
        par[ra]=m;par[rb]=m;par[rc]=m
    for i in range(n):par[i]=root(i)
    return par


def compact(v,f):
    used,ids=np.unique(f,return_inverse=True)
    return v[used],ids.reshape(-1,3).astype('i4')


def weld(v,f):
    keys=np.ascontiguousarray(np.rint(v*1e6).astype('i4')).view('V12').ravel()
    _,used,ids=np.unique(keys,return_index=True,return_inverse=True)
    faces=ids.astype('i4')[f];return v[used],faces[(faces[:,0]!=faces[:,1])&(faces[:,0]!=faces[:,2])&(faces[:,1]!=faces[:,2])]


def simplify_tiles(v,f):
    # Lock every cut-border vertex so adjacent independently simplified tiles still meet.
    key=np.empty(len(f),'i4')
    for s in range(0,len(f),200000):
        mid=v[f[s:s+200000]].mean(axis=1)
        x,y,z=np.floor(mid.T/3.2).astype('i4')+100
        key[s:s+len(x)]=x*40000+y*200+z
    order=key.argsort(kind='stable');stops=np.r_[0,1+np.flatnonzero(np.diff(key[order])),len(f)]
    verts=[];tris=[];offset=0
    for a,b in zip(stops,stops[1:]):
        vv,ff=compact(v,f[order[a:b]])
        if len(ff)>150:
            vv,ff=fast_simplification.simplify(vv,ff,target_count=max(80,int(.095*len(ff))),agg=6.5,preserve_border=True)
        verts.append(vv.astype('f4'));tris.append(ff.astype('i4')+offset);offset+=len(vv)
    return weld(np.concatenate(verts),np.concatenate(tris))


def thin_components(f,n):
    component=roots(f,n);labels=component[f[:,0]]
    counts=np.bincount(labels,minlength=n)
    return f[counts[labels]>=36]


def remove_stair_skin(v,f,architecture):
    # The measured step profile supplies sharp risers and treads through low-texture patches.
    b=architecture['b']; l,r,low=architecture['stair_bounds'];steps=architecture['steps']
    out=[]
    for s in range(0,len(f),100000):
        ff=f[s:s+100000];uvw=v[ff].mean(axis=1)@b;x,y,z=uvw.T
        index=np.searchsorted(steps[:,0],y,side='right')
        zs=np.r_[low,steps[:,1]]
        left=np.maximum(0,index-1);right=np.minimum(len(steps)-1,index)
        tread=abs(z-zs[index])<.095
        riser=np.zeros(len(ff),bool)
        for j in (left,right):
            riser|=(abs(y-steps[j,0])<.068)&(z>zs[j]-.055)&(z<zs[j+1]+.055)
        inside=(x>=l)&(x<=r)&(y>=steps[0,0]-.50)&(y<=steps[-1,0]+.55)
        out.append(ff[~(inside&(tread|riser))])
    return np.concatenate(out)


def supplement(v,f,other_v,other_f,dist):
    # Coarser reconstruction only supplies areas without a nearby fine surface.
    scene=o3d.t.geometry.RaycastingScene(nthreads=5)
    scene.add_triangles(o3d.core.Tensor(v.astype('f4',copy=False)),o3d.core.Tensor(f.astype('u4')))
    survivor=[]
    for s in range(0,len(other_f),85000):
        ff=other_f[s:s+85000];q=other_v[ff].mean(axis=1)
        nearest=scene.compute_distance(o3d.core.Tensor(q),nthreads=5).numpy()
        survivor.append(ff[nearest>dist])
    kept=np.concatenate(survivor)
    if not len(kept):return v,f,0
    vv,ff=compact(other_v,kept)
    # Snap close vertices on the exposed boundary to the denser measurements.
    for s in range(0,len(vv),70000):
        q=vv[s:s+70000]
        nearest=scene.compute_closest_points(o3d.core.Tensor(q),nthreads=5)['points'].numpy()
        ok=np.linalg.norm(q-nearest,axis=1)<dist*.85
        q[ok]=nearest[ok]
    return np.r_[v,vv],np.r_[f,ff+len(v)],len(ff)


def prepare(work, cached_fine=False):
    architecture=np.load('.runtime/isaac_building/building/scene.npz')
    if cached_fine:
        with np.load(work/'fine_qem.npz') as saved:
            v,f=saved['v'],saved['f']
    else:
        v=np.load(work/'vertices.npy',mmap_mode='r');f=np.load(work/'faces.npy',mmap_mode='r')
        f=thin_components(f,len(v));print('Connected triangles',len(f),flush=True)
        f=remove_stair_skin(v,f,architecture);v,f=simplify_tiles(v,f)
        if len(f)>2_850_000:
            v,f=fast_simplification.simplify(v,f,target_count=2_850_000,agg=6)
            v,f=v.astype('f4'),f.astype('i4')
        np.savez(work/'fine_qem.npz',v=v,f=f)
    print('Fine QEM surface',len(v),len(f),flush=True)
    n_fine=len(f);coarse_counts=[]
    for path,dist in [(work/'mesh_2cm/karte_mesh.ply',.035),(Path('reports/20261123_lidar_rgbd_mesh/karte_mesh.ply'),.065)]:
        mesh=o3d.io.read_triangle_mesh(str(path));vv=np.asarray(mesh.vertices).astype('f4')
        ff=remove_stair_skin(vv,np.asarray(mesh.triangles),architecture)
        v,f,added=supplement(v,f,vv,ff,dist);coarse_counts.append(added)
    # Close only previously modeled structural ground, wall or ceiling gaps.
    av,af,g=[architecture[k] for k in ('v','f','g')]
    base=o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(av),o3d.utility.Vector3iVector(af[np.isin(g,[0,1,3,4])]))
    base=base.subdivide_midpoint(1)
    v,f,structure=supplement(v,f,np.asarray(base.vertices).astype('f4'),np.asarray(base.triangles),.085)
    stair_v,stair_f=compact(av.astype('f4'),af[g==2]);v=np.r_[v,stair_v];f=np.r_[f,stair_f+len(v)-len(stair_v)]
    v,f=weld(v,f);v,f=compact(v,f)
    np.savez(work/'surface.npz',v=v,f=f)
    report=dict(fine_faces=n_fine,coarser_faces=coarse_counts,backing_faces=structure,stair_faces=len(stair_f),vertices=len(v),triangles=len(f))
    (work/'surface.json').write_text(json.dumps(report,indent=2))
    print('Hybrid',report,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('work',type=Path)
    p.add_argument('--cached-fine',action='store_true');a=p.parse_args();prepare(a.work,a.cached_fine)
