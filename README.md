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
| `r3d_interfaces` | Generated PathWithMetadata wire contract | none |
| `r3d_preprocessor` | PCD analysis and visualization | `pcd_analyser`, `pcd_server` |
| `r3d_planner` | Planning, perception, RViz input and control | `pcd_path_planner`, `local_filter`, `rviz_interface`, `path_follower`, `path_test` |

The pipeline is PCD-only. Pickle executables and external Pickle helper scripts
from V1 are not available here.

## Development metadata

All three packages use the provisional development version `0.0.1`. The two
executable packages use `ament_python`; `r3d_interfaces` uses `ament_cmake`/rosidl. `r3d_preprocessor` performs offline voxel-based PCD
clearance/traversability analysis; `r3d_planner` provides graph-based A* planning
and the existing ROS 2 navigation components listed above.

Repository: [RoboProjekt/R3D-Planner](https://github.com/RoboProjekt/R3D-Planner).
Bug tracker: [GitHub issues](https://github.com/RoboProjekt/R3D-Planner/issues).
Author of the own software: Bastian Aumer; existing maintainer contact:
`bauya <baau1001@stud.hs-kl.de>`. Authorized own software uses Apache-2.0;
existing third-party notices retain their original attribution and conditions.

V4 is currently developed locally. The project has no official ROS Index
registration or Bloom/Buildfarm release; `0.0.1` is not a released ROS version.
V4 bundles no PCD maps and requires user-provided inputs. The public V3 source
remains available; the V4 installation instructions below require the existing
local V4 checkout.

## Installation

Use Ubuntu 22.04, ROS 2 Humble and its Python 3.10 environment.
Required libraries include Open3D, NetworkX, NumPy, SciPy and PyYAML; ROS inputs
use standard geometry, navigation and sensor messages, Nav2 actions and TF2.
Sensor drivers, odometry, global localization and the robot command adapter
remain external. No specific SLAM package is a dependency.

For the local V4 checkout, follow [INSTALL.md](INSTALL.md) to place all three packages
below a workspace's `src` directory. The public V3 branch does not contain the
AP03 manifest corrections. Use the native Humble system interpreter, with no
Conda or unrelated workspace overlays:

```bash
cd <path-to-workspace>
source /opt/ros/humble/setup.bash
export PYTHONNOUSERSITE=1
sudo rosdep init  # only if not initialized on this machine
rosdep update --rosdistro humble
rosdep install --from-paths src/R3D-Planner \
  --ignore-src --rosdistro humble --os=ubuntu:jammy -y
rosdep check --from-paths src/R3D-Planner \
  --ignore-src --rosdistro humble --os=ubuntu:jammy
colcon build --packages-up-to r3d_planner
source install/setup.bash
```

AP03 verified the original external keys; the current three-package set also
passes actual rosdep installation and rosdep check
(exit 0) in two fresh isolated ROS 2 Humble / Ubuntu 22.04.5 containers using
system Python 3.10.12. Apt NumPy 1.21.5, SciPy 1.8.0, Open3D 0.14.1 and NetworkX
2.4 worked without the former NumPy/SciPy compatibility warning. Two fresh copy
workspaces each passed 225 tests (0 failures, 0 skips), including active lint and
copyright checks; a separate container without the source tree passed 169
installation/output/interface cases. The audit host was unchanged and still lacks apt
Open3D/NetworkX. These results establish the tested Humble installation scope;
CI, newer distributions, hardware deployment and official release remain separate.

Replace angle-bracket placeholders before running commands. Source ROS and the
workspace once in each new terminal. Optional developer `--symlink-install` makes source
configuration available at runtime, including newly added robot YAMLs.
Editing YAML thereafter requires only stopping and restarting the affected launch,
not rebuilding or sourcing again. Copy installations use the regular installed
package-share YAML and robot profiles. Set `R3D_CONFIG_DIR` to a user-owned
configuration directory for editable overrides; no source checkout is required.
Rebuild a copy installation to refresh its installed templates.

## M01 interface migration

Build and install `r3d_interfaces`, `r3d_preprocessor` and `r3d_planner` together.
`/global_path` remains `nav_msgs/Path` and the action result contains that same
geometric path, with normalized XY tangent orientations. Narrow flags are no
longer encoded in quaternion fields. `/global_path_metadata` carries
`r3d_interfaces/msg/PathWithMetadata`: the complete Path and exactly one boolean
per pose, atomically. The follower consumes this message with reliable,
transient-local, depth-1 QoS; late joining receives both path and flags.

Upgrade planner and follower together. External consumers that decoded
`orientation.z > 0.5` must use `narrow[index]` on the enriched path instead.
Inconsistent metadata clears the follower path; there is no legacy decoder.
M02 obstacle timeout/TF monitoring remains deferred: disabling the optional local
filter does not silently enable or disable a watchdog. See the proposal in the
[central protocol](docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md#182-m02-vorschlag--optionaler-filter-timeout-tf-und-stopzustände).

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
| `preprocessing` | Density, voxel hit filtering, floor filling, clustering and optional `output_dir` |
| `planner` | Map frame, odometry age limit, graph costs and path visualization |
| `components` | Independent Live Filter and RViz-interface launch switches |
| `live_filter` | Sensor-coordinate perception thresholds |
| `rviz_interface` | XY matching radius and optional calibration TF ownership |
| `path_follower` | Lookahead, speed limits and controller thresholds; explicit motion launch only |

See [the full parameter reference](docs/CONFIGURATION.md) for names, units,
validation, default values and adding a robot.

## Using the preprocessor: select and analyze a map

V4 bundles no PCD example maps. Provide a suitable PCD that you are entitled
to use, then set `maps.pcd_path` in your `planner_config.yaml`. Set
`maps.map_name` to the corresponding `<input-name>_analysed.pcd` before planning.
Both shipped values are empty; launch fails clearly until the selected input is
configured and exists. Relative paths resolve against the YAML directory;
absolute paths and `~` are accepted. No map is downloaded or selected as a fallback.
Installation does not require map data. See the [configuration reference](docs/CONFIGURATION.md)
for using an external configuration directory with a copied installation.

```bash
ros2 launch r3d_planner preprocessor.launch.py
```

This starts the existing one-shot `r3d_preprocessor/pcd_analyser` node.
It voxelizes the input, filters weak voxels, checks robot clearance, optionally
fills floors, and writes `<input-name>_analysed.pcd` in
`preprocessing.output_dir`. An empty value uses the user data directory
(`$XDG_DATA_HOME/r3d_preprocessor`, otherwise `~/.local/share/r3d_preprocessor`).
Inputs may be read-only. Existing outputs are rejected, including symlinks;
choose a new output directory for another analysis. It publishes no TF or topics.
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

## Action result and cancellation scope

ComputePathToPose succeeds with the geometric Path and measured planning_time,
aborts with an empty result on invalid frame/position/quaternion, missing/stale
pose or TF, and unreachable/empty paths. The existing A* checks accepted
cancellation cooperatively; active requests can reach CANCELED without publishing
a new path. Cancel or failed replanning does not revoke a previously published
path or command a robot stop. The four-worker executor permits cancel service
processing during planning, but makes no real-time or unlimited-concurrency promise.
Planner IDs remain accepted without plugin selection for compatibility. Humble's
result has no error_code field and its feedback payload is empty. This is an
action contract, not a full Nav2 planner plugin/lifecycle integration.

## Namespace composition

All four launches accept an optional namespace argument, for example:

```bash
ros2 launch r3d_planner planner.launch.py namespace:=robot_a
```

Internal Path, metadata, marker, map, RViz, action and service names compose
under that namespace. The empty default preserves root names. Explicit absolute
robot-profile topics remain global; use relative `odometry`, `cloud` and
`cmd_vel` names when those robot interfaces should inherit the namespace.
Direct executables support normal ROS remapping arguments. TF topics/frame IDs
are not automatically prefixed: configure robot-specific frames and a single
owner of each transform. Launching the follower remains a separate motion step.
RViz selections must use map_frame and finite valid poses; action lookup is
bounded by rviz_interface.action_server_timeout_sec (default 1 s).

## Maintenance

See [CONTRIBUTING.md](CONTRIBUTING.md) for focused synthetic reproductions/tests
and [MAINTENANCE.md](MAINTENANCE.md) for support, version/API/ABI and release gates.
Each package has a Forthcoming CHANGELOG.rst. None declares a released version.
