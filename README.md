# R3D-Planner

## Overview and goals

R3D-Planner is a ROS 2 Humble navigation stack for voxelized 3D point clouds.
It analyzes PCD maps, classifies traversability, and stores the result as a
color-coded PCD. The global planner builds a 3D graph from that map, computes
fully three-dimensional paths with A*, and publishes them through
`nav2_msgs/action/ComputePathToPose`.

The complete system was developed and tested on a Unitree Go2W, including the
Hesai point-cloud input, TF tree, RViz workflow, local obstacle filter, and
`/cmd_vel` interface. Other ROS distributions are not supported.

The source-level comparison with the original deployment repository is in
[`docs/REFERENCE_COMPARISON.md`](docs/REFERENCE_COMPARISON.md).

V2 uses a PCD-only pipeline:

```text
PCD map -> pcd_analyser -> *_analysed.pcd -> pcd_path_planner
                              |
                              +-> pcd_server -> RViz

Hesai LiDAR -> local_filter -> path_follower -> /cmd_vel
RViz input  -> rviz_interface -> /compute_path_to_pose
```

The workspace contains two `ament_python` packages:

| Package | Purpose | Executables |
|---|---|---|
| `r3d_preprocessor` | Analyze and publish PCD maps | `pcd_analyser`, `pcd_server` |
| `r3d_planner` | Global planning, local filtering, RViz input, path following, and test TF | `pcd_path_planner`, `local_filter`, `rviz_interface`, `path_follower`, `path_test` |

### Robot-independent and Go2W-specific parts

Offline PCD voxelization, traversability classification, graph reconstruction,
A*, and the `ComputePathToPose` interface are independent of the Go2W hardware.
The map can originate from any sensor pipeline that produces a PCD in the
intended `map` coordinates. Robot radius, narrow radius, height, base clearance,
voxel size, and step limits are ROS parameters during preprocessing; the PCD
planner separately accepts voxel and step limits.

The online layer is configured for the Go2W deployment: `local_filter` uses the
fixed Hesai topic and sensor-axis assumptions, the TF consumers require
`map`, `odom`, and `base_link`, and `path_follower` publishes fixed-limit
`Twist` commands on `/cmd_vel`. A different robot must supply the same TF and
message contracts or remap topics, and must retune dimensions and motion
limits. Sensor/filter thresholds, controller limits, and frame names are source
constants rather than ROS parameters, so adaptation is not configuration-only
in the current implementation.

## Installation

The supported setup uses Ubuntu 22.04, ROS 2 Humble, and Python 3.10.

### Dependencies

```bash
sudo apt update
sudo apt install \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-pip \
  python3-numpy \
  python3-scipy \
  python3-networkx \
  python3-open3d \
  ros-humble-ament-index-python \
  ros-humble-geometry-msgs \
  ros-humble-nav-msgs \
  ros-humble-nav2-msgs \
  ros-humble-rclpy \
  ros-humble-sensor-msgs \
  ros-humble-sensor-msgs-py \
  ros-humble-std-msgs \
  ros-humble-std-srvs \
  ros-humble-tf2-ros \
  ros-humble-tf2-ros-py \
  ros-humble-visualization-msgs \
  ros-humble-rviz2
```

Open3D handles PCD data, NetworkX stores the in-memory navigation graph, SciPy
supplies the nearest-node KDTree, and NumPy is used for point-cloud and geometry
operations.

### Workspace, rosdep, and build

Replace every `<path-to-workspace>` placeholder below with the absolute path of
your ROS 2 workspace before running a command.

```bash
mkdir -p <path-to-workspace>/src
cd <path-to-workspace>/src
git clone git@github.com:RoboProjekt/R3D-Planner.git
cd R3D-Planner
git checkout V2
cd <path-to-workspace>
```

The package manifests contain the unresolved rosdep key `numpy` and, depending
on the rosdep database, `scipy`. Install the packages above and run rosdep with
these exclusions:

```bash
sudo rosdep init  # only on a new ROS installation
rosdep update
cd <path-to-workspace>
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="numpy scipy"
```

Build and source the workspace:

