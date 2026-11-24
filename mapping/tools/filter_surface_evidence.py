"""Validate candidate planar patches with registered LiDAR rays and RGB-D keyframes.

All positions, patch grids, and camera-to-world matrices use a common metric
frame. Intrinsics must refer to the supplied depth raster. A zero depth is an
unknown pixel. No building extents or absolute poses enter the decisions.
"""
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree


def camera_votes(points, normals, poses, intrinsics, depth_mm, masks):
    support = np.zeros(len(points), np.int32)
    free = np.zeros_like(support)
    if not len(poses):
        return support, free
    height, width = depth_mm.shape[1:]
    # Revisiting or standing at the same position only casts one vote per patch.
    bins = np.floor((poses[:, :3, 3] - poses[0, :3, 3]) / .45).astype(int)
    _, groups = np.unique(bins, axis=0, return_inverse=True)
    for group in np.unique(groups):
        surface = np.zeros(len(points), bool)
        behind = np.zeros_like(surface)
        for i in np.flatnonzero(groups == group)[::2]:
            p = poses[i]
            delta = points - p[:3, 3]
            local = delta @ p[:3, :3]
            z = local[:, 2]
            incidence = np.abs(np.sum(delta * normals, axis=1))
            valid = (z > .35) & (z < 6.0) & (incidence > .18*np.linalg.norm(delta,axis=1))
            ids = np.flatnonzero(valid)
            uv = local[ids, :2] / z[ids, None] * intrinsics.diagonal()[:2] + intrinsics[:2, 2]
            ix, iy = np.rint(uv).astype(int).T
            ok = (ix>=2)&(ix<width-2)&(iy>=2)&(iy<height-2)
            idx, x, y = ids[ok], ix[ok], iy[ok]
            if not len(idx):
                continue
            readings = np.stack([depth_mm[i, y+dy, x+dx] for dx,dy in
                                 ((0,0),(-1,0),(1,0),(0,-1),(0,1))]) * .001
            measured = np.median(readings, axis=0)
            usable = (readings.min(0)>.2)&(readings.max(0)-readings.min(0)<.14+.015*z[idx])
            if masks is not None:
                usable &= ~masks[i,y,x]
            difference = measured-z[idx]
            surface[idx] |= usable & (abs(difference)<.065+.009*z[idx])
            behind[idx] |= usable & (difference>.17+.014*z[idx])
        support += surface
        free += behind & ~surface
    return support, free


