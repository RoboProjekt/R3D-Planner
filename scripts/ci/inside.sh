#!/usr/bin/env bash
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
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive PYTHONNOUSERSITE=1
set +u
source /opt/ros/humble/setup.bash
set -u
apt-get update
apt-get install -y --no-install-recommends python3-colcon-common-extensions python3-rosdep
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then rosdep init; fi
rosdep update --rosdistro humble
manifest_root=/r3d-source
if [ "$1" = runtime ]; then manifest_root=/manifests; fi
rosdep install --from-paths "$manifest_root" --ignore-src --rosdistro humble --os=ubuntu:jammy -y
rosdep check --from-paths "$manifest_root" --ignore-src --rosdistro humble --os=ubuntu:jammy
useradd --create-home --uid "$R3D_TEST_UID" r3dtest
mkdir -p /work/ci /results
chown r3dtest:r3dtest /work/ci /results
if [ "$1" = build ]; then
  python3 /r3d-source/scripts/ci/check.py /r3d-source
  python3 - <<'COPY'
from pathlib import Path
import shutil,os
uid=int(os.environ['R3D_TEST_UID'])
for name in ['r3d_interfaces','r3d_preprocessor','r3d_planner']:
 destination=Path('/work/ci/src')/name
 shutil.copytree(Path('/r3d-source')/name,destination,
                 ignore=shutil.ignore_patterns('__pycache__','*.pyc','.pytest_cache','*.egg-info'))
for path in [Path('/work/ci'),*Path('/work/ci').rglob('*')]:os.chown(path,uid,uid)
COPY
  su --shell /bin/bash r3dtest -c 'set -e; source /opt/ros/humble/setup.bash; cd /work/ci; colcon build --packages-up-to r3d_planner --event-handlers console_cohesion+; source install/setup.bash; colcon test --packages-up-to r3d_planner --event-handlers console_cohesion+; colcon test-result --verbose'
  python3 - <<'EXPORT'
from pathlib import Path
import shutil,os
root=Path('/results')
shutil.copytree('/work/ci/install',root/'install')
shutil.copytree('/work/ci/build',root/'build-results',ignore=shutil.ignore_patterns('*.o'))
(root/'runtime-tests').mkdir()
for name in ['test_installation.py','test_pointcloud.py','test_metadata_interface.py',
             'test_action_interface.py','test_composition_interface.py']:
 shutil.copyfile(Path('/work/ci/src/r3d_planner/test')/name,root/'runtime-tests'/name)
shutil.copyfile('/work/ci/src/r3d_preprocessor/test/test_output.py',root/'runtime-tests/test_output.py')
for name in ['r3d_interfaces','r3d_preprocessor','r3d_planner']:
 destination=root/'manifests'/name;destination.mkdir(parents=True)
 shutil.copyfile(Path('/work/ci/src')/name/'package.xml',destination/'package.xml')
 assert not list((root/'install'/name).rglob('*.pcd'))
for path in root.rglob('*'):os.chown(path,int(os.environ['R3D_TEST_UID']),int(os.environ['R3D_TEST_UID']),follow_symlinks=False)
EXPORT
else
  test ! -e /r3d-source
  test ! -e /work/ci/src
  export R3D_EXPECT_NO_SOURCE=1
  su --shell /bin/bash r3dtest -c 'set -e; source /opt/ros/humble/setup.bash; source /work/ci/install/setup.bash; cd /work/ci; python3 -m pytest -p no:cacheprovider --basetemp=/work/ci/pytest --junitxml=/results/runtime.xml /runtime-tests -q'
fi
