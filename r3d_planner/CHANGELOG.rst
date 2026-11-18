Changelog for package r3d_planner
=================================

Forthcoming
-----------

* Graph-based A* planning through the ComputePathToPose action.
* Robot-specific geometry, odometry interfaces and velocity configuration.
* Atomic path metadata with narrow-area flags for the planar follower.
* Optional local point-cloud filtering and RViz goal selection.
* Optional obstacle-input freshness, geometry and timestamped TF monitoring.
* Go2W stair-mode coordinator with SDK-confirmed switches at standstill,
  path-bound follower interlocks and robot-specific approach/exit distances.
* Explicit StairDetection boolean and post-traversal clear event.
* BalanceStand preparation and independent telemetry verification through an
  SDK guard, with acknowledged cmd_vel publication pauses during transitions.
