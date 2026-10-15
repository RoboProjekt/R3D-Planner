# Known Limitations and Maintenance Notes

These maintenance notes describe the V4 development tree, with retained V3
architecture and historical limitations explicitly distinguished.

## 1. Humble dependency and installation scope verified; other targets remain open

- **Location:** manifests, [INSTALL.md](../INSTALL.md), configuration/output modules.
- **Verified:** 26 Humble/Jammy keys; real rosdep install and check exit 0 in two
  fresh isolated apt containers. No skip keys. Two empty copy workspaces each
  pass 171 tests (0 fail, 0 skip), including Flake8, PEP257 and copyright. A
  separate source-free, read-only installation passes 120 installed/output/PointCloud2 cases.
- **Environment boundary:** Ubuntu 22.04.5, Humble, Python 3.10.12, NumPy 1.21.5,
  SciPy 1.8.0, Open3D 0.14.1, NetworkX 2.4. The original host is unchanged and
  still lacks apt Open3D/NetworkX; its earlier failure is historical evidence.
- **Warnings:** NetworkX `np.int` and ament tooling deprecations remain. The old
  user-site NumPy 1.26.4 / apt SciPy 1.8.0 compatibility warning is absent in
  the isolated apt set. This does not repair a mixed host environment.
- **AP09 boundary:** the previously investigated official Open3D key is
  unavailable for Ubuntu Noble. No Jazzy, other-platform or hardware verification.
- **Release boundary:** no CI run, coverage claim, public V4 ref, official
  release or complete legal/distribution approval. See the central protocol.

## 2. Standalone planner defaults still refer to uninstalled maps

- **Location:** `r3d_preprocessor/setup.py`, `r3d_pcd_path.py`
- **Behavior:** Direct developer `ros2 run` defaults to an uninstalled share map.
  Normal V3 launch resolves map paths from live central YAML and validates them.
- **Impact:** Standalone debugging needs an explicit map override. V4 ships no
  PCD maps; normal launch requires a user-provided selected path in the central YAML.
  Use `R3D_CONFIG_DIR` for a user-owned configuration in copied installations.
- **AP04 result:** Regular copy installations resolve installed package-share
  configuration; an explicit user-owned `R3D_CONFIG_DIR` remains the override.
  Data provision stays external. Historical Git versions retain the old maps.

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

## 5. Field decoding is corrected; sensor-axis and follower-frame contracts remain

- **Location:** `cloud.py`, `r3d_local_filter.py`, `r3d_path_follower.py`.
- **Current behavior:** Both consumers honor scalar numeric XYZ fields, offsets,
  point/row strides and endian order. Organized, padded and extra-channel clouds
  are supported; nonfinite XYZ is removed even when is_dense claims true.
  Input bytes are preserved. Empty filter outputs have complete XYZ metadata.
- **Rejected data:** Missing/non-scalar XYZ, unknown datatypes, inconsistent
  strides and truncated buffers are logged and rejected, not published as clear.
- **Remaining frame boundary:** Filter thresholds deliberately use sensor
  coordinates with X forward, Y lateral, Z up; outputs retain the sensor header.
  The current follower does not yet establish a timestamped sensor-to-base
  transformation or obstacle timeout. Those behavioral migrations need the
  separate approval recorded in central protocol section 17.4.
- **Verification boundary:** Synthetic byte-layout and node-output regressions
  establish decoding; no new physical sensor calibration or robot test.

## 6. Cliff and stair outputs have no internal consumer

- **Location:** `r3d_local_filter.py`, `r3d_path_follower.py`
- **Current behavior:** Nothing internally subscribes to
  `/local/cliff_virtual_wall` or `/stair_detect`. The follower stops only from
  `/local/filtered_obstacles`.
- **Impact:** The standalone follower does not react directly to detected
  cliffs, and stair messages do not affect motion.
- **Next step:** Verify an external consumer for the cliff output before the
  standalone follower controls the robot.

## 7. M01 replaces the incompatible legacy narrow encoding

- **Implemented:** Standard Path/action-result orientations are normalized
  geometric headings. The follower uses complete PathWithMetadata messages,
  not orientation.z flags; invalid metadata clears the path. Reliable,
  transient-local, depth-1 delivery retains path and flags for late joining.
- **Migration:** Build all three packages and upgrade planner/follower together.
  Old external narrow decoders must consume the typed metadata instead.
- **Remaining boundary:** This is not full Nav2 plugin/lifecycle compatibility
  or new obstacle freshness/TF monitoring. M02 is deferred by user decision.

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

## 16. Package-level lint passes; combined raw pytest collection remains unsuitable

- **Location:** both `test/` directories and Python sources.
- **Current result:** Flake8, PEP257 and activated copyright checks all pass;
  the complete colcon suite has 171 PASS / 0 FAIL / 0 SKIP. Own Apache headers
  use a form recognized by Humble's checker; original OSRF notices are preserved.
- **Invocation limitation:** raw combined pytest collection of both package test
  directories can collide on their existing template filenames. Use `colcon test`
  (separate package processes), or test package directories separately.
- **Remaining scope:** comprehensive algorithm/API coverage, CI and future AP05
  regressions remain work items. Root runs cannot prove ordinary-user write
  permissions; the final output tests were run as UID 1000, with no skips.

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

## Current action behavior after AP05 fixes

Pose/frame/nonfinite checks, empty/unreachable errors, result timing and accepted
cancellation are covered by real ROS clients. Explicit-start map coordinates do
not require Odometry/TF. Online requests require the existing fresh pose and TF.
planner_id is retained as a compatibility field and does not choose a plugin;
feedback has no Humble payload. Four workers are not a real-time latency guarantee.
A previous published path remains active after another request aborts/cancels;
cancellation is not a controller stop command. M02 remains deferred.
