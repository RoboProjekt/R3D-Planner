"""Complete measured slab edges, solid pilasters, and the open landing balustrade."""
import numpy as np
import open3d as o3d
from scipy import ndimage
from scipy.signal import find_peaks

from clean_building_photos import ROOT, FINE


def snap_axis(axis, landmarks):
    axis=axis.copy()
    for value in landmarks:
        i=np.argmin(abs(axis-value))
        if 0<i<len(axis)-1 and axis[i-1]<value<axis[i+1]:
            axis[i]=value
    return axis


def complete_floors(parts,points,arch,work):
    floor_height=float(arch['steps'][-1,1])
    left,right,_=arch['stair_bounds']
    # Horizontal support excludes a vertical facade intersecting the same elevation.
    pc=o3d.geometry.PointCloud(o3d.utility.Vector3dVector(points))
    pc=pc.voxel_down_sample(.05)
    pc.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=.18,max_nn=40))
    horizontal=np.asarray(pc.points)[abs(np.asarray(pc.normals)[:,2])>.92]
    # The entrance soffit and its continuation bound the slab below the upper
    # landing. The old prism extruded upward through the surveyed walking level.
    # Fit its underside to the closest distinct horizontal return band below it.
    for soffit in parts:
        if soffit.name not in ('Decke_Eingang','Deckenrand_EG'):
            continue
        lo=soffit.grid.min((0,1));hi=soffit.grid.max((0,1))
        inside=np.all((horizontal[:,:2]>lo[:2]+.14)&(horizontal[:,:2]<hi[:2]-.14),axis=1)
        heights=horizontal[inside,2]
        edges=np.arange(floor_height-.25,floor_height-.064,.012)
        counts=np.histogram(heights,edges)[0]
        peak=counts.argmax()
        if counts[peak]<5:raise ValueError('Insufficient slab underside returns for '+soffit.name)
        underside=float(np.median(heights[(heights>=edges[peak])&(heights<edges[peak+1])]))
        soffit.grid[:,:,2]=underside
        soffit.thickness=floor_height-.012-underside
    probes=[];stats=[]
    for panel in [part for part in parts if part.name in ('Boden_EG','Boden_1OG')]:
        upper=panel.group==1
        old=panel.mask.copy();grid=panel.grid
        u,w=grid[:,0,0].copy(),grid[0,:,1].copy()
        if upper:
            u=snap_axis(u,[-13.54,left,right,-7.98,-6.12,-5.85])
            w=snap_axis(w,[-9.50,-9.447,-9.10,-6.71,-6.058])
            grid[:,:,0]=u[:,None];grid[:,:,1]=w[None,:]
        x,y=np.meshgrid((u[1:]+u[:-1])*.5,(w[1:]+w[:-1])*.5,indexing='ij')
        height=(grid[1:,1:,2]+grid[:-1,:-1,2])*.5
        p=horizontal[abs(horizontal[:,2]-floor_height)<.115] if upper else horizontal[(horizontal[:,2]>-1.68)&(horizontal[:,2]<-.35)]
        i=np.clip(np.searchsorted(u,p[:,0])-1,0,len(u)-2);j=np.clip(np.searchsorted(w,p[:,1])-1,0,len(w)-2)
        p=p[abs(p[:,2]-height[i,j])<(.14 if upper else .37)]
        evidence=np.histogram2d(p[:,0],p[:,1],bins=(u,w))[0]
        local=ndimage.convolve((evidence>0).astype('i4'),np.ones((3,3),'i4'))
        supported=(evidence>=2)&(local>=4)
        # Grow an observed floor to nearby horizontal returns, including around
        # occluded edges. Disconnected returns cannot seed a second floor island.
        envelope=ndimage.binary_closing(old|supported,structure=np.ones((5,5)))|old|supported
        extension=ndimage.binary_propagation(old,mask=envelope)
        distance=ndimage.distance_transform_edt(~old,sampling=(np.mean(np.diff(u)),np.mean(np.diff(w))))
        extension &= (distance<1.35)&(ndimage.maximum_filter(supported,size=5)|old)
        updated=old|extension
        if upper:
            # The upper-floor scanner looked down the void from its landing. The
            # two banks of railing give its physical edges, including the threshold
            # where the last tread meets the landing.
            south=np.select([x<left,x<right,x<-7.98],[-9.10,-9.50,-9.447],default=-9.10)
            north=np.where((x>=left)&(x<-7.98),-6.058,-6.71)
            landing=(x>=-13.54)&(x<=-5.85)&(y>=south)&(y<=north)
            void_x=(x>=right)&(x<-7.98)
            southern_void=void_x&(y<-9.447)&(y>-15.65)
            northern_void=(x>=-10.20)&(x<-7.98)&(y>-6.058)&(y<-.27)
            stair_opening=(x>=left)&(x<right)&(y<-9.50)&(y>arch['steps'][0,0]-.5)
            updated=(updated|landing)&~(southern_void|northern_void|stair_opening)
        changed=updated&~old
        test_xyz=np.c_[x[changed],y[changed],height[changed]]
        probes.append(test_xyz)
        areas=np.diff(u)[:,None]*np.diff(w)[None,:]
        stats.append(dict(level=panel.name,added_area_m2=round(float(areas[changed].sum()),3),
                          cleared_opening_area_m2=round(float(areas[old&~updated].sum()),3),
                          added_cells=int(changed.sum())))
        panel.mask=updated
    np.save(work/'floor_probes.npy',np.vstack(probes))
    return stats


