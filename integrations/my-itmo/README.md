# my.itmo.ru — интеграция для ИИ

Доступ к личному кабинету ИТМО через **agent-browser** + credentials из `.env`.

## Быстрый старт

```bash
# 1. Создай .env с логином и паролем
cp .env.example .env
# заполни MY_ITMO_EMAIL и MY_ITMO_PASSWORD

# 2. Логин (сохранит сессию)
bash integrations/my-itmo/scripts/login.sh

# 3. Проверка
bash integrations/my-itmo/scripts/status.sh

# 4. Открыть заявки
bash integrations/my-itmo/scripts/open-applications.sh
```

## Архитектура

```
.env                          ← credentials (gitignored)
agent-browser.json            ← domain allowlist
integrations/my-itmo/
├── scripts/                  ← shell-обёртки (login, snapshot, apps)
├── mcp-server/               ← MCP для Cursor (опционально)
├── references/applications.md
└── .session/                 ← сохранённая сессия (gitignored)
.cursor/skills/my-itmo/       ← skill для агента
```

## MCP (Cursor)

После установки:

```bash
cd integrations/my-itmo/mcp-server && npm install
```

В `.cursor/mcp.json` уже настроен сервер `my-itmo`. Перезапусти Cursor / reload MCP.

**Tools:**
- `my_itmo_login` — войти в my.itmo.ru
- `my_itmo_status` — проверить сессию
- `my_itmo_snapshot` — снимок текущей страницы (a11y tree)
- `my_itmo_open` — открыть URL в авторизованной сессии

## Безопасность

- `.env` **никогда** не коммитится
- Пароль не попадает в логи скриптов (передаётся только в fill)
- `allowedDomains` ограничивает навигацию `*.itmo.ru`
- Для отладки: `AGENT_BROWSER_HEADED=1 bash integrations/my-itmo/scripts/login.sh`

## Логин

Аутентификация через **ITMO ID (Keycloak)** на `id.itmo.ru` → redirect на `my.itmo.ru`.

Используй **email** и пароль от ITMO ID (тот же, что для my.itmo.ru).
