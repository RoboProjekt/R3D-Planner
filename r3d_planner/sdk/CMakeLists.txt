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
project(r3d_go2w_gait_guard LANGUAGES CXX)
find_package(unitree_sdk2 REQUIRED)
add_executable(r3d_go2w_gait_guard go2w_gait_guard.cpp)
target_compile_features(r3d_go2w_gait_guard PRIVATE cxx_std_17)
target_compile_options(r3d_go2w_gait_guard PRIVATE -Wall -Wextra -Wpedantic)
target_link_libraries(r3d_go2w_gait_guard PRIVATE unitree_sdk2)
set_target_properties(r3d_go2w_gait_guard PROPERTIES
  INSTALL_RPATH "$<TARGET_FILE_DIR:ddsc>;$<TARGET_FILE_DIR:ddscxx>")
install(TARGETS r3d_go2w_gait_guard RUNTIME DESTINATION bin)

