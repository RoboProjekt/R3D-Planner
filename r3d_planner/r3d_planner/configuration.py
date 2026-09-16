"""Resolve the two-level runtime configuration without generating ROS YAML."""
import math
import os
from pathlib import Path

import yaml


class ConfigurationError(ValueError):
    """An invalid or unavailable runtime configuration."""


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently overriding earlier values."""


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ConfigurationError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def default_config_path():
    """Use live source files, never silently use a stale installed copy."""
    explicit = os.environ.get('R3D_CONFIG_DIR')
    if explicit:
        return Path(explicit).expanduser().resolve() / 'planner_config.yaml'
    source = Path(__file__).resolve().parent.parent / 'config/planner_config.yaml'
    if source.is_file():
        return source
    from ament_index_python.packages import get_package_share_directory
    installed = Path(get_package_share_directory('r3d_planner')) / 'config/planner_config.yaml'
    if installed.is_symlink():
        return installed.resolve()
    raise ConfigurationError(
        'Live configuration not found. Build once with colcon build --symlink-install '
        'or set R3D_CONFIG_DIR to the source r3d_planner/config directory. '
        'Copied install YAML is deliberately not used.')


def read_yaml(path):
    try:
        with path.open(encoding='utf-8') as stream:
            value = yaml.load(stream, Loader=UniqueLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f'{path}: {exc}') from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f'{path}: expected a YAML mapping')
    return value


def keys(value, expected, location):
    if not isinstance(value, dict):
        raise ConfigurationError(f'{location}: expected a YAML mapping')
    missing = set(expected) - set(value)
    extra = set(value) - set(expected)
    if missing or extra:
        raise ConfigurationError(
            f'{location}: missing keys {sorted(missing)}; unknown keys {sorted(extra)}')


def number(value, location, integer=False, zero=False):
    valid_type = type(value) is int if integer else type(value) in (int, float)
    if not valid_type or not math.isfinite(value) or value < 0 or (not zero and value == 0):
        kind = 'integer' if integer else 'number'
        bound = '>= 0' if zero else '> 0'
        raise ConfigurationError(f'{location}: expected a finite {kind} {bound}')


def text(value, location, frame=False, topic=False):
    if not isinstance(value, str) or not value or any(c.isspace() for c in value):
        raise ConfigurationError(f'{location}: expected a nonempty string without whitespace')
    if frame and (value.startswith('/') or '//' in value):
        raise ConfigurationError(f'{location}: TF frame must not start with /')
    if topic:
        from rclpy.validate_full_topic_name import validate_full_topic_name
        try:
            validate_full_topic_name(value)
        except Exception as exc:
            raise ConfigurationError(f'{location}: invalid absolute ROS topic: {exc}') from exc


def ros_parameters(values, integer_keys=()):
    """Normalize YAML integer spelling for declared ROS double parameters."""
    return {key: float(value) if type(value) in (int, float) and key not in integer_keys else value
            for key, value in values.items()}


def load_configuration(path=None, mode='planner'):
    if mode not in ('planner', 'preprocessor', 'map', 'follower'):
        raise ConfigurationError(f'Unknown launch mode: {mode}')
    path = Path(path).resolve() if path else default_config_path()
    cfg = read_yaml(path)
    keys(cfg, ['robot_config', 'maps', 'shared', 'preprocessing', 'planner',
               'components', 'live_filter', 'rviz_interface', 'path_follower'], str(path))
    text(cfg['robot_config'], 'robot_config')
    robot_path = Path(cfg['robot_config'])
    if robot_path.is_absolute():
        raise ConfigurationError('robot_config must be relative to planner_config.yaml')
    robot_path = (path.parent / robot_path).resolve()
    if not robot_path.is_relative_to(path.parent):
        raise ConfigurationError('robot_config must stay inside the configuration directory')
    robot = read_yaml(robot_path)
    keys(robot, ['robot'], str(robot_path))
    robot = robot['robot']
    keys(robot, ['name', 'geometry', 'odometry', 'topics'], 'robot')
    text(robot['name'], 'robot.name')
    geometry = robot['geometry']
    keys(geometry, ['robot_height_cm', 'robot_narrow_radius_cm', 'robot_radius_cm',
                    'robot_base_clearance_cm'], 'robot.geometry')
    for key, value in geometry.items():
        number(value, 'robot.geometry.' + key, zero=key == 'robot_base_clearance_cm')
    if geometry['robot_narrow_radius_cm'] > geometry['robot_radius_cm']:
        raise ConfigurationError('robot_narrow_radius_cm must be <= robot_radius_cm')
    if geometry['robot_base_clearance_cm'] >= geometry['robot_height_cm']:
        raise ConfigurationError('robot_base_clearance_cm must be < robot_height_cm')
    odometry = robot['odometry']
    keys(odometry, ['topic', 'odom_frame', 'base_frame'], 'robot.odometry')
    text(odometry['topic'], 'robot.odometry.topic', topic=True)
    for key in ('odom_frame', 'base_frame'):
        text(odometry[key], 'robot.odometry.' + key, frame=True)
    keys(robot['topics'], ['pointcloud', 'cmd_vel'], 'robot.topics')
    for key, value in robot['topics'].items():
        text(value, 'robot.topics.' + key, topic=True)
    keys(cfg['maps'], ['pcd_path', 'map_name'], 'maps')
    maps = {}
    for key, value in cfg['maps'].items():
        if not isinstance(value, str) or not value:
            raise ConfigurationError('maps.' + key + ': expected a path')
        maps[key] = str((path.parent / Path(value).expanduser()).resolve())
    selected = maps['pcd_path' if mode == 'preprocessor' else 'map_name']
    if not Path(selected).is_file() or Path(selected).suffix.lower() != '.pcd':
        raise ConfigurationError(f'Missing PCD map: {selected}')
    keys(cfg['shared'], ['voxel_size_cm', 'min_step_height_cm', 'max_step_height_cm'], 'shared')
    for key, value in cfg['shared'].items():
        number(value, 'shared.' + key, zero=key == 'min_step_height_cm')
    if cfg['shared']['min_step_height_cm'] >= cfg['shared']['max_step_height_cm']:
        raise ConfigurationError('min_step_height_cm must be < max_step_height_cm')
    preprocessing = cfg['preprocessing']
    keys(preprocessing, ['min_points_per_sqm', 'min_points_per_voxel', 'floor_height_tolerance',
                         'ground_fill', 'analysis_grid_size_cm', 'cluster_gap_threshold_cm',
                         'fill_plane_iterations', 'fill_plane_search_radius',
                         'fill_plane_min_neighbors'], 'preprocessing')
    for key, value in preprocessing.items():
        if key == 'ground_fill':
            if type(value) is not bool:
                raise ConfigurationError('ground_fill must be boolean')
        else:
            number(value, 'preprocessing.' + key,
                   integer=key in ('min_points_per_voxel', 'fill_plane_iterations',
                                   'fill_plane_search_radius', 'fill_plane_min_neighbors'),
                   zero=key == 'fill_plane_iterations')
    planner = cfg['planner']
    keys(planner, ['map_frame', 'odometry_timeout_sec', 'narrow_cost_multiplier',
                   'stair_cost_multiplier', 'path_line_width', 'path_z_offset_voxels'], 'planner')
    text(planner['map_frame'], 'planner.map_frame', frame=True)
    if len({planner['map_frame'], odometry['odom_frame'], odometry['base_frame']}) != 3:
        raise ConfigurationError('map, odom and base frames must be distinct')
    for key, value in planner.items():
        if key != 'map_frame':
            number(value, 'planner.' + key, zero=key == 'path_z_offset_voxels')
    if min(planner['narrow_cost_multiplier'], planner['stair_cost_multiplier']) < 1:
        raise ConfigurationError('cost multipliers must be >= 1 to preserve the A* heuristic')
    keys(cfg['components'], ['live_filter', 'rviz_interface'], 'components')
    for key, value in cfg['components'].items():
        keys(value, ['enabled'], 'components.' + key)
        if type(value['enabled']) is not bool:
            raise ConfigurationError('components.' + key + '.enabled must be boolean')
    live = cfg['live_filter']
    keys(live, ['min_height', 'max_height', 'min_step_height', 'max_step_height',
                'cliff_width', 'stair_roi_x_min', 'stair_roi_x_max', 'stair_roi_width',
                'min_reliable_distance', 'stair_min_points', 'cliff_roi_x_min',
                'cliff_roi_x_max', 'cliff_min_ground_points', 'cliff_wall_points',
                'cliff_wall_height'], 'live_filter')
    for key, value in live.items():
        number(value, 'live_filter.' + key,
               integer=key in ('stair_min_points', 'cliff_min_ground_points', 'cliff_wall_points'))
    for low, high in [('min_height', 'max_height'), ('min_step_height', 'max_step_height'),
                      ('stair_roi_x_min', 'stair_roi_x_max'),
                      ('cliff_roi_x_min', 'cliff_roi_x_max')]:
        if live[low] >= live[high]:
            raise ConfigurationError(f'live_filter.{low} must be < {high}')
    rviz = cfg['rviz_interface']
    keys(rviz, ['match_radius', 'publish_map_odom'], 'rviz_interface')
    number(rviz['match_radius'], 'rviz_interface.match_radius')
    if type(rviz['publish_map_odom']) is not bool:
        raise ConfigurationError('rviz_interface.publish_map_odom must be boolean')
    follower = cfg['path_follower']
    keys(follower, ['lookahead_distance', 'max_linear_speed', 'max_angular_speed',
                    'stop_distance', 'goal_tolerance', 'control_period_sec', 'obstacle_x_min',
                    'obstacle_half_width', 'max_angular_speed_narrow', 'angle_threshold',
                    'steering_gain', 'narrow_speed_factor', 'turning_speed_factor'],
         'path_follower')
    for key, value in follower.items():
        number(value, 'path_follower.' + key)
    if follower['obstacle_x_min'] >= follower['stop_distance']:
        raise ConfigurationError('obstacle_x_min must be < stop_distance')
    for key in ('narrow_speed_factor', 'turning_speed_factor'):
        if follower[key] > 1:
            raise ConfigurationError(key + ' must be <= 1')
    # ROS double parameters must remain doubles even if YAML uses integer notation.
    common = dict(ros_parameters(geometry), odometry_topic=odometry['topic'],
                  odom_frame=odometry['odom_frame'], base_frame=odometry['base_frame'])
    shared = ros_parameters(cfg['shared'])
    return {
        'config_path': str(path), 'robot_path': str(robot_path), 'robot_name': robot['name'],
        'preprocessor': {**ros_parameters(geometry), **shared,
                         **ros_parameters(preprocessing, (
                             'min_points_per_voxel', 'fill_plane_iterations',
                             'fill_plane_search_radius', 'fill_plane_min_neighbors')),
                         'pcd_path': maps['pcd_path']},
        'planner': {**common, **shared, **ros_parameters(planner), 'map_name': maps['map_name']},
        'live_filter': {**ros_parameters(live, (
                            'stair_min_points', 'cliff_min_ground_points', 'cliff_wall_points')),
                        'pointcloud_topic': robot['topics']['pointcloud']},
        'rviz_interface': {'match_radius': float(rviz['match_radius']),
                           'publish_map_odom': rviz['publish_map_odom'],
                           'map_frame': planner['map_frame'], 'odom_frame': odometry['odom_frame']},
        'components': cfg['components'],
        'path_follower': {'odometry_topic': odometry['topic'], 'odom_frame': odometry['odom_frame'],
                          'base_frame': odometry['base_frame'],
                          **ros_parameters(follower), 'map_frame': planner['map_frame'],
                          'odometry_timeout_sec': float(planner['odometry_timeout_sec']),
                          'cmd_vel_topic': robot['topics']['cmd_vel']},
    }
