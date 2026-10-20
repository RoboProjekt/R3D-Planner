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

"""Run all mandatory local release phases and bind their actual evidence."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from release_context import capture, digest, verify_exports, verify_source
from release_gate import coverage, junit


def validate(ci, debian, context):
    """Require every phase and identity; successful package builds alone do not pass."""
    reference = json.loads((debian/'build-evidence.json').read_text())
    built = reference['_context']
    if any(built[name] != context[name] for name in ('commit', 'tree', 'files')):
        raise ValueError('Debian build belongs to another source candidate')
    verify_exports(reference, built, debian/'debs', debian/'tests', debian/'manifests')
    runtime_context = json.loads((debian/'runtime-results/source-context.json').read_text())
    if runtime_context != built:
        raise ValueError('Missing or mismatched completed Debian runtime context')
    expected_runtime = []
    python_cases = 0
    for package in ('r3d_preprocessor', 'r3d_planner'):
        expected = reference[package]['expected']
        regular = junit(ci/'build-results'/package/'pytest.xml')
        coverage(expected, regular)
        python_cases += len(regular)
        build = junit(debian/(package+'-build-tests.xml'))
        coverage(reference[package]['build_cases'], build)
        coverage(expected, build+reference[package]['installed_required'])
        installed = junit(debian/'runtime-results'/(package+'-installed.xml'))
        coverage(expected, installed)
        expected_runtime += [node for node in expected if not node.startswith(
            ('test_copyright.py::', 'test_flake8.py::', 'test_pep257.py::'))]
        manifest = ci/'manifests'/package/'package.xml'
        if digest(manifest) != context['files'][package+'/package.xml']:
            raise ValueError('Colcon manifest belongs to another source')
    runtime = junit(ci/'runtime-results/runtime.xml')
    coverage(expected_runtime, runtime)
    interface_cases = 0
    for name in reference['r3d_interfaces']['xunit_cases']:
        filename = name+'.xml'
        regular = junit(ci/'build-results/r3d_interfaces/test_results/r3d_interfaces'/filename)
        binary = junit(debian/'interface-xunit/r3d_interfaces'/filename)
        coverage(binary, regular)
        interface_cases += len(regular)
    controls = junit(debian/'gate-controls.xml')
    smoke = json.loads((debian/'runtime-results/dpkg-smoke.json').read_text())
    for item in smoke['packages']:
        package = item['package'].removeprefix('ros-humble-').replace('-', '_')
        if item['sha256'] != reference[package]['sha256']:
            raise ValueError('Installed artifact does not match the build')
    if len(smoke['packages']) != 3:
        raise ValueError('Incomplete installed package evidence')
    return {'python_package_cases': python_cases, 'interface_xunit_cases': interface_cases,
            'normal_sourcefree_cases': len(runtime), 'gate_controls': len(controls),
            'debian_postinstall_cases': python_cases, 'fail': 0, 'error': 0, 'skip': 0}


def execute(root, results, name, script, pattern):
    """Execute a fresh complete runner; do not accept an artifact reuse argument."""
    log = results/(name+'.log')
    with log.open('w') as output:
        process = subprocess.run(['bash', str(root/script)], stdout=output,
                                 stderr=subprocess.STDOUT, timeout=2100, check=False)
    text = log.read_text()
    print('\n'.join(text.splitlines()[-12:]), flush=True)
    if process.returncode:
        raise RuntimeError(f'{name}: exit {process.returncode}; {log}')
    paths = re.findall(pattern, text)
    if len(paths) != 1:
        raise ValueError('Missing or ambiguous runner evidence directory: ' + name)
    return Path(paths[0])


def main():
    """Prepare a local candidate only, without any publication or release command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--results', type=Path)
    args = parser.parse_args()
    results = args.results or Path(tempfile.mkdtemp(prefix='r3d-release.'))
    if results.exists() and any(results.iterdir()):
        raise ValueError('Release results must be new and empty')
    results.mkdir(parents=True, exist_ok=True)
    context = capture(args.source)
    (results/'source-context.json').write_text(json.dumps(context, indent=2))
    print('LOCAL RELEASE TEST VALIDATION: '+str(results), flush=True)
    ci = execute(args.source, results, 'humble', Path('scripts/ci/run_humble.sh'),
                 r'CI logs and artifacts: (\S+)')
    verify_source(context, args.source)
    debian = execute(args.source, results, 'debian', Path('scripts/ci/run_humble_debian.sh'),
                     r'Debian logs and artifacts: (\S+)')
    verify_source(context, args.source)
    counts = validate(ci, debian, context)
    evidence = {'source': context, 'colcon_results': str(ci), 'debian_results': str(debian),
                'counts': counts, 'classification': 'LOCAL RELEASE TEST VALIDATION',
                'official_integration': 'NOT VERIFIED', 'maintainer_release_approval': 'REQUIRED'}
    sealed = {}
    for prefix, directory in (('colcon', ci), ('debian', debian)):
        for path in directory.rglob('*'):
            if path.is_file() and path.suffix in ('.xml', '.json', '.deb', '.exit'):
                sealed[prefix+'/'+str(path.relative_to(directory))] = digest(path)
    evidence['evidence_sha256'] = sealed
    (results/'release-evidence.json').write_text(json.dumps(evidence, indent=2))
    print(json.dumps(counts), flush=True)
    print('LOCAL_RELEASE_TEST_GATE_PASS: '+str(results), flush=True)


if __name__ == '__main__':
    main()
