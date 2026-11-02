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

"""Exercise profile-owned limits through real loaders, ROS nodes and installed launches."""
from contextlib import contextmanager
import copy
import math
import os
from pathlib import Path as FilePath
import signal
import subprocess
import time
import uuid
from unittest.mock import Mock, patch

import pytest
import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path
from rclpy.exceptions import InvalidParameterTypeException
from rclpy.node import Node
from rclpy.parameter import Parameter
from r3d_interfaces.msg import PathWithMetadata
from std_msgs.msg import Header
import yaml

import test_configuration as configuration_tests
import r3d_planner.configuration as configuration_module
from r3d_planner.configuration import ConfigurationError, load_configuration, load_robot_profile
from r3d_planner.r3d_path_follower import PathFollower


config = configuration_tests.config
_parameter_dump = configuration_tests._parameter_dump


@contextmanager
def follower(parameters=None):
    """Construct the actual follower with its actual profile loader in an isolated namespace."""
    rclpy.init()
    node = None
    original = Node.__init__
    values = dict(parameters or {})
    values.update(cmd_vel_topic='cmd', odometry_topic='odom')

    def init(instance, *args, **kwargs):
        kwargs['namespace'] = '/speed_' + uuid.uuid4().hex[:10]
        kwargs['parameter_overrides'] = [Parameter(k, value=v) for k, v in values.items()]
        original(instance, *args, **kwargs)
    try:
        with patch.object(Node, '__init__', init):
            node = PathFollower()
        node.timer.cancel()
        yield node
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


def path_for(node, angle=0.0, narrow=False):
    """Feed a valid atomic path through the production metadata callback."""
    header = Header(frame_id='map')
    header.stamp = node.get_clock().now().to_msg()
    poses = [PoseStamped(header=copy.deepcopy(header)) for _ in range(2)]
    for pose in poses:
        pose.pose.orientation.w = 1.0
    poses[1].pose.position.x = 2 * math.cos(angle)
    poses[1].pose.position.y = 2 * math.sin(angle)
    message = PathWithMetadata(path=Path(header=header, poses=poses),
                               narrow=[False, narrow])
    node.path_callback(message)
    node.get_robot_pose = lambda: (0.0, 0.0, 0.0)


def test_installed_schema_and_default_profile(installed_share, monkeypatch):
    """Check real installed YAML values and the default package-share lookup."""
    monkeypatch.delenv('R3D_CONFIG_DIR', raising=False)
    central = yaml.safe_load((installed_share/'config/planner_config.yaml').read_text())
    source = installed_share/'config/robots/Go2W.yaml'
    robot = yaml.safe_load(source.read_text())['robot']
    assert robot['velocity_limits'] == {
        'max_linear_speed': 0.35, 'max_angular_speed': 0.6,
        'max_angular_speed_narrow': 0.2, 'narrow_speed_factor': 0.4}
    assert not set(robot['velocity_limits']) & central['path_follower'].keys()
    assert all(type(x) in (int, float) and math.isfinite(x)
               for x in robot['velocity_limits'].values())
    actual_path, selected = load_robot_profile()
    live = FilePath(configuration_module.__file__).resolve().parent.parent / (
        'config/planner_config.yaml')
    expected = live.parent/'robots/Go2W.yaml' if live.is_file() else source
    assert actual_path.resolve() == expected.resolve()
    if os.environ.get('R3D_EXPECT_NO_SOURCE') == '1':
        assert not live.is_file()
        assert actual_path.resolve() == source.resolve()
    assert selected == robot
    with follower() as node:
        assert node.max_linear_speed == 0.35
        assert node.max_angular_speed == 0.6
        assert node.max_angular_speed_narrow == 0.2
        assert node.narrow_speed_factor == 0.4


@pytest.mark.parametrize('key', ['max_linear_speed', 'max_angular_speed',
                                 'max_angular_speed_narrow', 'narrow_speed_factor'])
@pytest.mark.parametrize('bad', [None, '0.35', -0.1, 0, math.nan, math.inf,
                                 -math.inf, True, False, [], {}])
def test_invalid_profile_value_never_creates_command_publisher(config, monkeypatch, key, bad):
    """Reject bad values through both real loaders and before a ROS command publisher."""
    path, central, robot, save = config
    robot['robot']['velocity_limits'][key] = bad
    save()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    for operation in (lambda: load_configuration(path, mode='follower'),
                      lambda: load_robot_profile(path), PathFollower):
        with patch.object(PathFollower, 'create_publisher') as publish:
            with pytest.raises(ConfigurationError):
                operation()
            publish.assert_not_called()


