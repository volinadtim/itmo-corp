#!/usr/bin/env bash
# Login to my.itmo.ru and persist session

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

load_env
do_login
echo "Session saved (session: ${SESSION_NAME})"
