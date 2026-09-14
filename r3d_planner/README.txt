# r3d_planner

`r3d_planner` contains the runtime components of the R3D stack:

- a global A* planner that rebuilds its graph from a color-coded PCD;
- a local Hesai point-cloud filter for obstacles, steps, and cliffs;
- an RViz interface for 3D start/goal selection and `map -> odom`;
- a simple 2D lookahead path follower that publishes `/cmd_vel`;
- a static test TF for planning without a robot.

This is an `ament_python` package. `setup.py` installs five executables and
`config/r3d_planner_params.yaml`. The package has no launch file.

> **Safety:** `path_follower` publishes motion commands directly. The Go2W
> integration has been tested with its TF, LiDAR, obstacle handling, emergency
> stop, and command interface. Revalidate that chain after integration changes.

## Nodes

| Executable | Node name | Purpose | Main interfaces |
|---|---|---|---|
| `pcd_path_planner` | `global_graph_planner` | Reconstruct a graph from an analyzed RGB PCD and run A* | `/compute_path_to_pose`; `/global_path`, `/planned_path` |
| `local_filter` | `obstacle_cliff_filter` | Filter local LiDAR data and detect steps/cliffs | Hesai input; three local outputs |
| `path_follower` | `r3d_path_follower` | 2D lookahead controller | `/global_path`, `/local/filtered_obstacles`, TF; `/cmd_vel` |
| `rviz_interface` | `r3d_rviz_interface` | Initial calibration and RViz goal selection | three input topics, service, action client, TF |
| `path_test` | `r3d_path_test` | Test without real odometry | static `odom -> base_link` TF |

## Global PCD planner

`pcd_path_planner` uses `scipy.spatial.KDTree` to map start and goal positions
to the nearest graph nodes, then searches with A*. The result is returned
through the Nav2 action and published as `nav_msgs/msg/Path`.

| Parameter | Default | Unit/meaning |
|---|---|---|
| `map_dir` | `<share/r3d_preprocessor>/maps`; `/tmp` on lookup failure | Base directory |
| `map_name` | `map_analysed.pcd` | RGB PCD filename or absolute path |
| `voxel_size_cm` | 5.0 | Grid size in cm |
| `min_step_height_cm` | 5.0 | Flat/step threshold |
| `max_step_height_cm` | 25.0 | Maximum connectable step height |

The planner requires colors. It skips magenta obstacles, recognizes cyan as a
narrow area and yellow as stair access, and treats other colors as floor. Grid
and step parameters must match those used by `pcd_analyser`.

```bash
ros2 run r3d_planner pcd_path_planner --ros-args \
  -p map_name:=/absolute/path/map_analysed.pcd \
  -p voxel_size_cm:=5.0 \
  -p min_step_height_cm:=5.0 \
  -p max_step_height_cm:=25.0
```

## Topics

| Topic | Type | Publisher | Consumer/purpose |
|---|---|---|---|
| `/planned_path` | `visualization_msgs/msg/Marker` | `pcd_path_planner` | RViz `LINE_STRIP` |
| `/global_path` | `nav_msgs/msg/Path` | `pcd_path_planner` | `path_follower` |
| `/hesai_ros_driver/hesai/lidar_points` | `sensor_msgs/msg/PointCloud2` | external Hesai driver | `local_filter` |
| `/local/filtered_obstacles` | `sensor_msgs/msg/PointCloud2` | `local_filter` | `path_follower`, optional external Nav2 costmap |
| `/local/cliff_virtual_wall` | `sensor_msgs/msg/PointCloud2` | `local_filter` | no internal subscriber |
| `/stair_detect` | `geometry_msgs/msg/PointStamped` | `local_filter` | no internal subscriber |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `path_follower` | external robot base |
| `/clicked_point` | `geometry_msgs/msg/PointStamped` | RViz | `rviz_interface`; 3D height |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | RViz | `rviz_interface`; initial calibration |
| `/goal_pose` | `geometry_msgs/msg/PoseStamped` | RViz | `rviz_interface`; goal pose |

All publishers and subscriptions created here use QoS depth 10.

## Action and service

| Name | Type | Server | Client/purpose |
|---|---|---|---|
| `/compute_path_to_pose` | `nav2_msgs/action/ComputePathToPose` | `pcd_path_planner` | `rviz_interface` or external client |
| `/recalibrate_pose` | `std_srvs/srv/Trigger` | `rviz_interface` | Reset internal calibration state |

See `points.txt` for a direct action example. Start and goal headers must use
`map` because the planners do not transform request coordinates. The example's
`planner_id: GridBased` is accepted but not evaluated by the action server.

## TF frames

