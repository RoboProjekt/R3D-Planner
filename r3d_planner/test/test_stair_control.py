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

"""Exercise stair sequencing with synthetic geometry and fake SDK executables."""
import math
import time

import pytest

from r3d_planner.stair_control import SdkSwitch, StairCoordinator, StairRoute


def route():
    """Provide a staircase followed by a sufficiently long upper landing."""
    return StairRoute([(0., 0., 0.), (1., 0., 0.), (2., 0., 0.),
                       (2.1, 0., 0.2), (2.2, 0., 0.4), (2.5, 0., 0.4),
                       (3.2, 0., 0.4), (4.2, 0., 0.4)],
                      [False, False, True, True, True, False, False, False])


def initialized():
    """Confirm normal mode before any initial forward movement."""
    control = StairCoordinator(1.0, 1.0)
    assert control.step(route(), (0., 0., 0.5), True, None, 0.) is None
    assert not control.motion_allowed
    assert control.step(route(), (0., 0., 0.5), True, None, 0.51) == 'normal'
    control.confirmed(True)
    control.step(route(), (0., 0., 0.5), True, None, 0.6)
    assert control.motion_allowed and control.state == 'NORMAL'
    return control


def climbing():
    """Enter stair mode after live confirmation and measured standstill."""
    control = initialized()
    control.step(route(), (1., 0., 0.5), False, None, 1.)
    assert control.state == 'WAIT_DETECTION' and not control.motion_allowed
    control.step(route(), (1., 0., 0.5), True, (2., 0., 0.1), 1.1)
    assert control.step(route(), (1., 0., 0.5), True, (2., 0., 0.1), 1.61) == 'stairs'
    assert not control.motion_allowed
    control.confirmed(True)
    control.step(route(), (2.1, 0., 0.7), False, None, 2.)
    assert control.motion_allowed and control.stair_mode_active
    return control


@pytest.mark.parametrize('value', [0, -1, True, '1', math.nan, math.inf])
@pytest.mark.parametrize('field', ['approach', 'exit'])
def test_invalid_distances(value, field):
    """Reject ambiguous types, nonfinite numbers and nonpositive margins."""
    with pytest.raises(ValueError):
        StairCoordinator(value if field == 'approach' else 1.,
                         value if field == 'exit' else 1.)


def test_full_stop_switch_climb_flat_exit_clear_sequence():
    """Release motion only after confirmation and clear detection after confirmed exit."""
    control = climbing()
    control.step(route(), (2.9, 0., 0.9), False, None, 3.)
    assert control.state == 'STAIRS'
    control.step(route(), (3.2, 0., 0.9), False, None, 3.5)
    assert not control.motion_allowed and control.phase == 'exit'
    assert not control.clear_detection
    control.step(route(), (3.2, 0., 0.9), True, None, 3.6)
    assert control.step(route(), (3.2, 0., 0.9), True, None, 4.11) == 'normal'
    assert not control.motion_allowed and control.stair_mode_active
    control.confirmed(True)
    assert control.clear_detection and not control.stair_mode_active
    control.step(route(), (3.2, 0., 0.9), True, (2., 0., 0.1), 4.2)
    assert control.motion_allowed and control.state == 'NORMAL'


def test_repeated_live_messages_and_unrelated_stairs():
    """Ignore off-route stair observations and require the configured approach distance."""
    control = initialized()
    control.step(route(), (0.5, 0., 0.5), False, (2., 0., 0.1), 1.)
    assert control.motion_allowed
    for now in (2., 2.5, 3.):
        assert control.step(route(), (1., 0., 0.5), True, (20., 0., 0.), now) is None
        assert control.state == 'WAIT_DETECTION' and not control.motion_allowed


def test_standstill_resets_and_missing_observation_holds():
    """Keep the SDK idle while moving or while the live confirmation is missing."""
    control = initialized()
    control.step(route(), (1., 0., 0.5), True, (2., 0., 0.), 1.)
    control.step(route(), (1., 0., 0.5), False, (2., 0., 0.), 1.4)
    assert control.step(route(), (1., 0., 0.5), True, (2., 0., 0.), 1.6) is None
    control.step(route(), (1., 0., 0.5), True, None, 2.)
    assert control.state == 'WAIT_DETECTION'


@pytest.mark.parametrize('fault', ['off_path', 'height', 'replan', 'missing_flags'])
def test_active_stairs_hold_on_pose_or_route_fault(fault):
    """Retain the confirmed mode while denying movement on an incompatible replan."""
    control = climbing()
    current, position = route(), (2.1, 0., 0.7)
    if fault == 'off_path':
        position = (2.1, 2., 0.7)
    elif fault == 'height':
        position = (2.1, 0., 3.)
    elif fault == 'replan':
        current = StairRoute([(0., 0., 0.), (2.1, 0., 0.2)], [False, True])
    else:
        current = StairRoute(current.positions, [False] * len(current.stairs))
    assert control.step(current, position, True, None, 3.) is None
    assert not control.motion_allowed and control.stair_mode_active
    assert control.state == 'WAIT_DATA'


