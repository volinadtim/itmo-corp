#!/usr/bin/env bash
# Выкачивание материалов ITMO LMS по сессионной куке.
#
# Кука берётся из файла вне репозитория (по умолчанию ~/.config/itmo-lms/session),
# в котором лежит одно значение MoodleSession. Как получить — см. README.md.
#
#   bash integrations/lms/fetch.sh <out_dir> <id> [<id> ...]
#   bash integrations/lms/fetch.sh study/modeling/materials/lms 6916 38373 7289

set -euo pipefail

COOKIE_FILE="${LMS_COOKIE_FILE:-$HOME/.config/itmo-lms/session}"
BASE="https://lms.itmo.ru"

[ -f "$COOKIE_FILE" ] || { echo "Нет файла с кукой: $COOKIE_FILE" >&2; exit 1; }
SESSION="$(tr -d '[:space:]' < "$COOKIE_FILE")"
[ -n "$SESSION" ] || { echo "Файл $COOKIE_FILE пуст" >&2; exit 1; }

OUT="${1:?укажи каталог назначения}"; shift
[ $# -gt 0 ] || { echo "укажи хотя бы один id ресурса" >&2; exit 1; }
mkdir -p "$OUT"

check() {
  local code
  code=$(curl -sS -o /dev/null -w '%{http_code}' -b "MoodleSession=$SESSION" \
    "$BASE/my/" --max-time 20)
  [ "$code" = 200 ] || { echo "Сессия недействительна (HTTP $code). Обнови куку." >&2; exit 2; }
}

check

for id in "$@"; do
  # mod/resource/view.php редиректит на pluginfile с настоящим именем файла
  if curl -sS -L -J -O --output-dir "$OUT" \
       -b "MoodleSession=$SESSION" \
       "$BASE/mod/resource/view.php?id=$id&redirect=1" --max-time 120; then
    echo "ok   $id"
  else
    echo "FAIL $id" >&2
  fi
done

# HTML-страницу входа вместо файла легко проглядеть — подсветим
grep -rl "Вход на сайт" "$OUT" 2>/dev/null | while read -r f; do
  echo "ВНИМАНИЕ: вместо файла скачалась страница логина: $f" >&2
done
