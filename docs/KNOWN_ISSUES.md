# Known Issues and Open Verification Items

These findings describe the PCD-only V2 branch. They were documented but not
automatically corrected unless the V2 scope required removal of Pickle-only
components.

## 1. Dependency metadata remains incomplete

- **Location:** both `package.xml` files and Python imports
- **Observation:** `numpy` and, depending on the rosdep database, `scipy` are
  not valid rosdep keys. Open3D, NetworkX, `ament_index_python`,
  `sensor_msgs_py`, `tf2_ros`, and some direct message imports are not fully
  represented in the manifests.
- **Impact:** `rosdep install` can fail or leave runtime dependencies missing.
- **Investigation:** Establish correct rosdep keys for the target distribution
  and validate revised manifests in a dedicated dependency-maintenance step.

## 2. Maps are not installed although the planner default refers to them

- **Location:** `r3d_preprocessor/setup.py`, `r3d_pcd_path.py`
- **Observation:** `setup.py` explicitly omits `maps/`, while
  `pcd_path_planner` defaults to
  `<share/r3d_preprocessor>/maps/map_analysed.pcd`.
- **Impact:** Default startup cannot find the map after a normal build.
- **Investigation:** Decide whether large maps should be installed, configured
  externally, or always passed explicitly.

## 3. No launch files or complete bringup

- **Location:** entire repository
- **Observation:** Every node is started separately with `ros2 run`; startup
  order, remappings, parameters, and lifecycle are not encoded.
- **Impact:** Reproducible startup remains operator-dependent.
- **Investigation:** Design hardware and test bringup variants only after such
  implementation work is explicitly approved.

## 4. Nav2 YAML is an unattached fragment

- **Location:** `r3d_planner/config/r3d_planner_params.yaml`
- **Observation:** It contains placeholders and no launch file loads it.
  `observation_sources` includes `cliff_virtual`, but only `scan_filtered` has
  a block. The MPPI configuration is partial.
- **Impact:** The file is not a complete Nav2 configuration and does not prove
  that `/local/cliff_virtual_wall` reaches a costmap.
- **Investigation:** Compare it with the external Nav2 bringup and plugin
  versions actually used on the robot.

## 5. The local filter is hard-coded to one sensor and binary layout

- **Location:** `r3d_local_filter.py`
- **Observation:** Input topic, dead zone, heights, ROIs, and thresholds are
  constants. PointCloud2 is interpreted as packed XYZ float32 without generally
  honoring fields, offsets, `point_step`, padding, or endianness. X forward, Y
  lateral, and Z up are assumed.
- **Impact:** Other layouts or sensor orientations may be decoded incorrectly.
- **Investigation:** Capture and compare the actual Hesai message layout,
  frame, and mounting orientation.

## 6. Cliff and stair outputs have no internal consumer

- **Location:** `r3d_local_filter.py`, `r3d_path_follower.py`
- **Observation:** Nothing internally subscribes to
  `/local/cliff_virtual_wall` or `/stair_detect`. The follower stops only from
  `/local/filtered_obstacles`.
- **Impact:** The standalone follower does not react directly to detected
  cliffs, and stair messages do not affect motion.
- **Investigation:** Demonstrate the intended external Nav2/safety integration
  before moving hardware.

## 7. Path orientation is used as a narrow-area flag

- **Location:** `r3d_pcd_path.py`, `r3d_path_follower.py`
- **Observation:** The planner sets `orientation.z=1.0` for narrow areas and
  always sets `orientation.w=1.0`, producing a non-normalized quaternion in
  narrow areas.
- **Impact:** General Pose consumers may treat the internal flag as a real
  orientation.
- **Investigation:** Consider explicit backward-compatible metadata later;
  preserve the current interface for now.

## 8. The map frame is assumed rather than enforced

