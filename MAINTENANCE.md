# Maintenance and release policy

## Development version and change control

All three packages currently use 0.0.1 as an unreleased development version;
V4 is a branch name, not version 4.0.0. Package changelogs use Forthcoming and
contain no release tag/date. A release version, public branch, tag and Bloom
track require a separate maintainer decision. The current CI metadata guard
checks the research development version; review that guard with an authorized
version change. Keep package.xml/setup.py versions consistent.

Use focused reviewed changes and regression evidence. The central research
protocol preserves historical baseline findings and records each implementation;
package changelogs are a public change summary, not the research record.
Before publication, choose and document a SemVer policy for future releases.
No stable API/ABI or REP-2004 Quality Level is claimed for this unreleased tree.
Generated ROS interface fields are public contracts; changes need compatibility
review and coordinated consumers. No binary or DDS interoperability across ROS
distributions is promised.

## Supported and verified scope

The tested target is Ubuntu 22.04/Jammy amd64, ROS 2 Humble and system Python3.10
with apt-managed dependencies. Container image and observed versions are recorded
in the central protocol; live apt/rosdep indexes are not a permanent lockfile.
Native and source-free tests use synthetic inputs without hardware. Historical
Go2W operation predates these V4 changes and is not a V4 deployment regression.
Other distributions/platforms are investigation targets, not supported by a
Humble test. Refer to INSTALL.md and the compatibility matrix in the protocol.

The CI workflow is implemented and locally reproducible, but NOT REMOTELY
VERIFIED until an authorized push and actual GitHub Actions run. Do not display a
successful remote badge without evidence. Coverage and hardware certification
are not available. M02 obstacle monitoring/TF stop behavior remains deferred;
a fresh published path or cloud is not a guarantee of physical safety.

## Support, EOL and security

Maintainer/contact are declared in package.xml; no response-time, security-fix,
long-term maintenance or funded support SLA has been established. ROS upstream
EOL dates do not themselves promise this project's support duration. Decide
project EOL/support scope before a public release; current development may change.
For sensitive defects contact the declared maintainer before posting private
robot/data details. There is no dedicated security service, disclosure SLA or
claimed security audit. Do not treat this navigation prototype as a certified
safety controller; deployment needs independent watchdogs, arbitration and stop
facilities outside the current repository.

## Release gates

Source indexing, rosdep resolution, Bloom, Buildfarm jobs and Debian delivery are
separate checks. V4 is local: no public source ref, ROS Index PR, release tag,
Bloom track or successful farm job is created by this project work. Root/package
Apache-2.0 notices are implemented; remaining contractual, historical Git-data
and concrete binary-bundle rights require separate resolution. Do not rewrite
Git history or alter external LiDAR projects as part of routine release prep.
A future release must confirm rights, select its version/target, publish the
approved source ref, validate clean target builds, run CI and obtain the external
reviews. Forthcoming changelogs and local tests are preparation, not a release.
