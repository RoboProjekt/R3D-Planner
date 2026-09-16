# Documentation scope on V3

The PCD-only package boundaries and generic topic/action names from V2 remain.
V3 replaces ordinary manual parameter lists with central YAML launch startup and
introduces a standard Odometry input independent of a particular SLAM package.

- README.md: overview, installation summary and offline/online usage.
- INSTALL.md: dependencies, initial symlink build, configuration, startup and tests.
- CONFIGURATION.md: full runtime schema, parameter ownership, defaults and restart workflow.
- ARCHITECTURE.md: node, configuration and ROS data flow.
- KNOWN_ISSUES.md: remaining constraints and resolved V2 findings.
- REFERENCE_COMPARISON.md: explicitly frozen historical V2 comparison.
- Package README.txt files: node interfaces and package-specific behavior.

Normal entry points are preprocessor.launch.py and planner.launch.py in
r3d_planner. Optional map.launch.py publishes the centrally selected map.
follower.launch.py is an explicit motion-producing launch, never included
automatically. Direct ros2 run remains available only for developer overrides.

Robot YAML owns geometry, odometry topic/frames and hardware cloud/command topics.
The central YAML owns shared map-analysis/reconstruction settings, algorithm and
controller tuning, plus independent Live Filter/RViz launch booleans.
YAML changes and new robot configurations need only process restart with the
supported symlink installation. No runtime config files are generated.
