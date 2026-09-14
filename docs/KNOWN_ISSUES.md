# Known Issues and Open Verification Items

The following findings come from static repository analysis. None were fixed
in functional code during the documentation phase.

## 1. Package dependencies are incomplete or incompatible with rosdep

- **Location:** both `package.xml` files and Python imports
- **Observation:** `pickle` is declared as a ROS dependency even though it is
  part of Python. `numpy` and, depending on the database, `scipy` are not valid
  rosdep keys. Actual imports such as Open3D, NetworkX, `ament_index_python`,
  `sensor_msgs_py`, `tf2_ros`, and some `std_msgs` usage are missing.
- **Impact:** `rosdep install` fails or leaves runtime dependencies absent.
- **Investigation:** Establish correct keys for each target ROS distribution
  and validate revised manifests in a later implementation phase.

## 2. Maps are not installed although planner defaults refer to them

- **Location:** `r3d_preprocessor/setup.py` and both global planners
- **Observation:** `setup.py` explicitly omits `maps/`, while planner defaults
  resolve below `<share/r3d_preprocessor>/maps`. No `nav_graph.pkl` is included.
- **Impact:** Default planner startup cannot find a map after a normal build.
- **Investigation:** Decide whether large maps should be installed, configured
  externally, or always passed explicitly.

## 3. No launch files or complete bringup

- **Location:** entire repository
- **Observation:** Every node must be started separately with `ros2 run`; no
  encoded startup order, remappings, parameters, or lifecycle exists.
- **Impact:** Startup is error-prone and alternative planners may be launched
  together accidentally.
- **Investigation:** Design explicit hardware and test bringup variants only
  after implementation changes are authorized.

## 4. Alternative planners conflict

- **Location:** `r3d_global_planner.py`, `r3d_pcd_path.py`
- **Observation:** Both use node name `global_graph_planner`, serve
  `/compute_path_to_pose`, and publish `/global_path` and `/planned_path`.
- **Impact:** Simultaneous operation creates name/action conflicts and
  nondeterministic path output.
- **Investigation:** Retain the documented “exactly one” rule; a future launch
  selection could enforce it without renaming interfaces.

## 5. Preprocessing tools share a node name

- **Location:** `r3d_pcd_analyser.py`, `r3d_pcd_to_graph.py`
- **Observation:** Both one-shot tools are named `pcd_to_graph_node`.
- **Impact:** Concurrent runs are ambiguous in ROS introspection and logs.
- **Investigation:** They normally run sequentially; do not rename either node
  without explicit approval.

## 6. Nav2 YAML is an unattached fragment

- **Location:** `r3d_planner/config/r3d_planner_params.yaml`
- **Observation:** It contains placeholder comments and no launch file loads
  it. `observation_sources` includes `cliff_virtual`, but only
  `scan_filtered` has a configuration block. The MPPI block is partial.
- **Impact:** The file is not a complete Nav2 configuration and does not prove
  that `/local/cliff_virtual_wall` reaches a costmap.
- **Investigation:** Compare it with the actual external Nav2 configuration and
  plugin versions.

## 7. The local filter is hard-coded to a sensor and binary layout

- **Location:** `r3d_local_filter.py`
- **Observation:** Input topic, dead zone, heights, ROIs, and thresholds are
  constants. PointCloud2 data is interpreted as a packed array of three
  float32 values without generally honoring fields, offsets, `point_step`, row
  padding, or endianness. X forward, Y lateral, and Z up are assumed.
- **Impact:** Other PointCloud2 layouts or sensor orientations may be decoded
  incorrectly.
- **Investigation:** Record and compare the real Hesai message layout, frame,
  and mounting orientation.

## 8. Cliff and stair outputs have no internal consumer

- **Location:** `r3d_local_filter.py`, `r3d_path_follower.py`
- **Observation:** Nothing in this repository subscribes to
  `/local/cliff_virtual_wall` or `/stair_detect`. `path_follower` stops only
  from `/local/filtered_obstacles`.
- **Impact:** The standalone path follower does not react directly to detected
  cliffs, and stair messages do not affect motion.
- **Investigation:** Demonstrate the intended external Nav2/safety integration
  before moving hardware.

## 9. Path orientation is repurposed as a narrow-area flag

- **Location:** both global planners and `r3d_path_follower.py`
- **Observation:** Planners set `orientation.z=1.0` for narrow areas and always
  set `orientation.w=1.0`, yielding a non-normalized quaternion in narrow areas.
- **Impact:** General Nav2 or Pose consumers may interpret the values as a real
  orientation. Only the internal follower understands the flag.
- **Investigation:** Evaluate an explicit, backward-compatible metadata model
  later; preserve the current interface for now.

## 10. The map frame is assumed rather than enforced

- **Location:** global planners and map publishers
- **Observation:** Map data is treated as map coordinates. Planner output copies
  the goal header frame, but start and goal coordinates are not transformed.
  Map publishers set `map` directly.
