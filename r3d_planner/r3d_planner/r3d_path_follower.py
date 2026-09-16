# =============================================================================
# R3D-Planner
#
# Author:        Bastian Aumer
# Last modified: 2026-09-16
# Repository:    https://github.com/RoboProjekt/R3D-Planner
#
# Copyright (c) Bastian Aumer
# =============================================================================

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Path
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import math
from .odometry import OdometryInput

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

        # --- VARIABLEN ---
        self.current_path = []
        self.obstacle_in_front = False

        # --- PUBLISHER & SUBSCRIBER ---
        self.cmd_pub = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        
        self.path_sub = self.create_subscription(
            Path, '/global_path', self.path_callback, 10)
            
        self.obstacle_sub = self.create_subscription(
            PointCloud2, '/local/filtered_obstacles', self.obstacle_callback, 10)

        # --- TF (Transformationen) ---
        # --- CONTROL LOOP ---
        self.timer = self.create_timer(self.control_period_sec, self.control_loop)
        self.get_logger().info("R3D Path Follower gestartet! Warte auf Pfad...")

    def path_callback(self, msg):
        self.current_path = msg.poses
        self.get_logger().info(f"Neuer Pfad empfangen mit {len(self.current_path)} Punkten.")

    def obstacle_callback(self, msg):
        obstacle_detected = False
        
        for point in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
            x, y, z = point
            if self.obstacle_x_min < x < self.stop_distance and abs(y) < self.obstacle_half_width:
                obstacle_detected = True
                break
                
        if obstacle_detected and not self.obstacle_in_front:
            self.get_logger().warn("DYNAMISCHES HINDERNIS! Stoppe...")
        elif not obstacle_detected and self.obstacle_in_front:
            self.get_logger().info("Weg ist wieder frei.")
            
        self.obstacle_in_front = obstacle_detected

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
        except Exception as e:
            return None, None, None

    def control_loop(self):
        msg = Twist()

        if not self.current_path:
            self.cmd_pub.publish(msg)
            return

        if self.obstacle_in_front:
            self.cmd_pub.publish(msg)
            return

        rx, ry, ryaw = self.get_robot_pose()
        if rx is None:
            self.cmd_pub.publish(msg)
            return

        goal_x = self.current_path[-1].pose.position.x
        goal_y = self.current_path[-1].pose.position.y
        dist_to_goal = math.hypot(goal_x - rx, goal_y - ry)
        
        if dist_to_goal < self.goal_tolerance:
            self.get_logger().info("ZIEL ERREICHT!")
            self.current_path = [] 
            self.cmd_pub.publish(msg) 
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
        is_narrow = (self.current_path[target_idx].pose.orientation.z > 0.5)

        dx = target_point[0] - rx
        dy = target_point[1] - ry
        
        target_yaw = math.atan2(dy, dx)
        
        angle_error = target_yaw - ryaw
        while angle_error > math.pi: angle_error -= 2.0 * math.pi
        while angle_error < -math.pi: angle_error += 2.0 * math.pi

        # --- NEU: Dynamische Bewegungskontrolle ---
        if is_narrow:
            # Engstellen-Modus (Sehr vorsichtig!)
            max_ang_narrow = self.max_angular_speed_narrow
            
            if abs(angle_error) > self.angle_threshold:
                # NUR auf der Stelle drehen, KEIN Vorwärtsfahren in der Tür!
                msg.linear.x = 0.0 
                msg.angular.z = max(-max_ang_narrow, min(max_ang_narrow, angle_error * self.steering_gain))
            else:
                # Er ist gut ausgerichtet -> Langsam durchfahren
                msg.linear.x = self.max_linear_speed * self.narrow_speed_factor
                msg.angular.z = max(-max_ang_narrow, min(max_ang_narrow, angle_error * self.steering_gain))
        else:
            # Normaler Modus (Grüner Boden)
            msg.angular.z = max(-self.max_angular_speed, min(self.max_angular_speed, angle_error * self.steering_gain))
            
            if abs(angle_error) > self.angle_threshold:
                msg.linear.x = self.max_linear_speed * self.turning_speed_factor
            else:
                msg.linear.x = self.max_linear_speed

        self.cmd_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = PathFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
