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

"""Check generated stair interfaces, actual ROS callbacks and follower interlocks."""
import copy
import math
import time
import uuid
from unittest.mock import Mock, patch

from geometry_msgs.msg import PoseStamped, Quaternion, TransformStamped
from nav_msgs.msg import Odometry, Path
import networkx as nx
import pytest
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.serialization import deserialize_message, serialize_message
from r3d_interfaces.msg import PathWithMetadata, StairDetection, StairStatus
from std_msgs.msg import Header
from std_srvs.srv import Trigger
import yaml

from r3d_planner.configuration import ConfigurationError, load_configuration, load_robot_profile
from r3d_planner.path_metadata import build_path, path_fingerprint, validate_metadata
from r3d_planner.r3d_path_follower import PathFollower
from r3d_planner.r3d_stair_controller import StairController
from test_stair_control import route


def metadata(node, current=None):
    """Build a real stamped message from the synthetic classified route."""
    current = current or route()
    header = Header(frame_id='map', stamp=node.get_clock().now().to_msg())
    poses = []
    for point in current.positions:
        pose = PoseStamped(header=copy.deepcopy(header))
        pose.pose.position.x, pose.pose.position.y, pose.pose.position.z = point
        pose.pose.orientation.w = 1.0
        poses.append(pose)
    return PathWithMetadata(path=Path(header=header, poses=poses),
                            narrow=[False] * len(poses), stairs=current.stairs)


class FakeSdk:
    """Record requests and require explicit simulated acknowledgement."""

    def __init__(self):
        self.requests = []
        self.result = None

    def start(self, mode, now):
        self.requests.append(mode)

    def poll(self, now):
        result, self.result = self.result, None
        return result

    def close(self):
        pass


@pytest.fixture
def controller(installed_share):
    """Construct the production node with a fake transport and isolated ROS names."""
    rclpy.init()
    original = Node.__init__

    def init(node, *args, **kwargs):
        kwargs['namespace'] = '/stairs_' + uuid.uuid4().hex[:8]
        original(node, *args, **kwargs)
    sdk = FakeSdk()
    with patch.object(Node, '__init__', init), patch(
            'r3d_planner.r3d_stair_controller.SdkSwitch', return_value=sdk):
        node = StairController()
    node.timer.cancel()
    node.status_publisher = Mock()
    node.detection_publisher = Mock()
    transform = TransformStamped()
    transform.header.frame_id, transform.child_frame_id = 'map', 'odom'
    transform.transform.rotation.w = 1.0
    node.odometry.buffer.set_transform_static(transform, 'test')
    try:
        yield node, sdk
    finally:
        node.destroy_node()
        rclpy.shutdown()


def odometry(node, x, z=0.5, moving=False):
    """Supply a fresh base pose and measured velocity independently of controller output."""
    message = Odometry()
    message.header.frame_id, message.child_frame_id = 'odom', 'base_link'
    message.header.stamp = node.get_clock().now().to_msg()
    message.pose.pose.orientation.w = 1.0
    message.pose.pose.position.x, message.pose.pose.position.z = float(x), float(z)
    message.twist.twist.linear.x = 0.35 if moving else 0.0
    node.odometry.callback(message)


def tick(node, now, x, z=0.5, moving=False):
    """Advance the production timer callback with fresh data and a deterministic steady clock."""
    odometry(node, x, z, moving)
    if node.coordinator.switching:
        acknowledge_pause(node, now)
    with patch('r3d_planner.r3d_stair_controller.time.monotonic', return_value=now):
        node.tick()
        if node.pending_mode is not None:
            acknowledge_pause(node, now)
            node.tick()


def acknowledge_pause(node, now):
    """Simulate the follower's explicit acknowledgement in controller unit tests."""
    ack = StairStatus(path_id=node.path_id, pause_commands=True, pause_id=node.pause_id)
    ack.header = Header(frame_id='map', stamp=node.get_clock().now().to_msg())
    with patch('r3d_planner.r3d_stair_controller.time.monotonic', return_value=now):
        node.pause_callback(ack)


def test_generated_detection_and_status_roundtrip():
    """Represent detection and explicit no-stair state with a real boolean field."""
    for detected in (True, False):
        message = StairDetection(detected=detected)
        assert deserialize_message(serialize_message(message), StairDetection) == message
    message = StairStatus(path_id='abc', state='STAIRS', motion_allowed=True,
                          stair_mode_active=True)
    assert deserialize_message(serialize_message(message), StairStatus) == message


