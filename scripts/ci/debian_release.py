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

"""Orchestrate local-only Bloom packaging and mandatory installed test evidence."""
import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path
import re
import shlex
import shutil
import subprocess

from release_gate import coverage, ctest, junit

PACKAGES = ('r3d_interfaces', 'r3d_preprocessor', 'r3d_planner')


def run(command, logfile, cwd=None, user=False, env=None):
    """Record a real exit code, with optional unprivileged ROS shell execution."""
    if user:
        script = 'set -e\nsource /opt/ros/humble/setup.bash\n'
        if cwd:
            script += 'cd ' + shlex.quote(str(cwd)) + '\n'
        command = ['su', '--shell', '/bin/bash', 'r3dtest', '-c',
                   script + shlex.join(command)]
        cwd = None
    with Path(logfile).open('w') as output:
        result = subprocess.run(command, cwd=cwd, env=env, stdout=output,
                                stderr=subprocess.STDOUT, check=False)
    Path(str(logfile)+'.exit').write_text(str(result.returncode)+'\n')
    if result.returncode:
        raise RuntimeError(f'Exit {result.returncode}: {command}; log={logfile}')
    return Path(logfile).read_text()


def collect(directory, logfile, marker=None):
    """Collect the actual complete or installation-required pytest node IDs."""
    command = ['/usr/bin/python3', '-m', 'pytest', '-p', 'no:cacheprovider',
               '--collect-only', '-q', 'test']
    if marker:
        command += ['-m', marker]
    text = run(command, logfile, directory, user=True)
    nodes = re.findall(r'^test/(test_[^\n]+\.py::[^\n]+)$', text, re.M)
    match = re.search(r'(\d+)(?:/\d+)? tests? (?:collected|selected)', text)
    if not nodes or len(nodes) != len(set(nodes)) or match is None:
        raise ValueError(f'Incomplete collection inventory: {logfile}')
    # The lines themselves are the identities; pytest versions spell summary differently.
    return nodes


def ownership_tree(path):
    """Grant only the temporary build and result trees to the ordinary test user."""
    uid = int(os.environ['R3D_TEST_UID'])
    for entry in (path, *path.rglob('*')):
        os.chown(entry, uid, uid)


def record_environment(results, phase):
    """Keep actual tool versions even when a later gate rejects a test report."""
    packages = ('cmake', 'debhelper', 'python3-bloom', 'python3-pytest',
                'python3-colcon-core', 'python3-setuptools', 'python3-rosdep',
                'python3-numpy', 'python3-scipy', 'python3-networkx',
                'python3-open3d', 'python3-yaml')
    versions = {}
    for package in packages:
        result = subprocess.run(['dpkg-query', '-W', '-f=${Version}', package],
                                capture_output=True, text=True)
        versions[package] = result.stdout if result.returncode == 0 else None
    data = {'os_release': Path('/etc/os-release').read_text(),
            'ros_distro': os.environ.get('ROS_DISTRO'), 'python': sys.version,
            'architecture': platform.machine(), 'versions': versions}
    (results/('environment-'+phase+'.json')).write_text(json.dumps(data, indent=2))


