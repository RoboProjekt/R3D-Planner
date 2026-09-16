# r3d_preprocessor

`r3d_preprocessor` is the offline map-processing package of the R3D stack. It
reads 3D point clouds in PCD format, voxelizes and classifies them using robot
dimensions, and produces a color-coded voxel point cloud
(`*_analysed.pcd`).

The package can publish PCD maps as `PointCloud2`. It contains no launch files
of its own or custom ROS interfaces. Central launches are provided by r3d_planner.

## Build type and installation

- Build type: `ament_python`
- Python package: `r3d_preprocessor`
- `setup.py` installs the Python nodes, Ament resource, and `package.xml`.
- The existing `maps/` directory is **not** installed into the package share.
  The central loader resolves source map paths and forwards an absolute runtime path.

See `../INSTALL.md` for dependencies and build commands.

## Processing model

`pcd_analyser` loads a PCD through Open3D. It can supplement floor points
using local point density, filter occupied voxels, and apply a cylindrical
collision model. Voxels are classified as normally traversable (`floor`),
traversable only with the smaller robot radius (`narrow`), or obstacles.
Neighboring traversable voxels are classified as flat or as stair access based
on their height difference.

### Color classes in an analyzed PCD

| Color | Class |
|---|---|
| Green | normally traversable floor |
| Cyan | narrow area, clear only for `robot_narrow_radius_cm` |
| Yellow | access to a step/stair edge |
| Magenta | occupied, non-traversable voxel |

## Nodes and executables

| Executable | Node name | Purpose | Input/output |
|---|---|---|---|
| `pcd_analyser` | `pcd_to_graph_node` | Analyze traversability and produce a color-coded PCD | reads `pcd_path`, writes `<name>_analysed.pcd` |
| `pcd_server` | `pcd_publisher` | Publish one PCD as PointCloud2 | `/map_pointcloud` |

`r3d_pcd_voxel_publisher.py` has no console entry point and cannot be started
with `ros2 run`.

## Topics

| Topic | Type | Publisher | QoS | Purpose |
|---|---|---|---|---|
| `/map_pointcloud` | `sensor_msgs/msg/PointCloud2` | `pcd_server` | depth 1, `TRANSIENT_LOCAL` | PCD in configured `map_frame` (default `map`); includes RGB if present |

The package subscribes to no topics, provides no services or actions, and
publishes no TF transforms.

## Analysis-node parameters

`pcd_analyser` declares these parameters. Normal launch loads geometry from the
selected robot YAML, voxel/step settings from `shared`, and other analysis
settings from `preprocessing` in `r3d_planner/config/planner_config.yaml`.
The defaults below describe standalone developer invocations, not a separate
normal configuration workflow.

| Parameter | Default | Unit | Actual behavior |
|---|---:|---|---|
| `pcd_path` | `environment.pcd` | file path | Input; expands `~` and resolves an absolute path |
| `voxel_size_cm` | 5.0 | cm | Open3D voxel edge length |
| `min_step_height_cm` | 5.0 | cm | Height differences up to this value are flat |
| `max_step_height_cm` | 25.0 | cm | Largest height difference accepted as a step |
| `min_points_per_sqm` | 10.0 | points/m² | Density value for floor filling; at least three points per analysis cell are required |
| `min_points_per_voxel` | 3 | points | Minimum number of hits for an occupied voxel |
| `floor_height_tolerance` | 0.02 | m | Z tolerance of a floor cluster; `pcd_analyser` checks `2*tolerance + 0.02 m` |
| `ground_fill` | `true` | boolean | Enable density filling and neighborhood plane filling |
| `robot_base_clearance_cm` | 10.0 | cm | Lower start of collision checks above the floor voxel |
| `robot_narrow_radius_cm` | 30.0 | cm | Smaller collision radius for narrow-area detection |
| `robot_radius_cm` | 40.0 | cm | Normal collision radius |
| `robot_height_cm` | 80.0 | cm | Collision-cylinder height |
| `analysis_grid_size_cm` | 20.0 | cm | XY cell size for density analysis |
| `cluster_gap_threshold_cm` | 20.0 | cm | Vertical gap separating height clusters |
| `fill_plane_iterations` | 2 | count | Maximum filling iterations |
| `fill_plane_search_radius` | 2 | voxels | Floor-neighbor search radius |
| `fill_plane_min_neighbors` | 4 | count | Required existing floor neighbors |

### Map-publisher parameters

| Executable | Parameter | Default | Behavior |
|---|---|---|---|
| `pcd_server` | `pcd_path` | `environment.pcd` | PCD to load and publish |
| `pcd_server` | `map_frame` | `map` | Coordinate label, no transform applied |

## Usage: color-coded PCD

Set `maps.pcd_path` and corresponding `maps.map_name` in the central YAML.
Select robot geometry using `robot_config`, then:

```bash
ros2 launch r3d_planner preprocessor.launch.py
```

The process exits after writing `<input-name>_analysed.pcd`. An existing
output is overwritten. Geometry or processing changes require regenerating this
artifact. They require no workspace rebuild or re-sourcing.

Publish the centrally selected analyzed output:

```bash
ros2 launch r3d_planner map.launch.py
```

In RViz use the configured map frame, `/map_pointcloud`, Transient Local
durability and RGB8. This package remains independent of any odometry source;
the analysis node consumes no Odometry or TF.

See `../docs/CONFIGURATION.md` for ownership, restart behavior and all settings.
Direct `ros2 run` is available for developer overrides, but does not load
the central YAML automatically.

## Dependencies

### Declared dependencies

`rclpy`, `sensor_msgs`, and `numpy`.

### Additional runtime dependency

Open3D. `package.xml` does not yet provide complete rosdep metadata; see
`../INSTALL.md` and `../docs/KNOWN_ISSUES.md`.

## Integration

`pcd_analyser` writes the analyzed PCD consumed by
`r3d_planner/pcd_path_planner`. `pcd_server` publishes the same file for
visualization. Both components treat its coordinates as the configured map coordinates;
neither applies a transform.
