# Hermes Action Engine — DEPRECATED

**Status**: Archived 2026-03-24
**Replaced by**: OpenClaw gateway + PAI (Personal AI Infrastructure)

## What This Was
Phase 5 "THE HANDS" — action execution engine for Jake Brain.
6 registered actions with 3-tier safety model (auto/confirm/approve).

## Actions Archived
| Action | Tier | Replacement |
|--------|------|-------------|
| send_telegram | 1 (auto) | OpenClaw Telegram channel (native) |
| set_reminder | 1 (auto) | OpenClaw + Apple Reminders via osascript |
| update_notion | 2 (confirm) | OpenClaw skills / MCP tools |
| send_email | 2 (confirm) | OpenClaw skills / Resend |
| create_event | 2 (confirm) | OpenClaw skills / Google Calendar |
| create_github_issue | 2 (confirm) | OpenClaw skills / gh CLI |

## Why Decommissioned
- OpenClaw provides native Telegram integration (no custom bot polling)
- OpenClaw's tool/skill system replaces the custom action registry
- LosslessClaw handles conversation persistence (replaces jake_episodic logging)
- PAI security model (4-layer) supersedes the 3-tier safety model

## Credentials Migration
Credentials that were in `~/.hermes/.env` should migrate to `~/.openclaw/.env`:
- TELEGRAM_BOT_TOKEN → already in openclaw.json
- NOTION_API_TOKEN → pending migration
- RESEND_API_KEY → pending migration
- GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN → pending migration
- GITHUB_PERSONAL_ACCESS_TOKEN → pending migration

## Session History
Hermes session data at `~/.hermes/sessions/` is retained for brain ingest.
Run `brain_hermes_ingest.py` one final time before removing `~/.hermes/`.

## Files Archived Here
- `actions/` — 8 files, ~900 LOC (base classes + 6 action implementations + audit)
- `scripts/jake_hands_cli.py` — CLI runner (~255 LOC)
- `scripts/brain_hermes_ingest.py` — Session ingestion (~360 LOC)
