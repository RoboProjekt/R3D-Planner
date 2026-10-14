# Copyright 2026 Bastian Aumer
# SPDX-FileCopyrightText: 2026 Bastian Aumer
# SPDX-License-Identifier: Apache-2.0
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

"""Regression coverage for read-only inputs and non-overwriting PCD output."""
import hashlib
import os
from pathlib import Path

import numpy as np
import open3d as o3d
import pytest

from r3d_preprocessor.output import resolve_output_path, write_point_cloud_exclusive


@pytest.fixture
def cloud():
    result = o3d.geometry.PointCloud()
    result.points = o3d.utility.Vector3dVector(np.array([[0., 0., 0.], [0.1, 0., 0.]]))
    result.colors = o3d.utility.Vector3dVector(np.array([[0., 1., 0.], [1., 0., 1.]]))
    return result


@pytest.fixture
def source(tmp_path, cloud):
    path = tmp_path / 'input/map.pcd'
    path.parent.mkdir()
    assert o3d.io.write_point_cloud(str(path), cloud)
    return path


def test_default_user_data_directory(source, tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'data'))
    assert resolve_output_path(source) == tmp_path / 'data/r3d_preprocessor/map_analysed.pcd'


def test_default_without_xdg(source, monkeypatch):
    monkeypatch.delenv('XDG_DATA_HOME', raising=False)
    assert resolve_output_path(source).parent == Path.home() / '.local/share/r3d_preprocessor'


@pytest.mark.parametrize('fault', ['missing', 'directory', 'suffix'])
def test_invalid_input(tmp_path, fault):
    path = tmp_path / 'bad.pcd'
    if fault == 'directory':
        path.mkdir()
    elif fault == 'suffix':
        path = tmp_path / 'bad.txt'
        path.write_text('not a PCD')
    with pytest.raises(ValueError, match='invalid input PCD'):
        resolve_output_path(path)


def test_read_only_input_and_separate_output(source, tmp_path, cloud):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    source.chmod(0o444)
    source.parent.chmod(0o555)
    try:
        target = resolve_output_path(source, str(tmp_path / 'output'))
        write_point_cloud_exclusive(target, cloud)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
        assert not (source.parent / 'map_analysed.pcd').exists()
        stored = o3d.io.read_point_cloud(str(target))
        assert np.allclose(stored.points, cloud.points)
        assert np.allclose(stored.colors, cloud.colors)
    finally:
        source.parent.chmod(0o755)


@pytest.mark.parametrize('existing', ['file', 'symlink'])
def test_existing_output_is_preserved(tmp_path, cloud, existing):
    target = tmp_path / 'map_analysed.pcd'
    if existing == 'file':
        target.write_bytes(b'foreign data')
    else:
        target.symlink_to('missing-target.pcd')
    with pytest.raises(FileExistsError, match='already exists'):
        write_point_cloud_exclusive(target, cloud)
    if existing == 'file':
        assert target.read_bytes() == b'foreign data'
    else:
        assert target.is_symlink() and os.readlink(target) == 'missing-target.pcd'


def test_open3d_write_failure_leaves_no_output(tmp_path, cloud, monkeypatch):
    target = tmp_path / 'output/map_analysed.pcd'
    monkeypatch.setattr(o3d.io, 'write_point_cloud', lambda *args: False)
    with pytest.raises(OSError, match='could not write PCD'):
        write_point_cloud_exclusive(target, cloud)
    assert list(target.parent.iterdir()) == []


def test_unwritable_output_is_an_error(tmp_path, cloud):
    if os.geteuid() == 0:
        pytest.skip('Root bypasses DAC; execute this regression as a regular user.')
    folder = tmp_path / 'output'
    folder.mkdir()
    folder.chmod(0o555)
    try:
        with pytest.raises(PermissionError):
            write_point_cloud_exclusive(folder / 'map_analysed.pcd', cloud)
    finally:
        folder.chmod(0o755)
