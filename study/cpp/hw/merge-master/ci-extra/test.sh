#!/usr/bin/env bash
set -euo pipefail

preset_name=$1

python3 -m pytest test \
  --exe "build/${preset_name}/src/merge" \
  --maxfail=1
