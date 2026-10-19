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
cmake_minimum_required(VERSION 3.8)
project(r3d_interfaces)
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(nav_msgs REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/PathWithMetadata.msg"
  DEPENDENCIES nav_msgs
)
ament_export_dependencies(rosidl_default_runtime)
install(FILES LICENSE README.md CHANGELOG.rst DESTINATION share/${PROJECT_NAME})
if(BUILD_TESTING)
  find_package(ament_cmake_copyright REQUIRED)
  find_package(ament_cmake_lint_cmake REQUIRED)
  find_package(ament_cmake_xmllint REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)
  # Check only project sources, independent of generated in-source Debian files.
  ament_copyright(test)
  ament_lint_cmake(CMakeLists.txt)
  ament_xmllint(package.xml)
  ament_add_pytest_test(source_headers test/test_source_headers.py)
endif()
ament_package()
