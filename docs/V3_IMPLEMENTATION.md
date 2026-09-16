# V3 configuration implementation

## Configuration hierarchy and ownership

```text
r3d_planner/config/
├── planner_config.yaml
├── robots/
│   └── Go2W.yaml
└── r3d_planner_params.yaml    # unchanged, legacy Nav2 fragment
```

The central entry point selects `robot_config: robots/Go2W.yaml`. The selected
robot YAML owns `robot_height_cm`, `robot_narrow_radius_cm`, `robot_radius_cm`,
`robot_base_clearance_cm`, Odometry topic/odom/base frames, sensor cloud input and
command output topic. Existing centimeter geometry names and effective defaults
are retained. There is no source-code selection of Go2W.

The central YAML owns map paths, shared voxel/step settings, preprocessing,
planner cost and visualization settings, sensor-local filter thresholds,
RViz behavior and general follower tuning. Shared graph parameters have a single
definition forwarded to analysis and reconstruction. Sensor-local step detection
and offline graph steps remain separate because their coordinate systems and
existing threshold semantics differ. Controller tuning remains central but must
be checked against the selected platform's motion limits.

Required/misplaced/unknown/duplicate settings and invalid geometry, topics,
booleans or map paths fail explicitly. Launch forwarding takes precedence over
the retained standalone developer defaults; defaults never overwrite YAML.

## Startup and restart workflow

```bash
ros2 launch r3d_planner preprocessor.launch.py
ros2 launch r3d_planner planner.launch.py
```

The preprocessor launch starts the existing `r3d_preprocessor/pcd_analyser`
one-shot node. The planner launch always starts `pcd_path_planner` and uses
independent boolean conditions for `components.live_filter.enabled` and
`components.rviz_interface.enabled`. All four combinations are covered by tests.
The optional map display uses `map.launch.py`. The explicit `follower.launch.py`
is never included automatically because it can produce motion commands.

Runtime configuration resolves to live source files with the supported initial
`colcon build --symlink-install`. Each launch reads both YAML files anew. Edits
and new robot YAMLs require only restart, without rebuilding or re-sourcing.
Copied installations must set `R3D_CONFIG_DIR` once to live source config;
otherwise the resolver deliberately rejects an installed YAML snapshot.
Moving a checkout/install prefix still requires installation repair/rebuild.

To add a robot, copy the robot YAML, update dimensions/interfaces and select its
relative filename in the central file. No source change is needed if the robot
obeys the existing message, frame, sensor and controller contracts. Regenerate
the analyzed PCD after changing geometry/processing settings. Existing PCD colors
are not reclassified by merely changing the robot selection.

## Standardized Odometry integration

The planner and explicit follower consume `nav_msgs/msg/Odometry` on the
selected robot topic, initially `/lidar_odometry`. Messages describe the
configured `odom_frame -> base_frame` pose with current timestamps.
The planner owns no TF. External odometry owns `odom -> base_link`; global
localization owns `map -> odom`. Online pose computation transforms the received
odometry pose through global TF at the message timestamp.

`ComputePathToPose.use_start=true` preserves offline explicit-start planning;
`false` selects the standard Odometry start. Goal and explicit-start headers are
validated against the configured map frame. Invalid/stale/missing Odometry or
missing global TF aborts online planning. Pose loss sends zero velocity from the
explicit follower, without adding a complete command safety system.

RViz sends online requests rather than obtaining the start through a TF lookup.
`rviz_interface.publish_map_odom=false` disables its legacy calibration TF for
external global localization; goal selection then needs no initial calibration.
Legacy calibration math, narrow quaternion metadata, A*, PCD representation,
sensor-axis assumptions and packed-XYZ decoding are otherwise retained.

No `lidar_slam_ros2` replacement, fork or direct dependency is implemented here.
The planned external LiDAR-odometry frontend can connect through the standard
message/TF contract. Other sources can connect through the same contract; a
sensor-frame pose needs external base-frame conversion, not just a topic rename.

## Files created

- `r3d_planner/config/planner_config.yaml`
- `r3d_planner/config/robots/Go2W.yaml`
- `r3d_planner/launch/preprocessor.launch.py`
- `r3d_planner/launch/planner.launch.py`
- `r3d_planner/launch/map.launch.py`
- `r3d_planner/launch/follower.launch.py`
- `r3d_planner/r3d_planner/configuration.py`
- `r3d_planner/r3d_planner/launching.py`
- `r3d_planner/r3d_planner/odometry.py`
- `r3d_planner/test/test_configuration.py`
- `docs/CONFIGURATION.md`
- `docs/V3_IMPLEMENTATION.md`

## Files modified

- `r3d_planner/setup.py`: install launch and robot-config resources.
- `r3d_planner/package.xml`: declare new loader/launch and preprocessor runtime dependencies.
- `r3d_planner/r3d_planner/r3d_pcd_path.py`: configuration-backed costs/display,
  robot geometry visibility, standard Odometry start and frame validation.
- `r3d_planner/r3d_planner/r3d_local_filter.py`: configurable input and effective thresholds.
- `r3d_planner/r3d_planner/r3d_rviz_interface.py`: parameterized matching/global
  TF ownership and standard online action requests.
- `r3d_planner/r3d_planner/r3d_path_follower.py`: parameterized tuning/topics,
  standard Odometry global pose and zero command on unavailable pose.
- `r3d_preprocessor/r3d_preprocessor/r3d_pcd_publisher.py`: configurable map frame.
- `README.md`, `INSTALL.md`, `README_r3d_planner.txt`, both package `README.txt`
  files and `docs/ARCHITECTURE.md`, `docs/KNOWN_ISSUES.md`, `docs/README_AUDIT.md`,
  `docs/REFERENCE_COMPARISON.md`: current usage/ownership and historical scope.

No packages, nodes or files are moved or renamed. Existing maps, legacy Nav2
YAML, ROS interfaces and external hardware code remain unchanged.

## Validation and deployment boundary

Both packages build with system Python, `PYTHONNOUSERSITE=1` and symlink install
using temporary validation build/install/log directories. All 26 Python files
parse and both manifests parse as XML. New configuration/launch/Odometry modules
and launch files pass focused Flake8 with a 100-character limit. Existing source
lint issues remain outside this refactor.

The focused tests cover robot selection using a temporary alternate configuration,
validation failures, live source resolution, refusal of copied snapshots,
ROS numeric types, effective preprocessing/planner geometry and shared settings,
synthetic Odometry reception, translated/rotated global poses, offline/online
action start behavior and stale pose rejection. A real preprocessor launch
creates a temporary analyzed PCD. The real planner launch is restarted for all
four component combinations in the same sourced environment, with robot and
shared YAML changes between starts and no intervening build or source command.
Daemon-free CLI parameter queries verify runtime values after restart.

The final focused run passes all 20 tests in 40.07 seconds under Fast DDS in a
localhost-only isolated ROS domain. Expanded assertions query Live Filter and
RViz parameters, including disabled calibration TF. The final run does not
rebuild or re-source between configuration edits and launch restarts.
The workstation's NumPy/SciPy version warning is not repaired by this task.
Early asynchronous-query/discovery harness failures are recorded in known issues;
the corrected real-launch harness uses explicit discovery time and fresh observers.

No physical robot, hardware adapter or motion follower is started during testing.
The original Go2W stack is tested, but V3 needs deployment regression and
independent motion-safety checks before enabling hardware motion. Changes are
local to V3 and are not committed or pushed by this implementation task.
