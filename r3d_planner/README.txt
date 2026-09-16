# r3d_planner

This ament_python package contains the PCD-based 3D A* planner, local point-cloud
filter, RViz interface, planar path follower and static test TF node. The
package boundaries and existing generic interface names are unchanged on V3.

## Configuration and startup

The stable entry point is config/planner_config.yaml. robot_config selects a
relative robots/<robot>.yaml. The default robots/Go2W.yaml owns robot dimensions,
Odometry topic/frames and hardware cloud/command topics. The central file owns
shared graph settings, map paths, preprocessing, perception and controller tuning.

```bash
ros2 launch r3d_planner preprocessor.launch.py
ros2 launch r3d_planner planner.launch.py
```

Preprocessing starts the existing node in r3d_preprocessor and exits after writing
the analyzed map. Planner launch starts pcd_path_planner and independently starts
local_filter and rviz_interface using components.live_filter.enabled and
components.rviz_interface.enabled. Both booleans default to true. All four
combinations work. No hardware driver, RViz GUI or motion controller is included.

Optional analyzed-map display:

```bash
ros2 launch r3d_planner map.launch.py
rviz2
```

Use --symlink-install for the initial build. Editing the central or robot YAML
requires launch restart only, without rebuild or re-sourcing. New robot YAMLs
also need no build. Copied installations must set R3D_CONFIG_DIR once to live
source config. See ../docs/CONFIGURATION.md for all keys, units, validation,
ownership and robot-selection instructions. Direct ros2 run is developer-only
and does not automatically load the central YAML.

## Nodes

| Executable | Node name | Main interfaces |
|---|---|---|
| pcd_path_planner | global_graph_planner | configured Odometry input; action server, /global_path and /planned_path |
| local_filter | obstacle_cliff_filter | configured sensor cloud; obstacle, cliff and stair outputs |
| rviz_interface | r3d_rviz_interface | RViz point/pose input; action client, reset service, optional map -> odom |
| path_follower | r3d_path_follower | configured Odometry, global path and obstacles; configured velocity output |
| path_test | r3d_path_test | static identity odom -> base_link, TF-only test helper |

## Global planner and odometry

The planner reconstructs an eight-neighbor weighted NetworkX graph from analyzed
PCD points and RGB classes. Magenta obstacles are skipped, cyan identifies narrow
areas, yellow identifies stair access; other colors are treated as floor.
KDTree snaps start/goal to nearest nodes; A* uses straight-line 3D distance.
Shared voxel/step values must match those used to generate the map. Geometry
parameters are visible on the planner but do not alter an existing analyzed PCD:
regenerate the artifact after geometry changes.

The planner subscribes to nav_msgs/msg/Odometry on robot.odometry.topic
(default /lidar_odometry), exposed as ROS parameter odometry_topic.
header.frame_id and child_frame_id must match odom_frame and base_frame.
SensorDataQoS permits reliable or best-effort publishers. Pose orientation must
be valid and timestamps current. The planner uses map -> odom at the received
timestamp to compute the global base pose. No TF is broadcast by the planner.

For ComputePathToPose:

- use_start=true uses the explicit start without Odometry/TF;
- use_start=false obtains the online start from Odometry;
- goal and explicit start headers must match planner.map_frame;
- missing/stale/invalid Odometry or global TF aborts online requests;
- planner_id is accepted but not evaluated; feedback/cancellation are unchanged.

See ../README.md for complete offline/online action requests.
Path orientations retain the legacy narrow-area flag (z=1,w=1 for narrow);
generic pose consumers must not interpret it as a normalized quaternion.

## Topics

| Topic | Type | Publisher | Subscriber |
|---|---|---|---|
| robot.odometry.topic (default /lidar_odometry) | nav_msgs/msg/Odometry | external estimator | planner and explicitly started follower |


