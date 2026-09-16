# Known Limitations and Maintenance Notes

These maintenance notes apply to the PCD-only V3 development branch. They cover
constraints that affect installation, integration, and future development.

## 1. Dependency metadata remains incomplete

- **Location:** both `package.xml` files and Python imports
- **Current behavior:** `numpy` and, depending on the rosdep database, `scipy` are
  not valid rosdep keys. Open3D, NetworkX,
  `sensor_msgs_py` and some direct message imports are not fully
  represented in the manifests.
- **Impact:** `rosdep install` can fail or leave runtime dependencies missing.
- **Next step:** Establish correct rosdep keys for ROS 2 Humble
  and validate revised manifests in a dedicated dependency-maintenance step.

## 2. Standalone planner defaults still refer to uninstalled maps

- **Location:** `r3d_preprocessor/setup.py`, `r3d_pcd_path.py`
- **Behavior:** Direct developer `ros2 run` defaults to an uninstalled share map.
  Normal V3 launch resolves map paths from live central YAML and validates them.
- **Impact:** Standalone debugging needs an explicit map override. Source maps
  must remain available for the supported configuration workflow.
- **Next step:** Decide on release-time external map distribution separately.

## 3. Planner launch gap resolved; hardware bringup remains external

V3 installs central preprocessor/planner launches and optional map/follower
launches. Live Filter and RViz switches are independent. Sensor drivers,
Odometry, global localization, robot adapter and safety supervision are not
launched by this workspace.

## 4. Nav2 YAML is an unattached fragment

- **Location:** `r3d_planner/config/r3d_planner_params.yaml`
- **Current behavior:** It contains placeholders and no launch file loads it.
  `observation_sources` includes `cliff_virtual`, but only `scan_filtered` has
  a block. The MPPI configuration is partial.
- **Impact:** The file is not a complete Nav2 configuration and does not prove
  that `/local/cliff_virtual_wall` reaches a costmap.
- **Next step:** Align it with the external Nav2 bringup and plugin
  versions actually used on the robot.

## 5. The local filter retains sensor-axis and binary-layout assumptions

- **Location:** `r3d_local_filter.py`
- **Current behavior:** Input topic comes from robot YAML; effective distances, heights,
  ROIs and thresholds are central YAML parameters. Binary decoding is unchanged. PointCloud2 is interpreted as packed XYZ float32 without generally
  honoring fields, offsets, `point_step`, padding, or endianness. X forward, Y
  lateral, and Z up are assumed.
- **Impact:** The Go2W integration has been exercised, but the reference Hesai
  configuration establishes only the topic and frame, not a packed 12-byte XYZ
  contract. A cloud with intensity, padding, different offsets, or a different
  `point_step` can be rejected or decoded incorrectly.
- **Next step:** Inspect `fields`, `point_step`, endianness, and mounting axes on
  the deployed Hesai topic and after every driver or sensor change.

## 6. Cliff and stair outputs have no internal consumer

- **Location:** `r3d_local_filter.py`, `r3d_path_follower.py`
- **Current behavior:** Nothing internally subscribes to
  `/local/cliff_virtual_wall` or `/stair_detect`. The follower stops only from
  `/local/filtered_obstacles`.
- **Impact:** The standalone follower does not react directly to detected
  cliffs, and stair messages do not affect motion.
- **Next step:** Verify an external consumer for the cliff output before the
  standalone follower controls the robot.

## 7. Path orientation is used as a narrow-area flag

- **Location:** `r3d_pcd_path.py`, `r3d_path_follower.py`
- **Current behavior:** The planner sets `orientation.z=1.0` for narrow areas and
  always sets `orientation.w=1.0`, producing a non-normalized quaternion in
  narrow areas.
- **Impact:** General Pose consumers may treat the internal flag as a real
  orientation.
- **Next step:** Consider explicit backward-compatible metadata later;
  preserve the current interface for now.

## 8. Request frame validation added; PCD coordinates remain implicit

- **Location:** `r3d_pcd_path.py`, `r3d_pcd_publisher.py`
- **Behavior:** V3 rejects goal/explicit-start headers outside the configured map
  frame and transforms online Odometry via `map -> odom`. PCD points are not
  transformed and carry no frame metadata. Map publisher uses configured frame.
- **Impact:** A PCD built in the wrong coordinate system can still be mislabeled.
- **Next step:** Version map frame and generating configuration with artifacts.

## 9. RViz calibration may conflict with external localization

- **Location:** `r3d_rviz_interface.py`
- **Current behavior:** The node publishes static `map -> odom` using the clicked
  map point directly and does not explicitly subtract a nonzero
  `odom -> base_link` pose. The reset service only changes internal state. V3 can disable calibration TF
  with `publish_map_odom=false` for external global localization.
- **Impact:** The tested Go2W TF tree uses one authoritative publisher per
  transform. Adding another localization source can make the tree inconsistent.
- **Next step:** Preserve the tested publisher ownership and inspect the TF
  tree after localization changes.

