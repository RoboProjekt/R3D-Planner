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

"""Verify installed Debian ownership, resources and the generated ROS interface."""
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from r3d_interfaces.msg import PathWithMetadata


def command(*arguments):
    """Require a successful real command and preserve its decoded output."""
    return subprocess.check_output(arguments, text=True).strip()


def main():
    """Inspect only the fresh runtime installation, never workspace artifacts."""
    debs, results = map(Path, sys.argv[1:])
    assert sys.executable == '/usr/bin/python3'
    for path in ('/r3d-source', '/work/debian-release', '/work/ci/install'):
        assert not Path(path).exists(), path
    modules = {'r3d_planner': 'r3d_planner.r3d_local_filter',
               'r3d_preprocessor': 'r3d_preprocessor.r3d_pcd_analyser',
               'r3d_interfaces': PathWithMetadata.__module__}
    rows = []
    for name, module in modules.items():
        package = 'ros-humble-' + name.replace('_', '-')
        artifacts = list(debs.glob(package + '_*.deb'))
        assert len(artifacts) == 1
        artifact = artifacts[0]
        status = command('dpkg-query', '-W', '-f=${Status}|${Version}|${Depends}',
                         package).split('|')
        assert status[0] == 'install ok installed' and status[1] == '0.0.1-0jammy'
        assert command('dpkg-deb', '-f', str(artifact), 'Version') == status[1]
        assert command('dpkg-deb', '-f', str(artifact), 'Package') == package
        files = command('dpkg-query', '-L', package).splitlines()
        loaded = Path(importlib.import_module(module).__file__)
        owner = command('dpkg-query', '-S', str(loaded))
        assert owner.startswith(package + ': ') and str(loaded) in files
        share = Path(get_package_share_directory(name))
        assert str(share) == '/opt/ros/humble/share/' + name
        assert ET.parse(share/'package.xml').findtext('version') == '0.0.1'
        expected = [loaded, share/'LICENSE', share/'package.xml', share/'CHANGELOG.rst']
        if name == 'r3d_planner':
            expected += list((share/'config').rglob('*.yaml'))
            expected += list((share/'launch').glob('*.py'))
            assert len(list((share/'launch').glob('*.py'))) == 4
            assert (share/'config/robots/Go2W.yaml').is_file()
            assert 'ros-humble-r3d-interfaces' in status[2]
            assert 'ros-humble-r3d-preprocessor' in status[2]
        if name == 'r3d_interfaces':
            assert 'ros-humble-rosidl-default-runtime' in status[2]
        assert not [path for path in files if path.lower().endswith('.pcd')]
        with tempfile.TemporaryDirectory(prefix='r3d-deb-extract-') as temporary:
            subprocess.run(['dpkg-deb', '-x', str(artifact), temporary], check=True)
            for path in expected:
                assert str(path) in files
                assert path.read_bytes() == (Path(temporary)/str(path).lstrip('/')).read_bytes()
        assert not command('dpkg', '--verify', package)
        rows.append({'package': package, 'version': status[1], 'depends': status[2],
                     'module': str(loaded), 'owner': owner, 'share': str(share),
                     'bytes': artifact.stat().st_size,
                     'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()})
    interface = command('ros2', 'interface', 'show', 'r3d_interfaces/msg/PathWithMetadata')
    (results/'dpkg-smoke.json').write_text(json.dumps(
        {'packages': rows, 'python': sys.version, 'interface': interface}, indent=2))
    print('DPKG_OWNERSHIP_RESOURCE_INTERFACE_PASS')


if __name__ == '__main__':
    main()
