# R3D Navigation Stack Architecture

## System boundary

R3D-Planner separates map processing, global planning, local point-cloud
filtering, RViz input, and path following into ROS 2 nodes. The complete stack
has been integrated and tested on a Unitree Go2W. V3 adds runtime configuration
and a standard Odometry contract; its refactor requires hardware regression testing. The Go2W runtime also
supplies:

- 3D LiDAR driver and sensor calibration;
- an implementation-independent `nav_msgs/msg/Odometry` source and `odom -> base_link`;
- separate global localization providing `map -> odom`, or legacy RViz calibration;
- robot hardware interface consuming `/cmd_vel`;
- optional Nav2 bringup and costmap/controller plugins;
- deployment-specific process supervision and motion-safety controls, which
  are not implemented in this repository.

## Packages and dependency flow

```text
r3d_preprocessor                         r3d_planner
----------------                         -----------
raw PCD -> color-coded PCD --------------+-> global A* planner
                                                   |       |
LiDAR (external) -> local filter -----------------+-> Nav2 action + Path
                                                           |
                                                           +-> simple path follower
                                                          |
                                                          +-> /cmd_vel
```

The package dependencies flow from `r3d_planner` to `r3d_preprocessor` and
`r3d_interfaces`. The latter generates PathWithMetadata, containing the complete
Path and index-aligned narrow flags used by the follower.
Both central launch entry points belong to the existing planner package.
The preprocessor does not depend on the planner or any odometry implementation.

## Configuration flow

```text
r3d_planner/config/planner_config.yaml -- selects --> robots/Go2W.yaml
                       |                         geometry + robot interfaces
                       +--------- loader validates and resolves --------+
                                                 |
                  +------------------------------+----------------------+
                  |                              |                      |
           preprocessor.launch.py         planner.launch.py       explicit follower launch
                  |                              |
             pcd_analyser                  pcd_path_planner
                                                 |
                                    +------------+------------+
                                    |                         |
                               local_filter             rviz_interface
                               (optional)               (optional)
```

Robot settings have one owner in the robot YAML; general settings have one owner
in the central YAML. Shared voxel/step settings are forwarded to analysis and
reconstruction, not duplicated per node. The two component booleans are
independent launch conditions. The map and follower launches are separate.
The follower is not automatically started because it can command motion.

The resolver reads YAML on each launch. An explicit user-owned `R3D_CONFIG_DIR`
takes precedence; otherwise direct source/symlink modules use source YAML and
copy installations resolve regular package-share YAML through ament_index_python.
The override needs only central YAML and robot profiles, no source checkout.
Restart applies user-YAML changes; copy-template changes require rebuilding.
Paths are relative to the selected central config directory.
See [CONFIGURATION.md](CONFIGURATION.md) for schema, units and validation.

### User data and included configuration

V4 contains no bundled PCD maps. The user supplies the analysis input and
classified planning file through `maps.pcd_path` and `maps.map_name`.
The shipped values are unset; installation is independent of these files.
The two older example maps remain part of historical Git versions, not the
active V4 tree. General PCD analysis, classification, loading and planning remain.

| File | Content |
|---|---|
| `r3d_planner/config/planner_config.yaml` | Central runtime entry point |
| `r3d_planner/config/robots/Go2W.yaml` | Robot geometry and interfaces |
| `r3d_planner/config/r3d_planner_params.yaml` | Incomplete Nav2 costmap/MPPI configuration fragment |
| `r3d_planner/points.txt` | Site-specific action CLI example and example waypoints |

Each package also contains the standard Ament Python resource file and three
template tests for copyright, Flake8, and PEP257. There is no map metadata file,
or standalone map metadata file. The generated r3d_interfaces package supplies PathWithMetadata. Four planner-package launch entry points are installed. The shared `cloud.py`
decoder honors PointCloud2 XYZ fields, point/row strides and endian order for
both local filter and follower; it preserves input storage and excludes NaN/Inf.
Filter geometry and output headers remain in the incoming sensor frame. The
implemented r3d_interfaces package generates the atomic PathWithMetadata contract.