@pytest.mark.parametrize('fault', ['too_close', 'tilted', 'height_changing', 'next_stair'])
def test_exit_requires_distance_and_flat_robot_and_path(fault):
    """Keep stair mode until both the landing path and the robot are level."""
    control = climbing()
    current = route()
    position = (3.2, 0., 0.9)
    if fault == 'too_close':
        position = (3.19, 0., 0.9)
    if fault == 'next_stair':
        current.stairs[-1] = True
        # Make the next flagged waypoint fall inside the forward horizon.
        current.positions[-1] = (3.4, 0., 0.4)
        current = StairRoute(current.positions, current.stairs)
    previous_z = 0.86 if fault == 'height_changing' else position[2]
    control.step(current, (2.9, 0., previous_z), False, None, 3.)
    control.step(current, position, False, None, 3.5, level=fault != 'tilted')
    assert control.phase == 'stairs' and control.motion_allowed


def test_error_latches_across_input_loss_until_explicit_retry():
    """A missing SDK cannot be silently retried by path or sensor callbacks."""
    control = climbing()
    control.confirmed(False, 'SDK refused BalanceStand')
    control.hold('missing odometry')
    assert control.state == 'ERROR' and not control.motion_allowed
    assert control.step(route(), (2.1, 0., 0.7), True, None, 3.) is None
    assert control.retry()
    assert not control.retry()


def test_custom_distances_and_short_landing_grouping():
    """Merge steps separated by a short landing and honor alternate approach margins."""
    current = StairRoute([(float(i), 0., 0.) for i in range(8)],
                         [False, False, True, False, True, False, False, False])
    assert current.next_flight(0., 2.1) == (2, 4)
    assert current.next_flight(0., 1.) == (2, 2)
    control = StairCoordinator(0.5, 1.5)
    control.confirmed(True)
    control.step(route(), (1.4, 0., 0.5), False, None, 1.)
    assert control.motion_allowed
    control.step(route(), (1.5, 0., 0.5), False, None, 1.1)
    assert not control.motion_allowed


def test_following_flight_keeps_gait_until_its_own_exit_distance():
    """Advance the active exit across a second nearby flight and eventually return."""
    control = climbing()
    current = StairRoute(route().positions[:-1] + [(3.4, 0., 0.4), (3.5, 0., 0.6),
                                                   (4.5, 0., 0.6), (5.5, 0., 0.6)],
                         [False, False, True, True, True, False, False,
                          True, True, False, False])
    control.step(current, (2.9, 0., 0.9), False, None, 3.)
    assert control.active_end == (3.5, 0., 0.6)
    control.step(current, (4.2, 0., 1.1), False, None, 4.)
    control.step(current, (4.5, 0., 1.1), False, None, 4.5)
    assert control.phase == 'exit' and not control.motion_allowed


def test_initialization_on_staircase_holds_without_normal_switch():
    """Require a flat initial approach when starting a new coordinator."""
    control = StairCoordinator(1., 1.)
    assert control.step(route(), (2.1, 0., 0.7), True, None, 0.) is None
    assert control.step(route(), (2.1, 0., 0.7), True, None, 1.) is None
    assert not control.motion_allowed


def test_replanned_exit_margin_uses_latest_flagged_endpoint():
    """Preserve the full exit margin when a compatible replan extends the last step."""
    control = climbing()
    current = route()
    positions = current.positions[:5] + [(2.3, 0., 0.4)] + current.positions[5:]
    flags = current.stairs[:5] + [True] + current.stairs[5:]
    updated = StairRoute(positions, flags)
    control.step(updated, (2.9, 0., 0.9), False, None, 3.)
    control.step(updated, (3.2, 0., 0.9), False, None, 3.5)
    assert control.active_end == (2.3, 0., 0.4)
    assert control.phase == 'stairs' and control.motion_allowed


def sdk_script(tmp_path, body):
    """Create an isolated test executable which never imports a robot SDK."""
    script = tmp_path / 'fake gait switch'
    script.write_text('#!/usr/bin/python3\n' + body)
    script.chmod(0o755)
    return str(script)


