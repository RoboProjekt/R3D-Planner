import unittest
from types import SimpleNamespace

import numpy as np

from filter_surface_evidence import camera_votes, filter_patches, lidar_votes, open_post_gaps


class SurfaceEvidenceTest(unittest.TestCase):
    def test_repeat_frames_occlusion_and_person_mask(self):
        poses=np.tile(np.eye(4),(6,1,1))
        poses[-1,0,3]=.75
        intrinsics=np.array([[10.,0,10.],[0,10.,10.],[0,0,1.]])
        xyz=np.array([[0.,0.,2.]])
        normal=np.array([[0.,0.,1.]])
        depth=np.full((6,21,21),3100,np.uint16)
        blocked=np.zeros_like(depth,bool)
        agree,free=camera_votes(xyz,normal,poses,intrinsics,depth,blocked)
        self.assertEqual((agree[0],free[0]),(0,2))
        blocked[-1]=True
        depth[:5]=1400
        agree,free=camera_votes(xyz,normal,poses,intrinsics,depth,blocked)
        self.assertEqual((agree[0],free[0]),(0,0))

    def test_ray_votes_survive_changed_map_origin_and_heading(self):
        x, z = np.meshgrid(np.arange(6)*.14, np.arange(6)*.14, indexing='ij')
        grid = np.stack([x, np.zeros_like(x), z],axis=-1)
        u, v = np.meshgrid(np.arange(.017,.70,.033),np.arange(.017,.70,.033))
        targets = np.c_[u.ravel(),np.zeros(u.size),v.ravel()]
        sources = np.array([[.1,-2,.2],[.9,-1.7,.4],[-.5,-2.2,.5]])
        origins = np.repeat(sources,len(targets),axis=0)
        plane = np.tile(targets,(len(sources),1))
        end = origins + (plane-origins)*np.where(plane[:,0,None]>.28,1.5,1.)
        station = np.repeat(np.arange(len(sources)),len(targets))
        for angle,offset in [(0,np.zeros(3)),(.84,np.array([13.,21.,4.5]))]:
            c,s=np.cos(angle),np.sin(angle)
            rot=np.array([[c,-s,0],[s,c,0],[0,0,1.]])
            l,q,f,p=lidar_votes(grid@rot+offset,origins@rot+offset,end@rot+offset,station,
                                np.linalg.norm(end-origins,axis=1))
            patch=SimpleNamespace(name='candidate',mask=np.ones(l.shape,bool))
            evidence=dict(lidar=l,cover=q,free=f,pass_cover=p,rgb=l*0,rgb_free=f*0,aligned=(l>0)*12)
            filter_patches([patch],[evidence],[False])
            self.assertTrue(patch.mask[:2].all())
            self.assertFalse(patch.mask[2:].any())

    def test_railing_does_not_carve_a_wall_behind_it(self):
        u,z=np.meshgrid(np.arange(7)*.10,np.arange(8)*.10,indexing='ij')
        grid=np.stack([u,np.zeros_like(u),z],axis=-1)
        rail=SimpleNamespace(grid=grid,mask=np.ones((6,7),bool),normal=np.array([0,1,0]))
        wall=SimpleNamespace(grid=grid+[0,.26,0],mask=rail.mask.copy(),normal=rail.normal)
        posts=np.array([[i*.10,0,0,.70] for i in range(7)])
        pairs=np.stack([posts[:-1],posts[1:]],axis=1)
        open_post_gaps([rail,wall],pairs)
        self.assertFalse(rail.mask.any())
        self.assertTrue(wall.mask.all())


if __name__=='__main__':
    unittest.main()
