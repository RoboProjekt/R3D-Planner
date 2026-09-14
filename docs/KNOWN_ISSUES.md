# Known Limitations and Maintenance Notes

These maintenance notes apply to `V1`. They cover constraints that affect
installation, integration, and future development.

## 1. Package dependencies are incomplete or incompatible with rosdep

- **Location:** both `package.xml` files and Python imports
- **Current behavior:** `pickle` is declared as a ROS dependency even though it is
  part of Python. `numpy` and, depending on the database, `scipy` are not valid
  rosdep keys. Actual imports such as Open3D, NetworkX, `ament_index_python`,
  `sensor_msgs_py`, `tf2_ros`, and some `std_msgs` usage are missing.
- **Impact:** `rosdep install` fails or leaves runtime dependencies absent.
- **Next step:** Establish correct keys for ROS 2 Humble
  and validate revised manifests in a later implementation phase.

## 2. Maps are not installed although planner defaults refer to them

- **Location:** `r3d_preprocessor/setup.py` and both global planners
- **Current behavior:** `setup.py` explicitly omits `maps/`, while planner defaults
  resolve below `<share/r3d_preprocessor>/maps`. No `nav_graph.pkl` is included.
- **Impact:** Default planner startup cannot find a map after a normal build.
- **Next step:** Decide whether large maps should be installed, configured
  externally, or always passed explicitly.

## 3. No launch files or complete bringup

- **Location:** entire repository
- **Current behavior:** Every node must be started separately with `ros2 run`; no
  encoded startup order, remappings, parameters, or lifecycle exists.
- **Impact:** Startup is error-prone and alternative planners may be launched
  together accidentally.
- **Next step:** Add separate hardware and test bringup variants when launch
  support is implemented.

## 4. Alternative planners conflict

- **Location:** `r3d_global_planner.py`, `r3d_pcd_path.py`
- **Current behavior:** Both use node name `global_graph_planner`, serve
  `/compute_path_to_pose`, and publish `/global_path` and `/planned_path`.
- **Impact:** Simultaneous operation creates name/action conflicts and
  nondeterministic path output.
- **Next step:** Retain the documented “exactly one” rule; a future launch
  selection could enforce it without renaming interfaces.

## 5. Preprocessing tools share a node name

- **Location:** `r3d_pcd_analyser.py`, `r3d_pcd_to_graph.py`
- **Current behavior:** Both one-shot tools are named `pcd_to_graph_node`.
- **Impact:** Concurrent runs are ambiguous in ROS introspection and logs.
- **Next step:** Run them sequentially; do not rename either node
  without explicit approval.

## 6. Nav2 YAML is an unattached fragment

- **Location:** `r3d_planner/config/r3d_planner_params.yaml`
- **Current behavior:** It contains placeholder comments and no launch file loads
  it. `observation_sources` includes `cliff_virtual`, but only
  `scan_filtered` has a configuration block. The MPPI block is partial.
- **Impact:** The file is not a complete Nav2 configuration and does not prove
  that `/local/cliff_virtual_wall` reaches a costmap.
- **Next step:** Align it with the external Nav2 configuration and
  plugin versions.

## 7. The local filter is hard-coded to a sensor and binary layout

- **Location:** `r3d_local_filter.py`
- **Current behavior:** Input topic, dead zone, heights, ROIs, and thresholds are
  constants. PointCloud2 data is interpreted as a packed array of three
  float32 values without generally honoring fields, offsets, `point_step`, row
  padding, or endianness. X forward, Y lateral, and Z up are assumed.
- **Impact:** The layout and sensor orientation are verified on the Go2W, but a
  driver or sensor change can cause incorrect decoding.
- **Next step:** Revalidate the PointCloud2 layout and mounting orientation
  whenever the Hesai integration changes.

## 8. Cliff and stair outputs have no internal consumer

- **Location:** `r3d_local_filter.py`, `r3d_path_follower.py`
- **Current behavior:** No node in this workspace subscribes to
  `/local/cliff_virtual_wall` or `/stair_detect`. `path_follower` stops only
  from `/local/filtered_obstacles`.
- **Impact:** The standalone path follower does not react directly to detected
  cliffs, and stair messages do not affect motion.
- **Next step:** Keep the tested external Nav2 and safety integration active
  whenever the standalone follower controls the robot.

## 9. Path orientation is repurposed as a narrow-area flag

- **Location:** both global planners and `r3d_path_follower.py`
- **Current behavior:** Planners set `orientation.z=1.0` for narrow areas and always
  set `orientation.w=1.0`, yielding a non-normalized quaternion in narrow areas.
- **Impact:** General Nav2 or Pose consumers may interpret the values as a real
  orientation. Only the internal follower understands the flag.
- **Next step:** Evaluate an explicit, backward-compatible metadata model
  later; preserve the current interface for now.

## 10. The map frame is assumed rather than enforced

