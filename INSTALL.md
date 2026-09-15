# Installation, Build, and Startup

## Reference environment

The installation commands use:

- Ubuntu 22.04.5 LTS
- ROS 2 Humble
- Python 3.10
- `ament_python` and `colcon`

ROS 2 Humble is the supported ROS distribution. Other ROS distributions are
not supported. The complete stack has run successfully on a Unitree Go2W with
the documented TF and sensor integration.

Installation uses a native ROS 2 workspace. No Docker, rosinstall,
requirements, or launch files are provided. Sensor and robot drivers are part
of the Go2W deployment rather than this workspace.

## Required software

### ROS and system dependencies

On Ubuntu 22.04 with ROS 2 Humble, install the build tools and imported ROS
modules with:

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

The stack uses these non-ROS libraries:

| Library | Use |
|---|---|
| NumPy | Voxel, point-cloud, and geometry operations |
| SciPy (`scipy.spatial.KDTree`) | Locate the graph node nearest to a start or goal |
| NetworkX | Undirected navigation graph and Pickle serialization |
| Open3D | Read, voxelize, color, and write PCD data |
| `pickle` | Python standard library; not a separately installable dependency |

Use the Ubuntu packages above for the ROS Python environment. Mixing global pip
packages with apt-managed ROS packages can introduce version conflicts. Test a
different Open3D release in an isolated Python environment before using it with
ROS 2.

### External runtime components

The tested Go2W deployment adds these runtime components to the workspace:

- a point-cloud publisher on `/hesai_ros_driver/hesai/lidar_points` using
  `sensor_msgs/msg/PointCloud2`; `local_filter` subscribes to this Hesai topic;
- an odometry or robot-state component publishing `odom -> base_link`;
- a robot base that safely consumes `/cmd_vel`;
- optionally Nav2 when integrating
  `r3d_planner/config/r3d_planner_params.yaml`.

Install the driver, network interface, sensor IP, DDS setup, and robot command
interface as part of the Go2W runtime. Their deployment configuration is not
stored in this workspace.

## Create a workspace

Place the repository under a ROS 2 workspace's `src` directory:

Replace `<path-to-workspace>` with the absolute path of the ROS 2 workspace in
every command in this guide. Angle-bracket placeholders are not literal shell
syntax and must not be copied unchanged.

```bash
mkdir -p <path-to-workspace>/src
cd <path-to-workspace>/src
git clone <repository-url> R3D-Planner
cd <path-to-workspace>
```

For an existing checkout, place the unchanged repository below the `src`
directory of a ROS 2 workspace. Do not rename package or source directories.

## rosdep

Initialize rosdep if it has not been initialized on this machine:

```bash
sudo rosdep init
rosdep update
```

The `package.xml` files contain keys that rosdep cannot resolve
(`pickle`, `numpy`, and, depending on the rosdep database, `scipy`) while also
omitting several modules that the source imports. Therefore, an unchanged

```bash
rosdep install --from-paths src --ignore-src -r -y
```

is currently **not reproducibly successful**. After installing the apt packages
listed above, rosdep can process the remaining declared dependencies with
explicit exclusions:

```bash
cd <path-to-workspace>
rosdep install --from-paths src --ignore-src -r -y \
  --skip-keys="pickle numpy scipy"
```

The package metadata does not yet support an unmodified rosdep run. The
required exclusions are tracked in `docs/KNOWN_ISSUES.md`.

## Build

```bash
cd <path-to-workspace>
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Verify package discovery and installed executables:

```bash
colcon list --names-only
ros2 pkg executables r3d_preprocessor
ros2 pkg executables r3d_planner
```

`colcon list` must include `r3d_preprocessor` and `r3d_planner`.

### Validation status

- All 21 Python and setup files pass Python AST parsing.
- Both `package.xml` files are well-formed XML.
- `colcon` discovers both packages.
- Package-level tests: PEP257 passes in both packages and the copyright test is
  skipped. Flake8 reports 286 findings in `r3d_preprocessor` and 200 in
  `r3d_planner`.
- Running both test directories together from the repository root fails during
  collection because both packages use test-module names such as
  `test_copyright.py`.
- The isolated build on the local workstation stopped before building
  project code because its global environment contains `packaging 21.3` while
  a Setuptools entry point requires `packaging>=23.2`. The Go2W environment
  does not have this conflict and runs the stack successfully.

If the same packaging error occurs, inspect the Python environment first:

```bash
python3 -m pip check
python3 -c "import packaging; print(packaging.__version__, packaging.__file__)"
```

Prefer a clean ROS 2 Humble shell with consistent apt packages. Do not blindly
replace packages in the system Python environment.

Run the existing tests separately without producing a Pytest cache:

```bash
cd <path-to-workspace>/src/R3D-Planner/r3d_preprocessor
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest test -p no:cacheprovider

cd <path-to-workspace>/src/R3D-Planner/r3d_planner
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest test -p no:cacheprovider
```

Flake8 currently reports the known lint findings listed above.

## Prepare a map

### Variant A: color-coded PCD

```bash
source /opt/ros/humble/setup.bash
source <path-to-workspace>/install/setup.bash
ros2 run r3d_preprocessor pcd_analyser --ros-args \
  -p pcd_path:=/absolute/path/map.pcd \
  -p voxel_size_cm:=5.0 \
  -p max_step_height_cm:=25.0 \
  -p min_step_height_cm:=5.0 \
  -p min_points_per_sqm:=10.0 \
  -p min_points_per_voxel:=3 \
  -p floor_height_tolerance:=0.02 \
  -p ground_fill:=true \
  -p robot_base_clearance_cm:=10.0 \
  -p robot_narrow_radius_cm:=30.0 \
  -p robot_radius_cm:=40.0 \
  -p robot_height_cm:=80.0 \
  -p analysis_grid_size_cm:=20.0 \
  -p cluster_gap_threshold_cm:=20.0 \
  -p fill_plane_iterations:=2 \
  -p fill_plane_search_radius:=2 \
  -p fill_plane_min_neighbors:=4
