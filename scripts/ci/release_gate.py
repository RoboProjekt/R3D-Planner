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

"""Reject failed, missing or incomplete test evidence, including tolerant Bloom builds."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import subprocess
import xml.etree.ElementTree as ET


def junit(path):
    """Read actual case identities and reject every failure, error or skip."""
    root = ET.parse(path).getroot()
    suites = list(root.iter('testsuite'))
    if not suites:
        raise ValueError(f'No test suites: {path}')
    for suite in suites:
        for name in ('errors', 'failures', 'skipped'):
            if int(suite.get(name, '0')):
                raise ValueError(f'{path}: {name}={suite.get(name)}')
    for suite in suites:
        if not list(suite.iterfind('testsuite')):
            if int(suite.get('tests', '-1')) != len(suite.findall('testcase')):
                raise ValueError(f'Inconsistent test count: {path}')
    cases = list(root.iter('testcase'))
    if not cases:
        raise ValueError(f'Empty test report: {path}')
    identities = []
    for case in cases:
        if any(case.find(kind) is not None for kind in ('failure', 'error', 'skipped')):
            raise ValueError(f'Unsuccessful case: {path}: {case.attrib}')
        module = case.get('classname', '').split('.')[-1]
        identities.append(module + '.py::' + case.attrib['name'])
    if len(set(identities)) != len(identities):
        raise ValueError(f'Duplicate test identity: {path}')
    return identities


def coverage(expected, actual):
    """Compare identities, rather than trusting totals or a process exit alone."""
    if Counter(expected) != Counter(actual):
        missing = sorted((Counter(expected)-Counter(actual)).elements())
        extra = sorted((Counter(actual)-Counter(expected)).elements())
        raise ValueError(f'Test coverage mismatch: missing={missing}, extra={extra}')


def ctest(directory):
    """Require the four intended interface checks and their successful reports."""
    # Debhelper runs plain ctest, which writes xUnit and LastTest.log but no
    # dashboard Test.xml. Read the actual generated CTest inventory separately.
    raw = subprocess.check_output(['ctest', '--test-dir', str(directory),
                                   '--show-only=json-v1'], text=True)
    tests = json.loads(raw)['tests']
    expected = {'copyright', 'lint_cmake', 'xmllint', 'source_headers'}
    names = [test['name'] for test in tests]
    if set(names) != expected or len(names) != len(expected):
        raise ValueError(f'Unexpected CTest discovery: {names}')
    reports = list(Path(directory).glob('test_results/r3d_interfaces/*.xunit.xml'))
    if len(reports) != len(expected):
        raise ValueError(f'Missing interface xUnit reports: {reports}')
    counts = {path.stem: len(junit(path)) for path in reports}
    return {'ctest_runs': len(tests), 'xunit_cases': counts}


def main():
    """Provide a small nonzero-exit verifier usable independently of the builder."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reports', nargs='+', type=Path)
    parser.add_argument('--expected', type=Path)
    args = parser.parse_args()
    try:
        actual = [item for report in args.reports for item in junit(report)]
        if args.expected:
            coverage(json.loads(args.expected.read_text()), actual)
    except (OSError, ValueError, KeyError, ET.ParseError) as error:
        print('RELEASE_GATE_FAILED: ' + str(error), file=sys.stderr)
        return 1
    print(f'RELEASE_GATE_PASS: {len(actual)} cases')
    return 0


if __name__ == '__main__':
    sys.exit(main())
