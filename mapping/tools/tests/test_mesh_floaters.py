import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from filter_mesh_floaters import floater_mask
from mesh_depth_guard import visible_surface_guard


def square(center, side):
    offsets=np.array([[-1,-1,0],[1,-1,0],[1,1,0],[-1,1,0]],'f4')
    return np.asarray(center,'f4') + offsets*(side/2)


class FloaterFilterTest(unittest.TestCase):
    def test_supported_small_objects_and_seams_survive(self):
        # A small unsupported island, an observed object, an architectural feature,
        # a handrail and an unconnected tessellation patch next to the large floor.
        centers=[(0,0,0),(.4,0,.5),(-.4,0,.5),(0,.4,.5),(0,-.4,.5),(0,0,.02)]
        vertices=np.concatenate([square(c,1.6 if i==0 else .04) for i,c in enumerate(centers)])
        faces=np.concatenate([np.array([[0,1,2],[2,3,0]],dtype='i4')+4*i for i in range(6)])
        labels=np.repeat([3,0,0,-2,-3,-1],2)
        with TemporaryDirectory() as name:
            work=Path(name);p=work/'scans.npz'
            cloud=np.tile(vertices[8:12],(3,1))
            np.savez(p,registered_points=cloud,cloud_stamps=[0,1,2],cloud_offsets=[0,4,8,12],
                     trajectory=[[0,0,0,1],[1,.3,0,1],[2,.6,0,1]])
            keep,info=floater_mask(vertices,faces,labels,work,p)
            np.testing.assert_array_equal(keep,np.repeat([True,False,True,True,True,True],2))
            self.assertEqual(info['removed_components'],1)
            # Baked legacy data without sensor evidence remains usable.
            np.testing.assert_array_equal(floater_mask(vertices,faces,labels,work)[0],np.ones(len(faces),bool))

    def test_depth_guard_protects_a_visible_measured_surface(self):
        v=np.r_[square([0,0,3],3),square([0,0,1.5],.40)]
        f=np.array([[0,1,2],[2,3,0],[4,5,6],[6,7,4]],'i4')
        with TemporaryDirectory() as name:
            w=Path(name)
            np.savez(w/'cameras.npz',depth_k=[[70,0,32],[0,70,32],[0,0,1]],
                     depth_poses=np.tile(np.eye(4),(9,1,1)))
            for observed,must_keep in [(1500,True),(3000,False),(0,False)]:
                np.save(w/'depth.npy',np.full((9,64,64),observed,'u2'))
                result=visible_surface_guard(v,f,np.array([0,0,1,1]),np.array([False,True]),w)
                self.assertEqual(bool(result[1]),must_keep)


if __name__=='__main__':
    unittest.main()
