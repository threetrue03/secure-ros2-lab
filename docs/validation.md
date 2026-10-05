# Implementation validation — 2026-10-05

## Environment

The project was created at `C:\projects\secure-ros2-lab` on Windows. Git
2.53.0.windows.3 and Python 3.13 were available; the bundled Python 3.12.14 was
also checked. Docker, Docker Compose, GNU Make, ROS 2, Trivy and a native C++
compiler were not available on PATH. Docker's standard installation path was
absent. `wsl --status` returned `Wsl/EnumerateDistros/Service/E_ACCESSDENIED`.
The WindowsApps Bash launcher depends on unavailable WSL, so no Linux shell
or ROS runtime was usable for this task.

## Checks actually run

* `git --version`, `git init -b main C:\projects\secure-ros2-lab`, and
  `git rev-parse --show-toplevel`: confirmed this standalone repository root.
* `python scripts/validate_repo.py`: five passing tests for manifest/syntax,
  exact policy publication roles, explicit governance, attacker command/scope, required files and
  private material ignore rules.
* `python -m unittest discover -s tests -v`: Compose isolation/hardening checks
  rejection of unencrypted synthetic governance, and exact compiled-permission checks passed; POSIX-only
  credential export test skipped on Windows.
* Python AST parsing and XML parsing cover all source Python and XML inputs;
  PyYAML loads both Compose files and GitHub Actions configuration.
* Git ignore checks, status and cached-diff checks confirmed no staged private
  material. Nothing was committed and no remote or push was configured.

Initial credential fixture tests failed because Windows owner-only temporary
directory ACLs were inaccessible in the execution sandbox. Synthetic fixture
creation now uses an ordinary ignored artifacts directory, and the successful
owner-only export test explicitly requires Linux. The three host-compatible
configuration/governance/compiled-permission checks were rerun successfully. Empty failed
fixture folders were cleaned up. No real credentials were generated.

## Unexecuted validation

| Check | Reason | Reproduction |
|---|---|---|
| Docker Compose semantic validation | Docker unavailable | `docker compose -f compose.insecure.yaml --profile attack config --quiet` and secure equivalent |
| Image and both ROS package builds | Docker/ROS/compiler unavailable | `make build` |
| C++ gtest and Python package pytest | ROS and pytest unavailable | `make test` |
| Successful owner-only credential export | Linux permissions required | `make test` in built image |
| Installed Jazzy SROS2 CLI/schema/signature compatibility | ROS/Docker unavailable | `make secure-setup` |
| Unsecured unauthorized command delivery | No DDS runtime | `make insecure-up`, inspect logs, `make down` |
| Secure legitimate delivery, status participation, denied command | No DDS runtime | `make secure-setup`, `make secure-up`, inspect logs, `make down` |
| Bounded automated integration checks | Docker/Make unavailable | `make integration-test` |
| SBOM and vulnerability report | Docker/Trivy unavailable | `make sbom`, `make scan` |
| Packet analysis and screenshots | No running DDS bridge/capture environment | Follow wireshark-analysis.md and evidence/README.md |
| GitHub Actions execution | Local repository only, no push requested | Run workflow after an authorized future publication |

Runtime results remain unverified. In particular, there is no claimed attacker
delivery or denial, no invented middleware exception, no generated scan result,
and no packet evidence. Linux CI includes both image/package tests and actual
insecure/secure delivery checks; it has not run in this session.

## Documented design choices

The status heartbeat adds one harmless topic to the specified pipeline so that
accepted secure participation can be distinguished from denied command publication.
Camera String metadata and PointStamped targets replace custom sensor interfaces.
The attacker may publish parameter events because rclpy creates that infrastructure
endpoint. Other optional parameter/log endpoints are disabled. DDS domain 42 and
UDPv4 are fixed to keep the controlled participant in the intended lab.

Per-service exported keystores replace whole-keystore mounts to prevent a container
from reading other identities or CA signing keys. Setup uses the invoking Linux
UID/GID for owner-only credential access, creates a success marker only after
all exports complete, and checks installed CLI help before running standard
positional SROS2 commands. Explicit checked-in governance is validated against the
installed SROS2 DDS schema and signed with OpenSSL before creating enclaves.
Compiled permissions must match each role exactly, including domain 42 and the
middleware discovery topic. Full installed-version compatibility is still untested.

Build dependencies remain in the single image to support repeatable `make test`;
this increases image size and scan surface. No external offensive action,
network scanning, real robot interaction, commit, or push was performed.
