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

"""Guard against false green release validation and missing phase coverage."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'release_gate.py'
SPEC = importlib.util.spec_from_file_location('r3d_release_gate', SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


@pytest.mark.parametrize('fault', ['failure', 'error', 'skipped', 'count', 'missing',
                                   'empty', 'duplicate', 'malformed', 'coverage', 'wrong_total'])
def test_gate_rejects_bad_evidence(tmp_path, fault):
    report = tmp_path/'report.xml'
    case = '<testcase classname="test.test_contract" name="test_value"/>'
    text = '<testsuite tests="1">' + case + '</testsuite>'
    if fault in ('failure', 'error', 'skipped'):
        text = text.replace('/>', '><' + fault + '/></testcase>')
    elif fault == 'count':
        text = text.replace('tests="1"', 'tests="1" failures="1"')
    elif fault == 'wrong_total':
        text = text.replace('tests="1"', 'tests="2"')
    elif fault == 'empty':
        text = '<testsuite tests="0"/>'
    elif fault == 'duplicate':
        text = text.replace(case, case+case)
    elif fault == 'malformed':
        text = '<invalid'
    if fault != 'missing':
        report.write_text(text)
    arguments = [sys.executable, str(SCRIPT), str(report)]
    if fault == 'coverage':
        expected = tmp_path/'expected.json'
        expected.write_text(json.dumps(['test_contract.py::test_different']))
        arguments += ['--expected', str(expected)]
    result = subprocess.run(arguments, capture_output=True, text=True)
    assert result.returncode == 1
    assert 'RELEASE_GATE_FAILED' in result.stderr


def test_gate_accepts_exact_successful_coverage(tmp_path):
    report = tmp_path/'report.xml'
    report.write_text('<testsuite tests="1"><testcase classname="test.test_contract" '
                      'name="test_value"/></testsuite>')
    expected = tmp_path/'expected.json'
    expected.write_text(json.dumps(['test_contract.py::test_value']))
    result = subprocess.run([sys.executable, str(SCRIPT), str(report),
                             '--expected', str(expected)], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'RELEASE_GATE_PASS: 1 cases' in result.stdout


@pytest.mark.parametrize('fault', ['inventory', 'report'])
def test_ctest_requires_the_correct_successful_checks(tmp_path, monkeypatch, fault):
    names = ['copyright', 'lint_cmake', 'xmllint', 'source_headers']
    inventory = names[:-1] if fault == 'inventory' else names
    monkeypatch.setattr(GATE.subprocess, 'check_output', lambda *args, **kwargs:
                        json.dumps({'tests': [{'name': name} for name in inventory]}))
    reports = tmp_path/'test_results/r3d_interfaces'
    reports.mkdir(parents=True)
    for name in names:
        report = reports/(name+'.xunit.xml')
        report.write_text('<testsuite tests="1" failures="1"><testcase classname="lint" '
                          'name="check"><failure/></testcase></testsuite>')
    with pytest.raises(ValueError):
        GATE.ctest(tmp_path)
