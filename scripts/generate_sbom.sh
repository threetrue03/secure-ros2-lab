#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v trivy >/dev/null || { echo 'Install host Trivy to generate an SBOM.' >&2; exit 1; }
mkdir -p artifacts
trivy image --image-src docker --format cyclonedx --output artifacts/sbom.cdx.json "${1:-secure-ros2-lab:jazzy}"
test -s artifacts/sbom.cdx.json
