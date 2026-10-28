# itmo-corp: agent notes

Workspace for studying at ITMO. See README.md for the layout.

## atlas

This folder is a registered atlas client `itmo-corp` bound to the space `itmo` (atlas ADR 0002). `.env` (gitignored) holds `ATLAS_SPACE=itmo` and `ATLAS_KEY=keychain:itmo-corp`, a reference: the key itself is in the macOS Keychain, never in a file. The `atlas` CLI picks them up from here:

- `atlas me`: what this workspace may do.
- `atlas find "пересдача"`: search ITMO chats, plans and documents (space `itmo` by default; filter with `--product comms|planner|docs|ledger`, `--since 2026-10-01`).
- `atlas find --product ledger`: tuition and other payments tagged `itmo`.
- `atlas put events.jsonl`: write records, one JSON per line, e.g. `{"kind":"planner.event","source":"itmo-corp","external_id":"exam-os","occurred_at":"2026-10-16T09:00:00Z","spaces":["itmo"],"data":{"title":"Пересдача ОС"}}`. Reuse `external_id` to update.

ITMO chats arrive from the Telegram connector (Telegram chats allowed into the space `itmo`). Data that only this workspace can fetch (my.itmo, LMS) is pushed into atlas with `source: "itmo-corp"`. Scopes are changed in atlas (`atlas clients scopes …` with the owner key), not here.