| Topic | Type | Publisher | Consumer/purpose |
|---|---|---|---|
| `/planned_path` | `visualization_msgs/msg/Marker` | `pcd_path_planner` | RViz `LINE_STRIP` |
| `/global_path` | `nav_msgs/msg/Path` | `pcd_path_planner` | `path_follower` |
| robot-configured cloud (default `/hesai_ros_driver/hesai/lidar_points`) | `sensor_msgs/msg/PointCloud2` | external driver | `local_filter` |
| `/local/filtered_obstacles` | `sensor_msgs/msg/PointCloud2` | `local_filter` | `path_follower`, optional external Nav2 costmap |
| `/local/cliff_virtual_wall` | `sensor_msgs/msg/PointCloud2` | `local_filter` | no internal subscriber |
| `/stair_detect` | `geometry_msgs/msg/PointStamped` | `local_filter` | no internal subscriber |
| robot-configured command (default `/cmd_vel`) | `geometry_msgs/msg/Twist` | `path_follower` | external robot base |
| `/clicked_point` | `geometry_msgs/msg/PointStamped` | RViz | `rviz_interface`; 3D height |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | RViz | `rviz_interface`; initial calibration |
| `/goal_pose` | `geometry_msgs/msg/PoseStamped` | RViz | `rviz_interface`; goal pose |

Existing generic interfaces use depth 10. Odometry uses SensorDataQoS.


## Action and service

| Name | Type | Server |
|---|---|---|
| /compute_path_to_pose | nav2_msgs/action/ComputePathToPose | pcd_path_planner |
| /recalibrate_pose | std_srvs/srv/Trigger | rviz_interface |

## TF and global localization

```text
map -- global localization or optional RViz calibration --> odom
odom -- external standard odometry source --> base_link
base_link -- external sensor calibration --> sensor frames
```

The planner has no direct dependency on lidar_slam_ros2 or another estimator.
The separate planned LiDAR-odometry fork is outside this repository.
The odometry source owns odom -> base_link, not map -> base_link.
Changing the Odometry topic supports other sources only when the base/odom
message and TF contracts are satisfied.

Set rviz_interface.publish_map_odom=false when an external global localizer owns
map -> odom. Point/goal pairs then work without initial calibration.
With the default true, Publish Point plus 2D Pose Estimate performs the legacy
calibration, then Publish Point plus 2D Goal Pose submits an online goal.
That calibration assumes an identity odometric base pose; it is not a general
global-localization method. The reset service changes state only.

## Local filter

All effective dead-zone, Z-band, ROI, point-count and synthetic-wall settings
are ROS parameters supplied from the central live_filter section. The input
topic comes from the selected robot YAML. Existing sensor-coordinate thresholds
and algorithms are retained. Offline graph step limits and sensor-local step
thresholds intentionally remain separate.

The filter still assumes packed 12-byte XYZ float32 records and X-forward,
Y-lateral, Z-up sensor axes; it does not generally decode PointCloud2 field
metadata or transform clouds. Recheck the driver layout after a sensor change.
Outputs keep the incoming header. Cliff and stair outputs have no internal
motion-control consumer.

## Explicit follower startup and safety

```bash
ros2 launch r3d_planner follower.launch.py
```

This separate launch can produce motion. It loads central path_follower settings
and robot Odometry/command topics. It uses XY/yaw only, including the existing
narrow-area flag. No path, detected obstacles or unavailable/stale global pose
produces zero Twist. This is not an emergency stop or complete command watchdog.

The external Go2W command adapter directly forwards velocity and can change
posture during startup. Independently validate watchdogs, command arbitration,
emergency stop and cliff handling before enabling any motion.

## Dependencies and installation

ROS dependencies include rclpy, standard navigation/sensor/geometry messages,
Nav2 actions, TF2, launch/launch_ros, ament_index_python and std_srvs.
Python libraries include Open3D, NetworkX, NumPy, SciPy and PyYAML.
r3d_preprocessor is the runtime PCD producer; no reverse dependency is added.
setup.py installs modules, executables, launch/*.launch.py, config/*.yaml and
config/robots/*.yaml. The legacy config/r3d_planner_params.yaml remains an
unattached incomplete Nav2 fragment, not an active configuration entry point.
See ../INSTALL.md and ../docs/KNOWN_ISSUES.md for metadata limitations.
