# R3D Navigation Stack Architecture

## System boundary

R3D-Planner separates map processing, global planning, local point-cloud
filtering, RViz input, and path following into ROS 2 nodes. The complete stack
has been integrated and tested on a Unitree Go2W. The Go2W runtime also
supplies:

- 3D LiDAR driver and sensor calibration;
- odometry or state estimation publishing `odom -> base_link`;
- robot hardware interface consuming `/cmd_vel`;
- optional Nav2 bringup and costmap/controller plugins;
- process supervision and safety-rated shutdown.

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

`r3d_planner` looks up `r3d_preprocessor` at runtime through
`get_package_share_directory('r3d_preprocessor')`, but does not declare that
package dependency in `package.xml`. In addition, `r3d_preprocessor/setup.py`
does not install `maps/`, so the constructed default map directory is unusable.
Pass map paths explicitly.

### Included data and configuration

| File | Content |
|---|---|
| `r3d_preprocessor/maps/voxel_05_minhits_7.pcd` | Binary PCD v0.7 with 602,619 points and XYZ, intensity, normal, and curvature fields (about 19 MB) |
| `r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd` | Binary PCD v0.7 with 556,586 XYZ/RGB-classified points (about 8.5 MB) |
| `r3d_planner/config/r3d_planner_params.yaml` | Incomplete Nav2 costmap/MPPI configuration fragment |
| `r3d_planner/points.txt` | Site-specific action CLI example and example waypoints |

Each package also contains the standard Ament Python resource file and three
template tests for copyright, Flake8, and PEP257. There is no map metadata file,
custom interface package, or launch configuration.

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
must be supplied separately and must match preprocessing.

## Global planning

The `pcd_path_planner` executable starts node `global_graph_planner` and serves
the `compute_path_to_pose` action:

1. Use a SciPy KDTree to map action start and goal positions to nearest graph
   nodes.
2. Run A* on the weighted NetworkX graph.
3. Publish `nav_msgs/msg/Path` on `/global_path` and return it in the action
   result.
4. Publish a `visualization_msgs/msg/Marker` on `/planned_path`.

The planner publishes a `LINE_STRIP`. Each output uses the goal request's frame
string without checking or transforming coordinates.

Narrow-area metadata is encoded in `Path.poses[*].pose.orientation.z` (`1.0`
for `narrow`, otherwise `0.0`) while `orientation.w` is always `1.0`. This is an
internal protocol for `path_follower`, not a generally valid pose quaternion.

## Local perception

`obstacle_cliff_filter` assumes X forward, Y lateral, and Z upward:

```text
/hesai_ros_driver/hesai/lidar_points
        |
        +-> remove dead zone at radius <= 0.65 m
        +-> step ROI and height threshold -> /stair_detect
        +-> obstacle height filter        -> /local/filtered_obstacles
        +-> missing floor points ahead    -> /local/cliff_virtual_wall
```

Output clouds retain the incoming header and frame; no TF transform is applied.
All thresholds are Python constants rather than ROS parameters. When a step is
detected, low points in its ROI are removed from the obstacle cloud. Fewer than
30 floor points between X=0.7 and 1.2 m causes a virtual wall at X=0.7 m.

## RViz interaction and TF

```text
/clicked_point + /initialpose -> XY match within 0.8 m -> static map -> odom
/clicked_point + /goal_pose   -> XY match within 0.8 m
                              -> query map -> base_link
                              -> /compute_path_to_pose action request
```

The first 3D point supplies Z, while the nearby initial pose supplies
orientation. After calibration, the node publishes static `map -> odom`.
Subsequent point/goal pairs create action requests with the current TF position
as start and the selected 3D point as goal.

`/recalibrate_pose` (`std_srvs/srv/Trigger`) only resets internal calibration
state. For tests, `path_test` can publish static identity `odom -> base_link`.

Intended TF tree:

```text
map
 └── odom            rviz_interface (StaticTransformBroadcaster)
      └── base_link  external odometry, or path_test for tests only
```

The tested Go2W integration uses one publisher for `map -> odom`, supplies a
time-correct `odom -> base_link`, and matches the assumed LiDAR orientation and
`map` coordinates. Recheck these constraints after changing localization,
odometry, or the sensor installation.

## Path following

`r3d_path_follower` is a simple 2D lookahead controller:

1. Receive `/global_path`.
2. Check `/local/filtered_obstacles` for points 0.1–0.6 m forward and ±0.3 m
   laterally.
3. Query the XY pose and yaw of `base_link` in `map`.
4. Select a path point at least 0.5 m ahead.
5. Reduce speed and turning in narrow areas; otherwise command at most 0.35 m/s
   and 0.6 rad/s.
6. Publish `geometry_msgs/msg/Twist` to `/cmd_vel` every 0.1 s.

The controller does not directly process path Z, `/stair_detect`, or the cliff
wall. It completes a path at 0.2 m XY distance from the goal. Values are
hard-coded.

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
| `/map_pointcloud` | `sensor_msgs/msg/PointCloud2` | `pcd_server` | external/RViz | depth 1, transient-local; frame `map` |
| `/planned_path` | `visualization_msgs/msg/Marker` | `pcd_path_planner` | external/RViz | depth 10 |
| `/global_path` | `nav_msgs/msg/Path` | `pcd_path_planner` | `path_follower` | depth 10 |
| `/hesai_ros_driver/hesai/lidar_points` | `sensor_msgs/msg/PointCloud2` | external driver | `local_filter` | depth 10 |
| `/local/filtered_obstacles` | `sensor_msgs/msg/PointCloud2` | `local_filter` | `path_follower`, optional Nav2 | depth 10; retains input header |
| `/local/cliff_virtual_wall` | `sensor_msgs/msg/PointCloud2` | `local_filter` | none internally | depth 10 |
| `/stair_detect` | `geometry_msgs/msg/PointStamped` | `local_filter` | none internally | sent only when a step is detected |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `path_follower` | external base | 10 Hz control output |
| `/clicked_point` | `geometry_msgs/msg/PointStamped` | RViz/external | `rviz_interface` | 3D height point |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | RViz/external | `rviz_interface` | initial calibration pose |
| `/goal_pose` | `geometry_msgs/msg/PoseStamped` | RViz/external | `rviz_interface` | goal pose |

No topic remappings are defined.

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
| `floor_height_tolerance` | 0.02 | m | Floor-cluster Z tolerance |
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
| `pcd_path_planner` | `map_dir` | `<share/r3d_preprocessor>/maps`, fallback `/tmp` | Base directory for relative names |
| `pcd_path_planner` | `map_name` | `map_analysed.pcd` | Analyzed PCD filename/path |
| `pcd_path_planner` | `voxel_size_cm` | 5.0 | Reconstruction grid size |
| `pcd_path_planner` | `min_step_height_cm` | 5.0 | Flat/step boundary |
| `pcd_path_planner` | `max_step_height_cm` | 25.0 | Maximum step height |

`local_filter`, `path_follower`, and `rviz_interface` declare no application
ROS parameters; their operating values are hard-coded.

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

Both packages install Python modules, their Ament resource index entry, and
`package.xml`. `r3d_planner` also installs `config/*.yaml`.
`r3d_preprocessor` explicitly does not install `maps/`. No libraries, headers,
launch files, or custom interfaces are built. See [../INSTALL.md](../INSTALL.md)
for commands.
