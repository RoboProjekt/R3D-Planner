# Contributing

The cleaned local main contains the V4 development and is not an official ROS
release. Do not publish a research checkout, data, tags or releases without the
maintainer's authorization.
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
the approved PathWithMetadata migration; M02 is implemented as optional monitoring.
Retain its fail-closed contract when enabled and assess changes to local geometry,
including the startup-only retain_near_obstacles policy. See MAINTENANCE.md for current support,
versioning and release boundaries.

Current changes target only Humble/Jammy/Python3.10. For obstacle-monitoring
reports include the four startup parameters, original measurement stamps, frames,
TF timing, state transition and synthetic reproduction. Use unique isolated
command topics and retain M01, disabled-mode and stop/recovery regressions.


For packaging changes also run `bash scripts/ci/run_humble_debian.sh`. Keep actual
installation requirements explicit through the `installed` marker/fixture contract;
all such tests must run in the mandatory post-install stage. Do not use source
fallbacks, skips or Bloom's tolerated dh_auto_test exit as a green result. Review
case identities and reports, and keep the deliberately failing temporary-copy
probe nonzero. No generated release repository or public template is edited here.


For a release candidate run `bash scripts/ci/run_humble_release.sh` from a clean
committed checkout. It executes both existing runners and requires every test
phase plus exact source/report/archive identity. The full gate-control suite is
part of the Debian build container. Package-native pybuild hooks handle the
build/install split; do not reintroduce wrapper-only selection or skip tests.
The prepared GitHub job runs this same command; Remote CI and Required Checks
remain unverified until separately authorized and actually configured. No release
or publication trigger is introduced. Maintainer release approval remains manual.
