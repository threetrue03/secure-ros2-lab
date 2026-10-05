#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v trivy >/dev/null || { echo 'Install host Trivy to scan the local image.' >&2; exit 1; }
mkdir -p artifacts
trivy image --image-src docker --scanners vuln --severity HIGH,CRITICAL --exit-code 1 \
  --format json --output artifacts/trivy.json "${1:-secure-ros2-lab:jazzy}"
# Exit code 1 means findings or an error; inspect the report rather than claiming safety.
