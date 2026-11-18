# r3d_interfaces

This `ament_cmake`/rosidl package generates
`r3d_interfaces/msg/PathWithMetadata` for Python and C++ consumers:

```text
nav_msgs/Path path
bool[] narrow
bool[] stairs
```

`narrow[i]` and `stairs[i]` belong to `path.poses[i]`. The geometric path and
both indexed flag arrays travel atomically. Quaternion components represent
normalized geometric orientations. The planner publishes `/global_path_metadata`
with reliable, transient-local, keep-last-1 QoS; the follower requests the same
profile. Invalid lengths, headers, frames or geometry clear the follower path.

Standard `/global_path` and the Nav2 action result retain `nav_msgs/Path` with
the same geometry. Build this package together with `r3d_planner` and
`r3d_preprocessor`; see [Installation and startup](../docs/INSTALL.md).
The generated messages, typesupport, headers, manifest and license are installed.

License: [Apache-2.0](LICENSE).


The package also generates `StairDetection` with an explicit `detected` boolean
and stamped point, and `StairStatus` with a path-bound motion permit and gait
transition state. See [Stair gait interfaces](../docs/ARCHITECTURE.md#stair-gait-interfaces).
Rebuild all three packages and migrate external consumers when updating from
the previous two-field metadata and PointStamped stair topic.
