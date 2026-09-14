# R3D-Planner

R3D-Planner is a ROS 2 based 3D navigation stack for voxelized point clouds.
The V2 implementation converts a PCD map into a color-coded PCD map, rebuilds a
NetworkX graph from that PCD in memory, computes a three-dimensional A* path,
and can follow the path with a simple local controller. According to the
original documentation, the target platform was a Unitree Go2W; general
hardware compatibility has not been demonstrated by this repository.

> **Status:** Research/thesis prototype. Before operating real hardware, verify
> the TF tree, LiDAR coordinate system, safety chain, and `/cmd_vel` consumer.
> Do not use the stack to move a robot without supervision.

## Verified environment

The repository does not define a binding operating-system or ROS 2 support
matrix. The analysis was performed with Ubuntu 22.04, ROS 2 Humble, and Python
3.10. The previous root documentation also referenced Humble. Other ROS
distributions are **not determinable from the source** and require separate
verification.

## Repository structure

```text
R3D-Planner/
├── r3d_preprocessor/       # Offline PCD analysis and PCD publisher
│   ├── maps/               # Example PCD and analyzed example PCD
│   └── r3d_preprocessor/   # Python nodes
├── r3d_planner/            # Planning, filtering, RViz UI, and path following
│   ├── config/             # Nav2 configuration fragment
│   └── r3d_planner/        # Python nodes
├── docs/ARCHITECTURE.md    # Complete data-flow and interface analysis
├── docs/KNOWN_ISSUES.md    # Observed issues that have not been fixed
└── INSTALL.md              # Installation, build, startup, and verification
```

Both ROS 2 packages use `ament_python`. The source tree contains no CMake,
launch, URDF, RViz, or custom message/service/action files.

| Package | Responsibility | Installed executables |
|---|---|---|
| `r3d_preprocessor` | Voxelize PCD data, classify traversability, generate a color-coded PCD, and publish it | `pcd_analyser`, `pcd_server` |
| `r3d_planner` | PCD-based A* planning, local LiDAR filtering, RViz interaction, simple path following, and test TF | `pcd_path_planner`, `local_filter`, `path_follower`, `rviz_interface`, `path_test` |

## Architecture at a glance

V2 contains one PCD-only map/planner pipeline:

```text
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

The former Pickle generator, Pickle marker publisher, and Pickle-based planner
are intentionally absent from V2. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the complete PCD data flow.

## Main ROS interfaces

| Name | Type | Producer | Consumer/purpose |
|---|---|---|---|
| `/compute_path_to_pose` | `nav2_msgs/action/ComputePathToPose` | `pcd_path_planner` | `rviz_interface` or external client |
| `/global_path` | `nav_msgs/msg/Path` | `pcd_path_planner` | `path_follower` |
| `/planned_path` | `visualization_msgs/msg/Marker` | `pcd_path_planner` | RViz |
| `/map_pointcloud` | `sensor_msgs/msg/PointCloud2` | `pcd_server` | RViz/external components |
| `/hesai_ros_driver/hesai/lidar_points` | `sensor_msgs/msg/PointCloud2` | external Hesai driver | `local_filter` |
| `/local/filtered_obstacles` | `sensor_msgs/msg/PointCloud2` | `local_filter` | `path_follower`, optional Nav2 integration |
| `/local/cliff_virtual_wall` | `sensor_msgs/msg/PointCloud2` | `local_filter` | no active subscriber in this repository |
| `/stair_detect` | `geometry_msgs/msg/PointStamped` | `local_filter` | no subscriber in this repository |
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

Sensor frames are not transformed by the code. `local_filter` retains the frame
of the incoming cloud. Verify the complete TF chain and actual LiDAR
orientation at runtime.

## Quick planning test with the included analyzed PCD

Full installation and build instructions are in [INSTALL.md](INSTALL.md). After
a successful build, source the environment in every terminal:

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
[INSTALL.md](INSTALL.md#runtime-variants-and-startup-order) before hardware use.

## Map preprocessing

The PCD workflow documented by the current root procedure produces a
color-coded PCD:

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

V2 does not generate or load `.pkl` files. Its persisted map exchange format is
the analyzed RGB PCD.

## Configuration

- Pass offline analysis parameters to `pcd_analyser` as ROS parameters.
- Pass planner map parameters as ROS parameters.
- Thresholds in `local_filter`, controller values in `path_follower`, and the
  RViz matching radius are hard-coded Python values, not ROS parameters.
- `r3d_planner/config/r3d_planner_params.yaml` is an incomplete Nav2
  configuration fragment. Nothing in this repository loads it automatically.
- There are no launch files; start all processes individually with `ros2 run`.

## Documentation

- [Installation, build, startup, and verification](INSTALL.md)
- [Architecture and complete ROS interfaces](docs/ARCHITECTURE.md)
- [Known issues and open runtime checks](docs/KNOWN_ISSUES.md)
- [Audit of the previous READMEs against the code](docs/README_AUDIT.md)
- [`r3d_preprocessor` package documentation](r3d_preprocessor/README.txt)
- [`r3d_planner` package documentation](r3d_planner/README.txt)
