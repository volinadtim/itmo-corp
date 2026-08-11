#!/usr/bin/env bash
# Shared helpers for my.itmo.ru browser automation

set -euo pipefail

ITMO_CORP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SESSION_NAME="${MY_ITMO_SESSION:-my-itmo}"
AB="npx --yes agent-browser --session ${SESSION_NAME}"

load_env() {
  local env_file="${ITMO_CORP_ROOT}/.env"
  if [[ ! -f "$env_file" ]]; then
    echo "ERROR: ${env_file} not found. Copy .env.example → .env and fill credentials." >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  set -a && source "$env_file" && set +a
  if [[ -z "${MY_ITMO_EMAIL:-}" || -z "${MY_ITMO_PASSWORD:-}" ]]; then
    echo "ERROR: MY_ITMO_EMAIL and MY_ITMO_PASSWORD must be set in .env" >&2
    exit 1
  fi
}

current_url() {
  $AB get url 2>/dev/null | tail -1
}

is_logged_in() {
  local url
  url="$(current_url)"
  [[ "$url" == *"my.itmo.ru"* ]] && [[ "$url" != *"id.itmo.ru"* ]] && [[ "$url" != *"/login"* ]]
}

do_login() {
  echo "→ Opening my.itmo.ru..."
  $AB open "https://my.itmo.ru" >/dev/null
  $AB wait --load networkidle >/dev/null 2>&1 || true

  if is_logged_in; then
    echo "✓ Already logged in: $(current_url)"
    return 0
  fi

  echo "→ Logging in via ITMO ID (Keycloak)..."
  $AB wait "#username, input[name=username], [ref=e4]" 15000 >/dev/null 2>&1 || \
    $AB wait @e4 15000 >/dev/null 2>&1 || true

  # Snapshot to get refs (Keycloak form)
  local snap
  snap="$($AB snapshot -i 2>&1)" || true

  if echo "$snap" | grep -q 'textbox "Email"'; then
    $AB fill @e4 "$MY_ITMO_EMAIL" >/dev/null
    $AB fill @e5 "$MY_ITMO_PASSWORD" >/dev/null
    $AB click @e9 >/dev/null
  elif echo "$snap" | grep -qi 'username\|email'; then
    $AB find label "Email" fill "$MY_ITMO_EMAIL" >/dev/null 2>&1 || \
      $AB fill "#username" "$MY_ITMO_EMAIL" >/dev/null 2>&1 || \
      $AB keyboard type "$MY_ITMO_EMAIL" >/dev/null 2>&1
    $AB find label "Password" fill "$MY_ITMO_PASSWORD" >/dev/null 2>&1 || \
      $AB fill "#password" "$MY_ITMO_PASSWORD" >/dev/null 2>&1
    $AB find role button click --name "Sign In" >/dev/null 2>&1 || \
      $AB click @e9 >/dev/null 2>&1
  else
    echo "ERROR: Could not find login form. Run: npx agent-browser --session ${SESSION_NAME} snapshot -i" >&2
    exit 1
  fi

  $AB wait --load networkidle >/dev/null 2>&1 || true
  sleep 2

  if is_logged_in; then
    echo "✓ Login successful: $(current_url)"
    $AB state save "${ITMO_CORP_ROOT}/integrations/my-itmo/.session/auth.json" >/dev/null 2>&1 || true
    return 0
  fi

  echo "ERROR: Login failed. URL: $(current_url)" >&2
  echo "Tip: run with --headed to debug: AGENT_BROWSER_HEADED=1 $0" >&2
  exit 1
}

ensure_logged_in() {
  load_env
  $AB open "https://my.itmo.ru" >/dev/null 2>&1 || true
  $AB wait --load networkidle >/dev/null 2>&1 || true
  if ! is_logged_in; then
    if [[ -f "${ITMO_CORP_ROOT}/integrations/my-itmo/.session/auth.json" ]]; then
      $AB state load "${ITMO_CORP_ROOT}/integrations/my-itmo/.session/auth.json" >/dev/null 2>&1 || true
      $AB open "https://my.itmo.ru" >/dev/null
      $AB wait --load networkidle >/dev/null 2>&1 || true
    fi
  fi
  if ! is_logged_in; then
    do_login
  fi
}
