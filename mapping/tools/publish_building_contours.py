"""Mesh, texture and validate the architectural contour reconstruction."""
import functools
import hashlib
import json
from pathlib import Path
import shutil

import cv2
import numpy as np
import open3d as o3d
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from build_building_contours import OUT, prepare, FINE, ROOT, JOB
from check_fine_mesh import scene, query
from publish_fine_mesh import write_glb, write_isaac


def anchor_components(parts,trajectory):
    points=[];owners=[];roots=[];entries=[]
    route=cKDTree(trajectory[:,:2])
    for part in parts:
        lab,n=ndimage.label(part.mask)
        center=(part.grid[:-1,:-1]+part.grid[1:,1:])*.5
        for idx in range(1,n+1):
            select=lab==idx
            q=center[select]
            if not len(q):continue
            patch=len(entries);entries.append((part,select))
            corners=np.zeros(part.grid.shape[:2],bool)
            for a,b in ((0,0),(0,1),(1,0),(1,1)):
                corners[a:a+select.shape[0],b:b+select.shape[1]]|=select
            coords=part.grid[corners]
            points.append(coords);owners.append(np.full(len(coords),patch,'i4'))
            if part.name in ('Boden_EG','Boden_1OG','Treppe') and np.min(route.query(q[:,:2],workers=4)[0])<1.1:
                roots.append(patch)
    coords=np.concatenate(points);owners=np.concatenate(owners)
    tree=cKDTree(coords);pairs=tree.query_pairs(.165,output_type='ndarray')
    edges=np.unique(np.sort(owners[pairs],axis=1),axis=0)
    n,cls=connected_components(coo_matrix((np.ones(len(edges)),edges.T),shape=(len(entries),len(entries))),directed=False)
    connected=np.isin(cls,cls[roots]);removed=0
    for ok,(part,mask) in zip(connected,entries):
        if not ok:part.mask[mask]=False;removed+=1
    return {'unattached_surface_components_dropped':int(removed),'kept_components_connected_to_route_structure':int(connected.sum()),'structural_attachment_tolerance_m':.165}