@pytest.mark.parametrize('exit_code', [0, 1, 7])
def test_sdk_literal_arguments_and_confirmed_exit(tmp_path, exit_code):
    """Forward the documented interface/mode arguments and honor every nonzero exit."""
    record = tmp_path / 'args'
    executable = sdk_script(tmp_path, f'import sys\nfrom pathlib import Path\n'
                            f'with Path({str(record)!r}).open("a") as stream:\n'
                            '    stream.write(repr(sys.argv[1:])+"\\n")\n'
                            f'print("confirmed")\nsys.exit({exit_code})\n')
    sdk = SdkSwitch(executable, 'eth0', 5., executable)
    try:
        sdk.start('stairs', time.monotonic())
        with pytest.raises(ValueError):
            sdk.start('normal', time.monotonic())
        deadline = time.monotonic() + 5
        result = None
        while result is None and time.monotonic() < deadline:
            result = sdk.poll(time.monotonic())
            time.sleep(0.01)
        assert result is not None and result[0] is (exit_code == 0)
        expected = ["['eth0', 'prepare']"]
        if exit_code == 0:
            expected += ["['eth0', 'stairs']", "['eth0', 'verify_stairs']"]
        assert record.read_text().splitlines() == expected
    finally:
        sdk.close()


def test_sdk_timeout_reaps_and_missing_binary_fails(tmp_path):
    """Bound a stalled process and report a missing installation explicitly."""
    executable = sdk_script(tmp_path, 'import time\ntime.sleep(30)\n')
    sdk = SdkSwitch(executable, 'eth0', 0.1, executable)
    try:
        sdk.start('normal', 0.)
        process = sdk.process
        assert sdk.poll(0.2) == (False, 'SDK timeout')
        assert process.poll() is not None
    finally:
        sdk.close()
    missing = SdkSwitch(str(tmp_path / 'missing'), 'eth0', 1.)
    with pytest.raises(FileNotFoundError):
        missing.start('stairs', 0.)
    assert missing.output is None


def test_sdk_shutdown_reaps_process(tmp_path):
    """Terminate outstanding test commands on node shutdown."""
    executable = sdk_script(tmp_path, 'import time\ntime.sleep(30)\n')
    sdk = SdkSwitch(executable, 'eth0', 5., executable)
    sdk.start('normal', time.monotonic())
    process = sdk.process
    sdk.close()
    assert process.poll() is not None


def test_finished_sdk_stage_cannot_bypass_overall_deadline(tmp_path):
    """Reject a zero exit observed after the total operation timeout."""
    executable = sdk_script(tmp_path, 'pass\n')
    sdk = SdkSwitch(executable, 'eth0', 0.1, executable)
    try:
        sdk.start('normal', 0.)
        sdk.process.wait(timeout=5)
        assert sdk.poll(0.2) == (False, 'SDK timeout')
    finally:
        sdk.close()


@pytest.mark.parametrize('executable,interface,timeout', [
    ('relative', 'eth0', 1.), ('/tmp/a', '', 1.), ('/tmp/a', 'eth 0', 1.),
    ('/tmp/a', 'eth0', 0.), ('/tmp/a', 'eth0', math.nan)])
def test_sdk_invalid_configuration(executable, interface, timeout):
    """Reject malformed startup settings before creating a subprocess."""
    with pytest.raises(ValueError):
        SdkSwitch(executable, interface, timeout)


@pytest.mark.parametrize('failed_stage', ['prepare', 'stairs', 'verify_stairs'])
def test_sdk_guard_and_switch_failures_never_report_success(tmp_path, failed_stage):
    """Reject failures even when the existing switch tool would return zero."""
    executable = sdk_script(tmp_path, 'import sys\n'
                            f'sys.exit(7 if sys.argv[2] == {failed_stage!r} else 0)\n')
    sdk = SdkSwitch(executable, 'eth0', 5., executable)
    try:
        sdk.start('stairs', time.monotonic())
        deadline = time.monotonic() + 5
        result = None
        while result is None and time.monotonic() < deadline:
            result = sdk.poll(time.monotonic())
            time.sleep(0.01)
        assert result is not None and result[0] is False
    finally:
        sdk.close()


def test_installed_cpp_guard_predicates(installed_share, tmp_path):
    """Compile and run telemetry predicates without linking or contacting an SDK."""
    import subprocess
    source = tmp_path / 'rules.cpp'
    source.write_text('''
#include "gait_guard.hpp"
#include <cassert>
#include <limits>
int main() {
  r3d::GaitState state;
  state.mode = 1;
  assert(r3d::ready(state, 0));
  assert(!r3d::ready(state, 1));
  state.mode = 2;
  assert(!r3d::ready(state));
  state.mode = 1;
  state.error = 1;
  assert(!r3d::ready(state));
  state.error = 0;
  state.velocity[0] = 0.1f;
  assert(!r3d::ready(state));
  state.velocity[0] = std::numeric_limits<float>::quiet_NaN();
  assert(!r3d::stationary(state));
  state.velocity[0] = 0;
  state.yaw_speed = 0.1f;
  assert(!r3d::stationary(state));
}
''')
    binary = tmp_path / 'rules'
    subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                    '-I' + str(installed_share / 'sdk'), str(source), '-o', str(binary)],
                   check=True, capture_output=True, text=True)
    subprocess.run([str(binary)], check=True, timeout=5)