def corridor_columns(p,arch):
    """Fit both side returns and the forward face of each recurring wall pier."""
    floor=float(arch['steps'][-1,1])
    ceiling=float(np.median(arch['v'][arch['f'][arch['g']==4],2]))
    q=p[(p[:,0]>-.8)&(p[:,0]<32.)&(p[:,1]>-6.82)&(p[:,1]<-6.25)&
        (p[:,2]>floor+.30)&(p[:,2]<floor+2.03)]
    # The narrow sides appear as vertical planes in three independent height bands.
    xs=np.arange(-.8,32.01,.016)
    depths=np.arange(-6.81,-6.23,.014)
    hist=np.histogram2d(q[:,0],q[:,1],(xs,depths))[0]
    profile=ndimage.gaussian_filter(hist,(1.4,.9))
    front=depths[profile.argmax(1)]+.007
    baseline=ndimage.percentile_filter(front,84,size=187)
    peaks=[]
    for low in (floor+.32,floor+.87,floor+1.42):
        zq=q[(q[:,2]>=low)&(q[:,2]<low+.52)]
        side=zq[(zq[:,1]<-6.43)&(zq[:,1]>-6.66)]
        counts=np.histogram(side[:,0],xs)[0].astype(float)
        peaks.append(ndimage.gaussian_filter1d(counts,1.))
    # A flank can be occluded in one band. Require two independent flank
    # observations and independently require the front depth in all three.
    side_signal=np.median(peaks,axis=0)
    loc=find_peaks(side_signal,prominence=5.,distance=13)[0]
    columns=[];used=set()
    for a in loc:
        if a in used or (columns and xs[a]<columns[-1]['x1']):continue
        candidates=loc[(xs[loc]>xs[a]+.31)&(xs[loc]<xs[a]+.57)]
        if len(candidates)==0:continue
        z=int(candidates[np.argmax(side_signal[candidates])])
        inside=(q[:,0]>xs[a]+.06)&(q[:,0]<xs[z]-.05)
        votes=[]
        for low in (floor+.32,floor+.87,floor+1.42):
            sample=q[inside&(q[:,2]>low)&(q[:,2]<low+.52),1]
            freq=np.histogram(sample,depths)[0]
            votes.append(float(depths[np.argmax(freq)]+.007))
        forehead=float(np.median(votes));surround=float(np.median(baseline[a:z]))
        if max(votes)-min(votes)>.065 or surround-forehead<.125:continue
        if side_signal[a]<12 or side_signal[z]<12:continue
        x0=float(xs[a]+.008);x1=float(xs[z]+.008)
        # Extend the unseen rear into the registered wall to avoid a slot at the join.
        back=max(-6.38,surround+.025)
        columns.append(dict(x0=x0,x1=x1,front_y=forehead,back_y=back,
                            bottom=floor-.015,top=ceiling+.015))
        used.update((a,z))
    return columns


