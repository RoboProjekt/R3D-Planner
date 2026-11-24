"""Regression checks for point provenance and cross-sensor wall distances."""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from measure_l1_walls import wall_residuals
from prepare_l1_ab import select_hesai
from evaluate_l1_ab import log_time_origin


def fields(x, times):
    x = np.asarray(x, dtype=np.float32)
    return {'x': x, 'y': x/2, 'z': x/4, 'intensity': x*2,
            'ring': np.zeros(len(x), 'u2'), 'timestamp': np.asarray(times, 'f8')}


class L1ComparisonTest(unittest.TestCase):
    def test_interleaved_coincident_timestamps(self):
        source = fields([2, 3, 3, 6], [10, 10, 10, 12])
        fused = fields([2, 3, 18, 3, 9, 6, 15], [10, 10, 10, 10, 11, 12, 12])
        np.testing.assert_array_equal(select_hesai(fused, source),
                                      [True, True, False, True, False, True, False])

    def test_matching_timestamps_do_not_prove_matching_scan(self):
        source = fields([2, 3, 6], [10, 10, 12])
        fused = fields([2, 8, 9, 6], [10, 10, 11, 12])
        self.assertIsNone(select_hesai(fused, source))

    def test_extra_identical_point_is_ambiguous(self):
        source = fields([2, 3], [10, 10])
        fused = fields([2, 2, 3], [10, 10, 10])
        self.assertIsNone(select_hesai(fused, source))

    def test_known_wall_offset_and_out_of_view(self):
        y, z = np.mgrid[-1:1:.06, -1:1:.06]
        wall = np.column_stack((np.full(y.size, 2.), y.ravel(), z.ravel()))
        unitree = np.vstack((wall[::3] + [0.075, 0, 0], [2., 2.5, 0]))
        residual, eligible = wall_residuals(wall, unitree)
        self.assertEqual(eligible, len(unitree))
        self.assertEqual(len(residual), len(unitree)-1)
        np.testing.assert_allclose(residual, .075, atol=1e-8)

    def test_state_log_uses_first_processed_cloud(self):
        rng = np.random.default_rng(7)
        headers = 1000 + np.cumsum(rng.uniform(.04, .08, 200))
        relative = headers[9::2] - headers[3]
        origin, error = log_time_origin(np.round(relative[:, None], 4), headers)
        self.assertEqual(origin, headers[3])
        self.assertLess(error, .0001)


if __name__ == '__main__':
    unittest.main()
