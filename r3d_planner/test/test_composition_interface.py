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

"""Check namespace composition, sensor reliability and existing TF ownership."""
import copy
import os
from pathlib import Path
import signal
import subprocess
import time
from unittest.mock import Mock

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PointStamped, PoseStamped, TransformStamped
from nav2_msgs.action import ComputePathToPose
from nav_msgs.msg import Odometry, Path as RosPath
import numpy as np
import pytest
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import Header
from tf2_ros import TransformException
import yaml

from r3d_planner.cloud import create_cloud_xyz32
from r3d_planner.configuration import load_configuration
from r3d_planner.odometry import OdometryInput
from r3d_planner.r3d_local_filter import ObstacleCliffFilter
from r3d_planner.r3d_rviz_interface import RVizInterfaceNode


@pytest.fixture
def composed_config(tmp_path):
    share = Path(get_package_share_directory('r3d_planner')) / 'config'
    central = yaml.safe_load((share / 'planner_config.yaml').read_text())
    robot = yaml.safe_load((share / 'robots/Go2W.yaml').read_text())
    (tmp_path / 'robots').mkdir()
    cloud = tmp_path / 'tiny.pcd'
    cloud.write_text('VERSION .7\nFIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F U\n'
                     'COUNT 1 1 1 1\nWIDTH 3\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n'
                     'POINTS 3\nDATA ascii\n0 0 0 65280\n0.05 0 0 65535\n0.1 0 0 65280\n')
    central['maps'] = {'pcd_path': str(cloud), 'map_name': str(cloud)}
    central['components']['live_filter']['enabled'] = False
    central['rviz_interface']['publish_map_odom'] = False
    path = tmp_path / 'planner_config.yaml'

    def save():
        path.write_text(yaml.safe_dump(central))
        (tmp_path / 'robots/Go2W.yaml').write_text(yaml.safe_dump(robot))
    save()
    return path, central, robot, save


@pytest.mark.parametrize('timeout', [None, 0.25, -1.0, True])
def test_relative_robot_topics_and_optional_wait_timeout(composed_config, timeout):
    path, central, robot, save = composed_config
    robot['robot']['odometry']['topic'] = 'odometry'
    robot['robot']['topics'] = {'cmd_vel': 'cmd_vel', 'pointcloud': 'cloud'}
    if timeout is None:
        central['rviz_interface'].pop('action_server_timeout_sec', None)
    else:
        central['rviz_interface']['action_server_timeout_sec'] = timeout
    save()
    if timeout is True or timeout == -1.0:
        with pytest.raises(ValueError):
            load_configuration(path)
    else:
        cfg = load_configuration(path)
        assert cfg['planner']['odometry_topic'] == 'odometry'
        assert cfg['rviz_interface']['action_server_timeout_sec'] == (
            1.0 if timeout is None else timeout)


@pytest.mark.parametrize('fault', ['frame', 'nan', 'quaternion', 'server'])
def test_rviz_rejects_invalid_selection_and_bounded_wait(fault):
    rclpy.init()
    node = RVizInterfaceNode()
    try:
        node.set_parameters([rclpy.parameter.Parameter('publish_map_odom', value=False)])
        # Destroy the real waitable before replacing its public reference.
        node.action_client.destroy()
        node.action_client = Mock()
        node.action_client.wait_for_server.return_value = False
        point = PointStamped(header=Header(frame_id='map'))
        point.point.z = 0.1
        node.point_cb(point)
        goal = PoseStamped(header=Header(frame_id='map'))
        if fault == 'frame':
            goal.header.frame_id = 'odom'
        elif fault == 'nan':
            goal.pose.position.x = float('nan')
        elif fault == 'quaternion':
            goal.pose.orientation.w = 0.0
        node.goal_pose_cb(goal)
        node.action_client.send_goal_async.assert_not_called()
        if fault == 'server':
            node.action_client.wait_for_server.assert_called_once_with(timeout_sec=1.0)
            assert node.latest_point is not None
        else:
            node.action_client.wait_for_server.assert_not_called()
        invalid = copy.deepcopy(point)
        invalid.header.frame_id = 'sensor'
        node.point_cb(invalid)
        assert node.latest_point is None
    finally:
        node.destroy_node()
        rclpy.shutdown()


@pytest.mark.parametrize('fault', ['static', 'missing_tf', 'stale_tf', 'nan_tf',
                                   'zero_tf_q', 'future_odom', 'invalid_pose', 'wrong_frame'])
def test_tf_odometry_contracts(fault):
    rclpy.init()
    node = Node('tf_contract_test')
    source = OdometryInput(node)
    try:
        message = Odometry(header=Header(frame_id='odom'), child_frame_id='base_link')
        message.header.stamp = node.get_clock().now().to_msg()
        if fault == 'future_odom':
            message.header.stamp.sec += 10
        if fault == 'invalid_pose':
            message.pose.pose.orientation.w = 0.0
        if fault == 'wrong_frame':
            message.child_frame_id = 'sensor'
        source.callback(message)
        transform = TransformStamped(header=Header(frame_id='map'), child_frame_id='odom')
        transform.transform.translation.x = 2.0
        if fault == 'stale_tf':
            transform.header.stamp = copy.deepcopy(message.header.stamp)
            transform.header.stamp.sec -= 10
            source.buffer.set_transform(transform, 'synthetic_test')
        elif fault != 'missing_tf':
            source.buffer.set_transform_static(transform, 'synthetic_test')
        if fault in ('nan_tf', 'zero_tf_q'):
            if fault == 'nan_tf':
                transform.transform.translation.x = float('nan')
            else:
                transform.transform.rotation.w = 0.0
            source.buffer.lookup_transform = Mock(return_value=transform)
        if fault == 'static':
            pose = source.map_pose()
            assert pose.pose.position.x == 2.0
            assert pose.header.stamp == message.header.stamp
        else:
            with pytest.raises((ValueError, TransformException)):
                source.map_pose()
    finally:
        node.destroy_node()
        rclpy.shutdown()


