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

Installation uses a native ROS 2 workspace. No Docker, rosinstall or requirements
files are provided. ROS launch entry points are installed by `r3d_planner`.
Sensor and robot drivers are part
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
  python3-yaml \
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
  ros-humble-rviz2 \
  ros-humble-launch \
  ros-humble-launch-ros
```

The stack uses these non-ROS libraries:

| Library | Use |
|---|---|
| NumPy | Voxel, point-cloud, and geometry operations |
| SciPy (`scipy.spatial.KDTree`) | Locate the graph node nearest to a start or goal |
| NetworkX | In-memory navigation graph reconstructed from the analyzed PCD |
| Open3D | Read, voxelize, color, and write PCD data |

Use the Ubuntu packages above for the ROS Python environment. Mixing global pip
packages with apt-managed ROS packages can introduce version conflicts. Test a
different Open3D release in an isolated Python environment before using it with
ROS 2.

### External runtime components

The tested Go2W deployment adds these runtime components to the workspace:

- a point-cloud publisher on `/hesai_ros_driver/hesai/lidar_points` using
  `sensor_msgs/msg/PointCloud2`; `local_filter` subscribes to this Hesai topic;
- a source publishing `nav_msgs/msg/Odometry` on the robot-configured topic
  (default `/lidar_odometry`) and `odom -> base_link`;
- global localization supplying `map -> odom`, or the legacy RViz calibration;
- a robot base that safely consumes `/cmd_vel`;
- optionally Nav2 when integrating
  `r3d_planner/config/r3d_planner_params.yaml`.

Install the driver, network interface, sensor IP, DDS setup, and robot command
interface as part of the Go2W runtime. Their deployment configuration is not
stored in this workspace.

The tested Go2W deployment uses the following integration contract. Treat the
concrete network and device values as deployment examples,
not portable defaults:

| Component | Reference contract |
|---|---|
| Hesai driver | `/hesai_ros_driver/hesai/lidar_points`, `sensor_msgs/msg/PointCloud2`, frame `hesai_lidar_link` |
| Hesai device | address `192.168.123.20`, UDP port 2368, `/dev/ttyUSB0`, `/dev/ttyUSB1`, correction file `<path-to-hesai-correction-file>` |
| Robot IMU adapter | publishes `/imu/data`, `/imu/accel`, and `/imu/gyro` in `imu_link` |
| LiDAR odometry | external source supplies Odometry and dynamic `odom -> base_link`; the historical deployment used `scanmatcher_node` |
| Sensor TF | reference startup uses `base_link -> hesai_lidar_link` with translation `(0.1384, 0, 0.1284)` and positional Euler arguments `(1.5708, 0, 0)` |
| Robot command adapter | starts with `RecoveryStand`, waits two seconds, requests `BalanceStand`, then subscribes to `/cmd_vel` and forwards X/Y/yaw velocity to Unitree `SportClient::Move` |

The reference CMake target is named `go2w_driver`, while some later reference
scripts invoke `go2w_cmd_vel`. Confirm the executable actually installed on the
robot before starting the command adapter:

```bash
ros2 pkg executables unitree_ros2_example | grep go2w
```

Starting that adapter can change the robot's physical posture before any
`/cmd_vel` message arrives. Secure the robot and approve motion readiness before
launching it.

The reference also contains differing `eth0`/`eno1` and ROS domain 0/10
examples. Use the values validated for the deployed Go2W; every process that
must communicate must use compatible DDS/domain settings.

## Create a workspace

Place the repository under a ROS 2 workspace's `src` directory:

Replace `<path-to-workspace>` with the absolute path of the ROS 2 workspace in
every command in this guide. Angle-bracket placeholders are not literal shell
syntax and must not be copied unchanged.

```bash
mkdir -p <path-to-workspace>/src
cd <path-to-workspace>/src
git clone git@github.com:RoboProjekt/R3D-Planner.git R3D-Planner
cd R3D-Planner
git checkout V3
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
(`numpy` and, depending on the rosdep database, `scipy`) while also
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
  --skip-keys="numpy scipy"
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

## Runtime configuration

Edit `<path-to-workspace>/src/R3D-Planner/r3d_planner/config/planner_config.yaml`.
Its `robot_config: robots/Go2W.yaml` selects the dedicated robot configuration.
Set `maps.pcd_path` and `maps.map_name`; relative paths resolve against this
config directory, not the shell working directory. Set general preprocessing,
graph, filtering and controller tuning in the central YAML and robot dimensions,
odometry frames/topic and hardware topics in the robot YAML.

Use `--symlink-install` for the initial build. Runtime reads resolve to live
source files; edits and newly added robot YAMLs need only launch restart, without
build or re-sourcing. For a copied install, set `R3D_CONFIG_DIR` once to the
live source config directory. Startup refuses stale installed copies.
See [configuration reference](docs/CONFIGURATION.md) for all parameters.

## Prepare and inspect a map

```bash
ros2 launch r3d_planner preprocessor.launch.py
```

The one-shot analyzer writes `<input-name>_analysed.pcd` beside the input,
overwriting any previous output of that name. It does not overwrite the input.
Set `maps.map_name` to this output. Regenerate it whenever geometry or
preprocessing/shared settings change. The analyzed PCD contains RGB classes,
not configuration metadata; retain the generating settings with it.

Optional visualization:

```bash
ros2 launch r3d_planner map.launch.py
rviz2
```