def test_live_filter_publishes_explicit_detection_with_sensor_header():
    """Keep existing filter criteria while publishing the new explicit interface."""
    from r3d_planner.cloud import create_cloud_xyz32
    from r3d_planner.r3d_local_filter import ObstacleCliffFilter
    rclpy.init()
    node = ObstacleCliffFilter()
    try:
        assert node.pub_stair_detect.msg_type is StairDetection
        node.pub_stair_detect = Mock()
        header = Header(frame_id='lidar', stamp=node.get_clock().now().to_msg())
        cloud = create_cloud_xyz32(header, [[0.9, 0., 0.15]] * 60 + [[0.9, 0., 0.]] * 40)
        node.pc_callback(cloud)
        message = node.pub_stair_detect.publish.call_args.args[0]
        assert message.detected and message.header == header
        assert message.point.x == pytest.approx(0.9)
        assert message.point.z == pytest.approx(0.15)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_planner_marks_stairs_from_classes_and_height_transitions():
    """Carry yellow voxels and traversed step edges into the atomic path metadata."""
    graph = nx.Graph()
    for i, (height, kind) in enumerate([(0., 'floor'), (0., 'stair_access'),
                                       (0.2, 'floor'), (0.2, 'floor')]):
        graph.add_node(i, pos=(i * 0.05, 0., height), type=kind)
    message = build_path(graph, [0, 1, 2, 3], Header(frame_id='map'),
                         Quaternion(w=1.0), 0.05)
    assert message.stairs == [False, True, True, False]
    assert message.narrow == [False] * 4
    validate_metadata(message, 'map', require_stairs=True)
    message.stairs.pop()
    with pytest.raises(ValueError, match='stairs count'):
        validate_metadata(message, 'map')


def test_controller_full_sequence_and_explicit_clear(controller):
    """Exercise actual subscriptions/timer logic with confirmed fake SDK transitions."""
    node, sdk = controller
    node.path_callback(metadata(node))
    tick(node, 0., 0.)
    tick(node, 0.51, 0.)
    assert sdk.requests == ['normal'] and not node.coordinator.motion_allowed
    sdk.result = (True, 'normal confirmed')
    tick(node, 0.6, 0.)
    assert node.coordinator.motion_allowed
    tick(node, 1., 1., moving=True)
    assert node.coordinator.state == 'WAIT_DETECTION'
    detection = StairDetection(detected=True)
    detection.header = Header(frame_id='map', stamp=node.get_clock().now().to_msg())
    detection.point.x = 2.0
    with patch('r3d_planner.r3d_stair_controller.time.monotonic', return_value=1.1):
        node.detection_callback(detection)
    tick(node, 1.1, 1.)
    tick(node, 1.61, 1.)
    assert sdk.requests == ['normal', 'stairs']
    assert not node.coordinator.motion_allowed
    sdk.result = (True, 'stairs confirmed')
    tick(node, 2., 2.1, z=0.7, moving=True)
    assert node.coordinator.motion_allowed and node.coordinator.stair_mode_active
    tick(node, 3., 2.9, z=0.9, moving=True)
    tick(node, 3.5, 3.2, z=0.9, moving=True)
    assert not node.coordinator.motion_allowed
    tick(node, 3.6, 3.2, z=0.9)
    tick(node, 4.11, 3.2, z=0.9)
    assert sdk.requests == ['normal', 'stairs', 'normal']
    sdk.result = (True, 'normal confirmed')
    tick(node, 4.2, 3.2, z=0.9)
    cleared = node.detection_publisher.publish.call_args.args[0]
    assert cleared.detected is False and cleared.header.frame_id == 'map'
    assert node.coordinator.motion_allowed and not node.coordinator.stair_mode_active


@pytest.mark.parametrize('fault', ['missing_odom', 'stale_odom', 'no_tf', 'bad_metadata'])
def test_input_faults_withdraw_permit(controller, fault):
    """Fail closed on missing pose/TF or incomplete terrain classification."""
    node, sdk = controller
    message = metadata(node)
    if fault == 'bad_metadata':
        message.stairs = []
    node.path_callback(message)
    odometry(node, 0.)
    if fault == 'missing_odom':
        node.odometry.latest = None
    elif fault == 'stale_odom':
        node.odometry.latest.header.stamp.sec -= 10
    elif fault == 'no_tf':
        node.odometry.buffer.clear()
    node.tick()
    assert not node.coordinator.motion_allowed and sdk.requests == []


