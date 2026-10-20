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

"""Bind fresh local release evidence to exact sources, tests and Debian archives."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

PACKAGES = ('r3d_interfaces', 'r3d_preprocessor', 'r3d_planner')


def digest(path):
    """Hash the actual bytes, never infer identity from a version or filename."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(root):
    """Require a clean tracked candidate and record only public source identity."""
    root = Path(root).resolve()

    def git(*arguments):
        return subprocess.check_output(['git', '-C', str(root), *arguments], text=True).strip()
    if git('status', '--porcelain=v1'):
        raise ValueError('Release validation requires a clean candidate')
    paths = git('ls-files', '-z').split('\0')
    return {'schema': 1, 'run_id': uuid.uuid4().hex,
            'commit': git('rev-parse', 'HEAD'), 'tree': git('rev-parse', 'HEAD^{tree}'),
            'files': {name: digest(root/name) for name in paths if name}}


def verify_source(context, root):
    """Reject source changes during a run, including helpers and configuration."""
    for name, expected in context['files'].items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or digest(Path(root)/path) != expected:
            raise ValueError('Source identity mismatch: ' + name)


def inventory(root):
    """Record the exact exported test, manifest and binary file set."""
    root = Path(root)
    return {str(path.relative_to(root)): digest(path)
            for path in sorted(root.rglob('*')) if path.is_file()}


def bind_exports(results, context):
    """Bind exports back to the input source and record exact runtime inputs."""
    results = Path(results)
    for path in (results/'tests').rglob('*'):
        if path.is_file():
            relative = str(path.relative_to(results/'tests'))
            if digest(path) != context['files'][relative]:
                raise ValueError('Exported test differs from source: ' + relative)
    for package in PACKAGES:
        manifest = results/'manifests'/package/'package.xml'
        if digest(manifest) != context['files'][package+'/package.xml']:
            raise ValueError('Exported manifest mismatch: ' + package)
    return {name: inventory(results/name) for name in ('debs', 'tests', 'manifests')}


def verify_exports(reference, context, debs, tests, manifests):
    """Reject stale, replaced, missing or additional inputs before installation."""
    if reference['_context'] != context:
        raise ValueError('Build/runtime source or run identity mismatch')
    if not context.get('run_id') or not context.get('commit') or not context.get('tree'):
        raise ValueError('Missing source identity')
    actual = {'debs': inventory(debs), 'tests': inventory(tests),
              'manifests': inventory(manifests)}
    if actual != reference['_exports']:
        raise ValueError('Runtime export hashes or file set differ from build evidence')
    if set(reference)-{'_context', '_exports'} != set(PACKAGES):
        raise ValueError('Incomplete package evidence')
    if len(actual['debs']) != len(PACKAGES):
        raise ValueError('Expected exactly three Debian archives')
    for package in PACKAGES:
        info = reference[package]
        if actual['debs'].get(info['deb']) != info['sha256']:
            raise ValueError('Debian artifact binding mismatch: ' + package)


def main():
    """Use the same small verifier on the host and before runtime installation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['capture', 'verify-exports'])
    parser.add_argument('paths', nargs='+', type=Path)
    args = parser.parse_args()
    if args.mode == 'capture':
        root, output = args.paths
        output.write_text(json.dumps(capture(root), indent=2))
    else:
        reference, context, debs, tests, manifests = args.paths
        verify_exports(json.loads(reference.read_text()), json.loads(context.read_text()),
                       debs, tests, manifests)
    print('RELEASE_CONTEXT_PASS')


if __name__ == '__main__':
    main()
