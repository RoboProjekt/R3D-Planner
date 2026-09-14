import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/bauya/Desktop/R3D-Planner/ros2_r3d_planner_ws/install/r3d_planner'
