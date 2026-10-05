# STRIDE threat model

The adversary is a controlled ROS participant inside the project's Docker
network. The insecure run deliberately grants no DDS identity protection. The
secure run grants the attacker its own valid identity with tightly scoped
permissions. Host compromise, arbitrary exploit development and real hardware
are outside the experiment, but remain residual deployment risks.

## Assets and boundaries

Assets: `/cmd_vel` integrity, node identity, DDS communication confidentiality
and integrity, SROS2 private keys, signed governance, permission policies,
container images, software dependencies and SBOM inventory data.

Boundaries: Docker host to containers; ROS participant to DDS domain; legitimate
robot to lab attacker; each container to its mounted enclave; build environment
to external dependency registries. Signing keys and runtime participant keys
are separate assets and must remain separately exposed.

## Threat assessment

| STRIDE | Asset | Threat | Attack surface | Impact | Mitigation | Residual risk |
|---|---|---|---|---|---|---|
| Spoofing | Node identity | Node impersonation | DDS discovery and identity handshake | False trusted participant | Signed identity certificates and enforced security | Stolen authorized identity works within its permissions |
| Tampering | /cmd_vel integrity | Unauthorized publisher | Matching DDS DataWriter | Conflicting movement commands in logs | Default-deny policy; only navigation may publish cmd_vel | Compromised navigation identity can issue commands |
| Information disclosure | DDS data | Unauthorized subscriber | Matching DataReader | Disclosure of sensor/command messages | Topic read permissions and authenticated joining | Authorized readers and host can access data |
| Information disclosure | DDS communication | Eavesdropping | UDP RTPS traffic on bridge | Loss of payload confidentiality | DDS encrypted data protection checked during setup | Some metadata, sizes and timing remain observable |
| Tampering | Command integrity | Command tampering in transit | RTPS application messages | Modified command values | DDS cryptographic integrity protection | Implementation flaws or endpoint compromise |
| Information disclosure | Private keys | Credential leakage | Bind mounts, Git, build context, backups | Attacker acquires a trusted identity | Per-enclave mounts; no signing CA mount; Git/build exclusions; owner-only files | Host administrator and weak Windows permissions |
| Elevation of privilege | Permissions/governance | Over-permissive authorization | Policy generation and signed XML | Unintended writes/reads | Checked-in exact allow list, explicit command denial, export guards and tests | Policy tooling errors; review generated permissions |
| Tampering | Dependencies | Compromised dependency | Ubuntu and ROS package sources | Malicious runtime code | Official repositories, SBOM, vulnerability review | Vulnerability scans do not detect all malicious code |
| Tampering / elevation | Container image | Compromised image | Base image and local build | Identity theft or malicious publisher | Official base, local build, hardening, Trivy | Mutable tags and host/build compromise |
| Tampering / repudiation | SBOM and supply chain | Supply-chain compromise | CI, build inputs, artifact provenance | Incomplete inventory or altered image | Source review, minimal CI permissions, record digests and scan logs | No signed release provenance in this first version |
| Denial of service | DDS availability | Message/discovery flooding | Shared bridge and DDS resource limits | Legitimate communication delayed or lost | Scope isolation and small deterministic participants | DDS authorization is not comprehensive rate limiting |
| Repudiation | Experiment evidence | Misattributed commands | Twist values and container logs | Incorrect conclusions | Preserve actual logs and require live heartbeat plus legitimate delivery | Value classification does not authenticate source attribution |

## Security concepts

Authentication answers who holds an accepted participant identity. Authorization
answers which resources that identity may use. Confidentiality encrypts content;
integrity protects it against undetected modification. Least privilege gives
each identity only the communication required by its role.

The attacker status channel is a deliberate teaching extension: successful
delivery while enforced security is active supports accepted identity and
authorized status publication. Rejected or undelivered `/cmd_vel` publication
demonstrates a separate permission decision. A dead attacker alone is not proof
of access-control enforcement. Verify runtime governance and signed permissions,
as well as logs, before drawing the security conclusion.
