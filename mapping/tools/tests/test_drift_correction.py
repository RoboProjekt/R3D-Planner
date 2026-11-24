"""Check the transform directions and that ambiguous geometry cannot close a loop."""
from pathlib import Path
import sys
import unittest

import numpy as np
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from correct_lio_drift import (
    Correction, Replay, align, apply_pose, confirm_known_revisit, matrices, optimize, verify_loop,
)


def replay_at_positions(times, positions):
    replay = Replay.__new__(Replay)
    replay.time = np.asarray(times, dtype=float)
    replay.positions = np.asarray(positions, dtype=float)
    replay.rotations = Rotation.identity(len(times))
    return replay


class DriftCorrectionTest(unittest.TestCase):
    def test_rotational_correction_pivots_around_each_robot_pose(self):
        replay = replay_at_positions([0, 1, 2], [[8, 2, 6], [9, 2, 6], [10, 2, 6]])
        times = np.array([0., 2.])
        rotations = Rotation.from_euler('z', [0, 90], degrees=True)
        base = replay.at(times)
        after = matrices(base[:, :3, 3] + [[0, 0, 0], [0, 1, 0]], rotations)
        corr = Correction(replay, times, base, after)
        np.testing.assert_allclose(corr.at(times) @ base, after, atol=1e-10)
        raw = np.array([[9., 2., 6.], [10., 2., 6.]])
        transformed = apply_pose(corr.at([1.])[0], raw)
        np.testing.assert_allclose(transformed[0], [9, 2.5, 6], atol=1e-10)
        np.testing.assert_allclose(transformed[1] - transformed[0],
                                   [2**-.5, 2**-.5, 0], atol=1e-10)

    def test_anchor_fixed_and_return_retains_measured_separation(self):
        times = np.arange(7.)
        positions = np.zeros((len(times), 3))
        positions[:, 0] = [0, 2, 4, 6, 4, 2, .9]
        replay = replay_at_positions(times, positions)
        base = replay.at(times)
        measurement = np.eye(4)
        measurement[0, 3] = .3
        result = optimize(times, base, [(0, len(times)-1, measurement)])
        np.testing.assert_array_equal(result[0], base[0])
        self.assertGreater(result[-1, 0, 3], .29)
        self.assertLess(result[-1, 0, 3], .36)
        np.testing.assert_allclose(optimize(times, base, []), base, atol=1e-10)

    def test_single_plane_is_underconstrained(self):
        x, y = np.mgrid[-2:2:.07, -2:2:.07]
        plane = np.column_stack([x.ravel(), y.ravel(), np.zeros(x.size)])
        with self.assertRaisesRegex(ValueError, 'Underconstrained'):
            align(plane, plane + [0, 0, .1], np.eye(4))

    def test_missing_cloud_skips_only_that_candidate(self):
        replay = replay_at_positions([0, 1], [[0, 0, 0], [0, 0, 0]])
        replay.stamps = np.array([.5])
        result, measurement = verify_loop(replay, {'name': 'gap', 'times': [0, 1]})
        self.assertIsNone(measurement)
        self.assertFalse(result['accepted'])
        self.assertIn('Insufficient registered scans', result['reason'])

    def test_confirmed_revisit_recovers_large_shift_and_rejects_conflict(self):
        rng = np.random.default_rng(7)
        room = []
        for axis, coordinate in enumerate([2., 1.7, -.9]):
            plane = rng.uniform(-2., 2., size=(1200, 3))
            plane[:, axis] = coordinate
            room.append(plane)
        room = np.vstack(room)
        drift = np.array([4.1, -.3, .15])
        replay = replay_at_positions([0, 12, 40, 44], [np.zeros(3), np.zeros(3), drift, drift])
        revisit = {'name': 'room', 'pairs': [[2, 40], [8, 44]]}
        replay.local_cloud = lambda t: room + (drift if t >= 40 else 0.)
        report, edge = confirm_known_revisit(replay, revisit)
        self.assertTrue(report['accepted'])
        np.testing.assert_allclose(edge[2], np.eye(4), atol=.02)
        replay.local_cloud = lambda t: room + (drift if t >= 40 else 0.) + ([.45, 0, 0] if t == 44 else 0.)
        report, edge = confirm_known_revisit(replay, revisit)
        self.assertIsNone(edge)
        self.assertEqual(report['reason'], 'Two registrations disagree')
