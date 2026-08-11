#!/usr/bin/env bash
# Check my.itmo.ru login status

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

load_env 2>/dev/null || { echo "NOT_CONFIGURED: .env missing"; exit 2; }

# Reuse session or login if expired
ensure_logged_in

url="$(current_url)"
if is_logged_in; then
  echo "LOGGED_IN"
  echo "url=${url}"
  $AB snapshot -i 2>&1 | head -30
else
  echo "NOT_LOGGED_IN"
  echo "url=${url}"
  exit 1
fi
