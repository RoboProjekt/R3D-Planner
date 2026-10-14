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

"""Store analyzed user PCDs without modifying inputs or existing outputs."""
import os
from pathlib import Path
import tempfile

import open3d as o3d


def resolve_output_path(input_path, output_dir=''):
    """Keep the analyzed filename while choosing a separate user directory."""
    source = Path(input_path).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != '.pcd':
        raise ValueError(f'Missing or invalid input PCD: {source}')
    if output_dir:
        directory = Path(output_dir).expanduser().resolve()
    else:
        data_home = Path(os.environ.get('XDG_DATA_HOME', '')).expanduser()
        if not data_home.is_absolute():
            data_home = Path.home() / '.local/share'
        directory = data_home / 'r3d_preprocessor'
    return directory / f'{source.stem}_analysed{source.suffix}'


def write_point_cloud_exclusive(output_path, cloud):
    """Publish a complete PCD atomically, refusing existing files and symlinks."""
    target = Path(output_path)
    if os.path.lexists(target):
        raise FileExistsError(f'Output already exists; choose another directory: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
            prefix=f'.{target.stem}-', suffix='.pcd', dir=target.parent, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        if not o3d.io.write_point_cloud(str(temporary), cloud):
            raise OSError(f'Open3D could not write PCD: {target}')
        os.link(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return target
