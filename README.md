# R3D-Planner

## Overview and goals

R3D-Planner is a ROS 2 Humble navigation stack for voxelized 3D point clouds.
It converts PCD maps into a traversability representation, builds a 3D graph,
and computes fully three-dimensional paths with A*. The stack publishes paths
through `nav2_msgs/action/ComputePathToPose` and can forward them to a simple
local controller.

The complete system was developed and tested on a Unitree Go2W, including the
Hesai point-cloud input, TF tree, RViz workflow, local obstacle filter, and
`/cmd_vel` interface. Other ROS distributions are not supported.

V1 supports two map formats:

```text
PCD map -> pcd_to_graph -> NetworkX Pickle graph -> global_planner
PCD map -> pcd_analyser -> color-coded PCD       -> pcd_path_planner
```

Both planners expose `/compute_path_to_pose`, `/global_path`, and
`/planned_path`. Run only one planner at a time.

The workspace contains two `ament_python` packages:

| Package | Purpose | Executables |
|---|---|---|
| `r3d_preprocessor` | Analyze PCD maps and publish PCD or Pickle map data | `pcd_to_graph`, `pcd_analyser`, `voxel_map_publisher`, `pcd_server` |
| `r3d_planner` | Global planning, local filtering, RViz input, path following, and test TF | `global_planner`, `pcd_path_planner`, `local_filter`, `rviz_interface`, `path_follower`, `path_test` |

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

Open3D handles PCD data, NetworkX stores the navigation graph, SciPy supplies
the nearest-node KDTree, and NumPy is used for point-cloud and geometry
operations. Pickle support is part of Python.

### Workspace, rosdep, and build

Replace every `<path-to-workspace>` placeholder below with the absolute path of
your ROS 2 workspace before running a command.

```bash
mkdir -p <path-to-workspace>/src
cd <path-to-workspace>/src
git clone git@github.com:RoboProjekt/R3D-Planner.git
cd R3D-Planner
git checkout V1
cd <path-to-workspace>
```

The package manifests contain the unresolved rosdep keys `pickle`, `numpy`,
and, depending on the rosdep database, `scipy`. Install the packages above and
run rosdep with these exclusions:

```bash
sudo rosdep init  # only on a new ROS installation
rosdep update
cd <path-to-workspace>
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="pickle numpy scipy"
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

The preprocessor loads a PCD map, voxelizes it, fills eligible floor gaps, checks
robot clearance, and classifies traversable, narrow, stair, and obstacle
voxels. `pcd_to_graph` writes a serialized NetworkX graph. `pcd_analyser`
performs the same map analysis and writes a color-coded `*_analysed.pcd` for the
PCD planner and RViz.

### Preprocessor parameters

Both analysis executables declare the same parameters:

| Parameter | Default | Unit | Description |
|---|---:|---|---|
| `pcd_path` | `environment.pcd` | path | Input PCD file; `~` is expanded |
| `voxel_size_cm` | `5.0` | cm | Voxel edge length |
| `max_step_height_cm` | `25.0` | cm | Largest height difference connected as a step |
| `min_step_height_cm` | `5.0` | cm | Boundary between flat and step connections |
| `min_points_per_sqm` | `10.0` | points/m² | Density threshold used by floor filling |
| `min_points_per_voxel` | `3` | points | Minimum hits retained in an occupied voxel |
| `floor_height_tolerance` | `0.02` | m | Z tolerance used to group floor samples |
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

### Generate a Pickle graph

This full invocation shows every configurable analysis parameter:

```bash
ros2 run r3d_preprocessor pcd_to_graph --ros-args \
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

`pcd_to_graph` writes `nav_graph_*.pkl` beside the input map. The filename
encodes the main preprocessing values. Pickle files can execute code while
loading; use only graphs generated by a trusted environment.

### Tested map configurations

The following commands are retained as deployment presets. Only
`voxel_05_minhits_7.pcd` is included in this repository. Copy the other maps to
the stated paths or replace `pcd_path` with their actual location.

RoboLab map:

```bash
ros2 run r3d_preprocessor pcd_to_graph --ros-args -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/RoboLab_map.pcd -p voxel_size_cm:=5.0 -p max_step_height_cm:=20.0 -p min_points_per_sqm:=10.0 -p min_points_per_voxel:=1 -p floor_height_tolerance:=0.03 -p ground_fill:=true -p robot_base_clearance_cm:=10.0 -p robot_narrow_radius_cm:=30.0
```

HomeLab map:

```bash
ros2 run r3d_preprocessor pcd_to_graph --ros-args -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/HomeLab_map1_lidar.pcd -p voxel_size_cm:=5.0 -p max_step_height_cm:=20.0 -p min_points_per_sqm:=10.0 -p min_points_per_voxel:=1 -p floor_height_tolerance:=0.03 -p ground_fill:=true -p robot_base_clearance_cm:=10.0 -p robot_narrow_radius_cm:=30.0
```

