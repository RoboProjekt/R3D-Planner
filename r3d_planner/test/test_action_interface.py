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

"""Exercise actual Humble goal statuses, cancellation and result contracts."""
import threading
import time
from unittest.mock import patch

import pytest
import rclpy
from action_msgs.msg import GoalStatus
from nav2_msgs.action import ComputePathToPose
from nav_msgs.msg import Odometry
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter

from r3d_planner.r3d_pcd_path import GlobalGraphPlanner


def wait(node, future, timeout=8):
    deadline = time.monotonic() + timeout
    while not future.done() and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.02)
    assert future.done(), 'ROS action future timed out'
    return future.result()


@pytest.fixture
def action_server(tmp_path):
    cloud = tmp_path / 'graph.pcd'
    cloud.write_text('VERSION .7\nFIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F U\n'
                     'COUNT 1 1 1 1\nWIDTH 3\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n'
                     'POINTS 3\nDATA ascii\n0 0 0 65280\n0.05 0 0 65535\n0.1 0 0 65280\n')
    rclpy.init()
    original = Node.__init__

    def init(node, *args, **kwargs):
        kwargs['parameter_overrides'] = [Parameter('map_name', value=str(cloud))]
        original(node, *args, **kwargs)
    with patch.object(Node, '__init__', init):
        planner = GlobalGraphPlanner()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(planner)
    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    node = Node('action_contract_test')
    client = ActionClient(node, ComputePathToPose, '/compute_path_to_pose')
    try:
        assert client.wait_for_server(timeout_sec=6)
        yield planner, node, client
    finally:
        client.destroy()
        node.destroy_node()
        executor.shutdown()
        thread.join(timeout=3)
        planner.destroy_node()
        rclpy.shutdown()


def goal():
    message = ComputePathToPose.Goal()
    message.use_start = True
    message.start.header.frame_id = message.goal.header.frame_id = 'map'
    message.goal.pose.position.x = 0.1
    return message


def request(node, client, message):
    handle = wait(node, client.send_goal_async(message))
    assert handle.accepted
    return handle, wait(node, handle.get_result_async())


@pytest.mark.parametrize('planner_id', ['', 'GridBased', 'legacy_unknown_identifier'])
def test_native_success_repeated_and_legacy_planner_id(action_server, planner_id):
    planner, node, client = action_server
    message = goal()
    message.planner_id = planner_id
    for index in range(2):
        handle, result = request(node, client, message)
        assert result.status == GoalStatus.STATUS_SUCCEEDED
        assert len(result.result.path.poses) == 3
        assert result.result.path.header.frame_id == 'map'
        duration = result.result.planning_time
        assert duration.sec * 10**9 + duration.nanosec > 0
    assert {'path', 'planning_time'} <= set(ComputePathToPose.Result.get_fields_and_field_types())


@pytest.mark.parametrize('fault', ['goal_frame', 'nan', 'quaternion', 'start_frame',
                                   'missing_pose', 'stale_pose', 'missing_tf',
                                   'disconnected', 'empty_path'])
def test_native_abort_cases(action_server, fault):
    planner, node, client = action_server
    message = goal()
    if fault == 'goal_frame':
        message.goal.header.frame_id = 'odom'
    elif fault == 'nan':
        message.goal.pose.position.x = float('nan')
    elif fault == 'quaternion':
        message.goal.pose.orientation.w = 0.0
    elif fault == 'start_frame':
        message.start.header.frame_id = ''
    elif fault in ('missing_pose', 'stale_pose', 'missing_tf'):
        message.use_start = False
        if fault != 'missing_pose':
            odometry = Odometry()
            odometry.header.frame_id = 'odom'
            odometry.child_frame_id = 'base_link'
            odometry.header.stamp = planner.get_clock().now().to_msg()
            if fault == 'stale_pose':
                odometry.header.stamp.sec -= 10
            planner.odometry.callback(odometry)
    elif fault == 'disconnected':
        planner.graph.remove_edges_from(list(planner.graph.edges))
    else:
        planner.a_star = lambda *args, **kwargs: []
    handle, result = request(node, client, message)
    assert result.status == GoalStatus.STATUS_ABORTED
    assert not result.result.path.poses


def test_native_cancellation_while_execute_is_active(action_server):
    planner, node, client = action_server
    entered = threading.Event()

    def active_search(start, end, cancel=None):
        entered.set()
        deadline = time.monotonic() + 8
        while not cancel() and time.monotonic() < deadline:
            time.sleep(0.01)
        return None
    planner.a_star = active_search
    handle = wait(node, client.send_goal_async(goal()))
    assert entered.wait(timeout=3)
    cancel = wait(node, handle.cancel_goal_async())
    assert cancel.goals_canceling
    result = wait(node, handle.get_result_async())
    assert result.status == GoalStatus.STATUS_CANCELED
    assert not result.result.path.poses


def test_actual_astar_cooperative_cancel_and_unmodified_route(action_server):
    planner, node, client = action_server
    first, last = planner.node_list[0], planner.node_list[-1]
    assert len(planner.a_star(first, last)) == 3
    assert planner.a_star(first, last, cancel=lambda: True) is None