@pytest.mark.parametrize('fault', ['stale', 'future', 'frame', 'nan', 'cleared'])
def test_live_detection_validation(controller, fault):
    """Reject stale, future, untransformable and explicit cleared observations."""
    node, _ = controller
    message = StairDetection(detected=True)
    message.header = Header(frame_id='map', stamp=node.get_clock().now().to_msg())
    message.point.x = 2.0
    if fault == 'stale':
        message.header.stamp.sec -= 10
    elif fault == 'future':
        message.header.stamp.sec += 10
    elif fault == 'frame':
        message.header.frame_id = 'unavailable'
    elif fault == 'nan':
        message.point.x = math.nan
    else:
        message.detected = False
    node.detection_callback(message)
    assert node.matching_detection(time.monotonic()) is None


def test_detection_tf_and_sdk_failure_retry(controller):
    """Use sensor-frame TF and expose an explicit recovery service for SDK failures."""
    node, sdk = controller
    transform = TransformStamped()
    transform.header.frame_id, transform.child_frame_id = 'map', 'lidar'
    transform.transform.rotation.w = 1.0
    transform.transform.translation.x = 1.0
    node.odometry.buffer.set_transform_static(transform, 'test')
    message = StairDetection(detected=True)
    message.header = Header(frame_id='lidar', stamp=node.get_clock().now().to_msg())
    message.point.x = 1.0
    node.detection_callback(message)
    assert node.matching_detection(time.monotonic()) == (2., 0., 0.)
    node.path_callback(metadata(node))
    tick(node, 0., 0.)
    tick(node, 0.51, 0.)
    sdk.result = (False, 'BalanceStand missing')
    tick(node, 0.6, 0.)
    assert node.coordinator.state == 'ERROR' and not node.coordinator.motion_allowed
    response = node.retry_callback(Trigger.Request(), Trigger.Response())
    assert response.success


@pytest.fixture
def gated_follower(installed_share):
    """Create the actual interlocked follower with isolated velocity output."""
    rclpy.init()
    original = Node.__init__

    def init(node, *args, **kwargs):
        kwargs['namespace'] = '/stair_gate_' + uuid.uuid4().hex[:8]
        kwargs['parameter_overrides'] = [
            Parameter('stair_control_enabled', value=True),
            Parameter('cmd_vel_topic', value='cmd')]
        original(node, *args, **kwargs)
    with patch.object(Node, '__init__', init):
        node = PathFollower()
    node.timer.cancel()
    node.cmd_pub = Mock()
    try:
        yield node
    finally:
        node.destroy_node()
        rclpy.shutdown()


@pytest.mark.parametrize('fault', ['missing', 'denied', 'expired', 'wrong_path', 'wrong_frame',
                                   'future', 'changed_terrain'])
def test_actual_follower_permit_gates_all_velocity_commands(fault, gated_follower):
    """Require a fresh exact-path permit and stop immediately when it is revoked."""
    node = gated_follower
    node.cmd_pub = Mock()
    message = metadata(node)
    node.path_callback(message)
    node.get_robot_pose = lambda: (0., 0., 0.)
    status = StairStatus(path_id=path_fingerprint(message), motion_allowed=True)
    status.header = Header(frame_id='map', stamp=node.get_clock().now().to_msg())
    node.stair_status_callback(status)
    node.control_loop()
    assert node.cmd_pub.publish.call_args.args[0].linear.x > 0
    if fault == 'missing':
        node.stair_status = None
    elif fault == 'denied':
        status.motion_allowed = False
        node.stair_status_callback(status)
        assert node.cmd_pub.publish.call_args.args[0].linear.x == 0
    elif fault == 'expired':
        node.stair_status_received -= 1.0
    elif fault == 'wrong_path':
        status.path_id = 'other'
    elif fault == 'wrong_frame':
        status.header.frame_id = 'odom'
    elif fault == 'future':
        status.header.stamp.sec += 10
    else:
        changed = copy.deepcopy(message)
        changed.stairs[0] = True
        node.path_callback(changed)
    node.control_loop()
    command = node.cmd_pub.publish.call_args.args[0]
    assert command.linear.x == 0 and command.angular.z == 0


