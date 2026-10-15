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

"""Exercise deterministic monitoring boundaries, frame contracts and configuration."""
import math
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Header

from r3d_planner.cloud import create_cloud_xyz32, read_xyz
from r3d_planner.configuration import ConfigurationError, load_configuration, monitoring_settings
from r3d_planner.obstacle_monitor import ObstacleMonitor


NS = 10**9


def cloud(points=(), stamp=10*NS, frame='base_link'):
    message = create_cloud_xyz32(Header(frame_id=frame), points)
    message.header.stamp.sec, message.header.stamp.nanosec = divmod(stamp, NS)
    return message


def monitor(**kwargs):
    settings = monitoring_settings()
    settings.update(enabled=True, **kwargs)
    return ObstacleMonitor(settings, 'base_link', (0.1, 0.6, 0.3), Mock())


@pytest.mark.parametrize('value', [0, -1, math.nan, math.inf, -math.inf,
                                   None, '1', True, [], {}, 1e-10, 1e20])
def test_invalid_timeout(value):
    settings = monitoring_settings()
    settings['timeout_sec'] = value
    with pytest.raises(ConfigurationError):
        monitoring_settings(settings)


@pytest.mark.parametrize('key', ['enabled', 'require_transform'])
@pytest.mark.parametrize('value', [1, 'true', None])
def test_strict_boolean(key, value):
    settings = monitoring_settings()
    settings[key] = value
    with pytest.raises(ConfigurationError):
        monitoring_settings(settings)


@pytest.mark.parametrize('value', [None, [], {}, {'enabled': True},
                                   {**monitoring_settings(), 'unknown': 1},
                                   {**monitoring_settings(), 'topic': '/bad topic'}])
def test_invalid_monitor_group(value):
    with pytest.raises(ConfigurationError):
        monitoring_settings(value)


def test_default_and_optional_topic():
    settings = monitoring_settings()
    assert settings == {'enabled': False, 'timeout_sec': 1.0,
                        'require_transform': True, 'topic': '/local/filtered_obstacles'}
    del settings['topic']
    assert monitoring_settings(settings)['topic'] == '/local/filtered_obstacles'
    disabled = ObstacleMonitor(monitoring_settings(), 'base_link', (0.1, 0.6, 0.3), Mock())
    assert disabled.state == 'DISABLED' and disabled.available(0, 0)


@pytest.mark.parametrize('delta,expected', [(NS-1, True), (NS, True), (NS+1, False)])
def test_measurement_and_receipt_timeout_boundaries(delta, expected):
    item = monitor()
    assert item.receive(cloud(), 10*NS, 100*NS)
    assert item.available(10*NS+delta, 100*NS+delta) is expected
    if not expected:
        assert item.state == 'STALE_DATA'


def test_paused_ros_time_still_expires_and_replay_cannot_refresh():
    item = monitor()
    assert item.receive(cloud(), 10*NS, 100*NS)
    assert not item.available(10*NS, 102*NS)
    assert item.state == 'STALE_DATA'
    assert not item.receive(cloud(), 10*NS, 102*NS)
    assert item.state == 'INVALID_DATA'
    assert item.receive(cloud(stamp=10*NS+1), 10*NS+1, 102*NS+1)


@pytest.mark.parametrize('now,stamp,state', [
    (10*NS, 8*NS, 'STALE_DATA'), (10*NS, 10*NS+1, 'FUTURE_DATA'),
    (10*NS, 0, 'INVALID_DATA'), (0, 1, 'CLOCK_ERROR')])
def test_invalid_time_on_arrival(now, stamp, state):
    item = monitor()
    assert not item.receive(cloud(stamp=stamp), now, 100*NS)
    assert item.state == state and item.stamp_ns is None


@pytest.mark.parametrize('ros_delta,steady_delta', [(-1, 1), (2*NS, 1), (1, -1)])
def test_clock_discontinuities_revoke_cache(ros_delta, steady_delta):
    item = monitor()
    assert item.receive(cloud(), 10*NS, 100*NS)
    assert not item.available(10*NS+ros_delta, 100*NS+steady_delta)
    assert item.state == 'CLOCK_ERROR' and item.stamp_ns is None
    item.clock_reset()
    assert not item.available(10*NS, 100*NS)
    assert item.receive(cloud(stamp=9*NS), 9*NS, 101*NS) is False
    assert item.receive(cloud(stamp=9*NS+1), 9*NS+1, 101*NS+1)


@pytest.mark.parametrize('fault', ['fields', 'stride', 'truncated', 'frame', 'bad_stamp',
                                   'nan', 'inf', 'mixed_nonfinite', 'empty_fields',
                                   'empty_stride', 'invalid_empty_shape'])
def test_invalid_geometry_revokes_clearance_and_preserves_bytes(fault):
    item = monitor()
    assert item.receive(cloud(), 10*NS, 100*NS)
    message = cloud([[2, 0, 0]], stamp=10*NS+1)
    if fault in ('fields', 'empty_fields'):
        if fault == 'empty_fields':
            message = cloud(stamp=10*NS+1)
        message.fields = []
    elif fault == 'stride':
        message.row_step = 1
    elif fault == 'truncated':
        message.data = message.data[:-1]
    elif fault == 'frame':
        message.header.frame_id = ''
    elif fault == 'bad_stamp':
        message.header.stamp.nanosec = NS
    elif fault == 'empty_stride':
        message = cloud(stamp=10*NS+1)
        message.point_step = 0
    elif fault == 'invalid_empty_shape':
        message.height = 0
        message.data = b''
    else:
        bad = math.nan if fault != 'inf' else math.inf
        points = [[bad, 0, 0]]
        if fault == 'mixed_nonfinite':
            points.append([2, 0, 0])
        message = cloud(points, stamp=10*NS+1)
    original = bytes(message.data)
    assert not item.receive(message, 10*NS+1, 100*NS+1)
    assert item.state == 'INVALID_DATA' and item.stamp_ns is None
    assert bytes(message.data) == original