```bash
cd <path-to-workspace>
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Source `/opt/ros/humble/setup.bash` and
`<path-to-workspace>/install/setup.bash` in every
terminal used below. See [INSTALL.md](INSTALL.md) for troubleshooting and the
known package-metadata limitations.

## Using `r3d_preprocessor`

`pcd_analyser` loads a PCD map, voxelizes it, fills eligible floor gaps, checks
robot clearance, and classifies traversable, narrow, stair, and obstacle
voxels. It writes the result beside the source map as `<name>_analysed.pcd`.
The output colors are green for floor, cyan for narrow areas, yellow for stair
access, and magenta for obstacles.

### Preprocessor parameters

| Parameter | Default | Unit | Description |
|---|---:|---|---|
| `pcd_path` | `environment.pcd` | path | Input PCD file; `~` is expanded |
| `voxel_size_cm` | `5.0` | cm | Voxel edge length |
| `max_step_height_cm` | `25.0` | cm | Largest height difference connected as a step |
| `min_step_height_cm` | `5.0` | cm | Boundary between flat and step connections |
| `min_points_per_sqm` | `10.0` | points/m² | Converted to a per-cell floor-fill threshold; at least three points are always required |
| `min_points_per_voxel` | `3` | points | Minimum hits retained in an occupied voxel |
| `floor_height_tolerance` | `0.02` | m | Planarity term; a height cluster is filled when its Z range is below `2*tolerance + 0.02 m` |
| `ground_fill` | `true` | bool | Enables density and neighborhood floor filling |
| `robot_base_clearance_cm` | `10.0` | cm | Lower start of the collision check above the floor |
| `robot_narrow_radius_cm` | `30.0` | cm | Reduced radius used to classify narrow passages |
| `robot_radius_cm` | `40.0` | cm | Normal collision radius |
| `robot_height_cm` | `80.0` | cm | Height of the collision cylinder |
| `analysis_grid_size_cm` | `20.0` | cm | XY cell size for density analysis |
| `cluster_gap_threshold_cm` | `20.0` | cm | Vertical gap used to separate height clusters |
| `fill_plane_iterations` | `2` | count | Maximum neighborhood-fill iterations |
| `fill_plane_search_radius` | `2` | voxels | Search radius for plane filling |
| `fill_plane_min_neighbors` | `4` | count | Required floor neighbors for filling |

### Analyze a map

This full invocation shows every configurable parameter. V2 uses
`pcd_analyser`; the `pcd_to_graph` executable belongs to V1 and is not available
on this branch.

```bash
ros2 run r3d_preprocessor pcd_analyser --ros-args \
  -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7.pcd \
  -p voxel_size_cm:=5.0 \
  -p max_step_height_cm:=25.0 \
  -p min_points_per_sqm:=10.0 \
  -p min_points_per_voxel:=1 \
  -p floor_height_tolerance:=0.03 \
  -p ground_fill:=false \
  -p robot_base_clearance_cm:=10.0 \
  -p robot_narrow_radius_cm:=30.0 \
  -p min_step_height_cm:=5.0 \
  -p robot_radius_cm:=40.0 \
  -p robot_height_cm:=80.0 \
  -p analysis_grid_size_cm:=20.0 \
  -p cluster_gap_threshold_cm:=20.0 \
  -p fill_plane_iterations:=2 \
  -p fill_plane_search_radius:=2 \
  -p fill_plane_min_neighbors:=4
```

### Tested map configurations

These presets use the parameter combinations from the deployed map workflow.
Only `voxel_05_minhits_7.pcd` is included in this repository. Copy the other
maps to the stated paths or replace `pcd_path` with their actual location.

RoboLab map:

```bash
ros2 run r3d_preprocessor pcd_analyser --ros-args -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/RoboLab_map.pcd -p voxel_size_cm:=5.0 -p max_step_height_cm:=20.0 -p min_points_per_sqm:=10.0 -p min_points_per_voxel:=1 -p floor_height_tolerance:=0.03 -p ground_fill:=true -p robot_base_clearance_cm:=10.0 -p robot_narrow_radius_cm:=30.0
```

HomeLab map:

```bash
ros2 run r3d_preprocessor pcd_analyser --ros-args -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/HomeLab_map1_lidar.pcd -p voxel_size_cm:=5.0 -p max_step_height_cm:=20.0 -p min_points_per_sqm:=10.0 -p min_points_per_voxel:=1 -p floor_height_tolerance:=0.03 -p ground_fill:=true -p robot_base_clearance_cm:=10.0 -p robot_narrow_radius_cm:=30.0
```

Included voxel map with the reduced density threshold:

```bash
ros2 run r3d_preprocessor pcd_analyser --ros-args -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7.pcd -p voxel_size_cm:=5.0 -p max_step_height_cm:=20.0 -p min_points_per_sqm:=1.0 -p min_points_per_voxel:=1 -p floor_height_tolerance:=0.05 -p ground_fill:=false -p robot_base_clearance_cm:=10.0 -p robot_narrow_radius_cm:=30.0
```

Unfiltered stair scan:

```bash
ros2 run r3d_preprocessor pcd_analyser --ros-args -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/Stair_unfiltered.pcd -p voxel_size_cm:=5.0 -p max_step_height_cm:=20.0 -p min_points_per_sqm:=1.0 -p min_points_per_voxel:=7 -p floor_height_tolerance:=0.05 -p ground_fill:=false -p robot_base_clearance_cm:=10.0 -p robot_narrow_radius_cm:=30.0
```

### Publish the source or analyzed map

```bash
ros2 run r3d_preprocessor pcd_server --ros-args \
  -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd
