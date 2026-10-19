# Installation, Build, and Startup

## Reference environment

The installation commands use:

- Ubuntu 22.04.5 LTS
- ROS 2 Humble
- Python 3.10
- `ament_python`/setuptools for planner/preprocessor, `ament_cmake`/rosidl for
  r3d_interfaces, and `colcon`

ROS 2 Humble is the supported ROS distribution. Other ROS distributions are
not supported. The complete stack has run successfully on a Unitree Go2W with
the documented TF and sensor integration.

Installation uses a native ROS 2 workspace. The isolated verification used the
official `ros:humble-ros-base` image; Docker is not a runtime requirement. No
Dockerfile, rosinstall or requirements file is provided. ROS launch entry points
are installed by `r3d_planner`.
Sensor and robot drivers are part
of the Go2W deployment rather than this workspace.

## Required software

### ROS and system dependencies

For the local V4 development tree, install ROS 2 Humble first and use its
system Python 3.10. Required workspace tools are `python3-colcon-common-extensions`
and `python3-rosdep`; they are workspace tooling rather than dependencies of a
node. If absent, install them through Ubuntu's package manager:

```bash
sudo apt install python3-colcon-common-extensions python3-rosdep
```

The corrected V4 manifests declare runtime libraries, ROS messages/launch APIs,
setuptools packaging and existing test tools. Resolve these through rosdep as
shown below; a parallel global pip installation is not required.

| Python import | Humble/Jammy rosdep key | Ubuntu package / AP03 reference version |
|---|---|---|
| `numpy` | `python3-numpy` | python3-numpy, 1.21.5 |
| `scipy.spatial.KDTree` | `python3-scipy` | python3-scipy, 1.8.0 |
| `networkx` | `python3-networkx` | python3-networkx, 2.4 |
| `open3d` | `python3-open3d` | python3-open3d, 0.14.1 |
| `yaml` | `python3-yaml` | python3-yaml, 5.4.1 |
| `tf2_ros` | `tf2_ros_py` | ros-humble-tf2-ros-py |
| `rcl_interfaces.msg.ParameterDescriptor` | `rcl_interfaces` | ros-humble-rcl-interfaces; M02 runtime |
| `rosgraph_msgs.msg.Clock` | `rosgraph_msgs` | ros-humble-rosgraph-msgs; synthetic clock tests |

These are observed Jammy reference versions, not manifest version pins. NumPy,
SciPy, Open3D and NetworkX provide point-cloud/geometry, nearest-node and graph
operations. Use one consistent apt-managed Python environment; user-site NumPy
1.26.4 together with system SciPy 1.8.0 triggered the observed compatibility
warning. System NumPy 1.21.5 did not. Conda's Python is not the ROS interpreter.

