# R3D-Planner

R3D-Planner is a ROS 2 navigation stack for voxelized 3D point clouds. It turns
PCD maps into a voxelized traversability map and publishes the classified map
for RViz. The planner computes fully three-dimensional paths with A* and
publishes them through standard ROS 2 interfaces. The complete stack, including
TF and sensor integration, was developed and tested on a Unitree Go2W.

> **Status:** The Unitree Go2W deployment uses a tested TF tree, LiDAR setup,
> safety chain, and `/cmd_vel` interface. Revalidate these components after any
> integration change, and operate the robot under supervision.

## Reference environment

The stack supports ROS 2 Humble. Other ROS distributions are not supported.
The commands in this guide use Ubuntu 22.04 and Python 3.10. The deployed Go2W
system provides the reference runtime environment.

## Repository structure

```text
R3D-Planner/
├── r3d_preprocessor/       # Offline map analysis and map publishers
│   ├── maps/               # Example PCD and analyzed example PCD
│   └── r3d_preprocessor/   # Python nodes
├── r3d_planner/            # Planning, filtering, RViz UI, and path following
│   ├── config/             # Nav2 configuration fragment
│   └── r3d_planner/        # Python nodes
├── docs/ARCHITECTURE.md    # Data flow and ROS interfaces
├── docs/KNOWN_ISSUES.md    # Known limitations and maintenance notes
└── INSTALL.md              # Installation, build, startup, and verification
```

Both ROS 2 packages use `ament_python`. The stack has no CMake, launch, URDF,
RViz configuration, or custom message/service/action files.

| Package | Responsibility | Installed executables |
|---|---|---|
| `r3d_preprocessor` | Voxelize PCD data, classify traversability, generate a Pickle graph or color-coded PCD, and publish maps | `pcd_to_graph`, `pcd_analyser`, `voxel_map_publisher`, `pcd_server` |
| `r3d_planner` | A* planning, local LiDAR filtering, RViz interaction, simple path following, and test TF | `global_planner`, `pcd_path_planner`, `local_filter`, `path_follower`, `rviz_interface`, `path_test` |

## Data flow

V1 supports two map and planner pipelines:

```text
Pickle pipeline:
raw PCD -> pcd_to_graph -> *.pkl -> global_planner
                                -> voxel_map_publisher -> RViz

PCD pipeline:
raw PCD -> pcd_analyser -> *_analysed.pcd -> pcd_path_planner
                         \-> pcd_server -> RViz

Runtime:
RViz input -> rviz_interface -> /compute_path_to_pose
                                 |               |
                                 |               v
map -> odom -> base_link         |          /global_path
                                 |               |
LiDAR -> local_filter -> /local/filtered_obstacles
                                                 |
                                                 v
                                          path_follower
                                                 |
                                                 v
                                             /cmd_vel
```

`global_planner` and `pcd_path_planner` are alternatives. Both use the node
name `global_graph_planner`, provide `/compute_path_to_pose`, and publish the
same path topics. They must not run at the same time. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for node-level details.

## Main ROS interfaces

| Name | Type | Producer | Consumer/purpose |
|---|---|---|---|
| `/compute_path_to_pose` | `nav2_msgs/action/ComputePathToPose` | one global planner | `rviz_interface` or external client |
| `/global_path` | `nav_msgs/msg/Path` | one global planner | `path_follower` |
| `/planned_path` | `visualization_msgs/msg/Marker` | one global planner | RViz |
| `/map_pointcloud` | `sensor_msgs/msg/PointCloud2` | `pcd_server` | RViz/external components |
| `/r3d_global_voxel_map` | `visualization_msgs/msg/Marker` | `voxel_map_publisher` | RViz |
| `/hesai_ros_driver/hesai/lidar_points` | `sensor_msgs/msg/PointCloud2` | external Hesai driver | `local_filter` |
| `/local/filtered_obstacles` | `sensor_msgs/msg/PointCloud2` | `local_filter` | `path_follower`, optional Nav2 integration |
| `/local/cliff_virtual_wall` | `sensor_msgs/msg/PointCloud2` | `local_filter` | no internal subscriber |
| `/stair_detect` | `geometry_msgs/msg/PointStamped` | `local_filter` | no internal subscriber |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `path_follower` | external robot base |
| `/clicked_point`, `/initialpose`, `/goal_pose` | standard RViz messages | RViz | `rviz_interface` |
| `/recalibrate_pose` | `std_srvs/srv/Trigger` | `rviz_interface` | reset calibration state |

