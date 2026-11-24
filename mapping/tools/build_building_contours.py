"""Construct solid architectural parts in the metric frame of the recorded route."""
from dataclasses import dataclass
import json
from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

from clean_building_photos import ROOT, FINE, JOB
from complete_building_walls import measured_rays

OUT=ROOT/'contours_evidence'


@dataclass
class Panel:
    name: str
    group: int
    grid: np.ndarray
    mask: np.ndarray
    normal: np.ndarray
    thickness: float


def grid(axis,level,u,w):
    first,second=[i for i in range(3) if i!=axis]
    points=np.empty((len(u),len(w),3))
    points[:,:,axis]=level
    points[:,:,first]=u[:,None]
    points[:,:,second]=w[None,:]
    return points


def spans(lo,hi,step):
    return np.linspace(lo,hi,max(1,round((hi-lo)/step))+1)


def histogram(points,u,w):
    return np.histogram2d(points[:,0],points[:,1],bins=(u,w))[0]


def components(mask,minimum):
    labels,n=ndimage.label(mask)
    sizes=np.bincount(labels.ravel(),minlength=n+1)
    sizes[0]=0
    return sizes[labels]>=minimum


def crossing(orig,delta,axis,level,u,w):
    start=orig[:,axis]-level;end=start+delta[:,axis]
    beyond=(start*end<0)&(abs(end)>.32)&(abs(start)>.25)
    src=orig[beyond];d=delta[beyond]
    hit=src+d*((level-src[:,axis])/d[:,axis])[:,None]
    return histogram(np.delete(hit,axis,axis=1),u,w)


def add_plane(parts,name,group,axis,level,u,w,mask,normal,thickness):
    if mask.any():
        parts.append(Panel(name,group,grid(axis,level,u,w).astype('f4'),mask,np.array(normal,dtype='f4'),thickness))


def rectangular(parts,name,group,axis,level,ul,ur,wl,wr,sign,thickness):
    u,w=spans(ul,ur,.14),spans(wl,wr,.14)
    normal=np.eye(3)[axis]*sign
    add_plane(parts,name,group,axis,level,u,w,np.ones((len(u)-1,len(w)-1),bool),normal,thickness)


def generic_walls(parts,p,v,f,g,tr,orig,delta,arch):
    tri=v[f[g==3]];cent=tri.mean(1)
    norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);axes=abs(norm).argmax(1)
    pos=np.round(cent[np.arange(len(cent)),axes],2)
    left,right,_=arch['stair_bounds'];steps=arch['steps'];top=steps[-1,1]
    route=cKDTree(tr/[.58,.58,.65])
    for axis,level in sorted(set(zip(axes,pos))):
        which=(axes==axis)&(pos==level);s=tri[which]
        if axis==2 or len(s)<65:continue
        level=float(np.median(cent[which,axis]));a=1-axis
        lo=s.min((0,1));hi=s.max((0,1))
        if hi[a]-lo[a]<.50 or hi[2]-lo[2]<.7:continue
        u=spans(lo[a]-.04,hi[a]+.04,.14);w=spans(lo[2]-.04,hi[2]+.04,.14)
        pts=p[abs(p[:,axis]-level)<.102]
        occ=histogram(pts[:,[a,2]],u,w)
        samples=np.concatenate([s.mean(1)]+[.72*s[:,j]+.14*s[:,(j+1)%3]+.14*s[:,(j+2)%3] for j in range(3)])
        old=histogram(samples[:,[a,2]],u,w)>0
        # The shell must be supported by a substantial, spatially contiguous wall.
        support=ndimage.gaussian_filter(occ,.82)
        seen=(support>1.5)&ndimage.maximum_filter(old,size=9)
        shell=ndimage.binary_closing(seen|old,structure=np.ones((5,7)))
        shell |= seen
        free=ndimage.gaussian_filter(crossing(orig,delta,axis,level,u,w),.8)
        opening=(free>1.9)&(free>support*.82)
        shell=ndimage.binary_fill_holes(shell)&~components(opening,7)
        X,Z=np.meshgrid((u[:-1]+u[1:])*.5,(w[:-1]+w[1:])*.5,indexing='ij')
        # The enclosed corridor below has fitted walls, jambs and glazing of its own.
        if axis==1 and min(abs(level+9.1),abs(level+6.42))<.55:
            shell &= ~((X>=-5.9)&(X<=32.55)&(Z>=top-.06)&(Z<5.15))
        if axis==0 and abs(level-right)<.46:
            tread=np.r_[arch['stair_bounds'][2],steps[:,1]][np.searchsorted(steps[:,0],X,side='right')]
            shell &= ~((X>=steps[0,0]-.55)&(X<=steps[-1,0]+.7)&(Z>tread-.18)&(Z<tread+2.65))
        q=grid(axis,level,(u[:-1]+u[1:])*.5,(w[:-1]+w[1:])*.5)
        route_distance=route.query(q.reshape(-1,3)/[.58,.58,.65],workers=4)[0].reshape(shell.shape)
        shell &= route_distance>1.
        shell=components(shell,45)
        normal=np.eye(3)[axis]
        if len(tr) and np.median(tr[:,axis])<level:normal=-normal
        add_plane(parts,f'Wand_{axis}_{level:.2f}',3,axis,level,u,w,shell,normal,.075)


