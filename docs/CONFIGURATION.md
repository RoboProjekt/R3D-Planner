# Runtime configuration reference

## Ownership and precedence

`r3d_planner/config/planner_config.yaml` is the central entry point. Its
`robot_config` path is relative to that directory and must stay inside it.
`robots/Go2W.yaml` owns geometry, robot interfaces and velocity limits; central sections own
algorithm settings. `shared` is forwarded to both analysis and reconstruction.
There is no merge precedence between competing definitions: the schema rejects
misplaced, missing, unknown and duplicate keys. Other launch parameters override
the deliberate standalone-node defaults; defaults never override YAML. The four
profile-owned velocity settings have no standalone fallback: the follower validates
the selected profile before its command publisher/timer, accepts only identical
startup ROS values, and declares all four visible velocity parameters read-only.

The loader reads both files anew on each launch and logs their resolved paths.
With `colcon build --symlink-install`, module and configuration
symlinks resolve to live source files. New robot files are read directly from
source and need no rebuild. For a copied installation, set `R3D_CONFIG_DIR`
to a user-owned directory containing `planner_config.yaml` and `robots/`.
The explicit directory does not need a source checkout and takes precedence.
Without an override, directly imported source/symlink modules use live source
configuration; regular copy installations resolve YAML and robot profiles through
`ament_index_python` in the package share. No source checkout is required.
Installed templates are read-only resources; copy them into a user-owned
directory to edit settings. Rebuild a copy installation to refresh templates.
Moving the workspace itself requires rebuilding its installation.

YAML changes are restart-time configuration, not live ROS parameter updates.
Stop the affected launch, edit YAML, and restart the same command in the same
terminal. No build or re-sourcing is needed. If processing settings or geometry
change, regenerate the analyzed PCD before planning.

## Robot YAML

| Key below `robot` | Go2W value | Meaning |
|---|---|---|
| `name` | `Go2W` | Configuration identification in startup logs |
| `geometry.robot_height_cm` | 80.0 | Collision-cylinder height, cm |
| `geometry.robot_narrow_radius_cm` | 30.0 | Tight collision radius, cm |
| `geometry.robot_radius_cm` | 40.0 | Normal safety radius, cm |
| `geometry.robot_base_clearance_cm` | 10.0 | Collision-check lower clearance above floor, cm |
| `velocity_limits.max_linear_speed` | 0.35 | Positive finite forward speed bound, m/s |
| `velocity_limits.max_angular_speed` | 0.6 | Positive finite normal steering bound, rad/s |
| `velocity_limits.max_angular_speed_narrow` | 0.2 | Positive narrow steering bound, rad/s; <= normal bound |
| `velocity_limits.narrow_speed_factor` | 0.4 | Positive factor <=1; reduced forward speed = robot maximum × factor |
| `odometry.topic` | `/lidar_odometry` | Standard `nav_msgs/msg/Odometry` input |
| `odometry.odom_frame` | `odom` | Required Odometry header frame |
| `odometry.base_frame` | `base_link` | Required Odometry child frame |
| `topics.pointcloud` | `/hesai_ros_driver/hesai/lidar_points` | Live Filter sensor input |
| `topics.cmd_vel` | `/cmd_vel` | Explicit follower command output |

Robot geometry uses centimetres. The loader maps
`odometry.topic` to the ROS parameter `odometry_topic` and the frame keys to
`odom_frame` and `base_frame`. Geometry is forwarded to the preprocessor and
planner. Only the preprocessor uses it for collision classification; the planner
does not reinterpret existing PCD colors using new dimensions.

Height and radii must be positive; narrow radius must not exceed normal radius.
Base clearance is nonnegative and smaller than height. Topics must be valid
relative or absolute ROS topic names; the map, odometry and base frames must be distinct.

## Central YAML

