# R3D-Planner — Quick Reference

Use `README.md` for the repository overview, `INSTALL.md` for setup and startup,
`docs/ARCHITECTURE.md` for interfaces and data flow, and
`docs/KNOWN_ISSUES.md` for unresolved problems. The source-level validation
against the original deployment is in `docs/REFERENCE_COMPARISON.md`.

R3D-Planner consists of two `ament_python` packages:

- `r3d_preprocessor`: produces color-coded analyzed PCDs and publishes them for
  RViz.
- `r3d_planner`: provides a PCD-based A* planner, a local Hesai filter, an RViz
  interface, a simple `/cmd_vel` path follower, and a test TF.

The supported ROS distribution is ROS 2 Humble. The stack has been implemented
and tested on a Unitree Go2W. The repository contains no launch files.

## Build

Replace `<path-to-workspace>` with the absolute path of the ROS 2 workspace
before running the commands.

```bash
cd <path-to-workspace>
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
  -p pcd_path:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd
```

```bash
ros2 run r3d_planner pcd_path_planner --ros-args \
  -p map_name:=<path-to-workspace>/src/R3D-Planner/r3d_preprocessor/maps/voxel_05_minhits_7_analysed.pcd \
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
