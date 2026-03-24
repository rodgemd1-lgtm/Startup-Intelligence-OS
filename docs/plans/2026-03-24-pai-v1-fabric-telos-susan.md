# PAI v1.0 — Fabric + TELOS + Susan Integration

**Date**: 2026-03-24
**Status**: DRAFT — awaiting approval
**Branch**: claude/jolly-lehmann

## Summary

Wire three capabilities into the PAI stack:
1. **Fabric patterns** accessible from Telegram via OpenClaw skills
2. **TELOS identity layer** injected into OpenClaw workspace for grounded responses
3. **Susan's 73-agent roster** invocable from Telegram via control plane API

## Current State

| Component | Status | Location |
|-----------|--------|----------|
| OpenClaw gateway | Running on :18789 | `~/.openclaw/openclaw.json` |
| Telegram bot | Live (@JakeStudio2011bot) | OpenClaw telegram plugin |
| Fabric | 251 patterns, Opus 4.6 default | `~/.config/fabric/` |
| TELOS | 18-file v1 exists | `pai/TELOS/` |
| Susan control plane | FastAPI on :8042 | `susan-team-architect/backend/control_plane/` |
| Susan MCP | 16 tools, stdio | `susan-team-architect/backend/mcp_server/` |
| LosslessClaw | Active, 0.75 threshold | OpenClaw plugin |

## Phase 1: Fabric → OpenClaw Skills

**Goal**: Send `/fabric extract_wisdom <url>` in Telegram → get Fabric pattern output back.

### Approach: OpenClaw Skill Files

OpenClaw skills are Markdown + Python files in the workspace. We create a `fabric-router` skill that:
1. Parses the pattern name and input from the Telegram message
2. Shells out to `fabric` CLI with the pattern
3. Returns formatted output

### Tasks

1.1. Create `~/.openclaw/workspace-jake/skills/fabric-router.md` — skill definition with pattern list
1.2. Create `~/.openclaw/workspace-jake/skills/fabric-router.py` — Python handler that calls `fabric --pattern <name>` via subprocess
1.3. Create `pai/config/fabric-patterns-whitelist.yaml` — curated list of 20-30 most useful patterns with descriptions and model routing
1.4. Update `~/.openclaw/openclaw.json` — register the skill
1.5. Test from Telegram: `/fabric summarize`, `/fabric extract_wisdom <url>`, `/fabric analyze_claims <text>`
1.6. Add model routing — cheap patterns → GPT-5.4-mini, analysis → Sonnet, strategic → Opus (per `fabric-models.env`)

### Files Changed
- `~/.openclaw/workspace-jake/skills/fabric-router.md` (NEW)
- `~/.openclaw/workspace-jake/skills/fabric-router.py` (NEW)
- `pai/config/fabric-patterns-whitelist.yaml` (NEW)
- `~/.openclaw/openclaw.json` (EDIT — add skill reference)

## Phase 2: TELOS Identity Layer → OpenClaw

**Goal**: Jake's responses grounded in Mike's actual identity, goals, beliefs, and strategies.

### Approach: Inject TELOS into OpenClaw Workspace

OpenClaw reads workspace files (IDENTITY.md, SOUL.md, etc.) at session start. We:
1. Consolidate the 18 TELOS files into OpenClaw's identity system
2. Update IDENTITY.md to reference TELOS sections
3. Create a TELOS sync script that keeps OpenClaw workspace current

### Tasks

2.1. Read current `pai/TELOS/` files — audit content, identify what's populated vs template
2.2. Update `~/.openclaw/workspace-jake/IDENTITY.md` — add TELOS sections (mission, goals, beliefs, strategies)
2.3. Update `~/.openclaw/workspace-jake/USER.md` — populate with TELOS personal data (narratives, challenges, predictions)
2.4. Create `pai/scripts/sync-telos-to-openclaw.sh` — script that copies TELOS updates into workspace files
2.5. Add TELOS context to the fabric-router skill — patterns like `extract_wisdom` get grounded in Mike's goals
2.6. Test: Send message in Telegram, verify Jake references actual goals/beliefs in responses

### Files Changed
- `~/.openclaw/workspace-jake/IDENTITY.md` (EDIT)
- `~/.openclaw/workspace-jake/USER.md` (EDIT)
- `pai/scripts/sync-telos-to-openclaw.sh` (NEW)

## Phase 3: Susan → OpenClaw/Telegram

**Goal**: Send `/susan route transformfit "Build coaching AI"` in Telegram → get agent recommendations + optional execution.

### Approach: OpenClaw Skill → Susan Control Plane API

Susan's control plane runs on :8042 with REST endpoints. We create a skill that:
1. Parses Susan commands from Telegram
2. Calls the control plane API (HTTP, not subprocess — cleaner)
3. Formats agent recommendations for Telegram

### Tasks

3.1. Create `~/.openclaw/workspace-jake/skills/susan-bridge.md` — skill definition with command reference
3.2. Create `~/.openclaw/workspace-jake/skills/susan-bridge.py` — Python handler that calls Susan API endpoints
3.3. Implement commands:
  - `/susan route <company> <task>` → `POST /api/susan/route`
  - `/susan status <company>` → `GET /api/susan/status/{company_id}`
  - `/susan search <query>` → `GET /api/knowledge/search`
  - `/susan team <company>` → team manifest
  - `/susan run <company> <agent> <prompt>` → execute specific agent
3.4. Add Telegram formatting — agent cards with role, model, and confidence score
3.5. Add cost guard — warn before executing agents that cost >$0.10
3.6. Test from Telegram: route a task, search knowledge, get status
3.7. Update `~/.openclaw/openclaw.json` — register susan-bridge skill

### Files Changed
- `~/.openclaw/workspace-jake/skills/susan-bridge.md` (NEW)
- `~/.openclaw/workspace-jake/skills/susan-bridge.py` (NEW)
- `~/.openclaw/openclaw.json` (EDIT — add skill reference)

## Verification Plan

| Test | Command | Expected |
|------|---------|----------|
| Fabric basic | `/fabric summarize` + paste text | Summarized output |
| Fabric URL | `/fabric extract_wisdom https://...` | Wisdom bullets |
| Fabric model routing | `/fabric analyze_claims` (should use Sonnet) | Correct model used |
| TELOS grounding | "What are my goals?" | Jake cites actual TELOS goals |
| TELOS in fabric | `/fabric extract_wisdom` on article | Output filtered through Mike's lens |
| Susan route | `/susan route transformfit "Build AI coach"` | 3-6 ranked agents |
| Susan search | `/susan search "retention optimization"` | RAG results |
| Susan status | `/susan status transformfit` | Company corpus stats |
| Susan execute | `/susan run transformfit coach "Design workout periodization"` | Agent response + cost |

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| OpenClaw skill format undocumented | Reference TechNickAI/openclaw-config for patterns |
| Susan control plane not running | Health check in susan-bridge.py, fallback to CLI |
| Fabric CLI slow on large inputs | Timeout + truncation in router |
| TELOS files contain sensitive data | Stay local, never push to public repos |
| Context budget | 3 phases, clean boundaries, checkpoint between |

## Session Plan

- **This session**: Phase 1 (Fabric skills) — research OpenClaw skill format, build, test
- **Next session**: Phase 2 (TELOS injection) + Phase 3 (Susan bridge)
- Checkpoint and handoff between phases
