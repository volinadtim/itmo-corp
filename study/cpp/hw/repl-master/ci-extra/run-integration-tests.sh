#!/usr/bin/env bash
set -euo pipefail

preset_name=$1

python3 -m pytest integration-tests/tests --exe "build/${preset_name}/app/repl-app"
