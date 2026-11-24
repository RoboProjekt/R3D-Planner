from importlib.util import find_spec
from pathlib import Path
import sys
import unittest

import numpy as np
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lidar_revisits import close_loops, compatible_motion, propose
from lidar_planes import constrain_planes, largest_vertical_gap, level_map, plane_height, wall_vertical
from lidar_floor_surfaces import align_floor_surfaces
from correct_lio_drift import optimize

if find_spec('kiss_icp') is not None:
    from map_hesai import rotational_phase, unpack_scan
    from sensor_msgs.msg import PointCloud2, PointField


class RevisitTest(unittest.TestCase):
    def test_repeated_floor_and_reversed_hall_are_rejected(self):
        self.assertFalse(compatible_motion(np.array([.1, .2, 2.5]), 0., 140.))
        self.assertFalse(compatible_motion(np.zeros(3), np.pi, 140.))
        self.assertTrue(compatible_motion(np.array([.8, 0., .4]), .1, 40.))

    def test_stationary_scans_do_not_generate_loops(self):
        poses = np.repeat(np.eye(4)[None], 8, axis=0)
        signatures = np.ones((8, 3, 36))
        self.assertEqual(list(propose(np.arange(8)*5, poses, signatures)), [])

    def test_no_revisit_preserves_trajectory_and_scan(self):
        poses = np.array([[100.,0,0,0,0,0,0,1], [101.,1,0,0,0,0,0,1]])
        clouds = [np.ones((150, 3))]
        out, returned, metrics = close_loops(poses, clouds, [100.])
        np.testing.assert_array_equal(out, poses)
        self.assertIs(returned, clouds)
        self.assertEqual(metrics['status'], 'local_odometry')


class PlaneTest(unittest.TestCase):
    def test_floor_mode_uses_wall_evidence_to_distinguish_slope_from_pose_drift(self):
        rng = np.random.default_rng(22)
        xy = rng.uniform(-2., 2., (1600, 2))
        lateral = rng.uniform(-2., 2., 850)
        height = rng.uniform(-.18, 1.35, len(lateral))
        times = np.arange(65.)*.3
        x = np.linspace(0., 12., len(times))
        for real_ramp in (False, True):
            grade = np.tan(np.deg2rad(2.)) if real_ramp else 0.
            # The same apparent gradient can come from translation drift.
            estimated_z = .8 + x*np.tan(np.deg2rad(2.))
            poses = np.zeros((len(x), 8))
            poses[:, 0], poses[:, 1], poses[:, 3], poses[:, 7] = times, x, estimated_z, 1.
            clouds = []
            for station, sensor_z in zip(x, estimated_z):
                floor = np.column_stack([station+xy[:, 0], xy[:, 1], sensor_z-.8+grade*xy[:, 0]])
                side = np.column_stack([station+lateral, np.full_like(lateral, 2.), sensor_z+height])
                next_wall = 3.*(np.floor(station/3.)+1.)
                end = np.column_stack([np.full_like(lateral, next_wall), lateral, sensor_z+height])
                clouds.append(np.vstack([floor, side, end]))
            fixed, out, report = align_floor_surfaces(poses, clouds, times, [])
            if real_ramp:
                self.assertFalse(report['applied'])
                np.testing.assert_array_equal(fixed, poses)
            else:
                self.assertTrue(report['applied'])
                self.assertAlmostEqual(report['surfaces'][0]['height_m'], 0., delta=.035)
                self.assertEqual(fixed[0, 3], poses[0, 3])
                self.assertLess(np.ptp(fixed[5:-5, 3]), .045)
                np.testing.assert_allclose(out[20][10]-out[20][0],
                                           clouds[20][10]-clouds[20][0], atol=.005)

    def test_level_export_rotates_scan_and_trajectory_in_the_same_frame(self):
        mount = Rotation.from_euler('y', 6., degrees=True)
        origin = np.array([1., -2., 3.])
        offsets = np.array([[0., 0., 0.], [3., 0., .7]])
        positions = origin + mount.apply(offsets)
        track = np.column_stack([np.arange(2.), positions, [mount.as_quat()]*2])
        target = np.array([[2., 1., .1]])
        clouds = [mount.apply(target)+p for p in positions]
        leveled, scans, transform = level_map(track, clouds, mount.apply([0., 0., 1.]))
        np.testing.assert_allclose(leveled[:, 1:4], origin+offsets, atol=1e-10)
        np.testing.assert_allclose(Rotation.from_quat(leveled[:, 4:]).magnitude(), 0., atol=1e-10)
        for i, scan in enumerate(scans):
            np.testing.assert_allclose(scan, target+leveled[i, 1:4], atol=1e-6)
        np.testing.assert_allclose(transform[:3, :3] @ mount.apply([0., 0., 1.]), [0., 0., 1.], atol=1e-10)

    def test_loop_cannot_freely_pitch_a_corridor_with_observed_verticals(self):
        nodes = np.arange(21.)
        base = np.repeat(np.eye(4)[None], len(nodes), axis=0)
        base[:, 0, 3] = np.minimum(nodes, nodes[::-1])
        loop = np.eye(4)
        loop[:3, :3] = Rotation.from_euler('zy', [5., 4.], degrees=True).as_matrix()
        edge = [(0, len(nodes)-1, loop)]
        free = optimize(nodes, base, edge)
        up = np.array([0., 0., 1.])
        held = optimize(nodes, base, edge, vertical_nodes=np.arange(1, len(nodes)), building_up=up)
        self.assertLess(np.linalg.norm(held[-1, :3, 2]-up), .55*np.linalg.norm(free[-1, :3, 2]-up))
        self.assertGreater(np.rad2deg(np.arctan2(held[-1, 1, 0], held[-1, 0, 0])), 4.)

    def test_shallow_ramp_and_step_between_observed_walls_keep_their_height(self):
        rng = np.random.default_rng(7)
        xy = rng.uniform(-2., 2., (1400, 2))
        y = rng.uniform(-2., 2., 750)
        wall_z = rng.uniform(-.18, 1.3, len(y))
        def ground(x):
            return np.maximum(x-2., 0.)*np.tan(np.deg2rad(2.)) + .20*(x >= 7.)
        times = np.arange(61)*.5
        x = times*.35
        poses = np.zeros((len(x), 8))
        poses[:, 0], poses[:, 1], poses[:, 3], poses[:, 7] = times, x, ground(x)+.8, 1.
        clouds = []
        for pos, height in zip(x, poses[:, 3]):
            local_x = pos+xy[:, 0]
            # Two fixed orthogonal walls and the actual piecewise floor.
            floor = np.column_stack([local_x, xy[:, 1], ground(local_x)])
            side = np.column_stack([pos+y, np.full_like(y, 2.), wall_z+height])
            wall_x = 3.*(np.floor(pos/3.)+1.)
            end = np.column_stack([np.full_like(y, wall_x), y, wall_z+height])
            clouds.append(np.vstack([floor, side, end]))
        result, _, report = constrain_planes(poses, clouds, times)
        self.assertTrue(report['applied'])
        self.assertGreater(result[-1, 3]-result[0, 3], .45)
        np.testing.assert_allclose(result[:, 3], poses[:, 3], atol=.035)
        with_surfaces, _, _ = align_floor_surfaces(poses, clouds, times, [])
        np.testing.assert_allclose(with_surfaces[:, 3], poses[:, 3], atol=.035)

    def test_gap_counts_motion_between_anchor_windows_including_a_turnaround(self):
        poses = np.zeros((7, 8))
        poses[:, 0], poses[:, 1] = 20+np.arange(7.), [0, 1, 2, 3, 2, 1, 0]
        gap = largest_vertical_gap(poses, [(0., 1.), (5., 6.)])
        self.assertEqual(gap, {'start_s': 1., 'end_s': 5., 'travel_m': 4.})

    def test_same_ramp_yields_no_floor_offset_at_common_position(self):
        normal = np.array([-.12, 0., 1.])
        normal /= np.linalg.norm(normal)
        query, up = np.array([1., 0., 0.]), np.array([0., 0., 1.])
        a = (normal, np.array([0., 0., -.5]), None)
        b = (normal, np.array([2., 0., -.26]), None)
        self.assertAlmostEqual(plane_height(a, query, up), plane_height(b, query, up))

    def test_two_walls_establish_vertical_but_sloped_floor_does_not(self):
        rng = np.random.default_rng(13)
        y = rng.uniform(-2., 2., 900)
        z = rng.uniform(-.18, 1.3, len(y))
        walls = np.vstack([np.column_stack([np.full_like(y, 2.), y, z]),
                           np.column_stack([y, np.full_like(y, 2.), z])])
        np.testing.assert_allclose(wall_vertical(walls, rng), [0., 0., 1.], atol=.02)
        xy = rng.uniform(-2.8, 2.8, (1400, 2))
        floor = np.column_stack([xy, -.8+.18*xy[:, 0]])
        scene = np.vstack([walls, floor])
        times = np.arange(20.)
        poses = np.zeros((len(times), 8))
        poses[:, 0], poses[:, 7] = times, 1.
        result, _, metrics = constrain_planes(poses, [scene]*len(times), times)
        np.testing.assert_array_equal(result, poses)
        self.assertFalse(metrics['applied'])


