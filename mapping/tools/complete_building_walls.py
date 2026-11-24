"""Restore walls from the measured architectural shell, with a free-space veto."""
import json

import cv2
import numpy as np
import open3d as o3d
from scipy import ndimage
from scipy.spatial import cKDTree
from check_fine_mesh import scene
from clean_building_photos import ROOT, JOB, FINE, HD
from texture_isaac_scan import project, pack
from publish_fine_mesh import write_glb, write_isaac


def body_faces(vertices,faces,protected):
    centers=vertices[faces].mean(1)
    body=cKDTree(np.load(JOB/'body.npy'))
    dist=body.query(centers,distance_upper_bound=.26,workers=5)[0]
    ids=np.flatnonzero((dist<.26)&~protected)
    candidates=centers[ids]
    cfg=np.load(FINE/'cameras.npz');k=cfg['color_k']
    poses=np.load(HD/'aligned.npz')['color_poses'];depth=np.load(FINE/'rgb_depth.npy',mmap_mode='r')
    positive=np.zeros(len(ids),'i4');static=positive.copy()
    for i,p in enumerate(poses):
        sel=np.flatnonzero(np.linalg.norm(candidates-p[:3,3],axis=1)<9.)
        if not len(sel):continue
        xy,z=project(candidates[sel],p,k)
        u,w=np.rint(xy).astype(int).T
        ok=(z>.24)&(u>=0)&(u<640)&(w>=0)&(w<480)
        sel,u,w,z=sel[ok],u[ok],w[ok],z[ok]
        mask=cv2.imread(str(JOB/'exclusion'/f'{i:04}.png'),0)
        blocked=mask[w,u]>0
        measured=depth[i,w//2,u//2]*.001
        positive[sel]+=blocked & (abs(z-measured)<.21+.027*z)
        static[sel]+=~blocked & (abs(z-measured)<.055+.009*z)
    remove=np.zeros(len(faces),bool)
    remove[ids]=(positive>=2)&(static<np.maximum(3,positive*1.25))&((dist[ids]<.17)|(positive>=4))
    return remove


def measured_rays(b):
    d=np.load(ROOT/'mapped/outputs.npz');track=d['trajectory']
    st=d['cloud_stamps'];offsets=d['cloud_offsets']
    src=np.column_stack([np.interp(st,track[:,0],q) for q in track[:,1:4].T])@b
    p=d['registered_points'][::2]@b
    ix=np.searchsorted(offsets[1:],np.arange(0,int(offsets[-1]),2),side='right')
    src=src[ix]; delta=p-src
    keep=np.linalg.norm(delta,axis=1)<15.
    return src[keep].astype('f4'),p[keep].astype('f4')


def clear_foreground(vertices,faces,allow):
    """Discard unsupported mesh fragments in the space in front of people.

    The distance camera often measured the person correctly while the fused
    surface grew towards the camera. Such triangles cannot be found by simply
    removing points at the depth of the body.
    """
    centers=vertices[faces].mean(1)
    tree=cKDTree(centers)
    cfg=np.load(FINE/'cameras.npz');k=cfg['color_k']
    poses=np.load(HD/'aligned.npz')['color_poses']
    depth=np.load(FINE/'rgb_depth.npy',mmap_mode='r')
    free=np.zeros(len(faces),'i4');surface=free.copy()
    frames=[]
    for i in range(len(poses)):
        mask=cv2.imread(str(JOB/'exclusion'/f'{i:04}.png'),0)
        if (mask>0).mean()>.012:frames.append(i)
    cameras=cKDTree(poses[frames,:3,3])
    for i,p in enumerate(poses):
        if cameras.query(p[:3,3])[0]>4.:continue
        ids=np.array(tree.query_ball_point(p[:3,3],5.8),int)
        ids=ids[allow[ids]]
        xy,z=project(centers[ids],p,k);u,w=np.rint(xy*.5).astype(int).T
        ok=(u>=2)&(u<318)&(w>=2)&(w<238)&(z>.12)
        ids,z,u,w=ids[ok],z[ok],u[ok],w[ok]
        dm=depth[i]
        sample=np.stack([dm[(w+dy),(u+dx)] for dx,dy in ((0,0),(-1,0),(1,0),(0,-1),(0,1))]).astype('f4')*.001
        mask=cv2.imread(str(JOB/'exclusion'/f'{i:04}.png'),0)
        blocked=mask[2*w,2*u]>0
        match=(abs(sample-z)<.075+.015*z).sum(0)>=2
        surface[ids]+=match&~blocked
        # All sampled rays must reach well beyond this triangle; discount a depth edge.
        past=(sample>z+.20+.038*z)&(sample<6.45)
        free[ids]+=(past.sum(0)>=4)
    return allow&(free>=4)&(free>2.5*surface+1)


def wall_patches(v,f,cv,cf,group,arch):
    b=arch['b'];target=scene(v,f)
    orig,end=measured_rays(b);delta=end-orig
    source=cv[cf[group==3]]@b
    normal=np.cross(source[:,1]-source[:,0],source[:,2]-source[:,0])
    axis=np.argmax(abs(normal),axis=1);mid=source.mean(1);track=arch['trajectory'][:,1:4]@b
    route=cKDTree(track/[.65,.65,.72]);l,r,_=arch['stair_bounds'];steps=arch['steps']
    planes=np.round(mid[np.arange(len(axis)),axis],2)
    new=[];extra=[];areas=[];sizes=[];veto=0
    cell=.16
    for ax,level in sorted(set(zip(axis,planes))):
        use=(axis==ax)&(planes==level)
        if ax==2 or use.sum()<50:continue
        level=float(np.median(mid[use,ax]))
        a=1-ax; uv=mid[use][:,[a,2]];lo=np.floor((uv.min(0)-.4)/cell)*cell
        shape=tuple((np.ceil((uv.max(0)-lo)/cell)+4).astype(int))
        def bins(p):
            ij=np.floor((p-lo)/cell).astype(int)
            inside=((ij>=0)&(ij<shape)).all(1);ij=ij[inside]
            return np.bincount(np.ravel_multi_index(ij.T,shape),minlength=np.prod(shape)).reshape(shape)
        # Rasterize the original measured triangles with several interior samples.
        tri=source[use]
        samples=np.concatenate([tri.mean(1)]+[.70*tri[:,i]+.15*tri[:,(i+1)%3]+.15*tri[:,(i+2)%3] for i in range(3)])
        shell=bins(samples[:,[a,2]])>0
        through=((orig[:,ax]-level)*(end[:,ax]-level)<0)&(abs(end[:,ax]-level)>.42)&(abs(orig[:,ax]-level)>.30)
        o=orig[through];d=delta[through]
        hits=o+d*((level-o[:,ax])/d[:,ax])[:,None]
        cross=ndimage.gaussian_filter(bins(hits[:,[a,2]]).astype('f4'),.85)
        endpoint=end[abs(end[:,ax]-level)<.11]
        returns=ndimage.gaussian_filter(bins(endpoint[:,[a,2]]).astype('f4'),.85)
        open_cells=(cross>.95)&(cross>returns*.75)
        # Only bridge enclosed small holes in an existing wall patch. An opening
        # connected to the wall boundary or large enough for a passage remains.
        holes=ndimage.binary_fill_holes(shell)&~shell
        labels,n=ndimage.label(holes);counts=np.bincount(labels.ravel());counts[0]=0
        small=holes&(counts[labels]<=20)&(ndimage.distance_transform_edt(~shell)<.40)
        small &= ~ndimage.maximum_filter(open_cells,size=3)
        veto+=int(((shell|small)&open_cells).sum())
        safe=(shell|small)&~open_cells
        ij=np.array(np.where(safe)).T
        if not len(ij):continue
        pt=np.zeros((len(ij),3));pt[:,ax]=level;pt[:,[a,2]]=lo+(ij+.5)*cell
        # The stair railing and adjacent open air must never become a solid wall.
        rail=(abs(pt[:,0]-r)<.43)&(pt[:,1]>steps[0,0]-.55)&(pt[:,1]<steps[-1,0]+.70)
        nearest_height=np.r_[arch['stair_bounds'][2],steps[:,1]][np.searchsorted(steps[:,0],pt[:,1],side='right')]
        rail &= (pt[:,2]>nearest_height-.13)&(pt[:,2]<nearest_height+2.1)
        keep=~rail & (route.query(pt/[.65,.65,.72],workers=4)[0]>1)
        pt=pt[keep];ij=ij[keep]
        if not len(pt):continue
        face_normal=b[:,ax].astype('f4')
        # Sample the centre and four off-centre points on each cell. Restrict
        # insertions to genuine gaps in the existing, cleaned visual mesh.
        covered=np.zeros(len(pt),'i4')
        for du,dz in [(0.,0.),(-.055,-.055),(-.055,.055),(.055,-.055),(.055,.055)]:
            sample=pt.copy();sample[:,a]+=du;sample[:,2]+=dz
            world=(sample@b.T).astype('f4');hit_any=np.zeros(len(pt),bool)
            for sign in (1.,-1.):
                direction=np.broadcast_to(face_normal*sign,world.shape)
                ray=np.c_[world-direction*.27,direction].astype('f4')
                hit=target.cast_rays(o3d.core.Tensor(ray),nthreads=4)
                distance=hit['t_hit'].numpy()
                aligned=abs(hit['primitive_normals'].numpy()@face_normal)>.52
                hit_any |= (abs(distance-.27)<.145)&aligned
            covered+=hit_any
        needed=covered<=2
        if not needed.any():continue
        pt,ij=pt[needed],ij[needed]
        quad=np.repeat(pt[:,None,:],4,axis=1)
        quad[:,:,a]+=cell*np.array([-.5,.5,.5,-.5]);quad[:,:,2]+=cell*np.array([-.5,-.5,.5,.5])
        new.append((quad@b.T).astype('f4'))
        extra.append(small[ij[:,0],ij[:,1]])
        areas.append(len(pt)*cell**2);sizes.append({'axis':int(ax),'plane_m':round(level,2),'area_m2':round(areas[-1],2)})
    if not new:raise ValueError('No supported wall repairs')
    quads=np.concatenate(new);infill=np.concatenate(extra)
    indices=np.arange(len(quads)*4,dtype='i4').reshape(-1,4)
    tris=indices[:,[0,1,2,0,2,3]].reshape(-1,3)
    summary={'added_wall_area_m2':round(sum(areas),2),'wall_planes':sizes,'added_wall_cells':len(quads),
             'small_enclosed_infill_m2':round(infill.sum()*cell**2,2),'wall_grid_spacing_m':cell,
             'vetoed_plane_cells_with_through_rays':veto}
    return quads.reshape(-1,3),tris,np.repeat(infill,2),summary


def patch_photos(v,f,initial_scene,colors_ref,v_ref):
    cfg=np.load(FINE/'cameras.npz');k=cfg['color_k'];poses=np.load(HD/'aligned.npz')['color_poses']
    depth=np.load(FINE/'rgb_depth.npy',mmap_mode='r')
    quads=v.reshape(-1,4,3);mid=quads.mean(1);norm=np.cross(quads[:,1]-quads[:,0],quads[:,3]-quads[:,0])
    norm/=np.linalg.norm(norm,axis=1,keepdims=True)
    tree=cKDTree(mid);best=np.zeros(len(mid),'f4');labels=np.full(len(mid),-1,'i4')
    for i,p in enumerate(poses):
        ids=np.array(tree.query_ball_point(p[:3,3],13.),int)
        if not len(ids):continue
        pix,z=project(quads[ids],p,k)
        good=((z>.25)&(pix[:,:,0]>2)&(pix[:,:,0]<637)&(pix[:,:,1]>2)&(pix[:,:,1]<477)).all(1)
        pix,z,ids=pix[good],z[good].mean(1),ids[good]
        if not len(ids):continue
        lo=np.floor(pix.min(1)).astype(int);hi=np.ceil(pix.max(1)).astype(int)+1
        mask=cv2.imread(str(JOB/'exclusion'/f'{i:04}.png'),0)
        if mask.any():
            arr=cv2.integral((mask>0).astype('u1'));x,y=lo.T;u,w=hi.T
            clear=(arr[w,u]-arr[w,x]-arr[y,u]+arr[y,x])==0
            pix,z,ids=pix[clear],z[clear],ids[clear]
        if not len(ids):continue
        x,y=(pix.mean(1)*.5).astype(int).T
        obs=depth[i,y,x]*.001; q=mid[ids]-p[:3,3];dist=np.linalg.norm(q,axis=1)
        direction=q/dist[:,None]
        rays=np.c_[np.broadcast_to(p[:3,3],direction.shape),direction].astype('f4')
        hit=initial_scene.cast_rays(o3d.core.Tensor(rays),nthreads=4)['t_hit'].numpy()
        agreement=np.where(obs>.25,np.exp(-abs(obs-z)/(.15+.045*z)),.49)
        score=np.abs((direction*norm[ids]).sum(1))*agreement/(.55+dist)*np.clip(cfg['sharpness'][i]/75,.45,1.6)
        score[(hit<dist-.14-.02*z)|((obs>.25)&(abs(obs-z)>.38+.07*z))]=0
        use=score>np.maximum(.008,best[ids]);best[ids[use]]=score[use];labels[ids[use]]=i
    tex=JOB/'repairs_textures'
    uv,at,_=pack(v,f,np.repeat(labels,2),np.arange(len(poses)),poses,k,JOB/'photos',tex)
    known=np.any(colors_ref!=125,axis=1) & np.any(colors_ref!=126,axis=1)
    src=np.flatnonzero(known)
    nbr=cKDTree(v_ref[src]).query(v,k=11,workers=5)[1]
    colors=np.median(colors_ref[src[nbr]],axis=1).astype('u1')
    return uv,at,colors


def main():
    cv2.setNumThreads(1)
    clean=np.load(JOB/'clean_surface.npz');v,f,uv,at,colors=(clean[k] for k in ('v','f','uv','atlas','colors'))
    arch=np.load(ROOT/'architecture/scene.npz');col=np.load(ROOT/'architecture/final_collision.npz')
    cv,cf,cg=col['v'],col['f'],col['g']
    # Keep measured structural surfaces when a person stood against them.
    structure=scene(cv,cf[np.isin(cg,[0,1,2,3,4])])
    centers=v[f].mean(1).astype('f4')
    close=np.concatenate([structure.compute_distance(o3d.core.Tensor(x),nthreads=5).numpy() for x in np.array_split(centers,18)])<.071
    gone=body_faces(v,f,close);removed_collision=body_faces(cv,cf,cg!=5)
    protected=scene(cv,cf[np.isin(cg,[0,1,2,4])])
    structural=np.concatenate([protected.compute_distance(o3d.core.Tensor(x),nthreads=5).numpy() for x in np.array_split(centers,18)])<.055
    rail=np.load(FINE/'rail.npz')
    guard=scene(rail['v'],rail['f'])
    local=centers@arch['b']
    near_stair=(abs(local[:,0]-arch['stair_bounds'][1])<.6)&(local[:,1]>-18.5)&(local[:,1]<-8.5)
    if near_stair.any():
        structural[near_stair]|=guard.compute_distance(o3d.core.Tensor(centers[near_stair]),nthreads=4).numpy()<.05
    clutter=clear_foreground(v,f,~structural)
    collision_clutter=clear_foreground(cv,cf,np.isin(cg,[3,5]))
    count_body=int(gone.sum());count_col_body=int(removed_collision.sum())
    gone|=clutter;removed_collision|=collision_clutter
    f,uv,at=f[~gone],uv[~gone],at[~gone]
    cf,cg=cf[~removed_collision],cg[~removed_collision]
    wall,wf,additional,stats=wall_patches(v,f,cv,cf,cg,arch)
    patch_uv,patch_at,wall_rgb=patch_photos(wall,wf,scene(v,f),colors,v)
    out=JOB/'result';out.mkdir(exist_ok=True);tex=out/'textures';tex.mkdir(exist_ok=True)
    for src in (JOB/'planes/textures').glob('*.jpg'):
        dst=tex/src.name
        if not dst.exists():dst.symlink_to(src.resolve())
    page=int(at.max())+1
    for src in (JOB/'repairs_textures').glob('*.jpg'):
        idx=int(src.stem.split('_')[-1]);dst=tex/f'detail_{idx+page:02}.jpg'
        if not dst.exists():dst.symlink_to(src.resolve())
    patch_at=np.where(patch_at>=0,patch_at+page,-1)
    stats.update({'removed_visual_body_faces':count_body,'removed_collision_body_faces':count_col_body,
                  'removed_visual_free_space_fragments':int(clutter.sum()),'removed_collision_free_space_fragments':int(collision_clutter.sum()),
                  'added_wall_quads_with_clean_photo':int((patch_at[::2]>=0).sum())})
    vv=np.vstack((v,wall));ff=np.vstack((f,wf+len(v)));aa=np.r_[at,patch_at];uu=np.concatenate([uv,patch_uv])
    collider=JOB/'collision.npz'
    np.savez(collider,v=np.vstack((cv,wall)),f=np.vstack((cf,wf[additional]+len(cv))),g=np.r_[cg,np.full(sum(additional),3,'i4')])
    rail=out/'rail.npz'
    if not rail.exists():rail.symlink_to((FINE/'rail.npz').resolve())
    np.savez(JOB/'patches.npz',v=wall,f=wf,extended=additional)
    from texture_restored_walls import apply
    vv,ff,uu,aa,rgb,area=apply(vv,ff,uu,aa,np.vstack([colors,wall_rgb]),out,measured_rays)
    stats['continuous_wall_photo_area_near_stairs_m2']=round(area,2)
    args=(out,out,vv,ff,uu,aa,rgb)
    write_glb(*args);write_isaac(*args,collider)
    (JOB/'repairs.json').write_text(json.dumps(stats,indent=2))
    print('REPAIRED',stats['added_wall_area_m2'],stats['removed_visual_body_faces'],stats['removed_collision_body_faces'],flush=True)


if __name__=='__main__':
    main()
