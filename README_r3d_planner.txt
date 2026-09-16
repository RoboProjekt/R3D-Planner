# R3D-Planner — Quick Reference

ROS 2 Humble is the only supported ROS distribution. The original complete stack
has run on a Unitree Go2W; V3 adds runtime YAML configuration and a standard
Odometry input without embedding a SLAM implementation.

See README.md for usage, INSTALL.md for dependencies/build,
docs/CONFIGURATION.md for settings, docs/ARCHITECTURE.md for ROS interfaces,
and docs/KNOWN_ISSUES.md for limitations. docs/REFERENCE_COMPARISON.md is the
historical V2 comparison, not the current V3 interface reference.

## Build once

Replace placeholders before running:

```bash
cd <path-to-workspace>
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Configure and use

Edit r3d_planner/config/planner_config.yaml; robot_config selects robots/Go2W.yaml.
Set maps.pcd_path and maps.map_name and the independent
components.live_filter.enabled / components.rviz_interface.enabled switches.

```bash
ros2 launch r3d_planner preprocessor.launch.py
ros2 launch r3d_planner planner.launch.py
```

The analyzer is one-shot. Use separate terminals for remaining long-running nodes.
Optional visualization:

```bash
ros2 launch r3d_planner map.launch.py
rviz2
```

YAML edits require launch restart only, no build or re-sourcing.
For offline action calls use use_start=true with explicit map-coordinate poses.
For online calls use use_start=false; the configured Odometry topic and
map -> odom TF supply the current start. A TF-only path_test is not sufficient.

The planner launch never starts a hardware driver or path_follower.
follower.launch.py is a separate motion-producing command, to be started only
after externally verified watchdogs, arbitration, cliff handling and emergency stop.
