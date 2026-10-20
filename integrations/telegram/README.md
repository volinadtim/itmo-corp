# Telegram ИТМО

Чаты ИТМО синхронизирует коннектор Telegram на сервере atlas (`connectors/telegram` в репо atlas) в записи `comms.chat` / `comms.message` с пространством `itmo`. Отсюда они только читаются.

## Доступ

- Клиент atlas `itmo-corp` (id `d420fc80-ddf1-46e0-b94d-7f229027455b`), scope `comms:read space=itmo`: только чтение, только `itmo`.
- Ключ: `~/.config/atlas/itmo-corp.env` (права 600, вне репо). Кейчейна в WSL нет, поэтому файл.
- Новый ключ (ротация), с ключом устройства из `~/.config/atlas/env`:
  `atlas clients key d420fc80-ddf1-46e0-b94d-7f229027455b --json` → `ATLAS_KEY=` в файле.
- Какие чаты попадают в `itmo`, выбирается на сервере: `/telegram/` в atlas.

## Команды

```
integrations/telegram/tg chats
integrations/telegram/tg search "моделирование" [--since 2026-09-01] [--limit 200]
integrations/telegram/tg chat "Моделирование" [--since ...] [--limit 200]
integrations/telegram/tg get <id>
```

Файлы из сообщений лежат на сервере atlas; здесь видно только их тип и имя.

Агент подключает это только через skill `/telegram` (`.claude/skills/telegram`), а не MCP-сервером: MCP из `.mcp.json` стартует в каждой сессии.
