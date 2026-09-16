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
With the supported `colcon build --symlink-install`, module and configuration
symlinks resolve to live source files. New robot files are read directly from
source and need no rebuild. For a copied installation, set `R3D_CONFIG_DIR`
once to the source `r3d_planner/config` directory. Without live source access,
startup fails explicitly instead of using an installed snapshot. Moving the
workspace itself requires rebuilding its installation, unlike editing YAML.

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
absolute ROS topic names; the map, odometry and base frames must be distinct.

## Central YAML

`maps.pcd_path` and `maps.map_name` resolve relative to the central config
directory, not the shell working directory. Absolute external map paths are
also accepted. Preprocessing validates the input exists; planner/map/follower
launch validates the analyzed file exists. The other map path may not exist yet.
Only PCD files are accepted. The analyzer always writes `<input>_analysed.pcd`;
keep `map_name` aligned manually. The included analyzed map is an example
artifact, not proof that it was generated using the current selected settings.

| `shared` key | Default | Unit / effect |
|---|---:|---|
| `voxel_size_cm` | 5.0 | cm; analysis voxel and graph reconstruction grid |
| `min_step_height_cm` | 5.0 | cm; largest flat connection |
| `max_step_height_cm` | 25.0 | cm; largest connectable graph step |

Voxel size and maximum step are positive; minimum step is nonnegative and
strictly below maximum step. PCD artifacts do not embed these values.

| `preprocessing` key | Default | Unit / effect |
|---|---:|---|
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
bounds. Changing settings does not fix the filter's packed-XYZ decoding or axes
assumptions. The unused legacy `cliff_dist` attribute is not a configuration key.

| `rviz_interface` key | Default | Effect |
|---|---:|---|
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
