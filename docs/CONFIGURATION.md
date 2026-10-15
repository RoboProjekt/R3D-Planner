# Runtime configuration reference

## Ownership and precedence

`r3d_planner/config/planner_config.yaml` is the central entry point. Its
`robot_config` path is relative to that directory and must stay inside it.
`robots/Go2W.yaml` owns geometry and robot interfaces; central sections own
algorithm settings. `shared` is forwarded to both analysis and reconstruction.
There is no merge precedence between competing definitions: the schema rejects
misplaced, missing, unknown and duplicate keys. Launch parameters override the
deliberate standalone-node defaults; defaults never override YAML.

The loader reads both files anew on each launch and logs their resolved paths.
With optional developer `colcon build --symlink-install`, module and configuration
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
| `odometry.topic` | `/lidar_odometry` | Standard `nav_msgs/msg/Odometry` input |
| `odometry.odom_frame` | `odom` | Required Odometry header frame |
| `odometry.base_frame` | `base_link` | Required Odometry child frame |
| `topics.pointcloud` | `/hesai_ros_driver/hesai/lidar_points` | Live Filter sensor input |
| `topics.cmd_vel` | `/cmd_vel` | Explicit follower command output |

The existing centimeter parameter names are retained rather than introducing
parallel height/tight/safety names with different units. The loader maps
`odometry.topic` to the ROS parameter `odometry_topic` and the frame keys to
`odom_frame` and `base_frame`. Geometry is forwarded to the preprocessor and
planner. Only the preprocessor uses it for collision classification; the planner
does not reinterpret existing PCD colors using new dimensions.

Height and radii must be positive; narrow radius must not exceed normal radius.
Base clearance is nonnegative and smaller than height. Topics must be valid
valid relative or absolute ROS topic names; the map, odometry and base frames must be distinct.

## Central YAML

`maps.pcd_path` and `maps.map_name` resolve relative to the central config
directory, not the shell working directory. Absolute external map paths are
also accepted. Preprocessing validates the input exists; planner/map/follower
launch validates the analyzed file exists. The other map path may not exist yet.
V4 contains no bundled PCD maps. Both shipped map values are empty. Set the
selected path to your own suitable PCD before launch; preprocessing requires
`pcd_path`, while planner/map/follower require `map_name`. The unused value may
remain empty or refer to a future output. Missing, non-PCD and directory inputs
fail with the selected key and resolved path; no old example fallback exists.
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

No PCD is needed to install either package. Data ownership/permission remains
the user's responsibility; synthetic test inputs are temporary fixtures.

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
| `min_reliable_distance` | 0.65 | m; discard XY returns at/below this radius |
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
the existing sensor-axis assumptions. The unused legacy `cliff_dist` attribute is not a configuration key.

| `rviz_interface` key | Default | Effect |
|---|---:|---|
| `action_server_timeout_sec` | 1.0 | s; positive bounded action-server wait, optional for older YAML |
| `match_radius` | 0.8 | m; maximum XY distance between point and pose selections |
| `publish_map_odom` | true | Retain legacy static calibration TF; false for external global localization |

When calibration TF is disabled, goal selection requires no initial calibration.
The planner obtains the online start from Odometry, not from an RViz TF lookup.
The reset service changes only calibration state; it does not remove an existing
static transform. Legacy calibration still assumes the odometric base pose is
identity. Use an external global localizer if this assumption is not satisfied.

| `path_follower` key | Default | Unit / effect |
|---|---:|---|
| `lookahead_distance` | 0.5 | m; target selection distance |
| `max_linear_speed` | 0.35 | m/s; maximum forward speed |
| `max_angular_speed` | 0.6 | rad/s; normal steering limit |
| `stop_distance` | 0.6 | m; obstacle corridor upper X bound |
| `goal_tolerance` | 0.2 | m; XY goal completion distance |
| `control_period_sec` | 0.1 | s; control timer period |
| `obstacle_x_min`, `obstacle_half_width` | 0.1, 0.3 | m; obstacle corridor lower X bound / half-width |
| `max_angular_speed_narrow` | 0.2 | rad/s; narrow steering limit |
| `angle_threshold` | 0.5 | rad; turn/slow-forward boundary |
| `steering_gain` | 1.5 | 1/s; angular error to yaw rate |
| `narrow_speed_factor`, `turning_speed_factor` | 0.4, 0.3 | dimensionless factors, >0 and <=1 |

