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
apt-get install -y --no-install-recommends python3-rosdep
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then rosdep init; fi
rosdep update --rosdistro humble
useradd --create-home --uid "$R3D_TEST_UID" r3dtest
mkdir -p /results /work/runtime
chown r3dtest:r3dtest /results /work/runtime
if [ "$1" = build ]; then
  apt-get install -y --no-install-recommends python3-bloom fakeroot debhelper dh-python python3-all python3-pytest
  python3 /r3d-source/scripts/ci/debian_release.py build "${@:2}"
else
  apt-get install -y --no-install-recommends /debs/*.deb
  apt-get check
  rosdep install --from-paths /manifests --ignore-src --rosdistro humble --os=ubuntu:jammy -y
  rosdep check --from-paths /manifests --ignore-src --rosdistro humble --os=ubuntu:jammy
  python3 /release-tools/debian_release.py runtime
fi
