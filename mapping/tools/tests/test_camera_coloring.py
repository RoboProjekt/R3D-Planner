import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from color_hesai_map import ColorMap, synchronize


class CameraColorTest(unittest.TestCase):
    def setUp(self):
        self.k = np.array([[100., 0., 80.], [0., 100., 60.], [0., 0., 1.]])
        self.camera = (161, 121, self.k, None)
        v, u = np.mgrid[0:121, 0:161]
        self.picture = np.stack([u, v, np.full_like(u, 17)], axis=-1).astype('u1')
        self.wall = np.column_stack([2*(u.ravel()-80)/100, 2*(v.ravel()-60)/100, np.full(u.size, 2.)])
        self.eye = np.eye(4)

    def test_only_depth_supported_visible_lidar_points_get_image_pixels(self):
        xyz = np.array([[0.,0.,2.], [.2,0.,2.], [0.,0.,2.5], [0.,0.,1.], [4.,0.,2.]], dtype='f4')
        original = xyz.copy()
        atlas = ColorMap(xyz)
        atlas.observe(self.wall, self.picture, self.eye, self.eye, self.camera, self.camera, 6.)
        np.testing.assert_array_equal(atlas.views, [1,1,0,0,0])
        np.testing.assert_array_equal(atlas.rgb[:2], [[80,60,17], [90,60,17]])
        np.testing.assert_array_equal(atlas.rgb[2:], np.full((3,3), 128))
        np.testing.assert_array_equal(xyz, original)

    def test_surface_hidden_only_in_color_camera_is_rejected(self):
        xyz = np.array([[0.,0.,2.]], dtype='f4')
        color_pose = self.eye.copy()
        color_pose[0,3] = .4
        atlas = ColorMap(xyz)
        # This close point and the LiDAR wall point land on different depth pixels
        # and on exactly the same RGB pixel due to the camera baseline.
        depth = np.vstack([self.wall, [.2,0.,1.]])
        atlas.observe(depth, self.picture, self.eye, color_pose, self.camera, self.camera, 6.)
        self.assertEqual(atlas.views[0], 0)

    def test_sync_uses_nearest_exposure_and_rejects_large_time_gaps(self):
        self.assertEqual(synchronize([(100,8),(122,9)],[(99,2),(121,3),(160,4)],4),
                         [(99,2,100,8),(121,3,122,9)])


if __name__ == '__main__':
    unittest.main()
