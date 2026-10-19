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

"""Observe actual isolated ROS commands, TF, QoS, launch and monitoring recovery."""
import copy
import math
import os
import subprocess
from pathlib import Path
import time
import uuid
from unittest.mock import patch

import pytest
import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped, TransformStamped, Twist
from nav_msgs.msg import Odometry, Path as RosPath
from rclpy.clock import ClockType
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy
from r3d_interfaces.msg import PathWithMetadata
from std_msgs.msg import Header
from sensor_msgs.msg import PointCloud2
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster

from installation_contract import assert_installed_module

from r3d_planner.cloud import create_cloud_xyz32
from r3d_planner.path_metadata import metadata_qos
from r3d_planner.r3d_local_filter import ObstacleCliffFilter
from r3d_planner.r3d_path_follower import PathFollower


def zero(message):
    return all(value == 0.0 for vector in (message.linear, message.angular)
               for value in (vector.x, vector.y, vector.z))


class Harness:
    """Use only unique namespaced test commands and synthetic inputs."""

    def __init__(self, enabled=True, reliable=True, simulation=False):
        self.namespace = '/m02_' + uuid.uuid4().hex[:10]
        overrides = {'cmd_vel_topic': 'cmd', 'odometry_topic': 'odom',
                     'obstacle_monitoring.enabled': enabled,
                     'obstacle_monitoring.timeout_sec': 1.0,
                     'obstacle_monitoring.topic': 'obstacles', 'use_sim_time': simulation}
        original = Node.__init__

        def init(node, *args, **kwargs):
            kwargs['namespace'] = self.namespace
            kwargs['cli_args'] = ['--ros-args', '-r', '/global_path_metadata:=metadata']
            kwargs['parameter_overrides'] = [Parameter(k, value=v) for k, v in overrides.items()]
            original(node, *args, **kwargs)
        with patch.object(Node, '__init__', init):
            self.follower = PathFollower()
        self.observer = Node('observer', namespace=self.namespace)
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.follower)
        self.executor.add_node(self.observer)
        self.commands = []
        self.observer.create_subscription(Twist, 'cmd', self.commands.append, 10)
        self.path_pub = self.observer.create_publisher(
            PathWithMetadata, 'metadata', metadata_qos())
        self.pose_pub = self.observer.create_publisher(Odometry, 'odom', 10)
        reliability = ReliabilityPolicy.RELIABLE if reliable else ReliabilityPolicy.BEST_EFFORT
        self.cloud_pub = self.observer.create_publisher(
            PointCloud2, 'obstacles',
            QoSProfile(depth=5, reliability=reliability))
        self.static = StaticTransformBroadcaster(self.observer)
        self.dynamic = TransformBroadcaster(self.observer)
        value = TransformStamped()
        value.header.frame_id, value.child_frame_id = 'map', 'odom'
        value.transform.rotation.w = 1.0
        self.static.sendTransform(value)
        self.until(lambda: (self.cloud_pub.get_subscription_count() and
                            self.path_pub.get_subscription_count() and
                            self.pose_pub.get_subscription_count()))
        self.until(lambda: self.follower.odometry.buffer.can_transform(
            'map', 'odom', rclpy.time.Time()))

    def until(self, condition, timeout=6):
        deadline = time.monotonic() + timeout
        while not condition() and time.monotonic() < deadline:
            self.executor.spin_once(timeout_sec=0.01)
        assert condition(), 'isolated ROS condition timed out'

    def pose(self, x=0):
        message = Odometry()
        message.header.frame_id, message.child_frame_id = 'odom', 'base_link'
        message.header.stamp = self.follower.get_clock().now().to_msg()
        message.pose.pose.orientation.w = 1.0
        message.pose.pose.position.x = float(x)
        self.pose_pub.publish(message)
        self.until(lambda: self.follower.odometry.latest == message)

    def path(self, goal=2):
        header = Header(frame_id='map')
        header.stamp = self.follower.get_clock().now().to_msg()
        poses = [PoseStamped(header=copy.deepcopy(header)) for _ in range(2)]
        for value in poses:
            value.pose.orientation.w = 1.0
        poses[1].pose.position.x = float(goal)
        message = PathWithMetadata(path=RosPath(header=header, poses=poses), narrow=[False, True])
        self.path_pub.publish(message)
        self.until(lambda: self.follower.current_path == poses)
        return message

    def cloud(self, points=(), frame='base_link'):
        header = Header(frame_id=frame)
        header.stamp = self.follower.get_clock().now().to_msg()
        return create_cloud_xyz32(header, points)

    def send(self, message=None, state='ACTIVE'):
        self.cloud_pub.publish(message if message is not None else self.cloud())
        self.until(lambda: self.follower.obstacle_monitor.state == state)

    def stopped(self):
        count = len(self.commands)
        self.until(lambda: len(self.commands) >= count + 2)
        assert all(zero(m) for m in self.commands[-2:])

    def moving(self):
        count = len(self.commands)
        self.until(lambda: len(self.commands) > count and self.commands[-1].linear.x > 0)
        assert self.commands[-1].linear.x == pytest.approx(
            self.follower.max_linear_speed * self.follower.narrow_speed_factor)

    def close(self):
        self.executor.shutdown()
        self.follower.destroy_node()
        self.observer.destroy_node()


