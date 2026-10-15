# Copyright 2026 Bastian Aumer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-FileCopyrightText: 2026 Bastian Aumer
# SPDX-License-Identifier: Apache-2.0

"""Check the radial-loss fix and actual isolated sensor-to-command geometry."""
import math
from pathlib import Path
import struct
import uuid
from unittest.mock import Mock, patch

import numpy as np
import pytest
import rclpy
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import yaml

from r3d_planner.cloud import read_xyz
from r3d_planner.configuration import ConfigurationError, load_configuration
from r3d_planner.obstacle_monitor import ObstacleMonitor
from r3d_planner.r3d_local_filter import ObstacleCliffFilter
from test_obstacle_monitor_ros import Harness, zero


def cloud64(points, frame='base_link', stamp=10**10, padded=False):
    """Keep exact double boundaries, optionally with reordered fields and row padding."""
    count = len(points)
    step, offsets = (40, [24, 0, 8]) if padded else (24, [0, 8, 16])
    width, height = (2, count//2) if padded and count else (count, 1)
    row = width*step + (13 if padded else 0)
    data = bytearray(row*height)
    for i, point in enumerate(points):
        r, c = divmod(i, width)
        for value, offset in zip(point, offsets):
            struct.pack_into('>d', data, r*row+c*step+offset, value)
    header = Header(frame_id=frame)
    header.stamp.sec, header.stamp.nanosec = divmod(stamp, 10**9)
    return PointCloud2(header=header, height=height, width=width,
                       fields=[PointField(name=n, offset=o, datatype=PointField.FLOAT64, count=1)
                               for n, o in zip(['x', 'y', 'z'], offsets)],
                       point_step=step, row_step=row, is_bigendian=True, data=bytes(data))


def local_node(namespace, **overrides):
    original = Node.__init__

    def init(node, *args, **kwargs):
        kwargs['namespace'] = namespace
        kwargs['cli_args'] = ['--ros-args', '-r', '/local/filtered_obstacles:=obstacles',
                              '-r', '/local/cliff_virtual_wall:=cliff',
                              '-r', '/stair_detect:=stairs']
        kwargs['parameter_overrides'] = [Parameter(k, value=v) for k, v in overrides.items()]
        original(node, *args, **kwargs)
    with patch.object(Node, '__init__', init):
        return ObstacleCliffFilter()


@pytest.fixture
def local():
    rclpy.init()
    node = local_node('/geo_' + uuid.uuid4().hex[:8])
    node.pub_obstacles, node.pub_cliff, node.pub_stair_detect = Mock(), Mock(), Mock()
    try:
        yield node
    finally:
        node.destroy_node()
        rclpy.shutdown()


def output(local, message):
    count = local.pub_obstacles.publish.call_count
    original = bytes(message.data)
    local.pc_callback(message)
    assert bytes(message.data) == original
    assert local.pub_obstacles.publish.call_count == count+1
    result = local.pub_obstacles.publish.call_args.args[0]
    assert result.header == message.header
    return result


def monitored(message, roi=(0.1, 0.6, 0.3), transform=None):
    lookup = Mock(return_value=transform)
    item = ObstacleMonitor({'enabled': True, 'timeout_sec': 1.0, 'require_transform': True},
                           'base_link', roi, lookup)
    item.receive(message, 10**10, 100*10**9)
    return item


@pytest.mark.parametrize('point,blocked', [
    ([0.3, 0, 0.2], True), ([0.59, 0, 0.2], True), ([0.6, 0, 0.2], False),
    ([0.625, 0, 0.2], False), ([0.65, 0, 0.2], False), ([0.66, 0, 0.2], False),
    ([0.59999, 0, 0.2], True), ([0.60001, 0, 0.2], False),
    ([0.10001, 0, 0.2], True), ([0.09999, 0, 0.2], False),
    ([0.05, 0, 0.2], False), ([-0.3, 0, 0.2], False),
    ([0.3, 0.31, 0.2], False), ([0.3, 0.2999, 0.2], True),
    ([0.3, 0, 0.049], False), ([0.3, 0, 1.001], False),
    ([0.59, 0.29, 0.2], True), ([0.3, 0, 0.051], True)])
def test_filtered_geometry_and_negative_regions(local, point, blocked):
    result = output(local, cloud64([point]))
    item = monitored(result)
    assert (item.state == 'BLOCKED') is blocked
    if 0.05 < point[2] < 1.0:
        np.testing.assert_allclose(read_xyz(result), [point])


@pytest.mark.parametrize('x,y,blocked', [(0.1, 0, False), (0.6, 0, False),
                                         (0.3, 0.3, False), (0.3, -0.3, False),
                                         (0.599999, 0.299999, True)])
def test_exact_open_follower_boundaries_in_double_input(x, y, blocked):
    assert (monitored(cloud64([[x, y, 0.2]])).state == 'BLOCKED') is blocked


@pytest.mark.parametrize('radius', [0.1, 0.6, 0.65, 1.0])
def test_filter_radius_cannot_erase_near_obstacles(local, radius):
    local.min_reliable_distance = radius
    result = output(local, cloud64([[0.3, 0, 0.2], [0.59, 0, 0.2]]))
    assert len(read_xyz(result)) == 2
    assert monitored(result).state == 'BLOCKED'


@pytest.mark.parametrize('retain', [False, True])
def test_new_policy_preserves_legacy_stair_cliff_and_no_duplicates(local, retain):
    points = [[0.3, 0, 0.2], [0.65, 0, 0.2], [0.8, 0, 0.15]]
    points += [[0.8, 0, 0.15]]*60 + [[0.8, 0, 0.0]]*40
    local.retain_near_obstacles = retain
    result = output(local, cloud64(points))
    # Strict radial equality was excluded by the old pipeline; it is retained once now.
    assert len(read_xyz(result)) == (2 if retain else 0)
    assert local.pub_stair_detect.publish.call_count == 1
    assert len(read_xyz(local.pub_cliff.publish.call_args.args[0])) == 0
    if retain:
        np.testing.assert_allclose(read_xyz(result)[:, 0], [0.3, 0.65])


def test_layout_padding_offsets_organization_and_multiple_points(local):
    points = [[0.59, 0, 0.2], [0.625, 0, 0.2], [0.3, 0.4, 0.2], [0.66, 0, 0.2]]
    result = output(local, cloud64(points, padded=True))
    assert monitored(result).state == 'BLOCKED'
    assert sorted(read_xyz(result)[:, 0]) == pytest.approx(sorted(p[0] for p in points))


def test_empty_invalid_and_nonfinite_do_not_become_fresh_clear(local):
    assert monitored(output(local, cloud64([]))).state == 'ACTIVE'
    malformed = cloud64([[0.3, 0, 0.2]])
    malformed.fields = []
    for message in [cloud64([[math.nan, 0, 0.2]]), malformed]:
        count = local.pub_obstacles.publish.call_count
        local.pc_callback(message)
        assert local.pub_obstacles.publish.call_count == count


@pytest.mark.parametrize('stop,blocked', [(0.5, False), (0.6, False), (0.7, True)])
def test_changed_stop_distance_still_receives_point(local, stop, blocked):
    result = output(local, cloud64([[0.625, 0, 0.2]]))
    assert len(read_xyz(result)) == 1
    assert (monitored(result, roi=(0.1, stop, 0.3)).state == 'BLOCKED') is blocked


@pytest.fixture
def config(tmp_path):
    share = Path(get_package_share_directory('r3d_planner'))/'config'
    cfg = yaml.safe_load((share/'planner_config.yaml').read_text())
    (tmp_path/'robots').mkdir()
    (tmp_path/'robots/Go2W.yaml').write_bytes((share/'robots/Go2W.yaml').read_bytes())
    (tmp_path/'map.pcd').write_text('configuration fixture only')
    cfg['maps'] = {'map_name': 'map.pcd', 'pcd_path': 'map.pcd'}
    return tmp_path, cfg


@pytest.mark.parametrize('value', [None, 0, 1, 'true', [], {}])
def test_invalid_retention_configuration(config, value):
    directory, cfg = config
    cfg['live_filter']['retain_near_obstacles'] = value
    path = directory/'planner_config.yaml'
    path.write_text(yaml.safe_dump(cfg))
    with pytest.raises(ConfigurationError, match='retain_near_obstacles'):
        load_configuration(path)


@pytest.mark.parametrize('mode', ['planner', 'follower', 'map', 'preprocessor'])
def test_old_profile_and_robot_radius_remain_independent(config, mode):
    directory, cfg = config
    cfg['live_filter'].pop('retain_near_obstacles')
    path = directory/'planner_config.yaml'
    path.write_text(yaml.safe_dump(cfg))
    old = load_configuration(path, mode=mode)
    assert old['live_filter']['retain_near_obstacles'] is True
    robot_path = directory/'robots/Go2W.yaml'
    robot = yaml.safe_load(robot_path.read_text())
    robot['robot']['geometry']['robot_radius_cm'] = 70.0
    robot_path.write_text(yaml.safe_dump(robot))
    changed = load_configuration(path, mode=mode)
    assert changed['path_follower'] == old['path_follower']
    assert changed['live_filter'] == old['live_filter']
    assert changed['planner']['robot_radius_cm'] == 70.0
    cfg['live_filter']['retain_near_obstacles'] = False
    path.write_text(yaml.safe_dump(cfg))
    assert load_configuration(path, mode=mode)['live_filter']['retain_near_obstacles'] is False


class GeometryHarness(Harness):
    """Observe filter output and real commands without production sensor topics."""

    def __init__(self, enabled=True, retain=True):
        super().__init__(enabled=enabled)
        self.local = local_node(self.namespace, pointcloud_topic='raw',
                                retain_near_obstacles=retain)
        self.executor.add_node(self.local)
        self.source = self.observer.create_publisher(PointCloud2, 'raw', qos_profile_sensor_data)
        self.outputs = []
        self.observer.create_subscription(PointCloud2, 'obstacles', self.outputs.append, 10)
        self.until(lambda: self.source.get_subscription_count() > 0 and
                   self.local.pub_obstacles.get_subscription_count() >= 2)
        self.pose()
        self.path()

    def filtered(self, points, frame='base_link'):
        self.pose()
        message = self.cloud(points, frame)
        count = len(self.outputs)
        self.source.publish(message)
        self.until(lambda: len(self.outputs) > count)
        assert self.outputs[-1].header == message.header
        return self.outputs[-1]

    def close(self):
        self.executor.remove_node(self.local)
        self.local.destroy_node()
        super().close()


@pytest.fixture
def geometry():
    rclpy.init()
    items = []

    def create(**kwargs):
        item = GeometryHarness(**kwargs)
        items.append(item)
        return item
    try:
        yield create
    finally:
        for item in items:
            item.close()
        rclpy.shutdown()


@pytest.mark.parametrize('enabled', [False, True])
def test_native_full_chain_stop_negative_regions_and_recovery(geometry, enabled):
    item = geometry(enabled=enabled)
    for points, blocked in [([[2, 0, 0.2]], False), ([[0.59, 0, 0.2]], True),
                            ([[0.625, 0, 0.2]], False), ([[0.59, 0, 0.2]], True),
                            ([[0.3, 0.31, 0.2]], False), ([[-0.3, 0, 0.2]], False),
                            ([[0.3, 0, 1.01]], False), ([], False),
                            ([[0.3, 0, 0.2], [2, 0, 0.2]], True)]:
        result = item.filtered(points)
        expected = any(0.05 < p[2] < 1.0 for p in points)
        assert bool(len(read_xyz(result))) is expected
        if enabled:
            item.until(lambda: item.follower.obstacle_monitor.state == (
                'BLOCKED' if blocked else 'ACTIVE'))
        item.until(lambda: item.follower.obstacle_in_front is blocked)
        if blocked:
            item.stopped()
            assert all(zero(v) for v in item.commands[-2:])
        else:
            item.moving()
        assert item.follower.current_narrow == [False, True]
    if enabled:
        item.until(lambda: item.follower.obstacle_monitor.state == 'STALE_DATA', timeout=3)
        item.stopped()
        item.filtered([[0.59, 0, 0.2]])
        item.until(lambda: item.follower.obstacle_monitor.state == 'BLOCKED')
        item.stopped()
        item.filtered([])
        item.until(lambda: item.follower.obstacle_monitor.state == 'ACTIVE')
        item.moving()


def test_native_sensor_translation_rotation_and_missing_tf(geometry):
    item = geometry()
    item.filtered([[0.625, 0, 0.2]], frame='geo_sensor')
    item.until(lambda: item.follower.obstacle_monitor.state == 'TF_UNAVAILABLE')
    item.stopped()
    value = TransformStamped()
    value.header.frame_id, value.child_frame_id = 'base_link', 'geo_sensor'
    value.transform.rotation.w = 1.0
    value.transform.translation.x = -0.125
    item.static.sendTransform(value)
    item.until(lambda: item.follower.odometry.buffer.can_transform(
        'base_link', 'geo_sensor', rclpy.time.Time()))
    result = item.filtered([[0.625, 0, 0.2]], frame='geo_sensor')
    np.testing.assert_allclose(read_xyz(result), [[0.625, 0, 0.2]])
    item.until(lambda: item.follower.obstacle_monitor.state == 'BLOCKED')
    item.stopped()
    value.child_frame_id = 'geo_rotated'
    value.transform.translation.x = 0.3
    value.transform.rotation.w = math.sqrt(0.5)
    value.transform.rotation.z = math.sqrt(0.5)
    item.static.sendTransform(value)
    item.until(lambda: item.follower.odometry.buffer.can_transform(
        'base_link', 'geo_rotated', rclpy.time.Time()))
    item.filtered([[0, 0, 0.2]], frame='geo_rotated')
    item.until(lambda: item.follower.obstacle_monitor.state == 'BLOCKED')
    item.stopped()
    item.filtered([[0.625, 0, 0.2]], frame='geo_rotated')
    item.until(lambda: item.follower.obstacle_monitor.state == 'ACTIVE')
    item.moving()


def test_native_explicit_legacy_switch_and_startup_parameter(geometry):
    item = geometry(retain=False)
    result = item.filtered([[0.59, 0, 0.2]])
    assert len(read_xyz(result)) == 0
    item.until(lambda: item.follower.obstacle_monitor.state == 'ACTIVE')
    item.moving()  # This intentionally reproduces the documented legacy loss.
    result = item.local.set_parameters([Parameter('retain_near_obstacles', value=True)])
    assert not result[0].successful
