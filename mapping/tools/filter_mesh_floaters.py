"""Remove detached fragments from a textured scan mesh using metric separation and sensor evidence."""
import cv2
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree


def component_geometry(vertices, faces):
    # Join exact coincident vertices too, since material seams may have separate indices.
    _, welded = np.unique(np.ascontiguousarray(vertices).view(
        np.dtype((np.void, vertices.dtype.itemsize * 3))).ravel(), return_inverse=True)
    a, b, c = welded.ravel()[faces].T
    n = int(welded.max()) + 1
    links = coo_matrix((np.ones(2*len(faces), dtype='u1'), (np.r_[a,b], np.r_[b,c])), shape=(n,n))
    _, group = connected_components(links.tocsr(), directed=False)
    _, component = np.unique(group[a], return_inverse=True)
    component = component.ravel().astype('i4')
    vertex_component = np.full(len(vertices), -1, 'i4')
    vertex_component[faces.ravel()] = np.repeat(component, 3)
    active = vertex_component >= 0
    count = int(component.max()) + 1
    lo = np.full((count,3), np.inf)
    hi = np.full((count,3), -np.inf)
    np.minimum.at(lo, vertex_component[active], vertices[active])
    np.maximum.at(hi, vertex_component[active], vertices[active])
    centers = vertices[faces].mean(1)
    return component, vertex_component, centers, np.linalg.norm(hi-lo, axis=1)


def surface_samples(vertices, faces, spacing=.045):
    """Cover large triangles as well as their vertices, to protect nearby fragments at seams."""
    points = [vertices[np.unique(faces)]]
    for chunk in np.array_split(faces, max(1, int(np.ceil(len(faces)/100000)))):
        tri = vertices[chunk]
        lengths = np.maximum.reduce([np.linalg.norm(tri[:,i]-tri[:,(i+1)%3], axis=1) for i in range(3)])
        div = np.ceil(lengths/spacing).astype(int)
        for n in np.unique(div[div>1]):
            selected = tri[div==n]
            i,j = np.tril_indices(n+1)
            u,v = (i-j)/n, j/n
            interior = ~(((u==0)&(v==0)) | (u==1) | (v==1))
            u,v = u[interior,None].astype('f4'),v[interior,None].astype('f4')
            for small in np.array_split(selected, max(1,int(np.ceil(len(selected)*len(u)/150000)))):
                xyz = small[:,:1] + (small[:,1:2]-small[:,:1])*u + (small[:,2:]-small[:,:1])*v
                points.append(xyz.reshape(-1,3))
    return np.concatenate(points)


def representative_samples(centers, component, eligible):
    # Deterministic sample of actual triangles, including the ends of elongated fragments.
    ids = np.flatnonzero(eligible[component])
    order = ids[np.argsort(component[ids],kind='stable')]
    cuts = np.r_[0, 1+np.flatnonzero(np.diff(component[order])), len(order)]
    selected = []
    for begin,end in zip(cuts,cuts[1:]):
        ix = order[begin:end]
        if len(ix)>12:
            q = centers[ix]
            ix = ix[np.unique(np.r_[q.argmin(0), q.argmax(0), np.linspace(0,len(ix)-1,6,dtype=int)])]
        selected.append(ix)
    ids = np.concatenate(selected)
    return centers[ids], component[ids]


