Changelog for package r3d_planner
=================================

Forthcoming
-----------

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