def floors(parts,p,cv,cf,cg,tr,orig,delta,arch):
    steps=arch['steps'];left,right,low=arch['stair_bounds']
    for group,name in ((0,'Boden_EG'),(1,'Boden_1OG'),(4,'Decke_Flur')):
        tri=cv[cf[cg==group]];mid=tri.mean(1)
        lo=tri.min((0,1));hi=tri.max((0,1))
        u,w=spans(lo[0],hi[0],.135),spans(lo[1],hi[1],.135)
        if group==4:
            # Fit the enclosed hallway between the two measured side walls.
            level=float(np.median(mid[:,2]));u=spans(-5.88,32.57,.135);w=spans(-9.14,-6.4,.135)
            q=grid(2,level,u,w);mask=np.ones((len(u)-1,len(w)-1),bool)
        else:
            level=steps[-1,1] if group==1 else float(np.median(mid[:,2]))
            samples=np.concatenate([mid]+[.7*tri[:,j]+.15*tri[:,(j+1)%3]+.15*tri[:,(j+2)%3] for j in range(3)])
            old=histogram(samples[:,:2],u,w)>0
            mask=ndimage.binary_closing(old,structure=np.ones((7,7)))|old
            mask=ndimage.binary_fill_holes(mask)
            q=grid(2,level,u,w)
            if group==0:
                nb=cKDTree(mid[:,:2]).query(q[:,:,:2].reshape(-1,2),k=12,workers=4)[1]
                q[:,:,2]=ndimage.gaussian_filter(np.median(mid[nb,2],axis=1).reshape(q.shape[:2]),1)
            else:
                surface=histogram(p[abs(p[:,2]-level)<.10,:2],u,w)
                free=crossing(orig,delta,2,float(level),u,w)
                opened=(ndimage.gaussian_filter(free,.85)>2)&(ndimage.gaussian_filter(free,.85)>ndimage.gaussian_filter(surface,.85)*1.25)
                mask &= ~components(opened,7)
            X,Y=np.meshgrid((u[:-1]+u[1:])*.5,(w[:-1]+w[1:])*.5,indexing='ij')
            if group==1:
                mask |= (X>=-5.85)&(X<=32.58)&(Y>=-9.14)&(Y<=-6.4)
                mask &= ~((X>left-.035)&(X<right+.035)&(Y>steps[0,0]-.48)&(Y<steps[-1,0]+.22))
            if group==0:
                # Keep the lower landing level with the first nosing.
                equal=(q[:,:,0]>left-.10)&(q[:,:,0]<right+.10)&(abs(q[:,:,1]-steps[0,0])<.76)
                q[:,:,2][equal]=low
            mask=components(mask,45)
        parts.append(Panel(name,group,q.astype('f4'),mask,np.array([0,0,-1 if group==4 else 1],'f4'),.10))