```

The one-shot node writes `/absolute/path/map_analysed.pcd` and does not
overwrite the input. Later, pass the same voxel size and minimum/maximum step
heights to the planner because the PCD does not expose those values as planner-
readable metadata.

### Variant B: Pickle graph

Use the same parameter set with `pcd_to_graph` to generate a NetworkX graph:

```bash
ros2 run r3d_preprocessor pcd_to_graph --ros-args \
  -p pcd_path:=/absolute/path/map.pcd \
  -p voxel_size_cm:=5.0 \
  -p min_step_height_cm:=5.0 \
  -p max_step_height_cm:=25.0
```

The output is written beside the PCD with a descriptive `nav_graph_*.pkl`
filename. It contains the graph, origin, voxel size, robot radius, and obstacle
voxels. Load Pickle files only from trusted sources.

## Startup

There are no launch files. Run each command in a separate terminal after
sourcing ROS and the workspace.

### Map and planning test without hardware

1. Publish the map:

   ```bash
   ros2 run r3d_preprocessor pcd_server --ros-args \
     -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd
   ```

2. Start exactly one planner:

   ```bash
   ros2 run r3d_planner pcd_path_planner --ros-args \
     -p map_name:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd \
     -p voxel_size_cm:=5.0 \
     -p min_step_height_cm:=5.0 \
     -p max_step_height_cm:=25.0
   ```

3. Start the test TF, RViz interface, and RViz:

   ```bash
   ros2 run r3d_planner path_test
   ros2 run r3d_planner rviz_interface
   rviz2
   ```

4. Set the RViz Fixed Frame to `map`. First use **Publish Point** to select a
   3D point, then set the initial orientation near the same XY position using
   **2D Pose Estimate**. For a goal, select its height with **Publish Point**
   and then set its pose with **2D Goal Pose**.

Alternatively, send an action directly using the example in
`r3d_planner/points.txt`. Start and goal coordinates must already be expressed
in map coordinates.

### Pickle variant

Run this instead of `pcd_path_planner`:

```bash
ros2 run r3d_planner global_planner --ros-args \
  -p map_name:=/absolute/path/nav_graph_....pkl
```

Optionally visualize the same graph:

```bash
ros2 run r3d_preprocessor voxel_map_publisher --ros-args \
  -p graph_path:=/absolute/path/nav_graph_....pkl
```

### Unitree Go2W operation

The Go2W integration has been tested with the expected LiDAR topic, TF tree,
and command interface. Recheck them after changing the driver, localization, or
robot interface:

```bash
ros2 topic info /hesai_ros_driver/hesai/lidar_points -v
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic info /cmd_vel -v
```

The intended process order is:

1. external LiDAR driver and odometry/robot state;
2. `pcd_server`, optionally for visualization;
3. exactly one of `global_planner` or `pcd_path_planner`;
4. `local_filter`;
5. `rviz_interface` or another action client;
6. `path_follower` **only after motion safety has been approved**.

```bash
ros2 run r3d_planner local_filter
ros2 run r3d_planner rviz_interface
ros2 run r3d_planner path_follower
```

`path_follower` publishes directly to `/cmd_vel` at 10 Hz. It considers
`/local/filtered_obstacles` but not `/local/cliff_virtual_wall`. Emergency stop,
watchdog, and command multiplexing belong to the external Go2W safety chain.

## Verify the ROS graph

Inspect the ROS graph without enabling motors:

```bash
ros2 node list
ros2 action list -t
ros2 topic list -t
ros2 service list -t
ros2 run tf2_tools view_frames
```

For `pcd_server`, `/map_pointcloud` should appear as
`sensor_msgs/msg/PointCloud2` with `TRANSIENT_LOCAL` durability. For a planner,
`/compute_path_to_pose` should appear as
`nav2_msgs/action/ComputePathToPose`.

## Nav2 configuration fragment

`setup.py` installs `r3d_planner/config/r3d_planner_params.yaml`, but no launch
file loads it. The file contains partial `local_costmap` and `controller_server`
sections with placeholder comments. Integrate it into a complete external Nav2
bringup and add the required plugins and launch configuration before use. It is
not a standalone Nav2 configuration.

## Troubleshooting

- **Map not found:** Always pass an absolute `map_name` or `pcd_path`. The
  `maps` directory is currently not installed into the package share.
- **No map in RViz:** Use Fixed Frame `map` and set PointCloud2 durability to
  `Transient Local`.
- **Planner reports an empty or colorless PCD:** `pcd_path_planner` requires an
  RGB-classified output from `pcd_analyser`.
- **No `map -> base_link`:** Check `map -> odom` and `odom -> base_link`
  independently. Use `path_test` only without real odometry.
- **No action response:** Confirm that exactly one global planner is running
  and that it loaded the map successfully.
- **rosdep errors:** Install the documented apt dependencies and use the
  explicit `--skip-keys` list.
- **Incorrect LiDAR filter output:** Verify the PointCloud2 field layout and
  sensor axes against the assumptions documented in the architecture guide.
