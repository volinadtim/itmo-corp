#!/usr/bin/env bash
# Snapshot current page (or given URL)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

URL="${1:-}"

ensure_logged_in

if [[ -n "$URL" ]]; then
  echo "→ Opening ${URL}"
  $AB open "$URL" >/dev/null
  $AB wait --load networkidle >/dev/null 2>&1 || true
fi

echo "url=$(current_url)"
echo ""
$AB snapshot -i 2>&1
