#!/usr/bin/env bash
set -euo pipefail

preset_name=${PRESET:-RelWithDebInfo}
exe_path="build-${preset_name}/src/merge"

if [[ ! -f "${exe_path}" ]]; then
  echo "Executable not found: ${exe_path}" >&2
  exit 1
fi

"${exe_path}" "${@}"
