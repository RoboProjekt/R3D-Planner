#!/bin/bash

# Pfad zum Workspace
WS_DIR=~/Desktop/R3D-Planner/ros2_r3d_planner_ws
MAPS_DIR=$WS_DIR/src/r3d_preprocessor/maps

# --- KONFIGURATION ---
DEFAULT_PCD="HomeLab_test2_LIO.pcd"
DEFAULT_PKL="nav_graph_step20_voxel10.pkl" 

PCD_FILE=${1:-$DEFAULT_PCD}
PKL_FILE=${2:-$DEFAULT_PKL}

echo "------------------------------------------------"
echo "R3D Planner Launch System (Full Stack)"
echo "------------------------------------------------"
echo "PCD Datei (Optik):  $PCD_FILE"
echo "PKL Datei (Logik):  $PKL_FILE"
echo "Pfad:               $MAPS_DIR"
echo "------------------------------------------------"

if [ ! -f "$MAPS_DIR/$PCD_FILE" ]; then
    echo "ERROR: PCD Datei nicht gefunden!"
    exit 1
fi
if [ ! -f "$MAPS_DIR/$PKL_FILE" ]; then
    echo "ERROR: PKL Datei nicht gefunden!"
    exit 1
fi

source $WS_DIR/install/setup.bash

# Trap: Beendet alle Hintergrundprozesse beim Skript-Abbruch (STRG+C)
trap "kill 0" EXIT

# 1. Voxel Map Publisher
echo "[1/6] Starte Voxel Map Publisher..."
ros2 run r3d_preprocessor voxel_map_publisher --ros-args -p graph_path:=$MAPS_DIR/$PKL_FILE &

# 2. PCD Server
echo "[2/6] Starte PCD Server..."
ros2 run r3d_preprocessor pcd_server --ros-args -p pcd_path:=$MAPS_DIR/$PCD_FILE &

# 3. Global Planner
echo "[3/6] Starte Global Planner..."
ros2 run r3d_planner global_planner --ros-args -p map_name:=$MAPS_DIR/$PKL_FILE &

# 4. Local Filter
echo "[4/6] Starte Local Filter..."
ros2 run r3d_planner local_filter &

# 5. Path Follower
echo "[5/6] Starte Path Follower..."
ros2 run r3d_planner path_follower &

# 6. RViz 3D Interface (NEU)
# Ermöglicht die Lokalisierung und Zielsetzung via RViz Tools
echo "[6/6] Starte RViz 3D Interface..."
ros2 run r3d_planner rviz_interface &

echo "Warte 3 Sekunden auf Node-Startup..."
sleep 3

echo "------------------------------------------------"
echo "✅ SYSTEM BEREIT"
echo "------------------------------------------------"

wait
