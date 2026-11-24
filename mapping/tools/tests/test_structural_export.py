import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from export_hesai_surfaces import structural_points


class StructuralExportTest(unittest.TestCase):
    def test_plumb_wall_keeps_heading_opening_and_confirmed_far_returns(self):
        rng = np.random.default_rng(12)
        tangent = np.array([.8, .6, 0.])
        normal = np.array([-.6, .8, 0.])
        u, z = np.meshgrid(np.linspace(-3.9, 3.9, 96), np.linspace(.1, 2.95, 40))
        visible = (abs(u) > .7) | (z > 2.)
        u, z = u[visible], z[visible]
        wall = u[:, None]*tangent + (z[:, None]-1.5)*.022*normal
        wall[:, 2] = z
        origins = np.array([tangent*x - 1.7*normal + [0, 0, 1.4] for x in np.linspace(-2.4, 2.4, 10)])
        origins = np.vstack([origins, -20*normal+[0, 0, 1.4]])
        clouds = [wall+rng.normal(0, .002, wall.shape) for _ in origins[:-1]]
        # A genuine far observation, a second echo 25 cm behind it, and a return in the doorway.
        clouds.append(np.vstack([wall, wall+.25*normal, [0., 0., .6]]))
        points = np.concatenate(clouds).astype('f4')
        scan = np.repeat(np.arange(len(clouds)), list(map(len, clouds)))
        out, keep, model, _ = structural_points(points, scan, origins, 7., 8.)
        far = np.flatnonzero(scan == len(clouds)-1)
        self.assertGreater(keep[far[:len(wall)]].mean(), .80)
        self.assertFalse(keep[far[len(wall):]].any())
        selected = model == 2
        self.assertGreater(selected.sum(), len(wall))
        np.testing.assert_allclose(out[selected, 2], points[selected, 2], atol=1e-7)
        np.testing.assert_allclose(out[selected] @ tangent, points[selected] @ tangent, atol=.002)
        # In each populated section, projected wall coordinates no longer lean with height.
        middle = selected & (abs(points @ tangent - 2.) < .16)
        self.assertGreater(np.ptp(out[middle, 2]), 1.)
        slope = np.polyfit(out[middle, 2], out[middle] @ normal, 1)[0]
        self.assertLess(abs(slope), .004)

    def test_flat_floor_is_leveled_but_real_ramp_and_step_survive(self):
        rng = np.random.default_rng(34)
        x, y = np.meshgrid(np.linspace(-3.9, 3.9, 93), np.linspace(-1.4, 1.4, 38))
        x, y = x.ravel(), y.ravel()
        origins = np.array([[s, 0., .65] for s in np.linspace(-2.4, 2.4, 10)])
        for ramp in (False, True):
            z = (.08 if ramp else .003)*y + np.where(x >= 0., .19, 0.)
            base = np.column_stack([x, y, z])
            points = np.concatenate([base+rng.normal(0., .001, base.shape) for _ in origins]).astype('f4')
            scan = np.repeat(np.arange(len(origins)), len(base))
            out, keep, model, _ = structural_points(points, scan, origins, 7., 8.)
            self.assertTrue(keep.all())
            if ramp:
                self.assertFalse(model.any())
                np.testing.assert_array_equal(out, points)
            else:
                self.assertGreater((model == 1).sum(), len(base))
                low = (model == 1) & (out[:, 0] < -1.)
                high = (model == 1) & (out[:, 0] > 1.)
                self.assertAlmostEqual(np.median(out[high, 2])-np.median(out[low, 2]), .19, delta=.01)
                self.assertLess(np.ptp(out[low, 2]), .005)