`maps.pcd_path` and `maps.map_name` resolve relative to the central config
directory, not the shell working directory. Absolute external map paths are
also accepted. Preprocessing validates the input exists; planner/map/follower
launch validates the analyzed file exists. The other map path may not exist yet.
No PCD maps are bundled. Both shipped map values are empty. Set the
selected path to your own suitable PCD before launch; preprocessing requires
`pcd_path`, while planner/map/follower require `map_name`. The unused value may
remain empty or refer to a future output. Missing, non-PCD and directory inputs
fail with the selected key and resolved path; no fallback map is selected.
Only PCD files are accepted. The analyzer preserves `<input>_analysed.pcd` as
its filename, but writes it into optional `preprocessing.output_dir`; keep
`maps.map_name` aligned manually. A nonempty output directory resolves relative
to the selected YAML, or accepts absolute and `~` paths. The empty default uses
`$XDG_DATA_HOME/r3d_preprocessor` when XDG_DATA_HOME is absolute, otherwise
`~/.local/share/r3d_preprocessor`. Old YAMLs without output_dir use the same default.
Input files/directories may be read-only. Output directories are created if needed;
existing output files and symlinks are rejected without overwrite. Failed
processing or writing produces a nonzero analyzer exit. Package shares are
read-only resources and are never an implicit output directory.

For a copied installation, create an editable user configuration from its share:

```bash
r3d_share=$(ros2 pkg prefix --share r3d_planner)
mkdir -p "$HOME/.config/r3d_planner"
cp "$r3d_share/config/planner_config.yaml" "$HOME/.config/r3d_planner/"
cp -r "$r3d_share/config/robots" "$HOME/.config/r3d_planner/"
export R3D_CONFIG_DIR="$HOME/.config/r3d_planner"
```

Then edit that directory's YAML. For example, replace these illustrative paths
with your own files (the analyzed file need not exist until you start planning):

Edit these fields in the copied full YAML. This partial example is not a
replacement configuration; retain all other required sections and keys.

```yaml
maps:
  pcd_path: /path/to/your/input.pcd
  map_name: /path/to/your/output/input_analysed.pcd
preprocessing:
  output_dir: /path/to/your/output
  # Keep all other shipped preprocessing keys unchanged.
```

No PCD is needed to install the packages. Provide map data that you are
permitted to use.

| `shared` key | Default | Unit / effect |
|---|---:|---|
| `voxel_size_cm` | 5.0 | cm; analysis voxel and graph reconstruction grid |
| `min_step_height_cm` | 5.0 | cm; largest flat connection |
| `max_step_height_cm` | 25.0 | cm; largest connectable graph step |

Voxel size and maximum step are positive; minimum step is nonnegative and
strictly below maximum step. PCD artifacts do not embed these values.

| `preprocessing` key | Default | Unit / effect |
|---|---:|---|
| `output_dir` | empty | optional directory path; resolved as described above |
| `min_points_per_sqm` | 10.0 | points/m²; floor-fill threshold `max(3, int(density * grid_m²))` |
| `min_points_per_voxel` | 3 | integer hits; occupied-voxel filtering |
| `floor_height_tolerance` | 0.02 | m; fill planarity `z_range < 2*tolerance + 0.02` |
| `ground_fill` | true | boolean; density and neighborhood filling |
| `analysis_grid_size_cm` | 20.0 | cm; XY density-analysis cells |
| `cluster_gap_threshold_cm` | 20.0 | cm; vertical height-cluster separation |
| `fill_plane_iterations` | 2 | nonnegative integer; maximum fill rounds |
| `fill_plane_search_radius` | 2 | positive integer voxels; neighborhood radius |
| `fill_plane_min_neighbors` | 4 | positive integer; required floor neighbors |

| `planner` key | Default | Unit / effect |
|---|---:|---|
| `map_frame` | map | Map/goal coordinates and global pose frame |
| `odometry_timeout_sec` | 1.0 | s; maximum Odometry timestamp age; future timestamps rejected |
| `narrow_cost_multiplier` | 1.2 | dimensionless; flat edges touching narrow nodes |
| `stair_cost_multiplier` | 3.0 | dimensionless; edges above the flat boundary |
| `path_line_width` | 0.05 | m; Marker line thickness |
| `path_z_offset_voxels` | 1.5 | voxels; visualization-only vertical offset |

Cost multipliers are at least 1 to preserve the existing Euclidean A* heuristic.
The visual offset can be zero. Offline explicit start and goal headers must use
`map_frame`; request coordinates in other frames are rejected, not transformed.

`components.live_filter.enabled` and `components.rviz_interface.enabled` are
independent booleans, both initially true. Planner startup uses launch conditions.
Neither switch starts the RViz GUI or a hardware driver. `follower.launch.py`
is a separate explicit motion-producing command.