Controller settings are general tuning values, but must be checked against the
selected robot's limits. Missing/stale Odometry or missing global TF produces a
zero Twist; this does not replace an external command watchdog.

## Add or select another robot

1. Copy `robots/Go2W.yaml` to a new file under the same directory.
2. Set its name, dimensions, odometry topic/frames, cloud and command topics.
3. Change `robot_config` in the central YAML to the new relative filename.
4. Recheck sensor axes, PointCloud2 binary layout and controller safety limits.
5. Restart preprocessing to regenerate the map, then restart the planner.

For example, selecting `odometry.topic: /kiss/odometry` needs no source change
if messages follow the configured base/odom frame contract and global localization
supplies `map -> odom`. A source describing a LiDAR frame rather than the base
requires an external frame adapter/extrinsic conversion, not merely a topic rename.
YAML selection is not a claim of physical support for a new platform.

## Developer overrides

Normal operation uses the launch files. Direct `ros2 run` remains available for
isolated debugging with ordinary ROS parameter overrides, but does not load
the central YAML automatically. Node defaults preserve standalone compatibility;
they are not a second normal configuration workflow. Use the logged source
paths and `ros2 param get /global_graph_planner odometry_topic` to confirm the
effective configuration.


## M01 path metadata and M02 monitoring

The existing narrow speed/steering parameters now use `PathWithMetadata.narrow`
at the target waypoint index. They never inspect quaternion fields. Build all
three packages and upgrade planner/follower together; Path/header/flags are
validated as one message. Standard `/global_path` remains geometric `nav_msgs/Path`.
M01 remains independent of the implemented optional M02 monitor. The accepted
YAML group is `obstacle_monitoring`; the earlier unimplemented proposal name
`obstacle_monitor` is not an alias. The local filter remains optional.
See the complete M02 contract below.


## Namespace and QoS contract

Each launch accepts `namespace:=robot_a`; the empty default preserves existing
root names. Internal absolute topic literals are consistently remapped to
namespace-relative names, including global_path_metadata and the planning action.
Explicit absolute robot topics remain global; relative robot topics inherit the
node namespace. Frame IDs and /tf ownership remain explicitly configured, with
no automatic TF prefix or new broadcaster.

Live PointCloud2 input uses SensorDataQoS (best-effort, volatile, keep-last5),
accepting both reliable and best-effort producers. Local outputs remain reliable,
volatile, depth10; Odometry remains SensorDataQoS, map publication reliable
transient-local/depth1, metadata reliable transient-local/depth1. Deadline/lifespan
and liveliness settings retain library defaults; no real-time guarantee is made.
RViz rejects foreign-frame/nonfinite/invalid-quaternion selections; valid
orientations are normalized. The new positive action timeout defaults to1s even
when omitted from older YAML. Obstacle monitoring is separately configured below; it does not depend on RViz.


## Obstacle monitoring (M02, Humble)

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

With `enabled: false`, the existing obstacle ROI, path/metadata validation,
Odometry/global-TF checks and goal stop remain active. No new missing-cloud
blockade is added, and the original ROS-clock control timer is retained. This
mode does not establish obstacle freshness or correct sensor-to-base geometry.
`require_transform` has no effect on this legacy mode.

With `enabled: true`, no movement is allowed until a complete valid current
measurement has been evaluated. Every regular command is gated, and an invalid
cloud or detected obstacle also publishes an immediate zero command through the
same publisher. All six Twist components are zero. State and reason are logged
on state transitions; no new public status topic is introduced.

| State | Meaning and movement policy |
|---|---|
| DISABLED | Legacy obstacle policy, without monitoring guarantees |
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
watchdogs and stop facilities. The internal filter's default 0.65 m exclusion
and the follower's 0.6 m stop bound still need deployment-specific geometric
reconciliation; fresh empty output does not prove complete near-field coverage.
Cliff/stair outputs are still not internal follower stop inputs. No thresholds,
new navigation algorithm, hardware driver or safety certification were added.
