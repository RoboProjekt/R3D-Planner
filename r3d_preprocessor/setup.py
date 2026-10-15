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
# Last modified: 2026-09-14
# Repository:    https://github.com/RoboProjekt/R3D-Planner
#
# Copyright (c) Bastian Aumer
# SPDX-FileCopyrightText: 2026 Bastian Aumer
# SPDX-License-Identifier: Apache-2.0
# =============================================================================

from setuptools import setup
# Den glob-Import brauchen wir jetzt nicht mehr
# from glob import glob

package_name = 'r3d_preprocessor'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'LICENSE', 'CHANGELOG.rst']),
        # Die Zeilen für den maps-Ordner wurden hier entfernt!
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bauya',
    maintainer_email='baau1001@stud.hs-kl.de',
    description=(
        'Offline voxel-based analysis and classification of PCD point '
        'clouds for robot-specific clearance and traversability assessment, '
        'with classified point-cloud output.'
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
            # Name des Befehls = package.file:main_funktion
            'pcd_analyser = r3d_preprocessor.r3d_pcd_analyser:main',
            'pcd_server = r3d_preprocessor.r3d_pcd_publisher:main',
        ],
    },
)
