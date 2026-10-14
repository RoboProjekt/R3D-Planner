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
# Last modified: 2026-09-14
# Repository:    https://github.com/RoboProjekt/R3D-Planner
#
# Copyright (c) Bastian Aumer
# SPDX-FileCopyrightText: 2026 Bastian Aumer
# SPDX-License-Identifier: Apache-2.0
# =============================================================================

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf2_ros


class PathTestTFNode(Node):
    def __init__(self):
        super().__init__('r3d_path_test')

        # Wir nutzen einen statischen Broadcaster, da sich der "Fake"-Roboter
        # relativ zu seiner Odometrie nicht bewegt (er steht auf 0,0,0).
        self.tf_broadcaster = tf2_ros.StaticTransformBroadcaster(self)

        self.publish_fake_robot_tf()
        self.get_logger().info(
            "🛠️ Test-Modus aktiv: Fake Transform 'odom -> base_link' "
            "wird gesendet!")

    def publish_fake_robot_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()

        # Das fehlende Bindeglied: Von Odom zum Roboter
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        # Keine Abweichung: Der Roboter steht genau auf dem Odom-Nullpunkt
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0

        # Keine Rotation
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = PathTestTFNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
