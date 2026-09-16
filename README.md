# R3D-Planner

## Overview and goals

R3D-Planner is a ROS 2 Humble stack for navigation in voxelized 3D PCD maps.
The preprocessor classifies clearance and traversability; the planner reconstructs
a weighted 3D graph and computes A* paths through the standard
`nav2_msgs/action/ComputePathToPose` action.

The complete original navigation stack, including sensor integration and TF,
has run successfully on a Unitree Go2W. V3 introduces centralized runtime
configuration and a source-independent Odometry input. This refactor has
non-motion workstation tests; it still needs deployment regression testing on
the Go2W. Other ROS distributions are not supported.

| Package | Role | Executables |
|---|---|---|
| `r3d_preprocessor` | PCD analysis and visualization | `pcd_analyser`, `pcd_server` |
| `r3d_planner` | Planning, perception, RViz input and control | `pcd_path_planner`, `local_filter`, `rviz_interface`, `path_follower`, `path_test` |

The pipeline is PCD-only. Pickle executables and external Pickle helper scripts
from V1 are not available here.

## Installation

Use Ubuntu 22.04, ROS 2 Humble and its Python 3.10 environment.
Required libraries include Open3D, NetworkX, NumPy, SciPy and PyYAML; ROS inputs
use standard geometry, navigation and sensor messages, Nav2 actions and TF2.
Sensor drivers, odometry, global localization and the robot command adapter
remain external. No specific SLAM package is a dependency.

Install the apt dependencies listed in [INSTALL.md](INSTALL.md), then:

```bash
mkdir -p <path-to-workspace>/src
cd <path-to-workspace>/src
git clone git@github.com:RoboProjekt/R3D-Planner.git
cd R3D-Planner
git checkout V3
cd <path-to-workspace>
source /opt/ros/humble/setup.bash
sudo rosdep init  # only if not initialized on this machine
rosdep update
rosdep install --from-paths src --ignore-src -r -y --skip-keys="numpy scipy"
colcon build --symlink-install
source install/setup.bash
```

Replace angle-bracket placeholders before running commands. Source ROS and the
workspace once in each new terminal. `--symlink-install` makes source
configuration available at runtime, including newly added robot YAMLs.
Editing YAML thereafter requires only stopping and restarting the affected launch,
not rebuilding or sourcing again. Copied installations must set
`R3D_CONFIG_DIR` once to the live source configuration directory; the loader
rejects stale copied YAML rather than using it silently.

## Configuration

The stable entry point is `r3d_planner/config/planner_config.yaml`:

```text
r3d_planner/config/
├── planner_config.yaml
├── robots/
│   └── Go2W.yaml
└── r3d_planner_params.yaml   # legacy Nav2 fragment, not loaded
```

`robot_config: robots/Go2W.yaml` selects the robot. Robot geometry, odometry
topic/frames, sensor input and command topic belong exclusively to that robot
YAML. General settings belong to the central file; shared graph settings are
forwarded to both analysis and planning. Unknown, duplicate or missing keys and
invalid values fail at startup.

| Central section | Ownership |
|---|---|
| `maps` | Input PCD and analyzed planning PCD; paths relative to the config directory |
| `shared` | Voxel size and minimum/maximum graph step heights |
| `preprocessing` | Density, voxel hit filtering, floor filling and clustering |
| `planner` | Map frame, odometry age limit, graph costs and path visualization |
| `components` | Independent Live Filter and RViz-interface launch switches |
| `live_filter` | Sensor-coordinate perception thresholds |
| `rviz_interface` | XY matching radius and optional calibration TF ownership |
| `path_follower` | Lookahead, speed limits and controller thresholds; explicit motion launch only |

See [the full parameter reference](docs/CONFIGURATION.md) for names, units,
validation, default values and adding a robot.

## Using the preprocessor: select and analyze a map

Edit `maps.pcd_path` in `planner_config.yaml`. The included input is
`r3d_preprocessor/maps/voxel_05_minhits_7.pcd`. Set `maps.map_name` to the
corresponding `*_analysed.pcd`. Other RoboLab, HomeLab and stair maps are not
included; provide your own PCD and change these two paths.

```bash
ros2 launch r3d_planner preprocessor.launch.py
```

This starts the existing one-shot `r3d_preprocessor/pcd_analyser` node.
It voxelizes the input, filters weak voxels, checks robot clearance, optionally
fills floors, and writes `<input-name>_analysed.pcd` beside the input.
An existing output with that name is overwritten. It publishes no TF or topics.
Green marks floor, cyan narrow clearance, yellow stair access and magenta
obstacles.

