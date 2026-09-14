# Audit of Previous Documentation Against the Code

Audit date: 2026-09-14. Every existing README and the supplementary
`Filters.txt` were compared with `package.xml`, `setup.py`, YAML, and all Python
nodes. No functional code was changed.

| File | Previous content | Finding against current code | Documentation update |
|---|---|---|---|
| `README_r3d_planner.txt` | Short installation list with global pip commands, only the PCD workflow, and `/home/basti/...` paths | PCD executable names were current, but dependencies, build/sourcing, TF, safety, Pickle workflow, and absence of launch files were missing; the global pip environment is inconsistent on the analyzed machine | Replaced with a portable quick reference and links to complete guides |
| `r3d_preprocessor/README.txt` | Described `pcd_to_graph`, `voxel_map_publisher`, and `pcd_server`; claimed `/r3d_global_graph_edges` | Current publisher only emits `/r3d_global_voxel_map`; `pcd_analyser` and newer parameters were absent | Added nodes, topics, QoS, all parameters, both artifact paths, dependencies, and verified commands |
| `r3d_planner/README.txt` | Mentioned only `global_planner` and `local_filter`; claimed a default `nav_graph.pkl` | Six executables exist; the default map is neither present nor installed; action, topics, service, TF, PCD planner, RViz interface, and path follower were missing | Replaced with a complete package reference and safety notes |
| `r3d_preprocessor/Filters.txt` | Eight parameters and a stale absolute path | Both analysis nodes declare 15 parameters | Added all parameters with defaults, units, behavior, and portable example |
| `r3d_planner/points.txt` | Action example and site-specific waypoints | Action name and type match the code; `planner_id` is not evaluated; coordinates remain site-specific data | Left unchanged and explained in the planner README |

The previous repository also lacked a standalone installation guide, complete
architecture description, and known-issues report. `INSTALL.md`,
`docs/ARCHITECTURE.md`, and `docs/KNOWN_ISSUES.md` now provide them.