def clear_old_column_faces(parts,columns):
    """Remove the coarse overlapping facade cells replaced by each measured pier."""
    removed=0
    for part in parts:
        if part.group!=3 or not (part.name.startswith('Wand_') or part.name=='Zusatzfläche_gemessen'):
            continue
        center=(part.grid[:-1,:-1]+part.grid[1:,1:])*.5
        x,y,z=center.transpose(2,0,1)
        replaced=np.zeros(part.mask.shape,bool)
        if part.name=='Zusatzfläche_gemessen' and abs(part.normal[1])>.94 and columns:
            # RGB-D can merge adjacent pilaster fronts into a strip across
            # recesses. The measured wall and its fitted piers cover this bank.
            replaced|=(x>columns[0]['x0']-.2)&(x<columns[-1]['x1']+.2)&(y>-6.84)&(y< -6.50)&(z>columns[0]['bottom']-.08)&(z<columns[0]['top']+.08)
        for c in columns:
            flank=(abs(part.normal[0])>.85)&(np.minimum(abs(x-c['x0']),abs(x-c['x1']))<.12)
            front=(abs(part.normal[1])>.85)&(x>=c['x0']-.04)&(x<=c['x1']+.04)
            replaced|=(flank|front)&(y>=c['front_y']-.24)&(y<=-6.35)&(z>c['bottom']-.09)&(z<c['top']+.09)
        removed+=int((part.mask&replaced).sum())
        part.mask &= ~replaced
    return removed


def rail_segments(arch):
    cloud=np.load(ROOT/'mapped/outputs.npz')['registered_points']@arch['b']
    floor=float(arch['steps'][-1,1]);segments=[]
    # The stairs already have the sloping handrail. These five runs are its
    # measured continuation around the two landing openings.
    for ax,seed,lo,hi in [(1,-9.447,-10.60,-7.98),(0,-7.978,-15.7,-9.447),
                           (1,-6.058,-10.25,-7.98),(0,-7.978,-6.06,-.23),
                           (0,-10.578,-9.94,-9.447)]:
        along=1-ax
        band=cloud[(abs(cloud[:,ax]-seed)<.075)&(cloud[:,along]>=lo-.035)&(cloud[:,along]<=hi+.035)]
        stem=band[(band[:,2]>floor+.17)&(band[:,2]<floor+.79)]
        plane=float(np.median(stem[:,ax]))
        bins=np.arange(lo-.045,hi+.05,.008)
        sig=ndimage.gaussian_filter1d(np.histogram(stem[:,along],bins)[0].astype(float),1.05)
        peaks=find_peaks(sig,prominence=max(3.,np.percentile(sig,85)*.09),distance=10)[0]
        bars=[]
        for peak in peaks:
            t=bins[peak]+.004
            cluster=stem[abs(stem[:,along]-t)<.023]
            if len(cluster)<15 or np.sum(np.histogram(cluster[:,2],bins=np.linspace(floor+.17,floor+.79,7))[0]>1)<4:continue
            bars.append(float(np.median(cluster[:,along])))
        if len(bars)<3:raise ValueError('Insufficient measured railing support')
        top_band=band[(band[:,2]>floor+.77)&(band[:,2]<floor+1.11)]
        binsz=np.arange(floor+.77,floor+1.11,.01)
        zh=np.histogram(top_band[:,2],binsz)[0]
        handrail=float(binsz[ndimage.gaussian_filter1d(zh.astype(float),1.).argmax()]+.005)
        segments.append(dict(axis=ax,level=plane,lo=lo,hi=hi,posts=bars,floor=floor,handrail=handrail))
    return segments