Use Fixed Frame `map`, PointCloud2 `/map_pointcloud`, Transient Local
durability and RGB8 colors.

## Startup

Source ROS and the workspace once per terminal, then:

```bash
ros2 launch r3d_planner planner.launch.py
```

Planner startup always starts `pcd_path_planner`. Central boolean keys
`components.live_filter.enabled` and `components.rviz_interface.enabled`
independently start their respective nodes; both default to true. All four
combinations work. The RViz GUI and hardware drivers are separate.

### Offline test without hardware

Set both component switches to false and send an explicit start/goal with
`use_start: true` using the [README example](README.md#offline-planning)
or `r3d_planner/points.txt`. Both pose headers must use the configured map
frame. No TF or Odometry is needed for explicit-start requests.
`path_test` remains a static TF-only test helper; it does not provide the
Odometry required by online planning or the RViz goal workflow.

### Online integration

The odometry implementation is external. The planner uses only standard
`nav_msgs/msg/Odometry` and TF2, with no direct SLAM dependency.
The separate planned scanmatcher-based LiDAR-odometry fork is not implemented
or bundled here.

The selected robot YAML supplies:

- `odometry.topic`: default `/lidar_odometry`;
- `odometry.odom_frame`: required header frame `odom`;
- `odometry.base_frame`: required child frame `base_link`.

Odometry messages need current timestamps and valid base poses. The external
source owns only `odom -> base_link`; global localization owns `map -> odom`.
The planner transforms the received pose into map coordinates at its timestamp.
Requests with `use_start: false` abort on missing, invalid, future-dated or
stale odometry or unavailable global TF.

Recommended order:

1. external sensor driver, standard odometry source and sensor TF;
2. global localization, or RViz initial calibration;
3. planner launch with desired Live Filter/RViz switches;
4. optional map launch and RViz GUI;
5. explicit follower launch only after independent motion-safety approval.

When an external global localizer owns `map -> odom`, set
`rviz_interface.publish_map_odom: false`. The RViz interface then accepts
Publish Point / 2D Goal Pose pairs without first publishing calibration TF.
Otherwise retain the original Publish Point / 2D Pose Estimate calibration
workflow, followed by goal pairs. That legacy calibration assumes an identity
odom base pose and is not a general global localizer.

```bash
ros2 service call /recalibrate_pose std_srvs/srv/Trigger "{}"
```

The reset changes calibration state, not TF ownership or an already published
static transform.

### Explicit motion startup

```bash
ros2 launch r3d_planner follower.launch.py
```

This launch is never included by planner startup. It applies the central
controller tuning and selected robot's Odometry/command topic. Loss of pose input
produces zero velocity, but the controller ignores path Z and does not consume
cliff or stair outputs. The external Go2W adapter directly forwards commands
and can change posture during startup. Validate watchdogs, arbitration, emergency
stop, sensor freshness and cliff handling independently before motion.

## Verification

Replace topic/frame examples below if the selected robot changes them:

```bash
ros2 node list
ros2 action info /compute_path_to_pose
ros2 param get /global_graph_planner robot_height_cm
ros2 param get /global_graph_planner robot_narrow_radius_cm
ros2 param get /global_graph_planner robot_radius_cm
ros2 param get /global_graph_planner odometry_topic
ros2 param get /global_graph_planner voxel_size_cm
ros2 topic info /lidar_odometry -v
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_link
```

To check reload, change a YAML value, stop and restart the same launch in the
same terminal, then query it again. Do not run build or source in between.
Processing is one-shot: its parameters can be inspected during processing or
with the constructor-level integration test.

After a sourced build, run focused non-motion tests in a local isolated domain:

```bash
cd <path-to-workspace>/src/R3D-Planner
ROS_DOMAIN_ID=83 ROS_LOCALHOST_ONLY=1 RMW_IMPLEMENTATION=rmw_fastrtps_cpp python3 -m pytest \
  r3d_planner/test/test_configuration.py -p no:cacheprovider
```

These tests use temporary PCD/config files, publish synthetic Odometry, exercise
action start selection and restart actual planner launches for all four
component combinations. No hardware driver or motion follower is launched.
The complete original Go2W system is tested; the V3 refactor requires deployment
regression testing before motion. Existing template Flake8 tests still report
legacy lint failures. Run package test directories separately to avoid their
duplicate template module names.

## Troubleshooting

- **Configuration rejected:** Check the logged paths and exact key names in
  [CONFIGURATION.md](docs/CONFIGURATION.md). Strings are not booleans.
- **Live source unavailable:** Use the supported symlink build or configure
  `R3D_CONFIG_DIR` once; do not edit an unnoticed install snapshot.
- **Missing map:** Paths are relative to the central config directory; generate
  the analyzed output and align `map_name`.
- **No online start:** Confirm Odometry topic, frame IDs, timestamps and age
  limit, then `map -> odom` at the message timestamp. TF alone is insufficient.
- **TF conflict:** Disable RViz calibration TF when global localization owns it.
- **Filter output wrong:** Check the sensor's packed-XYZ binary layout and axes;
  these assumptions remain unchanged.
- **Python warnings/build errors:** Use the ROS system Python and consistent
  dependencies. The local workstation previously had a packaging conflict;
  the isolated V3 system-Python build succeeds, but its NumPy/SciPy version
  warning remains. The Go2W environment does not have this conflict. Do not
  blindly upgrade global packages.
- **Cliff handling:** No internal follower subscriber consumes cliff/stair output.
  Supply and verify the safety integration externally.