Included voxel map with the reduced density threshold:

```bash
ros2 run r3d_preprocessor pcd_to_graph --ros-args -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7.pcd -p voxel_size_cm:=5.0 -p max_step_height_cm:=20.0 -p min_points_per_sqm:=1.0 -p min_points_per_voxel:=1 -p floor_height_tolerance:=0.05 -p ground_fill:=false -p robot_base_clearance_cm:=10.0 -p robot_narrow_radius_cm:=30.0
```

Unfiltered stair scan:

```bash
ros2 run r3d_preprocessor pcd_to_graph --ros-args -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/Stair_unfiltered.pcd -p voxel_size_cm:=5.0 -p max_step_height_cm:=20.0 -p min_points_per_sqm:=1.0 -p min_points_per_voxel:=7 -p floor_height_tolerance:=0.05 -p ground_fill:=false -p robot_base_clearance_cm:=10.0 -p robot_narrow_radius_cm:=30.0
```

### Generate and inspect a color-coded PCD

Replace `pcd_to_graph` with `pcd_analyser` and keep the same analysis
parameters:

```bash
ros2 run r3d_preprocessor pcd_analyser --ros-args \
  -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7.pcd \
  -p voxel_size_cm:=5.0 \
  -p min_step_height_cm:=5.0 \
  -p max_step_height_cm:=25.0
```

The output is `voxel_05_minhits_7_analysed.pcd`. Publish any PCD on
`/map_pointcloud` with:

```bash
ros2 run r3d_preprocessor pcd_server --ros-args \
  -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/HomeLab_test1_LIO.pcd
```

`pcd_server` has one parameter:

| Parameter | Default | Description |
|---|---|---|
| `pcd_path` | `environment.pcd` | PCD file published in frame `map` |

In RViz, add a PointCloud2 display for `/map_pointcloud`, set durability to
`Transient Local`, and use `RGB8` to display the traversability colors.

## Using `r3d_planner`

### Offline planning with a prepared map

Publish a Pickle graph for RViz:

```bash
ros2 run r3d_preprocessor voxel_map_publisher --ros-args \
  -p graph_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/nav_graph_step25_voxel5_dens10_minpts1_tol0.030_fillFalse_clear10_narrow30_rad40.pkl
```

| Parameter | Default | Description |
|---|---|---|
| `graph_path` | empty | Trusted Pickle graph published on `/r3d_global_voxel_map` |

Start the Pickle planner with an absolute path or a file below `map_dir`:

```bash
ros2 run r3d_planner global_planner --ros-args \
  -p map_name:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/nav_graph_step20_voxel5.pkl
```

| Parameter | Default | Description |
|---|---|---|
| `map_dir` | `<share/r3d_preprocessor>/maps`, fallback `/tmp` | Directory used for relative graph names |
| `map_name` | `nav_graph.pkl` | Pickle graph filename or absolute path |

The default package map directory is not installed. Pass an absolute
`map_name` unless the graph is provided separately.

Alternatively, start the PCD planner:

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

Send a 3D start and goal directly to either planner:

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
| `planner_id` | Accepted by the action interface but not evaluated by either planner |

The planner returns the path in the action result, publishes
`nav_msgs/msg/Path` on `/global_path`, and publishes a Marker on
`/planned_path`.

### Online operation on the Go2W

The online stack requires the tested Go2W components that publish the Hesai
cloud on `/hesai_ros_driver/hesai/lidar_points`, provide
`odom -> base_link`, and consume `/cmd_vel`.

Start exactly one global planner, then run:

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
`/cmd_vel` at 10 Hz. Keep the tested Go2W emergency-stop, watchdog, and command
multiplexer active whenever this node is running.

For a planning-only TF test without robot odometry, use:

```bash
ros2 run r3d_planner path_test
```

`path_test` publishes a static identity `odom -> base_link`. Do not run it with
the real odometry publisher.

### External deployment wrapper

The deployed system has also been started with these commands:

```bash
./r3d_planner_launch.sh HomeLab_test2_LIO.pcd nav_graph_step25_voxel5_dens10_minpts3_tol0.020.pkl
./r3d_planner_launch.sh HomeLab_map1_lidar.pcd nav_graph_step20_voxel10_dens8_minpts2_tol0.050.pkl
./r3d_planner_launch.sh voxel_05_minhits_7.pcd nav_graph_step20_voxel5_dens10_minpts1_tol0.030.pkl
```

`r3d_planner_launch.sh` is an external deployment wrapper and is not included
in this repository. Use the explicit `ros2 run` commands above when working
from a clean checkout.

## Further documentation

- [Detailed installation and troubleshooting](INSTALL.md)
- [Architecture and ROS interfaces](docs/ARCHITECTURE.md)
- [Known limitations and maintenance notes](docs/KNOWN_ISSUES.md)
- [`r3d_preprocessor` reference](r3d_preprocessor/README.txt)
- [`r3d_planner` reference](r3d_planner/README.txt)