@unittest.skipUnless(find_spec('kiss_icp'), 'requires the LiDAR mapping environment')
class FiringTimeTest(unittest.TestCase):
    def setUp(self):
        angle = np.repeat(np.linspace(1., -4.5, 100), 16)
        self.xyz = np.column_stack([3*np.cos(angle), 3*np.sin(angle), np.zeros(len(angle))])
        self.rings = np.tile(np.arange(16), 100)

    def test_azimuth_with_missing_returns_and_wraparound(self):
        self.xyz[16*30:16*33] = 0
        phase = rotational_phase(self.xyz, self.rings)
        np.testing.assert_allclose(phase[::16], np.linspace(0, 1, 100), atol=1e-6)
        self.assertFalse(len(rotational_phase(self.xyz, self.rings[::-1])))
        self.assertFalse(len(rotational_phase(np.zeros_like(self.xyz), self.rings)))

    def test_known_point_times_take_priority_and_invalid_xyz_stays_paired(self):
        records = np.zeros(3, dtype=[(k, '<f4') for k in 'xyz'] + [('timestamp','<f8')])
        records['x'] = [2, np.nan, 3]
        records['timestamp'] = [100.,100.018,100.04]
        msg = PointCloud2(height=1, width=3, point_step=20, row_step=60,
                          fields=[PointField(name=k, offset=records.dtype.fields[k][1], count=1,
                                             datatype=PointField.FLOAT64 if k=='timestamp' else PointField.FLOAT32)
                                  for k in records.dtype.names], data=records.tobytes())
        msg.header.stamp.sec = 100
        end, cloud, times, timing = unpack_scan(msg)
        self.assertEqual(timing, 'recorded')
        self.assertEqual(end, 100.04)
        np.testing.assert_array_equal(cloud[:,0], [2,3])
        np.testing.assert_allclose(times, [0,.04])
        records['timestamp'] = 100.
        msg.data = records.tobytes()
        self.assertEqual(unpack_scan(msg)[3], 'rigid')
