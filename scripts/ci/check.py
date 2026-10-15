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

"""Validate release metadata and document structure without changing files."""
from pathlib import Path
import ast
import hashlib
import re
import sys
import xml.etree.ElementTree as ET

from catkin_pkg.package import parse_package
import yaml


def check(root):
    """Check all three packages and current user-facing Markdown resources."""
    packages = ['r3d_interfaces', 'r3d_preprocessor', 'r3d_planner']
    expected = hashlib.sha256((root/'LICENSE').read_bytes()).hexdigest()
    for name in packages:
        directory = root/name
        package = parse_package(str(directory))
        assert package.name == name and package.version == '0.0.1'
        assert package.licenses == ['Apache-2.0']
        assert hashlib.sha256((directory/'LICENSE').read_bytes()).hexdigest() == expected
        assert not list(directory.rglob('*.pcd')), 'bundled maps are forbidden'
        ET.parse(directory/'package.xml')
        for source in directory.rglob('*.py'):
            ast.parse(source.read_text())
    for source in (root/'r3d_planner/config').rglob('*.yaml'):
        assert isinstance(yaml.safe_load(source.read_text()), dict)
    workflow = yaml.safe_load((root/'.github/workflows/ros2-humble.yml').read_text())
    assert workflow['permissions'] == {'contents': 'read'}
    assert set(workflow['on']) == {'push', 'pull_request', 'workflow_dispatch'}
    assert workflow['jobs']['humble']['runs-on'] == 'ubuntu-22.04'
    steps = workflow['jobs']['humble']['steps']
    assert steps[0]['uses'] == 'actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1'
    assert steps[0]['with']['persist-credentials'] is False
    assert steps[1]['run'] == 'bash scripts/ci/run_humble.sh'
    documents = [root/'README.md', root/'INSTALL.md', root/'r3d_interfaces/README.md']
    documents += list((root/'docs').glob('*.md'))
    for document in documents:
        text = document.read_text()
        assert sum(line.startswith('```') for line in text.splitlines()) % 2 == 0, document
        for link in re.findall(r'\]\(([^)]+)\)', text):
            if link.startswith(('https:', 'http:', 'mailto:', '#', '/')):
                continue
            link = link.split('#', 1)[0].strip('<>')
            assert (document.parent/link).exists(), (document, link)
    print('METADATA_XML_YAML_SYNTAX_DOC_STRUCTURE_PASS')


if __name__ == '__main__':
    check(Path(sys.argv[1]).resolve())
