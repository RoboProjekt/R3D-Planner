# Contributing

V4 is local development and is not an official ROS release. Do not publish a
research checkout, data, tags or releases without the maintainer's authorization.
Use a focused change with a concrete issue, interface impact and suitable tests.
During the research project, implementation changes also update the single
`docs/V4_ROS_COMPLIANCE_DEVELOPMENT.md` protocol; do not create replacement reports.

For a bug report include ROS/Ubuntu/Python versions, the commit, install type,
rosdep output and a minimal configuration/reproduction. Use synthetic PCD/ROS
messages; do not upload sensitive maps, credentials, robot identifiers or data
you cannot redistribute. State whether the failure occurs in a clean copy build.

Run `bash scripts/ci/run_humble.sh` with Docker already available. It builds/tests
three packages and checks a source-free installation in isolated containers.
Do not introduce dependency skips, suppress test groups or claim unexecuted CI.
Tests must use isolated ROS domains/topics and no hardware drivers or motion.

Changes to message fields, names, geometry semantics, TF ownership or controller
input requirements need an explicit compatibility/migration assessment. M01 is
the approved PathWithMetadata migration; M02 is a proposal and requires separate
authorization before implementation. See MAINTENANCE.md for current support,
versioning and release boundaries.