def lidar_support(samples, scans):
    """Count nearby endpoints and detect views separated by at least 25 cm along one axis."""
    with np.load(scans) as data:
        cloud, times, offsets = data['registered_points'], data['cloud_stamps'], data['cloud_offsets']
        track = data['trajectory']
    origins = np.column_stack([np.interp(times,track[:,0],col) for col in track[:,1:4].T])
    tree = cKDTree(cloud)
    counts = np.zeros(len(samples),'i4')
    repeat = np.zeros(len(samples),bool)
    # Radius queries include all viewpoints even in strongly oversampled patches.
    for begin in range(0,len(samples),5000):
        rows = tree.query_ball_point(samples[begin:begin+5000], .045, workers=4)
        lengths = np.fromiter((len(row) for row in rows),dtype='i4',count=len(rows))
        counts[begin:begin+len(rows)] = lengths
        if lengths.sum()==0:continue
        points = np.concatenate([row for row in rows if len(row)]).astype('i8')
        positions = origins[np.searchsorted(offsets[1:],points,side='right')]
        starts = np.cumsum(np.r_[0,lengths[:-1]])[lengths>0]
        spread = np.maximum.reduceat(positions,starts) - np.minimum.reduceat(positions,starts)
        repeat[begin+np.flatnonzero(lengths)] = spread.max(1)>=.25
    votes = np.zeros(len(samples),'i4')
    separated = np.zeros(len(samples),bool)
    first = np.zeros((len(samples),3),'f4')
    sample_tree = cKDTree(samples)
    # Check the actual lines of sight of individual scans. Two nearby beams
    # must both travel past the candidate, even at silhouettes and glass edges.
    for i in range(0,len(times),2):
        eye = origins[i]
        rays = cloud[offsets[i]:offsets[i+1]]-eye
        ranges = np.linalg.norm(rays,axis=1)
        good = ranges>.35
        if good.sum()<3:continue
        ranges=ranges[good]
        directions=cKDTree(rays[good]/ranges[:,None])
        ix=np.array(sample_tree.query_ball_point(eye,8.),dtype='i4')
        if not len(ix):continue
        delta=samples[ix]-eye
        length=np.linalg.norm(delta,axis=1)
        visible=length>.42
        ix,delta,length=ix[visible],delta[visible],length[visible]
        angle,near=directions.query(delta/length[:,None],k=2,distance_upper_bound=.014)
        near_range=ranges[np.minimum(near,len(ranges)-1)]
        # The angular and metric gates bound the width of the free-space test.
        free=(angle[:,1]*length<.021+.0025*length)&(near_range.min(1)>length+.13+.012*length)
        passed=ix[free]
        first[passed[votes[passed]==0]]=eye
        separated[passed]|=np.linalg.norm(first[passed]-eye,axis=1)>=.30
        votes[passed]+=1
    return counts,repeat,votes,separated


def camera_evidence(samples, work):
    cameras = np.load(work/'cameras.npz')
    corrected = work/'poses.npz'
    with np.load(corrected if corrected.exists() else work/'cameras.npz') as d:
        poses = d['depth_poses']
    depth = np.load(work/'depth.npy',mmap_mode='r')
    k = cameras['depth_k']
    if len(depth)!=len(poses):raise ValueError('Depth and camera pose counts differ')
    close, free = np.zeros((2,len(samples)),'i4')
    multi_close,multi_free = np.zeros((2,len(samples)),bool)
    first_close,first_free = np.zeros((2,len(samples),3),'f4')
    tree = cKDTree(samples)
    h,w = depth.shape[1:]
    for i in range(0,len(poses),2):
        pose = poses[i];eye = pose[:3,3]
        ids = np.array(tree.query_ball_point(eye,5.),dtype='i4')
        if not len(ids):continue
        local = (samples[ids]-eye)@pose[:3,:3]
        z = local[:,2]
        pixel = local[:,:2]/np.maximum(z[:,None],.05)*[k[0,0],k[1,1]]+k[:2,2]
        valid = (z>.35)&(z<4.1)&(pixel[:,0]>=2)&(pixel[:,0]<w-2)&(pixel[:,1]>=2)&(pixel[:,1]<h-2)
        ids,z,pixel = ids[valid],z[valid],pixel[valid]
        if not len(ids):continue
        u,v = np.rint(pixel).astype(int).T
        image = depth[i]
        measurement = image[v,u]*.001
        # A missing return or a foreground edge is never evidence for empty space.
        nearest = cv2.erode(image, np.ones((3,3),'u1'))[v,u]*.001
        close_ids = ids[(measurement>.3)&(abs(z-measurement)<.045+.012*z)]
        free_ids = ids[(nearest>z+.11+.02*z)&(nearest<4.5)]
        for ix, num, first, multi in ((close_ids,close,first_close,multi_close),(free_ids,free,first_free,multi_free)):
            first[ix[num[ix]==0]] = eye
            multi[ix] |= np.linalg.norm(first[ix]-eye,axis=1) >= .25
            num[ix] += 1
    return close,free,multi_close,multi_free


