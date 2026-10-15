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

"""Keep geometric orientations separate from atomic traversability metadata."""
import math
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from rclpy.qos import QoSProfile, DurabilityPolicy
from r3d_interfaces.msg import PathWithMetadata
from .odometry import components


def metadata_qos():
    """Retain the last complete path and flags for late joining followers."""
    return QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)


def build_path(graph, path_ids, header, goal_orientation):
    """Build one atomic path with real XY headings and index-aligned flags."""
    path = Path(header=header)
    narrow = []
    positions = [graph.nodes[key]['pos'] for key in path_ids]
    if not all(math.isfinite(v) for position in positions for v in position):
        raise ValueError('nonfinite graph position')
    headings = [None] * len(path_ids)
    next_heading = None
    for index in range(len(path_ids) - 2, -1, -1):
        dx = positions[index + 1][0] - positions[index][0]
        dy = positions[index + 1][1] - positions[index][1]
        if math.hypot(dx, dy) > 1e-12:
            next_heading = math.atan2(dy, dx)
        headings[index] = next_heading
    heading = None
    for index, key in enumerate(path_ids):
        position = tuple(float(v) for v in positions[index])
        if headings[index] is not None:
            heading = headings[index]
        pose = PoseStamped(header=header)
        pose.pose.position.x, pose.pose.position.y, pose.pose.position.z = position
        if heading is None:
            q = components(goal_orientation)
        else:
            q = (0.0, 0.0, math.sin(heading / 2), math.cos(heading / 2))
        (pose.pose.orientation.x, pose.pose.orientation.y,
         pose.pose.orientation.z, pose.pose.orientation.w) = q
        path.poses.append(pose)
        narrow.append(graph.nodes[key].get('type') == 'narrow')
    return PathWithMetadata(path=path, narrow=narrow)


def validate_metadata(message, frame):
    """Reject mismatched metadata or invalid geometric path contracts."""
    if len(message.path.poses) != len(message.narrow):
        raise ValueError('narrow count must equal pose count')
    if message.path.header.frame_id != frame:
        raise ValueError('path frame does not match map_frame')
    for pose in message.path.poses:
        if pose.header != message.path.header:
            raise ValueError('pose header differs from path header')
        position = pose.pose.position
        if not all(math.isfinite(v) for v in (position.x, position.y, position.z)):
            raise ValueError('nonfinite path position')
        q = pose.pose.orientation
        norm = sum(v * v for v in (q.x, q.y, q.z, q.w))
        if not math.isfinite(norm) or abs(norm - 1) > 1e-6:
            raise ValueError('path quaternion must be normalized')
