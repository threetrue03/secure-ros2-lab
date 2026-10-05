# Container security

## Implemented controls

Runtime services use a non-root Linux user (the invoking user's UID/GID through
Make), drop every Linux capability, and enable `no-new-privileges`. They have
read-only root filesystems and a 64 MiB `/tmp` with `nosuid,nodev`. ROS logs are
written into `/tmp`, while Docker captures stdout/stderr. No devices, host
networking, elevated capabilities, privileged mode, or socket mounts are used.
Only the internal `secure_ros2_lab` bridge is attached, and no ports are published.

All nodes use UDPv4 transport within that bridge; Fast DDS shared-memory
transport is disabled by the checked-in XML profile. Credentials are separate
read-only bind mounts. Export dereferences SROS2's public-certificate symlinks,
copies exactly six participant files, sets directories to owner-only access,
and omits the CA signing keys and other identities. Docker refuses missing mount
sources. The build context excludes `.env`, runtime material and evidence.

The official ROS Jazzy base and apt package list keep dependencies focused:
rclcpp/rclpy, standard messages, Fast DDS, SROS2 and package-build/test tooling.
Trivy is a host tool, so scanning never requires mounting the host Docker socket
in a ROS container. CycloneDX and vulnerability reports are ignored artifacts.

## Known limitations

The image retains build/test tooling so `make test` can run without a second
runtime image; a validated release could use a smaller multi-stage final image.
Tags and apt versions are mutable, so two builds at different times can differ.
CI currently uses tagged actions. Record the base and built-image digests for
each evidence run. SBOM generation is inventory, not security certification.

The setup service needs writable runtime storage and therefore is not given
a read-only root filesystem. It is offline, capability-free and short-lived.
Its owner can read signing material on the host; protect the checkout and backups.
Windows-mounted volumes may not honor POSIX permissions. A Linux filesystem
under WSL2 is preferred for runtime keys. Make exports UID 0 if invoked by root;
run as a normal Linux user to preserve the non-root runtime control.

## Residual risks

Containers share the host kernel and are not a perfect security boundary.
A compromised Docker daemon or host can read keys and join as authorized nodes.
An authorized navigation identity can publish malicious commands; DDS permissions
do not validate command semantics. The lab has no safety controller, watchdog,
rate limiter, motor firmware, or physical stop mechanism because it has no
actuators. Unauthenticated traffic can still consume network and CPU resources.

The internal bridge is containment for a trusted local educational lab, not an
Internet attack sandbox. Do not join other networks or mount host devices.
Inspect scan findings and update vulnerable packages. DDS Security protects
communication subject to correct middleware behavior, policy and credential management.
