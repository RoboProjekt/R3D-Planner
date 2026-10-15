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
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
results=$(mktemp -d /tmp/r3d-ci.XXXXXXXX)
image=ros:humble-ros-base@sha256:860e53793ccf575e5369b5e9a19939de2bfcfb46a299954d06f54f2af54fed19
builder_uid=$(id -u)
if [ "$builder_uid" = 0 ]; then builder_uid=1000; fi
created=()
cleanup() {
  for container in "${created[@]}"; do docker rm -f "$container" >/dev/null 2>&1 || true; done
  echo "CI logs and artifacts: $results"
}
trap cleanup EXIT
# Mount only this checkout read-only and a task-specific result directory.
cid=$(docker create --label codex.task=r3d-ci --mount "type=bind,src=$repo,dst=/r3d-source,readonly" --mount "type=bind,src=$results,dst=/results" -e R3D_TEST_UID="$builder_uid" -e ROS_DOMAIN_ID=231 -e ROS_LOCALHOST_ONLY=1 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp -e PYTHONNOUSERSITE=1 -e RCUTILS_COLORIZED_OUTPUT=0 "$image" bash /r3d-source/scripts/ci/inside.sh build)
created+=("$cid")
docker start --attach "$cid" 2>&1 | tee "$results/build.log"
test "$(docker inspect --format '{{.State.ExitCode}}' "$cid")" -eq 0
cp "$repo/scripts/ci/inside.sh" "$results/inside.sh"
mkdir "$results/runtime-results"
# No source checkout or build tree is exposed to the runtime container.
cid=$(docker create --label codex.task=r3d-ci --mount "type=bind,src=$results/install,dst=/work/ci/install,readonly" --mount "type=bind,src=$results/runtime-tests,dst=/runtime-tests,readonly" --mount "type=bind,src=$results/manifests,dst=/manifests,readonly" --mount "type=bind,src=$results/inside.sh,dst=/inside.sh,readonly" --mount "type=bind,src=$results/runtime-results,dst=/results" -e R3D_TEST_UID="$builder_uid" -e ROS_DOMAIN_ID=232 -e ROS_LOCALHOST_ONLY=1 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp -e PYTHONNOUSERSITE=1 -e RCUTILS_COLORIZED_OUTPUT=0 "$image" bash /inside.sh runtime)
created+=("$cid")
docker start --attach "$cid" 2>&1 | tee "$results/runtime.log"
test "$(docker inspect --format '{{.State.ExitCode}}' "$cid")" -eq 0
echo CI_LOCAL_BUILD_AND_SOURCEFREE_PASS
