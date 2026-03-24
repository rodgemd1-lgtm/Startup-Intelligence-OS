# HANDOFF — Session 4: Fabric Deterministic Dispatch (WIP)

**Date:** 2026-03-24
**Branch:** `claude/jolly-lehmann`
**Commits:** 04adc10 (this session), 6e6cdcf (previous)

## What We Did

### Fabric CLI Setup (COMPLETE)
- Ran `fabric --setup` — 251 patterns downloaded, Anthropic/claude-opus-4-6 default, 1M context
- Fabric works perfectly from terminal: `echo "text" | fabric --pattern summarize`

### Telegram Testing (PARTIAL)
- **Test 1 PASS**: TELOS grounding — Jake knows goals, PAI score 34->50, morning briefs
- **Test 2 PASS**: Identity — Army vet, James, Jacob, Alex, all companies
- **Test 3 FAIL**: Fabric via Telegram — GPT-5.4 paraphrases instead of calling Bash tool

### Fabric Dispatch Deep Dive
Reverse-engineered OpenClaw's skill dispatch system.

**Key discoveries:**
1. SKILL.md supports `command-dispatch: tool` + `command-tool: exec` frontmatter keys
2. This creates DETERMINISTIC dispatch — bypasses LLM entirely, sends raw args to exec tool
3. The dispatch IS firing (confirmed in session logs)
4. **BLOCKER**: exec tool can't find `summarize` because `~/go/bin` not in exec sandbox PATH

**Architecture (works locally, not through dispatch):**
```
User: /fabric summarize text
  -> OpenClaw dispatch (deterministic, bypasses LLM) OK
  -> exec tool: command = "summarize text" OK
  -> Shell finds "summarize" in PATH -> fabric-dispatch -> fabric-cmd -> fabric binary FAILS (PATH)
```

### Files Created/Modified

**In repo (pai/skills/fabric-router/):**
- `SKILL.md` — command-dispatch: tool, command-tool: exec, command-arg-mode: raw
- `fabric-run.sh` — Wrapper with alias resolution and env isolation

**On filesystem (NOT in repo):**
- `~/go/bin/fabric-cmd` — Main wrapper (copy of fabric-run.sh)
- `~/go/bin/fabric-dispatch` — Symlink router (reads $0 basename as pattern)
- `~/go/bin/{summarize,extract_wisdom,w,s,a,...}` — Symlinks to fabric-dispatch
- `~/.openclaw/workspace-jake/bin/` — Duplicate symlinks (attempted)
- `~/.openclaw/openclaw.json` — Added `tools.exec.pathPrepend` config

## What's Blocking

### exec tool PATH doesn't include ~/go/bin

```javascript
// From pi-embedded-CbCYZxIb.js
const DEFAULT_PATH = process.env.PATH ?? "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin";
```

OpenClaw.app launched from Finder gets launchd PATH, not shell PATH.

**Solutions to try next session (in priority order):**
1. `sudo ln -sf ~/go/bin/fabric-dispatch /usr/local/bin/summarize` (and other patterns) — just needs password
2. `launchctl setenv PATH "$PATH"` then relaunch OpenClaw.app — injects shell PATH into launchd
3. Launch OpenClaw from terminal (`openclaw`) instead of Finder — inherits shell PATH
4. Verify `tools.exec.pathPrepend` — already added to config, may need CLI restart not app restart
5. Use absolute paths in dispatch — would need OpenClaw code change or different approach

## Key Reference

**Dispatch code:** `~/.openclaw/extensions/lossless-claw/node_modules/openclaw/dist/pi-embedded-CbCYZxIb.js` ~line 91314

**Frontmatter keys (from skills-M0AZJeXx.js):**
- `command-dispatch` / `command_dispatch` -> "tool"
- `command-tool` / `command_tool` -> "exec"
- `command-arg-mode` / `command_arg_mode` -> "raw"

**Session cache:** Delete `skillsSnapshot` from `~/.openclaw/agents/main/sessions/sessions.json` to force skill reload

## PAI Stack Status

```
Telegram (@JakeStudio2011bot) -> OpenClaw (port 18789)
  |- GPT-5.4 (default, fast)                          OK
  |- o3-pro (/model think)                             OK
  |- LosslessClaw (persistence)                        OK
  |- TELOS identity (USER.md, SOUL.md, GOALS.md)       OK
  |- Fabric (251 patterns, Opus 4.6)     terminal OK / Telegram BLOCKED (PATH)
  |- Susan bridge skill (loaded)                       PENDING (needs control plane)
  '- Claude Code (execution)                           OK
```

## Next Steps

1. Fix Fabric dispatch PATH (this session's blocker)
2. Complete Telegram test suite (Tests 4-7)
3. TELOS identity layer (Phase 2)
4. Susan integration (Phase 3)