@pytest.mark.parametrize('reliability',
                         [ReliabilityPolicy.BEST_EFFORT, ReliabilityPolicy.RELIABLE])
def test_native_sensor_qos_accepts_both_publishers(reliability):
    rclpy.init()
    node = ObstacleCliffFilter()
    producer = Node('qos_cloud_test')
    outputs = []
    try:
        assert node.sub.qos_profile.reliability == ReliabilityPolicy.BEST_EFFORT
        publisher = producer.create_publisher(
            type(create_cloud_xyz32(Header(), [])), node.sub.topic_name,
            QoSProfile(depth=5, reliability=reliability))
        producer.create_subscription(type(create_cloud_xyz32(Header(), [])),
                                     '/local/filtered_obstacles', outputs.append, 10)
        deadline = time.monotonic() + 6
        while not outputs and time.monotonic() < deadline:
            message = create_cloud_xyz32(Header(frame_id='sensor'),
                                         np.array([[0.8, 0.0, 0.1]], dtype=np.float32))
            message.header.stamp = producer.get_clock().now().to_msg()
            publisher.publish(message)
            rclpy.spin_once(node, timeout_sec=0.03)
            rclpy.spin_once(producer, timeout_sec=0.03)
        assert outputs and outputs[-1].width == 1
        assert outputs[-1].header.frame_id == 'sensor'
        assert node.pub_obstacles.qos_profile.reliability == ReliabilityPolicy.RELIABLE
    finally:
        producer.destroy_node()
        node.destroy_node()
        rclpy.shutdown()


def test_native_namespaced_launch_and_remapping(composed_config, monkeypatch):
    path, central, robot, save = composed_config
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    environment = os.environ.copy()
    environment['ROS_LOG_DIR'] = str(path.parent / 'ros-log')
    rclpy.init()
    observer = Node('namespace_contract_observer')
    process = None
    try:
        with (path.parent / 'namespace-launch.log').open('w') as log:
            process = subprocess.Popen(['ros2', 'launch', 'r3d_planner', 'planner.launch.py',
                                        'namespace:=r3d_contract'], stdout=log,
                                       stderr=subprocess.STDOUT, env=environment,
                                       start_new_session=True)
            client = ActionClient(observer, ComputePathToPose,
                                  '/r3d_contract/compute_path_to_pose')
            assert client.wait_for_server(
                timeout_sec=10), (path.parent / 'namespace-launch.log').read_text()
            paths = []
            observer.create_subscription(RosPath, '/r3d_contract/global_path', paths.append, 10)
            message = ComputePathToPose.Goal()
            message.use_start = True
            message.goal.header.frame_id = message.start.header.frame_id = 'map'
            message.goal.pose.position.x = 0.1
            # Wait for the standard path subscription before requesting publication.
            deadline = time.monotonic() + 5
            while not observer.get_publishers_info_by_topic('/r3d_contract/global_path'):
                assert time.monotonic() < deadline
                rclpy.spin_once(observer, timeout_sec=0.05)
            future = client.send_goal_async(message)
            rclpy.spin_until_future_complete(observer, future, timeout_sec=8)
            assert future.done() and future.result().accepted
            result = future.result().get_result_async()
            rclpy.spin_until_future_complete(observer, result, timeout_sec=8)
            assert result.done() and result.result().result.path.poses
            deadline = time.monotonic() + 5
            while not paths and time.monotonic() < deadline:
                rclpy.spin_once(observer, timeout_sec=0.05)
            assert paths and paths[-1] == result.result().result.path
            names = observer.get_node_names_and_namespaces()
            assert ('global_graph_planner', '/r3d_contract') in names
            assert ('r3d_rviz_interface', '/r3d_contract') in names
            assert not observer.get_publishers_info_by_topic('/global_path')
            client.destroy()
    finally:
        if process is not None:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=3)
        observer.destroy_node()
        rclpy.shutdown()


def test_native_explicit_topic_remapping(composed_config):
    from unittest.mock import patch
    from rclpy.parameter import Parameter
    from r3d_planner.r3d_pcd_path import GlobalGraphPlanner
    path, central, robot, save = composed_config
    rclpy.init()
    original = Node.__init__

    def init(node, *args, **kwargs):
        kwargs['parameter_overrides'] = [Parameter('map_name', value=central['maps']['map_name'])]
        kwargs['namespace'] = '/remap_contract'
        kwargs['cli_args'] = ['--ros-args', '-r', '/global_path:=custom/path']
        original(node, *args, **kwargs)
    planner = None
    try:
        with patch.object(Node, '__init__', init):
            planner = GlobalGraphPlanner()
        assert planner.pub_path.topic_name == '/remap_contract/custom/path'
    finally:
        if planner:
            planner._action_server.destroy()
            planner.destroy_node()
        rclpy.shutdown()