## Offline map processing

### Processing stages

`pcd_analyser` performs these stages:

1. Load a PCD with Open3D.
2. Optionally supplement floor samples from point density in XY cells.
3. Voxelize using the configured voxel size.
4. Discard voxels below `min_points_per_voxel`.
5. Find surface candidates and apply a cylindrical clearance test using robot
   radius, height, and base clearance.
6. Classify fully clear voxels as `floor`, voxels clear only with the smaller
   radius as `narrow`, and the remainder as obstacles.
7. Optionally fill small gaps in near-planar surfaces.
8. Classify height differences between eight neighboring XY columns as flat or
   step connections.

Input coordinates are used without an external transform. The input map must
already use the intended map coordinate system.

### Color-coded PCD pipeline

```text
map.pcd
  -> pcd_analyser
  -> map_analysed.pcd
     magenta=obstacle, green=floor, cyan=narrow, yellow=stair access
  -> pcd_path_planner and/or pcd_server
```

`pcd_path_planner` reconstructs a NetworkX graph from points and RGB values at
startup. It skips magenta points. Discrete node keys are computed by dividing
coordinates by `voxel_size_cm` and rounding. Voxel size and step-height values
are forwarded from the shared YAML section and must match the generating settings of the artifact.

## Global planning

The `pcd_path_planner` executable starts node `global_graph_planner` and serves
the `compute_path_to_pose` action:

1. Resolve an explicit map-frame start when `use_start=true`, otherwise transform
   current standard Odometry through `map -> odom` at its timestamp.
2. Use a SciPy KDTree to map action start and goal positions to nearest graph
   nodes.
3. Run A* on the weighted NetworkX graph.
4. Publish `nav_msgs/msg/Path` on `/global_path` and return it in the action
   result.
5. Publish a `visualization_msgs/msg/Marker` on `/planned_path`.

The planner publishes a `LINE_STRIP`. Goal and explicit-start headers must
match the configured map frame. Other request frames are rejected. Online
requests fail for unavailable global TF, invalid/mismatched Odometry or timestamps
outside `odometry_timeout_sec`. Offline explicit-start planning needs no TF
or Odometry. The planner subscribes with SensorDataQoS and broadcasts no TF.
Its Odometry topic and odom/base frames come from the robot YAML; no particular
SLAM package is a dependency or is launched by this workspace.

Path orientations are normalized XY tangent headings. Narrow metadata is no
longer encoded in a geometric field. `/global_path_metadata` transports the same
complete Path plus one boolean per pose as `r3d_interfaces/msg/PathWithMetadata`.
The follower validates this atomic payload, clears invalid metadata, and retains
narrow speed/steering behavior. Upgrade the interface, planner and follower
together; external legacy orientation-flag decoders must migrate.

## Local perception

`obstacle_cliff_filter` assumes X forward, Y lateral, and Z upward:

```text
/hesai_ros_driver/hesai/lidar_points
        |
        +-> legacy XY radial gate (> min_reliable_distance)
        |      +-> step ROI              -> /stair_detect
        |      +-> far obstacle heights  --+
        |      +-> missing ground        -> /local/cliff_virtual_wall
        +-> near returns (<= radius)       |
               +-> obstacle heights -----+-> /local/filtered_obstacles
                    (retain_near_obstacles=true)
```

Output clouds retain the incoming header and frame; no TF transform is applied.
Thresholds are ROS parameters forwarded from the central live_filter section;
the cloud topic comes from the robot YAML. When a step is
detected, low points in its ROI are removed from the obstacle cloud. Fewer than
30 floor points between X=0.7 and 1.2 m causes a virtual wall at X=0.7 m.

## RViz interaction and TF

```text
/clicked_point + /initialpose -> XY match within 0.8 m -> static map -> odom
/clicked_point + /goal_pose   -> XY match within 0.8 m
                              -> request use_start=false
                              -> /compute_path_to_pose action request
```