def hallway(parts,p,orig,delta,arch,report):
    floor=arch['steps'][-1,1];ceiling=float(np.median(arch['v'][arch['f'][arch['g']==4],2]))
    doors=[]
    for level,side in ((-6.41,1),(-9.10,-1)):
        xl,xr=(-5.90,32.58);u=spans(xl,xr,.055);w=spans(floor,ceiling,.065)
        xs=(u[:-1]+u[1:])*.5;zs=(w[:-1]+w[1:])*.5
        depth=(p[:,1]-level)*side
        measured=p[abs(depth)<.11]
        surface=ndimage.gaussian_filter(histogram(measured[:,[0,2]],u,w),1.1)
        passed=ndimage.gaussian_filter(crossing(orig,delta,1,level,u,w),1.25)
        free=(passed>1)&(passed>surface*.92)
        mask=np.ones_like(free,bool)
        # Any broad floor-connected opening is preserved across its full observed width.
        lower=(zs>floor+.13)&(zs<floor+1.55);widths=ndimage.binary_closing(free[:,lower].mean(1)>.49,structure=np.ones(4))
        lab,_=ndimage.label(widths)
        for span in ndimage.find_objects(lab):
            if span is None:continue
            a=span[0].start;b=span[0].stop
            if u[b]-u[a]<.46:continue
            clear=free[a:b].mean(0)>.30
            high=np.flatnonzero(clear&(zs<floor+2.34))
            if len(high):
                top=min(ceiling,w[high[-1]+1]+.04)
                face_counts=histogram(measured[:,[0,2]],u,w)[a:b].sum(0)
                lintel=np.flatnonzero((zs>floor+1.78)&(zs<floor+2.40)&(ndimage.gaussian_filter1d(face_counts.astype(float),1.)>5))
                if len(lintel) and top<floor+1.78:
                    top=w[lintel[0]]
                mask[a:b,zs<top]=False
                doors.append(dict(kind='measured_opening',wall_y=float(level),start_x=float(u[a]),end_x=float(u[b]),height=float(top-floor)))
        # Recesses in the opaque wall have a depth peak from well above the skirting
        # to shoulder height; a genuine open doorway has no such back surface.
        dense=(p[:,2]>floor+.22)&(p[:,2]<floor+1.60)
        depth_bins=np.arange(-.28,.57,.025)
        h=np.histogram2d(p[dense,0],depth[dense],bins=(u,depth_bins))[0]
        sh=ndimage.gaussian_filter(h,(2.0,1.0));offset=depth_bins[sh.argmax(1)]+.0125
        embedded=(offset>.085)&(offset<.34)&(sh.max(1)>2.0)&(xs>-1.2)
        lab,_=ndimage.label(ndimage.binary_closing(embedded,structure=np.ones(4)))
        for span in ndimage.find_objects(lab):
            if span is None:continue
            a,b=span[0].start,span[0].stop;wide=u[b]-u[a]
            if not .62<wide<1.65:continue
            inside=(p[:,0]>u[a]+.09)&(p[:,0]<u[b]-.09)
            inset=float(np.median(offset[a:b]))
            dels=depth[inside];heights=p[inside,2]
            edges=spans(floor+.15,ceiling,.055)
            back=np.histogram(heights[abs(dels-inset)<.047],edges)[0]
            front=np.histogram(heights[abs(dels)<.045],edges)[0]
            credible=(back>=3)&(back>front*.65)
            upper=np.flatnonzero(credible&(edges[:-1]>floor+1.68))
            if len(upper)==0:continue
            top=min(ceiling-.04,edges[upper[-1]+1])
            if not 1.72<top-floor<2.46:continue
            mask[a:b,zs<top]=False
            back_y=level+side*inset
            rectangular(parts,'Türblatt',5,1,back_y,u[a],u[b],floor,top,-side,.035)
            for edge,sign in [(u[a],1),(u[b],-1)]:
                rectangular(parts,'Türlaibung',5,0,edge,min(level,back_y),max(level,back_y),floor,top,sign,.025)
            rectangular(parts,'Türsturz',5,2,top,u[a],u[b],min(level,back_y),max(level,back_y),-1,.028)
            doors.append(dict(kind='measured_recess',wall_y=float(level),start_x=float(u[a]),end_x=float(u[b]),height=float(top-floor),depth=inset))
        # The glazed bank in the recorded corridor has a continuous sill, regular
        # mullions and an opaque parapet. Never use this rule outside that window bank.
        if side<0:
            bank=(xs>2.65)&(xs<21.70)
            mask[bank,:]=True
        # Adapt to the offset of the wall segment beside the open first-floor landing.
        q=grid(1,level,u,w)
        if side>0:
            q[:,:,1]+=np.where(u<-1.15,-.26,0)[:,None]
        parts.append(Panel('Flurwand_Fenster' if side<0 else 'Flurwand_Türen',3,q.astype('f4'),mask,np.array([0,-side,0],'f4'),.07))
    report['door_and_passage_measurements']=doors