| `live_filter` key | Default | Unit / effect |
|---|---:|---|
| `min_height`, `max_height` | 0.05, 1.0 | m; obstacle Z band |
| `min_step_height`, `max_step_height` | 0.06, 0.22 | m; sensor-coordinate step Z band |
| `stair_roi_x_min`, `stair_roi_x_max` | 0.7, 1.1 | m; step ROI X bounds |
| `stair_roi_width` | 0.5 | m; step ROI half-width |
| `stair_min_points` | 50 | integer; detection needs strictly more points |
| `min_reliable_distance` | 0.65 | m; XY radial gate for stair/cliff and far-obstacle classification |
| `retain_near_obstacles` | true | Startup-only bool; additionally pass height-qualified near returns to the obstacle output |
| `cliff_roi_x_min`, `cliff_roi_x_max` | 0.7, 1.2 | m; visible-floor X bounds; wall at lower bound |
| `cliff_width` | 0.4 | m; cliff ROI and wall half-width |
| `cliff_min_ground_points` | 30 | integer; fewer floor points produce a wall |
| `cliff_wall_points` | 20 | positive integer; synthetic wall samples |
| `cliff_wall_height` | 0.5 | m; synthetic wall Z |

All distances are in the sensor frame. These step thresholds are separate from
offline world-coordinate graph connectivity and intentionally keep their
existing distinct semantics/defaults. Minimum bounds must be below maximum
bounds. PointCloud2 decoding honors field offsets, numeric XYZ types, endian
order and point/row padding; extra channels are ignored and NaN/Inf excluded.
Changing settings does not establish a sensor-to-base transformation or change
the sensor-axis assumptions.

| `rviz_interface` key | Default | Effect |
|---|---:|---|
| `action_server_timeout_sec` | 1.0 | s; positive bounded action-server wait, optional for older YAML |
| `match_radius` | 0.8 | m; maximum XY distance between point and pose selections |
| `publish_map_odom` | true | Publish static calibration TF; false for external global localization |

When calibration TF is disabled, goal selection requires no initial calibration.
The planner obtains the online start from Odometry, not from an RViz TF lookup.
The reset service changes only calibration state; it does not remove an existing
static transform. Static calibration assumes the odometric base pose is
identity. Use an external global localizer if this assumption is not satisfied.

| `path_follower` key | Default | Unit / effect |
|---|---:|---|
| `lookahead_distance` | 0.5 | m; target selection distance |
| `stop_distance` | 0.6 | m; obstacle corridor upper X bound |
| `goal_tolerance` | 0.2 | m; XY goal completion distance |
| `control_period_sec` | 0.1 | s; control timer period |
| `obstacle_x_min`, `obstacle_half_width` | 0.1, 0.3 | m; obstacle corridor lower X bound / half-width |
| `angle_threshold` | 0.5 | rad; turn/slow-forward boundary |
| `steering_gain` | 1.5 | 1/s; angular error to yaw rate |
| `turning_speed_factor` | 0.3 | General turning factor outside narrow areas, >0 and <=1 |

All four velocity settings are mandatory under the selected robot's
`velocity_limits`, not in the global controller table:

```yaml
# Excerpt within the existing robot mapping; retain name/geometry/odometry/topics.
robot:
  velocity_limits:
    max_linear_speed: 0.35  # m/s
    max_angular_speed: 0.6  # rad/s
    max_angular_speed_narrow: 0.2  # rad/s
    narrow_speed_factor: 0.4  # Go2W forward speed in narrow areas: 0.14 m/s
```

All four values require finite strictly positive int/float YAML scalars; int spelling
is normalized to ROS double. Null, bool, string, negative, NaN/Infinity, container,
missing and duplicate definitions are rejected. Zero profile limits are unsupported. Use the stop/monitoring contracts for
stopping; a velocity profile is not a stop command.

