# Known limitations and troubleshooting

## Supported environment

The supported environment is ROS 2 Humble on Ubuntu 22.04 Jammy, Python 3.10,
amd64. Other ROS distributions and platforms are not supported by this package's
installation instructions. Use one consistent ROS system Python environment;
mixed apt/pip or Conda environments can cause import and dependency conflicts.

## Launch fails because a map is missing

No PCD maps are bundled. The shipped `maps.pcd_path` and `maps.map_name` values
are empty. Set the selected path in your full configuration before launching:
preprocessing needs `pcd_path`; planner, map and follower launches need
`map_name`. The unused map path may remain empty. Direct `ros2 run` defaults
are not a substitute for configuring an input map.

The analyzed PCD contains point coordinates and RGB classes, not the voxel size,
robot geometry or processing settings used to generate it. Keep those settings
with the map and regenerate it after changing geometry or preprocessing. The
planner cannot reclassify stored colors when selecting another robot profile.
PCD coordinates must already use the configured map frame.

## Configuration changes do not take effect

YAML is read at startup. Restart the affected launch after editing it. In a
regular copy installation, edit a user-owned directory selected by
`R3D_CONFIG_DIR`, or rebuild to refresh installed templates. All four velocity
settings belong under `robot.velocity_limits`; old global definitions are
rejected by launch validation. Those ROS parameters are read-only, so conflicting
startup overrides cannot replace the selected profile.

## Planning works offline but fails online

Explicit-start requests with `use_start: true` need valid map-frame poses and
no Odometry or TF. Online requests need fresh standard Odometry with the
configured odom/base frames and `map -> odom` TF at the pose timestamp.
Invalid, future-dated or stale input causes the request to abort. A source that
publishes only TF, or Odometry for a sensor rather than the robot base, does not
meet this contract. Drivers, localization and frame adapters are external.

## RViz calibration or TF is inconsistent

Use one owner for each transform. Set `rviz_interface.publish_map_odom: false`
when global localization already publishes `map -> odom`. The built-in static
RViz calibration assumes an identity odometric base pose; it is not a general
global localizer. `/recalibrate_pose` resets selection state, but does not remove
an already published static transform. Namespaces do not prefix TF frame IDs.

## Action cancellation does not stop a previously accepted path

Canceling a planning request, or receiving an aborted request, does not revoke
an earlier published path. The follower can continue following that path when
its own input conditions allow it. Action cancellation is not a robot stop
interface. `planner_id` is accepted for compatibility and does not select a
planner plugin. This stack is not a complete Nav2 lifecycle/plugin integration.

## Follower and obstacle-input limits

The follower uses path XY/yaw and ignores path Z. It does not directly consume
`/stair_detect` or `/local/cliff_virtual_wall`. Independent command watchdogs,
arbitration and stop facilities are external; a zero Twist is a software command,
not a demonstrated physical emergency stop.

Obstacle freshness/TF monitoring is disabled by default. Without it, the follower
evaluates received obstacle coordinates directly and does not stop merely because
cloud input disappears. Enabling monitoring requires a valid current input and
the configured frame/time contract; missing or invalid input keeps commands zero.
See [Obstacle monitoring](CONFIGURATION.md#obstacle-monitoring).

The local filter uses sensor coordinates with X forward, Y lateral and Z up.
Its Z thresholds are not automatically heights above the ground. Near-obstacle
retention does not reconstruct missing returns or prove sensor coverage; self
returns can cause stops. The follower's open forward rectangle is not a complete
robot footprint, side/rear/turn envelope or braking-distance model. Offline
geometry parameters do not supply that local model.

## Nav2 configuration fragment

`r3d_planner/config/r3d_planner_params.yaml` is an incomplete costmap/MPPI
fragment and is not loaded by the package launch files. It contains no full
`cliff_virtual` observation-source configuration. Do not treat it as a complete
Nav2 bringup or as an internal consumer of cliff detections.

## Diagnostics

Start with [Installation and startup](INSTALL.md) and verify package discovery,
the selected YAML paths, action availability, Odometry timestamps and the TF
tree. Topic and frame defaults are listed in [ARCHITECTURE.md](ARCHITECTURE.md).
When running tests, use colcon or separate package processes; collecting both
Python package test directories together can collide on shared template names.