def extra_ceilings(parts,p,orig,delta,track):
    # Only locally supported overhead patches, with a measured return on the same
    # horizontal plane. Rays through the open atrium veto any slab over the void.
    for level in (2.85,4.96,5.68):
        near=p[abs(p[:,2]-level)<.09]
        if len(near)<200:continue
        u=spans(-16.5,3.,.16);w=spans(-23.,2.5,.16)
        hits=histogram(near[:,:2],u,w);s=ndimage.gaussian_filter(hits,1.)
        free=ndimage.gaussian_filter(crossing(orig,delta,2,level,u,w),1.)
        mask=ndimage.binary_closing(s>1.8,structure=np.ones((5,5)))
        mask=ndimage.binary_fill_holes(mask)&~((free>1.6)&(free>s*.75))
        X,Y=np.meshgrid((u[:-1]+u[1:])/2,(w[:-1]+w[1:])/2,indexing='ij')
        if abs(level-4.96)<.02:
            mask &=~((X>-5.95)&(Y>-9.24)&(Y<-6.35))
        below=track[(track[:,2]>level-1.45)&(track[:,2]<level+.65)]
        if len(below):
            distance=cKDTree(below[:,:2]).query(np.c_[X.ravel(),Y.ravel()])[0].reshape(X.shape)
            mask &= distance>2.0
        # A line of wall returns in an elevation slice is not a ceiling.
        core=ndimage.binary_opening(mask,structure=np.ones((5,5)))
        mask &= ndimage.maximum_filter(core,size=7)
        add_plane(parts,'Decke_gemessen',4,2,level,u,w,components(mask,55),[0,0,-1],.08)


