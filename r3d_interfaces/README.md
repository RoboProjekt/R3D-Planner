# r3d_interfaces

Version 0.0.1, Apache-2.0. This ament_cmake/rosidl package generates
`r3d_interfaces/msg/PathWithMetadata` for Python and C++ consumers:

```text
nav_msgs/Path path
bool[] narrow
```

`narrow[i]` belongs to `path.poses[i]`. All flags and the complete path travel
atomically, avoiding pairing races between independent topics. The path contains
normalized geometric orientations; no orientation component is a flag.

The planner publishes `/global_path_metadata` with reliable, transient-local,
keep-last-1 QoS; the follower requests the same profile. Invalid lengths,
headers, frames or geometry clear the follower path. Standard `/global_path`
and the Nav2 action result retain `nav_msgs/Path` with the identical path.

Build/install this package together with `r3d_planner` and `r3d_preprocessor`.
The generated message, typesupport, headers, manifest and LICENSE are installed.
See the repository INSTALL.md and central development protocol for the verified
scope and migration. M02 obstacle monitoring is not implemented by this package.


Build-time checks explicitly target own sources, not the generated Debian/ROSIDL
build tree. Copyright/CMake/XML checks remain active, and two source-header cases
cover CMakeLists.txt and PathWithMetadata.msg. The local Debian gate verifies
these reports and the generated installed interface; it performs no Bloom release.
