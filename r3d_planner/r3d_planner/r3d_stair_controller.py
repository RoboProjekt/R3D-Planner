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

"""ROS adapter for the stopped and acknowledged Go2W stair-mode sequence."""
import math
import time

import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from rclpy.time import Time
from rcl_interfaces.msg import ParameterDescriptor
from r3d_interfaces.msg import PathWithMetadata, StairDetection, StairStatus
from std_srvs.srv import Trigger

from .configuration import load_robot_profile, stair_settings
from .odometry import OdometryInput, components, quaternion_product
from .path_metadata import metadata_qos, path_fingerprint, validate_metadata
from .stair_control import SdkSwitch, StairCoordinator, StairRoute


class StairController(Node):
    """Fuse planned stairs, live detections and fresh map-frame robot poses."""

    def __init__(self):
        super().__init__('r3d_stair_controller')
        _, robot = load_robot_profile()
        defaults = {**stair_settings(robot.get('stairs')),
                    'sdk_executable': '/home/unitree/go2w_gait_switch/build/go2w_gait_switch',
                    'guard_executable': '/home/unitree/.local/bin/r3d_go2w_gait_guard',
                    'network_interface': 'eth0', 'sdk_timeout_sec': 20.0}
        for key, value in defaults.items():
            self.declare_parameter(key, value, ParameterDescriptor(read_only=True))
        self.coordinator = StairCoordinator(
            self.get_parameter('approach_distance_m').value,
            self.get_parameter('exit_distance_m').value)
        self.sdk = SdkSwitch(self.get_parameter('sdk_executable').value,
                             self.get_parameter('network_interface').value,
                             self.get_parameter('sdk_timeout_sec').value,
                             self.get_parameter('guard_executable').value)
        self.odometry = OdometryInput(self)
        self.route = None
        self.path_id = ''
        self.detection = None
        self.detection_received = None
        self.pause_id = 0
        self.pause_ack = None
        self.pause_ack_received = None
        self.pause_started = None
        self.pending_mode = None
        self.status_publisher = self.create_publisher(StairStatus, '/stair_control', 10)
        self.detection_publisher = self.create_publisher(StairDetection, '/stair_detect', 10)
        self.path_subscription = self.create_subscription(
            PathWithMetadata, '/global_path_metadata', self.path_callback, metadata_qos())
        self.detection_subscription = self.create_subscription(
            StairDetection, '/stair_detect', self.detection_callback, 10)
        self.pause_subscription = self.create_subscription(
            StairStatus, '/stair_command_ack', self.pause_callback, 10)
        self.retry_service = self.create_service(Trigger, '~/retry', self.retry_callback)
        self.timer = self.create_timer(
            0.05, self.tick, clock=Clock(clock_type=ClockType.STEADY_TIME))
        self.last_state = None

    def path_callback(self, message):
        """Reject incomplete terrain flags before authorizing any motion."""
        try:
            validate_metadata(message, self.odometry.map_frame, require_stairs=True)
            positions = [(p.pose.position.x, p.pose.position.y, p.pose.position.z)
                         for p in message.path.poses]
            route = StairRoute(positions, message.stairs)
            path_id = path_fingerprint(message)
            if self.coordinator.switching and self.path_id != path_id:
                self.abort_switch('Path changed during gait transition. '
                                  'Retry after checking the route')
            self.route, self.path_id = route, path_id
        except ValueError as exc:
            if self.coordinator.switching:
                self.abort_switch(str(exc))
            self.route, self.path_id = None, ''
            self.coordinator.hold(str(exc))
        self.coordinator.motion_allowed = False
        self.publish_status()

    def detection_callback(self, message):
        """Store positive and explicit no-stair observations with receipt freshness."""
        self.detection = message
        self.detection_received = time.monotonic()

    def pause_callback(self, message):
        """Record the follower acknowledgement for this specific pause request."""
        self.pause_ack = message
        self.pause_ack_received = time.monotonic()

    def pause_confirmed(self, now):
        """Reject stale or mismatched acknowledgements before invoking the SDK guard."""
        ack = self.pause_ack
        if ack is None or not ack.pause_commands:
            return False
        age = (self.get_clock().now() - Time.from_msg(ack.header.stamp)).nanoseconds / 1e9
        return (ack.pause_id == self.pause_id and ack.path_id == self.path_id and
                ack.header.frame_id == self.odometry.map_frame and
                0 <= age <= 0.5 and 0 <= now - self.pause_ack_received <= 0.5)

    def abort_switch(self, detail):
        """Abort the outstanding operation and restore zero-command publication."""
        self.sdk.close()
        self.pending_mode = None
        self.coordinator.confirmed(False, detail)

    def matching_detection(self, steady_now):
        """Transform a fresh sensor observation into the planned map frame."""
        message = self.detection
        if message is None or not message.detected:
            return None
        age = (self.get_clock().now() - Time.from_msg(message.header.stamp)).nanoseconds / 1e9
        if not 0 <= age <= 1.0 or not 0 <= steady_now - self.detection_received <= 1.0:
            return None
        point = (message.point.x, message.point.y, message.point.z)
        if not all(math.isfinite(v) for v in point) or not message.header.frame_id:
            return None
        if message.header.frame_id == self.odometry.map_frame:
            return point
        try:
            transform = self.odometry.buffer.lookup_transform(
                self.odometry.map_frame, message.header.frame_id,
                Time.from_msg(message.header.stamp))
            q = components(transform.transform.rotation)
            rotated = quaternion_product(quaternion_product(q, (*point, 0.0)),
                                         (-q[0], -q[1], -q[2], q[3]))
            t = transform.transform.translation
            result = (rotated[0] + t.x, rotated[1] + t.y, rotated[2] + t.z)
            return result if all(math.isfinite(v) for v in result) else None
        except Exception:
            return None

    def tick(self):
        """Keep status alive while the SDK runs and fail closed on missing inputs."""
        now = time.monotonic()
        if (self.coordinator.switching and self.pending_mode is None and
                not self.pause_confirmed(now)):
            self.abort_switch('Follower command-pause acknowledgement expired')
        result = self.sdk.poll(now)
        if result is not None:
            self.coordinator.confirmed(*result)
        mode = None
        try:
            if self.route is None:
                raise ValueError('Waiting for a valid path with stair metadata')
            map_pose = self.odometry.map_pose().pose
            pose = map_pose.position
            qx, qy, qz, qw = components(map_pose.orientation)
            # The local vertical must be within about eight degrees of map vertical.
            level = 1.0 - 2.0 * (qx * qx + qy * qy) >= math.cos(math.radians(8))
            velocity = self.odometry.latest.twist.twist
            speeds = (velocity.linear.x, velocity.linear.y, velocity.linear.z,
                      velocity.angular.x, velocity.angular.y, velocity.angular.z)
            stationary = (all(math.isfinite(v) for v in speeds) and
                          math.sqrt(sum(v * v for v in speeds[:3])) <= 0.02 and
                          math.sqrt(sum(v * v for v in speeds[3:])) <= 0.03)
            mode = self.coordinator.step(self.route, (pose.x, pose.y, pose.z), stationary,
                                         self.matching_detection(now), now, level=level)
        except Exception as exc:
            if self.coordinator.switching:
                self.abort_switch(str(exc))
            elif self.coordinator.state != 'ERROR':
                self.coordinator.hold(str(exc))
        if mode is not None:
            self.pause_id = time.monotonic_ns()
            self.pause_started = now
            self.pending_mode = mode
        # Withdraw movement permission before the external command is started.
        self.publish_status()
        if self.coordinator.clear_detection:
            cleared = StairDetection(detected=False)
            cleared.header.frame_id = self.odometry.map_frame
            cleared.header.stamp = self.get_clock().now().to_msg()
            self.detection_publisher.publish(cleared)
            self.coordinator.clear_detection = False
            self.detection = None
        if self.pending_mode is not None and now - self.pause_started > 1.0:
            self.abort_switch('Follower did not acknowledge command pause within 1 s')
            self.publish_status()
        elif self.pending_mode is not None and self.pause_confirmed(now):
            try:
                self.sdk.start(self.pending_mode, now)
                self.pending_mode = None
            except (OSError, ValueError) as exc:
                self.abort_switch(str(exc))
                self.publish_status()

    def publish_status(self):
        """Publish a timestamped permit bound to the complete current path."""
        coordinator = self.coordinator
        message = StairStatus(path_id=self.path_id, state=coordinator.state,
                              motion_allowed=coordinator.motion_allowed,
                              stair_mode_active=coordinator.stair_mode_active,
                              pause_commands=coordinator.switching,
                              pause_id=self.pause_id,
                              detail=coordinator.detail)
        message.header.frame_id = self.odometry.map_frame
        message.header.stamp = self.get_clock().now().to_msg()
        self.status_publisher.publish(message)
        if coordinator.state != self.last_state:
            self.get_logger().info(f'Stair control: {coordinator.state}: {coordinator.detail}')
            self.last_state = coordinator.state

    def retry_callback(self, request, response):
        """Allow an operator to retry an SDK failure after correcting its cause."""
        response.success = self.coordinator.retry()
        response.message = 'Retry requested' if response.success else 'No SDK error to retry'
        return response

    def destroy_node(self):
        """Withdraw permission and terminate any outstanding tool on shutdown."""
        self.sdk.close()
        self.coordinator.switching = False
        self.coordinator.motion_allowed = False
        try:
            if rclpy.ok(context=self.context):
                self.publish_status()
        finally:
            self.sdk.close()
        return super().destroy_node()


def main(args=None):
    """Run the coordinator on the Jetson beside the installed SDK executable."""
    rclpy.init(args=args)
    node = StairController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
