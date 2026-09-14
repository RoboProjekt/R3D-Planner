# R3D-Planner — Quick Reference

The complete, code-verified repository documentation is in `README.md`.
Installation, build, and startup instructions are in `INSTALL.md`; the complete
interface and data-flow analysis is in `docs/ARCHITECTURE.md`; observed but
unfixed problems are recorded in `docs/KNOWN_ISSUES.md`.

The current repository contains two `ament_python` packages:

- `r3d_preprocessor`: produces color-coded analyzed PCDs and publishes them for
  RViz.
- `r3d_planner`: provides a PCD-based A* planner, a local Hesai filter, an RViz
  interface, a simple `/cmd_vel` path follower, and a test TF.

Analysis reference environment: Ubuntu 22.04, ROS 2 Humble, Python 3.10. The
repository itself has no binding support matrix and contains no launch files.

## Build

```bash
cd ~/r3d_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

The current manifests do not yet permit a completely automatic rosdep run. See
`INSTALL.md` before building.

## PCD-based planning test

Run these commands in separate, sourced terminals:

```bash
ros2 run r3d_preprocessor pcd_server --ros-args \
  -p pcd_path:=~/r3d_ws/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd
```

```bash
ros2 run r3d_planner pcd_path_planner --ros-args \
  -p map_name:=~/r3d_ws/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd \
  -p voxel_size_cm:=5.0 \
  -p min_step_height_cm:=5.0 \
  -p max_step_height_cm:=25.0
```

```bash
ros2 run r3d_planner path_test
ros2 run r3d_planner rviz_interface
rviz2
```

In RViz, set the Fixed Frame to `map`. For `/map_pointcloud`, select
`Transient Local` durability and the `RGB8` color transformer. Display
`/planned_path` as a Marker.

`path_test` is exclusively for tests without real odometry. `path_follower` is
deliberately not started here because it publishes directly to `/cmd_vel`.
Read the hardware checks in `INSTALL.md` before enabling motion.