@pytest.mark.parametrize('key', ['max_linear_speed', 'max_angular_speed',
                                 'max_angular_speed_narrow', 'narrow_speed_factor'])
@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'legacy_global'])
def test_missing_duplicate_and_old_global_are_not_fallbacks(config, monkeypatch, key, fault):
    """Require each selected profile field even if old global Go2W values remain."""
    path, central, robot, save = config
    if fault != 'duplicate':
        del robot['robot']['velocity_limits'][key]
    if fault == 'legacy_global':
        central['path_follower'].update(max_linear_speed=0.35, max_angular_speed=0.6)
    save()
    if fault == 'duplicate':
        profile = path.parent/'robots/Go2W.yaml'
        lines = profile.read_text().splitlines()
        index = next(i for i, line in enumerate(lines) if line.strip().startswith(key+':'))
        lines.insert(index+1, lines[index])
        profile.write_text('\n'.join(lines)+'\n')
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with pytest.raises(ConfigurationError):
        load_configuration(path, mode='follower')
    with pytest.raises(ConfigurationError):
        PathFollower()


@pytest.mark.parametrize('fault', ['missing_file', 'escape', 'absolute', 'wrong_mapping',
                                   'missing_group', 'null_group', 'list_group'])
def test_wrong_selected_profile_has_no_go2w_fallback(config, monkeypatch, fault):
    """Keep a valid Go2W file present while rejecting an invalid selected profile."""
    path, central, robot, save = config
    if fault == 'missing_file':
        central['robot_config'] = 'robots/unavailable.yaml'
    elif fault == 'escape':
        central['robot_config'] = '../Go2W.yaml'
    elif fault == 'absolute':
        central['robot_config'] = str(path.parent/'robots/Go2W.yaml')
    elif fault == 'wrong_mapping':
        central['robot_config'] = 'robots/wrong.yaml'
        (path.parent/'robots/wrong.yaml').write_text('robot: []\n')
    elif fault == 'missing_group':
        del robot['robot']['velocity_limits']
    else:
        robot['robot']['velocity_limits'] = None if fault == 'null_group' else []
    save()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with pytest.raises(ConfigurationError):
        load_configuration(path, mode='follower')
    with pytest.raises(ConfigurationError):
        PathFollower()


@pytest.mark.parametrize('key', ['max_linear_speed', 'max_angular_speed',
                                 'max_angular_speed_narrow', 'narrow_speed_factor'])
def test_valid_profile_rejects_leftover_global_values(config, key):
    """Do not assign a precedence to contradictory old global definitions."""
    path, central, robot, save = config
    central['path_follower'][key] = 9.0
    save()
    with pytest.raises(ConfigurationError, match='unknown keys'):
        load_configuration(path, mode='follower')
    assert load_robot_profile(path)[1]['velocity_limits'][key] == robot['robot'][
        'velocity_limits'][key]


@pytest.mark.parametrize('key', ['max_linear_speed', 'max_angular_speed',
                                 'max_angular_speed_narrow', 'narrow_speed_factor'])
@pytest.mark.parametrize('value', [0.9, 0.0, math.nan, math.inf, -0.1, '0.35', True])
def test_ros_override_cannot_replace_profile(config, monkeypatch, key, value):
    """Reject changed startup values rather than silently accepting another authority."""
    path, central, robot, save = config
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with pytest.raises((ConfigurationError, InvalidParameterTypeException)):
        with follower({key: value}):
            pytest.fail('A conflicting speed override constructed a live follower')


@pytest.mark.parametrize('key', ['max_linear_speed', 'max_angular_speed',
                                 'max_angular_speed_narrow', 'narrow_speed_factor'])
def test_ros_profile_values_are_read_only(config, monkeypatch, key):
    """Preserve visible typed ROS parameters without a runtime source conflict."""
    path, central, robot, save = config
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    values = load_configuration(path, mode='follower')['path_follower']
    with follower(values) as node:
        assert node.describe_parameter(key).read_only
        assert node.get_parameter(key).type_ == Parameter.Type.DOUBLE
        previous = node.get_parameter(key).value
        result = node.set_parameters([Parameter(key, value=previous*0.5)])[0]
        assert not result.successful
        assert node.get_parameter(key).value == previous
        assert getattr(node, key) == previous


