# Technical Comparison with Go2-W-Praxisphase

## Scope and evidence

This review compares the PCD-only `V2` branch of this repository with
[`RoboProjekt/Go2-W-Praxisphase`](https://github.com/RoboProjekt/Go2-W-Praxisphase.git).
The inspected revisions were:

| Repository | Branch | Revision |
|---|---|---|
| `R3D-Planner` | `V2` | `cf0c527b587b387c56c69ae4c90a98d180f2d22d` |
| `Go2-W-Praxisphase` | `main` | `3e1c5d4e52c90717c9415cb279c3dd2dcf780ee1` |

The comparison covered source, manifests, setup files, shell and launch files,
YAML, ROS interfaces, TF use, maps, controller behavior, and existing
documentation. Generated build output and large simulation assets were not
treated as canonical implementation. No robot was commanded and no functional
source was changed.

The reference is valuable deployment evidence, but it contains several
work-in-progress and internally inconsistent scripts. Findings therefore
distinguish current-repository defects from reference-only defects.

## System relationship

The reference repository contains two different layers:

1. `R3D_Planner/`, the planning workspace from which the current project was
   separated; and
2. the surrounding Go2W deployment, including Unitree SDK adapters, Hesai
   configuration, LiDAR SLAM, Docker/domain setup, mapping experiments, and
   startup scripts.

The functional Python files in reference `R3D_Planner/` match `V1` except for
one text file. `V2` intentionally removes the Pickle generator, Pickle map
publisher, and Pickle planner while retaining the analyzed-PCD path. This is an
`ARCHITECTURE CHANGE`, not evidence of an accidental package loss.

```text
Reference deployment
--------------------
Hesai driver ---> /hesai_ros_driver/hesai/lidar_points ---> LiDAR SLAM
       |                                                       |
       +-------------------> R3D local_filter                  +--> odom -> base_link
Unitree LowState ---> Go2W IMU adapter ---> /imu/data
R3D path_follower ---> /cmd_vel ---> Unitree SportClient adapter

Current V2 repository
---------------------
raw PCD ---> pcd_analyser ---> analyzed RGB PCD ---> pcd_path_planner
                         \--> pcd_server/RViz          |
RViz ---> rviz_interface ---> ComputePathToPose -------+--> /global_path
Hesai cloud ---> local_filter ---> path_follower ---> /cmd_vel
```

The current repository deliberately does not vendor the hardware drivers,
LiDAR SLAM, Docker setup, or Unitree SDK. Those remain external runtime
requirements.

## ROS package comparison

| Area | Reference | Current V2 | Classification |
|---|---|---|---|
| R3D packages | `r3d_preprocessor`, `r3d_planner` | same names and `ament_python` build type | `EXPECTED` |
| PCD analysis | `pcd_analyser` | retained | `EXPECTED` |
| PCD publishing | `pcd_server` | retained | `EXPECTED` |
| PCD planning | `pcd_path_planner` | retained | `EXPECTED` |
| Pickle pipeline | generator, publisher, planner present | removed | `ARCHITECTURE CHANGE` |
| Planner/local-control nodes | local filter, RViz interface, follower, test TF | retained | `EXPECTED` |
| Go2W/Hesai/SLAM packages | deployment files outside `R3D_Planner/` | not included | `EXPECTED`; external boundary |
| Launch files | external deployment scripts and LiDAR-SLAM launches | none in this repository | `CONFIGURATION CHANGE` |
| Nav2 YAML | incomplete fragment | same incomplete fragment | `LEGACY` |

Both current packages have incomplete dependency metadata. This was inherited
from the reference rather than introduced by V2. The current documentation's
explicit apt list and rosdep exclusions remain necessary until manifests are
corrected in a functional maintenance step.

Current R3D code uses Open3D rather than PCL and has no direct PCL import or
linkage. PCL may still be required by external sensor/localization packages.
The reference Unitree wrapper CMake uses Unitree SDK2, Cyclone DDS libraries,
ROS messages, Eigen, and `rosbag2_cpp`, but no accompanying `package.xml` is
present at that wrapper root and SDK include/library paths are hard-coded.

## ROS interfaces

The R3D ROS interface names are unchanged from the reference R3D source.

| Interface | Type | Current owner/use | Reference integration |
|---|---|---|---|
| `/compute_path_to_pose` | `nav2_msgs/action/ComputePathToPose` | `pcd_path_planner` server; `rviz_interface` client | same |
| `/global_path` | `nav_msgs/msg/Path` | planner to `path_follower` | same |
| `/planned_path` | `visualization_msgs/msg/Marker` | planner visualization | same |
| `/map_pointcloud` | `sensor_msgs/msg/PointCloud2` | `pcd_server` | same |
| `/hesai_ros_driver/hesai/lidar_points` | `sensor_msgs/msg/PointCloud2` | external Hesai driver to `local_filter` | configured by the reference Hesai driver |
| `/local/filtered_obstacles` | `sensor_msgs/msg/PointCloud2` | `local_filter` to follower; optional costmap input | same |
| `/local/cliff_virtual_wall` | `sensor_msgs/msg/PointCloud2` | no current internal subscriber | named but not configured in the Nav2 fragment |
| `/stair_detect` | `geometry_msgs/msg/PointStamped` | no current internal subscriber | same |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | follower output | reference Go2W adapter subscribes and calls `SportClient::Move` |
| `/clicked_point`, `/initialpose`, `/goal_pose` | RViz standard message types | `rviz_interface` inputs | same |
| `/recalibrate_pose` | `std_srvs/srv/Trigger` | `rviz_interface` server | same |

The reference Go2W IMU adapter additionally publishes `/imu/data`,
`/imu/accel`, and `/imu/gyro` in frame `imu_link`. It declares a magnetometer
publisher but never publishes a magnetometer message. These topics are inputs
to external localization experiments, not to the current R3D nodes.

### Action behavior that the interface name does not imply

Both planners always use `request.start`; they do not branch on `use_start`.
They accept but do not evaluate `planner_id`, do not transform input poses, and
do not implement feedback or cancellation handling. Start and goal numeric
coordinates must therefore be in `map`, even though the result copies the goal
header's frame string. This is a `POTENTIAL BUG` for arbitrary Nav2 clients and
an `EXPECTED` constraint for the documented direct calls.

## TF and coordinate frames

The R3D nodes require the following composed transform:

```text
map --rviz_interface (static)--> odom --external LiDAR odometry--> base_link
                                      |
                                      +-- reference static --> hesai_lidar_link
```

The reference startup scripts also publish identity `body -> base_link`. Their
Hesai transform command is:

```bash
ros2 run tf2_ros static_transform_publisher \
  0.1384 0.0 0.1284 1.5708 0 0 base_link hesai_lidar_link
```

The positional Euler-angle convention must be checked against the installed
ROS 2 Humble executable before treating the rotation as calibration metadata.
The Hesai YAML labels outgoing clouds `hesai_lidar_link`. The planner and map
publisher use `map`; neither transforms map coordinates.

The user-confirmed Go2W deployment proves that a working TF and sensor chain
has existed. Static review still identifies two assumptions that must remain
true:

- `rviz_interface` writes the clicked map pose directly as `map -> odom`.
  Mathematically, this is exact only when the current odometric base pose is
  the identity, or when the operator has already accounted for that pose.
- `local_filter` does not transform the cloud into `base_link`; its X-forward,
  Y-lateral, Z-up thresholds operate directly in `hesai_lidar_link`.

Both are `REQUIRES VERIFICATION` after any localization reset or sensor-mount
change. Runtime checks are listed below.

## Map representations and preprocessing

### Reference/V1 Pickle representation

The original preprocessor stores a NetworkX graph plus `origin`, `voxel_size`,
`robot_radius`, and obstacle voxel indices. Nodes are integer voxel indices.
World coordinates are reconstructed as:

```text
world = origin + voxel_index * voxel_size + voxel_size / 2
```

Edges connect eight neighboring XY columns. Their weights are 3D Euclidean
distance, multiplied by `1.2` when either endpoint is narrow and by `3.0` for a
step above the minimum and not above the maximum step height.

### Current V2 PCD representation

`pcd_analyser` saves voxel-center world coordinates and RGB classes:

| Color | Meaning |
|---|---|
| green | normal floor |
| cyan | narrow floor |
| yellow | access to a step edge |
| magenta | obstacle |

`pcd_path_planner` rebuilds node keys by rounding each coordinate divided by
the separately supplied voxel size. It then reconstructs the same eight-way
XY topology and 1.2/3.0 penalties. The conversion intentionally exchanges the
portable visual PCD for loss of the original graph metadata and explicit edge
types. This is an `IMPROVEMENT` in portability and an `ARCHITECTURE CHANGE` in
reproducibility.

The analyzed PCD does not store voxel size, step thresholds, robot dimensions,
or preprocessing settings. A mismatched planner voxel size can merge keys or
alter adjacency silently. This is a `POTENTIAL BUG`; always preserve the map's
parameter set with the artifact.

`min_points_per_sqm` is converted to a per-cell count using
`max(3, int(value * analysis_grid_size**2))`. With the 0.20 m default grid,
values 1 and 10 both resolve to the enforced minimum of three points per cell.
`floor_height_tolerance` is used in the planarity test
`z_range < 2 * tolerance + 0.02 m`; height clusters themselves are separated
by `cluster_gap_threshold_cm`. These details correct earlier shorthand in the
README parameter description.

## A* graph, costs, and output

Both global planners use a nearest-neighbor KDTree for start and goal, then a
custom A* over positive NetworkX edge weights. The heuristic is straight-line
3D distance. Because every edge cost is at least its straight-line distance,
the heuristic is admissible for the generated graph. No closed set or stale
heap-entry rejection is used; this can add work but does not by itself change
the optimum with the current positive costs.

Important behavior:

- start and goal snap to the nearest traversable node with no maximum snap
  distance (`POTENTIAL BUG` for out-of-map goals);
- unknown non-magenta PCD colors become normal floor (`POTENTIAL BUG` for a
  malformed or unrelated colored PCD);
- step direction is not represented; step edges are undirected (`EXPECTED`
  for the current graph model);
- path orientation is repurposed as a narrow flag: narrow poses get
  `z=1, w=1`, which is not a normalized quaternion (`POTENTIAL BUG` for generic
  pose consumers);
- the controller uses only path XY and the narrow flag; path Z and
  `stair_access` do not directly alter motion (`ARCHITECTURE CHANGE` between 3D
  planning and 2D control).

## Local perception and controller

The local filter keeps all thresholds as source constants. It removes returns
within 0.65 m, classifies obstacle heights from 0.05 to 1.0 m, recognizes a
step from more than 50 points in its ROI, and creates a virtual cliff wall when
fewer than 30 floor points occur in the forward ROI.

The filter manually reads the PointCloud2 byte buffer as packed 12-byte XYZ
records. It does not use the message's fields, offsets, `point_step`, row step,
endianness, or organized-cloud shape. The Hesai driver commonly emits extra
fields; the reference YAML establishes the topic and frame but does not prove
the on-wire byte layout. This is a `POTENTIAL BUG`, not a portable sensor
contract. Verify `point_step` and fields at runtime before relying on the
filter.

The follower is a 10 Hz planar lookahead controller. It stops for points in
`/local/filtered_obstacles`, but nothing in the current repository connects
`/local/cliff_virtual_wall` or `/stair_detect` to motion control. On a TF lookup
failure it publishes no fresh zero command. The reference `go2w_driver.cpp`
forwards every `/cmd_vel` directly to `SportClient::Move` and performs no
timeout stop, velocity clamp, command mux, or emergency-stop logic. Therefore
those protections must be supplied and validated outside these repositories.
Earlier documentation implying that such a safety chain was demonstrated by
the reference was a `DOCUMENTATION ERROR` and has been corrected.

## Installation and startup comparison

The supported target remains ROS 2 Humble. Reference scripts contain a legacy
host variable set to `foxy` around a Humble container; this is `LEGACY`
deployment material and does not establish support for another ROS release.

The reference deployment identifies the following external components:

- Unitree SDK2/ROS 2 messages and a custom `unitree_ros2_example` package;
- Hesai ROS driver with sensor address `192.168.123.20`, UDP port 2368,
  frame `hesai_lidar_link`, serial devices `/dev/ttyUSB0` and `/dev/ttyUSB1`,
  and correction file `<path-to-hesai-correction-file>`;
- LiDAR SLAM `scanmatcher_node` for `odom -> base_link` and optional graph SLAM;
- a deployment network interface (`eth0` in later scripts, `eno1` in older
  notes), host networking, and a consistent ROS domain;
- static sensor/body transforms.

These are deployment-specific values, not defaults to copy to another machine.
The reference alternates ROS domain 0 and 10 and contains both local and remote
hard-coded Unitree SDK paths. This is a `CONFIGURATION CHANGE` that must be
resolved per deployment.

The reference CMake file builds the command adapter as `go2w_driver`, but its
later startup scripts invoke `go2w_cmd_vel`, which is not an installed target
in the inspected source. This is a reference-side `POTENTIAL BUG`. The current
documentation now tells operators to verify the actual installed executable
instead of copying that command.

Constructing the reference command adapter immediately calls
`RecoveryStand()`, waits two seconds, and calls `BalanceStand()` before normal
spinning. Starting it can therefore cause physical posture change even before
the first `/cmd_vel`; this is a safety-critical startup prerequisite.

## Potential issues and next investigations

| ID | Affected component | Current behavior | Reference behavior | Potential impact | Confidence | Recommended verification |
|---|---|---|---|---|---|---|
| P01 | `r3d_local_filter.py` | Reads each cloud record as packed XYZ float32 without consulting message metadata. | Hesai YAML fixes topic/frame but not its binary record layout. | Extra fields or padding can corrupt XYZ or discard a cloud. | High | Echo `fields` and `point_step`; replay a representative cloud and compare decoded bounds. |
| P02 | both planners | Copies the goal frame to output but performs no input transform or frame validation. | Identical R3D behavior. | A non-`map` request can produce a numerically wrong path labeled with another frame. | High | Send equivalent `map` and transformed non-`map` test goals; only the `map` request is currently supported. |
| P03 | both planners | KDTree always selects a nearest node; no maximum distance exists. | Identical R3D behavior. | An out-of-map goal can silently route to a remote boundary node. | High | Send goals at increasing distance beyond map bounds and record snap distance/result. |
| P04 | planners and follower | Uses pose quaternion fields as a narrow flag and emits `(z=1,w=1)`. | Identical R3D behavior. | Generic Nav2/pose consumers receive a non-normalized quaternion. | High | Inspect `/global_path`; restrict it to the internal follower until metadata is redesigned. |
| P05 | local filter, follower, Nav2 fragment | Publishes cliff/stair detections, but the follower ignores both and the cliff costmap source has no block. | Identical R3D behavior. | A detected drop may not stop the robot. | High | Trace subscribers with `ros2 topic info -v` and perform a no-motion synthetic-cloud test. |
| P06 | follower and Go2W adapter | TF loss emits no fresh zero command; the adapter forwards commands without a timeout. | Reference adapter has the same direct forwarding behavior. | The last motion command may persist depending on robot-side semantics. | Medium; persistence is runtime-dependent | Interrupt TF while wheels are disabled and observe `/cmd_vel` plus robot-adapter timeout behavior. |
| P07 | `rviz_interface` | Publishes clicked pose directly as `map -> odom`. | Identical R3D behavior with external odometry. | Calibration is offset when the current odometric base pose is nonzero. | High mathematically; operational impact depends on workflow | Calibrate after moving in odom and compare clicked pose with `tf2_echo map base_link`. |
| P08 | PCD analyzer/planner | Map settings are not stored in the analyzed PCD. | Pickle path retains origin/voxel size; PCD path does not. | Wrong planner parameters silently change keys, connectivity, and costs. | High | Record settings beside the map and compare graph node/edge counts under matching and mismatched values. |
| P09 | PCD planner | Treats every non-magenta unrecognized color as floor. | Same PCD planner in the reference. | An unrelated or damaged colored PCD can become traversable. | High | Count RGB classes before planning and reject unexpected colors operationally. |
| P10 | action servers | Ignores `use_start` and `planner_id`; provides no feedback/cancel handling. | Identical R3D behavior. | General Nav2 clients can observe semantics different from the standard action contract. | High | Exercise `use_start=false`, cancellation, and result fields with a non-motion action test. |
| P11 | reference Go2W startup | Documentation invokes `go2w_cmd_vel`. | Inspected CMake installs `go2w_driver`. | Startup can fail before command transport is available. | High for inspected revision | Run `ros2 pkg executables unitree_ros2_example` on the deployed image. |
| P12 | reference `go2w_driver.cpp` | Calls recovery/balance stand during node construction. | This behavior is outside current R3D and easy to miss in shell-level startup. | Launching the adapter can move the robot before a velocity command is sent. | High | Secure the robot and validate the startup state transition with wheels unloaded. |

## Classified findings

| ID | Classification | Applies to | Finding |
|---|---|---|---|
| C01 | `EXPECTED` | both | R3D topic, action, service, node, and frame names match the reference R3D code. |
| C02 | `ARCHITECTURE CHANGE` | V2 | Pickle processing and planning were intentionally removed; PCD analysis/planning remains. |
| C03 | `IMPROVEMENT` | V2 | PCD artifacts are inspectable and less trust-sensitive than Python Pickle. |
| C04 | `POTENTIAL BUG` | current/reference | PointCloud2 parsing assumes packed XYZ and ignores the declared binary layout. |
| C05 | `POTENTIAL BUG` | current/reference | Arbitrary action frame strings are copied but coordinates are never transformed. |
| C06 | `POTENTIAL BUG` | current/reference | No maximum distance is applied when snapping start/goal to the graph. |
| C07 | `POTENTIAL BUG` | current/reference | Narrow metadata creates invalid pose quaternions for generic consumers. |
| C08 | `POTENTIAL BUG` | current/reference | Cliff and stair outputs have no internal motion-control consumer. |
| C09 | `POTENTIAL BUG` | current/reference | The follower emits no stop command during TF failure; the shown robot adapter has no watchdog. |
| C10 | `REQUIRES VERIFICATION` | deployment | Confirm `map -> odom` calibration math when odometry is nonzero. |
| C11 | `REQUIRES VERIFICATION` | deployment | Confirm sensor axes and PointCloud2 fields/stride on the deployed Hesai driver. |
| C12 | `LEGACY` | reference | Mixed host/container ROS setup and multiple superseded mapping workflows coexist. |
| C13 | `CONFIGURATION CHANGE` | reference/deployment | Network interface, ROS domain, IPs, serial devices, correction path, and SDK paths are machine-specific. |
| C14 | `POTENTIAL BUG` | reference | Startup scripts call `go2w_cmd_vel`, while inspected CMake installs `go2w_driver`. |
| C15 | `DOCUMENTATION ERROR` | current docs | Claims that the reference proves watchdog/mux/emergency-stop behavior were removed. |
| C16 | `DOCUMENTATION ERROR` | old docs | `floor_height_tolerance` does not form clusters; it gates cluster planarity. |
| C17 | `POTENTIAL BUG` | current | PCD preprocessing metadata is not stored with the analyzed map. |
| C18 | `LEGACY` | current/reference | Incomplete Nav2 YAML is not loaded by any launch file. |
| C19 | `POTENTIAL BUG` | current/reference | `use_start`, feedback, cancellation, and most action result metadata are not implemented. |
| C20 | `EXPECTED` | deployment | The complete stack and TF/sensor integration have been successfully exercised on the Go2W under Humble. |

## Documentation corrections made by this review

- Added the reference-derived Go2W/Hesai/SLAM boundary and exact interface
  ownership without importing deployment code.
- Clarified the complete TF chain and the sensor frame retained by the local
  filter.
- Corrected the meaning of `floor_height_tolerance` and explained the effective
  minimum density-cell count.
- Reclassified packed-XYZ parsing as an unresolved compatibility risk because
  the reference does not establish a 12-byte PointCloud2 layout.
- Removed the unsupported claim that watchdog, command mux, and emergency-stop
  behavior are implemented or proven by the inspected reference.
- Documented the reference `go2w_driver`/`go2w_cmd_vel` executable mismatch and
  ROS-domain/network/path inconsistencies here rather than presenting them as
  current installation commands.

## Validation performed

Static validation performed during this review:

- both repositories and both current branches were inspected at the revisions
  listed above;
- package manifests, setup files, R3D Python sources, reference Go2W adapters,
  launch scripts, shell scripts, Hesai YAML, and Nav2 YAML were read;
- `diff -qr` confirmed that reference R3D functional source matches V1;
- `colcon list --names-only` discovers `r3d_planner` and `r3d_preprocessor`;
- Python AST parsing succeeded for all 18 Python files on V2 and all 21 on V1;
- included PCD headers were checked: the source map has 602,619 points and the
  analyzed RGB PCD has 556,586 points;
- V2 package tests were run separately with system Python: PEP257 passed and
  copyright was skipped in both packages; Flake8 failed with 151 preprocessor
  and 166 planner findings. V1 produced the already documented 286 and 200
  Flake8 findings respectively.

No hardware runtime, ROS graph, TF timing, sensor packet, planning latency, or
motion test was performed. A full build remains blocked on this workstation by
the already documented local Python packaging conflict; that conflict is not
present on the deployed Go2W.

## Recommended non-motion runtime checks

Run these on the Humble Go2W deployment after sourcing its driver and R3D
workspaces:

```bash
ros2 pkg executables unitree_ros2_example | grep go2w
ros2 topic info /hesai_ros_driver/hesai/lidar_points -v
ros2 topic echo /hesai_ros_driver/hesai/lidar_points --once \
  --field fields
ros2 topic echo /hesai_ros_driver/hesai/lidar_points --once \
  --field point_step
ros2 run tf2_ros tf2_echo base_link hesai_lidar_link
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo map base_link
ros2 action info /compute_path_to_pose
ros2 topic info /cmd_vel -v
```

Before enabling motion, separately verify command timeout behavior, command
arbitration, emergency stop, the consumer of the cliff output, and zero-command
behavior when TF or LiDAR data is lost.
