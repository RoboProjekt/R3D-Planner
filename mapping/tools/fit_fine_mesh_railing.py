"""Fit the observed metal bars and handrails of the staircase to LiDAR cross sections."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from scipy.signal import find_peaks

from fuse_lyra_lidar import read_pcd, BASE, xyz


class Tubes:
    def __init__(self):
        self.verts=[];self.faces=[];self.colors=[];self.n=0
    def rod(self,start,end,radius,rgb,sides):
        start,end=np.asarray(start),np.asarray(end)
        d=end-start;d=d/np.linalg.norm(d)
        u=np.cross(d,[1.,0.,0.]);u/=np.linalg.norm(u);v=np.cross(d,u)
        t=2*np.pi*np.arange(sides)/sides
        circle=radius*(np.cos(t)[:,None]*u+np.sin(t)[:,None]*v)
        self.verts.extend(np.r_[circle+start,circle+end])
        # Retain a little cylindrical shading even for renderers showing baked colours.
        shade=.85+.15*(.5+.5*np.cos(t))
        cs=np.rint(shade[:,None]*rgb).clip(0,255)
        self.colors.extend(np.r_[cs,cs])
        for i in range(sides):
            j=(i+1)%sides
            self.faces.extend([[self.n+i,self.n+j,self.n+sides+j],[self.n+i,self.n+sides+j,self.n+sides+i]])
        for i in range(1,sides-1):
            self.faces.extend([[self.n,self.n+i+1,self.n+i],[self.n+sides,self.n+sides+i,self.n+sides+i+1]])
        self.n+=2*sides


def railing(work, architecture='.runtime/isaac_building/building/scene.npz',
            measured_cloud=Path('reports/20261123_kamerakarte/karte_rgb.pcd')):
    a=np.load(architecture)
    s=a['steps'];left,right,low=a['stair_bounds']
    cloud=read_pcd(measured_cloud,BASE)
    points=xyz(cloud)@a['b']
    stage=(points[:,1]>-17.8)&(points[:,1]<-9.6)&(points[:,0]>left-.25)&(points[:,0]<right+.35)
    x,y,z=points[stage].T;rgb=cloud['rgb'][stage].view('u4')
    col=np.column_stack([(rgb>>shift)&255 for shift in (16,8,0)]);colored=cloud['views'][stage]>0
    # Three adjoining line segments follow the lower flight, landing and upper flight.
    breaks=np.array([s[0,0]-.10,s[5,0]+.10,s[6,0]-.17,s[-1,0]+.10])
    base=np.interp(breaks,s[:,0],s[:,1]);base[0]-=.05;base[2]=base[1]
    def height(y):return np.interp(y,breaks,base)
    dz=z-height(y)
    rods=Tubes();count=0;observations=[]
    def shade(mask,quantile,default):
        pixels=col[mask&colored]
        return np.quantile(pixels,quantile,axis=0) if len(pixels)>8 else np.array(default)
    rails=[[],[],[]];rail_colors=[[],[],[]]
    for j,(lo,hi) in enumerate(zip(breaks,breaks[1:])):
        section=(y>=lo)&(y<hi)
        # Each candidate peak must be supported at multiple different heights.
        bars=section&(abs(x-right)<.048)&(dz>.13)&(dz<.73)
        bins=np.arange(lo,hi+.008,.008);h=np.histogram(y[bars],bins)[0]
        smooth=gaussian_filter1d(h.astype(float),1.)
        peaks,_=find_peaks(smooth,prominence=max(3.,np.percentile(smooth,80)*.16),distance=10)
        near=section&(abs(x-right)<.05)&(dz>.76)&(dz<1.18)
        top=float(np.percentile(dz[near],90))
        for peak in peaks:
            py=bins[peak]+.004
            narrow=bars&(abs(y-py)<.021)
            if narrow.sum()<15 or (np.histogram(dz[narrow],np.linspace(.13,.73,7))[0]>1).sum()<4:continue
            px=float(np.median(x[narrow]));py=float(np.median(y[narrow]))
            foot=np.r_[low,s[:,1]][np.searchsorted(s[:,0],py,side='right')]
            radius=np.clip((np.percentile(y[narrow],86)-np.percentile(y[narrow],14))*.62,.010,.018)
            rods.rod([px,py,foot-.025],[px,py,height(py)+top],radius,shade(narrow,.25,[33,35,35]),8)
            count+=1
        # Determine the two graspable rails by peaks in horizontal offset and height.
        for n,(x0,x1) in enumerate(((left+.075,left+.165),(right-.165,right-.075))):
            near=section&(x>x0)&(x<x1)&(dz>.76)&(dz<.96)
            hist,xe,ze=np.histogram2d(x[near],dz[near],bins=(19,30),range=((x0,x1),(.76,.96)))
            i,k=np.unravel_index(gaussian_filter(hist,1.4).argmax(),hist.shape)
            cx=(xe[i]+xe[i+1])*.5;cz=(ze[k]+ze[k+1])*.5
            supported=near&(abs(x-cx)<.035)&(abs(dz-cz)<.054)
            if supported.sum()<15:raise ValueError('Unconfirmed handrail section')
            rails[n].append((cx,cz));rail_colors[n].append(shade(supported,.73,[169,170,166]))
            observations.append(int(supported.sum()))
        rails[2].append((float(np.median(x[section&(abs(x-right)<.05)])),top))
        rail_colors[2].append(shade(bars,.28,[40,42,40]))
    for i,sections in enumerate(rails):
        anchors=np.array([sections[0],*((np.array(sections[:-1])+np.array(sections[1:]))*.5),sections[-1]])
        track=np.column_stack((anchors[:,0],breaks,base+anchors[:,1]))
        for j in range(len(track)-1):rods.rod(track[j],track[j+1],.022 if i<2 else .016,rail_colors[i][j],14)
    with np.load(work/'surface.npz') as mesh:v,f=mesh['v'],mesh['f']
    corr=np.load(work/'correspondence.npz');count_arch=len(corr['arch_ids'])
    ff=f[:-count_arch]
    center=np.vstack([v[chunk].mean(1) for chunk in np.array_split(ff,40)])
    mx,my,mz=(center@a['b']).T;mh=mz-height(my)
    affected=(my>=breaks[0])&(my<=breaks[-1])&(mh>-.16)&(mh<1.23)
    right_side=(mx>right-.24)&(mx<right+.19)
    left_rail=(mx>left+.035)&(mx<left+.20)&(mh>.58)&(mh<1.13)
    keep=~(affected&(right_side|left_rail))
    rv=(np.array(rods.verts)@a['b'].T).astype('f4')
    rf=np.asarray(rods.faces,'i4')
    begin=int(keep.sum())
    np.savez(work/'rail.npz',v=rv,f=rf,color=np.array(rods.colors,'u1'),
             start_face=begin,stop_face=begin+len(rf),start_vertex=len(v))
    np.savez(work/'surface.npz',v=np.r_[v,rv],f=np.r_[ff[keep],rf+len(v),f[-count_arch:]])
    summary=json.loads((work/'surface.json').read_text())
    summary.update(rail_pickets=count,rail_vertices=len(rv),rail_triangles=len(rf),
                   rail_physical_contact='static triangle mesh',handrail_support_counts=observations,
                   vertices=len(v)+len(rv),triangles=begin+len(rf)+count_arch)
    (work/'surface.json').write_text(json.dumps(summary,indent=2))
    print(summary,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('work',type=Path);railing(p.parse_args().work)