@pytest.fixture
def harness():
    rclpy.init()
    instances = []

    def create(**kwargs):
        instance = Harness(**kwargs)
        instances.append(instance)
        return instance
    try:
        yield create
    finally:
        for instance in instances:
            instance.close()
        rclpy.shutdown()


def test_waiting_stop_recovery_loss_and_new_invalid_data(harness):
    item = harness()
    item.pose()
    item.path()
    assert item.follower.obstacle_monitor.state == 'WAITING_FOR_DATA'
    item.stopped()
    item.send()
    item.moving()
    item.until(lambda: item.follower.obstacle_monitor.state == 'STALE_DATA', timeout=3)
    item.stopped()
    invalid = item.cloud()
    invalid.fields = []
    item.send(invalid, 'INVALID_DATA')
    item.stopped()
    item.pose()
    item.send()
    item.moving()


@pytest.mark.parametrize('fault', ['missing_path', 'invalid_path', 'pose', 'obstacle', 'goal'])
def test_recovery_preserves_every_existing_stop_condition(harness, fault):
    item = harness()
    item.pose()
    message = item.path()
    item.send()
    item.moving()
    item.send(item.cloud([[0.3, 0, 0]]), 'BLOCKED')
    item.stopped()
    if fault == 'missing_path':
        item.path_pub.publish(PathWithMetadata(path=RosPath(header=Header(frame_id='map'))))
        item.until(lambda: not item.follower.current_path)
    elif fault == 'invalid_path':
        message.narrow.pop()
        item.path_pub.publish(message)
        item.until(lambda: not item.follower.current_path)
    elif fault == 'pose':
        item.pose_pub.publish(Odometry())
        item.until(lambda: item.follower.odometry.latest is None)
    elif fault == 'goal':
        item.pose(2)
    else:
        item.send(item.cloud([[0.3, 0, 0]]), 'BLOCKED')
        item.stopped()
        return
    item.send()
    item.stopped()
    if fault != 'goal':
        item.pose()
        item.path()
        item.send()
        item.moving()


def test_new_metadata_during_stop_replaces_old_path(harness):
    item = harness()
    item.pose()
    item.path(2)
    item.stopped()
    newest = item.path(3)
    item.pose(1.95)
    item.send()
    item.moving()
    assert item.follower.current_path == newest.path.poses
    assert item.follower.current_narrow == newest.narrow


