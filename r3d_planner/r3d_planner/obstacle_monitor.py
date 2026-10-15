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

"""Validate obstacle measurements without coupling to a particular producer."""
import math

import numpy as np
from rclpy.time import Time

from .cloud import read_xyz
from .configuration import monitoring_settings, text
from .odometry import components


class ObstacleMonitor:
    """Keep only successful measurements; failed inputs revoke prior clearance."""

    def __init__(self, settings, base_frame, roi, lookup):
        self.settings = monitoring_settings(settings)
        text(base_frame, 'obstacle base_frame', frame=True)
        self.base_frame = base_frame
        self.timeout_ns = int(self.settings['timeout_sec'] * 1e9)
        self.roi = roi
        self.lookup = lookup
        self.state = 'WAITING_FOR_DATA' if self.settings['enabled'] else 'DISABLED'
        self.reason = self.state
        self.obstacle = False
        self.stamp_ns = self.receipt_ns = None
        self.last_ros_ns = self.last_steady_ns = None
        self.last_measurement_ns = None

    def invalidate(self, state, reason):
        """Require a new successful sample after any error or clock reset."""
        self.stamp_ns = self.receipt_ns = None
        self.state, self.reason = state, reason
        return False

    def clock_reset(self):
        """Invalidate values from a previous ROS time epoch."""
        self.last_ros_ns = self.last_steady_ns = None
        self.last_measurement_ns = None
        return self.invalidate('CLOCK_ERROR', 'ROS time basis changed or jumped backward')

    def observe_time(self, now_ns, steady_ns):
        """Detect discontinuities, with monotonic receipt time independent of ROS."""
        previous = (self.last_ros_ns, self.last_steady_ns)
        self.last_ros_ns, self.last_steady_ns = now_ns, steady_ns
        if now_ns <= 0 or steady_ns < 0:
            return self.invalidate('CLOCK_ERROR', 'clock is not initialized')
        if previous[0] is not None:
            ros_delta, steady_delta = now_ns - previous[0], steady_ns - previous[1]
            if ros_delta < 0 or steady_delta < 0 or ros_delta - steady_delta > self.timeout_ns:
                self.last_measurement_ns = None
                return self.invalidate('CLOCK_ERROR', 'clock discontinuity')
        return True

    def available(self, now_ns, steady_ns):
        """Permit movement only while both successful-input age limits hold."""
        if not self.settings['enabled']:
            return True
        if not self.observe_time(now_ns, steady_ns):
            return False
        if self.stamp_ns is None:
            return False
        age, silence = now_ns - self.stamp_ns, steady_ns - self.receipt_ns
        if age < 0 or silence < 0:
            return self.invalidate('CLOCK_ERROR', 'measurement belongs to another time epoch')
        if age > self.timeout_ns or silence > self.timeout_ns:
            return self.invalidate('STALE_DATA', 'measurement or successful input timed out')
        return self.state == 'ACTIVE'

    def points_in_base(self, cloud, points):
        """Use exact measurement time; foreign frames never get an identity fallback."""
        if cloud.header.frame_id == self.base_frame:
            return points
        if not self.settings['require_transform']:
            raise ValueError('foreign frame rejected with require_transform=false')
        transform = self.lookup(self.base_frame, cloud.header.frame_id,
                                Time.from_msg(cloud.header.stamp))
        if (transform.header.frame_id != self.base_frame or
                transform.child_frame_id != cloud.header.frame_id):
            raise ValueError('TF direction does not match source and target')
        stamp = transform.header.stamp.sec * 10**9 + transform.header.stamp.nanosec
        wanted = cloud.header.stamp.sec * 10**9 + cloud.header.stamp.nanosec
        if stamp not in (0, wanted):
            raise ValueError('TF is not valid at the measurement timestamp')
        q = transform.transform.rotation
        norm = sum(v*v for v in (q.x, q.y, q.z, q.w))
        if not math.isfinite(norm) or abs(norm - 1.0) > 1e-6:
            raise ValueError('TF rotation is not a normalized quaternion')
        x, y, z, w = components(q)
        rotation = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                             [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                             [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
        t = transform.transform.translation
        translation = np.array([t.x, t.y, t.z])
        if not np.isfinite(translation).all():
            raise ValueError('TF translation is not finite')
        points = points @ rotation.T + translation
        if not np.isfinite(points).all():
            raise ValueError('transformed geometry is not finite')
        return points

    def receive(self, cloud, now_ns, steady_ns):
        """Validate an entire input before storing its measurement and receipt time."""
        if not self.settings['enabled']:
            return True
        if not self.observe_time(now_ns, steady_ns):
            return False
        try:
            text(cloud.header.frame_id, 'obstacle frame_id', frame=True)
            sec, nano = cloud.header.stamp.sec, cloud.header.stamp.nanosec
            if sec < 0 or not 0 <= nano < 10**9 or sec * 10**9 + nano == 0:
                raise ValueError('uninitialized or invalid measurement timestamp')
            stamp = sec * 10**9 + nano
            age = now_ns - stamp
            if age < 0:
                return self.invalidate('FUTURE_DATA', 'measurement timestamp is in the future')
            if age > self.timeout_ns:
                return self.invalidate('STALE_DATA', 'measurement was already stale on receipt')
            if self.last_measurement_ns is not None and stamp <= self.last_measurement_ns:
                raise ValueError('measurement timestamp did not advance')
            points = read_xyz(cloud, strict=True)
        except (ValueError, AttributeError, TypeError) as exc:
            return self.invalidate('INVALID_DATA', str(exc))
        try:
            points = self.points_in_base(cloud, points)
        except Exception as exc:
            return self.invalidate('TF_UNAVAILABLE', str(exc))
        low, high, half_width = self.roi
        self.obstacle = bool(((points[:, 0] > low) & (points[:, 0] < high) &
                              (np.abs(points[:, 1]) < half_width)).any())
        self.stamp_ns, self.receipt_ns = stamp, steady_ns
        self.last_measurement_ns = stamp
        self.state = 'BLOCKED' if self.obstacle else 'ACTIVE'
        self.reason = 'obstacle in stop region' if self.obstacle else 'current valid input'
        return not self.obstacle