- **Location:** `r3d_pcd_path.py`, `r3d_pcd_publisher.py`
- **Observation:** PCD coordinates are treated as map coordinates. Planner
  output copies the goal frame string but does not transform request positions;
  `pcd_server` sets `map` directly.
- **Impact:** Requests in another frame may be answered with numerically
  misinterpreted coordinates.
- **Investigation:** Use `map` for requests and later consider frame validation
  or transformation.

## 9. RViz calibration may conflict with external localization

- **Location:** `r3d_rviz_interface.py`
- **Observation:** The node publishes static `map -> odom` using the clicked
  map point directly and does not explicitly subtract a nonzero
  `odom -> base_link` pose. The reset service only changes internal state.
- **Impact:** Existing localization or nontrivial odometry may produce an
  inconsistent TF tree.
- **Investigation:** Test with real odometry and `tf2_tools view_frames`, with
  one authoritative publisher per transform.

## 10. The path follower is not a complete safety controller

- **Location:** `r3d_path_follower.py`
- **Observation:** Values are hard-coded, path Z is ignored, TF errors are
  silently dropped, and `/cmd_vel` is published directly. Emergency stop,
  watchdog, command mux, action feedback, and cancellation are absent.
- **Impact:** Real operation without external protection is hazardous.
- **Investigation:** Test only after a safety review and document the external
  command and stop chain.

## 11. PCD metadata is insufficient for reproducible reconstruction

- **Location:** `pcd_analyser`, `pcd_path_planner`
- **Observation:** The analyzed PCD stores points and RGB classes, while voxel
  size and step heights are passed separately. The filename does not encode
  these settings.
- **Impact:** Mismatched settings silently change graph keys and connectivity.
- **Investigation:** Version settings with maps or add verifiable metadata in a
  future change.

## 12. Package metadata is inconsistent

- **Location:** both `package.xml` and `setup.py` files
- **Observation:** Manifests use version `0.0.0`, TODO descriptions, and a TODO
  license; setup files use version `0.0.1`, concrete descriptions, and
  Apache-2.0.
- **Impact:** Release metadata and license status are ambiguous.
- **Investigation:** Confirm ownership and licensing before publishing.

## 13. Generated bytecode files are tracked

- **Location:** both package `__pycache__` directories
- **Observation:** CPython 3.10 `.pyc` files remain tracked. V2 removed only
  bytecode belonging to the deleted Pickle components.
- **Impact:** Binary artifacts can become stale and create noisy diffs.
- **Investigation:** Decide an ignore and cleanup strategy in an authorized
  maintenance step.

## 14. An alternative PCD publisher module is not installed

- **Location:** `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py`
- **Observation:** The module duplicates node name `pcd_publisher` and topic
  `/map_pointcloud`, is not registered in `setup.py`, and publishes XYZ only.
- **Impact:** Its purpose is unclear and it is not available through normal
  `ros2 run` discovery.
- **Investigation:** Determine its historical purpose before removing,
  registering, or consolidating it.

## 15. Build verification is blocked by the analyzed Python environment

- **Location:** local analysis environment, not repository source
- **Observation:** An isolated build stops during setup metadata inspection:
  system `packaging` is 21.3 while an installed entry point requires
  `packaging>=23.2`. SciPy 1.8.0 also warns about pip-visible NumPy 1.26.4.
- **Impact:** A complete build is not confirmed on this machine, although
  syntax, XML, and package discovery checks succeed.
- **Investigation:** Repair the apt/pip environment separately and retest in a
  clean ROS Humble environment.

## 16. Existing lint tests fail and conflict in a combined run

- **Location:** both `test/` directories and existing Python sources
- **Observation:** PEP257 passes and copyright is skipped. Flake8 reports
  existing findings, while a combined root invocation collides on duplicate
  test-module names.
- **Impact:** The current revision has no green package-level lint result.
- **Investigation:** Address lint and test layout in an explicitly authorized
  maintenance step; V2 does not reformat retained functional code.
