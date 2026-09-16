# =============================================================================
# R3D-Planner
#
# Author:        Bastian Aumer
# Last modified: 2026-09-16
# Repository:    https://github.com/RoboProjekt/R3D-Planner
#
# Copyright (c) Bastian Aumer
# =============================================================================

"""SLAM-independent Odometry input; global pose needs a separate map -> odom TF."""
import math
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener


def quaternion_product(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw*bx + ax*bw + ay*bz - az*by,
            aw*by - ax*bz + ay*bw + az*bx,
            aw*bz + ax*by - ay*bx + az*bw,
            aw*bw - ax*bx - ay*by - az*bz)


def components(q):
    values = (q.x, q.y, q.z, q.w)
    norm = math.sqrt(sum(v*v for v in values))
    if not math.isfinite(norm) or norm < 1e-9:
        raise ValueError('invalid pose quaternion')
    return tuple(v / norm for v in values)


class OdometryInput:
    """Never broadcasts TF; accepts sources obeying the configured frame contract."""

    def __init__(self, node):
        self.node = node
        defaults = {'odometry_topic': '/lidar_odometry', 'odom_frame': 'odom',
                    'base_frame': 'base_link', 'map_frame': 'map', 'odometry_timeout_sec': 1.0}
        for key, value in defaults.items():
            if not node.has_parameter(key):
                node.declare_parameter(key, value)
        self.topic = node.get_parameter('odometry_topic').value
        self.odom_frame = node.get_parameter('odom_frame').value
        self.base_frame = node.get_parameter('base_frame').value
        self.map_frame = node.get_parameter('map_frame').value
        self.timeout = node.get_parameter('odometry_timeout_sec').value
        self.latest = None
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, node)
        self.subscription = node.create_subscription(Odometry, self.topic, self.callback,
                                                     qos_profile_sensor_data)

    def callback(self, msg):
        try:
            if msg.header.frame_id != self.odom_frame or msg.child_frame_id != self.base_frame:
                raise ValueError(f'expected {self.odom_frame} -> {self.base_frame}, received '
                                 f'{msg.header.frame_id} -> {msg.child_frame_id}')
            position = msg.pose.pose.position
            if not all(math.isfinite(v) for v in (position.x, position.y, position.z)):
                raise ValueError('nonfinite odometry position')
            components(msg.pose.pose.orientation)
            self.latest = msg
        except ValueError as exc:
            self.latest = None
            self.node.get_logger().warning(f'Odometry rejected: {exc}', throttle_duration_sec=2.0)

    def map_pose(self):
        msg = self.latest
        if msg is None:
            raise ValueError(f'No valid Odometry received on {self.topic}')
        stamp = Time.from_msg(msg.header.stamp)
        age = (self.node.get_clock().now() - stamp).nanoseconds / 1e9
        if age < 0 or age > self.timeout:
            raise ValueError(f'Odometry is stale or future-dated (age {age:.3f}s)')
        transform = self.buffer.lookup_transform(self.map_frame, self.odom_frame, stamp)
        q = components(transform.transform.rotation)
        p = msg.pose.pose.position
        rotated = quaternion_product(quaternion_product(q, (p.x, p.y, p.z, 0.0)),
                                     (-q[0], -q[1], -q[2], q[3]))
        orientation = quaternion_product(q, components(msg.pose.pose.orientation))
        result = PoseStamped()
        result.header.frame_id = self.map_frame
        result.header.stamp = msg.header.stamp
        translation = transform.transform.translation
        result.pose.position.x = rotated[0] + translation.x
        result.pose.position.y = rotated[1] + translation.y
        result.pose.position.z = rotated[2] + translation.z
        (result.pose.orientation.x, result.pose.orientation.y,
         result.pose.orientation.z, result.pose.orientation.w) = orientation
        return result