def build(source, results, failure_probe):
    """Generate standard rules, build and strictly inspect the resulting tests."""
    from catkin_pkg.package import parse_package
    from bloom.generators.debian.generate_cmd import place_template_files, process_template_files
    from bloom.generators.rosdebian import RosDebianGenerator

    work = Path('/work/debian-release')
    work.mkdir(parents=True)
    packages = {name: parse_package(source/name) for name in PACKAGES}
    generator = RosDebianGenerator()
    generator.rosdistro, generator.os_name = 'humble', 'ubuntu'
    generator.install_prefix, generator.debian_inc = '/opt/ros/humble', '0'
    generator.packages = packages
    exports = results/'tests'
    exports.mkdir()
    evidence = {}
    for name, package in packages.items():
        destination = work/name
        shutil.copytree(source/name, destination, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.pytest_cache', '*.egg-info'))
        if name == 'r3d_preprocessor' and failure_probe:
            (destination/'test/test_release_failure_probe.py').write_text(
                (source/'r3d_preprocessor/test/test_output.py').read_text().split('"""')[0] +
                '"""Deliberate isolated failure control."""\n\n\n'
                'def test_intentional_release_gate_failure():\n'
                '    assert False, "deliberate isolated release gate control"\n')
        os.chdir(destination)
        substitutions = generator.get_subs(package, 'jammy', {})
        place_template_files('.', package.get_build_type())
        for template in process_template_files('.', substitutions):
            Path(template).unlink()
        rules = (destination/'debian/rules').read_text()
        if rules.count('dh_auto_test || true') != 1:
            raise ValueError('Bloom template changed: review local gate assumptions')
        generated = results/'generated'/name
        generated.mkdir(parents=True)
        for filename in ('control', 'rules', 'copyright', 'changelog'):
            shutil.copyfile(destination/'debian'/filename, generated/filename)
        ownership_tree(destination)
    ownership_tree(work)
    for name in PACKAGES:
        directory = work/name
        # A package must never validate a previous installation of itself at build time.
        state = subprocess.run(['dpkg-query', '-W', '-f=${Status}',
                                'ros-humble-'+name.replace('_', '-')],
                               capture_output=True, text=True)
        if state.returncode == 0 and state.stdout == 'install ok installed':
            raise ValueError('Preinstalled build target: ' + name)
        run(['apt-get', 'build-dep', '-y', '--no-install-recommends', str(directory)],
            results/(name+'-build-deps.log'))
        run(['dpkg-checkbuilddeps'], results/(name+'-checkbuilddeps.log'), directory)
        record_environment(results, name)
        expected = []
        if name != 'r3d_interfaces':
            expected = collect(directory, results/(name+'-collection.log'))
        report = directory/'build-tests.xml'
        environment = os.environ.copy()
        environment['PYBUILD_TEST_PYTEST'] = '1'
        environment['PYBUILD_TEST_ARGS'] = (
            '-p no:cacheprovider -m "not installed" --junitxml='+str(report))
        run(['dpkg-buildpackage', '-us', '-uc', '-b'],
            results/(name+'-build.log'), directory, user=True, env=environment)
        if name == 'r3d_interfaces':
            shutil.copytree(directory/'.obj-x86_64-linux-gnu/Testing', results/'interface-ctest')
            shutil.copytree(directory/'.obj-x86_64-linux-gnu/test_results',
                            results/'interface-xunit')
            data = ctest(directory/'.obj-x86_64-linux-gnu')
        else:
            # Preserve failed evidence before the strict validator raises.
            if report.is_file():
                shutil.copyfile(report, results/(name+'-build-tests.xml'))
            actual = junit(report)
            deferred = []
            if name == 'r3d_planner':
                deferred = collect(directory, results/(name+'-installed-collection.log'),
                                   'installed')
            coverage(expected, actual+deferred)
            shutil.copytree(source/name/'test', exports/name/'test')
            data = {'expected': expected, 'build_cases': actual, 'installed_required': deferred}
        candidates = list(work.glob('ros-humble-'+name.replace('_', '-')+'_*.deb'))
        if len(candidates) != 1:
            raise ValueError(f'Expected one binary: {candidates}')
        artifact = candidates[0]
        data['deb'] = artifact.name
        data['sha256'] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        data['bytes'] = artifact.stat().st_size
        data['control'] = subprocess.check_output(['dpkg-deb', '-f', str(artifact)], text=True)
        (results/'debs').mkdir(exist_ok=True)
        shutil.copyfile(artifact, results/'debs'/artifact.name)
        evidence[name] = data
        (results/'build-evidence.json').write_text(json.dumps(evidence, indent=2))
        # Install peers only after their successful build/test validation.
        run(['apt-get', 'install', '-y', '--no-install-recommends', str(artifact)],
            results/(name+'-peer-install.log'))
    (results/'manifests').mkdir()
    for name in PACKAGES:
        (results/'manifests'/name).mkdir()
        shutil.copyfile(source/name/'package.xml', results/'manifests'/name/'package.xml')
    print('DEBIAN_BUILD_TEST_GATE_PASS')


def runtime(results):
    """Require the entire Python suite against a fresh, source-free Debian install."""
    for path in ('/r3d-source', '/work/debian-release', '/work/ci/install'):
        if Path(path).exists():
            raise ValueError('Source/build overlay in runtime: ' + path)
    record_environment(results, 'runtime')
    reference = json.loads(Path('/build-evidence.json').read_text())
    summary = {}
    for name in ('r3d_preprocessor', 'r3d_planner'):
        directory = Path('/release-tests')/name
        work = Path('/work/runtime')/name
        work.mkdir(parents=True)
        ownership_tree(work)
        report = results/(name+'-installed.xml')
        environment = {**os.environ, 'R3D_EXPECT_NO_SOURCE': '1'}
        run(['/usr/bin/python3', '-m', 'pytest', '-p', 'no:cacheprovider',
             '--basetemp='+str(work/'pytest'), '--junitxml='+str(report), 'test', '-q'],
            results/(name+'-installed.log'), directory, user=True, env=environment)
        actual = junit(report)
        coverage(reference[name]['expected'], actual)
        summary[name] = {'passed': len(actual), 'failed': 0, 'errors': 0, 'skipped': 0}
    run(['/usr/bin/python3', '/release-tools/debian_smoke.py', '/debs', str(results)],
        results/'smoke.log', user=True)
    (results/'installed-evidence.json').write_text(json.dumps(summary, indent=2))
    print('DEBIAN_INSTALLED_TEST_GATE_PASS')


def main():
    """Keep a single auditable entry point for each isolated stage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['build', 'runtime'])
    parser.add_argument('--source', type=Path, default=Path('/r3d-source'))
    parser.add_argument('--results', type=Path, default=Path('/results'))
    parser.add_argument('--failure-probe', action='store_true')
    args = parser.parse_args()
    args.results.mkdir(exist_ok=True)
    for name in ('DEB_BUILD_OPTIONS', 'DEB_BUILD_PROFILES'):
        if 'nocheck' in os.environ.get(name, '').split():
            raise ValueError('nocheck is forbidden in the release validation')
    if os.environ.get('PYTEST_ADDOPTS'):
        raise ValueError('External pytest selection flags are not allowed')
    if args.phase == 'build':
        build(args.source, args.results, args.failure_probe)
    else:
        runtime(args.results)


if __name__ == '__main__':
    main()