def collect(parts,b,columns=(),rail_file=None):
    vs=[];fs=[];groups=[];tile_ids=[];uvs=[];colors=[]
    tiles=[];count=0;open_edges=0;nonmanifold=0
    defaults=[[127,127,122],[143,143,136],[138,136,131],[166,167,162],[189,188,182],[127,132,131]]
    for part in parts:
        if not part.mask.any():continue
        grid=part.grid
        world=(grid@b.T).astype('f4')
        n=part.normal@b.T;n=n/np.linalg.norm(n)
        if part.name=='Treppe':n=np.array([0,0,1.])-.24*b[:,1];n=n/np.linalg.norm(n)
        index=np.arange(np.prod(grid.shape[:2])).reshape(grid.shape[:2])
        raw=world.reshape(-1,3);V=len(raw)
        xlen=np.linalg.norm(np.diff(grid,axis=0),axis=2).mean(1)
        ylen=np.linalg.norm(np.diff(grid,axis=1),axis=2).mean(0)
        sx=max(1,round(2.28/max(.02,np.median(xlen))));sy=max(1,round(2.28/max(.02,np.median(ylen))))
        front=[];labels=[];coords=[]
        for i in range(0,len(xlen),sx):
            i1=min(len(xlen),i+sx)
            for j in range(0,len(ylen),sy):
                j1=min(len(ylen),j+sy);sel=part.mask[i:i1,j:j1]
                if not sel.any():continue
                sub=index[i:i1+1,j:j1+1]
                quads=np.stack([sub[:-1,:-1],sub[1:,:-1],sub[1:,1:],sub[:-1,1:]],-1)[sel]
                T=quads[:,[0,1,2,0,2,3]].reshape(-1,3)
                normals=np.cross(raw[T[:,1]]-raw[T[:,0]],raw[T[:,2]]-raw[T[:,0]])
                flip=normals@n<0;T[flip]=T[flip,::-1]
                m,h=sub.shape
                x,y=np.unravel_index(T,index.shape)
                xy=np.stack([(x-i)/(m-1),(y-j)/(h-1)],-1)
                tile=len(tiles);texels=300 if part.group==2 else (175 if part.group in (1,3,5) else 115)
                width=max(15,round(xlen[i:i1].sum()*texels));height=max(15,round(ylen[j:j1].sum()*texels))
                tiles.append((world[i:i1+1,j:j1+1].copy(),width,height,part.group,part.name))
                front.append(T);coords.append(xy.astype('f4'));labels.append(np.full(len(T),tile,'i4'))
        t=np.concatenate(front);uv=np.concatenate(coords);at=np.concatenate(labels)
        # At a diagonal contact two disconnected face fans have the same point.
        # Give each fan its own index before closing the boundary at that point.
        m=part.mask
        checker=(m[:-1,:-1]==m[1:,1:])&(m[:-1,1:]==m[1:,:-1])&(m[:-1,:-1]!=m[:-1,1:])
        original_t=t.copy()
        for ii,jj in zip(*np.where(checker)):
            ii+=1;jj+=1;vertex=index[ii,jj]
            on=np.flatnonzero((original_t==vertex).any(1));rr,_=np.unravel_index(original_t[on],index.shape)
            fan=on[rr.mean(1)>ii]
            if len(fan):
                t[fan]=np.where(t[fan]==vertex,len(raw),t[fan])
                raw=np.vstack([raw,raw[vertex]])
        V=len(raw)
        # Build closed solids. Each boundary gets a side face and a back face.
        # Chamfering a diagonal-only grid contact into separate sheets prevents
        # unrelated surfaces from joining at one point.
        e=t[:,[0,1,1,2,2,0]].reshape(-1,2)
        _,idx,counts=np.unique(np.sort(e,axis=1),axis=0,return_index=True,return_counts=True)
        a,c=e[idx[counts==1]].T
        side=np.vstack([np.c_[c,a,a+V],np.c_[c,a+V,c+V]])
        faces=np.vstack([t,t[:,::-1]+V,side])
        ge=faces[:,[0,1,1,2,2,0]].reshape(-1,2)
        _,uses=np.unique(np.sort(ge,axis=1),axis=0,return_counts=True)
        open_edges+=int((uses==1).sum());nonmanifold+=int((uses>2).sum())
        vs.append(np.vstack([raw,raw-part.thickness*n]).astype('f4'));fs.append(faces+count);count+=2*V
        groups.append(np.full(len(faces),part.group,'i4'))
        tile_ids.append(np.r_[at,at,np.full(len(side),-1,'i4')])
        uvs.append(np.concatenate([uv,uv[:,::-1],np.zeros((len(side),3,2),'f4')]))
        colors.append(np.tile(defaults[part.group],(2*V,1)))
    if open_edges:raise ValueError(f'{open_edges} unsealed architectural edges')
    from repair_floors_and_pillars import add_column_geometry
    count=add_column_geometry(columns,b,vs,fs,groups,tile_ids,uvs,colors,tiles,count)
    rail=np.load(rail_file or FINE/'rail.npz')
    vs.append(rail['v']);fs.append(rail['f']+count);groups.append(np.full(len(rail['f']),6,'i4'))
    tile_ids.append(np.full(len(rail['f']),-1,'i4'));uvs.append(np.zeros((len(rail['f']),3,2),'f4'));colors.append(rail['color'])
    return (np.vstack(vs),np.vstack(fs).astype('i4'),np.concatenate(groups),np.concatenate(tile_ids),
            np.concatenate(uvs),np.vstack(colors).astype('u1'),tiles,{'open_architectural_boundary_edges':open_edges,'nonmanifold_edges':nonmanifold})


