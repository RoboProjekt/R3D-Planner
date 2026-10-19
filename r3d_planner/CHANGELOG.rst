Changelog for package r3d_planner
=================================

Forthcoming
-----------

* Classify installation-dependent tests explicitly and verify registered ROS prefixes
  for copied and Debian installations; retain all functional regressions.
* Declare ROS and science APIs needed during build-time test execution.
* Retain height-qualified near obstacle returns before the legacy radial gate
  can erase the follower stop region; add optional startup-only
  retain_near_obstacles (true by default, false restores legacy output).
* Add geometry boundaries, configuration and native sensor/filter/follower
  command regressions; preserve M01/M02 and existing numeric limits.
* Existing graph reconstruction, A* and navigation components retained from the baseline.
* Consistent metadata/dependencies and source-independent configuration/install behavior.
* Replace legacy quaternion narrow flags with atomic typed metadata; migrate follower.
* Cooperative action cancellation/result timing and pose/frame validation.
* Optional launch namespaces/remapping, sensor-input QoS and RViz/TF validation.
* Installed/interface/native ROS regressions and local two-container CI preparation.
* Add opt-in obstacle monitoring with strict startup parameters and compatible legacy defaults.
* Validate original measurement and monotonic receipt age, clock changes, geometry and timestamped TF.
* Enforce zero commands and validated automatic recovery; retain the optional filter and external producers.
* Support reliable/best-effort obstacle input and reject false clear output from nonfinite-only raw input.
* Add synthetic unit, native ROS, installed-launch and source-free monitoring regressions.
* Restrict current release preparation to Humble/Jammy/Python3.10; no hardware safety claim.
