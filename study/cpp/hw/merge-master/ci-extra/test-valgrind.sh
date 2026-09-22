#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"

preset_name=$1

python3 -m pytest test \
  --exe "build/${preset_name}/src/merge" \
  --valgrind-wrapper "${SCRIPT_DIR}/run-valgrind.sh" \
  --maxfail=1