def clear_guard_sheets(parts,segments):
    removed=0
    for part in parts:
        if part.group not in (3,4,5) or part.name.startswith('Glas_'):continue
        c=(part.grid[:-1,:-1]+part.grid[1:,1:])*.5
        block=np.zeros(part.mask.shape,bool)
        for s in segments:
            a=s['axis'];along=1-a
            if abs(part.normal[a])<.64:continue
            block|=(abs(c[:,:,a]-s['level'])<.23)&(c[:,:,along]>s['lo']-.04)&(c[:,:,along]<s['hi']+.04)&(c[:,:,2]>s['floor']-.04)&(c[:,:,2]<s['floor']+1.52)
        removed+=int((part.mask&block).sum());part.mask &= ~block
    return removed


def write_guard(work,segments,b):
    from fit_fine_mesh_railing import Tubes
    rods=Tubes()
    for s in segments:
        def point(t,z):
            q=np.zeros(3);q[s['axis']]=s['level'];q[1-s['axis']]=t;q[2]=z
            return q
        for t in s['posts']:
            rods.rod(point(t,s['floor']-.035),point(t,s['handrail']),.014,np.array([42,48,49]),8)
        # Tubes.rod uses a reference transverse to the rod; model horizontal
        # members in a local Y direction before rotating them onto either axis.
        temp=Tubes();temp.rod([0,0,0],[0,s['hi']-s['lo'],0],.026,np.array([61,65,63]),12)
        vertices=np.asarray(temp.verts)
        if s['axis']==1:vertices=np.c_[vertices[:,1],-vertices[:,0],vertices[:,2]]
        vertices+=point(s['lo'],s['handrail'])
        rods.verts.extend(vertices);rods.faces.extend(np.asarray(temp.faces)+rods.n)
        rods.colors.extend(temp.colors);rods.n+=len(vertices)
    old=np.load(FINE/'rail.npz')
    np.savez(work/'rail.npz',v=np.vstack((old['v'],np.asarray(rods.verts)@b.T)).astype('f4'),
             f=np.vstack((old['f'],np.asarray(rods.faces)+len(old['v']))).astype('i4'),
             color=np.vstack((old['color'],rods.colors)).astype('u1'))


def add_column_geometry(columns,b,vs,fs,groups,tile_ids,uvs,colors,tiles,count):
    for c in columns:
        footprint=np.array([[c['x0'],c['front_y']],[c['x1'],c['front_y']],
                            [c['x1'],c['back_y']],[c['x0'],c['back_y']]])
        vertices=np.vstack((np.c_[footprint,np.full(4,c['bottom'])],np.c_[footprint,np.full(4,c['top'])]))@b.T
        faces=[];labels=[];coords=[]
        for i in range(4):
            j=(i+1)%4;index=np.array([i,j,j+4,i+4])
            tile_grid=vertices[index[[0,3,1,2]]].reshape(2,2,3).astype('f4')
            width=int(np.ceil(np.linalg.norm(vertices[j]-vertices[i])*210))
            tile=len(tiles);tiles.append((tile_grid,width,round((c['top']-c['bottom'])*210),3,'Säule'))
            faces.extend([index[[0,1,2]],index[[0,2,3]]]);labels.extend([tile,tile])
            coords.extend([[[0,0],[1,0],[1,1]],[[0,0],[1,1],[0,1]]])
        faces.extend([[0,2,1],[0,3,2],[4,5,6],[4,6,7]]);labels.extend([-1]*4);coords.extend(np.zeros((4,3,2)))
        ff=np.asarray(faces);edges=np.sort(ff[:,[0,1,1,2,2,0]].reshape(-1,2),axis=1)
        if not np.all(np.unique(edges,axis=0,return_counts=True)[1]==2):raise ValueError('Open pier')
        vs.append(vertices.astype('f4'));fs.append(ff+count);count+=8
        groups.append(np.full(len(ff),3,'i4'));tile_ids.append(np.asarray(labels,'i4'))
        uvs.append(np.asarray(coords,'f4'));colors.append(np.tile([165,167,165],(8,1)))
    return count