The first 3D point supplies Z, while the nearby initial pose supplies
orientation. After calibration, the node publishes static `map -> odom`.
Subsequent point/goal pairs submit goals with `use_start=false`; the planner
resolves the current start from Odometry. Set `publish_map_odom=false` when an
external global localizer owns the transform; initial calibration is then not
required and no RViz calibration TF is published.

`/recalibrate_pose` (`std_srvs/srv/Trigger`) only resets internal calibration
state. For tests, `path_test` can publish static identity `odom -> base_link`.

Intended TF tree:

```text
map
 └── odom            rviz_interface (StaticTransformBroadcaster)
      └── base_link  external odometry, or path_test for tests only
           └── hesai_lidar_link  external static transform
```

The Go2W startup publishes `base_link -> hesai_lidar_link` using
translation `(0.1384, 0, 0.1284)` and positional Euler arguments
`(1.5708, 0, 0)`. It also publishes identity `body -> base_link`. Confirm the
Euler convention of the installed Humble `static_transform_publisher` and the
resulting axes with `tf2_echo`; `local_filter` processes the sensor-frame
coordinates directly rather than transforming them into `base_link`.

The tested Go2W integration uses one publisher for `map -> odom`, supplies a
time-correct `odom -> base_link`, and matches the assumed LiDAR orientation and
`map` coordinates. Recheck these constraints after changing localization,
odometry, or the sensor installation.

## Path following

`r3d_path_follower` is a simple 2D lookahead controller:

1. Receive atomic `/global_path_metadata` (Path plus narrow flags).
2. Check the configured obstacle topic for points 0.1–0.6 m forward and ±0.3 m
   laterally. With M02 enabled, validate freshness/geometry and transform to the
   base frame at measurement time before this existing ROI test.
3. Transform the configured Odometry base pose into map and use XY/yaw.
4. Select a path point at least 0.5 m ahead.
5. Reduce speed and turning in narrow areas; otherwise command at most 0.35 m/s
   and 0.6 rad/s.
6. Publish `geometry_msgs/msg/Twist` to `/cmd_vel` every 0.1 s.

The controller does not directly process path Z, `/stair_detect`, or the cliff
wall. It completes a path at 0.2 m XY distance from the goal. Values are
loaded from the central path_follower section. Missing or stale pose input
produces a zero Twist, but external command supervision remains necessary.

## Node and executable mapping

| Package/executable | Node name | Behavior |
|---|---|---|
| `r3d_preprocessor/pcd_analyser` | `pcd_to_graph_node` | One-shot PCD analysis; writes `_analysed.pcd` |
| `r3d_preprocessor/pcd_server` | `pcd_publisher` | Publishes one transient-local PCD and remains active |
| `r3d_planner/pcd_path_planner` | `global_graph_planner` | PCD-based action server |
| `r3d_planner/local_filter` | `obstacle_cliff_filter` | LiDAR filter |
| `r3d_planner/path_follower` | `r3d_path_follower` | Path controller and `/cmd_vel` publisher |
| `r3d_planner/rviz_interface` | `r3d_rviz_interface` | RViz input, TF, service, and action client |
| `r3d_planner/path_test` | `r3d_path_test` | Static test TF `odom -> base_link` |

`r3d_pcd_voxel_publisher.py` is present but not installed as a console script.

## Topics

