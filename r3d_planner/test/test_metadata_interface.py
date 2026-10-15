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

"""Check the generated wire contract and atomic path/narrow migration."""
import copy
import math
from unittest.mock import Mock, patch

import networkx as nx
import pytest
import rclpy
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Path
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.serialization import serialize_message, deserialize_message
from r3d_interfaces.msg import PathWithMetadata
from std_msgs.msg import Header

from r3d_planner.path_metadata import build_path, metadata_qos, validate_metadata
from r3d_planner.r3d_path_follower import PathFollower


def path_message(narrow=True):
    graph = nx.Graph()
    graph.add_node(0, pos=(0.0, 0.0, 0.0), type='floor')
    graph.add_node(1, pos=(0.0, 1.0, 0.2), type='narrow' if narrow else 'floor')
    header = Header(frame_id='map')
    header.stamp.sec = 10
    return build_path(graph, [0, 1], header, Quaternion(w=1.0))


def test_generated_wire_roundtrip_and_geometric_path():
    original = path_message()
    message = deserialize_message(serialize_message(original), PathWithMetadata)
    assert message == original
    assert message.narrow == [False, True]
    validate_metadata(message, 'map')
    assert message.path.poses[1].pose.position.z == 0.2
    for pose in message.path.poses:
        q = pose.pose.orientation
        assert q.z == pytest.approx(2**-0.5)
        assert q.w == pytest.approx(2**-0.5)
        assert q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w == pytest.approx(1.0)


@pytest.mark.parametrize('count', [0, 1, 3])
def test_empty_single_and_vertical_headings(count):
    graph = nx.Graph()
    for i in range(count):
        graph.add_node(i, pos=(1.0, 2.0, float(i)), type='narrow')
    message = build_path(graph, list(range(count)), Header(frame_id='map'), Quaternion(w=2.0))
    validate_metadata(message, 'map')
    assert message.narrow == [True] * count
    assert all(p.pose.orientation.w == 1.0 for p in message.path.poses)


@pytest.mark.parametrize('fault', ['length', 'frame', 'pose_frame', 'stamp',
                                   'nan', 'quaternion', 'nonfinite_q'])
def test_reject_inconsistent_metadata(fault):
    message = path_message()
    if fault == 'length':
        message.narrow.pop()
    elif fault == 'frame':
        message.path.header.frame_id = 'odom'
    elif fault == 'pose_frame':
        message.path.poses[0].header = Header(frame_id='odom')
    elif fault == 'stamp':
        message.path.poses[0].header = copy.deepcopy(message.path.header)
        message.path.poses[0].header.stamp.sec += 1
    elif fault == 'nan':
        message.path.poses[0].pose.position.x = math.nan
    elif fault == 'quaternion':
        message.path.poses[0].pose.orientation.w = 2.0
    else:
        message.path.poses[0].pose.orientation.z = math.inf
    with pytest.raises(ValueError):
        validate_metadata(message, 'map')


def make_follower():
    original = Node.__init__

    def init(node, *args, **kwargs):
        kwargs['parameter_overrides'] = [Parameter('cmd_vel_topic', value='/m01_test/cmd_vel')]
        original(node, *args, **kwargs)
    with patch.object(Node, '__init__', init):
        node = PathFollower()
    node.timer.cancel()
    return node


