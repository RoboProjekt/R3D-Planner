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

"""Classify actual installation requirements without skipping any default test."""
import json
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Register the phase contract for regular and source-free pytest runs."""
    config.addinivalue_line('markers', 'installed: requires the regular R3D installation')
    source = debian_source_root()
    if source is not None and not config.option.collectonly:
        if config.option.markexpr or config.option.keyword or config.option.deselect:
            raise pytest.UsageError('External selection is forbidden in the Debian build phase')
        config.option.xmlpath = str(source / 'build-tests.xml')


@pytest.fixture
def installed_share():
    """Resolve real installed resources; no source or build-tree fallback."""
    return Path(get_package_share_directory('r3d_planner'))


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Carry installation requirements through the pytest fixture dependency graph."""
    for item in items:
        if 'installed_share' in item.fixturenames:
            item.add_marker(pytest.mark.installed)

    source = debian_source_root()
    if source is not None and not config.option.collectonly:
        deferred = [item for item in items if item.get_closest_marker('installed')]
        selected = [item for item in items if not item.get_closest_marker('installed')]
        data = {'phase': 'debian-build',
                'expected': [item.nodeid for item in items],
                'selected': [item.nodeid for item in selected],
                'installed_required': [item.nodeid for item in deferred]}
        (source / 'build-phase.json').write_text(json.dumps(data, indent=2))
        config.hook.pytest_deselected(items=deferred)
        items[:] = selected


def debian_source_root():
    """Identify the supported Jammy pybuild layout, never a regular ROS test run."""
    directory = Path(__file__).resolve().parent.parent
    if directory.name != 'build' or directory.parent.parent.name != '.pybuild':
        return None
    source = directory.parents[2]
    if all((source / 'debian' / name).is_file() for name in ('control', 'rules')):
        return source
    return None
