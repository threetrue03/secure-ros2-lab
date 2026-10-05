#!/usr/bin/env bash
set -euo pipefail
cd /opt/lab
umask 077
root=/runtime/keystore
if [[ -e "$root" || -e /runtime/mounts ]]; then
  echo 'Runtime material already exists. Stop the lab and use make clean before regenerating.' >&2
  exit 1
fi
# Check the installed Jazzy tooling before using its documented positional CLI.
ros2 security create_keystore --help
ros2 security create_enclave --help
ros2 security create_permission --help
ros2 security create_keystore "$root"
python3 /opt/lab/security/scripts/configure_governance.py "$root" /opt/lab/security/policies/governance.xml
for enclave in /robot/camera /robot/perception /robot/navigation /robot/motor /lab/attacker; do
  ros2 security create_enclave "$root" "$enclave"
  ros2 security create_permission "$root" "$enclave" /opt/lab/security/policies/lab.policy.xml
done
python3 /opt/lab/security/scripts/export_credentials.py "$root" /runtime/mounts
touch /runtime/.ready
echo 'Created local credentials and restricted per-service keystore mounts.'
