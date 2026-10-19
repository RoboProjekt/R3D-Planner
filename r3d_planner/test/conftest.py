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
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
import pytest


def pytest_configure(config):
    """Register the phase contract for regular and source-free pytest runs."""
    config.addinivalue_line('markers', 'installed: requires the regular R3D installation')


@pytest.fixture
def installed_share():
    """Resolve real installed resources; no source or build-tree fallback."""
    return Path(get_package_share_directory('r3d_planner'))


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    """Carry installation requirements through the pytest fixture dependency graph."""
    for item in items:
        if 'installed_share' in item.fixturenames:
            item.add_marker(pytest.mark.installed)
