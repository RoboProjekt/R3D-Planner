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

"""Exercise field-based cloud decoding with real ROS message storage."""
import copy
import itertools
import struct
from unittest.mock import Mock

import numpy as np
import pytest
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header

from r3d_planner.cloud import create_cloud_xyz32, read_xyz


def make_cloud(layout='packed', big=False, organized=False, padding=False, dense=False):
    offsets, point_step = {
        'packed': ([0, 4, 8], 12), 'reordered': ([8, 0, 4], 12),
        'xyz_rgb_padding': ([4, 12, 20], 32), 'float64': ([0, 8, 16], 24),
    }[layout]
    fmt = 'd' if layout == 'float64' else 'f'
    datatype = PointField.FLOAT64 if fmt == 'd' else PointField.FLOAT32
    fields = [PointField(name=name, offset=off, datatype=datatype, count=1)
              for name, off in zip(('x', 'y', 'z'), offsets)]
    if layout == 'xyz_rgb_padding':
        fields.append(PointField(name='rgb', offset=24, datatype=PointField.UINT32, count=1))
    width, height = (2, 2) if organized else (4, 1)
    row_step = width * point_step + (9 if padding else 0)
    data = bytearray([0x7e] * (row_step * height))
    points = [(1.0, 2.0, 3.0), (2.0, -3.0, 4.0), (float('nan'), 1.0, 0.0),
              (0.75, -0.1, 0.15)]
    for index, point in enumerate(points):
        row, col = divmod(index, width)
        for value, off in zip(point, offsets):
            struct.pack_into(('>' if big else '<') + fmt, data,
                             row * row_step + col * point_step + off, value)
    return PointCloud2(header=Header(frame_id='sensor'), width=width, height=height,
                       point_step=point_step, row_step=row_step, fields=fields,
                       is_bigendian=big, is_dense=dense, data=bytes(data))


@pytest.mark.parametrize('layout,big,organized,padding,dense', list(itertools.product(
    ['packed', 'reordered', 'xyz_rgb_padding', 'float64'], [False, True],
    [False, True], [False, True], [False, True])))
def test_xyz_layouts_and_input_immutability(layout, big, organized, padding, dense):
    msg = make_cloud(layout, big, organized, padding, dense)
    before = bytes(msg.data)
    points = read_xyz(msg)
    np.testing.assert_allclose(points, [[1, 2, 3], [2, -3, 4], [0.75, -0.1, 0.15]])
    assert bytes(msg.data) == before
    assert points.shape == (3, 3)


@pytest.mark.parametrize('bad', ['missing', 'duplicate', 'array_xyz', 'datatype',
                                 'field_overrun', 'row_step', 'truncated', 'step_zero'])
def test_invalid_cloud_rejected(bad):
    msg = make_cloud()
    if bad == 'missing':
        msg.fields = msg.fields[:-1]
    elif bad == 'duplicate':
        msg.fields.append(copy.deepcopy(msg.fields[0]))
    elif bad == 'array_xyz':
        msg.fields[0].count = 2
    elif bad == 'datatype':
        msg.fields[0].datatype = 99
    elif bad == 'field_overrun':
        msg.fields[0].offset = msg.point_step
    elif bad == 'row_step':
        msg.row_step -= 1
    elif bad == 'truncated':
        msg.data = bytes(msg.data[:-1])
    elif bad == 'step_zero':
        msg.point_step = 0
    with pytest.raises(ValueError):
        read_xyz(msg)


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf')])
@pytest.mark.parametrize('dense', [False, True])
def test_nonfinite_rejected_even_if_dense(value, dense):
    msg = create_cloud_xyz32(Header(), [[1, 2, value], [4, 5, 6]])
    msg.is_dense = dense
    np.testing.assert_array_equal(read_xyz(msg), [[4, 5, 6]])


def test_integer_and_mixed_xyz_fields():
    fields = [PointField(name='x', offset=0, datatype=PointField.INT16, count=1),
              PointField(name='y', offset=2, datatype=PointField.FLOAT32, count=1),
              PointField(name='z', offset=6, datatype=PointField.FLOAT64, count=1)]
    msg = PointCloud2(width=1, height=1, point_step=14, row_step=14, fields=fields,
                      data=struct.pack('<hfd', 2000, 2.5, 3.25))
    np.testing.assert_array_equal(read_xyz(msg), [[2000, 2.5, 3.25]])


@pytest.mark.parametrize('points', [[], [[1, 2, 3]]])
def test_serialized_output_and_empty_metadata(points):
    msg = create_cloud_xyz32(Header(frame_id='sensor'), points)
    assert msg.header.frame_id == 'sensor'
    assert [field.name for field in msg.fields] == ['x', 'y', 'z']
    assert msg.point_step == 12 and msg.row_step == 12 * len(points)
    np.testing.assert_array_equal(read_xyz(msg), np.asarray(points).reshape((-1, 3)))


def test_local_filter_preserves_geometry_for_equivalent_layouts():
    import rclpy
    from r3d_planner.r3d_local_filter import ObstacleCliffFilter
    rclpy.init()
    node = ObstacleCliffFilter()
    try:
        node.pub_obstacles = Mock()
        node.pub_cliff = Mock()
        node.pub_stair_detect = Mock()
        expected = None
        for layout in ['packed', 'reordered', 'xyz_rgb_padding', 'float64']:
            node.pc_callback(make_cloud(layout, big=True, organized=True, padding=True))
            obstacles = node.pub_obstacles.publish.call_args.args[0]
            points = read_xyz(obstacles)
            if expected is None:
                expected = points
            else:
                np.testing.assert_allclose(points, expected)
            assert obstacles.header.frame_id == 'sensor'
        count = node.pub_obstacles.publish.call_count
        invalid = make_cloud()
        invalid.fields = []
        node.pc_callback(invalid)
        assert node.pub_obstacles.publish.call_count == count
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_extra_array_and_unnamed_fields():
    msg = make_cloud('xyz_rgb_padding')
    msg.fields += [PointField(name='', offset=0, datatype=PointField.UINT8, count=1),
                   PointField(name='', offset=1, datatype=PointField.UINT8, count=1),
                   PointField(name='intensity', offset=28, datatype=PointField.UINT8, count=4)]
    points = read_xyz(msg)
    np.testing.assert_allclose(points, [[1, 2, 3], [2, -3, 4], [0.75, -0.1, 0.15]])