Open3D's official rosdep rule resolves to Jammy's universe package. Enable the
Ubuntu universe repository if necessary. On 14 October 2026, actual rosdep
installation and subsequent check both exited 0 in two fresh isolated Humble
containers (Ubuntu 22.04.5, Python 3.10.12). Open3D 0.14.1 and NetworkX 2.4 came
from apt, with NumPy 1.21.5 and SciPy 1.8.0; the former compatibility warning
was absent. No skip keys or global pip/Conda replacements were needed. The audit
host still lacks apt Open3D/NetworkX and was not modified. Full commands, image
digest, failures during test-tool preparation and results are in the
[central protocol](docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md#16-ap03ap04ap06--isolierte-humble-abnahme-und-portabilität).

The current official `python3-open3d` rule is explicitly unavailable on Ubuntu
24.04 Noble. A Humble/Jammy result does not establish Jazzy support. That target
is postponed by the Humble-only release decision; it is not a
Humble release blocker. Do not silently substitute a pip key.

RViz (`ros-humble-rviz2`) is optional for visualization and starts separately.
`tf2_ros` command-line tools are optional when users supply an external static
TF publisher. They are not required Python libraries of either R3D package.

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

The following procedure targets the local V4 checkout with the corrected AP03
manifests. V4 has not been pushed; do not assume an upstream V4 branch exists.
The public V3 checkout still has historical dependency declarations and requires
its separate historical installation instructions. Place your existing local V4
checkout under `src`, or clone from the local repository:

```bash
mkdir -p <path-to-workspace>/src
git clone --branch V4 <path-to-local-R3D-Planner> <path-to-workspace>/src/R3D-Planner
cd <path-to-workspace>
```

Replace `<path-to-local-R3D-Planner>` with the existing local repository path.
No upstream branch checkout or push is part of this procedure.

## rosdep

Initialize rosdep only if this machine has not been initialized:

```bash
sudo rosdep init
```

With a native Humble environment (no Conda interpreter or unrelated workspace
overlays), resolve the manifests and check installed packages:

```bash
cd <path-to-workspace>
source /opt/ros/humble/setup.bash
export PYTHONNOUSERSITE=1
rosdep update --rosdistro humble
rosdep install --from-paths src/R3D-Planner \
  --ignore-src --rosdistro humble --os=ubuntu:jammy -y
rosdep check --from-paths src/R3D-Planner \
  --ignore-src --rosdistro humble --os=ubuntu:jammy
```

V4 needs no dependency skip list. AP03 separately verified key resolution,
actual installation, imports and rosdep check; the last two install/check runs
were performed in fresh isolated containers rather than on the audit host.
A successful check proves package presence, not successful build or runtime.
The workspace contains all three R3D packages, so `--ignore-src` excludes the
local `r3d_preprocessor` and `r3d_interfaces` dependencies. Every external manifest key was also resolved
individually to avoid mistaking an installed ROS overlay for key validation.

## Build

```bash
cd <path-to-workspace>
source /opt/ros/humble/setup.bash
colcon build --packages-up-to r3d_planner
source install/setup.bash
```

Verify package discovery and installed executables:

```bash
colcon list --names-only
ros2 pkg executables r3d_preprocessor
ros2 pkg executables r3d_planner
```

`colcon list` must include `r3d_interfaces`, `r3d_preprocessor` and `r3d_planner`.

The current regular copy installation was verified by the local CI reproduction:
its build exited 0, the full suite reported 358 successful colcon test records and `colcon test-result`
exited 0. Earlier independent two-workspace proofs remain dated in the protocol. Standard configuration/robot resources work through package share;
use `R3D_CONFIG_DIR` for editable user configuration. A separate source-free
container with a read-only installed tree passed 343 installation/output/interface tests.
The install prefix remained at its build-time path: relocating a workspace is
not established by this test. Optional `--symlink-install` is a developer workflow.

## Runtime configuration

V4 bundles no PCD maps; installation does not require concrete map data.
Provide your own suitable PCD inputs and configure `maps.pcd_path` for analysis
and `maps.map_name` for planning/display. The shipped paths are empty; there is
no fallback to a repository example. Use the source `planner_config.yaml` in a
symlink workspace, or copy installed configuration into a user-owned directory
as described in [CONFIGURATION.md](docs/CONFIGURATION.md).
Its `robot_config: robots/Go2W.yaml` selects the dedicated robot configuration.
Relative paths resolve against the YAML directory, not the shell working directory;
absolute paths and `~` are also accepted. Set general preprocessing,
graph, filtering and controller tuning in the central YAML and robot dimensions,
odometry frames/topic and hardware topics in the robot YAML.

With optional developer `--symlink-install`, runtime reads resolve to live source
files; edits and newly added robot YAMLs need only launch restart, without build
or re-sourcing. For a copied install, set `R3D_CONFIG_DIR` once to the
user configuration directory containing `planner_config.yaml` and robot profiles.
Without an override, a copy installation reads its regular package-share YAML
and robot profiles. User configuration needs no source checkout.
See [configuration reference](docs/CONFIGURATION.md) for all parameters.

## Prepare and inspect a map

```bash
ros2 launch r3d_planner preprocessor.launch.py
```

The one-shot analyzer writes `<input-name>_analysed.pcd` into
`preprocessing.output_dir`, relative to the chosen YAML directory or an absolute/`~`
path. An empty value uses `$XDG_DATA_HOME/r3d_preprocessor` (absolute XDG path),
otherwise `~/.local/share/r3d_preprocessor`. The input may be read-only; no
package-share write location is assumed. Existing output files or symlinks are
rejected; choose another directory to retain multiple analyses. Input and existing
output data remain intact. A failed analysis/write exits nonzero.
Set `maps.map_name` to the resulting output path. Regenerate it whenever geometry or
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
The original Go2W deployment has historical test evidence; the V3 refactor requires deployment
regression testing before motion. The current V4 package-level Flake8, PEP257
and copyright checks pass; both copyright skips have been removed. Run the full
suite through colcon, which keeps each package's duplicate template module names
in its own test process:

```bash
cd <path-to-workspace>
colcon test --packages-up-to r3d_planner
colcon test-result --verbose
```

The verified colcon total is 358 reported records / 0 FAIL / 0 SKIP: 43 retained functional cases,
10 output cases, 27 installation cases, 83 PointCloud2 cases, two parameter-query
cases, 15 metadata cases, 14 action cases, 20 composition cases, six Python lint
checks, nine CMake report records (four CTest runs plus five xUnit entries), 63 deterministic monitoring cases and18
native monitoring/launch cases, plus48geometry cases (44deterministic and4native). Launch lookup covers all four files using `--show-args`; seven node constructors use
synthetic inputs and an isolated command topic without running follower control.
This does not prove full navigation, motion safety, coverage or a remote CI run. Dependency
warnings from NetworkX `np.int` and ament tooling remain; they are not test failures.

## Troubleshooting

- **Configuration rejected:** Check the logged paths and exact key names in
  [CONFIGURATION.md](docs/CONFIGURATION.md). Strings are not booleans.
- **Configuration location:** Copy installations resolve package-share YAML;
  set `R3D_CONFIG_DIR` to an editable user-owned copy when changing settings.
- **Missing map:** Paths are relative to the central config directory; generate
  the analyzed output and align `map_name`.
- **No online start:** Confirm Odometry topic, frame IDs, timestamps and age
  limit, then `map -> odom` at the message timestamp. TF alone is insufficient.
- **TF conflict:** Disable RViz calibration TF when global localization owns it.
- **Filter output wrong:** Check valid scalar XYZ fields, dimensions and buffer
  sizes; offsets, padding and endian order are decoded. Sensor axes, units and
  calibration remain deployment contracts; no frame transformation is added by
  the byte-layout correction.
- **Python warnings/build errors:** Use the ROS system Python and consistent
  dependencies. The local workstation previously had a packaging conflict;
  the V4 isolated apt/Humble environment passes without the NumPy/SciPy
  compatibility warning. The host conflict was not repaired. Do not blindly
  upgrade global packages.
- **Cliff handling:** No internal follower subscriber consumes cliff/stair output.
  Supply and verify the safety integration externally.


## Reproduce the prepared Humble CI locally

With Docker already available, run `bash scripts/ci/run_humble.sh` from the local
V4 checkout. It installs packages only inside two temporary nonprivileged
containers, keeps the source read-only and tests as an ordinary user. The second
container receives only the read-only install tree, tests and manifest copies;
no source or build tree is mounted. Temporary logs/artifacts stay under the
printed `/tmp/r3d-ci.*` directory. Only containers created by this run are removed;
no images, host packages, ROS installation or Conda environment are changed.
The same command is configured in `.github/workflows/ros2-humble.yml`.

Local reproduction passed the full suite (358 reported colcon records) (0 failure/skip) and343
source-free cases. This is not a GitHub Actions result. The workflow remains
IMPLEMENTED / NOT REMOTELY VERIFIED while V4 is local and no push is authorized.

## Distribution investigation (15 October 2026)

| Target | Current evidence | Support boundary |
|---|---|---|
| Humble / Jammy / Python 3.10 amd64 | Clean copy build, rosdep, 358 colcon records and343 unique source-free cases pass | Verified tested scope |
| Jazzy / Noble / Python 3.12 amd64 | Full rosdep blocked by Open3D; generated interface alone builds and passes five checks plus CDR | Planner/preprocessor not verified |
| Kilted / Noble | Same official Open3D system rule; no native build/test | Not supported by this evidence |
| Lyrical / Resolute / Python 3.14 amd64 | All dependencies and three-package build pass; default colcon Python test discovery fails; direct pytest 218 pass /2 lint failures | Partial investigation, no complete support claim |
| Rolling | Current official image uses Resolute; no native verification | Development target only |

Newer Nav2 actions add error fields and, in Lyrical, viapoints. Their full contract
is not implemented or verified here. No pip/vendor migration was applied.
See central protocol section18.8 for commands, exact images and remaining work.

## M02 configuration and current target

Only Humble/Jammy/Python3.10 is the current release target. Newer distributions
remain postponed investigation results, not prerequisites for this release.
To opt into follower obstacle monitoring, edit the existing central YAML or its
R3D_CONFIG_DIR override and restart follower.launch.py. See the complete
[parameter, input, TF and stop/recovery contract](docs/CONFIGURATION.md#obstacle-monitoring-m02-humble).
The default is disabled; enabling it requires a current valid obstacle producer
even when the internal filter is disabled. This does not change planner startup.


Local obstacle geometry: the filter now additionally retains finite, height-qualified
near returns by default (`live_filter.retain_near_obstacles: true`). This prevents
radial filtering from erasing points before the follower's stop-rectangle test.
Existing numeric defaults, frames, M01 and optional M02 are unchanged. Explicit
false restores the documented legacy radial loss. Self returns, sensor coverage
and robot/body clearances still need deployment validation. The new boolean is
startup-only; old configurations without it remain valid. See the local geometry
contract in docs/CONFIGURATION.md (repository root) for formulas and limits.


Local Debian packaging was also exercised for all three packages: peer-aware Bloom
preparation, unsigned package build/install and a fresh source-free runtime probe
with dpkg file ownership, versions, dependencies and ROS interfaces passed.
These are local artifacts, not an official Bloom or Buildfarm release. Bloom's
generated rules retain their tolerant test exit behavior. The required local
release wrapper now validates the actual reports and complete test identities,
rejecting failures, errors, skips and missing evidence independently of Bloom.
Installation-dependent checks run in a mandatory fresh Debian runtime container.
Use `bash scripts/ci/run_humble_debian.sh`; ordinary CI remains a separate check.

The 358 reported colcon records comprise 349 unique Python cases and the nine
CMake records described above. CTest and xUnit represent some of the same lint
executions; they are not nine independent CMake checks. The separate normal-CI runtime
suite contains 343 unique pytest cases, including all 48 geometry cases and
the 45 configuration cases now runnable without source resources.


## Local Debian release gate (Humble / Jammy / amd64)

Run both independent checks before considering local release readiness:

```bash
bash scripts/ci/run_humble.sh
bash scripts/ci/run_humble_debian.sh
```

The Debian runner uses fresh containers, readonly source/probe mounts and ordinary
build/test users. It uses the official Bloom peer-package generator and installs
actual generated Build-Depends with `apt-get build-dep`. New test dependencies
explicitly declare the runtime APIs imported during test collection/execution.
No host package, Conda environment, Docker configuration or public release is
changed. The generated Bloom `debian/rules` files are kept unchanged.

The planner's `installed` pytest marker describes a real resource requirement.
It is inherited through the explicit `installed_share` fixture; it never skips
a default test run. Before installation, the Debian phase selects `not installed`:
243 planner tests run and 93 installation-dependent tests are deferred. The
preprocessor runs all 13 build tests. The interface runs four explicit CTest
checks: copyright, CMake lint, XML lint and source headers (two cases).

After package creation, a second fresh container installs all three Debian
packages and their dependencies. It executes **all 336 planner and 13 preprocessor
Python cases**, including every deferred installation check. This is mandatory,
not an optional replacement for missing tests. It also verifies dpkg file owners,
versions, installed resources, LICENSE/CHANGELOG, generated message imports and
ROS interface lookup without a source checkout or earlier R3D install prefix.

`release_gate.py` validates actual xUnit/JUnit, CTest discovery and the complete
unfiltered test inventory. FAIL, ERROR, SKIP, missing/empty/malformed/duplicate
reports, inconsistent counts or missing case identities fail the release gate,
even when Bloom tolerates `dh_auto_test` failure. Results remain separated by
phase; repeated runs are not added as independent tests. Artifact names, sizes,
SHA-256, control metadata and per-command exits are saved under the printed
`/tmp/r3d-debian.*` result path. Environment snapshots record actual tool versions.
The builder must not have the package under test preinstalled.

The diagnostic control is intentionally expected to fail:

```bash
bash scripts/ci/run_humble_debian.sh --failure-probe
```

It inserts a failing test only into a private temporary package copy. A nonzero
exit proves propagation through the actual two-stage entry point; it never alters
repository tests. Thirteen separate unit controls cover report rejection and
coverage matching (`/usr/bin/python3 -m pytest scripts/ci/tests -q` in a suitable
Python/pytest environment). No test deactivation or generated-template edit is a
permanent project workaround. Build-time source checks and installed checks have
different contracts; a neutral working directory and the registered ROS prefix
replace the former literal `/install/` pathname assumption.

These results are local technical evidence. Remote GitHub Actions, the final
release version, public V4 source, ROS Index/Bloom/Buildfarm operations and legal
publication clearance remain separate, explicitly unperformed gates.
