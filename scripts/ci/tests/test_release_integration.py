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

"""Exercise native Debian phases and reject stale or incomplete release evidence."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parents[1]


def load(name):
    """Load the standalone CI tools without installing a package or ROS overlay."""
    spec = importlib.util.spec_from_file_location(name, TOOLS/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CONTEXT = load('release_context')
load('release_gate')
VALIDATION = load('release_validation')
RELEASE = load('debian_release')


@pytest.fixture
def bound_exports(tmp_path):
    """Provide isolated synthetic byte identities, not actual Debian packages."""
    context = {'run_id': 'new-run', 'commit': 'current-commit', 'tree': 'current-tree',
               'files': {'example': 'unused'}}
    for directory in ('debs', 'tests', 'manifests'):
        (tmp_path/directory).mkdir()
    reference = {'_context': copy.deepcopy(context)}
    for package in CONTEXT.PACKAGES:
        name = package+'.deb'
        archive = tmp_path/'debs'/name
        archive.write_bytes(package.encode())
        reference[package] = {'deb': name, 'sha256': CONTEXT.digest(archive)}
    (tmp_path/'tests/check.py').write_text('synthetic test input')
    (tmp_path/'manifests/package.xml').write_text('synthetic manifest input')
    reference['_exports'] = {name: CONTEXT.inventory(tmp_path/name)
                             for name in ('debs', 'tests', 'manifests')}
    return tmp_path, context, reference


def test_current_exports_are_accepted(bound_exports):
    directory, context, reference = bound_exports
    CONTEXT.verify_exports(reference, context, directory/'debs',
                           directory/'tests', directory/'manifests')


@pytest.mark.parametrize('fault', [
    'old-run', 'old-commit', 'old-tree', 'changed-deb', 'missing-deb', 'extra-deb',
    'changed-test', 'extra-test', 'changed-manifest', 'missing-package', 'wrong-deb-hash'])
def test_stale_or_changed_inputs_are_rejected(bound_exports, fault):
    directory, context, reference = bound_exports
    if fault.startswith('old-'):
        key = {'old-run': 'run_id', 'old-commit': 'commit', 'old-tree': 'tree'}[fault]
        context[key] = 'old'
    elif fault == 'missing-package':
        del reference['r3d_interfaces']
    elif fault == 'wrong-deb-hash':
        reference['r3d_interfaces']['sha256'] = 'wrong'
    else:
        file = {'changed-deb': 'debs/r3d_interfaces.deb',
                'missing-deb': 'debs/r3d_interfaces.deb', 'extra-deb': 'debs/old.deb',
                'changed-test': 'tests/check.py', 'extra-test': 'tests/extra.py',
                'changed-manifest': 'manifests/package.xml'}[fault]
        path = directory/file
        if fault == 'missing-deb':
            path.unlink()
        else:
            path.write_bytes(b'changed bytes')
    with pytest.raises(ValueError):
        CONTEXT.verify_exports(reference, context, directory/'debs',
                               directory/'tests', directory/'manifests')


def test_changed_source_is_rejected(tmp_path):
    file = tmp_path/'source.py'
    file.write_text('original')
    context = {'files': {'source.py': CONTEXT.digest(file)}}
    file.write_text('different')
    with pytest.raises(ValueError, match='Source identity'):
        CONTEXT.verify_source(context, tmp_path)


def test_missing_completed_runtime_is_rejected(bound_exports):
    directory, context, reference = bound_exports
    (directory/'build-evidence.json').write_text(json.dumps(reference))
    with pytest.raises(FileNotFoundError):
        VALIDATION.validate(directory/'unused-ci', directory, context)


def test_failed_process_is_not_hidden_by_reports(tmp_path):
    with pytest.raises(RuntimeError, match='Exit 7'):
        RELEASE.run([sys.executable, '-c', 'raise SystemExit(7)'], tmp_path/'process.log')
    assert (tmp_path/'process.log.exit').read_text().strip() == '7'


@pytest.mark.parametrize('package', ['r3d_planner', 'r3d_preprocessor'])
@pytest.mark.parametrize('phase', ['pybuild', 'ordinary', 'external-selection'])
def test_native_phase_has_no_ordinary_pytest_deselection(tmp_path, package, phase):
    """Run real nested pytest on synthetic tests with the real phase hooks."""
    source = tmp_path/'package'
    (source/'debian').mkdir(parents=True)
    for name in ('control', 'rules'):
        (source/'debian'/name).write_text('synthetic Debian context')
    build = source/'.pybuild/cpython3_3.10/build' if phase != 'ordinary' else source/'ordinary'
    tests = build/'test'
    tests.mkdir(parents=True)
    shutil.copyfile(ROOT/package/'test/conftest.py', tests/'conftest.py')
    # Only the synthetic nested test imports this fixture stub; no R3D module is loaded.
    stub = tmp_path/'stubs/ament_index_python'
    stub.mkdir(parents=True)
    (stub/'__init__.py').write_text('')
    (stub/'packages.py').write_text('def get_package_share_directory(name):\n    return name\n')
    marker = '@pytest.mark.installed\n' if package == 'r3d_planner' else ''
    (tests/'test_synthetic.py').write_text(
        'import pytest\n\ndef test_build_case():\n    assert True\n\n' + marker +
        'def test_install_case():\n    assert True\n')
    command = [sys.executable, '-B', '-m', 'pytest', '-p', 'no:cacheprovider', 'test', '-q']
    if phase == 'external-selection':
        command += ['-k', 'build_case']
    result = subprocess.run(command, cwd=build, capture_output=True, text=True,
                            env={**os.environ, 'PYTHONPATH': str(stub.parent)})
    if phase == 'external-selection':
        assert result.returncode != 0
        assert 'External selection is forbidden' in result.stderr
    elif phase == 'ordinary':
        assert result.returncode == 0, result.stdout+result.stderr
        assert '2 passed' in result.stdout
        assert not (source/'build-phase.json').exists()
        assert not (source/'build-tests.xml').exists()
    else:
        assert result.returncode == 0, result.stdout+result.stderr
        data = json.loads((source/'build-phase.json').read_text())
        assert len(data['expected']) == 2
        required = 1 if package == 'r3d_planner' else 0
        assert len(data['installed_required']) == required
        assert len(data['selected']) == 2-required
        cases = list(ET.parse(source/'build-tests.xml').iter('testcase'))
        assert len(cases) == 2-required
        assert not any(case.find('skipped') is not None for case in cases)


@pytest.mark.parametrize('prefix', ['test/', '.pybuild/cpython3_3.10/build/test/',
                                   '/work/package/.pybuild/cpython3_3.10/build/test/'])
def test_pybuild_node_identity_preserves_case_and_parameters(prefix):
    node = prefix+'test_output.py::test_invalid_input[missing]'
    assert RELEASE.canonical_nodes([node]) == ['test_output.py::test_invalid_input[missing]']