@pytest.mark.parametrize('reliable', [False, True])
def test_external_publisher_qos_replacement_and_subscriber_restart(harness, reliable):
    item = harness(reliable=reliable)
    item.pose()
    item.path()
    item.send()
    item.moving()
    item.observer.destroy_publisher(item.cloud_pub)
    item.until(lambda: item.follower.obstacle_monitor.state == 'STALE_DATA', timeout=3)
    item.stopped()
    item.cloud_pub = item.observer.create_publisher(
        PointCloud2, 'obstacles', QoSProfile(depth=5, reliability=(
            ReliabilityPolicy.BEST_EFFORT if reliable else ReliabilityPolicy.RELIABLE)))
    item.until(lambda: item.cloud_pub.get_subscription_count() > 0)
    item.pose()
    item.send()
    item.moving()
    item.follower.destroy_subscription(item.follower.obstacle_sub)
    item.follower.obstacle_sub = item.follower.create_subscription(
        PointCloud2, 'obstacles', item.follower.obstacle_callback,
        QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT))
    item.until(lambda: item.cloud_pub.get_subscription_count() > 0)
    item.send()
    item.moving()


def test_native_static_tf_and_dynamic_wrong_measurement_time(harness):
    item = harness()
    item.pose()
    item.path()
    item.send(item.cloud(frame='sensor'), 'TF_UNAVAILABLE')
    item.stopped()
    value = TransformStamped()
    value.header.frame_id, value.child_frame_id = 'base_link', 'sensor'
    value.transform.rotation.w = 1.0
    value.transform.translation.x = 0.3
    item.static.sendTransform(value)
    item.until(lambda: item.follower.odometry.buffer.can_transform(
        'base_link', 'sensor', rclpy.time.Time()))
    item.send(item.cloud([[0, 0, 0]], frame='sensor'), 'BLOCKED')
    item.stopped()
    item.pose()
    item.send(item.cloud(frame='sensor'))
    item.moving()
    message = item.cloud(frame='dynamic_sensor')
    value.child_frame_id = 'dynamic_sensor'
    value.header.stamp = copy.deepcopy(message.header.stamp)
    value.header.stamp.sec -= 2
    item.dynamic.sendTransform(value)
    item.until(lambda: item.follower.odometry.buffer.can_transform(
        'base_link', 'dynamic_sensor', rclpy.time.Time()))
    item.send(message, 'TF_UNAVAILABLE')
    item.stopped()
    value.header.stamp = copy.deepcopy(message.header.stamp)
    item.dynamic.sendTransform(value)
    item.until(lambda: item.follower.odometry.buffer.can_transform(
        'base_link', 'dynamic_sensor', rclpy.time.Time.from_msg(message.header.stamp)))
    # The failed sample did not become clearance when TF appeared: resend new valid data.
    item.stopped()
    message = item.cloud(frame='dynamic_sensor')
    value.header.stamp = copy.deepcopy(message.header.stamp)
    item.dynamic.sendTransform(value)
    item.until(lambda: item.follower.odometry.buffer.can_transform(
        'base_link', 'dynamic_sensor', rclpy.time.Time.from_msg(message.header.stamp)))
    item.pose()
    item.send(message)
    item.moving()


@pytest.mark.parametrize('enabled', [False, True])
def test_optional_internal_filter_and_nonfinite_only_input(harness, enabled):
    item = harness(enabled=enabled)
    item.pose()
    item.path()
    original = Node.__init__

    def init(node, *args, **kwargs):
        kwargs['namespace'] = item.namespace
        kwargs['cli_args'] = ['--ros-args', '-r', '/local/filtered_obstacles:=obstacles']
        original(node, *args, **kwargs)
    with patch.object(Node, '__init__', init):
        local = ObstacleCliffFilter()
    item.executor.add_node(local)
    source = item.observer.create_publisher(
        PointCloud2, '/hesai_ros_driver/hesai/lidar_points',
        QoSProfile(depth=5, reliability=ReliabilityPolicy.BEST_EFFORT))
    try:
        item.until(lambda: source.get_subscription_count() > 0 and
                   local.pub_obstacles.get_subscription_count() > 0)
        source.publish(item.cloud([[2, 0, 0.2]]))
        item.until(lambda: item.follower.obstacle_monitor.state == 'ACTIVE' if enabled else
                   not item.follower.obstacle_in_front)
        item.moving()
        source.publish(item.cloud([[math.nan, 0, 0]]))
        if enabled:
            item.until(lambda: item.follower.obstacle_monitor.state == 'STALE_DATA', timeout=3)
            item.stopped()
        else:
            # Monitoring disabled still responds to the filter's real obstacles.
            local.min_reliable_distance = 0.1
            source.publish(item.cloud([[0.3, 0, 0.2]]))
            item.until(lambda: item.follower.obstacle_in_front)
            item.stopped()
    finally:
        item.executor.remove_node(local)
        local.destroy_node()


