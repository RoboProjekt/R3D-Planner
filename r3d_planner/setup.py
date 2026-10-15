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
# =============================================================================
# R3D-Planner
#
# Author:        Bastian Aumer
# Last modified: 2026-09-16
# Repository:    https://github.com/RoboProjekt/R3D-Planner
#
# Copyright (c) Bastian Aumer
# SPDX-FileCopyrightText: 2026 Bastian Aumer
# SPDX-License-Identifier: Apache-2.0
# =============================================================================

from setuptools import setup
import os
from glob import glob

package_name = 'r3d_planner'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'LICENSE', 'CHANGELOG.rst']),
        # Hier installieren wir die Config Datei, damit launch files sie finden
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'config', 'robots'), glob('config/robots/*.yaml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bauya',
    maintainer_email='baau1001@stud.hs-kl.de',
    description=(
        'Graph-based A* path planning on classified PCD traversability data '
        'with a ComputePathToPose action, RViz integration, local obstacle '
        'filtering and path following.'
    ),
    author='Bastian Aumer',
    url='https://github.com/RoboProjekt/R3D-Planner',
    project_urls={
        'Bug Tracker': 'https://github.com/RoboProjekt/R3D-Planner/issues',
    },
    license='Apache-2.0',
    license_files=['LICENSE'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Das registriert die Executables für 'ros2 run'
            'local_filter = r3d_planner.r3d_local_filter:main',
            'path_follower = r3d_planner.r3d_path_follower:main',
            'rviz_interface = r3d_planner.r3d_rviz_interface:main',
            'pcd_path_planner = r3d_planner.r3d_pcd_path:main',
            'path_test = r3d_planner.r3d_path_test:main'
        ],
    },
)
