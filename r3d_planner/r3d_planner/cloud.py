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

"""Decode ROS PointCloud2 geometry without assuming a packed byte layout."""
import numpy as np
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py.point_cloud2 import dtype_from_fields


def read_xyz(cloud):
    """
    Return finite XYZ rows, honoring offsets, endian order and row padding.

    Input storage is never mutated. The record view avoids copying extra sensor
    channels; only XYZ and the finite-row selection are materialized.
    """
    if not isinstance(cloud, PointCloud2):
        raise ValueError('expected PointCloud2')
    if cloud.width == 0 or cloud.height == 0:
        if len(cloud.data):
            raise ValueError('empty cloud has nonempty data')
        return np.empty((0, 3), dtype=np.float32)
    if cloud.point_step == 0 or cloud.row_step < cloud.width * cloud.point_step:
        raise ValueError('invalid point_step or row_step')
    if len(cloud.data) < cloud.height * cloud.row_step:
        raise ValueError('truncated PointCloud2 data')
    fields = {field.name: field for field in cloud.fields}
    if len([f.name for f in cloud.fields if f.name]) != len({
            f.name for f in cloud.fields if f.name}):
        raise ValueError('duplicate PointField names')
    for name in ('x', 'y', 'z'):
        if name not in fields or fields[name].count != 1:
            raise ValueError('XYZ fields must be present scalar values')
    try:
        dtype = dtype_from_fields(cloud.fields, point_step=cloud.point_step)
    except (AssertionError, KeyError, ValueError, TypeError) as exc:
        raise ValueError(f'invalid PointFields: {exc}') from exc
    for field in cloud.fields:
        if dtype_from_fields([field]).itemsize > cloud.point_step:
            raise ValueError('PointField exceeds point_step')
    dtype = dtype.newbyteorder('>' if cloud.is_bigendian else '<')
    records = np.ndarray((cloud.height, cloud.width), dtype=dtype,
                         buffer=cloud.data, strides=(cloud.row_step, cloud.point_step))
    xyz_dtype = np.result_type(*(dtype.fields[name][0] for name in ('x', 'y', 'z')),
                               np.float32)
    points = np.empty((cloud.height, cloud.width, 3), dtype=xyz_dtype)
    for axis, name in enumerate(('x', 'y', 'z')):
        points[:, :, axis] = records[name]
    points = points.reshape((-1, 3))
    finite = np.isfinite(points).all(axis=1)
    return points if finite.all() else points[finite]


def create_cloud_xyz32(header, points):
    """Serialize finite XYZ output with complete metadata, including empty clouds."""
    points = np.asarray(points, dtype='<f4').reshape((-1, 3))
    fields = [PointField(name=name, offset=offset, datatype=PointField.FLOAT32, count=1)
              for name, offset in [('x', 0), ('y', 4), ('z', 8)]]
    return PointCloud2(header=header, height=1, width=len(points),
                       is_dense=bool(np.isfinite(points).all()),
                       is_bigendian=False, fields=fields, point_step=12,
                       row_step=12 * len(points), data=points.tobytes())
