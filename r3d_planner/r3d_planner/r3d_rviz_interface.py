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
# =============================================================================
# R3D-Planner
#
# Author:        Bastian Aumer
# Last modified: 2026-09-16
# Repository:    https://github.com/RoboProjekt/R3D-Planner
#
# Copyright (c) Bastian Aumer
# SPDX-FileCopyrightText: 2026 Bastian Aumer
# SPDX-License-Identifier: Apache-2.0
# =============================================================================

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import (
    PointStamped, PoseStamped, PoseWithCovarianceStamped, TransformStamped, Quaternion)
from nav2_msgs.action import ComputePathToPose
from rclpy.action import ActionClient
from std_srvs.srv import Trigger  # Einfacher Service für den Reset
import tf2_ros
import math
from .odometry import components


class RVizInterfaceNode(Node):
    def __init__(self):
        super().__init__('r3d_rviz_interface')

        # --- PARAMETER & STATE ---
        self.declare_parameter('match_radius', 0.8)
        self.declare_parameter('action_server_timeout_sec', 1.0)
        self.declare_parameter('publish_map_odom', True)
        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('odom_frame', 'odom')
        self.match_radius = self.get_parameter('match_radius').value
        self.initial_calibration_done = False  # Der "Schalter" für deinen Workflow
        self.latest_point = None

        # --- SUBSCRIPTIONS ---
        self.sub_point = self.create_subscription(
            PointStamped, '/clicked_point', self.point_cb, 10)
        self.sub_initial = self.create_subscription(
            PoseWithCovarianceStamped, '/initialpose', self.initial_pose_cb, 10)
        self.sub_goal = self.create_subscription(PoseStamped, '/goal_pose', self.goal_pose_cb, 10)

        # --- SERVICE (Der "Action Call" zum Neusetzen der Position) ---
        # Aufruf via Terminal: ros2 service call /recalibrate_pose std_srvs/srv/Trigger
        self.srv_recalibrate = self.create_service(
            Trigger, 'recalibrate_pose', self.recalibrate_callback)

        # --- ACTION & TF ---
        self.action_client = ActionClient(self, ComputePathToPose, 'compute_path_to_pose')
        self.tf_broadcaster = tf2_ros.StaticTransformBroadcaster(self)

        self.get_logger().info("--- R3D RViz Smart Interface GESTARTET ---")
        if self.get_parameter('publish_map_odom').value:
            self.get_logger().info('Waiting for initial map calibration.')
        else:
            self.get_logger().info(
                'External global localization enabled; ready for point/goal pairs.')

    def recalibrate_callback(self, request, response):
        """Setzt das System zurück, um die Position neu zu kalibrieren."""
        self.initial_calibration_done = False
        self.get_logger().warn(
            "🔄 Rekalibrierung aktiviert! Bitte Startpunkt (Point + Pose) neu setzen.")
        response.success = True
        response.message = "Interface ist wieder im Kalibrierungs-Modus."
        return response

    def _valid_selection(self, position, frame, orientation=None):
        try:
            if frame != self.get_parameter('map_frame').value:
                raise ValueError('RViz selection must use map_frame')
            if not all(math.isfinite(v) for v in (position.x, position.y, position.z)):
                raise ValueError('RViz position must be finite')
            if orientation is not None:
                components(orientation)
            return True
        except ValueError as exc:
            self.get_logger().warning(f'RViz selection rejected: {exc}')
            return False

    def point_cb(self, msg):
        if not self._valid_selection(msg.point, msg.header.frame_id):
            self.latest_point = None
            return
        self.latest_point = msg
        mode = ('KALIBRIERUNG' if self.get_parameter('publish_map_odom').value and
                not self.initial_calibration_done else 'ZIELSETZUNG')
        self.get_logger().info(f"📍 [{mode}] Punkt empfangen (Z={msg.point.z:.2f}).")

    def initial_pose_cb(self, msg):
        """Wird für die Kalibrierung (Startpunkt) genutzt."""
        if not self.get_parameter('publish_map_odom').value:
            return
        if self.initial_calibration_done:
            self.get_logger().info(
                "ℹ️ Kalibrierung bereits aktiv. Nutze '2D Goal Pose' für neue Ziele.")
            return

        position = msg.pose.pose.position if hasattr(msg.pose, 'pose') else msg.pose.position
        orientation = (msg.pose.pose.orientation if hasattr(msg.pose, 'pose')
                       else msg.pose.orientation)
        if not self._valid_selection(position, msg.header.frame_id, orientation):
            return
        if self.latest_point is None:
            self.get_logger().warn("⚠️ Klicke erst auf 'Publish Point' für die Höhe!")
            return

        # Distanz-Check
        dist = math.hypot(self.latest_point.point.x - msg.pose.pose.position.x,
                          self.latest_point.point.y - msg.pose.pose.position.y)

        if dist <= self.match_radius:
            self.get_logger().info(f"✅ INITIALISIERUNG ERFOLGREICH! Abstand: {dist:.2f}m")
            self.publish_map_odom_tf(self.latest_point.point, msg.pose.pose.orientation)
            self.initial_calibration_done = True
            self.latest_point = None  # Speicher leeren
            self.get_logger().info(
                "🚀 Modus gewechselt: Alle weiteren Klicks werden als ZIELE behandelt.")
        else:
            self.get_logger().error(
                f"❌ Abweichung zu groß ({dist:.2f}m)! "
                "Punkt und Pose müssen näher beieinander liegen.")

    def goal_pose_cb(self, msg):
        """Wird für die Zielsetzung genutzt."""
        if self.get_parameter('publish_map_odom').value and not self.initial_calibration_done:
            self.get_logger().warn("⚠️ Roboter noch nicht lokalisiert! Setze erst den Startpunkt.")
            return

        position = msg.pose.pose.position if hasattr(msg.pose, 'pose') else msg.pose.position
        orientation = (msg.pose.pose.orientation if hasattr(msg.pose, 'pose')
                       else msg.pose.orientation)
        if not self._valid_selection(position, msg.header.frame_id, orientation):
            return
        if self.latest_point is None:
            self.get_logger().warn("⚠️ Klicke erst auf 'Publish Point' für die Zielhöhe!")
            return

        # Automatischer Match für das Ziel
        dist = math.hypot(self.latest_point.point.x - msg.pose.position.x,
                          self.latest_point.point.y - msg.pose.position.y)

        if dist <= self.match_radius:
            self.get_logger().info("🎯 ZIEL BESTÄTIGT! Sende Pfadanfrage...")
            if self.send_path_request(self.latest_point.point, msg.pose.orientation):
                self.latest_point = None  # Speicher leeren
        else:
            self.get_logger().error(f"❌ Ziel-Match fehlgeschlagen (Distanz: {dist:.2f}m)")

    def publish_map_odom_tf(self, point, orientation):
        """Berechnet und setzt den statischen Offset zwischen Map und Odometrie."""
        t = TransformStamped()
        if not self.get_parameter('publish_map_odom').value:
            self.get_logger().info(
                'External global localization owns map -> odom; calibration TF disabled.')
            return
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.get_parameter('map_frame').value
        t.child_frame_id = self.get_parameter('odom_frame').value
        t.transform.translation.x = point.x
        t.transform.translation.y = point.y
        t.transform.translation.z = point.z
        q = components(orientation)
        t.transform.rotation = Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])
        self.tf_broadcaster.sendTransform(t)
        self.get_logger().info("🗺️ TF 'map -> odom' fixiert. Odometrie ist nun synchronisiert.")

    def send_path_request(self, target_point, target_orientation):
        """Request planning using the planner's current Odometry input."""
        try:
            goal_pose = PoseStamped()
            goal_pose.header.frame_id = self.get_parameter('map_frame').value
            goal_pose.pose.position.x = target_point.x
            goal_pose.pose.position.y = target_point.y
            goal_pose.pose.position.z = target_point.z
            q = components(target_orientation)
            goal_pose.pose.orientation = Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])

            goal_msg = ComputePathToPose.Goal()
            # The planner resolves the start from its standard Odometry input.
            goal_msg.use_start = False
            goal_msg.goal = goal_pose
            goal_msg.planner_id = 'GridBased'

            timeout = self.get_parameter('action_server_timeout_sec').value
            if not self.action_client.wait_for_server(timeout_sec=timeout):
                self.get_logger().warning('Planning action server unavailable')
                return False
            self.action_client.send_goal_async(goal_msg)
            return True
        except Exception as e:
            self.get_logger().error(f'Planning request failed: {e}')
            return False


def main(args=None):
    rclpy.init(args=args)
    node = RVizInterfaceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
