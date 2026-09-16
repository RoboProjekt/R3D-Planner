# =============================================================================
# R3D-Planner
#
# Author:        Bastian Aumer
# Last modified: 2026-09-16
# Repository:    https://github.com/RoboProjekt/R3D-Planner
#
# Copyright (c) Bastian Aumer
# =============================================================================

"""Configuration and non-motion ROS integration tests (ROS 2 Humble)."""
import copy
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from r3d_planner.configuration import ConfigurationError, load_configuration


SOURCE = Path(__file__).resolve().parents[1] / 'config'


@pytest.fixture
def config(tmp_path):
    central = yaml.safe_load((SOURCE / 'planner_config.yaml').read_text())
    robot = yaml.safe_load((SOURCE / 'robots/Go2W.yaml').read_text())
    (tmp_path / 'robots').mkdir()
    cloud = tmp_path / 'tiny.pcd'
    cloud.write_text('VERSION .7\nFIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F U\n'
                     'COUNT 1 1 1 1\nWIDTH 3\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n'
                     'POINTS 3\nDATA ascii\n0 0 0 65280\n0.05 0 0 65280\n0.1 0 0 65280\n')
    central['maps'] = {'pcd_path': 'tiny.pcd', 'map_name': 'tiny.pcd'}
    path = tmp_path / 'planner_config.yaml'
    def save():
        path.write_text(yaml.safe_dump(central))
        (tmp_path / 'robots/Go2W.yaml').write_text(yaml.safe_dump(robot))
    save()
    return path, central, robot, save


def test_selection_and_restart_reload(config):
    path, central, robot, save = config
    first = load_configuration(path)
    assert first['planner']['odometry_topic'] == '/lidar_odometry'
    assert first['preprocessor']['robot_height_cm'] == 80.0
    alternate = copy.deepcopy(robot)
    alternate['robot']['name'] = 'ConfigurationTestOnly'
    alternate['robot']['geometry']['robot_height_cm'] = 90.0
    alternate['robot']['odometry']['topic'] = '/test/odometry'
    (path.parent / 'robots/test.yaml').write_text(yaml.safe_dump(alternate))
    central['robot_config'] = 'robots/test.yaml'
    central['shared']['voxel_size_cm'] = 10.0
    save()
    second = load_configuration(path)
    assert second['robot_name'] == 'ConfigurationTestOnly'
    assert second['planner']['odometry_topic'] == '/test/odometry'
    for section in ('preprocessor', 'planner'):
        assert second[section]['robot_height_cm'] == 90.0
        assert second[section]['voxel_size_cm'] == 10.0


@pytest.mark.parametrize('fault', ['missing_robot', 'missing_height', 'radius', 'height',
                                  'topic', 'boolean', 'duplicate', 'malformed', 'shared'])
def test_validation(config, fault):
    path, central, robot, save = config
    if fault == 'missing_robot':
        central['robot_config'] = 'robots/missing.yaml'
    elif fault == 'missing_height':
        del robot['robot']['geometry']['robot_height_cm']
    elif fault == 'radius':
        robot['robot']['geometry']['robot_radius_cm'] = -1.0
    elif fault == 'height':
        robot['robot']['geometry']['robot_height_cm'] = 0.0
    elif fault == 'topic':
        robot['robot']['odometry']['topic'] = '/invalid topic'
    elif fault == 'boolean':
        central['components']['live_filter']['enabled'] = 'false'
    elif fault == 'shared':
        central['shared']['voxel_size_cm'] = 0
    save()
    if fault == 'duplicate':
        with path.open('a') as stream:
            stream.write('\nrobot_config: robots/Go2W.yaml\n')
    if fault == 'malformed':
        path.write_text('robot_config: [\n')
    with pytest.raises(ConfigurationError):
        load_configuration(path)


@pytest.mark.parametrize('live,rviz', [(False, False), (False, True), (True, False), (True, True)])
def test_launch_conditions(config, live, rviz):
    from launch import LaunchContext
    from r3d_planner.launching import configured_nodes
    path, central, robot, save = config
    central['components']['live_filter']['enabled'] = live
    central['components']['rviz_interface']['enabled'] = rviz
    save()
    with patch('r3d_planner.launching.load_configuration',
               side_effect=lambda **kw: load_configuration(path, **kw)):
        context = LaunchContext()
        actions = configured_nodes(context, 'planner')[1:]
        assert actions[0].condition is None
        assert actions[1].condition.evaluate(context) is live
        assert actions[2].condition.evaluate(context) is rviz