def fit_other_doorways(parts,p,report):
    """Find recessed door-sized panels supported by jambs, a lintel and a measured slab."""
    slab_parts=[part for part in parts if part.group in (0,1)]
    floor_xyz=np.vstack([((s.grid[:-1,:-1]+s.grid[1:,1:])/2)[s.mask] for s in slab_parts])
    fitted=[]
    for wall in list(parts):
        if not wall.name.startswith('Wand_'):continue
        axis=int(np.argmax(abs(wall.normal)));along=1-axis;level=wall.grid[0,0,axis]
        u=wall.grid[:,0,along];z=wall.grid[0,:,2]
        if u[-1]-u[0]<1.6:continue
        near=p[(abs(p[:,axis]-level)<.42)&(p[:,along]>u[0]-.1)&(p[:,along]<u[-1]+.1)]
        soil=floor_xyz[abs(floor_xyz[:,axis]-level)<.48]
        for base in (-.65,2.43):
            floors=soil[abs(soil[:,2]-base)<.55]
            if not len(floors):continue
            flevel=float(np.median(floors[:,2]))
            if z[-1]<flevel+1.95 or z[0]>flevel+.44:continue
            e=spans(float(u[0]),float(u[-1]),.08)
            d=near[:,axis]-level
            face=abs(d)<.055
            for sign in (1,-1):
                back=(d*sign>.09)&(d*sign<.34)
                supported=np.ones(len(e)-1,bool)
                for lo,hi in ((.24,.80),(.85,1.42),(1.45,1.85)):
                    h=(near[:,2]>flevel+lo)&(near[:,2]<flevel+hi)
                    n=np.histogram(near[h&back,along],e)[0];front=np.histogram(near[h&face,along],e)[0]
                    supported &= (ndimage.gaussian_filter1d(n.astype(float),1)>3)&(n>front*.9)
                lab,_=ndimage.label(ndimage.binary_closing(supported,structure=np.ones(3)))
                for piece in ndimage.find_objects(lab):
                    if piece is None:continue
                    a,b=e[piece[0].start],e[piece[0].stop]
                    if not .68<b-a<1.55 or np.min(abs(floors[:,along]-(a+b)*.5))>.65:continue
                    span=(near[:,along]>a+.07)&(near[:,along]<b-.07)
                    high=np.arange(flevel+1.82,min(flevel+2.44,z[-1]),.06)
                    if len(high)<3:continue
                    n=np.histogram(near[span&face,2],high)[0]
                    lintel=np.flatnonzero(n>=4)
                    if not len(lintel):continue
                    top=float(high[lintel[0]])
                    sides=(near[:,2]>flevel+.5)&(near[:,2]<top-.2)&face
                    if min(np.sum(sides&(abs(near[:,along]-edge)<.17)) for edge in (a,b))<14:continue
                    backdepth=d[span&back&(near[:,2]>flevel+.3)&(near[:,2]<top-.15)]
                    if len(backdepth)<45:continue
                    recess=float(np.median(backdepth))
                    pos=np.zeros(3);pos[axis]=level;pos[along]=(a+b)*.5;pos[2]=flevel+1
                    if any(np.linalg.norm(pos-q)<.48 for q in fitted):continue
                    column=(u[:-1]+u[1:])*.5;row=(z[:-1]+z[1:])*.5
                    affected=(column[:,None]>=a)&(column[:,None]<=b)&(row[None,:]>=flevel-.05)&(row[None,:]<=top)
                    if not affected.any() or (wall.mask&affected).sum()<affected.sum()*.33:continue
                    wall.mask &= ~affected
                    # Snap all stone/door edges to the actual shell grid so the jamb has no slit.
                    cols=np.flatnonzero(affected.any(1));rows=np.flatnonzero(affected.any(0))
                    a,b=float(u[cols[0]]),float(u[cols[-1]+1]);top=float(z[rows[-1]+1])
                    bottom=min(float(flevel),float(z[rows[0]]));end=float(level+recess)
                    rectangular(parts,'Türblatt',5,axis,end,a,b,bottom,top,-sign,.032)
                    for loc,sgn in ((a,1),(b,-1)):
                        rectangular(parts,'Türlaibung',5,along,loc,min(end,level),max(end,level),bottom,top,sgn,.027)
                    bounds=(min(level,end),max(level,end),a,b) if axis==0 else (a,b,min(level,end),max(level,end))
                    rectangular(parts,'Türsturz',5,2,top,*bounds,-1,.027)
                    fitted.append(pos)
                    report['door_and_passage_measurements'].append(dict(kind='measured_recess',axis=axis,plane=float(level),start=float(a),end=float(b),floor_z=bottom,height=round(top-bottom,3),depth=round(abs(recess),3)))