Normal mode uses `linear.x = max_linear_speed` or that value times
`turning_speed_factor`; `angular.z` uses the normal steering clamp. Narrow mode
uses zero or `max_linear_speed * narrow_speed_factor` in X and its separate
`max_angular_speed_narrow` clamp in Z. Both narrow settings come from the
selected robot, not global tuning. Go2W retains 0.14 m/s forward and at most
0.2 rad/s yaw in narrow areas. These are reduced operating settings, not
enforced minimum velocities: rotation-only, obstacle/timeout/goal stops and
zero yaw error still permit zero commands. `linear.y` remains zero; there is no new
planar-vector clamp. The narrow cap must be <= the selected profile angular limit,
and both speed factors must remain <=1. An incompatible profile/tuning pair is
rejected at startup. Choose a compatible narrow cap for each robot rather
than copying the Go2W values without checking them.

Matching ROS startup values forwarded by launch are
accepted, conflicting overrides are rejected, and runtime writes of all four
profile-owned parameters fail. Invalid profiles fail before any command
publisher exists. Direct `ros2 run` uses the same selected profile without needing
a map file merely to construct the follower; full launch retains its existing
map validation. To migrate an older external configuration, remove the global
`max_linear_speed`, `max_angular_speed`, `max_angular_speed_narrow` and
`narrow_speed_factor` keys and add them to its chosen robot profile; no fallback or automatic rewrite.

Controller settings are general tuning values, but must be checked against the
selected robot's limits. Missing/stale Odometry or missing global TF produces a
zero Twist; this does not replace an external command watchdog.

## Add or select another robot

1. Copy `robots/Go2W.yaml` to a new file under the same directory.
2. Set its name, dimensions, odometry topic/frames, cloud/command topics and validated
   finite positive `velocity_limits` for that robot. Do not copy Go2W speeds as
   evidence of another robot's safe operating limits.
3. Change `robot_config` in the central YAML to the new relative filename.
4. Recheck sensor axes, PointCloud2 binary layout and controller safety limits.
5. Restart preprocessing to regenerate the map, then restart the planner.

For example, selecting `odometry.topic: /kiss/odometry` needs no source change
if messages follow the configured base/odom frame contract and global localization
supplies `map -> odom`. A source describing a LiDAR frame rather than the base
requires an external frame adapter/extrinsic conversion, not merely a topic rename.
YAML selection is not a claim of physical support for a new platform.

## Direct node execution

Normal operation uses the launch files. Direct `ros2 run` allows ordinary ROS
parameter overrides for isolated node execution, but does not automatically
load all central tuning. The follower always loads the selected robot profile
for its four mandatory velocity settings, including in direct execution.
Use logged configuration paths and `ros2 param get` to inspect effective values.

