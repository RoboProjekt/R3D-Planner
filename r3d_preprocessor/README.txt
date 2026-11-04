# r3d_preprocessor

Offline voxel-based PCD classification using robot clearance and traversability.
The pcd_analyser executable writes a color-coded <input-name>_analysed.pcd;
pcd_server publishes a selected PCD for visualization.

Use the launch files provided by r3d_planner to load central configuration and
the selected robot profile. Input maps are user-provided. Existing analysis
outputs are not overwritten.

- [Installation and startup](../docs/INSTALL.md)
- [Processing parameters, units and output paths](../docs/CONFIGURATION.md)
- [Processing pipeline and map interfaces](../docs/ARCHITECTURE.md)
