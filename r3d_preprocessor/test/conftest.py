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

"""Record standard Jammy pybuild tests without external wrapper selection."""
import json
from pathlib import Path

import pytest


def debian_source_root():
    """Identify the supported Debian build tree, not source or installed tests."""
    directory = Path(__file__).resolve().parent.parent
    if directory.name != 'build' or directory.parent.parent.name != '.pybuild':
        return None
    source = directory.parents[2]
    if all((source / 'debian' / name).is_file() for name in ('control', 'rules')):
        return source
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Create a native build report; leave ordinary pytest and colcon unchanged."""
    source = debian_source_root()
    if source is not None and not config.option.collectonly:
        if config.option.markexpr or config.option.keyword or config.option.deselect:
            raise pytest.UsageError('External selection is forbidden in the Debian build phase')
        config.option.xmlpath = str(source / 'build-tests.xml')


def pytest_collection_modifyitems(config, items):
    """Record every preprocessor build case as a mandatory build obligation."""
    source = debian_source_root()
    if source is not None and not config.option.collectonly:
        nodes = [item.nodeid for item in items]
        (source / 'build-phase.json').write_text(json.dumps(
            {'phase': 'debian-build', 'expected': nodes,
             'selected': nodes, 'installed_required': []}, indent=2))
