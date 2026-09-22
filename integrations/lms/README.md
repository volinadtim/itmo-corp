# ITMO LMS — выкачивание материалов

`lms.itmo.ru` закрыт логином (ITMO ID / Keycloak). Скрипт ходит по уже существующей
сессии, свой логин не выполняет.

## Как отдать сессию

1. Залогинься в `lms.itmo.ru` в любом браузере.
2. DevTools → Application/Storage → Cookies → `https://lms.itmo.ru` → скопируй значение
   **`MoodleSession`**.
3. Положи его в файл вне репозитория:

```bash
mkdir -p ~/.config/itmo-lms && chmod 700 ~/.config/itmo-lms
printf '%s' 'ВСТАВЬ_ЗНАЧЕНИЕ' > ~/.config/itmo-lms/session && chmod 600 ~/.config/itmo-lms/session
```

## Использование

```bash
bash integrations/lms/fetch.sh study/modeling/materials/lms 6916 38373 7289
```

Аргументы — id ресурсов из ссылок вида `lms.itmo.ru/mod/resource/view.php?id=<id>`.
Карта id по курсу «Моделирование» — в [study/modeling/materials/links.md](../../study/modeling/materials/links.md).

Скрипт сначала проверяет сессию на `/my/`; при HTTP ≠ 200 выходит с кодом 2 — значит куку
надо обновить. Если вместо файла прилетела страница логина, скрипт это отдельно напишет.

## Безопасность

- `MoodleSession` равносильна паролю: даёт полный доступ к аккаунту, включая тесты и оценки.
- Хранится только в `~/.config/itmo-lms/session` (0600), **не в репозитории**.
- Живёт до логаута/протухания сессии. После работы можно просто выйти из LMS в браузере —
  кука станет бесполезной.