| Topic | Type | Publisher | Subscriber | QoS/purpose |
|---|---|---|---|---|
| `/lidar_odometry` (robot-configurable) | `nav_msgs/msg/Odometry` | external source | planner, follower | SensorDataQoS; robot odom/base frames |
| `/map_pointcloud` | `sensor_msgs/msg/PointCloud2` | `pcd_server` | external/RViz | depth 1, transient-local; configured map frame (default `map`) |
| `/planned_path` | `visualization_msgs/msg/Marker` | `pcd_path_planner` | external/RViz | depth 10 |
| `/global_path` | `nav_msgs/msg/Path` | `pcd_path_planner` | generic consumers | depth 10 |
| `/global_path_metadata` | `r3d_interfaces/msg/PathWithMetadata` | `pcd_path_planner` | `path_follower` | depth1, reliable, transient-local |
| `/hesai_ros_driver/hesai/lidar_points` | `sensor_msgs/msg/PointCloud2` | external driver | `local_filter` | SensorDataQoS: depth5, best-effort, volatile |
| `/local/filtered_obstacles` | `sensor_msgs/msg/PointCloud2` | `local_filter` | `path_follower`, optional Nav2 | reliable output depth10; follower best-effort/volatile/depth5; retains input header |
| `/local/cliff_virtual_wall` | `sensor_msgs/msg/PointCloud2` | `local_filter` | none internally | depth 10 |
| `/stair_detect` | `geometry_msgs/msg/PointStamped` | `local_filter` | none internally | sent only when a step is detected |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `path_follower` | external base | 10 Hz control output |
| `/clicked_point` | `geometry_msgs/msg/PointStamped` | RViz/external | `rviz_interface` | 3D height point |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | RViz/external | `rviz_interface` | initial calibration pose |
| `/goal_pose` | `geometry_msgs/msg/PoseStamped` | RViz/external | `rviz_interface` | goal pose |

Odometry, cloud input and command output topics are selected in the robot YAML;
generic planner outputs and RViz input topics keep their existing names.

## Services and actions

| Name | Type | Server | Client/purpose |
|---|---|---|---|
| `/recalibrate_pose` | `std_srvs/srv/Trigger` | `rviz_interface` | external; return to calibration mode |
| `/compute_path_to_pose` | `nav2_msgs/action/ComputePathToPose` | `pcd_path_planner` | `rviz_interface` or external |

There are no other application services or actions. ROS parameter services are
not listed here.

## Parameters

### Preprocessor (`pcd_analyser`)

| Parameter | Default | Unit | Effect |
|---|---:|---|---|
| `pcd_path` | `environment.pcd` | path | Input PCD; expands `~` and resolves absolute path |
| `voxel_size_cm` | 5.0 | cm | Voxel edge length |
| `min_step_height_cm` | 5.0 | cm | Maximum height difference treated as flat |
| `max_step_height_cm` | 25.0 | cm | Maximum connectable step height |
| `min_points_per_sqm` | 10.0 | points/m² | Density threshold for synthesized floor |
| `min_points_per_voxel` | 3 | points | Minimum points in an occupied voxel |
| `floor_height_tolerance` | 0.02 | m | Planarity term; accepted Z range is below `2*tolerance + 0.02 m` |
| `ground_fill` | `true` | boolean | Enable density and neighborhood filling |
| `robot_base_clearance_cm` | 10.0 | cm | Start height for collision checks |
| `robot_narrow_radius_cm` | 30.0 | cm | Narrow-area radius |
| `robot_radius_cm` | 40.0 | cm | Normal collision radius |
| `robot_height_cm` | 80.0 | cm | Collision cylinder height |
| `analysis_grid_size_cm` | 20.0 | cm | Density-analysis XY cell size |
| `cluster_gap_threshold_cm` | 20.0 | cm | Gap separating height clusters |
| `fill_plane_iterations` | 2 | count | Maximum neighborhood fill rounds |
| `fill_plane_search_radius` | 2 | voxels | Neighbor search radius |
| `fill_plane_min_neighbors` | 4 | count | Required traversable neighbors |

### Map publishers and planners

| Node | Parameter | Default | Effect |
|---|---|---|---|
| `pcd_server` | `pcd_path` | `environment.pcd` | PCD to publish |
| `pcd_server` | `map_frame` | `map` | Coordinate frame label; no transform |
| `pcd_path_planner` | `map_dir` | `<share/r3d_preprocessor>/maps`, fallback `/tmp` | Base directory for relative names |
| `pcd_path_planner` | `map_name` | `map_analysed.pcd` | Analyzed PCD filename/path |
| `pcd_path_planner` | `voxel_size_cm` | 5.0 | Reconstruction grid size |
| `pcd_path_planner` | `min_step_height_cm` | 5.0 | Flat/step boundary |
| `pcd_path_planner` | `max_step_height_cm` | 25.0 | Maximum step height |