def test_disabled_monitor_retains_obstacles_pose_and_path_conditions(harness):
    item = harness(enabled=False)
    item.pose()
    item.path()
    item.moving()
    assert item.follower.timer.clock.clock_type == ClockType.ROS_TIME
    item.cloud_pub.publish(item.cloud([[0.3, 0, 0]]))
    item.until(lambda: item.follower.obstacle_in_front)
    item.stopped()
    item.pose()
    item.cloud_pub.publish(item.cloud())
    item.until(lambda: not item.follower.obstacle_in_front)
    item.moving()
    item.pose_pub.publish(Odometry())
    item.until(lambda: item.follower.odometry.latest is None)
    item.stopped()


def test_paused_simulation_clock_uses_steady_timeout_and_basis_reset(harness):
    from rosgraph_msgs.msg import Clock as ClockMessage
    item = harness(simulation=True)
    clock_pub = item.observer.create_publisher(ClockMessage, '/clock', 10)
    item.until(lambda: clock_pub.get_subscription_count() > 0)
    clock = ClockMessage()
    clock.clock.sec = 10
    clock_pub.publish(clock)
    item.until(lambda: item.follower.get_clock().now().nanoseconds == 10**10)
    item.pose()
    item.path()
    item.send()
    item.moving()
    assert item.follower.timer.clock.clock_type == ClockType.STEADY_TIME
    item.until(lambda: item.follower.obstacle_monitor.state == 'STALE_DATA', timeout=3)
    item.stopped()
    item.send(item.cloud(), 'INVALID_DATA')  # Replay at frozen ROS time cannot refresh receipt.
    item.stopped()
    clock.clock.sec = 9
    clock_pub.publish(clock)
    item.until(lambda: item.follower.obstacle_monitor.state == 'CLOCK_ERROR')
    item.stopped()
    item.pose()
    item.send()
    item.moving()
    clock.clock.sec = 15
    clock_pub.publish(clock)
    item.until(lambda: item.follower.obstacle_monitor.state == 'CLOCK_ERROR')
    item.stopped()
    item.pose()
    item.send()
    item.moving()
    # Switching time basis invalidates the old measurement even before new obstacle input.
    result = item.follower.set_parameters([Parameter('use_sim_time', value=False)])
    assert result[0].successful
    item.until(lambda: item.follower.obstacle_monitor.state == 'CLOCK_ERROR')
    item.stopped()
    item.pose()
    item.send()
    item.moving()


def test_monitor_parameters_readonly_and_installed_import(harness):
    item = harness()
    result = item.follower.set_parameters([
        Parameter('obstacle_monitoring.enabled', value=False)])
    assert not result[0].successful
    import r3d_planner.obstacle_monitor as module
    if os.environ.get('R3D_EXPECT_NO_SOURCE') == '1':
        assert_installed_module('r3d_planner', module.__file__)
        assert not Path('/r3d-source').exists()
    assert not item.follower.count_publishers('/cmd_vel')
    assert item.follower.obstacle_sub.topic_name == item.namespace + '/obstacles'
    assert item.follower.obstacle_sub.qos_profile.depth == 5