@pytest.mark.parametrize('fault', ['low_angular', 'high_narrow', 'bad_factor'])
def test_inconsistent_tuning_is_rejected_without_new_clamping(config, monkeypatch, fault):
    """A separate narrow cap or scaling factor may not exceed the robot bounds."""
    path, central, robot, save = config
    if fault == 'low_angular':
        robot['robot']['velocity_limits']['max_angular_speed'] = 0.1
    elif fault == 'high_narrow':
        robot['robot']['velocity_limits']['max_angular_speed_narrow'] = 0.7
    else:
        central['path_follower']['turning_speed_factor'] = 1.1
    save()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with pytest.raises(ConfigurationError):
        load_configuration(path, mode='follower')
    with pytest.raises(ConfigurationError):
        with follower({'turning_speed_factor': central['path_follower'][
                'turning_speed_factor']}):
            pytest.fail('Inconsistent tuning accepted')


@pytest.mark.parametrize('angle,narrow,expected_x,expected_z', [
    (0.0, False, 0.35, 0.0), (0.1, False, 0.35, 0.15),
    (0.4, False, 0.35, 0.6), (0.8, False, 0.105, 0.6),
    (-0.8, False, 0.105, -0.6), (0.1, True, 0.14, 0.15),
    (0.4, True, 0.14, 0.2), (0.8, True, 0.0, 0.2)])
def test_actual_go2w_control_outputs_unchanged(config, monkeypatch, angle, narrow,
                                               expected_x, expected_z):
    """Compare every control branch against explicit pre-migration Go2W outputs."""
    path, central, robot, save = config
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with follower() as node:
        path_for(node, angle, narrow)
        node.cmd_pub = Mock()
        node.control_loop()
        message = node.cmd_pub.publish.call_args.args[0]
        assert message.linear.x == pytest.approx(expected_x)
        assert message.angular.z == pytest.approx(expected_z)
        assert (message.linear.y, message.linear.z, message.angular.x, message.angular.y) == (
            0.0, 0.0, 0.0, 0.0)


@pytest.mark.parametrize('stop', ['no_path', 'obstacle', 'no_pose', 'goal'])
def test_existing_zero_commands_remain_zero(config, monkeypatch, stop):
    """Retain path, obstacle, odometry and goal stop branches using the real controller."""
    path, central, robot, save = config
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with follower() as node:
        path_for(node)
        if stop == 'no_path':
            node.current_path = []
        elif stop == 'obstacle':
            node.obstacle_in_front = True
        elif stop == 'no_pose':
            node.get_robot_pose = lambda: (None, None, None)
        else:
            node.get_robot_pose = lambda: (2.0, 0.0, 0.0)
        node.cmd_pub = Mock()
        node.control_loop()
        command = node.cmd_pub.publish.call_args.args[0]
        assert all(getattr(vector, axis) == 0 for vector in (command.linear, command.angular)
                   for axis in ('x', 'y', 'z'))


def test_profile_restart_invalid_transition_and_integer_spelling(config, monkeypatch):
    """Reload on each construction; no cache or previous robot's speeds may survive."""
    path, central, robot, save = config
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    for linear, angular in [(0.35, 0.6), (0.52, 0.9), (1, 1)]:
        robot['robot']['velocity_limits'].update(
            max_linear_speed=linear, max_angular_speed=angular)
        save()
        values = load_configuration(path, mode='follower')['path_follower']
        assert all(type(values[key]) is float for key in (
            'max_linear_speed', 'max_angular_speed'))
        with follower(values) as node:
            assert node.max_linear_speed == float(linear)
            assert node.max_angular_speed == float(angular)
        robot['robot']['velocity_limits']['max_linear_speed'] = None
        save()
        with pytest.raises(ConfigurationError):
            PathFollower()


def test_synthetic_selected_profile_controls_real_cmd_vel(config, monkeypatch):
    """Observe actual ROS output from an alternate profile; no publisher mock or fallback."""
    path, central, robot, save = config
    alternate = copy.deepcopy(robot)
    alternate['robot']['name'] = 'SyntheticVelocityTestOnly'
    alternate['robot']['velocity_limits'].update(
        max_linear_speed=0.52, max_angular_speed=0.9)
    (path.parent/'robots/synthetic.yaml').write_text(yaml.safe_dump(alternate))
    central['robot_config'] = 'robots/synthetic.yaml'
    save()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with follower(load_configuration(path, mode='follower')['path_follower']) as node:
        observer = Node('velocity_observer', namespace=node.get_namespace())
        received = []
        observer.create_subscription(Twist, node.cmd_vel_topic, received.append, 10)
        try:
            path_for(node, 0.8)
            deadline = time.monotonic()+5
            while not received and time.monotonic() < deadline:
                node.control_loop()
                rclpy.spin_once(node, timeout_sec=0.01)
                rclpy.spin_once(observer, timeout_sec=0.02)
            assert received
            assert received[-1].linear.x == pytest.approx(0.52*0.3)
            assert received[-1].angular.z == pytest.approx(0.9)
        finally:
            observer.destroy_node()


