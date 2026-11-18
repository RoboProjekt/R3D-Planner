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

"""Coordinate path-confirmed stairs and stopped, acknowledged gait transitions."""
from collections import deque
import math
import os
import signal
import subprocess
import tempfile


class StairRoute:
    """Measure distance along the geometric path, including its height changes."""

    def __init__(self, positions, stairs):
        self.positions = [tuple(p) for p in positions]
        self.stairs = list(stairs)
        if not self.positions or len(self.positions) != len(self.stairs):
            raise ValueError('a nonempty path needs one stair flag per pose')
        if not all(math.isfinite(v) for point in self.positions for v in point):
            raise ValueError('nonfinite route position')
        self.distance = [0.0]
        for before, after in zip(self.positions, self.positions[1:]):
            self.distance.append(self.distance[-1] + math.dist(before, after))

    def project(self, position, xy_only=False):
        """Return route distance, nearest point and tracking error."""
        dimensions = 2 if xy_only else 3
        closest = (math.inf, 0.0, self.positions[0])
        for index in range(max(1, len(self.positions) - 1)):
            start = self.positions[index]
            end = self.positions[min(index + 1, len(self.positions) - 1)]
            vector = tuple(b - a for a, b in zip(start, end))
            length_sq = sum(v * v for v in vector[:dimensions])
            fraction = 0.0
            if length_sq:
                fraction = sum((position[d] - start[d]) * vector[d]
                               for d in range(dimensions)) / length_sq
                fraction = min(1.0, max(0.0, fraction))
            point = tuple(a + fraction * v for a, v in zip(start, vector))
            error = math.dist(position[:dimensions], point[:dimensions])
            along = self.distance[index] + fraction * math.dist(start, end)
            if error < closest[0]:
                closest = (error, along, point)
        error, along, point = closest
        return along, point, error

    def next_flight(self, progress, landing_distance):
        """Keep stair mode across landings shorter than the configured exit distance."""
        indices = [i for i, flag in enumerate(self.stairs) if flag]
        groups = []
        for index in indices:
            if groups and self.distance[index] - self.distance[groups[-1][-1]] < landing_distance:
                groups[-1].append(index)
            else:
                groups.append([index])
        for group in groups:
            if self.distance[group[-1]] >= progress - 1e-6:
                return group[0], group[-1]
        return None

    def flat_after(self, end, progress):
        """Check the post-stair path through the robot and a short forward horizon."""
        horizon = min(self.distance[-1], progress + 0.5)
        points = [p for i, p in enumerate(self.positions) if end < self.distance[i] <= horizon]
        flags = [flag for i, flag in enumerate(self.stairs) if end < self.distance[i] <= horizon]
        if not points or any(flags):
            return False
        return max(p[2] for p in points) - min(p[2] for p in points) <= 0.05