## 10. The path follower is not a complete safety controller

- **Location:** `r3d_path_follower.py`
- **Current behavior:** Controller tuning is central YAML, but path Z is ignored and velocity is
  published directly on the selected command topic. Missing/stale Odometry or
  global TF now produces a zero command; no external command watchdog is added. Emergency stop,
  watchdog, command mux, action feedback, and cancellation are absent.
- **Impact:** The inspected Go2W adapter forwards `/cmd_vel` to the Unitree
  SportClient without implementing these protections. Running `path_follower`
  without independently validated safeguards remains hazardous.
- **Next step:** Verify command timeout, arbitration, velocity limits, and
  emergency-stop behavior before motion and after controller/interface changes.

## 11. PCD metadata is insufficient for reproducible reconstruction

- **Location:** `pcd_analyser`, `pcd_path_planner`
- **Current behavior:** The analyzed PCD stores points and RGB classes, while voxel
  size and step heights are forwarded from one shared YAML section. The filename does not encode
  these settings.
- **Impact:** Shared settings prevent per-node duplication, but settings that do not match
  an older artifact still change keys/connectivity. Geometry forwarded to the
  planner does not reclassify stored PCD colors.
- **Next step:** Version settings with maps or add verifiable metadata in a
  future change.

## 12. Package metadata is inconsistent

- **Location:** both `package.xml` and `setup.py` files
- **Current behavior:** Manifests use version `0.0.0`, TODO descriptions, and a TODO
  license; setup files use version `0.0.1`, concrete descriptions, and
  Apache-2.0.
- **Impact:** Release metadata and license status are ambiguous.
- **Next step:** Confirm ownership and licensing before publishing.

## 13. Generated bytecode files are tracked

- **Location:** both package `__pycache__` directories
- **Current behavior:** CPython 3.10 `.pyc` files remain tracked. V2 removed only
  bytecode belonging to the deleted Pickle components.
- **Impact:** Binary artifacts can become stale and create noisy diffs.
- **Next step:** Add an ignore and cleanup policy in a dedicated maintenance
  change.

## 14. An alternative PCD publisher module is not installed

- **Location:** `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py`
- **Current behavior:** The module duplicates node name `pcd_publisher` and topic
  `/map_pointcloud`, is not registered in `setup.py`, and publishes XYZ only.
- **Impact:** Its purpose is unclear and it is not available through normal
  `ros2 run` discovery.
- **Next step:** Determine its intended role before removing,
  registering, or consolidating it.

## 15. The local workstation has a Python environment conflict

- **Location:** local development environment, not project source
- **Current behavior:** An isolated build on the local workstation stops during
  setup metadata inspection: system `packaging` is 21.3 while an installed
  entry point requires `packaging>=23.2`. SciPy 1.8.0 also warns about
  pip-visible NumPy 1.26.4. The Go2W does not have this conflict.
- **Impact:** The isolated V3 build succeeds with system Python and `PYTHONNOUSERSITE=1`.
  The SciPy/NumPy warning remains; the global environment is not repaired by
  this configuration refactor. The stack
  builds and runs in the deployed Go2W ROS 2 Humble environment.
- **Next step:** Repair the local workstation's apt/pip environment
  separately.

## 16. Existing lint tests fail and conflict in a combined run

- **Location:** both `test/` directories and existing Python sources
- **Current behavior:** PEP257 passes and copyright is skipped. Flake8 reports
  lint failures, while a combined root invocation collides on duplicate
  test-module names.
- **Impact:** Package-level lint does not pass.
- **Next step:** Address lint and test layout in a dedicated maintenance change.

## 17. Standard Odometry integration requires deployment regression

- **Location:** `r3d_planner/odometry.py`, online action requests and follower
- **Behavior:** Online start selection uses configured `nav_msgs/msg/Odometry`
  and global TF, not TF-only `map -> base_link` tracking. The source must
  provide the configured base child frame, valid current poses and timestamps.
- **Impact:** A TF-only deployment needs an Odometry output before using V3
  online planning. Sensor-frame Odometry needs an external base-frame adapter.
  The planned LiDAR-odometry fork is external and not implemented here.
- **Next step:** Validate the standardized source, clocks, global TF and pose-loss
  behavior on Go2W without motion before enabling the follower.

## 18. Discovery timing and cached ROS graph entries in test tooling

- **Location:** non-motion test harness and workstation ROS discovery
- **Behavior:** Early native asynchronous parameter queries timed out under
  Cyclone DDS and Fast DDS. CLI queries succeeded, but the CLI daemon and cached
  discovery leases initially confused node-absence assertions. The final harness
  uses daemon-free CLI queries with explicit discovery time and recreates its
  observer after shutdown. All four real launch combinations and parameter
  reload assertions pass under Fast DDS. No middleware default is changed.
- **Impact:** A stale graph or too-short discovery window can misreport launch
  conditions. The early failures do not establish a planner or middleware bug.
- **Next step:** Use the corrected harness for regression; validate deployment
  middleware independently on the Go2W.
