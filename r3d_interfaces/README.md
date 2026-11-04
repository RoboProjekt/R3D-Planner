# r3d_interfaces

This `ament_cmake`/rosidl package generates
`r3d_interfaces/msg/PathWithMetadata` for Python and C++ consumers:

```text
nav_msgs/Path path
bool[] narrow
```

`narrow[i]` belongs to `path.poses[i]`. The complete geometric path and exactly
one flag per pose travel atomically. Quaternion components represent normalized
geometric orientations, not flags. The planner publishes `/global_path_metadata`
with reliable, transient-local, keep-last-1 QoS; the follower requests the same
profile. Invalid lengths, headers, frames or geometry clear the follower path.

Standard `/global_path` and the Nav2 action result retain `nav_msgs/Path` with
the same geometry. Build this package together with `r3d_planner` and
`r3d_preprocessor`; see [Installation and startup](../docs/INSTALL.md).
The generated messages, typesupport, headers, manifest and license are installed.

License: [Apache-2.0](LICENSE).
