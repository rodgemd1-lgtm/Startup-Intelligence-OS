# Session Handoff

**Date**: 2026-03-28
**Branch**: main
**Session Goal**: Full system health check + M5 Max migration recovery

---

## Completed

- [x] **System health check** — diagnosed all post-Migration Assistant gaps
- [x] **~/.zshrc created** — Homebrew PATH, gcloud, NVM, OpenClaw completion
- [x] **Susan venv rebuilt** — Python 3.14, all deps from pyproject.toml installed
- [x] **Jake Brain verified** — 149,526 memories, Supabase connected and healthy
- [x] **Vault rebuilt** — ~/.hermes/.env with 30 API keys (was completely missing)
  - Symlinked to susan-team-architect/backend/.env
- [x] **~/.openclaw/.env created** — subset of vault for OpenClaw services
- [x] **OpenClaw configured and running** — gateway on port 18789, LaunchAgent installed
  - Fixed config: removed legacy `agent.*` keys, added `gateway.mode=local`
- [x] **Telegram verified** — BirchRodgers bot live, chat ID 8634072195
- [x] **Google OAuth completed** — Calendar + Gmail tokens saved to ~/.jake-vault/
- [x] **gcloud CLI installed + authenticated** — rodgemd1@gmail.com
- [x] **gh CLI authenticated** — rodgemd1-lgtm
- [x] **SSH key generated** — ~/.ssh/id_ed25519 (still needs adding to GitHub)
- [x] **jq installed** — was missing from Homebrew
- [x] **Go + Fabric installed** — Go 1.26.1, fabric built from danielmiessler/fabric
- [x] **Stripe MCP wired** — sk_live key in ~/.claude.json
- [x] **Resend MCP wired** — re_* key in ~/.claude.json
- [x] **LaunchAgents installed** — 6 agents running:
  - ai.openclaw.gateway (running, pid ~51932)
  - com.jake.autonomous-worker (running)
  - com.jake.claude-remote (running)
  - com.jake.health-monitor (loaded)
  - com.jake.morning-briefing (loaded, fires 7 AM)
  - com.jake.claude-brain (loaded)
- [x] **Ollama running** — qwen2.5-coder:32b pulled (19GB, M5 Max target model)

---

## In Progress

- [ ] **Fabric LaunchAgent** — com.jake.fabric-api.plist was templated for `michaelrodgers` path, fabric binary now at ~/go/bin/fabric — plist needs updating and loading
- [ ] **SSH key → GitHub** — generated but gh couldn't add it (needs `admin:public_key` scope re-auth that didn't complete)

---

## Blocked

- **Google Calendar showing 0 events today** — OAuth works (no error), but calendar may be empty or using wrong calendar ID. `GOOGLE_CALENDAR_ID=rodgemd1@gmail.com` is set. Test with `bin/gcal-reauth.py` in a new session.
- **Cloudflare Tunnel** (`ai.jakestudio.tunnel`) — not yet reconfigured. Tunnel daemon not running. Needs `cloudflared` install + tunnel re-auth.

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| ~/.hermes/.env as single vault source | Migration Assistant doesn't transfer dotfiles — keeping one canonical location |
| Symlink backend/.env → ~/.hermes/.env | All Susan code reads from backend/.env; hermes is the truth |
| qwen2.5-coder:32b for Ollama | M5 Max has RAM for 32b; HANDOFF from M4 Pro said to upgrade from 14b |
| gateway.mode=local | Required by OpenClaw 2026.3.24 — was missing, caused gateway to refuse to start |

---

## API Keys Set (30 total in ~/.hermes/.env)

Anthropic, OpenAI, OpenRouter, Groq, Voyage, Supabase (URL + service + anon), Firecrawl, Exa, Brave, Jina, Apify, Resend, Telegram (token + chat ID), Notion, SuperMemory, GitHub PAT, Stripe (live), Google OAuth (client ID + secret + refresh token + calendar ID), Tavily, Gemini, Gateway flag

---

## Next Steps

1. **Add SSH key to GitHub manually** — go to github.com/settings/ssh/new, paste:
   `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJP53emQ6v5xEccYMnFB4k3AjKHQ1RgCVPl0dxLeaQ5E mikerodgers@mac`
2. **Fix fabric LaunchAgent** — update com.jake.fabric-api.plist HOME path to `/Users/mikerodgers` and binary path to `~/go/bin/fabric`, install to ~/Library/LaunchAgents/
3. **Cloudflare Tunnel** — `brew install cloudflared`, then `cloudflared tunnel login` and reconfigure ai.jakestudio.tunnel
4. **Wire Firehose SSE** into birch/sources/firehose.py (from previous session's handoff)
5. **Cancel paid services** — CrewAI ($85.50), Neural Frames ($99), LangSmith ($39), Aimtell ($49)
6. **Verify OpenClaw Telegram pairing** — open Telegram, message the bot to confirm Jake responds

---

## Key File Locations

| File | Path |
|------|------|
| Primary vault | ~/.hermes/.env |
| OpenClaw config | ~/.openclaw/openclaw.json |
| OpenClaw env | ~/.openclaw/.env |
| Google tokens | ~/.jake-vault/google_oauth_tokens.json |
| Susan venv | ~/Desktop/Startup-Intelligence-OS/susan-team-architect/backend/.venv |
| LaunchAgents | ~/Library/LaunchAgents/ai.openclaw.gateway.plist + com.jake.*.plist |
| Shell config | ~/.zshrc |
| Go binaries | ~/go/bin/ (fabric, etc.) |