def test_follower_pause_ack_suppresses_zero_twists_and_expires(gated_follower):
    """Pause cmd_vel during BalanceStand and restore zeros if the controller disappears."""
    node = gated_follower
    message = metadata(node)
    node.path_callback(message)
    node.get_robot_pose = lambda: (0., 0., 0.)
    node.stair_ack_publisher = Mock()
    status = StairStatus(path_id=path_fingerprint(message), pause_commands=True, pause_id=42)
    status.header = Header(frame_id='map', stamp=node.get_clock().now().to_msg())
    node.cmd_pub.reset_mock()
    node.stair_status_callback(status)
    node.control_loop()
    node.cmd_pub.publish.assert_not_called()
    ack = node.stair_ack_publisher.publish.call_args.args[0]
    assert ack.pause_commands and ack.pause_id == 42 and ack.path_id == status.path_id
    node.stair_status_received -= 1.0
    node.control_loop()
    assert node.cmd_pub.publish.call_args.args[0].linear.x == 0


def test_controller_waits_for_exact_pause_ack_before_sdk(controller):
    """Require an acknowledgement for the current transition and enforce its timeout."""
    node, sdk = controller
    node.path_callback(metadata(node))
    odometry(node, 0.)
    with patch('r3d_planner.r3d_stair_controller.time.monotonic', return_value=0.):
        node.tick()
    with patch('r3d_planner.r3d_stair_controller.time.monotonic', return_value=0.51):
        node.tick()
    assert node.pending_mode == 'normal' and sdk.requests == []
    acknowledge_pause(node, 0.6)
    node.pause_ack.pause_id -= 1
    with patch('r3d_planner.r3d_stair_controller.time.monotonic', return_value=0.6):
        node.tick()
    assert sdk.requests == []
    with patch('r3d_planner.r3d_stair_controller.time.monotonic', return_value=1.6):
        node.tick()
    assert node.coordinator.state == 'ERROR' and sdk.requests == []


def test_sdk_operation_aborts_when_pause_ack_is_lost(controller):
    """Stop the external operation if the follower stops confirming its pause."""
    node, sdk = controller
    node.path_callback(metadata(node))
    tick(node, 0., 0.)
    tick(node, 0.51, 0.)
    assert sdk.requests == ['normal']
    odometry(node, 0.)
    with patch('r3d_planner.r3d_stair_controller.time.monotonic', return_value=1.1):
        node.tick()
    assert node.coordinator.state == 'ERROR' and not node.coordinator.switching


@pytest.mark.parametrize('value', [0, -1, True, '1', math.inf, None])
@pytest.mark.parametrize('key', ['approach_distance_m', 'exit_distance_m'])
def test_robot_distance_validation(installed_share, tmp_path, monkeypatch, value, key):
    """Validate both robot-specific distances using the production YAML loader."""
    central = yaml.safe_load((installed_share / 'config/planner_config.yaml').read_text())
    robot = yaml.safe_load((installed_share / 'config/robots/Go2W.yaml').read_text())
    (tmp_path / 'robots').mkdir()
    robot['robot']['stairs'][key] = value
    (tmp_path / 'planner_config.yaml').write_text(yaml.safe_dump(central))
    (tmp_path / 'robots/Go2W.yaml').write_text(yaml.safe_dump(robot))
    monkeypatch.setenv('R3D_CONFIG_DIR', str(tmp_path))
    with pytest.raises(ConfigurationError):
        load_robot_profile()


def test_custom_distances_forwarded_to_installed_follower_launch(installed_share, tmp_path):
    """Forward the selected robot settings and enable the follower interlock in launch."""
    from launch import LaunchContext
    from r3d_planner.launching import configured_nodes
    central = yaml.safe_load((installed_share / 'config/planner_config.yaml').read_text())
    robot = yaml.safe_load((installed_share / 'config/robots/Go2W.yaml').read_text())
    central['maps']['map_name'] = str(tmp_path / 'map.pcd')
    (tmp_path / 'map.pcd').touch()
    (tmp_path / 'robots').mkdir()
    robot['robot']['stairs'] = {'approach_distance_m': 0.9, 'exit_distance_m': 1.4}
    path = tmp_path / 'planner_config.yaml'
    path.write_text(yaml.safe_dump(central))
    (tmp_path / 'robots/Go2W.yaml').write_text(yaml.safe_dump(robot))
    cfg = load_configuration(path, mode='follower')
    assert cfg['stair_controller']['approach_distance_m'] == 0.9
    assert cfg['stair_controller']['exit_distance_m'] == 1.4
    context = LaunchContext()
    with patch('r3d_planner.launching.load_configuration', return_value=cfg):
        nodes = configured_nodes(context, 'follower')[1:]
    assert len(nodes) == 2
    assert nodes[0].node_executable == 'stair_controller'
    assert nodes[1].node_executable == 'path_follower'


