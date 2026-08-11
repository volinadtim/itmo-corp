#!/usr/bin/env bash
# Open «Заявки и очереди» and snapshot available applications

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ensure_logged_in

echo "→ Opening applications..."
# Common routes — SPA may redirect; agent navigates by UI if needed
for url in \
  "https://my.itmo.ru/applications" \
  "https://my.itmo.ru/requests" \
  "https://my.itmo.ru/services/applications"; do
  $AB open "$url" >/dev/null 2>&1 || true
  $AB wait --load networkidle >/dev/null 2>&1 || true
  if is_logged_in; then
    break
  fi
done

# Fallback: open home, click «Requests and queues» in sidebar (@e12 on dashboard)
if ! is_logged_in; then
  ensure_logged_in
fi

$AB open "https://my.itmo.ru" >/dev/null
$AB wait --load networkidle >/dev/null 2>&1 || true
$AB find text "Requests and queues" click >/dev/null 2>&1 || \
  $AB click @e12 >/dev/null 2>&1 || true
$AB wait --load networkidle >/dev/null 2>&1 || true

echo "=== URL ==="
current_url

echo ""
echo "=== Snapshot (interactive elements) ==="
$AB snapshot -i 2>&1
