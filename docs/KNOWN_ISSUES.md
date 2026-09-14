# Known Limitations and Maintenance Notes

These maintenance notes apply to the PCD-only `V2` branch. They cover
constraints that affect installation, integration, and future development.

## 1. Dependency metadata remains incomplete

- **Location:** both `package.xml` files and Python imports
- **Current behavior:** `numpy` and, depending on the rosdep database, `scipy` are
  not valid rosdep keys. Open3D, NetworkX, `ament_index_python`,
  `sensor_msgs_py`, `tf2_ros`, and some direct message imports are not fully
  represented in the manifests.
- **Impact:** `rosdep install` can fail or leave runtime dependencies missing.
- **Next step:** Establish correct rosdep keys for ROS 2 Humble
  and validate revised manifests in a dedicated dependency-maintenance step.

## 2. Maps are not installed although the planner default refers to them

- **Location:** `r3d_preprocessor/setup.py`, `r3d_pcd_path.py`
- **Current behavior:** `setup.py` explicitly omits `maps/`, while
  `pcd_path_planner` defaults to
  `<share/r3d_preprocessor>/maps/map_analysed.pcd`.
- **Impact:** Default startup cannot find the map after a normal build.
- **Next step:** Decide whether large maps should be installed, configured
  externally, or always passed explicitly.

## 3. No launch files or complete bringup

- **Location:** entire repository
- **Current behavior:** Every node is started separately with `ros2 run`; startup
  order, remappings, parameters, and lifecycle are not encoded.
- **Impact:** Reproducible startup remains operator-dependent.
- **Next step:** Add separate hardware and test bringup variants when launch
  support is implemented.

## 4. Nav2 YAML is an unattached fragment

- **Location:** `r3d_planner/config/r3d_planner_params.yaml`
- **Current behavior:** It contains placeholders and no launch file loads it.
  `observation_sources` includes `cliff_virtual`, but only `scan_filtered` has
  a block. The MPPI configuration is partial.
- **Impact:** The file is not a complete Nav2 configuration and does not prove
  that `/local/cliff_virtual_wall` reaches a costmap.
- **Next step:** Align it with the external Nav2 bringup and plugin
  versions actually used on the robot.

## 5. The local filter is hard-coded to one sensor and binary layout

- **Location:** `r3d_local_filter.py`
- **Current behavior:** Input topic, dead zone, heights, ROIs, and thresholds are
  constants. PointCloud2 is interpreted as packed XYZ float32 without generally
  honoring fields, offsets, `point_step`, padding, or endianness. X forward, Y
  lateral, and Z up are assumed.
- **Impact:** The layout and sensor orientation are verified on the Go2W, but a
  driver or sensor change can cause incorrect decoding.
- **Next step:** Revalidate the PointCloud2 layout and mounting orientation
  whenever the Hesai integration changes.

## 6. Cliff and stair outputs have no internal consumer

- **Location:** `r3d_local_filter.py`, `r3d_path_follower.py`
- **Current behavior:** Nothing internally subscribes to
  `/local/cliff_virtual_wall` or `/stair_detect`. The follower stops only from
  `/local/filtered_obstacles`.
- **Impact:** The standalone follower does not react directly to detected
  cliffs, and stair messages do not affect motion.
- **Next step:** Keep the tested external Nav2 and safety integration active
  whenever the standalone follower controls the robot.

## 7. Path orientation is used as a narrow-area flag

- **Location:** `r3d_pcd_path.py`, `r3d_path_follower.py`
- **Current behavior:** The planner sets `orientation.z=1.0` for narrow areas and
  always sets `orientation.w=1.0`, producing a non-normalized quaternion in
  narrow areas.
- **Impact:** General Pose consumers may treat the internal flag as a real
  orientation.
- **Next step:** Consider explicit backward-compatible metadata later;
  preserve the current interface for now.

## 8. The map frame is assumed rather than enforced

- **Location:** `r3d_pcd_path.py`, `r3d_pcd_publisher.py`
- **Current behavior:** PCD coordinates are treated as map coordinates. Planner
  output copies the goal frame string but does not transform request positions;
  `pcd_server` sets `map` directly.
- **Impact:** Requests in another frame may be answered with numerically
  misinterpreted coordinates.
- **Next step:** Use `map` for requests and later consider frame validation
  or transformation.

## 9. RViz calibration may conflict with external localization

- **Location:** `r3d_rviz_interface.py`
- **Current behavior:** The node publishes static `map -> odom` using the clicked
  map point directly and does not explicitly subtract a nonzero
  `odom -> base_link` pose. The reset service only changes internal state.
- **Impact:** The tested Go2W TF tree uses one authoritative publisher per
  transform. Adding another localization source can make the tree inconsistent.
- **Next step:** Preserve the tested publisher ownership and inspect the TF
  tree after localization changes.

## 10. The path follower is not a complete safety controller

- **Location:** `r3d_path_follower.py`
- **Current behavior:** Values are hard-coded, path Z is ignored, TF errors are
  silently dropped, and `/cmd_vel` is published directly. Emergency stop,
  watchdog, command mux, action feedback, and cancellation are absent.
- **Impact:** The tested Go2W deployment supplies the external safety chain.
  Running `path_follower` without that integration remains hazardous.
- **Next step:** Preserve and retest the Go2W command and stop chain after
  changes to the controller or robot interface.

## 11. PCD metadata is insufficient for reproducible reconstruction

- **Location:** `pcd_analyser`, `pcd_path_planner`
- **Current behavior:** The analyzed PCD stores points and RGB classes, while voxel
  size and step heights are passed separately. The filename does not encode
  these settings.
- **Impact:** Mismatched settings silently change graph keys and connectivity.
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
- **Impact:** Local build validation is blocked on this machine only. The stack
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
