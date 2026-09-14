# Documentation Audit for the PCD-only V2 Branch

Audit date: 2026-09-14. Documentation was compared again with the V2 source,
entry points, package manifests, YAML, and retained maps.

## V2 scope applied

V2 intentionally removes the persisted Pickle workflow while retaining package
boundaries and existing PCD interfaces:

| Removed component | Reason |
|---|---|
| `r3d_preprocessor/r3d_pcd_to_graph.py` and `pcd_to_graph` entry point | Generates `.pkl` graph artifacts |
| `r3d_preprocessor/r3d_voxel_map_publisher.py` and entry point | Loads and visualizes `.pkl` artifacts |
| `r3d_planner/r3d_global_planner.py` and `global_planner` entry point | Loads and plans from `.pkl` artifacts |
| Matching tracked `.pyc` files | Generated artifacts belonging to removed modules |

The retained path is:

```text
raw PCD -> pcd_analyser -> analyzed RGB PCD -> pcd_path_planner
                              \-> pcd_server -> RViz
```

The root README, legacy quick reference, installation guide, package READMEs,
parameter reference, architecture overview, and known-issues report were
updated to describe only this PCD workflow. `r3d_planner/points.txt` remains
unchanged because its action request is still valid for `pcd_path_planner`.

No topics, services, actions, TF frame names, parameter names, YAML values, map
files, or package directories were renamed.