class StairCoordinator:
    """Keep movement stopped until the SDK has confirmed each requested mode."""

    def __init__(self, approach_distance, exit_distance):
        for value in (approach_distance, exit_distance):
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError('stair distances must be finite and positive')
        self.approach_distance = approach_distance
        self.exit_distance = exit_distance
        self.phase = 'initial'
        self.state = 'WAIT_PATH'
        self.detail = 'Waiting for a valid path and fresh map pose'
        self.motion_allowed = False
        self.stair_mode_active = False
        self.clear_detection = False
        self.switching = False
        self.height_offset = None
        self.active_end = None
        self.entry_point = None
        self.still_since = None
        self.heights = deque()

    def hold(self, detail):
        """Withdraw the permit without forgetting a confirmed active stair mode."""
        self.motion_allowed = False
        if self.state == 'ERROR':
            return
        self.state = 'WAIT_DATA'
        self.detail = detail
        self.still_since = None
        self.heights.clear()

    def fail(self, detail):
        """Latch SDK failures for explicit retry while keeping zero velocity."""
        self.motion_allowed = False
        self.state = 'ERROR'
        self.detail = detail
        self.switching = False

    def retry(self):
        """Retry the interrupted transition after its stationary checks."""
        if self.state != 'ERROR':
            return False
        self.state = 'WAIT_DATA'
        self.still_since = None
        return True

    def confirmed(self, success, detail=''):
        """Consume the SDK process result; exit code zero confirms the target gait."""
        self.switching = False
        if not success:
            self.fail(detail)
            return
        self.still_since = None
        if self.phase == 'enter':
            self.stair_mode_active = True
            self.phase = 'stairs'
        else:
            self.clear_detection = self.phase == 'exit'
            self.stair_mode_active = False
            self.phase = 'normal'
            self.active_end = self.entry_point = None

    def stopped_switch(self, stationary, now, mode):
        """Require half a second of measured standstill before invoking the tool."""
        self.state = 'STOPPING_' + mode.upper()
        if not stationary:
            self.still_since = None
        elif self.still_since is None:
            self.still_since = now
        elif now - self.still_since >= 0.5:
            self.switching = True
            self.state = 'SWITCHING_' + mode.upper()
            return mode
        return None

    def step(self, route, robot, stationary, detection, now, level=True):
        """Return an optional SDK mode request and update the current movement permit."""
        self.motion_allowed = False
        if self.state == 'ERROR' or self.switching:
            return None
        if self.height_offset is None:
            _, ground, _ = route.project(robot, xy_only=True)
            self.height_offset = robot[2] - ground[2]
        tracking = (robot[0], robot[1], robot[2] - self.height_offset)
        progress, ground, error = route.project(tracking)
        if error > 0.5 or abs(tracking[2] - ground[2]) > 0.1:
            self.hold('Robot pose does not match the planned path/level')
            return None
        self.heights.append((now, robot[2]))
        while self.heights and self.heights[0][0] < now - 0.6:
            self.heights.popleft()
        self.detail = ''
        if self.phase == 'initial':
            flight = route.next_flight(progress, self.exit_distance)
            if flight is not None and route.distance[flight[0]] <= progress + 0.1:
                self.hold('Initialize on a flat approach before the first stair waypoint')
                return None
            return self.stopped_switch(stationary, now, 'normal')
        if self.phase == 'normal':
            flight = route.next_flight(progress, self.exit_distance)
            if flight is None or route.distance[flight[0]] - progress > self.approach_distance:
                self.state, self.motion_allowed = 'NORMAL', True
                return None
            self.entry_point = route.positions[flight[0]]
            self.active_end = route.positions[flight[1]]
            self.phase = 'enter'
            self.still_since = None
        if self.phase in ('enter', 'stairs', 'exit'):
            end, _, end_error = route.project(self.active_end)
            if end_error > 0.15:
                self.hold('Replanned route omits the active staircase. '
                          'Retain its exit until confirmed')
                return None
            # A changed classification cannot clear a flight already being traversed.
            matching = [i for i, (point, flag) in enumerate(zip(route.positions, route.stairs))
                        if flag and math.dist(point, self.active_end) <= 0.15]
            if not matching:
                self.hold('Active staircase is missing from the new terrain metadata')
                return None
            last = max(matching, key=lambda index: route.distance[index])
            self.active_end, end = route.positions[last], route.distance[last]
            if self.phase == 'stairs':
                following = route.next_flight(end + 1e-5, self.exit_distance)
                if (following is not None and route.distance[following[0]] - progress <=
                        max(self.approach_distance, 0.5)):
                    # Keep the confirmed gait if the next flight is already in approach range.
                    self.active_end = route.positions[following[1]]
                    end = route.distance[following[1]]
        if self.phase == 'enter':
            # Confirm that the live observation belongs to the planned staircase.
            if detection is None or math.dist(detection, self.entry_point) > 0.75:
                self.state = 'WAIT_DETECTION'
                self.detail = ('Stopped before the planned stairs. '
                               'Waiting for matching live detection')
                self.still_since = None
                return None
            return self.stopped_switch(stationary, now, 'stairs')
        if self.phase in ('stairs', 'exit'):
            flat_robot = (len(self.heights) >= 2 and
                          self.heights[-1][0] - self.heights[0][0] >= 0.4 and
                          max(z for _, z in self.heights) -
                          min(z for _, z in self.heights) <= 0.03)
            if (progress - end >= self.exit_distance - 1e-6 and flat_robot and level and
                    route.flat_after(end, progress)):
                if self.phase != 'exit':
                    self.phase = 'exit'
                    self.still_since = None
            else:
                if self.phase == 'exit':
                    self.hold('Exit conditions changed before normal-mode confirmation')
                    return None
                self.state, self.motion_allowed = 'STAIRS', True
                return None
        return self.stopped_switch(stationary, now, 'normal')


class SdkSwitch:
    """Run the documented executable asynchronously with bounded process lifetime."""

    def __init__(self, executable, interface, timeout):
        if not os.path.isabs(executable) or not interface or any(c.isspace() for c in interface):
            raise ValueError('SDK executable must be absolute and interface must be one name')
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('SDK timeout must be finite and positive')
        self.executable, self.interface, self.timeout = executable, interface, timeout
        self.process = self.output = None
        self.started = None

    def start(self, mode, now):
        """Pass literal arguments, without a shell or unbounded output pipe."""
        if mode not in ('stairs', 'normal') or self.process is not None:
            raise ValueError('invalid or concurrent SDK switch')
        self.output = tempfile.TemporaryFile()
        try:
            self.process = subprocess.Popen(
                [self.executable, self.interface, mode], stdin=subprocess.DEVNULL,
                stdout=self.output, stderr=subprocess.STDOUT, start_new_session=True)
        except Exception:
            self.output.close()
            self.output = None
            raise
        self.started = now

    def poll(self, now):
        """Return a confirmed result, a failure, or None while the tool is running."""
        if self.process is None:
            return None
        code = self.process.poll()
        timed_out = code is None and now - self.started >= self.timeout
        if code is None and not timed_out:
            return None
        if timed_out:
            self.stop_process()
        self.output.seek(0, os.SEEK_END)
        size = self.output.tell()
        self.output.seek(max(0, size - 4096))
        detail = self.output.read().decode('utf-8', errors='replace').strip()
        self.output.close()
        self.output = self.process = None
        return code == 0 and not timed_out, ('SDK timeout' if timed_out else
                                             f'SDK exit {code}: {detail}')

    def stop_process(self):
        """Reap the process group on timeout or shutdown."""
        if self.process is not None and self.process.poll() is None:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.process.wait()

    def close(self):
        """Release process and temporary log resources."""
        self.stop_process()
        if self.output is not None:
            self.output.close()
        self.output = self.process = None
