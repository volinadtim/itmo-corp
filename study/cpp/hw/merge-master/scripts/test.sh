#!/usr/bin/env bash
set -euo pipefail

preset_name=${PRESET:-RelWithDebInfo}
exe_path="build-${preset_name}/src/merge"

if [[ ! -f "${exe_path}" ]]; then
  echo "Executable not found: ${exe_path}" >&2
  exit 1
fi

if ! python3 -m pytest --noconftest --version >/dev/null 2>&1; then
  echo "pytest is not available, maybe you forgot to activate your virtual environment?" >&2
  exit 1
fi

python3 -m pytest test --maxfail=1 --exe "${exe_path}" "${@}"
