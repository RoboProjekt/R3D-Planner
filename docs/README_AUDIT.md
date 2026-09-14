# V2 Documentation Scope

V2 uses PCD files throughout the offline map and global-planning pipeline:

```text
raw PCD -> pcd_analyser -> analyzed RGB PCD -> pcd_path_planner
                              \-> pcd_server -> RViz
```

`r3d_preprocessor` installs `pcd_analyser` and `pcd_server`.
`r3d_planner` installs `pcd_path_planner`, `local_filter`, `path_follower`,
`rviz_interface`, and `path_test`.

V2 does not include the Pickle graph generator, Pickle marker publisher, or
Pickle-based planner. `r3d_planner/points.txt` remains a valid action request
example for `pcd_path_planner`.

The documentation is split by purpose:

- `README.md` introduces the stack and provides a planning test.
- `INSTALL.md` covers dependencies, build, map preparation, and startup.
- `docs/ARCHITECTURE.md` documents data flow and ROS interfaces.
- `docs/KNOWN_ISSUES.md` records implementation constraints and maintenance
  work.
- Each package README documents its nodes and parameters.

Topics, services, actions, TF frames, parameters, YAML values, map files, and
package names follow the interfaces defined by V2.