```

`pcd_server` publishes `/map_pointcloud` with transient-local durability:

| Parameter | Default | Description |
|---|---|---|
| `pcd_path` | `environment.pcd` | PCD file published in frame `map` |

In RViz, add a PointCloud2 display for `/map_pointcloud`, set durability to
`Transient Local`, and use `RGB8` to display the traversability colors.

## Using `r3d_planner`

### Offline planning with an analyzed PCD

Start the PCD planner with the same voxel and step values used during
preprocessing:

```bash
ros2 run r3d_planner pcd_path_planner --ros-args \
  -p map_name:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd \
  -p voxel_size_cm:=5.0 \
  -p min_step_height_cm:=5.0 \
  -p max_step_height_cm:=25.0
```

| Parameter | Default | Description |
|---|---|---|
| `map_dir` | `<share/r3d_preprocessor>/maps`, fallback `/tmp` | Directory used for relative PCD names |
| `map_name` | `map_analysed.pcd` | Color-coded PCD filename or absolute path |
| `voxel_size_cm` | `5.0` | Reconstruction grid size; must match preprocessing |
| `min_step_height_cm` | `5.0` | Flat-to-step boundary; must match preprocessing |
| `max_step_height_cm` | `25.0` | Maximum connected step height; must match preprocessing |

The default package map directory is not installed. Pass an absolute
`map_name` or use the explicit workspace path above.

Send a 3D start and goal:

```bash
ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose "{
  use_start: true,
  start: {
    header: {frame_id: 'map'},
    pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}
  },
  goal: {
    header: {frame_id: 'map'},
    pose: {position: {x: 5.0, y: 0.0, z: 2.5}, orientation: {w: 1.0}}
  },
  planner_id: 'GridBased'
}"
```

The deployed HomeLab workflow also uses this site-specific request:

```bash
ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose "{
  use_start: true,
  start: {
    header: {frame_id: 'map'},
    pose: {position: {x: 0, y: 0, z: -0.3}, orientation: {w: 1.0}}
  },
  goal: {
    header: {frame_id: 'map'},
    pose: {position: {x: -1, y: -10.24, z: -0.3}, orientation: {w: 1.0}}
  },
  planner_id: 'GridBased'
}"
```

| Goal field | Description |
|---|---|
| `use_start` | Uses the supplied `start` pose when `true` |
| `start` | 3D start pose in `map` coordinates |
| `goal` | 3D goal pose in `map` coordinates |
| `planner_id` | Accepted by the action interface but not evaluated by the planner |

The planner returns the path in the action result, publishes
`nav_msgs/msg/Path` on `/global_path`, and publishes a `LINE_STRIP` Marker on
`/planned_path`.

### Online operation on the Go2W

The online stack requires the tested Go2W components that publish the Hesai
cloud on `/hesai_ros_driver/hesai/lidar_points`, provide
`odom -> base_link`, and consume `/cmd_vel`.

Start `pcd_path_planner`, then run:

```bash
ros2 run r3d_planner local_filter
ros2 run r3d_planner rviz_interface
ros2 run r3d_planner path_follower
```

`local_filter` publishes obstacles on `/local/filtered_obstacles`, a virtual
cliff wall on `/local/cliff_virtual_wall`, and step detections on
`/stair_detect`. It has no ROS parameters; its topic names and thresholds are
defined in `r3d_local_filter.py`.

`rviz_interface` combines **Publish Point** with **2D Pose Estimate** for
initial calibration, publishes `map -> odom`, and sends the selected goal to
`/compute_path_to_pose`. Reset its calibration state with:

```bash
ros2 service call /recalibrate_pose std_srvs/srv/Trigger "{}"
```

`path_follower` subscribes to `/global_path` and
`/local/filtered_obstacles`, looks up `map -> base_link`, and publishes
`/cmd_vel` at 10 Hz. The Go2W adapter forwards this command directly
to the Unitree SportClient and does not itself implement a watchdog, command
multiplexer, velocity clamp, or emergency stop. Validate those deployment
safeguards before enabling motion.

For a planning-only TF test without robot odometry, use:

```bash
ros2 run r3d_planner path_test
```

`path_test` publishes a static identity `odom -> base_link`. Do not run it with
the real odometry publisher.

### V1-only commands

`pcd_to_graph`, `voxel_map_publisher`, and `global_planner` load or create
Pickle artifacts and are intentionally not part of V2. The external
`r3d_planner_launch.sh` examples depend on that Pickle workflow and cannot be
used with a clean V2 checkout. Use `pcd_analyser`, `pcd_server`, and
`pcd_path_planner` as documented above.

## Further documentation

- [Detailed installation and troubleshooting](INSTALL.md)
- [Architecture and ROS interfaces](docs/ARCHITECTURE.md)
- [Known limitations and maintenance notes](docs/KNOWN_ISSUES.md)
- [`r3d_preprocessor` reference](r3d_preprocessor/README.txt)
- [`r3d_planner` reference](r3d_planner/README.txt)
