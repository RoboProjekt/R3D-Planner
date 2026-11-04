# Installation and startup

## Requirements

- Ubuntu 22.04 Jammy, amd64
- ROS 2 Humble with its system Python 3.10
- `python3-colcon-common-extensions` and `python3-rosdep`
- Your own PCD map; no maps are bundled

Use the ROS system environment rather than a Conda interpreter or unrelated
workspace overlay. Runtime dependencies include Open3D, NetworkX, NumPy, SciPy,
PyYAML, ROS message packages, Nav2 action definitions and TF2. Resolve them through
rosdep; a parallel global pip installation is not required. RViz is optional.

## Create and build a workspace

Install ROS 2 Humble before following these commands. The example workspace is
`$HOME/r3d_ws`; change it consistently if you use another location.

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions python3-rosdep
mkdir -p "$HOME/r3d_ws/src"
git clone --branch main https://github.com/RoboProjekt/R3D-Planner.git \
  "$HOME/r3d_ws/src/R3D-Planner"
cd "$HOME/r3d_ws"
source /opt/ros/humble/setup.bash
export PYTHONNOUSERSITE=1
```

Initialize rosdep only if it has not already been initialized on this machine:

```bash
sudo rosdep init
```

Install dependencies, build all three packages and source the result:

```bash
cd "$HOME/r3d_ws"
rosdep update --rosdistro humble
rosdep install --from-paths src/R3D-Planner \
  --ignore-src --rosdistro humble --os=ubuntu:jammy -y
rosdep check --from-paths src/R3D-Planner \
  --ignore-src --rosdistro humble --os=ubuntu:jammy
colcon build --packages-up-to r3d_planner
source install/setup.bash
```

Source ROS and the workspace in every new terminal:

```bash
source /opt/ros/humble/setup.bash
source "$HOME/r3d_ws/install/setup.bash"
```

Check package and executable discovery:

```bash
ros2 pkg prefix r3d_interfaces
ros2 pkg executables r3d_preprocessor
ros2 pkg executables r3d_planner
```

## Configure an installed workspace

Copy the installed templates into a user-owned directory:

```bash
r3d_share=$(ros2 pkg prefix --share r3d_planner)
mkdir -p "$HOME/.config/r3d_planner"
cp "$r3d_share/config/planner_config.yaml" "$HOME/.config/r3d_planner/"
cp -r "$r3d_share/config/robots" "$HOME/.config/r3d_planner/"
export R3D_CONFIG_DIR="$HOME/.config/r3d_planner"
```

Set `R3D_CONFIG_DIR` in each terminal that starts an R3D launch. Edit the copied
full YAML, retaining all required sections. At minimum, configure:

- `maps.pcd_path`: the PCD input for preprocessing
- `preprocessing.output_dir`: where the classified file is written
- `maps.map_name`: the resulting `<input-name>_analysed.pcd`
- `robot_config`: the relative path to the selected robot profile

Relative data paths resolve against the central YAML directory; absolute and
`~` data paths are accepted. The robot profile path must be relative and stay
inside that configuration directory. See [CONFIGURATION.md](CONFIGURATION.md)
for required robot fields, velocity settings, units and validation.

An optional `colcon build --symlink-install --packages-up-to r3d_planner` reads
configuration from the source tree. User-owned configuration works with either
installation type. YAML edits require restarting the affected launch; they do
not require rebuilding. Rebuild to refresh copied installed templates or after
changing code. Moving the workspace requires rebuilding its installation.

## Process and display a map

```bash
ros2 launch r3d_planner preprocessor.launch.py
```

The analyzer writes `<input-name>_analysed.pcd` and exits. With an empty
`output_dir`, it uses `$XDG_DATA_HOME/r3d_preprocessor` when that environment
variable is absolute, otherwise `~/.local/share/r3d_preprocessor`. Existing
outputs, including symlinks, are rejected. Select another directory to retain
multiple analyses. Set `maps.map_name` to the produced file.

For optional visualization, start these in separate terminals:

```bash
ros2 launch r3d_planner map.launch.py
```

```bash
rviz2
```

Use fixed frame `map`, PointCloud2 `/map_pointcloud`, Transient Local durability
and RGB8 coloring in RViz.

## Start planning

```bash
ros2 launch r3d_planner planner.launch.py
```

The planner always starts. The central `components.live_filter.enabled` and
`components.rviz_interface.enabled` switches independently control the other
two nodes. Disable both for offline explicit-start planning. See the
[README action example](../README.md#plan-a-path).

For online planning, supply external standard `nav_msgs/msg/Odometry`, dynamic
`odom -> base_link` and global `map -> odom` TF with the configured frame names.
The LiDAR driver and sensor-to-base transform are also external. A TF-only
`path_test` node does not supply the required Odometry.

Use exactly one publisher for `map -> odom`. With an external global localizer,
set `rviz_interface.publish_map_odom: false`. Otherwise the RViz interface's
initial calibration pairs Publish Point and 2D Pose Estimate; subsequent goals
pair Publish Point and 2D Goal Pose. See [ARCHITECTURE.md](ARCHITECTURE.md).

Each launch accepts an optional namespace, for example:

```bash
ros2 launch r3d_planner planner.launch.py namespace:=robot_a
```

Absolute robot topics and TF frame IDs are not automatically prefixed.

## Start the follower separately

```bash
ros2 launch r3d_planner follower.launch.py
```

The planner launch never starts this motion-producing node automatically.
Configure robot interfaces, velocity limits, obstacle input and independent
watchdog/stop facilities before hardware use. The follower is planar and does
not directly stop from cliff or stair outputs. Optional obstacle monitoring is
configured separately from the local filter. See [KNOWN_ISSUES.md](KNOWN_ISSUES.md).

## Inspect the running system

```bash
ros2 node list
ros2 action info /compute_path_to_pose
ros2 param get /global_graph_planner odometry_topic
ros2 topic info /lidar_odometry -v
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_link
```

Adjust names for your namespace and robot profile. Optional package tests run
separately through colcon:

```bash
cd "$HOME/r3d_ws"
colcon test --packages-up-to r3d_planner
colcon test-result --verbose
```

For configuration errors, missing inputs and integration constraints, see
[Known limitations and troubleshooting](KNOWN_ISSUES.md).
