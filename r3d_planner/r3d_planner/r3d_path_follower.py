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

import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock, ClockType, JumpThreshold
from rclpy.duration import Duration
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.msg import ParameterDescriptor
from geometry_msgs.msg import Twist
from r3d_interfaces.msg import PathWithMetadata
from sensor_msgs.msg import PointCloud2
from .cloud import read_xyz
from .configuration import MONITOR_DEFAULTS, monitoring_settings
import math
from .odometry import OdometryInput
from .path_metadata import metadata_qos, validate_metadata
from .obstacle_monitor import ObstacleMonitor


class PathFollower(Node):
    def __init__(self):
        super().__init__('r3d_path_follower')

        # --- PARAMETER ---
        defaults = {'lookahead_distance': 0.5, 'max_linear_speed': 0.35,
                    'max_angular_speed': 0.6, 'stop_distance': 0.6, 'goal_tolerance': 0.2,
                    'control_period_sec': 0.1, 'obstacle_x_min': 0.1,
                    'obstacle_half_width': 0.3, 'max_angular_speed_narrow': 0.2,
                    'angle_threshold': 0.5, 'steering_gain': 1.5,
                    'narrow_speed_factor': 0.4, 'turning_speed_factor': 0.3,
                    'cmd_vel_topic': '/cmd_vel'}
        for key, value in defaults.items():
            self.declare_parameter(key, value)
            setattr(self, key, self.get_parameter(key).value)
        self.odometry = OdometryInput(self)
        monitoring = {}
        for key, value in MONITOR_DEFAULTS.items():
            name = 'obstacle_monitoring.' + key
            self.declare_parameter(name, value, ParameterDescriptor(read_only=True))
            monitoring[key] = self.get_parameter(name).value
        self.monitoring_settings = monitoring_settings(monitoring)

        # --- VARIABLEN ---
        self.current_path = []
        self.current_narrow = []
        self.obstacle_in_front = False
        self.obstacle_monitor = ObstacleMonitor(
            self.monitoring_settings, self.odometry.base_frame,
            (self.obstacle_x_min, self.stop_distance, self.obstacle_half_width),
            self.odometry.buffer.lookup_transform)
        self._monitor_state = None
        self._clock_reset = threading.Event()
        self._jump_handle = None
        if self.monitoring_settings['enabled']:
            self._jump_handle = self.get_clock().create_jump_callback(
                JumpThreshold(min_forward=None, min_backward=Duration(nanoseconds=-1),
                              on_clock_change=True),
                post_callback=lambda jump: self._clock_reset.set())

        # --- PUBLISHER & SUBSCRIBER ---
        self.cmd_pub = self.create_publisher(Twist, self.cmd_vel_topic, 10)

        self.path_sub = self.create_subscription(
            PathWithMetadata, '/global_path_metadata', self.path_callback, metadata_qos())

        self.obstacle_sub = self.create_subscription(
            PointCloud2, self.monitoring_settings['topic'], self.obstacle_callback,
            qos_profile_sensor_data)

        # --- TF (Transformationen) ---
        # --- CONTROL LOOP ---
        self.control_clock = (Clock(clock_type=ClockType.STEADY_TIME)
                              if self.monitoring_settings['enabled'] else self.get_clock())
        self.timer = self.create_timer(
            self.control_period_sec, self.control_loop, clock=self.control_clock)
        self.get_logger().info("R3D Path Follower gestartet! Warte auf Pfad...")

    def path_callback(self, msg):
        try:
            validate_metadata(msg, self.get_parameter('map_frame').value)
        except ValueError as exc:
            self.current_path, self.current_narrow = [], []
            self.get_logger().warning(f'Path metadata rejected: {exc}')
            return
        self.current_path, self.current_narrow = list(msg.path.poses), list(msg.narrow)
        self.get_logger().info(f"Neuer Pfad empfangen mit {len(self.current_path)} Punkten.")

    def obstacle_callback(self, msg):
        if self.monitoring_settings['enabled']:
            now, steady = self.monitor_times()
            self.obstacle_monitor.receive(msg, now, steady)
            if self.obstacle_monitor.state in ('ACTIVE', 'BLOCKED'):
                self.obstacle_in_front = self.obstacle_monitor.obstacle
            self.log_monitor_state()
            if self.obstacle_monitor.state != 'ACTIVE':
                self.publish_command(Twist())
            return
        obstacle_detected = False

        try:
            points = read_xyz(msg)
        except ValueError as exc:
            self.get_logger().warning(f'PointCloud2 rejected: {exc}', throttle_duration_sec=2.0)
            return
        for point in points:
            x, y, z = point
            if self.obstacle_x_min < x < self.stop_distance and abs(y) < self.obstacle_half_width:
                obstacle_detected = True
                break

        if obstacle_detected and not self.obstacle_in_front:
            self.get_logger().warn("DYNAMISCHES HINDERNIS! Stoppe...")
        elif not obstacle_detected and self.obstacle_in_front:
            self.get_logger().info("Weg ist wieder frei.")

        self.obstacle_in_front = obstacle_detected

    def monitor_times(self):
        """Consume clock notifications in the serialized node callback group."""
        if self._clock_reset.is_set():
            self._clock_reset.clear()
            self.obstacle_monitor.clock_reset()
        return self.get_clock().now().nanoseconds, time.monotonic_ns()

    def log_monitor_state(self):
        """Log transitions rather than flooding every controller cycle."""
        state = self.obstacle_monitor.state
        if state != self._monitor_state:
            self.get_logger().info(f'Obstacle monitoring: {state}: '
                                   f'{self.obstacle_monitor.reason}')
            self._monitor_state = state

    def monitor_available(self):
        """Check freshness even with no path or a paused simulation clock."""
        now, steady = self.monitor_times()
        available = self.obstacle_monitor.available(now, steady)
        self.log_monitor_state()
        return available

    def publish_command(self, message):
        """Recheck monitored clearance immediately before the single command publisher."""
        if self.monitoring_settings['enabled'] and not self.monitor_available():
            message = Twist()
        self.cmd_pub.publish(message)

    def destroy_node(self):
        """Remove the clock callback before destroying the node's ROS entities."""
        if self._jump_handle is not None:
            self._jump_handle.unregister()
            self._jump_handle = None
        return super().destroy_node()

    def get_robot_pose(self):
        try:
            pose = self.odometry.map_pose().pose
            x = pose.position.x
            y = pose.position.y

            q = pose.orientation
            siny_cosp = 2 * (q.w * q.z + q.x * q.y)
            cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
            yaw = math.atan2(siny_cosp, cosy_cosp)

            return x, y, yaw
        except Exception:
            return None, None, None

    def control_loop(self):
        msg = Twist()
        if self.monitoring_settings['enabled'] and not self.monitor_available():
            self.publish_command(msg)
            return

        if not self.current_path:
            self.publish_command(msg)
            return

        if self.obstacle_in_front:
            self.publish_command(msg)
            return

        rx, ry, ryaw = self.get_robot_pose()
        if rx is None:
            self.publish_command(msg)
            return

        goal_x = self.current_path[-1].pose.position.x
        goal_y = self.current_path[-1].pose.position.y
        dist_to_goal = math.hypot(goal_x - rx, goal_y - ry)

        if dist_to_goal < self.goal_tolerance:
            self.get_logger().info("ZIEL ERREICHT!")
            self.current_path, self.current_narrow = [], []
            self.publish_command(msg)
            return

        target_point = None
        closest_dist = float('inf')
        closest_idx = 0

        for i, pose in enumerate(self.current_path):
            px = pose.pose.position.x
            py = pose.pose.position.y
            dist = math.hypot(px - rx, py - ry)
            if dist < closest_dist:
                closest_dist = dist
                closest_idx = i

        # --- NEU: Ziel-Index merken ---
        target_idx = closest_idx
        for i in range(closest_idx, len(self.current_path)):
            px = self.current_path[i].pose.position.x
            py = self.current_path[i].pose.position.y
            dist = math.hypot(px - rx, py - ry)

            if dist >= self.lookahead_distance:
                target_point = (px, py)
                target_idx = i
                break

        if target_point is None:
            target_point = (goal_x, goal_y)
            target_idx = len(self.current_path) - 1

        # --- NEU: Engstellen-Flag auslesen ---
        is_narrow = self.current_narrow[target_idx]

        dx = target_point[0] - rx
        dy = target_point[1] - ry

        target_yaw = math.atan2(dy, dx)

        angle_error = target_yaw - ryaw
        while angle_error > math.pi:
            angle_error -= 2.0 * math.pi
        while angle_error < -math.pi:
            angle_error += 2.0 * math.pi

        # --- NEU: Dynamische Bewegungskontrolle ---
        if is_narrow:
            # Engstellen-Modus (Sehr vorsichtig!)
            max_ang_narrow = self.max_angular_speed_narrow

            if abs(angle_error) > self.angle_threshold:
                # NUR auf der Stelle drehen, KEIN Vorwärtsfahren in der Tür!
                msg.linear.x = 0.0
                msg.angular.z = max(-max_ang_narrow, min(max_ang_narrow,
                                    angle_error * self.steering_gain))
            else:
                # Er ist gut ausgerichtet -> Langsam durchfahren
                msg.linear.x = self.max_linear_speed * self.narrow_speed_factor
                msg.angular.z = max(-max_ang_narrow, min(max_ang_narrow,
                                    angle_error * self.steering_gain))
        else:
            # Normaler Modus (Grüner Boden)
            msg.angular.z = max(-self.max_angular_speed,
                                min(self.max_angular_speed, angle_error * self.steering_gain))

            if abs(angle_error) > self.angle_threshold:
                msg.linear.x = self.max_linear_speed * self.turning_speed_factor
            else:
                msg.linear.x = self.max_linear_speed

        self.publish_command(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PathFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