def test_namespaced_installed_launch_uses_selected_profile(config, monkeypatch):
    """Start the installed follower launch and query the effective profiled ROS parameters."""
    path, central, robot, save = config
    robot['robot']['velocity_limits'].update(
        max_linear_speed=0.52, max_angular_speed=0.9,
        max_angular_speed_narrow=0.12, narrow_speed_factor=0.25)
    robot['robot']['topics']['cmd_vel'] = 'cmd'
    robot['robot']['odometry']['topic'] = 'odom'
    save()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    monkeypatch.setenv('ROS_LOG_DIR', str(path.parent/'ros-log'))
    namespace = 'speed_launch_' + uuid.uuid4().hex[:10]
    remote = '/'+namespace+'/r3d_path_follower'
    with (path.parent/'velocity-launch.log').open('w') as log:
        process = subprocess.Popen(['ros2', 'launch', 'r3d_planner', 'follower.launch.py',
                                    'namespace:='+namespace], stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True,
                                   env=os.environ.copy())
        try:
            result = _parameter_dump(remote)
            values = yaml.safe_load(result.stdout)[remote]['ros__parameters']
            assert values['max_linear_speed'] == 0.52
            assert values['max_angular_speed'] == 0.9
            assert values['max_angular_speed_narrow'] == 0.12
            assert values['narrow_speed_factor'] == 0.25
            assert process.poll() is None
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=3)


@pytest.mark.parametrize('linear,angular,cap,factor', [
    (0.52, 0.9, 0.12, 0.25), (0.4, 0.5, 0.3, 0.6)])
@pytest.mark.parametrize('angle', [0.1, 0.4, 0.8, -0.8])
def test_selected_profile_controls_narrow_ros_output(config, monkeypatch,
                                                     linear, angular, cap, factor, angle):
    """Observe reduced speed, both yaw signs and rotation-only from selected profiles."""
    path, central, robot, save = config
    alternate = copy.deepcopy(robot)
    alternate['robot']['name'] = 'SyntheticNarrowTestOnly'
    alternate['robot']['velocity_limits'] = {
        'max_linear_speed': linear, 'max_angular_speed': angular,
        'max_angular_speed_narrow': cap, 'narrow_speed_factor': factor}
    (path.parent/'robots/narrow-test.yaml').write_text(yaml.safe_dump(alternate))
    central['robot_config'] = 'robots/narrow-test.yaml'
    save()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with follower(load_configuration(path, mode='follower')['path_follower']) as node:
        observer = Node('narrow_observer', namespace=node.get_namespace())
        received = []
        observer.create_subscription(Twist, node.cmd_vel_topic, received.append, 10)
        try:
            path_for(node, angle, narrow=True)
            deadline = time.monotonic()+5
            while not received and time.monotonic() < deadline:
                node.control_loop()
                rclpy.spin_once(node, timeout_sec=0.01)
                rclpy.spin_once(observer, timeout_sec=0.02)
            assert received
            expected_x = 0.0 if abs(angle) > 0.5 else linear*factor
            assert received[-1].linear.x == pytest.approx(expected_x)
            assert received[-1].angular.z == pytest.approx(max(-cap, min(cap, angle*1.5)))
            assert received[-1].linear.y == 0.0
        finally:
            observer.destroy_node()


def test_narrow_factor_above_one_fails_before_command_start(config, monkeypatch):
    """A robot's reduced speed cannot exceed its own maximum forward speed."""
    path, central, robot, save = config
    robot['robot']['velocity_limits']['narrow_speed_factor'] = 1.01
    save()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    with pytest.raises(ConfigurationError):
        load_configuration(path, mode='follower')
    with patch.object(PathFollower, 'create_publisher') as publish:
        with pytest.raises(ConfigurationError):
            PathFollower()
        publish.assert_not_called()
