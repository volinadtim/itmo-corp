---
name: my-itmo
description: Access my.itmo.ru (ITMO personal cabinet) via browser automation. Use when the user asks to login to my.itmo.ru, check applications (заявки), submit restoration request, order documents, read notifications, or interact with ITMO ID portal. Credentials live in project .env file.
---

# my.itmo.ru — личный кабинет ИТМО

<objective>
Automate read/write interaction with my.itmo.ru using agent-browser and credentials from `.env`. Never ask the user for password in chat — read from `.env` only.
</objective>

## Prerequisites

1. `.env` exists at project root with `MY_ITMO_EMAIL` and `MY_ITMO_PASSWORD`
2. `npx agent-browser` available (installed on first use)
3. Read [integrations/my-itmo/references/applications.md](../../integrations/my-itmo/references/applications.md) for application names

## Security rules

- **NEVER** print, log, or commit passwords
- **NEVER** add `.env` to git
- Use session name `my-itmo` consistently
- Restrict navigation to `*.itmo.ru` domains

## Standard workflow

```
1. bash integrations/my-itmo/scripts/login.sh     # or ensure_logged_in via lib.sh
2. npx agent-browser --session my-itmo snapshot -i
3. Interact using @refs from snapshot
4. Re-snapshot after every navigation/click
```

## Scripts (preferred entry points)

| Script | Purpose |
|---|---|
| `integrations/my-itmo/scripts/login.sh` | Login + save session |
| `integrations/my-itmo/scripts/status.sh` | Check if logged in |
| `integrations/my-itmo/scripts/open-applications.sh` | Go to applications section |
| `integrations/my-itmo/scripts/snapshot.sh [url]` | Snapshot page |

## Common tasks

### Check restoration application status

```bash
bash integrations/my-itmo/scripts/login.sh
bash integrations/my-itmo/scripts/open-applications.sh
# Then: find "Мои заявки" or "Переводы и восстановления" in snapshot
npx agent-browser --session my-itmo find text "Мои заявки" click
npx agent-browser --session my-itmo wait --load networkidle
npx agent-browser --session my-itmo snapshot -i
```

### Navigate by text (when refs unknown)

```bash
npx agent-browser --session my-itmo find text "Заявки и очереди" click
npx agent-browser --session my-itmo find text "Переводы и восстановления" click
```

### Debug login visually

```bash
AGENT_BROWSER_HEADED=1 bash integrations/my-itmo/scripts/login.sh
```

## MCP tools (preferred)

Servers `my-itmo` (read-only) and `my-itmo-write` (read + write) call the portal API directly with ITMO ID login handled automatically — no manual login, no browser. Full docs: [integrations/my-itmo/README.md](../../integrations/my-itmo/README.md); site map: [integrations/my-itmo/references/sitemap.md](../../integrations/my-itmo/references/sitemap.md).

Start with `itmo_whoami` / `itmo_sitemap`; find unknown endpoints with `itmo_api_catalog`. Main tools: `itmo_schedule`, `itmo_record_book`, `itmo_requests`, `itmo_request_form`, `itmo_finances`, `itmo_student_info`, `itmo_public_schedule(_search)` (teacher/group/room timetables from itmo.ru, no login).

Write tools (`itmo_request_submit`, `itmo_request_cancel`, `itmo_booking_cancel`, `itmo_sport_unsubscribe`, `itmo_api_write`) are dry-run unless `confirm: true`. Show the user the dry-run preview and set `confirm: true` only after they approve that exact action. Payments, e-signing, housing settlement and approvals are blocked by design.

Browser automation below is the fallback for pages that have no API.

## Key applications for restoration (ИСУ 368086)

1. **Персональная анкета** — update first
2. **Переводы и восстановления** → «Восстановление в число обучающихся после отчисления»
3. **Заказ комплекта документов после отчисления** — if needed

See `apply-itmo/plan-2026.md` for deadlines (3–20 August 2026).

## Troubleshooting

| Problem | Action |
|---|---|
| Login form refs changed | Run `snapshot -i`, update refs in lib.sh or use `find label` |
| 2FA / captcha | User must login manually with `--headed`, then `state save` |
| Session expired | Re-run `login.sh` |
| `.env` missing | Tell user to `cp .env.example .env` |
