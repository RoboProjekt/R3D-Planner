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

"""Assertions shared by copied and Debian-installed ROS test contexts."""
from pathlib import Path

from ament_index_python.packages import get_package_prefix


def assert_installed_module(package, filename):
    """Require imports to belong to the package's registered installation prefix."""
    prefix = Path(get_package_prefix(package)).resolve()
    location = Path(filename).resolve()
    assert location.is_relative_to(prefix), (package, str(location), str(prefix))
    return location
