# Maintenance and release policy

## Development version and change control

All three packages currently use 0.0.1 as an unreleased development version;
V4 is a branch name, not version 4.0.0. Package changelogs use Forthcoming and
contain no release tag/date. The cleaned local main is the selected future
development source. Public synchronization, release version, tag and Bloom track
remain separate decisions. The current CI metadata guard
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
are not available. M02 obstacle monitoring/TF stop behavior is implemented as an opt-in feature;
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
separate checks. The cleaned main remains local: no public migration, ROS Index
PR, release tag,
Bloom track or successful farm job is created by this project work. Root/package
Apache-2.0 notices are implemented. The developer has confirmed licensing
authority over his own software after consultation with the supervising professor.
The four legacy PCD blobs were removed from every local candidate ref, including
historical copies and the technical tree ref. Original data remain in the private
backup and old public clones; concrete third-party/binary-bundle obligations and
any separately used document/image rights remain to be checked. Do not rewrite
Git history or alter external LiDAR projects as part of routine release prep.
A future release must resolve concrete redistribution obligations, select its
version/target, publish the
approved source ref, validate clean target builds, run CI and obtain the external
reviews. Forthcoming changelogs and local tests are preparation, not a release.

## Distribution investigation (15 October 2026)

| Target | Current evidence | Support boundary |
|---|---|---|
| Humble / Jammy / Python 3.10 amd64 | Clean copy build, rosdep, 358 colcon records and343 unique source-free cases pass | Verified tested scope |
| Jazzy / Noble / Python 3.12 amd64 | Full rosdep blocked by Open3D; generated interface alone builds and passes five checks plus CDR | Planner/preprocessor not verified |
| Kilted / Noble | Same official Open3D system rule; no native build/test | Not supported by this evidence |
| Lyrical / Resolute / Python 3.14 amd64 | All dependencies and three-package build pass; default colcon Python test discovery fails; direct pytest 218 pass /2 lint failures | Partial investigation, no complete support claim |
| Rolling | Current official image uses Resolute; no native verification | Development target only |

Newer Nav2 actions add error fields and, in Lyrical, viapoints. Their full contract
is not implemented or verified here. No pip/vendor migration was applied.
See central protocol section18.8 for commands, exact images and remaining work.

## Binding target decision during M02

The only current development/release target is ROS2 Humble, Ubuntu22.04 Jammy,
Python3.10 with the verified apt dependencies. Jazzy/Lyrical/Rolling are deferred,
so lack of multi-distribution support is not a Humble release blocker. Their
previous investigation results remain dated evidence. AP07 retains the Humble
workflow and an unverified remote status; AP09 is assessed against Humble.
AP10 still requires rights/public-source/version/release-organization and
external release checks. M02 monitoring does not close these separate gates.


Local Debian packaging was also exercised for all three packages: peer-aware Bloom
preparation, unsigned package build/install and a fresh source-free runtime probe
with dpkg file ownership, versions, dependencies and ROS interfaces passed.
These are local artifacts, not an official Bloom or Buildfarm release. Bloom's
generated rules retain their tolerant test exit behavior. The required local
release wrapper now validates the actual reports and complete test identities,
rejecting failures, errors, skips and missing evidence independently of Bloom.
Installation-dependent checks run in a mandatory fresh Debian runtime container.
For the complete local preflight use `bash scripts/ci/run_humble_release.sh`
from a clean committed checkout. It runs both ordinary CI and the complete
Debian gate, then validates source/report/artifact identity. Individual runners
remain diagnostic entry points; this command does not authorize a release.


## Final audit decision boundary (19 October 2026)

The final AP10 audit is in section 22 of the central protocol. R28 remains locally
verified; its extra test-phase selection and mandatory post-install gate are not
automatically installed in an official Bloom/Buildfarm workflow. R29 now supplies package-native Jammy build reports and a mandatory combined
workflow entry point. The workflow and pinned report archival are prepared
locally but have not run remotely. Configure and verify Required Checks and
the official process before claiming equivalent external test enforcement.

All packages remain 0.0.1 with Forthcoming changelogs. A common 0.1.0 initial public
prerelease is a recommendation, not an authorized version change. Own-code
licensing authority and the local cleaned main/history scope are now
confirmed; Bastian Aumer remains maintainer and licensor of his own parts.
The candidate has no legacy PCD blobs in any reachable ref or its object database.
Public synchronization, concrete third-party redistribution obligations,
support/EOL terms and release timing remain separate. See section23 of the
central protocol for the full mapping, private backup, new successful Humble and
Debian checks, and the still-open official test-integration gate R29.


## R29 local preflight boundary (20 October 2026)

Use `bash scripts/ci/run_humble_release.sh` on a clean committed candidate.
The package-native build phase, full independent Debian runtime, case identities,
source commit/tree/file hashes, fresh run context and archive/report hashes are
checked together. Errors, missing phases or stale/replaced exports reject the
gate. The original thirteen controls remain; the complete current gate suite
contains37 cases. No generated Bloom rule is patched and no test is replaced by
a skip. The local proof is preparation, not a maintainer release decision.
Official Source/PR test jobs, release binary jobs, Jenkins report handling and
repository publication have distinct semantics. Their actual configuration and
results still require authorized external verification. R29 overall remains
BLOCKED; see the complete acceptance matrix in protocol section24.