```text
map --(rviz_interface, static)--> odom --(external or path_test)--> base_link
```

- `rviz_interface` publishes static `map -> odom` after initial calibration.
- `path_follower` and `rviz_interface` require the composed
  `map -> base_link` transform.
- A real odometry stack must provide `odom -> base_link`.
- `path_test` publishes static identity for `odom -> base_link`; use it only
  when no real publisher supplies the transform.
- `local_filter` does not transform clouds; outputs retain the input header and
  sensor frame.

## `local_filter`

The filter assumes X points forward, Y sideways, and Z upward. It removes
points within 0.65 m, searches for step candidates, publishes points in the
obstacle height band, and creates a virtual wall when it sees too few floor
points ahead.

These values are hard-coded and are not ROS parameters:

| Value | Setting | Meaning |
|---|---:|---|
| Input | `/hesai_ros_driver/hesai/lidar_points` | Fixed topic |
| `min_height` / `max_height` | 0.05 / 1.0 m | Obstacle height band |
| `min_step_height` / `max_step_height` | 0.06 / 0.22 m | Step height band |
| Step ROI X | 0.7–1.1 m | Region ahead of sensor |
| Step ROI half-width | 0.5 m | `abs(y) < 0.5` |
| Step threshold | more than 50 points | Triggers `/stair_detect` |
| Cliff-check X | 0.7–1.2 m | Visible floor region |
| Cliff half-width | 0.4 m | `abs(y) < 0.4` |
| Safe floor | at least 30 points | Otherwise wall at X=0.7 m |

`local_filter` interprets PointCloud2 binary data as a contiguous array of
XYZ float32 values. This matches the tested Hesai integration on the Go2W;
revalidate it after changing the driver or sensor setup.

## `path_follower`

The controller finds the closest path point and then a target at least 0.5 m
ahead. It uses only XY and yaw. It detects narrow areas through an internal flag
stored in `pose.orientation.z`.

| Hard-coded value | Setting |
|---|---:|
| Lookahead | 0.5 m |
| Maximum linear speed | 0.35 m/s |
| Maximum angular speed | 0.6 rad/s |
| Obstacle stop distance | 0.6 m |
| Obstacle corridor | ±0.3 m |
| Goal tolerance | 0.2 m |
| Control period | 0.1 s (10 Hz) |
| Narrow-area angular limit | 0.2 rad/s |
| Narrow-area linear factor | 0.4 |

With no path or a detected obstacle, the node publishes a zero Twist. On a TF
failure, that control cycle publishes no new command. The controller does not
subscribe to the cliff cloud or `/stair_detect`.

```bash
ros2 run r3d_planner path_follower
```

## RViz workflow

```bash
ros2 run r3d_planner rviz_interface
```

1. Select a 3D start point, including height, with **Publish Point**.
2. Within 0.8 m in XY, use **2D Pose Estimate** to set orientation.
3. The node publishes static `map -> odom` and switches to goal mode.
4. Select the goal height with **Publish Point**.
5. Within 0.8 m, set goal position and orientation with **2D Goal Pose**.
6. The node reads `map -> base_link` as the start and sends an action request.

Reset the calibration state with:

```bash
ros2 service call /recalibrate_pose std_srvs/srv/Trigger "{}"
```

## Test operation without hardware

```bash
ros2 run r3d_planner path_test
```

This node only publishes a static identity transform from `odom` to
`base_link`. It simulates neither movement nor changing odometry. Do not run it
alongside real odometry.

## YAML configuration

`config/r3d_planner_params.yaml` is an incomplete Nav2 fragment that is not
loaded automatically. It names `/local/filtered_obstacles` as a costmap
observation source and contains an MPPI controller excerpt. Although
`cliff_virtual` appears in `observation_sources`, its configuration block is
missing. A complete external Nav2 configuration and bringup are required.

## Dependencies

### Declared in `package.xml`

`rclpy`, `nav2_msgs`, `geometry_msgs`, `nav_msgs`, `sensor_msgs`,
`visualization_msgs`, `scipy`, `numpy`, and `std_srvs`.

### Additional runtime dependencies

NetworkX, Open3D, `ament_index_python`, `sensor_msgs_py`, `tf2_ros`, and
`std_msgs`. `r3d_planner` also looks up `r3d_preprocessor` through the Ament index.
These dependencies are not fully represented in the manifest; see
`../INSTALL.md` and `../docs/KNOWN_ISSUES.md`.

The planner consumes the PCD produced by `r3d_preprocessor`. See
`../docs/ARCHITECTURE.md` for the cross-package data flow and `../INSTALL.md`
for startup order and runtime checks.
