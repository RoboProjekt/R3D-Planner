"""Launch-time parameter forwarding shared by the two entry points."""
from launch import LaunchDescription
from launch.actions import OpaqueFunction, LogInfo
from launch.conditions import IfCondition
from launch_ros.actions import Node
from .configuration import load_configuration


def configured_nodes(context, mode):
    cfg = load_configuration(mode=mode)
    actions = [LogInfo(msg=f"R3D config: {cfg['config_path']}; robot: {cfg['robot_path']}")]
    if mode == 'preprocessor':
        actions.append(Node(package='r3d_preprocessor', executable='pcd_analyser',
                            parameters=[cfg['preprocessor']], output='screen'))
    elif mode == 'follower':
        actions.append(Node(package='r3d_planner', executable='path_follower',
                            parameters=[cfg['path_follower']], output='screen'))
    elif mode == 'map':
        actions.append(Node(package='r3d_preprocessor', executable='pcd_server',
                            parameters=[{'pcd_path': cfg['planner']['map_name'],
                                         'map_frame': cfg['planner']['map_frame']}],
                            output='screen'))
    else:
        actions.append(Node(package='r3d_planner', executable='pcd_path_planner',
                            parameters=[cfg['planner']], output='screen'))
        for section, executable in [('live_filter', 'local_filter'),
                                    ('rviz_interface', 'rviz_interface')]:
            enabled = str(cfg['components'][section]['enabled']).lower()
            actions.append(Node(package='r3d_planner', executable=executable,
                                parameters=[cfg[section]], output='screen',
                                condition=IfCondition(enabled)))
    return actions


def description(mode):
    return LaunchDescription([OpaqueFunction(function=configured_nodes, kwargs={'mode': mode})])