| Setting | Location | Meaning |
|---|---|---|
| `pcd_path` | `maps` | Source PCD to analyze |
| `voxel_size_cm` | `shared` | Voxel edge length, cm |
| `min_step_height_cm`, `max_step_height_cm` | `shared` | Flat boundary and largest step, cm |
| `robot_height_cm` | robot `geometry` | Collision-cylinder height, cm |
| `robot_narrow_radius_cm` | robot `geometry` | Tight clearance radius, cm |
| `robot_radius_cm` | robot `geometry` | Normal safety radius, cm |
| `robot_base_clearance_cm` | robot `geometry` | Collision check starts above the floor, cm |
| `min_points_per_sqm`, `min_points_per_voxel` | `preprocessing` | Floor-fill density and occupied-voxel hit threshold |
| `floor_height_tolerance`, `ground_fill` | `preprocessing` | Planarity tolerance in m and filling switch |

Changing robot dimensions or processing settings requires analyzing the map again,
but not rebuilding the workspace. A PCD does not carry configuration metadata:
keep its generating YAML settings with the artifact. Selecting a robot does not
reclassify an existing PCD automatically.

For an optional map display:

```bash
ros2 launch r3d_planner map.launch.py
rviz2
```

In RViz use fixed frame `map`, PointCloud2 topic `/map_pointcloud`,
Transient Local durability and RGB8 coloring. The map launch loads the analyzed
PCD selected in the central configuration.

## Using the planner: offline and online

```bash
ros2 launch r3d_planner planner.launch.py
```

The launch always starts `pcd_path_planner` and independently starts the
Live Filter and RViz interface according to:

```yaml
components:
  live_filter:
    enabled: true
  rviz_interface:
    enabled: true
```

All four true/false combinations are supported. These switches control node
startup, not internal disabled logic. The RViz interface is a ROS node, not an
RViz GUI plugin; start `rviz2` separately. The Path Follower and hardware
drivers are never included automatically.

### Offline planning

Set both component flags to `false` for a minimal planner. Explicit start
and goal poses must use `planner.map_frame` (default `map`). No odometry
or TF is required for this request:

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

Coordinates are examples; start and goal snap to the nearest traversable node.
The action returns a Path and publishes `/global_path`; `/planned_path`
provides a LINE_STRIP Marker. `planner_id` is accepted but not evaluated.

### Online planning

The robot YAML defines the standard input contract:

```yaml
odometry:
  topic: /lidar_odometry
  odom_frame: odom
  base_frame: base_link
```

The external source publishes `nav_msgs/msg/Odometry` with
`header.frame_id=odom`, `child_frame_id=base_link`, a valid pose and current
timestamp. It owns `odom -> base_link`. A separate global localization
source owns `map -> odom`. No odometry node should publish `map -> base_link`.
The planner does not broadcast any TF and does not depend on
`lidar_slam_ros2`, KISS-ICP, FAST-LIO or a particular estimator.

Use `use_start: false` to plan from current odometry:

```bash
ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose "{
  use_start: false,
  goal: {
    header: {frame_id: 'map'},
    pose: {position: {x: 5.0, y: 0.0, z: 2.5}, orientation: {w: 1.0}}
  }
}"
```

The planner transforms the odometry pose using `map -> odom` at its timestamp.
Missing TF, mismatched frames, invalid or stale odometry aborts the request.
Only the configured Odometry topic supplies the online pose; a TF-only source
must also publish Odometry. `path_test` supplies test TF only and is not an
online odometry simulator.

Enable RViz integration for point/pose goal pairs. With
`rviz_interface.publish_map_odom: true`, first combine Publish Point and
2D Pose Estimate for the existing calibration workflow. With an external global
localizer, set it to `false`; no calibration TF is sent and goals can be
selected directly through Publish Point and 2D Goal Pose. Keep exactly one
`map -> odom` publisher. The legacy calibration assumes an identity
odometric pose; do not use it as a replacement for global localization.

```bash
ros2 service call /recalibrate_pose std_srvs/srv/Trigger "{}"
```

For approved motion only:

```bash
ros2 launch r3d_planner follower.launch.py
```

This starts the existing planar follower with central controller settings and
the selected robot's Odometry and command topic. It publishes zero velocity
when pose input is unavailable or stale. It is not a complete safety controller:
path Z, cliff walls and stair detections do not directly control motion.
Validate external watchdogs, arbitration, emergency stop and cliff handling
before enabling the Go2W adapter, which may change posture on startup.

## Further documentation

- [Installation and verification](INSTALL.md)
- [Configuration reference](docs/CONFIGURATION.md)
- [Architecture and interfaces](docs/ARCHITECTURE.md)
- [Known limitations](docs/KNOWN_ISSUES.md)
- [Preprocessor reference](r3d_preprocessor/README.txt)
- [Planner reference](r3d_planner/README.txt)
- [Historical V2 deployment comparison](docs/REFERENCE_COMPARISON.md)
