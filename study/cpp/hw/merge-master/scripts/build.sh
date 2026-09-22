#!/usr/bin/env bash
set -euo pipefail

preset_name=${PRESET:-RelWithDebInfo}

# Configure
cmake -B "build-${preset_name}" --preset "${preset_name}"

# Build
cmake --build "build-${preset_name}" -j