def test_empty_clear_blocked_recovery_and_no_relevant_obstacles():
    item = monitor()
    assert item.state == 'WAITING_FOR_DATA'
    assert not item.available(10*NS, 100*NS)
    assert item.receive(cloud(), 10*NS, 100*NS)
    assert not item.receive(cloud([[0.3, 0, 0]], stamp=10*NS+1), 10*NS+1, 100*NS+1)
    assert item.state == 'BLOCKED' and not item.available(10*NS+1, 100*NS+1)
    assert item.receive(cloud([[2, 0, 0], [0.3, 1, 0]], stamp=10*NS+2),
                        10*NS+2, 100*NS+2)
    assert item.state == 'ACTIVE'
    assert not item.receive(cloud(stamp=10*NS+1), 10*NS+3, 100*NS+3)
    assert not item.available(10*NS+3, 100*NS+3)
    assert item.receive(cloud(stamp=10*NS+4), 10*NS+4, 100*NS+4)


def transform(stamp=0):
    value = TransformStamped()
    value.header.frame_id = 'base_link'
    value.child_frame_id = 'sensor'
    value.header.stamp.sec, value.header.stamp.nanosec = divmod(stamp, NS)
    value.transform.rotation.z = math.sqrt(0.5)
    value.transform.rotation.w = math.sqrt(0.5)
    value.transform.translation.x = 0.3
    return value


def test_tf_rotation_translation_direction_and_measurement_time():
    item = monitor()
    item.lookup.return_value = transform(10*NS)
    message = cloud([[0, 0, 0], [0, 2, 0]], frame='sensor')
    original = bytes(message.data)
    assert not item.receive(message, 10*NS, 100*NS)
    assert item.state == 'BLOCKED'
    args = item.lookup.call_args.args
    assert args[:2] == ('base_link', 'sensor') and args[2].nanoseconds == 10*NS
    assert bytes(message.data) == original
    np.testing.assert_allclose(item.points_in_base(message, read_xyz(message)),
                               [[0.3, 0, 0], [-1.7, 0, 0]], atol=1e-12)


@pytest.mark.parametrize('fault', ['missing', 'wrong_time', 'direction', 'translation',
                                   'rotation', 'nonnormalized'])
def test_tf_failures_even_for_empty_cloud(fault):
    item = monitor()
    value = transform()
    if fault == 'missing':
        item.lookup.side_effect = RuntimeError('missing transform')
    elif fault == 'wrong_time':
        value.header.stamp.sec = 8
    elif fault == 'direction':
        value.header.frame_id, value.child_frame_id = 'sensor', 'base_link'
    elif fault == 'translation':
        value.transform.translation.x = math.nan
    elif fault == 'rotation':
        value.transform.rotation.w = math.inf
    else:
        value.transform.rotation.w = 2.0
    item.lookup.return_value = value
    assert not item.receive(cloud(frame='sensor'), 10*NS, 100*NS)
    assert item.state == 'TF_UNAVAILABLE'


@pytest.mark.parametrize('require', [False, True])
def test_base_frame_never_queries_tf_and_false_rejects_foreign(require):
    item = monitor(require_transform=require)
    assert item.receive(cloud(), 10*NS, 100*NS)
    item.lookup.assert_not_called()
    if not require:
        assert not item.receive(cloud(stamp=10*NS+1, frame='sensor'), 10*NS+1, 100*NS+1)
        assert item.state == 'TF_UNAVAILABLE'
        item.lookup.assert_not_called()


def test_static_tf_stamp_zero_is_valid():
    item = monitor()
    item.lookup.return_value = transform()
    assert item.receive(cloud(frame='sensor'), 10*NS, 100*NS)


@pytest.fixture
def config(tmp_path):
    share = Path(get_package_share_directory('r3d_planner'))/'config'
    cfg = yaml.safe_load((share/'planner_config.yaml').read_text())
    (tmp_path/'robots').mkdir()
    (tmp_path/'robots/Go2W.yaml').write_bytes((share/'robots/Go2W.yaml').read_bytes())
    (tmp_path/'map.pcd').write_text('synthetic configuration path only')
    cfg['maps'] = {'map_name': 'map.pcd', 'pcd_path': 'map.pcd'}
    return tmp_path, cfg


@pytest.mark.parametrize('mode', ['planner', 'map', 'preprocessor', 'follower'])
def test_config_override_and_legacy_group(config, monkeypatch, mode):
    directory, cfg = config
    monkeypatch.setenv('R3D_CONFIG_DIR', str(directory))
    cfg['path_follower']['obstacle_monitoring'].update(
        enabled=True, timeout_sec=2, require_transform=False, topic='external')
    path = directory/'planner_config.yaml'
    path.write_text(yaml.safe_dump(cfg))
    values = load_configuration(mode=mode)['path_follower']
    assert values['obstacle_monitoring.enabled'] is True
    assert values['obstacle_monitoring.timeout_sec'] == 2.0
    assert values['obstacle_monitoring.require_transform'] is False
    assert values['obstacle_monitoring.topic'] == 'external'
    del cfg['path_follower']['obstacle_monitoring']
    path.write_text(yaml.safe_dump(cfg))
    assert load_configuration(mode=mode)['path_follower']['obstacle_monitoring.enabled'] is False
    cfg['path_follower']['obstacle_monitoring'] = None
    path.write_text(yaml.safe_dump(cfg))
    with pytest.raises(ConfigurationError):
        load_configuration(mode=mode)