def floater_mask(vertices, faces, labels, work, scans=None):
    if len(faces)!=len(labels):
        raise ValueError('Face labels must correspond to the input mesh')
    camera = (work/'depth.npy').is_file() and (work/'cameras.npz').is_file()
    if not len(faces) or (not camera and scans is None):
        return np.ones(len(faces),bool), {'removed_components':0,'removed_triangles':0,
            'triangles_before':len(faces),'triangles_after':len(faces),'camera_used':camera,'lidar_used':scans is not None}
    component, vertex_component, centers, diameter = component_geometry(vertices,faces)
    n = len(diameter)
    # These labels are assigned by the earlier architectural and measured railing stages.
    protected = np.bincount(component,weights=np.isin(labels,[-2,-3]),minlength=n)>0
    candidate = (diameter<=.45)&~protected
    anchor = ~candidate
    keep_all = np.ones(len(faces),bool)
    if not candidate.any() or not anchor.any():
        return keep_all, {'components':n,'removed_components':0,'removed_triangles':0}
    main = cKDTree(surface_samples(vertices,faces[anchor[component]]))
    # Minimum distance includes vertices and centroids. The sampling margin is included
    # in the removal thresholds below, so tessellation gaps close to walls survive.
    usable = vertex_component>=0
    vertex_ids = np.flatnonzero(usable & candidate[np.maximum(vertex_component,0)])
    face_ids = np.flatnonzero(candidate[component])
    separation = np.full(n,np.inf)
    for xyz,group in ((vertices[vertex_ids],vertex_component[vertex_ids]),(centers[face_ids],component[face_ids])):
        distances = main.query(xyz,workers=4,distance_upper_bound=.6)[0]
        np.minimum.at(separation,group,distances)
    candidate &= separation>.041
    if not candidate.any():
        return keep_all, {'components':n,'removed_components':0,'removed_triangles':0}
    samples,owner = representative_samples(centers,component,candidate)
    samples_n = np.maximum(1,np.bincount(owner,minlength=n))
    def fraction(mask):
        return np.bincount(owner,weights=mask,minlength=n)/samples_n
    counts = np.zeros(len(samples),'i4')
    repeat = np.zeros(len(samples),bool)
    lidar_free = np.zeros(len(samples),'i4')
    multi_lidar_free = np.zeros(len(samples),bool)
    if scans is not None:
        counts,repeat,lidar_free,multi_lidar_free = lidar_support(samples,scans)
    close,free,multi_close,multi_free = np.zeros((4,len(samples)),'i4')
    if camera:
        close,free,multi_close,multi_free = camera_evidence(samples,work)
    confirmed = fraction(repeat | (multi_close & (close>=3))) >= .30
    contradicted = fraction(multi_free & (free>=3) & (free>=2*close+1)) >= .58
    # With no observations, geometry-only pruning would erase real isolated details.
    # Reserve this second rule for tiny, clearly detached pieces with little measured support.
    weak = fraction((counts>=2)|(close>=2)) < .30
    tiny = candidate & (diameter<.23) & (separation>.10) & weak & ~confirmed & (scans is not None)
    laser_clear = fraction(multi_lidar_free & (lidar_free>=3)) >= .65
    strong_return = fraction(repeat & (counts>=4)) >= .45
    laser_conflict = candidate & laser_clear & ~strong_return & (fraction(multi_close)<.28)
    conflict = candidate & contradicted & ~confirmed
    # A cluster near the edges of a reconstructed wall needs positive free-space
    # evidence. Larger stand-alone gaps can also be cleared when no returns support them.
    tiny &= (fraction((free>=2)|(lidar_free>=2))>=.25) | ((diameter<.13)&(separation>.17))
    conflict |= laser_conflict
    removed = tiny|conflict
    spared = np.zeros(n,bool)
    if camera and removed.any():
        from mesh_depth_guard import visible_surface_guard
        spared = visible_surface_guard(vertices, faces, component, removed, work)
        removed &= ~spared
    keep = ~removed[component]
    summary = dict(components=n, protected_components=int(protected.sum()), detached_candidates=int(candidate.sum()),
                   removed_components=int(removed.sum()), protected_by_depth_comparison=int(spared.sum()), lidar_free_space=int((removed&laser_conflict).sum()), weak_isolated=int((removed&tiny).sum()),
                   contradicted_only=int((removed&conflict&~tiny).sum()), removed_triangles=int((~keep).sum()),
                   triangles_before=len(faces),triangles_after=int(keep.sum()),camera_used=camera,lidar_used=scans is not None)
    return keep,summary