- **Impact:** A request in another frame can be answered while its numeric
  values are still interpreted as map coordinates.
- **Investigation:** Keep requests in `map`, and later consider explicit frame
  validation or transformation.

## 11. RViz calibration may conflict with external localization

- **Location:** `r3d_rviz_interface.py`
- **Observation:** The node publishes static `map -> odom` and sets translation
  directly from the clicked map point. It does not explicitly subtract an
  existing nonzero `odom -> base_link` pose. Resetting the service only changes
  internal state; distributed static TF data remains.
- **Impact:** A nontrivial odometry pose or second localization publisher can
  make the TF tree inconsistent.
- **Investigation:** Test the workflow with real odometry and
  `tf2_tools view_frames`, ensuring one publisher per transform.

## 12. The path follower is not a complete safety controller

- **Location:** `r3d_path_follower.py`
- **Observation:** Values are hard-coded, path Z is ignored, TF errors are
  silently dropped, and `/cmd_vel` is commanded directly at 10 Hz. There is no
  emergency stop, watchdog, command mux, action feedback, or cancellation
  protocol.
- **Impact:** Real operation without external safety controls is hazardous.
- **Investigation:** Test only in a controlled environment after a separate
  safety review and document the external command/stop chain.

## 13. PCD metadata is insufficient for reproducible reconstruction

- **Location:** `pcd_analyser`, `pcd_path_planner`
- **Observation:** The analyzed PCD stores points and RGB classes, but the
  planner receives voxel size and step heights separately. `_analysed.pcd`
  filenames do not encode those settings.
- **Impact:** Mismatched planner settings silently alter node keys and graph
  connectivity.
- **Investigation:** Version settings with the map or add verifiable metadata
  in a future change.

## 14. Pickle input is version- and trust-sensitive

- **Location:** `pcd_to_graph`, `global_planner`, `voxel_map_publisher`
- **Observation:** NetworkX objects are serialized and loaded with Python
  `pickle` without provenance checks.
- **Impact:** Untrusted Pickle files can execute code when loaded; compatibility
  may also vary across Python and NetworkX versions.
- **Investigation:** Use only self-generated trusted files and consider a
  portable data format in later development.

## 15. Package metadata is inconsistent

- **Location:** both `package.xml` and `setup.py` files
- **Observation:** `package.xml` uses version `0.0.0`, TODO descriptions, and a
  TODO license, while `setup.py` uses version `0.0.1`, concrete descriptions,
  and Apache-2.0.
- **Impact:** Release metadata and license status are ambiguous.
- **Investigation:** Confirm ownership and the actual license before changing
  metadata or publishing packages.

## 16. Generated bytecode files are tracked

- **Location:** both package `__pycache__` directories
- **Observation:** CPython 3.10 `.pyc` files are tracked by Git.
- **Impact:** Binary artifacts can become stale, create noisy diffs, and be
  mistaken for canonical implementation.
- **Investigation:** Decide an ignore and cleanup strategy in an authorized
  maintenance step. No files were removed during this analysis.

## 17. An alternative publisher module is not installed

- **Location:** `r3d_preprocessor/r3d_preprocessor/r3d_pcd_voxel_publisher.py`
- **Observation:** The module duplicates node name `pcd_publisher` and topic
  `/map_pointcloud`, but is not registered in `setup.py`. Unlike `pcd_server`,
  it publishes only XYZ without RGB.
- **Impact:** Its purpose and lifecycle are unclear, and it cannot be started
  through a normal `ros2 run r3d_preprocessor ...` command.
- **Investigation:** Determine its historical purpose before removing,
  registering, or consolidating it.

## 18. Build verification is blocked by the analyzed Python environment

- **Location:** local analysis environment, not repository source
- **Observation:** An isolated `colcon build` stopped during `setup.py` metadata
  inspection. System `packaging` is 21.3 while an installed Setuptools entry
  point requires `packaging>=23.2`. System SciPy 1.8.0 also warns about the
  pip-visible NumPy 1.26.4.
- **Impact:** A complete build has not been confirmed on this machine, although
  syntax parsing, XML validation, and package discovery succeeded.
- **Investigation:** Repair the global apt/pip mixture separately and repeat in
  a clean ROS Humble environment. No package version was changed here.

## 19. Existing lint tests fail and conflict in a combined run

- **Location:** both `test/` directories and existing Python sources
- **Observation:** Per-package PEP257 passes and copyright is skipped, while
  Flake8 reports 286 findings in `r3d_preprocessor` and 200 in `r3d_planner`,
  including whitespace, line length, unused imports, and mixed indentation.
  Running both test directories together from the root fails collection with
  `ImportMismatchError` because names such as `test_copyright.py` are repeated.
- **Impact:** The current revision has no green package-level lint result, and
  a naive combined test command does not produce complete results.
- **Investigation:** Address lint and test layout in an explicitly authorized
  code-maintenance step. No source formatting was changed in this phase.
