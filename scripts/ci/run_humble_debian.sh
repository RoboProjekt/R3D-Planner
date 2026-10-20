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
probe=()
if [ "${1:-}" = --failure-probe ] && [ "$#" -eq 1 ]; then
  probe=(--failure-probe)
elif [ "$#" -ne 0 ]; then
  echo "Usage: $0 [--failure-probe]" >&2
  exit 2
fi
results=$(mktemp -d /tmp/r3d-debian.XXXXXXXX)
image=ros:humble-ros-base@sha256:860e53793ccf575e5369b5e9a19939de2bfcfb46a299954d06f54f2af54fed19
builder_uid=$(id -u)
if [ "$builder_uid" = 0 ]; then builder_uid=1000; fi
/usr/bin/python3 -B "$repo/scripts/ci/release_context.py" capture "$repo" "$results/source-context.json"
created=()
cleanup() {
  for container in "${created[@]}"; do docker rm -f "$container" >/dev/null 2>&1 || true; done
  echo "Debian logs and artifacts: $results"
}
trap cleanup EXIT
cid=$(docker create --label codex.task=r3d-debian-gate --mount "type=bind,src=$repo,dst=/r3d-source,readonly" --mount "type=bind,src=$results,dst=/results" -e R3D_TEST_UID="$builder_uid" -e ROS_DOMAIN_ID=94 -e ROS_LOCALHOST_ONLY=1 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp -e PYTHONNOUSERSITE=1 "$image" bash /r3d-source/scripts/ci/debian_inside.sh build "${probe[@]}")
created+=("$cid")
docker start --attach "$cid" 2>&1 | tee "$results/build-driver.log"
test "$(docker inspect --format '{{.State.ExitCode}}' "$cid")" -eq 0
mkdir "$results/runtime-results"
cid=$(docker create --label codex.task=r3d-debian-gate --mount "type=bind,src=$results/debs,dst=/debs,readonly" --mount "type=bind,src=$results/tests,dst=/release-tests,readonly" --mount "type=bind,src=$results/manifests,dst=/manifests,readonly" --mount "type=bind,src=$results/build-evidence.json,dst=/build-evidence.json,readonly" --mount "type=bind,src=$results/source-context.json,dst=/source-context.json,readonly" --mount "type=bind,src=$repo/scripts/ci,dst=/release-tools,readonly" --mount "type=bind,src=$results/runtime-results,dst=/results" -e R3D_TEST_UID="$builder_uid" -e ROS_DOMAIN_ID=95 -e ROS_LOCALHOST_ONLY=1 -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp -e PYTHONNOUSERSITE=1 "$image" bash /release-tools/debian_inside.sh runtime)
created+=("$cid")
docker start --attach "$cid" 2>&1 | tee "$results/runtime-driver.log"
test "$(docker inspect --format '{{.State.ExitCode}}' "$cid")" -eq 0
echo DEBIAN_LOCAL_BUILD_TEST_INSTALL_RUNTIME_PASS
