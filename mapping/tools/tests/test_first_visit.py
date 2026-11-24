from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lidar_first_visit import first_visit_anchors


class FirstVisitTest(unittest.TestCase):
    def scene(self, changed_ground=False):
        rng = np.random.default_rng(14)
        x = np.r_[np.linspace(0, 9, 40), np.linspace(9, 0, 40)]
        ts = np.arange(len(x))*.45
        z = 1.7+.025*x
        track = np.zeros((len(x), 8))
        track[:, 0], track[:, 1], track[:, 3], track[:, 7] = ts, x, z+.72, 1.
        floor_xy = rng.uniform([-4.,-2.], [13.,2.], (5000,2))
        floor = np.column_stack([floor_xy, 1.7+.025*floor_xy[:,0]])
        # Fixed cabinets give a check on vertical alignment independent of the ground.
        wall = rng.uniform([-4.,-1.8,2.55], [13.,1.8,2.57], (2500,3))
        scans = []
        for i, station in enumerate(x):
            patch = floor[abs(floor[:,0]-station)<3.2].copy()
            cabinet = wall[abs(wall[:,0]-station)<3.2].copy()
            if i >= 40:
                patch[:,2] -= .33
                if not changed_ground:
                    track[i,3] -= .33
                    cabinet[:,2] -= .33
            scans.append(np.vstack([patch, cabinet]).astype('f4'))
        return track, scans, ts

    def test_revisit_uses_first_inclined_surface_and_moves_whole_scan(self):
        track, clouds, stamps = self.scene()
        fixed, aligned, report = first_visit_anchors(track, clouds, stamps, [(stamps[4],stamps[-5])])
        self.assertTrue(report['applied'])
        np.testing.assert_array_equal(fixed[:40], track[:40])
        self.assertIs(aligned[4], clouds[4])
        self.assertGreater(fixed[57,3]-track[57,3], 0.)
        self.assertLess(fixed[57,3]-track[57,3], .33)
        for i in [59, 65, 76]:
            np.testing.assert_allclose(fixed[i,3]-track[i,3], .33, atol=.015)
            np.testing.assert_allclose(aligned[i]-clouds[i], np.tile([0,0,.33],(len(clouds[i]),1)), atol=.012)

    def test_changed_floor_alone_cannot_move_unchanged_cabinets(self):
        track, clouds, stamps = self.scene(changed_ground=True)
        fixed, _, report = first_visit_anchors(track, clouds, stamps, [(stamps[4],stamps[-5])])
        self.assertFalse(report['applied'])
        np.testing.assert_array_equal(fixed, track)

    def test_same_xy_on_another_storey_and_absent_loop(self):
        track, clouds, stamps = self.scene()
        track[40:,3] += 3.
        for cloud in clouds[40:]:
            cloud[:,2] += 3.
        for loops in [[], [(stamps[4],stamps[-5])]]:
            fixed, _, report = first_visit_anchors(track, clouds, stamps, loops)
            self.assertFalse(report['applied'])
            np.testing.assert_array_equal(fixed, track)
