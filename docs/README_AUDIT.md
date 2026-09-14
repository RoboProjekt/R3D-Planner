# V1 Documentation Scope

V1 supports two offline map formats and matching global planners:

```text
raw PCD -> pcd_analyser -> analyzed RGB PCD -> pcd_path_planner
raw PCD -> pcd_to_graph -> Pickle graph      -> global_planner
```

`global_planner` and `pcd_path_planner` expose the same node name, action, and
path topics. Run exactly one of them at a time. `pcd_server` publishes PCD maps;
`voxel_map_publisher` visualizes Pickle graphs.

The documentation is split by purpose:

- `README.md` introduces both pipelines and provides a PCD planning test.
- `INSTALL.md` covers dependencies, build, map preparation, and startup.
- `docs/ARCHITECTURE.md` documents data flow and ROS interfaces.
- `docs/KNOWN_ISSUES.md` records implementation constraints and maintenance
  work.
- Each package README documents its nodes and parameters.

`r3d_planner/points.txt` contains a valid action request example and
site-specific example coordinates. Topics, services, actions, TF frames,
parameters, YAML values, map files, and package names follow the interfaces
defined by V1.
