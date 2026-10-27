# my.itmo.ru — MCP для ИИ

Два MCP-сервера над **собственным API портала** (то, что дёргает фронтенд my.itmo.ru), без браузера:

| Сервер | Файл | Что умеет |
|---|---|---|
| `my-itmo` | `mcp-server/index.js` | **Только чтение.** Мутирующие инструменты не регистрируются вообще. |
| `my-itmo-write` | `mcp-server/write.js` | Всё то же + запись. Любая запись — **dry-run**, пока не передан `confirm: true`. |

Подключено в `.cursor/mcp.json` (Cursor) и `.mcp.json` (Claude Code). Включай `my-itmo-write` только когда реально нужна запись.

## Быстрый старт

```bash
cp .env.example .env          # MY_ITMO_EMAIL, MY_ITMO_PASSWORD (ITMO ID)
cd integrations/my-itmo/mcp-server && npm install
npm test                      # 11 тестов (часть ходит в сеть и логинится)
```

Логиниться руками не нужно: сервер сам проходит ITMO ID, кэширует токены и обновляет их.

## Как это устроено

```
.env ─► src/auth.js ─► id.itmo.ru (Keycloak, Authorization Code + PKCE, client student-personal-cabinet)
                         │  access_token 30 мин, refresh_token 30 дней
                         ▼  .session/tokens.json (0600, в .gitignore)
        src/client.js ─► https://my.itmo.ru/api/…  (Bearer, только same-origin /api/)
        src/tools/read.js    — инструменты чтения
        src/tools/write.js   — инструменты записи (только write.js-сервер)
        src/public-schedule.js ─► itmo.ru/ru/schedule (публичное расписание, HTML)
        data/{sitemap,api-catalog}.json ◄─ scripts/crawl-sitemap.mjs (из фронтенд-бандла)
```

Почему не браузер (как было раньше): вход по HTTP занимает ~2 с вместо запуска Chromium, нет хрупких `@ref` из снапшотов, ответы — структурированный JSON. Старые bash-скрипты (`scripts/*.sh`, agent-browser) остались как запасной путь для страниц без API.

## Карта сайта

[references/sitemap.md](references/sitemap.md) — сайты, 67 SPA-маршрутов, меню учётки, ~750 API-эндпоинтов по модулям со статусом живой проверки. Машинный вид: `mcp-server/data/*.json`, поиск из MCP: `itmo_sitemap`, `itmo_api_catalog`.

Обновить после изменений на сайте:

```bash
cd integrations/my-itmo/mcp-server && npm run crawl:probe
```

Краулер качает публичный JS-бандл, достаёт маршруты и вызовы `$axios`, а с `--probe` под вашей учёткой выполняет **только GET** без параметров и пишет статус и форму ответа (не значения).

## Инструменты

Чтение (оба сервера): `itmo_whoami`, `itmo_sitemap`, `itmo_api_catalog`, `itmo_schedule`, `itmo_record_book`, `itmo_requests`, `itmo_request_details`, `itmo_request_form`, `itmo_request_dictionary`, `itmo_finances`, `itmo_student_info` (общежитие, спорт, практики, выборность, очереди, брони, соглашения, ИПО…), `itmo_sport_calendar`, `itmo_sport_schedule`, `itmo_people_search`, `itmo_api_get`, `itmo_public_schedule_search`, `itmo_public_schedule`.

Запись (только `my-itmo-write`, всё с `confirm`, по умолчанию `false`):

| Инструмент | Действие |
|---|---|
| `itmo_request_submit` | подать заявку: валидация по форме (обязательные поля, типы), предпросмотр, затем отправка |
| `itmo_request_cancel` | отозвать свою заявку |
| `itmo_booking_cancel` | отменить бронь помещения |
| `itmo_sport_unsubscribe` | выписаться с секции/занятия/соревнования/проекта |
| `itmo_api_write` | сырая запись по allowlist (заявки, очереди, брони, спорт, выбор, факультативы) |

## Модель безопасности

- Пароль только из `.env` / переменных `MY_ITMO_*`; в вывод, логи и токен-кэш не попадает. Токены в ответах инструментов не возвращаются.
- Bearer-токен уходит только на `my.itmo.ru/api/*` (путь валидируется: без `..`, `//`, внешних хостов).
- Запись: dry-run по умолчанию; `confirm: true` — только после явного согласия пользователя на показанное действие.
- **Жёстко запрещено** даже с `confirm`: платежи (`/pay`), подписание соглашений (`agreements/*/sign`), заселение в общежитие (`dormitory/settlement`), согласования/отклонения, все служебные модули (`constructor`, `gia`, `employments`, `vacation`, админка `requests/v2`). Это юридически значимые или денежные действия — их делает человек.
- Не используется имперсонация («войти как другой пользователь»), которая есть во фронтенде.
- Аудит: `.session/audit.log` (JSONL: время, инструмент, метод, путь, ключи тела, dry-run/статус; значений нет).
- После неверного входа повторные попытки паузятся на 10 минут, чтобы не заблокировать учётку (brute-force protection Keycloak).

## Ограничения

- 2FA, капча и экраны смены пароля в ITMO ID не автоматизируются — тогда войдите в браузере и проверьте пароль.
- Форма заявок: условная видимость полей (`/api/requests/form_update`) не вычисляется; сервер всё равно валидирует и вернёт `error_list`.
- Группы/аудитории в публичном расписании itmo.ru проверены хуже, чем поиск по преподавателю; запрос с пробелом сайт режет WAF-ом, поэтому ищется первое слово, остальные фильтруют локально.
- Эндпоинты с ответом 403 (выборность, ИПО, факультативы) закрыты для учётки вне окна выбора/по роли.