def test_effective_ros_parameters_and_odometry(config):
    import rclpy
    from rclpy.parameter import Parameter
    from geometry_msgs.msg import TransformStamped
    from nav_msgs.msg import Odometry
    from nav2_msgs.action import ComputePathToPose
    from r3d_planner.r3d_pcd_path import GlobalGraphPlanner
    from r3d_preprocessor.r3d_pcd_analyser import PcdToGraphNode
    path, central, robot, save = config
    robot['robot']['geometry']['robot_height_cm'] = 85.0
    central['preprocessing']['min_points_per_sqm'] = 12.0
    save()
    cfg = load_configuration(path)
    rclpy.init()
    nodes = []
    try:
        for section, cls in [('preprocessor', PcdToGraphNode), ('planner', GlobalGraphPlanner)]:
            overrides = [Parameter(key, value=value) for key, value in cfg[section].items()]
            # Preserve production constructors; inject normal ROS parameter overrides.
            original = rclpy.node.Node.__init__
            def init(node, *args, **kwargs):
                kwargs['parameter_overrides'] = overrides
                original(node, *args, **kwargs)
            with patch.object(rclpy.node.Node, '__init__', init):
                node = cls()
            nodes.append(node)
            for key in ('robot_height_cm', 'robot_narrow_radius_cm', 'robot_radius_cm',
                        'voxel_size_cm', 'max_step_height_cm'):
                assert node.get_parameter(key).value == cfg[section][key]
        planner = nodes[-1]
        assert nodes[0].get_parameter('min_points_per_sqm').value == 12.0
        assert planner.get_parameter('odometry_topic').value == '/lidar_odometry'
        transform = TransformStamped()
        transform.header.frame_id = 'map'
        transform.child_frame_id = 'odom'
        transform.transform.translation.x = 2.0
        transform.transform.rotation.w = 1.0
        planner.odometry.buffer.set_transform_static(transform, 'test')
        message = Odometry()
        message.header.stamp = planner.get_clock().now().to_msg()
        message.header.frame_id = 'odom'
        message.child_frame_id = 'base_link'
        message.pose.pose.orientation.w = 1.0
        publisher = planner.create_publisher(Odometry, '/lidar_odometry', 10)
        import time
        deadline = time.monotonic() + 5
        while planner.odometry.latest is None and time.monotonic() < deadline:
            message.header.stamp = planner.get_clock().now().to_msg()
            publisher.publish(message)
            rclpy.spin_once(planner, timeout_sec=0.05)
        assert planner.odometry.latest is not None
        assert planner.odometry.map_pose().pose.position.x == 2.0
        transform.transform.translation.x = 1.0
        transform.transform.rotation.z = 2**-0.5
        transform.transform.rotation.w = 2**-0.5
        planner.odometry.buffer.set_transform_static(transform, 'test')
        planner.odometry.latest.pose.pose.position.x = 1.0
        transformed = planner.odometry.map_pose()
        assert transformed.pose.position.x == pytest.approx(1.0)
        assert transformed.pose.position.y == pytest.approx(1.0)
        goal = ComputePathToPose.Goal()
        goal.goal.header.frame_id = 'map'
        goal.goal.pose.position.x = 0.1
        class Handle:
            request = goal
            succeeded = False
            aborted = False
            def succeed(self):
                self.succeeded = True
            def abort(self):
                self.aborted = True
        handle = Handle()
        assert planner.execute_callback(handle).path.poses
        assert handle.succeeded
        planner.odometry.latest.header.stamp.sec = 0
        planner.odometry.latest.header.stamp.nanosec = 0
        with pytest.raises(ValueError, match='stale'):
            planner.odometry.map_pose()
        handle = Handle()
        planner.execute_callback(handle)
        assert handle.aborted
        # Offline requests do not need odometry or TF.
        goal.use_start = True
        goal.start.header.frame_id = 'map'
        handle = Handle()
        assert planner.execute_callback(handle).path.poses
        assert handle.succeeded
    finally:
        for node in nodes:
            node.destroy_node()
        rclpy.shutdown()


def test_default_live_source_config(monkeypatch):
    from r3d_planner.configuration import default_config_path
    monkeypatch.delenv('R3D_CONFIG_DIR', raising=False)
    assert default_config_path().resolve() == SOURCE / 'planner_config.yaml'


def test_copied_install_does_not_silently_load_snapshot(config, monkeypatch):
    import r3d_planner.configuration as module
    from ament_index_python import packages
    path, central, robot, save = config
    monkeypatch.delenv('R3D_CONFIG_DIR', raising=False)
    monkeypatch.setattr(module, '__file__', str(path.parent / 'installed/lib/module.py'))
    monkeypatch.setattr(packages, 'get_package_share_directory', lambda name: str(path.parent / 'installed/share'))
    with pytest.raises(ConfigurationError, match='Copied install YAML'):
        module.default_config_path()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    assert module.default_config_path() == path


def test_integer_yaml_spelling_keeps_ros_double_types(config):
    path, central, robot, save = config
    robot['robot']['geometry']['robot_height_cm'] = 80
    central['preprocessing']['min_points_per_sqm'] = 10
    central['live_filter']['max_height'] = 1
    central['shared']['voxel_size_cm'] = 5
    save()
    cfg = load_configuration(path)
    assert type(cfg['planner']['robot_height_cm']) is float
    assert type(cfg['preprocessor']['min_points_per_sqm']) is float
    assert type(cfg['live_filter']['max_height']) is float
    assert type(cfg['preprocessor']['voxel_size_cm']) is float
    assert type(cfg['preprocessor']['min_points_per_voxel']) is int
    assert type(cfg['preprocessor']['ground_fill']) is bool