def stair(parts,arch):
    left,right,low=arch['stair_bounds'];s=arch['steps']
    rows=[(s[0,0]-.53,low),(s[0,0],low)]
    for i,(y,z) in enumerate(s):
        rows.extend([(y,z),(s[i+1,0] if i+1<len(s) else y+.54,z)])
    # An uninterrupted folded sheet with explicit tread and vertical riser edges.
    u=spans(left,right,.12);poly=[]
    for a,b in zip(rows[:-1],rows[1:]):
        a=np.array(a);b=np.array(b)
        poly.extend(a+(b-a)*float(t) for t in np.linspace(0,1,max(1,round(np.linalg.norm(b-a)/.10))+1)[:-1])
    poly=np.vstack([*poly,rows[-1]]);q=np.empty((len(u),len(poly),3),'f4')
    q[:,:,0]=u[:,None];q[:,:,1:]=poly
    parts.append(Panel('Treppe',2,q,np.ones((len(u)-1,len(poly)-1),bool),np.array([0,-.3,1.],'f4'),.14))


def bounded_glazing_and_soffits(parts,report):
    # These contours were picked at the frame edges in calibrated photographs.
    # The entrance header and foot agree in frames 138 and 151; the upper landing
    # and the return around the atrium can also be seen from frames 296, 376, 398.
    # Keep the rectangular opening above the stairs and the adjoining atrium clear.
    surfaces=[
        ('Glas_Eingang',5,1,-21.015,-12.10,-6.24,-1.16,2.43,1,.027),
        ('Glas_Aufzug',5,1,-6.055,-12.10,-10.53,2.428,5.64,-1,.025),
        ('Glas_Podest_Seite',5,0,-13.54,-9.12,-6.71,2.428,4.94,1,.026),
        ('Glas_Flurabschluss',5,0,32.95,-9.12,-6.41,2.428,4.95,-1,.032),
        ('Decke_Eingang',4,2,2.425,-12.10,-6.19,-21.02,-18.01,-1,.105),
        ('Deckenrand_EG',4,2,2.425,-8.00,-6.17,-18.01,-12.20,-1,.105),
        ('Deckenrand_Treppe',4,2,5.685,-12.13,-10.54,-17.60,-9.27,-1,.095),
        ('Decke_Podest',4,2,5.685,-12.13,-6.12,-9.27,-6.04,-1,.095),
    ]
    for name,group,axis,level,ul,ur,wl,wr,sign,thickness in surfaces:
        dims=[d for d in range(3) if d!=axis]
        for part in parts:
            if abs(part.normal[axis])<.80:continue
            center=(part.grid[:-1,:-1]+part.grid[1:,1:])*.5
            coord=center[:,:,axis]
            # Remove only the old plane skin, retaining glass jambs in front of it.
            same=(abs(coord-level)<(.105 if group==4 else .092))&(center[:,:,dims[0]]>ul)&(center[:,:,dims[0]]<ur)&(center[:,:,dims[1]]>wl)&(center[:,:,dims[1]]<wr)
            part.mask &= ~same
        rectangular(parts,name,group,axis,level,ul,ur,wl,wr,sign,thickness)
    report['photo_confirmed_glazed_assemblies']=4
    report['soffit_reference_training_images']=[138,151,296,376,398]


def prepare():
    OUT.mkdir(exist_ok=True);arch=np.load(ROOT/'architecture/scene.npz');b=arch['b']
    col=np.load(JOB/'collision.npz');v=col['v']@b;f,g=col['f'],col['g']
    with (ROOT/'mapped/measured.pcd').open('rb') as stream:
        while stream.readline()!=b'DATA binary\n':pass
        p=np.fromfile(stream,'<f4').reshape(-1,3)@b
    orig,end=measured_rays(b);delta=end-orig;tr=arch['trajectory'][:,1:4]@b
    parts=[];report={}
    floors(parts,p,v,f,g,tr,orig,delta,arch)
    generic_walls(parts,p,v,f,g,tr,orig,delta,arch)
    hallway(parts,p,orig,delta,arch,report);fit_other_doorways(parts,p,report);extra_ceilings(parts,p,orig,delta,tr);stair(parts,arch)
    bounded_glazing_and_soffits(parts,report)
    from repair_floors_and_pillars import complete_floors, corridor_columns
    report['floor_repairs']=complete_floors(parts,p,arch,OUT)
    report['solid_columns']=corridor_columns(p,arch)
    return parts,b,report