def lidar_votes(grid, origin, end, station, length):
    """Count distinct observing stations and independently sampled cell quadrants."""
    shape = tuple(n-1 for n in grid.shape[:2])
    base = grid[0,0]
    du, dv = grid[1,0]-base, grid[0,1]-base
    normal = np.cross(du,dv)
    normal = normal/np.linalg.norm(normal)
    start = (origin-base)@normal
    stop = (end-base)@normal
    change = stop-start
    facing = (abs(change)>.18*length)&(abs(start)>.18)
    close = facing & (abs(stop)<.065)
    crossed = facing & (start*stop<0)&(abs(stop)>.19)
    axes=np.stack((du/(du@du),dv/(dv@dv))).T
    def bins(points, groups):
        uv = (points-base)@axes
        valid = np.all((uv>=0)&(uv<shape),axis=1)
        fine = np.floor(2*uv[valid]).astype(np.int64)
        cell=(fine[:,0]//2)*shape[1]+fine[:,1]//2
        quadrants = (fine[:,0]%2)*2+fine[:,1]%2
        key=np.unique((cell*4+quadrants)*station_count+groups[valid])
        count=np.bincount(np.unique((key//(4*station_count))*station_count+key%station_count)//station_count,
                          minlength=np.prod(shape))
        quadr=np.bincount(np.unique(key//station_count)//4,minlength=np.prod(shape))
        return count.reshape(shape),quadr.reshape(shape)
    station_count=int(station.max())+1
    support, cover = bins(end[close],station[close])
    ratio = -start[crossed]/change[crossed]
    intersection = origin[crossed]+(end[crossed]-origin[crossed])*ratio[:,None]
    free, pass_cover = bins(intersection,station[crossed])
    return support,cover,free,pass_cover


def measure(parts, origin, end, poses, intrinsics, depth_mm, masks):
    """Return evidence images for the active cells of each regular planar grid."""
    from open3d import geometry, utility
    cloud=geometry.PointCloud(utility.Vector3dVector(end))
    cloud=cloud.voxel_down_sample(.048)
    cloud.estimate_normals(geometry.KDTreeSearchParamHybrid(radius=.16,max_nn=45))
    samples=np.asarray(cloud.points)
    surface_normals=np.asarray(cloud.normals)
    tree=cKDTree(samples)
    length=np.linalg.norm(end-origin,axis=1)
    _,station=np.unique(np.floor((origin-origin[0])/.45).astype('i4'),axis=0,return_inverse=True)
    centers=[((p.grid[1:,1:]+p.grid[:-1,:-1])*.5)[p.mask] for p in parts]
    points=np.vstack(centers)
    normals=np.vstack([np.broadcast_to(p.normal,q.shape) for p,q in zip(parts,centers)])
    rgb, rgb_free=camera_votes(points,normals,poses,intrinsics,depth_mm,masks)
    ds,near=tree.query(points,k=24,workers=4)
    offsets=samples[near]-points[:,None]
    agreement=(abs(np.einsum('ijk,ik->ij',surface_normals[near],normals))>.90)
    agreement &= abs(np.einsum('ijk,ik->ij',offsets,normals))<.068
    aligned=((ds<.18)&agreement).sum(1)
    out=[];j=0
    for part,xyz in zip(parts,centers):
        support,cover,free,pass_cover=lidar_votes(part.grid,origin,end,station,length)
        row=dict(lidar=support,cover=cover,free=free,pass_cover=pass_cover)
        for name,values in [('rgb',rgb),('rgb_free',rgb_free),('aligned',aligned)]:
            m=np.zeros(part.mask.shape,np.int32);m[part.mask]=values[j:j+len(xyz)];row[name]=m
        out.append(row)
        j+=len(xyz)
    return out


def filter_patches(parts,evidence,residual):
    """Reject contradicted surface cells before generating thickness or texturing."""
    report=[]
    for p,e,supplement in zip(parts,evidence,residual):
        mask=p.mask.copy()
        L,F,R,D,A,Q,P=[e[k] for k in ('lidar','free','rgb','rgb_free','aligned','cover','pass_cover')]
        contradicted=((F>=2)&(P>=3)&(F>1.7*L)&(A<9))|((D>=2)&(D>1.6*R)&(A<5)&(F>L))
        seed=((L>=2)&(Q>=3)&(A>=5))|((A>=10)&(L>=1))|((R>=2)&(A>=3)&(F<=L+1))
        present=mask & ~contradicted
        # Require a patch of area support. A row of hits along the intersection
        # of two planes, or the outline of a door, cannot justify a solid sheet.
        if supplement:
            core=ndimage.uniform_filter((seed&mask).astype(float),size=3)>.43
            plausible=ndimage.maximum_filter(core,size=3)&present
            labels,n=ndimage.label(plausible)
            for i,region in enumerate(ndimage.find_objects(labels),1):
                sub=labels[region]==i
                if sub.sum()<10 or not ndimage.binary_opening(sub,np.ones((2,2))).any():
                    target=plausible[region];target[sub]=False
            present=plausible
        p.mask=present
        report.append(dict(patch=p.name,cells_before=int(mask.sum()),cells_after=int(present.sum()),
                           contradicted=int((contradicted&mask).sum())))
    return report


def measured_post_gaps(vertices, faces):
    """Find passages between adjacent upright cylindrical mesh members in Z-up coordinates."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    edges=faces[:,[0,1,1,2]].reshape(-1,2)
    graph=coo_matrix((np.ones(len(edges),bool),edges.T),shape=(len(vertices),len(vertices)))
    _,labels=connected_components(graph,directed=False)
    posts=[]
    order=np.argsort(labels)
    for ids in np.split(order,np.flatnonzero(np.diff(labels[order]))+1):
        pts=vertices[ids]
        width=np.ptp(pts[:,:2],axis=0)
        bottom,top=pts[:,2].min(),pts[:,2].max()
        if len(ids)>=8 and max(width)<.085 and top-bottom>.32:
            posts.append([*pts[:,:2].mean(0),bottom,top])
    if len(posts)<2:
        return np.empty((0,2,4))
    posts=np.asarray(posts)
    pairs=cKDTree(posts[:,:2]).query_pairs(.23,output_type='ndarray')
    pairs=posts[pairs]
    delta=pairs[:,1]-pairs[:,0]
    use=(np.linalg.norm(delta[:,:2],axis=1)>.065)&(abs(delta[:,2])<.26)&(abs(delta[:,3])<.23)
    return pairs[use]


def open_post_gaps(parts,pairs):
    removed=0
    if not len(pairs):
        return removed
    centers=pairs.mean(1)
    delta=pairs[:,1,:2]-pairs[:,0,:2]
    spans=np.linalg.norm(delta,axis=1)
    tangent=delta/spans[:,None]
    normal=np.stack([-tangent[:,1],tangent[:,0]],axis=1)
    tree=cKDTree(centers[:,:2])
    for p in parts:
        if abs(p.normal[2])>.60 or not p.mask.any():
            continue
        idx=np.where(p.mask)
        xyz=((p.grid[1:,1:]+p.grid[:-1,:-1])*.5)[idx]
        dist,j=tree.query(xyz[:,:2],k=min(4,len(pairs)))
        j=j.reshape(len(xyz),-1)
        off=xyz[:,None,:2]-centers[j,:2]
        along=np.sum(off*tangent[j],axis=2)
        cross=np.sum(off*normal[j],axis=2)
        # A wall behind a rail must remain. Only replace a sheet occupying
        # the actual row of posts and parallel to its run.
        coplanar=(abs(cross)<.078)&(abs(along)<spans[j]*.5+.055)&(abs(normal[j]@p.normal[:2])>.86)
        t=np.clip(.5+along/spans[j],0,1)
        lo=pairs[j,0,2]+t*(pairs[j,1,2]-pairs[j,0,2])
        hi=pairs[j,0,3]+t*(pairs[j,1,3]-pairs[j,0,3])
        replace=np.any(coplanar&(xyz[:,None,2]>lo-.055)&(xyz[:,None,2]<hi+.06),axis=1)
        p.mask[idx[0][replace],idx[1][replace]]=False
        removed+=int(replace.sum())
    return removed


def filter_registered_build(parts, basis, ray_origins, ray_ends, rail, camera_poses,
                            rgb_intrinsics, depth_mm, masks):
    """Adapter for the contour builder. Pass LiDAR in the panel frame, cameras/rail in world."""
    selected=[p for p in parts if p.mask.any() and
              (p.name.startswith('Wand_') or p.name in ('Decke_gemessen','Zusatzfläche_gemessen'))]
    # Analytically fitted floors, doors, glazing, stairs and piers keep their
    # explicit semantic boundaries. Glass transmits both types of range sensor.
    poses=camera_poses.copy()
    poses[:,:3,:3]=basis.T@poses[:,:3,:3]
    poses[:,:3,3]=poses[:,:3,3]@basis
    if not selected:
        return {'patches':[],'guard_sheet_cells_removed':0,'surveyed_recesses':[]}
    measured=np.isfinite(ray_origins).all(1)&np.isfinite(ray_ends).all(1)
    if not measured.any():
        raise ValueError("Surface filtering requires finite registered LiDAR rays")
    if not measured.all():
        ray_origins,ray_ends=ray_origins[measured],ray_ends[measured]
    evidence=measure(selected,ray_origins,ray_ends,poses,rgb_intrinsics,depth_mm,masks)
    report=filter_patches(selected,evidence,[p.name in ('Zusatzfläche_gemessen','Decke_gemessen') for p in selected])
    pairs=measured_post_gaps(rail['v']@basis,rail['f'])
    removed=open_post_gaps(selected,pairs)
    recesses=fit_recesses(parts,ray_ends)
    return {'patches':report,'guard_sheet_cells_removed':removed,'surveyed_recesses':recesses}


def fit_recesses(parts, returns):
    """Fit a rectangular reveal when a measured back panel, side walls and a lintel agree."""
    from build_building_contours import rectangular

    result=[]
    for back in [p for p in parts if p.name.startswith('Glas_') or p.name=='Türblatt']:
        ax=int(abs(back.normal).argmax())
        if ax==2:continue
        along=1-ax
        lo,hi=back.grid.min((0,1)),back.grid.max((0,1))
        zb,zt=lo[2],hi[2];u0,u1=lo[along],hi[along]
        if min(zt-zb,u1-u0)<.70:continue
        for wall in list(parts):
            if not wall.name.startswith('Wand_') or abs(wall.normal[ax])<.99:continue
            front=float(wall.grid[0,0,ax]);rear=float(lo[ax]);depth=(front-rear)*back.normal[ax]
            if not .33<depth<2.05:continue
            wallbase=wall.grid.min((0,1));walltop=wall.grid.max((0,1))
            if wallbase[along]>u0 or walltop[along]<u1 or walltop[2]<zt-.22:continue
            near=returns[(abs(returns[:,ax]-front)<.064)&(returns[:,2]>zb)&(returns[:,2]<zt+.25)]
            mid=(near[:,2]>zb+.32)&(near[:,2]<zt-.40)
            center=(near[:,along]>u0+.16)&(near[:,along]<u1-.16)
            skin=(returns[:,ax]>min(rear,front)+.09)&(returns[:,ax]<max(rear,front)-.09)
            # Both lateral faces must be observed at several heights inside
            # the recess. This blocks accidental pairings across open rooms.
            sides=[]
            for edge in (u0,u1):
                face=returns[skin&(abs(returns[:,along]-edge)<.10)]
                count=np.histogram(face[:,2],bins=np.linspace(zb+.20,zt-.20,6))[0]
                sides.append((count>=4).sum()>=4)
            if not all(sides):continue
            if sum(mid&center)>max(20,.14*(sum(mid&(abs(near[:,along]-u0)<.24))+sum(mid&(abs(near[:,along]-u1)<.24)))):continue
            levels=np.arange(zt-.25,zt+.25,.035)
            header=np.histogram(near[center,2],levels)[0]
            good=np.flatnonzero(np.minimum(header[:-1],header[1:])>5)
            if not len(good):continue
            top=float(levels[good[0]])
            bands=np.linspace(zb+.22,zt-.25,6)
            shoulders=[]
            for edge,side in ((u0,-1),(u1,1)):
                shoulder=near[(side*(near[:,along]-edge)>.08)&(side*(near[:,along]-edge)<.36)]
                shoulders.append((np.histogram(shoulder[:,2],bands)[0]>=6).sum()>=4)
            # Snap the wall grid to the fitted rim, avoiding a serrated seam.
            def snap(values,target):
                ix=int(np.argmin(abs(values-target)))
                return float(values[ix])
            us=wall.grid[:,0,along];zs=wall.grid[0,:,2]
            right,left=snap(us,u1),snap(us,u0);top=snap(zs,top)
            boxlo=np.zeros(3);boxhi=np.zeros(3)
            boxlo[ax],boxhi[ax]=sorted([rear,front])
            boxlo[along]=left;boxhi[along]=right;boxlo[2]=zb;boxhi[2]=top
            enclosed=all(shoulders)
            if not enclosed and not back.name.startswith('Glas_'):continue
            if not enclosed:
                boxlo[along]=u0;boxhi[along]=u1;boxhi[2]=zt
            # Clear competing cells within and immediately at the confirmed
            # recess. Keep the semantic back panel and other fitted inserts.
            for p in parts:
                if not (p.name.startswith('Wand_') or p.name in ('Zusatzfläche_gemessen','Decke_gemessen')):continue
                xyz=(p.grid[:-1,:-1]+p.grid[1:,1:])*.5
                pad=np.array([.072,.072,.065])
                if p is wall:
                    pad[:]=0.;pad[2]=.02
                cut=np.all((xyz>=boxlo-pad)&(xyz<=boxhi+pad),axis=2)
                p.mask &= ~cut
            xyz=(wall.grid[:-1,:-1]+wall.grid[1:,1:])*.5
            u=xyz[:,:,along];z=xyz[:,:,2]
            collar=(u>=left-.22)&(u<=right+.22)&(z>=zb)&(z<=top+.19)
            if enclosed:
                wall.mask|=collar&((u<left)|(u>right)|(z>top))
            for edge,sgn in ((left,1),(right,-1)) if enclosed else ((u0,1),(u1,-1)):
                # Use the real depth of each upright on exposed glass assemblies.
                # The atrium side may have a narrow metal frame and no outer wall.
                face=front
                if not enclosed:
                    sample=returns[skin&(abs(returns[:,along]-edge)<.10)]
                    bins=np.arange(0,depth+.035,.05)
                    density=np.histogram2d((sample[:,ax]-rear)*back.normal[ax],sample[:,2],(bins,bands))[0]
                    signal=np.flatnonzero((density>=3).sum(1)>=3)
                    if not len(signal):continue
                    face=rear+back.normal[ax]*min(depth,bins[signal[-1]+1])
                # Offset the reveal into the aperture by 3 mm to cover the
                # wall's cut end face without rendering coincident triangles.
                rectangular(parts,'Laibung_gemessen',3,along,edge+sgn*.003,
                            min(rear,face),max(rear,face),zb,top if enclosed else zt,sgn,.04)
            if enclosed:
                rectangular(parts,'Laibungsdecke_gemessen',4,2,top-.003,boxlo[0],boxhi[0],boxlo[1],boxhi[1],-1,.05)
            result.append(dict(enclosed=bool(enclosed),axis=ax,front=front,rear=rear,along_min=float(left),
                               along_max=float(right),bottom=float(zb),top=float(top),
                               depth_m=round(float(depth),3),width_m=round(right-left,3),height_m=round(float(top-zb),3)))
            break
    return result
