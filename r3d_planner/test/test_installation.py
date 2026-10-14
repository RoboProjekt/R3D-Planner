# Copyright 2026 Bastian Aumer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-FileCopyrightText: 2026 Bastian Aumer
# SPDX-License-Identifier: Apache-2.0

"""Verify installed resources, user configuration and safe ROS entry points."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from ament_index_python.packages import get_package_share_directory
import pytest
import yaml


LICENSE_SHA = 'cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30'
EXECUTABLES = {
    'r3d_planner': ['local_filter', 'path_follower', 'path_test',
                    'pcd_path_planner', 'rviz_interface'],
    'r3d_preprocessor': ['pcd_analyser', 'pcd_server'],
}
LAUNCHES = ['planner.launch.py', 'preprocessor.launch.py',
            'map.launch.py', 'follower.launch.py']


def probe(code, directory, config_dir=None):
    """Import from a neutral working directory, outside the package sources."""
    environment = os.environ.copy()
    environment.pop('R3D_CONFIG_DIR', None)
    if config_dir is not None:
        environment['R3D_CONFIG_DIR'] = str(config_dir)
    result = subprocess.run([sys.executable, '-c', code], cwd=directory,
                            env=environment, capture_output=True, text=True, timeout=25)
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


@pytest.fixture
def user_config(tmp_path):
    share = Path(get_package_share_directory('r3d_planner'))
    central = yaml.safe_load((share / 'config/planner_config.yaml').read_text())
    robot = yaml.safe_load((share / 'config/robots/Go2W.yaml').read_text())
    (tmp_path / 'robots').mkdir()
    cloud = tmp_path / 'input/map.pcd'
    cloud.parent.mkdir()
    cloud.write_text('VERSION .7\nFIELDS x y z rgb\nSIZE 4 4 4 4\nTYPE F F F U\n'
                     'COUNT 1 1 1 1\nWIDTH 3\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\n'
                     'POINTS 3\nDATA ascii\n0 0 0 65280\n0.05 0 0 65280\n0.1 0 0 65280\n')
    central['maps'] = {'pcd_path': 'input/map.pcd', 'map_name': 'input/map.pcd'}
    central['preprocessing']['output_dir'] = 'output'
    central['preprocessing']['min_points_per_voxel'] = 1
    central['preprocessing']['ground_fill'] = False
    central['components']['live_filter']['enabled'] = False
    central['components']['rviz_interface']['enabled'] = False
    robot['robot']['topics']['cmd_vel'] = '/r3d_install_test/cmd_vel'
    robot['robot']['topics']['pointcloud'] = '/r3d_install_test/pointcloud'
    robot['robot']['odometry']['topic'] = '/r3d_install_test/odometry'

    def save():
        (tmp_path / 'planner_config.yaml').write_text(yaml.safe_dump(central))
        (tmp_path / 'robots/Go2W.yaml').write_text(yaml.safe_dump(robot))

    save()
    return tmp_path, cloud, central, robot, save


@pytest.mark.parametrize('package', ['r3d_planner', 'r3d_preprocessor'])
def test_installed_artifacts_and_entry_points(tmp_path, package):
    code = '''
import importlib, importlib.metadata, json
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
pkg = PACKAGE
share = Path(get_package_share_directory(pkg))
dist = importlib.metadata.distribution(pkg)
entries = []
for ep in dist.entry_points:
    if ep.group == 'console_scripts':
        assert callable(ep.load())
        module = importlib.import_module(ep.module)
        assert '/install/' in module.__file__, module.__file__
        entries.append(ep.name)
print(json.dumps({'share': str(share), 'version': dist.version, 'entries': entries}))
'''.replace('PACKAGE', repr(package))
    result = probe(code, tmp_path)
    assert result['version'] == '0.0.1'
    assert sorted(result['entries']) == sorted(EXECUTABLES[package])
    share = Path(result['share'])
    prefix = share.parents[1]
    assert (share / 'package.xml').is_file()
    assert hashlib.sha256((share / 'LICENSE').read_bytes()).hexdigest() == LICENSE_SHA
    assert (prefix / 'share/ament_index/resource_index/packages' / package).is_file()
    for executable in EXECUTABLES[package]:
        path = prefix / 'lib' / package / executable
        assert path.is_file() and not path.is_symlink() and os.access(path, os.X_OK)
    assert not list(prefix.rglob('*.pcd'))
    if package == 'r3d_planner':
        assert sorted(p.name for p in (share / 'launch').glob('*.launch.py')) == sorted(LAUNCHES)
        configs = sorted(str(p.relative_to(share)) for p in (share / 'config').rglob('*.yaml'))
        assert configs == ['config/planner_config.yaml', 'config/r3d_planner_params.yaml',
                           'config/robots/Go2W.yaml']


@pytest.mark.parametrize('mode', ['planner', 'preprocessor', 'map', 'follower'])
def test_installed_default_is_found_and_requires_user_data(tmp_path, mode):
    code = '''
import json
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from r3d_planner.configuration import default_config_path, load_configuration, ConfigurationError
expected = Path(get_package_share_directory('r3d_planner')) / 'config/planner_config.yaml'
assert default_config_path() == expected
try:
    load_configuration(mode=MODE)
except ConfigurationError as error:
    assert 'configure a user-provided PCD path' in str(error), str(error)
else:
    raise AssertionError('Empty shipped input was silently accepted')
print(json.dumps(str(expected)))
'''.replace('MODE', repr(mode))
    assert probe(code, tmp_path).endswith('/config/planner_config.yaml')


def test_installed_override_and_robot_profile(user_config):
    directory, cloud, central, robot, save = user_config
    alternate = directory / 'robots/alternate.yaml'
    robot['robot']['name'] = 'InstallationTest'
    robot['robot']['geometry']['robot_height_cm'] = 90.0
    alternate.write_text(yaml.safe_dump(robot))
    central['robot_config'] = 'robots/alternate.yaml'
    save()
    result = probe('''
import json
import r3d_planner.configuration as module
cfg = module.load_configuration()
assert '/install/' in module.__file__
print(json.dumps(cfg))
''', directory, directory)
    assert result['robot_path'] == str(alternate)
    assert result['robot_name'] == 'InstallationTest'
    assert result['planner']['robot_height_cm'] == 90.0
    assert result['planner']['map_name'] == str(cloud)
    assert result['preprocessor']['output_dir'] == str(directory / 'output')


@pytest.mark.parametrize('form', ['relative', 'absolute', 'tilde'])
def test_installed_user_map_path_forms(user_config, form):
    directory, cloud, central, robot, save = user_config
    value = 'input/map.pcd' if form == 'relative' else str(cloud)
    if form == 'tilde':
        value = str(Path('~') / os.path.relpath(cloud, Path.home()))
    central['maps'] = {'pcd_path': value, 'map_name': value}
    save()
    result = probe('''
import json
from r3d_planner.configuration import load_configuration
print(json.dumps(load_configuration()))
''', directory, directory)
    assert result['planner']['map_name'] == str(cloud)
    assert result['preprocessor']['pcd_path'] == str(cloud)


@pytest.mark.parametrize('form', ['legacy', 'relative', 'absolute', 'tilde'])
def test_installed_output_directory_forms(user_config, form):
    directory, cloud, central, robot, save = user_config
    destination = directory / 'analysis'
    if form == 'legacy':
        del central['preprocessing']['output_dir']
    elif form == 'relative':
        central['preprocessing']['output_dir'] = 'analysis'
    elif form == 'absolute':
        central['preprocessing']['output_dir'] = str(destination)
    else:
        central['preprocessing']['output_dir'] = str(
            Path('~') / os.path.relpath(destination, Path.home()))
    save()
    result = probe('''
import json
from r3d_planner.configuration import load_configuration
print(json.dumps(load_configuration()['preprocessor']['output_dir']))
''', directory, directory)
    assert result == ('' if form == 'legacy' else str(destination))


@pytest.mark.parametrize('bad', [None, True, 1, '   '])
def test_installed_output_directory_type_errors(user_config, bad):
    directory, cloud, central, robot, save = user_config
    central['preprocessing']['output_dir'] = bad
    save()
    result = probe('''
import json
from r3d_planner.configuration import load_configuration, ConfigurationError
try:
    load_configuration()
except ConfigurationError as error:
    print(json.dumps(str(error)))
else:
    raise AssertionError('Invalid output directory was accepted')
''', directory, directory)
    assert 'preprocessing.output_dir' in result


def test_missing_explicit_override_has_no_default_fallback(tmp_path):
    result = probe('''
import json
from r3d_planner.configuration import load_configuration, ConfigurationError
try:
    load_configuration()
except ConfigurationError as error:
    print(json.dumps(str(error)))
else:
    raise AssertionError('Missing explicit override fell back to package defaults')
''', tmp_path, tmp_path / 'missing-override')
    assert str(tmp_path / 'missing-override') in result


@pytest.mark.parametrize('launch', LAUNCHES)
def test_installed_launch_discovery_without_starting_nodes(tmp_path, launch):
    result = subprocess.run(['ros2', 'launch', 'r3d_planner', launch, '--show-args'],
                            cwd=tmp_path, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr


def test_installed_analyzer_read_only_input_and_collision(user_config):
    directory, cloud, central, robot, save = user_config
    prefix = Path(get_package_share_directory('r3d_preprocessor')).parents[1]
    executable = prefix / 'lib/r3d_preprocessor/pcd_analyser'
    target = directory / 'output/map_analysed.pcd'
    before = hashlib.sha256(cloud.read_bytes()).hexdigest()
    cloud.chmod(0o444)
    cloud.parent.chmod(0o555)
    arguments = [str(executable), '--ros-args', '-p', f'pcd_path:={cloud}',
                 '-p', f'output_dir:={target.parent}', '-p', 'min_points_per_voxel:=1',
                 '-p', 'ground_fill:=false']
    try:
        result = subprocess.run(arguments, cwd=directory, capture_output=True,
                                text=True, timeout=20)
        assert result.returncode == 0, result.stdout + result.stderr
        assert target.is_file() and target.stat().st_size > 0
        assert hashlib.sha256(cloud.read_bytes()).hexdigest() == before
        original = target.read_bytes()
        collision = subprocess.run(arguments, cwd=directory, capture_output=True,
                                   text=True, timeout=20)
        assert collision.returncode == 1, collision.stdout + collision.stderr
        assert target.read_bytes() == original
        assert not (cloud.parent / target.name).exists()
    finally:
        cloud.parent.chmod(0o755)


def test_installed_analyzer_invalid_pcd_has_error_exit(user_config):
    directory, cloud, central, robot, save = user_config
    cloud.write_text('Invalid PCD data')
    prefix = Path(get_package_share_directory('r3d_preprocessor')).parents[1]
    result = subprocess.run([str(prefix / 'lib/r3d_preprocessor/pcd_analyser'), '--ros-args',
                             '-p', f'pcd_path:={cloud}',
                             '-p', f'output_dir:={directory / "output"}'],
                            cwd=directory, capture_output=True, text=True, timeout=20)
    assert result.returncode == 1, result.stdout + result.stderr
    assert not (directory / 'output/map_analysed.pcd').exists()


def test_installed_nodes_initialize_with_isolated_inputs(user_config):
    directory, cloud, central, robot, save = user_config
    result = probe('''
import importlib, json
from unittest.mock import patch
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from r3d_planner.configuration import load_configuration
cfg = load_configuration()
classes = [
    ('r3d_planner.r3d_pcd_path', 'GlobalGraphPlanner', cfg['planner']),
    ('r3d_planner.r3d_path_follower', 'PathFollower', cfg['path_follower']),
    ('r3d_planner.r3d_local_filter', 'ObstacleCliffFilter', cfg['live_filter']),
    ('r3d_planner.r3d_rviz_interface', 'RVizInterfaceNode', cfg['rviz_interface']),
    ('r3d_planner.r3d_path_test', 'PathTestTFNode', {}),
    ('r3d_preprocessor.r3d_pcd_analyser', 'PcdToGraphNode', cfg['preprocessor']),
    ('r3d_preprocessor.r3d_pcd_publisher', 'PCDPublisher', {'pcd_path': str(INPUT)}),
]
original = Node.__init__
rclpy.init()
names = []
try:
    for module_name, class_name, values in classes:
        module = importlib.import_module(module_name)
        assert '/install/' in module.__file__
        def init(node, *args, **kwargs):
            kwargs['parameter_overrides'] = [Parameter(k, value=v) for k, v in values.items()]
            original(node, *args, **kwargs)
        with patch.object(Node, '__init__', init):
            node = getattr(module, class_name)()
        names.append(node.get_name())
        node.destroy_node()
finally:
    rclpy.shutdown()
print(json.dumps(names))
'''.replace('INPUT', repr(str(cloud))), directory, directory)
    assert len(result) == 7


def test_source_free_execution_contract(tmp_path):
    code = '''
import json, os
from pathlib import Path
import r3d_planner.configuration as module
assert '/install/' in module.__file__, module.__file__
if os.environ.get('R3D_EXPECT_NO_SOURCE') == '1':
    assert not Path('/r3d-source').exists()
    assert not Path('/work/final1/src').exists()
    assert not Path('/work/final2/src').exists()
    assert not Path('/work/final3/src').exists()
print(json.dumps(module.__file__))
'''
    assert '/install/' in probe(code, tmp_path)