`local_filter`, `path_follower` and `rviz_interface` now declare operating
parameters. [CONFIGURATION.md](CONFIGURATION.md) lists all settings, including
Odometry, geometry forwarding, launch flags, graph costs and visualization.
The tables above retain standalone-node defaults; normal startup uses YAML.

## Nav2 configuration

`r3d_planner_params.yaml` is not a complete bringup. It contains:

- `scan_filtered` and `cliff_virtual` observation-source names under
  `local_costmap.local_costmap`;
- `/local/filtered_obstacles`, height range 0.05–2.0 m, marking, clearing, and
  raytrace range 0.7–10.0 m for `scan_filtered`;
- an MPPI `FollowPath` excerpt with X velocity -0.1–0.5 and critic settings.

There is no configuration block for `cliff_virtual`. Placeholder comments
remain, and no launch file loads this YAML.

## Build and installation

The two Python packages install modules, Ament resource entries, manifests,
LICENSE and Forthcoming changelogs. `r3d_planner` also installs central/robot YAML and four launch files.
`r3d_preprocessor` explicitly does not install `maps/`. `r3d_interfaces` uses ament_cmake/rosidl to generate and install message code,
headers and typesupport libraries, with manifest, schema, LICENSE, README and
changelog. Launch files are installed rather than compiled. See [../INSTALL.md](../INSTALL.md)
for commands.


## Current AP05 composition and frame validation

Four launches accept optional namespace; root names remain the default. Internal
interfaces remap consistently, while explicit absolute robot-profile topics and
TF frame IDs remain intentional global contracts. Relative robot topic names
are valid. RViz action lookup uses the node namespace and a bounded configurable
wait. Selection frame/finite geometry and quaternion checks precede calibration
or planning; normalized valid quaternions are published. Odometry TF composition
rejects nonfinite translation and unavailable/time-incompatible transforms.
Local filter sensor data accepts best-effort/reliable input; outputs retain their
original frame and QoS. Follower obstacle monitoring is now an opt-in feature;
its parameter/input/TF/time/recovery contract is documented in CONFIGURATION.md.

## M02 placement

The follower owns monitoring, reuses its Odometry TF buffer and keeps a single
Twist publisher. Its default mutually exclusive callbacks serialize input and
control. Clock jump notifications only set an event; no command is published
from the clock callback. Enabled monitoring uses a steady control timer, an
immediate zero on invalid input/obstacles and a final gate before command output.
The standalone monitor class stores only successful measurements, their receipt
time and explicit failure reason. It does not own a sensor/filter lifecycle or
broadcast TF. A failed sample cannot recover merely because TF later appears.

The optional filter retains sensor-axis thresholds. Nonfinite-only input now
yields no clear output; valid empty output still has complete XYZ metadata.
See [the monitoring reference](CONFIGURATION.md#obstacle-monitoring-m02-humble).


## AP05 local geometry contract

The additional near-obstacle branch prevents the demonstrated radial loss while
preserving the stair/cliff branch. Filter output stays in the input frame.
M02 evaluates timestamped sensor-to-base TF and the existing open forward
rectangle; it validates geometry as well as data freshness, without proving
physical sensing coverage. With monitoring disabled, the legacy direct-frame
ROI remains. No new dependency, ROS type, topic, planner or body model is added.
See [configuration](CONFIGURATION.md#local-obstacle-geometry-and-near-return-retention)
for formulas, optional legacy mode and the distinction from offline robot geometry.


## Debian validation phases

R28 changes test/build integration only. Source → build → build-time tests →
staging → package → installation → mandatory source-free runtime tests remain
separate phases. Installation-dependent fixtures use actual package shares;
copy and Debian prefixes are validated through ament registration. The separate
local release wrapper requires both phases and complete case-identity coverage.
Navigation algorithms, M01/M02, geometry, ROS names and TF ownership are unchanged.
