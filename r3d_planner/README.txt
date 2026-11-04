# r3d_planner

ROS 2 graph-based A* planning on classified PCD maps, with local point-cloud
filtering, RViz goal input and a separately started planar path follower.

Executables: pcd_path_planner, local_filter, rviz_interface, path_follower,
path_test. Launch entry points: preprocessor.launch.py, map.launch.py,
planner.launch.py and follower.launch.py.

- [Installation and startup](../docs/INSTALL.md)
- [Configuration and robot profiles](../docs/CONFIGURATION.md)
- [Nodes, topics, actions and TF](../docs/ARCHITECTURE.md)
- [Known limitations](../docs/KNOWN_ISSUES.md)

No maps or hardware drivers are bundled. The follower can command motion and
must be started explicitly. Robot velocity settings belong to the selected
robot profile under robot.velocity_limits.
