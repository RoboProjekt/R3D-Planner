# Indoor mapping and flythrough

Run the commands below from `mapping/`. The LiDAR mapper reads the Hesai ROS 2 topic. The contour builder combines registered LiDAR, calibrated RGB-D observations and fitted building parts into a photo-textured GLB and an Isaac Sim USDZ with collision geometry.

## LiDAR map

Use ROS 2 Humble with its Python environment, SciPy and the packages in `tools/requirements-lidar.txt`. Set `HESAI_PYTHON` to the interpreter containing KISS-ICP if it is outside the default mapping environment. Choose fresh output directories for each run.

```bash
bash tools/run_hesai_mapper.sh --bag /path/to/rosbag --output .runtime/run --level-floors
python3 tools/export_hesai_surfaces.py .runtime/run --output .runtime/flythrough
python3 flythrough.py --z-up .runtime/flythrough/karte_dicht.pcd
```

The viewer uses GLFW and PyOpenGL. WASD moves, dragging with the left mouse button turns, and Space / left Ctrl changes elevation.

## Textured mesh from a prepared survey

The mesh environment uses NumPy, SciPy, Open3D, OpenCV, Pillow and the OpenUSD Python bindings (`pxr`). Set `R3D_SCAN_ROOT` to the prepared survey directory. The table lists the inputs read by the contour builder.

| Location in the survey | Inputs |
| --- | --- |
| `mapped/` | `measured.pcd` and `outputs.npz` with registered points, scan offsets, timestamps and trajectory |
| `architecture/` | `scene.npz` with the building frame, structural mesh, stair bounds and tread elevations |
| `fine/` | `cameras.npz`, `rgb_depth.npy` and `rail.npz` |
| `photomesh_hd/` | `aligned.npz` with calibrated poses |
| `clean_building/` | `collision.npz`, numbered photos in `photos/` and corresponding masks in `exclusion/` |

```bash
export R3D_SCAN_ROOT=/path/to/prepared-survey
python3 tools/publish_building_contours.py
```

Open `$R3D_SCAN_ROOT/contours_evidence/Gebaeude.usdz` in Isaac Sim. For the standalone mesh flythrough, place the survey's `Kameraposen.npz` next to `Gebaeude.glb`.

```bash
python3 flythrough.py "$R3D_SCAN_ROOT/contours_evidence/Gebaeude.glb"
```

F7, F8 and F9 jump to the staircase, landing and corridor. The camera pose file supplies these bookmarks and the viewer intrinsics.

## Which parts transfer to another survey?

`tools/filter_surface_evidence.py` checks candidate surfaces against LiDAR rays and depth observations from distinct camera positions. Repeated frames from a stationary camera count as one observation. The filter also removes sheets occupying gaps between measured railing posts. It runs before triangle generation and photo texturing.

The current architectural reconstruction includes fitted bounds for this building's stairs, landings and glazing. A different building needs its own structural inputs and review of those bounds. The survey data, ROS bags and generated models are kept outside Git.

Run the filter regression tests from the mesh environment.

```bash
PYTHONPATH=tools python3 -m unittest discover -s tools/tests -p 'test_surface_evidence.py'
```
