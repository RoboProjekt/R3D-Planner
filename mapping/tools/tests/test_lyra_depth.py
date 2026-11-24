import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reconstruct_lyra_route import registered_depth


class ProjectedDepthTests(unittest.TestCase):
    def setUp(self):
        self.depth_k = np.array([[194., 0., 160.], [0., 194., 120.], [0., 0., 1.]])
        self.color_k = np.array([[607., 0., 320.], [0., 607., 240.], [0., 0., 1.]])

    def project(self, depth):
        return registered_depth(depth, self.depth_k, self.color_k, np.eye(4), (640, 480))

    def test_measured_plane_survives_reprojection_to_narrower_rgb_fov(self):
        depth = np.full((240, 320), 2000, np.uint16)
        projected = self.project(depth)
        np.testing.assert_allclose(projected[4:-4, 4:-4], 2.)

    def test_discontinuity_and_missing_depth_stay_invalid(self):
        depth = np.full((240, 320), 2000, np.uint16)
        depth[:, 160:] = 4500
        depth[90:136, 100:130] = 0
        projected = self.project(depth)
        self.assertEqual(projected[120, 92], 0.)
        self.assertEqual(projected[120, 145], 2.)
        self.assertIn(0., projected[120, 156:165])
        self.assertEqual(projected[120, 180], 4.5)
        self.assertFalse(self.project(np.zeros_like(depth)).any())


if __name__ == '__main__':
    unittest.main()