Path narrow-area flags come from `PathWithMetadata.narrow`, indexed to its path.
They are never decoded from orientation fields. See
[Architecture and ROS interfaces](ARCHITECTURE.md#path-planning-and-metadata).

## Namespace and QoS contract

Each launch accepts `namespace:=robot_a`; the empty default preserves existing
root names. Internal absolute topic literals are consistently remapped to
namespace-relative names, including global_path_metadata and the planning action.
Explicit absolute robot topics remain global; relative robot topics inherit the
node namespace. Frame IDs and /tf ownership remain explicitly configured, with
no automatic TF prefix.

Live PointCloud2 input uses SensorDataQoS (best-effort, volatile, keep-last5),
accepting both reliable and best-effort producers. Local outputs remain reliable,
volatile, depth10; Odometry remains SensorDataQoS, map publication reliable
transient-local/depth1, metadata reliable transient-local/depth1. Deadline/lifespan
and liveliness settings retain library defaults; no real-time guarantee is made.
RViz rejects foreign-frame/nonfinite/invalid-quaternion selections; valid
orientations are normalized. The action-server timeout defaults to 1 s. Obstacle monitoring is separately configured below; it does not depend on RViz.


## Obstacle monitoring

The optional follower monitor validates its obstacle input. It is independent of
`components.live_filter.enabled`: either the R3D filter or an external ROS
producer can supply the same PointCloud2 contract. Planner startup still does
not start the follower. Offline planning needs no obstacle producer.

```yaml
path_follower:
  # Keep the other existing controller keys.
  obstacle_monitoring:
    enabled: false
    timeout_sec: 1.0
    require_transform: true
    topic: /local/filtered_obstacles
```

This is an excerpt to merge into the existing central YAML. An older YAML without
`obstacle_monitoring` uses these defaults. When the group is present, `enabled`,
`timeout_sec` and `require_transform` are required; `topic` may be omitted.
Unknown keys and a null/non-mapping group are rejected. Both switches require
actual booleans. Timeout must be numeric, finite and positive, representable
between 1 ns and the signed 64-bit nanosecond clock limit; bool, null, strings,
NaN, Inf, zero and negative values are rejected. Integer YAML spelling is
normalized to a ROS double. Direct ROS overrides must use the declared type
(e.g. `1.0`).

The four ROS parameters have the names `obstacle_monitoring.enabled`,
`obstacle_monitoring.timeout_sec`, `obstacle_monitoring.require_transform` and
`obstacle_monitoring.topic`. They are read-only after startup: edit the selected
YAML and restart `follower.launch.py` to apply changes. This avoids a partially
changed timer, topic or monitoring policy during motion. `R3D_CONFIG_DIR` and
normal installed package-share configuration work as before.

With `enabled: false`, the obstacle ROI, path/metadata validation,
Odometry/global-TF checks and goal stop remain active. Missing clouds do not add a
blockade, and the original ROS-clock control timer is retained. This
mode does not establish obstacle freshness or correct sensor-to-base geometry.
`require_transform` has no effect while monitoring is disabled.

With `enabled: true`, no movement is allowed until a complete valid current
measurement has been evaluated. Every regular command is gated, and an invalid
cloud or detected obstacle also publishes an immediate zero command through the
same publisher. All six Twist components are zero. State and reason are logged
on state transitions; there is no separate public status topic.

| State | Meaning and movement policy |
|---|---|
| DISABLED | Direct obstacle policy, without freshness/TF monitoring |
| WAITING_FOR_DATA | No successful measurement yet; zero command |
| ACTIVE | Valid current clear input; other controller conditions still apply |
| BLOCKED | Valid measurement contains an obstacle in the existing stop ROI; zero |
| STALE_DATA | Measurement age or successful-input silence exceeds timeout; zero |
| FUTURE_DATA | Measurement timestamp is later than current ROS time; zero |
| INVALID_DATA | Invalid header/layout/geometry, zero stamp or non-advancing stamp; zero |
| TF_UNAVAILABLE | Required timestamped transform missing/invalid, or foreign frame rejected; zero |
| CLOCK_ERROR | Uninitialized/discontinuous clock or changed ROS time basis; zero |

**Time:** `header.stamp` must represent the original measurement in the current
ROS time basis, be nonzero and not future-dated. Measurement age and monotonic
time since the last fully validated input must both be at most `timeout_sec`.
Equality is valid; exceeding either limit stops. Repeated or out-of-order stamps
within an epoch are rejected, so replay cannot refresh the receipt deadline.
A steady-clock timer runs monitoring at the configured control period even when
simulation time pauses. Backward/time-basis changes invalidate cached input;
a forward ROS discontinuity exceeding timeout relative to monotonic elapsed
time also invalidates it. Initialization at ROS time zero cannot grant motion;
the first fully valid measurement after clock initialization can recover.
Clock changes require new validation in the new epoch.

**Frames:** Evaluation uses the existing robot profile's `base_frame`. Input
already in that frame requires no TF lookup. With `require_transform: true`,
foreign-frame XYZ is transformed to base at the measurement stamp, with direction,
finite translation, normalized rotation and result time checked. Static TF may
legitimately have stamp zero. Lookup is nonblocking: missing/extrapolated TF
stops; adding TF alone does not reactivate an old failed sample. There is no
latest-time or identity fallback. With `require_transform: false`, only clouds
already in base are accepted; foreign frames are rejected. No TF is broadcast
by the monitor.

**Geometry:** XYZ must use metres in the declared frame. The producer must
preserve original measurement time in the same ROS time basis. The monitor
cannot detect mislabeled physical units or frames. The existing shared decoder
handles fields, numeric scalar XYZ,
offsets, strides, endian order, organized clouds and padding without changing
input bytes. A true empty cloud with valid XYZ metadata, layout, header, time
and any required TF is a valid clear measurement. Finite points outside the stop
ROI are also a valid clear result. Missing XYZ, truncated/unsupported layout,
nonfinite-only or mixed nonfinite geometry in the monitored input is invalid.
The internal filter continues selecting finite points from mixed raw input;
nonempty raw input with no finite geometry now produces no output instead of
a false fresh empty clearance. The monitor validates the supplied obstacle
message, not the physical completeness of upstream sensing.

**Recovery:** Errors revoke cached clearance. A new measurement must pass every
check and clear the existing obstacle ROI. A valid current PathWithMetadata,
matching flags, fresh valid Odometry/global TF and an unreached goal are still
required. The controller computes a new command; it does not replay an old
velocity. A path arriving during a stop replaces the current path and flags
normally and does not bypass the monitor. There is no manual-reset service or
new mode. With the filter disabled, an external publisher can recover monitoring;
without any producer an enabled monitor stays stopped.

**ROS transport:** The obstacle subscription uses SensorDataQoS (best-effort,
volatile, keep-last depth 5) and accepts both best-effort and reliable offers.
Path metadata retains reliable/transient-local/depth 1. The existing namespace
remap applies to the default obstacle topic; custom relative topics resolve in
the node namespace, and explicit absolute hardware topics remain intentional.
Publisher replacement or loss does not bypass the timeout. External publishers
must preserve measurement stamps and provide suitable base/sensor TF.

**Limits:** A zero Twist is a software command, not a demonstrated physical
emergency stop. The control period, callback execution and transport add latency;
a blocked executor, process failure or actuator queue needs independent command
watchdogs and stop facilities. The internal filter now retains height-qualified near returns by default;
Physical sensor coverage, self returns and body clearances still need deployment
validation; fresh empty output does not prove complete near-field coverage.
Cliff output handling remains external. Stair-mode transitions use the separate
coordinator described below.


## Local obstacle geometry and near-return retention

All distances below are metres. The filter evaluates incoming sensor XYZ without
TF. It requires X forward, Y lateral and Z up; sensor-Z is not automatically height
above the ground. The existing radial gate is `x*x + y*y > min_reliable_distance**2`.
Stair and cliff processing continues using that gated set with the existing
thresholds. The obstacle height range is strictly `min_height < z < max_height`
(default 0.05 to 1.0 in the input frame).

With `live_filter.retain_near_obstacles: true` (default), finite raw points
inside or exactly on the excluded radius are additionally published as obstacles
when they satisfy that height range. Near points are not suppressed by stair
classification. The far-obstacle, stair and cliff branches retain their previous
logic. No point is duplicated between near and far branches. Output remains XYZ32
with the original frame and measurement stamp; cloud point order has no contract.
No missing or physically unreliable sensor returns are reconstructed.

```yaml
live_filter:
  # Keep all other existing live_filter keys in the selected configuration.
  min_reliable_distance: 0.65
  retain_near_obstacles: true
path_follower:
  # Keep all other existing path_follower keys.
  obstacle_x_min: 0.1
  stop_distance: 0.6
  obstacle_half_width: 0.3
```

This is a partial example, not a complete replacement YAML. Omitting this optional key uses true. The key requires a boolean;
null, numbers and strings are rejected. The ROS parameter is read-only after
startup: edit your `R3D_CONFIG_DIR` copy and restart. Explicit false applies the radial exclusion to obstacle output too and can
remove near obstacles before the follower sees them. Retaining near returns may
produce additional conservative stops from valid but unwanted self/noise returns;
use an upstream calibrated self-filter, not a larger exclusion radius as a
substitute for complete obstacle coverage.

With obstacle monitoring enabled, the follower transforms XYZ to `robot.odometry.base_frame` at
the original measurement time, then stops if **any** point meets the open
rectangle `obstacle_x_min < x < stop_distance` and `abs(y) < obstacle_half_width`.
There is no additional Z test: the producer supplies classified obstacles.
`stop_distance` is an upper X coordinate from the base origin, not a circular
radius or clearance from the body front. Exact upper/lower/lateral boundaries
are excluded. XYZ32 serialization rounds decimals: a mathematical boundary must
be distinguished from its transmitted value. For example, float32(0.6) is
0.6000000238418579, while the stored ROS double limit is0.6.

With obstacle monitoring disabled, the existing follower evaluates the same rectangle directly in the
received coordinates; correct frame alignment remains the integrator's obligation.
Filter and monitor switches remain independent. With the filter off, external
publishers must supply classified obstacles and fulfill the frame/time/layout/QoS contract when monitoring is enabled.

The robot profile's offline radius, narrow radius, height and base clearance use
centimetres for PCD classification. They do not define a measured local footprint,
body-front offset, sensor transform, braking distance or turn envelope. They are
not automatically reused here. Sensor coverage, height alignment, self filtering,
body geometry, braking and actuator watchdogs need deployment-specific validation.
Cliff handling and reverse-motion protection remain external. Stair gait
coordination is described below.


## Go2W stair control

The selected robot profile owns the two route-distance margins.

```yaml
robot:
  stairs:
    approach_distance_m: 1.0
    exit_distance_m: 1.0
```

These fields belong alongside `geometry`, `velocity_limits`, `odometry` and
`topics` in the full profile. Values must be finite positive numbers in metres.
Older profiles which omit `stairs` use 1.0 m for both margins. Changing the
profile takes effect after restarting the follower launch. Inspect the effective
read-only parameters on `/r3d_stair_controller`.

Distances are measured along the 3D planned path. The first and last flagged
stair waypoints define the flight boundaries. A flag can include the lower
approach voxel adjacent to a step. Consequently the requested stop is
approximately the configured distance before the first physical step. Sensor,
controller, braking and transport effects require deployment validation.

`follower.launch.py` starts `stair_controller` and enables the follower's
`stair_control_enabled` interlock. The coordinator publishes `/stair_control`
at 20 Hz. The follower accepts movement only with a permit for the complete
current path and terrain metadata. A missing, denied, mismatched, future-dated
or more than 0.5 s old permit keeps all Twist components zero. A steady timer
also expires permits while simulation time pauses. Direct isolated
`ros2 run r3d_planner path_follower` defaults `stair_control_enabled` to false.
The follower launch enables integrated stair operation.

The sequence is as follows.

1. Start on the flat approach with a valid path, fresh Odometry and timestamped
   map TF. Hold movement and confirm normal gait through the SDK tool.
2. At `approach_distance_m` before the next planned flight, withdraw movement
   permission. Require a positive live observation within 0.75 m of the first
   flagged stair point in map coordinates. Observations need finite coordinates,
   a valid frame and timestamp, and at most 1 s timestamp/receipt age.
3. Require measured linear speed at most 0.02 m/s and angular speed at most
   0.03 rad/s continuously for 0.5 s. Request a command-publication pause and
   wait for the follower's fresh acknowledgement for this transition. The SDK
   guard reads fresh `rt/lf/sportmodestate` in DDS domain 0. After measured
   standstill, it calls `SportClient::BalanceStand()` once if mode differs from
   1 and confirms stable mode 1, zero error code and standstill.
4. Invoke the existing SDK tool with `eth0 stairs`. After its exit code 0,
   independently verify fresh mode 1, `gait_type=1`, zero error code and
   standstill through the guard. Keep cmd_vel publication paused throughout.
   Resume movement only after this final verification.
5. Follow the path in stair mode. Flights separated by a landing shorter than
   `exit_distance_m` are grouped into one traversal. A following flight already
   within the next approach range also keeps stair mode active.
6. Once the robot is at least `exit_distance_m` beyond the last flagged point,
   require a flat following path, path-relative height agreement within 0.1 m,
   height variation at most 0.03 m over at least 0.4 s, and body vertical within
   eight degrees of map vertical. The forward path check extends up to 0.5 m
   ahead, limited by the available path.
7. Hold movement, verify standstill and pause acknowledgement again, prepare
   BalanceStand, invoke `eth0 normal`, then verify mode 1 and `gait_type=0`.
   Publish `/stair_detect` with `detected: false`, then resume normal following. Only the confirmed normal-mode result clears the traversal event.

The controller estimates the base-to-path vertical offset on the initial flat
approach and keeps it through traversal. Map, Odometry and base TF must preserve
that relationship. Initialize before the first stair waypoint. While a flight
is active, replans must retain its exit geometry and stair classification.
Movement is held until a compatible path is available. Plan a landing
at least `exit_distance_m + path_follower.goal_tolerance` beyond the last stair
flag so goal stopping leaves room for the full exit margin. A goal closer to the
flight can be reached while stair mode remains active.

A live observation alone authorizes a switch only when the path confirms the
staircase. Ensure the live-filter ROI and sensor extrinsics cover the selected
approach distance. With the default approximately 0.7--1.1 m sensor-X ROI,
a substantially longer approach margin can stop the robot before the detector
can see the step. In that case extend the detection ROI consistently. Offline
step-height bounds and live sensor-Z thresholds remain separately configured.
Both sets of criteria must cover the intended staircase.

The external tool is a deployment dependency on the Jetson. Its default absolute
path is `/home/unitree/go2w_gait_switch/build/go2w_gait_switch`, with `eth0` as
the default network interface. The tool performs the BalanceStand/motion checks,
sends neutral-axis wireless-controller button sequences in DDS domain 0, and
reads the gait back from `rt/lf/sportmodestate`. Its already-active-gait shortcut
can return zero without checking BalanceStand. The independent guard therefore
runs before and after every invocation, including already-active gaits. The ROS
wrapper uses literal subprocess arguments. The total prepare/switch/verify
process timeout is 20 s.
The tool and Unitree SDK remain externally installed dependencies. The guard
uses the public [SportClient API](https://github.com/unitreerobotics/unitree_sdk2/blob/aaf69cb56c9d5ed63d8b284008ec3a8ab999bec1/include/unitree/robot/go2/sport/sport_client.hpp).

The node's startup-only parameters `sdk_executable`, `guard_executable`,
`network_interface` and `sdk_timeout_sec` configure this sequence. Launch exposes
`gait_switch_executable`, `gait_guard_executable` and `gait_network_interface`.
SDK errors, missing executables and timeouts latch `ERROR` with movement denied. Inspect `/stair_control`
for its detail, correct the cause, then explicitly retry.

```bash
ros2 service call /r3d_stair_controller/retry std_srvs/srv/Trigger '{}'
```

A retry repeats the outstanding transition after the same input and standstill
checks. Node shutdown terminates an outstanding SDK subprocess and withdraws
its permit. Status includes the last SDK-confirmed stair-mode flag. Tracking
external mode changes requires separate continuous gait feedback. Physical mode transitions and stair traversal remain unverified.


### Build the Jetson SDK guard

The guard source and standalone CMake project are installed under the planner's
`share/r3d_planner/sdk`. Build it on the Jetson against its existing Unitree C++
SDK. The example prefix matches the provided SDK installation.

```bash
r3d_share=$(ros2 pkg prefix --share r3d_planner)
cmake -S "$r3d_share/sdk" -B "$HOME/r3d_gait_guard_build" \
  -DCMAKE_PREFIX_PATH=/home/unitree/SDK_WS/install/unitree_sdk2 \
  -DCMAKE_INSTALL_PREFIX="$HOME/.local"
cmake --build "$HOME/r3d_gait_guard_build"
cmake --install "$HOME/r3d_gait_guard_build"
```

The default guard path is `/home/unitree/.local/bin/r3d_go2w_gait_guard`.
Its `prepare` operation waits for fresh, error-free standstill telemetry, calls
BalanceStand once when required, and confirms mode 1. `verify_stairs` and
`verify_normal` independently confirm the final mode, gait, error code and
standstill. Telemetry needs at least two received samples, receipt age at most
0.2 s, and continuously valid conditions for 0.5 s before preparation or 0.3 s
for confirmation. Each telemetry wait is bounded to 4 s. SDK RPC timeout is 3 s.

During preparation and switching, `/stair_control.pause_commands` requests
suppression of all follower cmd_vel messages, including zero Twist messages.
The follower echoes a fresh `/stair_command_ack` carrying the exact `path_id`
and transition `pause_id`. The coordinator waits at most 1 s for that
acknowledgement before starting a process and requires continuing acknowledgements.
This prevents its Move(0,0,0) stream from undoing BalanceStand. A lost controller
heartbeat restores zero-command publication after the normal permit timeout.
Changed paths, lost pose data, acknowledgement loss or SDK failure abort the
operation, latch ERROR and restore zero-command publication. Other velocity
publishers and driver-side watchdogs must cooperate with this pause contract.

The hardware adapter uses the external SDK only in its standalone Jetson build.
The regular ROS packages install its source and use a configured executable.
Build the adapter for the Jetson architecture against its installed SDK and
keep those runtime libraries available. Jetson compilation and physical stair
traversal remain unverified.