@pytest.mark.installed
@pytest.mark.parametrize('mode', ['enabled', 'disabled', 'legacy'])
def test_installed_launch_external_config_parameters_and_no_filter(tmp_path, mode):
    from rcl_interfaces.srv import GetParameters
    share = Path(get_package_share_directory('r3d_planner'))/'config'
    cfg = yaml.safe_load((share/'planner_config.yaml').read_text())
    robot = yaml.safe_load((share/'robots/Go2W.yaml').read_text())
    namespace = 'm02launch_' + uuid.uuid4().hex[:8]
    (tmp_path/'robots').mkdir()
    (tmp_path/'map.pcd').write_text('configuration fixture; follower does not open maps')
    cfg['maps'] = {'pcd_path': 'map.pcd', 'map_name': 'map.pcd'}
    cfg['components']['live_filter']['enabled'] = False
    cfg['components']['rviz_interface']['enabled'] = False
    if mode == 'legacy':
        del cfg['path_follower']['obstacle_monitoring']
    else:
        cfg['path_follower']['obstacle_monitoring'] = {
            'enabled': mode == 'enabled', 'timeout_sec': 0.4,
            'require_transform': False, 'topic': 'external_obstacles'}
    robot['robot']['topics']['cmd_vel'] = '/' + namespace + '/cmd'
    robot['robot']['odometry']['topic'] = '/' + namespace + '/odom'
    (tmp_path/'planner_config.yaml').write_text(yaml.safe_dump(cfg))
    (tmp_path/'robots/Go2W.yaml').write_text(yaml.safe_dump(robot))
    env = {**os.environ, 'R3D_CONFIG_DIR': str(tmp_path)}
    rclpy.init()
    observer = Node('launch_observer', namespace=namespace)
    commands = []
    observer.create_subscription(Twist, 'cmd', commands.append, 10)
    output = (tmp_path/'launch.log').open('w')
    process = subprocess.Popen(['ros2', 'launch', 'r3d_planner', 'follower.launch.py',
                                'namespace:=' + namespace], env=env,
                               stdout=output, stderr=subprocess.STDOUT)
    try:
        client = observer.create_client(
            GetParameters, '/' + namespace + '/r3d_path_follower/get_parameters')
        deadline = time.monotonic() + 10
        while not client.service_is_ready() and time.monotonic() < deadline:
            rclpy.spin_once(observer, timeout_sec=0.05)
        assert process.poll() is None, (tmp_path/'launch.log').read_text()
        assert client.service_is_ready()
        request = GetParameters.Request(names=[
            'obstacle_monitoring.enabled', 'obstacle_monitoring.timeout_sec',
            'obstacle_monitoring.require_transform', 'obstacle_monitoring.topic'])
        future = client.call_async(request)
        rclpy.spin_until_future_complete(observer, future, timeout_sec=5)
        assert future.done()
        values = future.result().values
        assert values[0].bool_value is (mode == 'enabled')
        assert values[1].double_value == (1.0 if mode == 'legacy' else 0.4)
        assert values[2].bool_value is (mode == 'legacy')
        assert values[3].string_value == ('/local/filtered_obstacles' if mode == 'legacy'
                                          else 'external_obstacles')
        deadline = time.monotonic() + 3
        while len(commands) < 2 and time.monotonic() < deadline:
            rclpy.spin_once(observer, timeout_sec=0.05)
        assert len(commands) >= 2 and all(zero(m) for m in commands)
        names = {name for name, ns in observer.get_node_names_and_namespaces()
                 if ns == '/' + namespace}
        assert 'r3d_path_follower' in names
        assert 'obstacle_cliff_filter' not in names
        if os.environ.get('R3D_EXPECT_NO_SOURCE') == '1':
            assert not Path('/r3d-source').exists()
            assert not Path('/work/ci/src').exists()
    finally:
        process.terminate()
        try:
            process.wait(timeout=6)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
        output.close()
        observer.destroy_node()
        rclpy.shutdown()
