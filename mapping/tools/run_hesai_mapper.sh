#!/usr/bin/env bash
set -e
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ -z ${ROS_DISTRO:-} && -r /opt/ros/humble/setup.bash ]]; then
    source /opt/ros/humble/setup.bash
fi
mapper_python="${HESAI_PYTHON:-$script_dir/../.runtime/hesai_mapping/bin/python}"
if [[ ! -x "$mapper_python" ]]; then
    mapper_python=python3
fi
export OPENBLAS_NUM_THREADS=1
exec "$mapper_python" "$script_dir/map_hesai.py" "$@"