class PhotoBaker:
    def __init__(self,mesh):
        self.k=np.load(FINE/'cameras.npz')['color_k'].astype('f4')
        self.poses=np.load(ROOT/'photomesh_hd/aligned.npz')['color_poses'].astype('f4')
        self.depth=np.load(FINE/'rgb_depth.npy',mmap_mode='r')
        self.sharp=np.clip((np.load(FINE/'cameras.npz')['sharpness']/65.)**.5,.42,1.6)
        self.masks=np.stack([cv2.resize(cv2.imread(str(JOB/'exclusion'/f'{i:04}.png'),0),(320,240),interpolation=cv2.INTER_AREA)>0 for i in range(len(self.poses))])
        k=self.k.copy();k[:2]/=4
        self.visible=np.zeros((len(self.poses),120,160),'u2')
        for i,p in enumerate(self.poses):
            hit=query(mesh,k,p,(160,120))['t_hit'].numpy()
            self.visible[i]=np.where(np.isfinite(hit),np.minimum(hit*1000,65000),0).astype('u2')

    @functools.lru_cache(maxsize=100)
    def image(self,i):
        return cv2.imread(str(JOB/'photos'/f'{i:04}.jpg'))

    def evidence(self,xyz,n,i,glass):
        p=self.poses[i];q=(xyz-p[:3,3])@p[:3,:3];z=q[:,:,2]
        u=q[:,:,0]*self.k[0,0]/np.maximum(.10,z)+self.k[0,2];w=q[:,:,1]*self.k[1,1]/np.maximum(.10,z)+self.k[1,2]
        row=np.rint(w*.5).astype(int).clip(0,239);col=np.rint(u*.5).astype(int).clip(0,319)
        dm=self.depth[i,row,col]*.001;scene_z=self.visible[i,row//2,col//2]*.001
        margin=np.minimum.reduce([u/640,(639-u)/640,w/480,(479-w)/480])
        d=xyz-p[:3,3];length=np.linalg.norm(d,axis=2)
        angle=abs((d*n).sum(2))/np.maximum(.1,length)
        weight=np.clip(margin*12,0,1)*np.maximum(angle,.035)**.72*self.sharp[i]/(.45+.30*length)
        dz=z-dm
        if glass:dz=np.maximum(dz,0)
        agreement=np.where(dm>.20,np.exp(-abs(dz)/(.13+.030*np.maximum(.1,z))),.46)
        # A closer return hides a surface even when its source image is sharp.
        ok=(z>.18)&(z<16)&(margin>.003)&~self.masks[i,row,col]
        ok &= (scene_z<.1)|(z<scene_z+.20+.02*z)
        ok &= (dm<.20)|(dz<.32+.047*z)
        return np.stack([u,w],-1).astype('f4'),(ok*weight*agreement).astype('f4')

    def bake(self,tile):
        grid,width,height,group,name=tile;glass=name=='Flurwand_Fenster' or name.startswith('Glas_')
        def positions(w,h):
            x,y=np.meshgrid((np.arange(w,dtype='f4')+.5)*(grid.shape[0]-1)/w,(np.arange(h,dtype='f4')+.5)*(grid.shape[1]-1)/h)
            return cv2.remap(grid,y,x,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
        coarse=positions(max(5,width//12),max(5,height//12));mid=coarse.mean((0,1))
        n=np.cross(grid[-1,0]-grid[0,0],grid[0,-1]-grid[0,0]);n=n/max(np.linalg.norm(n),1.e-7)
        ids=np.flatnonzero(np.linalg.norm(self.poses[:,:3,3]-mid,axis=1)<16.)
        scores=[]
        for i in ids:
            _,w=self.evidence(coarse,n,int(i),glass);s=float(w.mean())*(.22+.78*float((w>.025).mean()))
            if s>.00045:scores.append((s,int(i)))
        scores.sort(reverse=True);ids=[]
        for _,i in scores:
            if all(abs(i-j)>=2 for j in ids):ids.append(i)
            if len(ids)==8:break
        base=np.array([[122,127,127],[137,143,143],[130,137,139],[161,166,168],[181,183,184],[128,132,130]][group],'f4')
        if not ids:return np.broadcast_to(base,(height,width,3)).astype('u1').copy()
        xyz=positions(width,height);total=np.zeros((height,width,3),'f4');mass=np.zeros((height,width),'f4')
        for j,i in enumerate(ids):
            xy,score=self.evidence(xyz,n,i,glass)
            col=cv2.remap(self.image(i),xy,None,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
            wt=(score*(1.5 if j==0 else 1.))**3.1
            total+=col*wt[:,:,None];mass+=wt
        val=total/np.maximum(mass[:,:,None],1.e-12)
        good=mass>9.e-7
        if good.any() and not good.all():
            d,near=ndimage.distance_transform_edt(~good,return_indices=True)
            reference=np.median(val[good][::max(1,int(good.sum()//1400))],axis=0)
            if good.mean()<.15:reference=.50*reference+.50*base
            t=np.exp(-d/19.)[:,:,None]
            val=np.where(good[:,:,None],val,val[tuple(near)]*t+reference*(1-t))
        elif not good.any():val[:]=base
        return val.clip(0,255).astype('u1')


def bake_atlases(tiles,uv,at,baker,cache):
    tex=OUT/'textures';tex.mkdir(exist_ok=True);edge=2048;pad=4
    cache.mkdir(parents=True,exist_ok=True)
    result=uv.copy();pages=np.full(len(at),-1,'i4')
    order=np.argsort(at);page=-1;sheet=None;x=y=height=0
    for counter,idx in enumerate(sorted(range(len(tiles)),key=lambda i:-tiles[i][2])):
        tile=tiles[idx];w,h=tile[1:3]
        if x+w+2*pad>edge:x=0;y+=height;height=0
        if sheet is None or y+h+2*pad>edge:
            if sheet is not None:cv2.imwrite(str(tex/f'detail_{page:02}.jpg'),sheet,[cv2.IMWRITE_JPEG_QUALITY,96])
            sheet=np.full((edge,edge,3),145,'u1');page+=1;x=y=height=0
        tile_path=cache/f'{idx:04}.jpg'
        if tile_path.exists():pic=cv2.imread(str(tile_path))
        else:
            pic=baker.bake(tile);cv2.imwrite(str(tile_path),pic,[cv2.IMWRITE_JPEG_QUALITY,97])
        sheet[y:y+h+2*pad,x:x+w+2*pad]=cv2.copyMakeBorder(pic,pad,pad,pad,pad,cv2.BORDER_REPLICATE)
        positions=np.searchsorted(at,[idx,idx+1],sorter=order);ids=order[positions[0]:positions[1]]
        result[ids,:,0]=(x+pad+uv[ids,:,0]*w)/edge;result[ids,:,1]=1-(y+pad+uv[ids,:,1]*h)/edge;pages[ids]=page
        x+=w+2*pad;height=max(height,h+2*pad)
        if counter%60==0:print('Texture',counter,'/',len(tiles),flush=True)
    cv2.imwrite(str(tex/f'detail_{page:02}.jpg'),sheet,[cv2.IMWRITE_JPEG_QUALITY,96])
    return result,pages


def main():
    cv2.setNumThreads(1);parts,b,report=prepare()
    a=np.load(ROOT/'architecture/scene.npz')
    from fit_missing_building_planes import extend
    extend(parts,b,a,report)
    from repair_floors_and_pillars import clear_guard_sheets, clear_old_column_faces, rail_segments, write_guard
    segments=rail_segments(a)
    report['coarse_column_cells_replaced']=clear_old_column_faces(parts,report['solid_columns'])
    report['opaque_landing_guard_cells_removed']=clear_guard_sheets(parts,segments)
    report['landing_guard_segments']=segments
    write_guard(OUT,segments,b)
    from complete_building_walls import measured_rays
    from filter_surface_evidence import filter_registered_build
    origins,ends=measured_rays(b)
    poses=np.load(ROOT/'photomesh_hd/aligned.npz')['color_poses']
    depth=np.load(FINE/'rgb_depth.npy',mmap_mode='r')
    calibration=np.load(FINE/'cameras.npz')
    k=calibration['color_k'].copy()
    k[0]*=depth.shape[2]/calibration['size'][0]
    k[1]*=depth.shape[1]/calibration['size'][1]
    raster_size=(depth.shape[2],depth.shape[1])
    masks=np.stack([cv2.resize(cv2.imread(str(JOB/'exclusion'/f'{i:04}.png'),0),
                    raster_size,interpolation=cv2.INTER_AREA)>0 for i in range(len(poses))])
    with np.load(OUT/'rail.npz') as rail:
        report['surface_evidence']=filter_registered_build(parts,b,origins,ends,rail,poses,k,depth,masks)
    report.update(anchor_components(parts,a['trajectory'][:,1:4]@b))
    v,f,g,at,uv,col,tiles,stats=collect(parts,b,report['solid_columns'],OUT/'rail.npz');report.update(stats)
    print('geometry',len(v),len(f),len(tiles),report,flush=True)
    np.savez(OUT/'geometry.npz',v=v,f=f,g=g)
    report.update({'triangles':len(f),'treads':len(a['steps']),'photo_tiles':len(tiles),'solid_parts':sum(p.mask.any() for p in parts).item()})
    (OUT/'geometry.json').write_text(json.dumps(report,indent=2))
    mesh_key=hashlib.sha256()
    for data in (v,f,at,uv):mesh_key.update(np.ascontiguousarray(data).view('u1'))
    baker=PhotoBaker(scene(v,f))
    st,pages=bake_atlases(tiles,uv,at,baker,OUT/'tiles'/mesh_key.hexdigest()[:20])
    collision=OUT/'collision.npz'
    np.savez(collision,v=v,f=f[g<6],g=g[g<6],already_solid=True)
    args=(OUT,OUT,v,f,st,pages,col)
    write_glb(*args);write_isaac(*args,collision)
    print('Finished contour model',flush=True)


if __name__=='__main__':main()