- **Location:** global planners and map publishers
- **Current behavior:** Map data is treated as map coordinates. Planner output copies
  the goal header frame, but start and goal coordinates are not transformed.
  Map publishers set `map` directly.
- **Impact:** A request in another frame can be answered while its numeric
  values are still interpreted as map coordinates.
- **Next step:** Keep requests in `map`, and later consider explicit frame
  validation or transformation.

## 11. RViz calibration may conflict with external localization

- **Location:** `r3d_rviz_interface.py`
- **Current behavior:** The node publishes static `map -> odom` and sets translation
  directly from the clicked map point. It does not explicitly subtract an
  existing nonzero `odom -> base_link` pose. Resetting the service only changes
  internal state; distributed static TF data remains.
- **Impact:** The tested Go2W TF tree uses one authoritative publisher per
  transform. Adding another localization source can make the tree inconsistent.
- **Next step:** Preserve the tested publisher ownership and inspect the TF
  tree after localization changes.

## 12. The path follower is not a complete safety controller

- **Location:** `r3d_path_follower.py`
- **Current behavior:** Values are hard-coded, path Z is ignored, TF errors are
  silently dropped, and `/cmd_vel` is commanded directly at 10 Hz. There is no
  emergency stop, watchdog, command mux, action feedback, or cancellation
  protocol.
- **Impact:** The tested Go2W deployment supplies the external safety chain.
  Running `path_follower` without that integration remains hazardous.
- **Next step:** Preserve and retest the Go2W command and stop chain after
  changes to the controller or robot interface.

## 13. PCD metadata is insufficient for reproducible reconstruction

- **Location:** `pcd_analyser`, `pcd_path_planner`
- **Current behavior:** The analyzed PCD stores points and RGB classes, but the
  planner receives voxel size and step heights separately. `_analysed.pcd`
  filenames do not encode those settings.
- **Impact:** Mismatched planner settings silently alter node keys and graph
  connectivity.
- **Next step:** Version settings with the map or add verifiable metadata
  in a future change.

## 14. Pickle input is version- and trust-sensitive

- **Location:** `pcd_to_graph`, `global_planner`, `voxel_map_publisher`
- **Current behavior:** NetworkX objects are serialized and loaded with Python
  `pickle` without provenance checks.
- **Impact:** Untrusted Pickle files can execute code when loaded; compatibility
  may also vary across Python and NetworkX versions.
- **Next step:** Use only self-generated trusted files and consider a
  portable data format in later development.

## 15. Package metadata is inconsistent

- **Location:** both `package.xml` and `setup.py` files
- **Current behavior:** `package.xml` uses version `0.0.0`, TODO descriptions, and a
  TODO license, while `setup.py` uses version `0.0.1`, concrete descriptions,
  and Apache-2.0.
- **Impact:** Release metadata and license status are ambiguous.
- **Next step:** Confirm ownership and the actual license before changing
  metadata or publishing packages.

## 16. Generated bytecode files are tracked

- **Location:** both package `__pycache__` directories
- **Current behavior:** CPython 3.10 `.pyc` files are tracked by Git.
- **Impact:** Binary artifacts can become stale, create noisy diffs, and be
  mistaken for canonical implementation.
- **Next step:** Add an ignore and cleanup policy in a dedicated maintenance
  change.

## 17. An alternative publisher module is not installed

- **Location:** `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py`
- **Current behavior:** The module duplicates node name `pcd_publisher` and topic
  `/map_pointcloud`, but is not registered in `setup.py`. Unlike `pcd_server`,
  it publishes only XYZ without RGB.
- **Impact:** Its purpose and lifecycle are unclear, and it cannot be started
  through a normal `ros2 run r3d_preprocessor ...` command.
- **Next step:** Determine its intended role before removing,
  registering, or consolidating it.

## 18. The local workstation has a Python environment conflict

- **Location:** local development environment, not project source
- **Current behavior:** An isolated build on the local workstation stops during
  setup metadata inspection: system `packaging` is 21.3 while an installed
  entry point requires `packaging>=23.2`. SciPy 1.8.0 also warns about
  pip-visible NumPy 1.26.4. The Go2W does not have this conflict.
- **Impact:** Local build validation is blocked on this machine only. The stack
  builds and runs in the deployed Go2W ROS 2 Humble environment.
- **Next step:** Repair the local workstation's apt/pip environment
  separately.

## 19. Existing lint tests fail and conflict in a combined run

- **Location:** both `test/` directories and existing Python sources
- **Current behavior:** Per-package PEP257 passes and copyright is skipped, while
  Flake8 reports 286 findings in `r3d_preprocessor` and 200 in `r3d_planner`,
  including whitespace, line length, unused imports, and mixed indentation.
  Running both test directories together from the root fails collection with
  `ImportMismatchError` because names such as `test_copyright.py` are repeated.
- **Impact:** Package-level lint does not pass, and
  a naive combined test command does not produce complete results.
- **Next step:** Address lint and test layout in a dedicated maintenance change.
