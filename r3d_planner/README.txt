# r3d_planner

ROS 2 graph-based A* planning on classified PCD maps, with local point-cloud
filtering, RViz goal input and a separately started planar path follower.

Executables: pcd_path_planner, local_filter, rviz_interface, path_follower,
path_test, stair_controller. Launch entry points: preprocessor.launch.py, map.launch.py,
planner.launch.py and follower.launch.py.

- [Installation and startup](../docs/INSTALL.md)
- [Configuration and robot profiles](../docs/CONFIGURATION.md)
- [Nodes, topics, actions and TF](../docs/ARCHITECTURE.md)
- [Known limitations](../docs/KNOWN_ISSUES.md)

No maps or hardware drivers are bundled. The follower can command motion and
must be started explicitly. Robot velocity settings belong to the selected
robot profile under robot.velocity_limits.

The follower launch starts stair_controller and requires its fresh path-bound
movement permits. Robot stairs.approach_distance_m and stairs.exit_distance_m
configure the margins. The SDK executable runs externally on the Jetson.
See the Go2W stair-control section of the configuration reference.