Unless stated otherwise, publishers and subscriptions use the rclpy default
QoS with depth 10. The static map publishers use `TRANSIENT_LOCAL` with depth 1.

## TF requirements

The intended tree is:

```text
map --(rviz_interface, static)--> odom --(robot or path_test)--> base_link
```

`path_follower` and `rviz_interface` query `map -> base_link`. A real robot must
provide `odom -> base_link`. For tests only, `path_test` publishes a static
identity transform from `odom` to `base_link`; it must not run alongside a real
publisher for the same transform.

`local_filter` does not transform sensor frames; its output retains the frame
of the incoming cloud. The documented TF chain, LiDAR orientation, and sensor
integration have been tested on the Go2W.

## Planning test with the included analyzed PCD

After building as described in [INSTALL.md](INSTALL.md), source ROS and the
workspace in every terminal:

```bash
source /opt/ros/humble/setup.bash
source <workspace>/install/setup.bash
```

1. Publish the analyzed map for RViz (optional):

   ```bash
   ros2 run r3d_preprocessor pcd_server --ros-args \
     -p pcd_path:=<workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd
   ```

2. Start the PCD-based planner:

   ```bash
   ros2 run r3d_planner pcd_path_planner --ros-args \
     -p map_name:=<workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd \
     -p voxel_size_cm:=5.0 \
     -p min_step_height_cm:=5.0 \
     -p max_step_height_cm:=25.0
   ```

3. For a TF/planning test without a robot only:

   ```bash
   ros2 run r3d_planner path_test
   ros2 run r3d_planner rviz_interface
   rviz2
   ```

   Set the RViz Fixed Frame to `map`. Set the `/map_pointcloud` display
   durability to `Transient Local`; use a Marker display for `/planned_path`.

`path_follower` and `local_filter` are deliberately excluded from this harmless
planning test because `path_follower` publishes real velocity commands. See
[INSTALL.md](INSTALL.md#startup) before hardware use.

## Map preprocessing

Generate a color-coded PCD with:

```bash
ros2 run r3d_preprocessor pcd_analyser --ros-args \
  -p pcd_path:=/absolute/path/map.pcd \
  -p voxel_size_cm:=5.0 \
  -p min_step_height_cm:=5.0 \
  -p max_step_height_cm:=25.0
```

The output is written beside the input as `map_analysed.pcd`. The planner
interprets colors as follows: magenta = obstacle (skipped), cyan = narrow area,
yellow = stair access, and other colors = floor.

Alternatively, `pcd_to_graph` creates a `nav_graph_*.pkl` for
`global_planner`. Load Pickle files only from trusted sources.

## Configuration

- Pass offline analysis parameters to `pcd_analyser` or `pcd_to_graph` as ROS
  parameters.
- Pass planner map parameters as ROS parameters.
- Thresholds in `local_filter`, controller values in `path_follower`, and the
  RViz matching radius are hard-coded Python values, not ROS parameters.
- `r3d_planner/config/r3d_planner_params.yaml` is an incomplete Nav2
  configuration fragment. No launch file loads it automatically.
- There are no launch files; start all processes individually with `ros2 run`.

## Documentation

- [Installation, build, startup, and verification](INSTALL.md)
- [Architecture and ROS interfaces](docs/ARCHITECTURE.md)
- [Known issues and open runtime checks](docs/KNOWN_ISSUES.md)
- [V1 documentation scope](docs/README_AUDIT.md)
- [`r3d_preprocessor` package documentation](r3d_preprocessor/README.txt)
- [`r3d_planner` package documentation](r3d_planner/README.txt)