def test_preprocessor_real_launch(config, monkeypatch):
    import subprocess
    path, central, robot, save = config
    central['preprocessing']['min_points_per_voxel'] = 1
    central['preprocessing']['ground_fill'] = False
    save()
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    monkeypatch.setenv('ROS_LOG_DIR', str(path.parent / 'ros-log'))
    result = subprocess.run(['ros2', 'launch', 'r3d_planner', 'preprocessor.launch.py'],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (path.parent / 'tiny_analysed.pcd').is_file(), result.stdout + result.stderr


def test_real_launch_restart_and_all_components(config, monkeypatch):
    """Restart real launches in the same environment; no rebuild or re-sourcing."""
    import os
    import signal
    import subprocess
    import time
    import rclpy
    from rclpy.node import Node
    path, central, robot, save = config
    monkeypatch.setenv('R3D_CONFIG_DIR', str(path.parent))
    monkeypatch.setenv('ROS_LOG_DIR', str(path.parent / 'ros-log'))
    rclpy.init()
    observer = Node('configuration_test_observer')
    try:
        for index, (live, rviz) in enumerate([(False, False), (True, False),
                                              (False, True), (True, True)]):
            central['components']['live_filter']['enabled'] = live
            central['components']['rviz_interface']['enabled'] = rviz
            robot['robot']['geometry']['robot_height_cm'] = 80.0 + index
            central['shared']['max_step_height_cm'] = 25.0 + index
            central['rviz_interface']['publish_map_odom'] = index != 2
            central['rviz_interface']['match_radius'] = 0.8 + index / 10
            central['live_filter']['min_height'] = 0.05 + index / 100
            if index:
                central['robot_config'] = 'robots/alternate.yaml'
                robot['robot']['name'] = 'ConfigurationTestOnly'
                robot['robot']['odometry']['topic'] = '/test/odometry'
                (path.parent / 'robots/alternate.yaml').write_text(yaml.safe_dump(robot))
            save()
            with (path.parent / f'launch-{index}.log').open('w') as log:
                process = subprocess.Popen(['ros2', 'launch', 'r3d_planner', 'planner.launch.py'],
                                           stdout=log, stderr=subprocess.STDOUT,
                                           start_new_session=True, env=os.environ.copy())
                try:
                    expected = {'global_graph_planner'}
                    if live:
                        expected.add('obstacle_cliff_filter')
                    if rviz:
                        expected.add('r3d_rviz_interface')
                    deadline = time.monotonic() + 12
                    while time.monotonic() < deadline:
                        names = {name for name in observer.get_node_names()
                                 if not name.startswith('_') and name != 'configuration_test_observer'}
                        if names == expected:
                            break
                        assert process.poll() is None, (path.parent / f'launch-{index}.log').read_text()
                        rclpy.spin_once(observer, timeout_sec=0.1)
                    assert names == expected
                    dump = subprocess.run(['ros2', 'param', 'dump', '/global_graph_planner',
                                           '--no-daemon', '--spin-time', '2'],
                                          capture_output=True, text=True, timeout=12, check=True)
                    values = yaml.safe_load(dump.stdout)['/global_graph_planner']['ros__parameters']
                    assert values['robot_height_cm'] == 80.0 + index
                    assert values['robot_narrow_radius_cm'] == 30.0
                    assert values['robot_radius_cm'] == 40.0
                    assert values['odometry_topic'] == robot['robot']['odometry']['topic']
                    assert values['max_step_height_cm'] == 25.0 + index
                    for enabled, remote, section, key in [
                        (live, '/obstacle_cliff_filter', 'live_filter', 'min_height'),
                        (rviz, '/r3d_rviz_interface', 'rviz_interface', 'match_radius')
                    ]:
                        if enabled:
                            extra = subprocess.run(['ros2', 'param', 'dump', remote,
                                                    '--no-daemon', '--spin-time', '2'],
                                                   capture_output=True, text=True, timeout=12, check=True)
                            params = yaml.safe_load(extra.stdout)[remote]['ros__parameters']
                            assert params[key] == central[section][key]
                            if section == 'rviz_interface':
                                assert params['publish_map_odom'] is central[section]['publish_map_odom']
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGINT)
                    try:
                        process.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=3)
                    # Recreate the observer to discard old DDS discovery leases.
                    # The launched node environment and sourced install stay unchanged.
                    observer.destroy_node()
                    rclpy.shutdown()
                    rclpy.init()
                    observer = Node('configuration_test_observer')
    finally:
        observer.destroy_node()
        rclpy.shutdown()