def test_native_dds_detection_permit_and_heartbeat_loss(installed_share):
    """Pass the new interfaces over DDS and stop after a controller heartbeat disappears."""
    rclpy.init()
    original = Node.__init__
    namespace = '/stair_dds_' + uuid.uuid4().hex[:8]

    def init(node, *args, **kwargs):
        kwargs['namespace'] = namespace
        kwargs['cli_args'] = ['--ros-args', '-r', '/stair_control:=permit',
                              '-r', '/stair_detect:=detection',
                              '-r', '/stair_command_ack:=ack',
                              '-r', '/global_path_metadata:=path']
        if args and args[0] == 'r3d_path_follower':
            kwargs['parameter_overrides'] = [
                Parameter('stair_control_enabled', value=True),
                Parameter('cmd_vel_topic', value='cmd')]
        original(node, *args, **kwargs)
    node = follower = observer = None
    try:
        with patch.object(Node, '__init__', init), patch(
                'r3d_planner.r3d_stair_controller.SdkSwitch', return_value=FakeSdk()):
            node = StairController()
            follower = PathFollower()
        node.timer.cancel()
        follower.timer.cancel()
        follower.cmd_pub = Mock()
        follower.get_robot_pose = lambda: (0., 0., 0.)
        observer = Node('stair_dds_observer', namespace=namespace)
        from r3d_planner.path_metadata import metadata_qos
        path_publisher = observer.create_publisher(PathWithMetadata, 'path', metadata_qos())
        detection_publisher = observer.create_publisher(StairDetection, 'detection', 10)
        message = metadata(node)
        path_publisher.publish(message)
        deadline = time.monotonic() + 6
        while (node.route is None or not follower.current_path) and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.02)
            rclpy.spin_once(follower, timeout_sec=0.02)
        assert node.route is not None and follower.current_path
        detection = StairDetection(detected=True)
        detection.header = Header(frame_id='map', stamp=node.get_clock().now().to_msg())
        detection.point.x = 2.0
        deadline = time.monotonic() + 6
        while node.detection is None and time.monotonic() < deadline:
            detection_publisher.publish(detection)
            rclpy.spin_once(node, timeout_sec=0.03)
        assert node.detection.detected
        node.coordinator.switching = True
        node.pause_id = 123
        deadline = time.monotonic() + 6
        while not node.pause_confirmed(time.monotonic()) and time.monotonic() < deadline:
            node.publish_status()
            rclpy.spin_once(follower, timeout_sec=0.02)
            rclpy.spin_once(node, timeout_sec=0.02)
        assert node.pause_confirmed(time.monotonic())
        assert node.pause_ack.pause_id == 123
        node.coordinator.switching = False
        node.coordinator.state = 'NORMAL'
        node.coordinator.motion_allowed = True
        deadline = time.monotonic() + 6
        while follower.stair_status is None and time.monotonic() < deadline:
            node.publish_status()
            rclpy.spin_once(follower, timeout_sec=0.03)
        assert follower.stair_status is not None
        # A preceding path callback can have sent a deny permit. Send a fresh allow.
        for _ in range(10):
            node.publish_status()
            rclpy.spin_once(follower, timeout_sec=0.02)
        follower.control_loop()
        assert follower.cmd_pub.publish.call_args.args[0].linear.x > 0
        time.sleep(0.55)
        follower.control_loop()
        command = follower.cmd_pub.publish.call_args.args[0]
        assert command.linear.x == 0 and command.angular.z == 0
    finally:
        if node:
            node.destroy_node()
        if follower:
            follower.destroy_node()
        if observer:
            observer.destroy_node()
        rclpy.shutdown()