def test_follower_narrow_speed_pairing_replan_clear_and_invalid():
    rclpy.init()
    node = make_follower()
    try:
        node.cmd_pub = Mock()
        node.get_robot_pose = lambda: (0.0, 0.0, math.pi / 2)
        message = path_message()
        node.path_callback(message)
        node.control_loop()
        assert node.cmd_pub.publish.call_args.args[0].linear.x == pytest.approx(
            node.max_linear_speed * node.narrow_speed_factor)
        # The actual heading still has z>0.5; normal mode must use the new flag.
        node.path_callback(path_message(False))
        node.control_loop()
        assert node.cmd_pub.publish.call_args.args[0].linear.x == node.max_linear_speed
        assert node.current_narrow == [False, False]
        invalid = path_message()
        invalid.narrow.pop()
        node.path_callback(invalid)
        node.control_loop()
        assert not node.current_path and not node.current_narrow
        assert node.cmd_pub.publish.call_args.args[0].linear.x == 0.0
        node.path_callback(message)
        node.path_callback(PathWithMetadata(path=Path(header=Header(frame_id='map'))))
        assert not node.current_path and not node.current_narrow
        # The default retains the legacy obstacle policy; M01 is independent.
        assert not node.has_parameter('obstacle_timeout_sec')
        assert node.get_parameter('obstacle_monitoring.enabled').value is False
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_native_metadata_late_join_and_type_isolation():
    import time
    rclpy.init()
    publisher_node = Node('m01_metadata_publisher')
    follower = None
    try:
        publisher = publisher_node.create_publisher(PathWithMetadata, '/global_path_metadata',
                                                    metadata_qos())
        message = path_message()
        publisher.publish(message)
        follower = make_follower()
        deadline = time.monotonic() + 6
        while not follower.current_path and time.monotonic() < deadline:
            rclpy.spin_once(publisher_node, timeout_sec=0.02)
            rclpy.spin_once(follower, timeout_sec=0.05)
        assert follower.current_path == message.path.poses
        assert follower.current_narrow == message.narrow
        assert follower.path_sub.msg_type is PathWithMetadata
        assert not any(sub.topic_name == '/global_path' for sub in follower.subscriptions)
    finally:
        if follower:
            follower.destroy_node()
        publisher_node.destroy_node()
        rclpy.shutdown()


def test_generated_package_resources():
    from pathlib import Path
    from ament_index_python.packages import get_package_share_directory
    share = Path(get_package_share_directory('r3d_interfaces'))
    assert (share / 'LICENSE').is_file()
    assert (share / 'package.xml').is_file()
    assert (share / 'msg/PathWithMetadata.msg').is_file()
    schema = PathWithMetadata.get_fields_and_field_types()
    assert set(schema) == {'path', 'narrow'}


def test_planner_action_result_and_both_ros_publications_match(tmp_path):
    import time
    from nav2_msgs.action import ComputePathToPose
    from r3d_planner.r3d_pcd_path import GlobalGraphPlanner
    cloud = tmp_path/'classified.pcd'
    cloud.write_text('VERSION .7\nFIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F U\n'
                     'COUNT 1 1 1 1\nWIDTH 3\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n'
                     'POINTS 3\nDATA ascii\n0 0 0 65280\n0.05 0 0 65535\n0.1 0 0 65280\n')
    rclpy.init()
    planner = observer = None
    original = Node.__init__

    def init(node, *args, **kwargs):
        kwargs['parameter_overrides'] = [Parameter('map_name', value=str(cloud))]
        original(node, *args, **kwargs)
    try:
        with patch.object(Node, '__init__', init):
            planner = GlobalGraphPlanner()
        observer = Node('m01_path_pair_observer')
        paths, messages = [], []
        observer.create_subscription(Path, '/global_path', paths.append, 10)
        observer.create_subscription(PathWithMetadata, '/global_path_metadata', messages.append,
                                     metadata_qos())
        deadline = time.monotonic()+6
        while planner.pub_path.get_subscription_count() == 0 and time.monotonic() < deadline:
            rclpy.spin_once(observer, timeout_sec=0.05)
            rclpy.spin_once(planner, timeout_sec=0.05)
        assert planner.pub_path.get_subscription_count() > 0
        goal = ComputePathToPose.Goal()
        goal.use_start = True
        goal.start.header.frame_id = goal.goal.header.frame_id = 'map'
        goal.goal.pose.position.x = 0.1
        handle = Mock(request=goal)
        result = planner.execute_callback(handle)
        deadline = time.monotonic()+6
        while (not paths or not messages) and time.monotonic() < deadline:
            rclpy.spin_once(observer, timeout_sec=0.05)
        assert paths[0] == messages[0].path == result.path
        assert messages[0].narrow == [False, True, False]
        validate_metadata(messages[0], 'map')
        handle.succeed.assert_called_once()
    finally:
        if observer:
            observer.destroy_node()
        if planner:
            planner.destroy_node()
        rclpy.shutdown()
