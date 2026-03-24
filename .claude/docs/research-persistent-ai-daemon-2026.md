# Research: Persistent AI Assistant Daemon with Full Computer Access

**Date**: 2026-03-24
**Researcher**: Jake
**Confidence**: DRAFT — deep research complete, implementation decisions remain
**Context Health**: GREEN

---

## Executive Summary

There are now **5 viable approaches** to running a persistent AI assistant daemon with full computer access on a Mac, each with different trade-offs. The landscape changed dramatically in March 2026 with three key developments:

1. **Claude Code Channels** (v2.1.80, March 20 2026) — Anthropic's first-party Telegram/Discord bridge
2. **OpenClaw ACP** — persistent Claude Code sessions routed through OpenClaw's messaging gateway
3. **Perplexity Personal Computer** — purpose-built always-on AI agent for Mac mini

The bottom line: **Claude Code Channels + launchd + WISC memory stack** is the most direct path for Jake, but OpenClaw gives you multi-agent orchestration and battle-tested messaging infrastructure that Channels doesn't have yet.

---

## 1. Claude Code as a Daemon

### Can Claude Code Run as a Persistent Background Process?

**Yes, but it requires wrapping.** Claude Code is a foreground CLI process. Close the terminal, lose the session. There is no built-in `--daemon` flag. However, it CAN be kept alive through:

| Method | How | Pros | Cons |
|--------|-----|------|------|
| **tmux** | `tmux new-session -d -s claude "claude --channels plugin:telegram@claude-plugins-official"` | Simple, immediate | Dies on reboot unless scripted |
| **launchd** | plist in `~/Library/LaunchAgents/` with `KeepAlive` + `RunAtLoad` | Native macOS, auto-restart on crash, starts on boot | Harder to debug, no TTY |
| **pm2** | `pm2 start "claude --channels ..." --name jake` | Cross-platform, log management, `pm2 startup` for boot | Requires Node.js, extra dependency |
| **Clautel** | `npm install -g clautel && clautel start && clautel install-service` | Purpose-built for this, per-project Telegram bots | Third-party dependency |
| **Docker** | Containerized Claude Code with volume mounts | Isolation, reproducibility | Overhead, macOS Docker perf issues |

### How Sessions Work

- **Interactive sessions**: Ephemeral by default. Context lives in memory during the session.
- **`-p` (headless) mode**: One-shot by default, but supports `--continue` and `--resume <session_id>` for multi-turn.
- **Agent SDK** (Python/TypeScript): Full programmatic control. Sessions auto-persist to disk. Can be resumed by session ID.
- **Channels mode**: Session stays alive as long as the process runs. Messages from Telegram/Discord arrive in the same active session.

### Session Resumption (Critical for Daemon)

```bash
# Capture session ID from first run
session_id=$(claude -p "Start monitoring" --output-format json | jq -r '.session_id')

# Resume later
claude -p "Continue the monitoring task" --resume "$session_id"
```

The Agent SDK writes sessions to disk automatically. The bidirectional stream-json protocol enables persistent multi-turn conversations from external processes.

### Claude Code Scheduled Tasks (/loop)

Claude Code now supports cron-style scheduling within a session:
- Up to 50 concurrent scheduled tasks per session
- Intervals: minutes, hours, or days
- Only runs while a session is active (not a standalone scheduler)
- Useful for: periodic test runs, file monitoring, health checks

---

## 2. OpenClaw ACP (Agent Client Protocol) Bridge

### Architecture

ACP is a **JSON-RPC 2.0 protocol over stdio** with official SDKs in TypeScript, Rust, Python, and Kotlin. Think of it as "LSP but for AI agents" — a shared contract so any agent runtime can work with any messaging platform.

```
Telegram/Discord -> OpenClaw Gateway (WebSocket) -> ACP Bridge -> Claude Code CLI
                                                               -> Codex CLI
                                                               -> Gemini CLI
                                                               -> Any ACP-compatible agent
```

### Session Types

| Type | Flag | Behavior |
|------|------|----------|
| **Persistent** | `mode: "persistent"` | Maintains context across messages. Thread-bound. |
| **One-shot** | `mode: "run"` | Single task, complete, done. |
| **Resumed** | `resumeSessionId: "<id>"` | Full history replay from previous session. |

### Thread Binding (Key Feature)

ACP sessions can bind to specific messaging threads:
- **Discord threads** and **Telegram forum topics** supported
- Messages in the bound thread auto-route to the session
- Output returns to the same thread
- Binding persists until unfocused, closed, or expired

### Configuration

```json5
{
  "acp": {
    "enabled": true,
    "backend": "acpx",
    "defaultAgent": "claude",
    "allowedAgents": ["claude", "codex", "gemini"],
    "maxConcurrentSessions": 8
  }
}
```

### Commands

```bash
# Install
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true

# Spawn persistent Claude Code session
/acp spawn claude --mode persistent --thread auto

# Resume previous session
/acp spawn claude --resumeSessionId "<previous-session-id>"

# Control
/acp status          # Check session state
/acp steer "focus on tests"  # Guide without replacing context
/acp close           # Terminate session
/acp doctor          # Health check
```

### Permission Handling

ACP sessions run non-interactively (no TTY). Configure:
- `permissionMode: "approve-all"` — auto-approve writes and commands
- `permissionMode: "approve-reads"` — only auto-approve reads
- `nonInteractivePermissions: "fail"` — abort on permission prompts (default)

### Key Limitation

**ACP sessions run on the host runtime, NOT inside OpenClaw's sandbox.** This means full computer access but no sandboxing. For Jake, this is actually a feature — we want full access.

---

## 3. The openclaw-claude-code-skill (Enderfga)

### What It Is

An MCP skill that gives OpenClaw agents **programmatic access to Claude Code** — persistent sessions, effort control, context management, model switching, and agent teams.

**Repo**: https://github.com/Enderfga/openclaw-claude-code-skill

### Architecture

```
OpenClaw Agent -> MCP Protocol -> Claude Code Skill -> Claude Code Backend (localhost:18795)
                                                     |
                                              Persistent Session Storage
                                              (conversation history, cost tracking, context)
```

### Session Lifecycle

```
session-start (create with project dir)
  -> session-send (multiple messages, maintains context)
  -> session-pause / session-resume
  -> session-fork (branch with new model/effort)
  -> session-compact (reclaim context window)
  -> session-stop
```

### Key Capabilities

- **Persistent sessions**: Survive CLI disconnections, resumable by ID
- **Effort control**: low/medium/high/max maps to Claude Code thinking depth
- **Agent teams**: Multiple specialized agents in one session (@architect, @developer, @reviewer)
- **Streaming**: SSE or NDJSON for real-time output
- **Cost tracking**: Per-session token/cost breakdown
- **Webhook hooks**: onToolError, onContextHigh, onStop, onTurnComplete
- **Permission modes**: acceptEdits, plan, bypassPermissions

### Message Flow (When a Telegram Message Arrives)

1. User sends message to Telegram -> OpenClaw Gateway
2. Gateway routes to agent with Claude Code skill
3. Skill calls session-send on existing persistent session (or creates new one)
4. Claude Code executes with full tool access (Bash, Read, Edit, Write, Glob, Grep)
5. Response streams back through OpenClaw -> Telegram

---

## 4. Claude Code Channels (v2.1.80)

### What It Is

Anthropic's **first-party** Telegram and Discord integration, shipped March 20, 2026 as a research preview. A channel is an MCP server that pushes events into a running Claude Code session.

### Architecture

```
Telegram Bot (polling) -> Channel Plugin (Bun) -> Claude Code Session (running)
                                                 |
                                          Your real files, terminal, tools
                                                 |
                                          Reply via channel -> Telegram
```

### Setup

```bash
# Install plugin
/plugin install telegram@claude-plugins-official

# Configure
/telegram:configure <BOT_FATHER_TOKEN>

# Launch with channels
claude --channels plugin:telegram@claude-plugins-official

# Pair your account
/telegram:access pair <code>
/telegram:access policy allowlist
```

### Persistence Model

**Events only arrive while the session is open.** This is the critical limitation.

| Scenario | Behavior |
|----------|----------|
| Session running | Messages arrive in real-time, Claude responds |
| Terminal closed | Channel goes offline. Telegram messages LOST. |
| Discord (offline) | Messages queued via fetch_messages on reconnect |
| Permission prompt hit | Session PAUSES until resolved |
| --dangerously-skip-permissions | Bypasses prompts (full auto mode) |

### For Always-On Operation

You MUST keep Claude Code running. Options:
1. **tmux**: `tmux new-session -d -s jake "claude --channels plugin:telegram@claude-plugins-official"`
2. **launchd**: plist with KeepAlive and RunAtLoad
3. **pm2**: `pm2 start "claude --channels ..." --name jake-channels`

### Permission Relay

Channel plugins can declare the **permission relay capability**, forwarding permission prompts to Telegram/Discord. This means you can approve file edits from your phone. Only allowlisted senders can approve.

### Security

- Sender allowlist per channel (only your Telegram ID can send messages)
- --channels flag must explicitly name the plugin each session
- Enterprise/Team orgs must enable channelsEnabled in managed settings

### Current Limitations (Research Preview)

- Only Anthropic-approved plugins (claude-plugins-official) allowed
- Custom channels require --dangerously-load-development-channels
- No persistent daemon mode — you must keep the process running
- Telegram messages lost when offline (Discord has reconnect queueing)
- --channels syntax may change

---

## 5. Computer Access Patterns

### Claude Code (Native)

Claude Code already has extensive computer access through its standard tools:
- **Bash**: Full terminal access (any command, any app)
- **Read/Edit/Write**: File system access
- **Glob/Grep**: File search
- **MCP servers**: Calendar, mail, browser, Notion, GitHub, etc.

### Claude Computer Use (macOS, March 2026)

Anthropic's newest capability — direct GUI control:
- **Accessibility permission**: Click, type, scroll on any app
- **Screen Recording permission**: See what's on screen
- **Priority order**: Connector > Bash > Claude in Chrome > Computer Use (broadest, slowest)
- Available in Claude Cowork and Claude Code as research preview

### MCP-Based Full Access Stack

| System | MCP Server | What It Does |
|--------|-----------|-------------|
| **Files** | Built-in Bash/Read/Edit | Full filesystem |
| **Terminal** | Built-in Bash | Any CLI command |
| **Browser** | Claude in Chrome, Playwright | Web automation |
| **Calendar** | Google Calendar MCP | Schedule management |
| **Mail** | Gmail MCP or Bash+AppleScript | Email |
| **Notes** | Notion MCP, Apple Notes via AppleScript | Note-taking |
| **Tasks** | Things 3 MCP, Todoist MCP | Task management |
| **Git** | GitHub MCP, built-in Bash | Code management |
| **Search** | Brave, Tavily, Exa MCPs | Web research |
| **Apps** | AppleScript via Bash, Computer Use | Any macOS app |

### Sam Zoloth's "Claude as OS" Pattern (Production-Tested, 1 Year)

One of the most mature implementations:
- **10 macOS LaunchAgents** as background processors
- **Browser automation** via Chrome DevTools Protocol (port 9222)
- **10 MCP servers**: Things 3, Google Calendar, Strava, Firefly III, Readwise, Roam, Agent Mail
- **Safety guards**: PreToolUse Python hook blocks dangerous commands (git reset --hard, rm -rf)
- **46 explicit permission patterns** for whitelisting safe operations
- **~/.claude/ directory is git-controlled** for configuration versioning
- Results after 1 year: 131 diaries, 28 extracted patterns, 20 active rules, 40+ CLI tools

---

## 6. Persistent Session with Memory (Jake's Identity Across Restarts)

### The Problem

Claude Code sessions are ephemeral. Every restart starts fresh. Jake's personality, memory, and context must survive:
1. Process restarts (crashes, reboots)
2. Context window compaction (200K token limit)
3. Session boundaries (new conversations)

### Solution Architecture: 4-Layer Memory Stack

```
Layer 1: ALWAYS LOADED (survives everything)
  CLAUDE.md — mission, routing, quick-start
  .claude/rules/jake*.md — personality, protocols, boot sequence
  .claude/rules/wisc-global.md — methodology
  ~/.claude/projects/<project>/memory/MEMORY.md — auto-memory

Layer 2: SESSION PERSISTENT (survives compaction)
  Agent SDK session files (auto-persisted to disk)
  --resume <session_id> to continue
  LosslessClaw DAG summaries (if using OpenClaw)

Layer 3: FILE-BACKED STATE (survives restarts)
  .startup-os/ — workspace contract, company/project state
  .claude/plans/ — in-progress plans, parking lot
  HANDOFF.md — structured session handoff
  ~/.claude/projects/<project>/memory/*.md — curated knowledge

Layer 4: RETRIEVABLE (survives everything, on-demand)
  Susan RAG (6,693+ chunks)
  Git history (git log)
  MCP-accessible knowledge bases
  Web search (Brave, Tavily, Exa)
```

### OpenClaw-Specific Memory (If Using OpenClaw)

OpenClaw auto-loads exactly 8 files at boot:
- SOUL.md — Jake's personality, values, communication style
- IDENTITY.md — Core identity layer
- AGENTS.md — Agent roster and capabilities
- USER.md — Mike's profile and preferences
- TOOLS.md — Available tools config
- HEARTBEAT.md — Scheduled tasks / cron
- BOOTSTRAP.md — Startup instructions
- MEMORY.md — Persistent memory (decisions, patterns)

### LosslessClaw (Context Preservation Plugin)

Replaces OpenClaw's sliding-window compaction with a **DAG-based summarization system**:
- Every message persisted in SQLite
- Older messages summarized into DAG nodes
- Recent messages kept raw (default: last 32)
- Agent can search/expand older material
- Critical for: multi-day project threads, Telegram workflows, research sessions

```bash
openclaw plugins install @martian-engineering/lossless-claw
```

Config: freshTailCount=32, incrementalMaxDepth=-1 (unlimited condensation)

### Jake's Identity Persistence Strategy

For Jake specifically, the identity chain is:
1. ~/.claude/rules/jake.md — personality, four minds, quality gates (GLOBAL, always loaded)
2. ~/.claude/rules/jake-boot.md — boot sequence, greeting protocol (GLOBAL)
3. ~/.claude/rules/jake-context-engineering.md — PRP, Chain-of-Index (GLOBAL)
4. ~/.claude/rules/jake-memory-ops.md — 3-tier memory architecture (GLOBAL)
5. Project-specific CLAUDE.md — routing, architecture
6. Project-specific .claude/rules/jake-project.md — project context
7. Auto-memory files — learned preferences, decisions

**This stack already survives restarts.** Every time Claude Code starts, it loads CLAUDE.md + all rules. Jake IS Jake from the first token. The only thing lost on restart is in-session conversation history, which is handled by --resume or HANDOFF.md.

---

## 7. Always-On Responsiveness (<5 Second Target)

### The Challenge

Opus-level reasoning takes 10-60+ seconds depending on task complexity. A Telegram user expects near-instant acknowledgment.

### Pattern: Tiered Response Architecture

```
Message arrives (0ms)
  |
Telegram "typing..." indicator sent (50ms)    <-- User sees immediate feedback
  |
Effort classification (500ms)
  |
  +-- Simple query -> Haiku/Sonnet response (1-3 sec)
  +-- Medium task -> Sonnet with tools (5-15 sec)
  +-- Complex task -> Opus deep reasoning (15-60 sec)
  |     |
  |     Send interim "Processing..." message (edited later with result)
  +-- Background task -> "Started. I'll message you when done."
       |
       Async execution -> Completion notification via Telegram
```

### Implementation Patterns

**1. Typing Indicator (Built-In)**
Both Claude Code Channels and OpenClaw show "typing..." in Telegram automatically while Claude works.

**2. Interim Message + Edit**
Send a quick "On it..." message, then edit that same message with the final result. Prevents chat flooding.

**3. Model Routing for Speed**
Route simple queries to faster models. Use Sonnet for quick tasks, Opus for deep reasoning.

**4. Message Queue (For Heavy Load)**
Queue messages arriving while Claude is processing. Process sequentially or batch. Acknowledge receipt immediately.

**5. Scheduled Tasks for Proactive Work**
Use Claude Code /loop or OpenClaw HEARTBEAT.md for recurring tasks.

### Realistic Expectations

| Task Type | Expected Response Time | Model |
|-----------|----------------------|-------|
| Simple question | 1-3 seconds | Sonnet/Haiku |
| File lookup | 2-5 seconds | Sonnet |
| Code review | 10-30 seconds | Opus |
| Multi-file implementation | 30-120 seconds | Opus |
| Deep research | 2-10 minutes | Opus + tools |

---

## 8. Mac Studio as Always-On AI Server

### Recommended Stack

```
macOS (Mac Studio / Mac mini)
  launchd (process management — native, zero dependencies)
    Claude Code + Channels (Telegram bridge)
    OpenClaw Gateway (if using OpenClaw)
    Health check script (5-min intervals)
  tmux (fallback for interactive debugging)
  Caffeine/Amphetamine (prevent sleep)
  Tailscale (secure remote access)
```

### launchd Setup (Recommended for macOS)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jake.claude-daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/claude</string>
        <string>--channels</string>
        <string>plugin:telegram@claude-plugins-official</string>
        <string>--dangerously-skip-permissions</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/mikerodgers/Startup-Intelligence-OS</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/jake-daemon.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/jake-daemon-error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>/Users/mikerodgers</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

```bash
# Install
cp com.jake.claude-daemon.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.jake.claude-daemon.plist

# Verify
launchctl list | grep jake

# Logs
tail -f /tmp/jake-daemon.log
```

### OpenClaw Gateway as Daemon

```bash
# Built-in daemon install
openclaw gateway start --install-daemon

# Creates a launchd plist automatically with:
# - RunAtLoad: true
# - KeepAlive: true
# - Auto-restart on crash
# - Starts before user login
```

### Health Monitoring Script

```bash
#!/bin/bash
# /usr/local/bin/jake-health-check.sh
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:18789/health 2>/dev/null)
if [ "$HEALTH" != "200" ]; then
    curl -s "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=Jake daemon health check failed (HTTP $HEALTH)"
    launchctl kickstart -k gui/$(id -u)/com.jake.claude-daemon
fi
```

Run via cron every 5 minutes: `*/5 * * * * /usr/local/bin/jake-health-check.sh`

### macOS Power Management

```bash
# Prevent sleep (critical for always-on)
sudo pmset -a sleep 0
sudo pmset -a disksleep 0
sudo pmset -a displaysleep 5  # Display can sleep, machine stays awake

# Or use caffeinate for specific process
caffeinate -s -w $(pgrep -f "claude --channels") &
```

### Comparison: launchd vs pm2 vs Docker

| Factor | launchd | pm2 | Docker |
|--------|---------|-----|--------|
| **Native macOS** | Yes | No (needs Node) | No (needs Docker Desktop) |
| **Auto-restart** | KeepAlive | --restart | restart: always |
| **Boot start** | RunAtLoad | pm2 startup | Docker Desktop auto-start |
| **Logs** | /tmp/ or custom | pm2 logs | docker logs |
| **Overhead** | Zero | ~50MB Node | ~2GB Docker Desktop |
| **macOS integration** | Full (permissions, keychain) | Partial | Limited (no GUI access) |
| **Recommendation** | **Primary** for Mac | Fallback | Not recommended |

---

## Decision Matrix: Which Approach for Jake?

| Approach | Persistence | Computer Access | Memory | Multi-Agent | Maturity | Effort |
|----------|------------|----------------|--------|-------------|----------|--------|
| **Claude Code Channels** | Process-level (keep running) | Full (native + MCP + Computer Use) | Native (CLAUDE.md + rules + auto-memory) | No | Research preview (Mar 2026) | Low |
| **OpenClaw + ACP** | Session-level (persistent + resumable) | Full (host runtime, no sandbox) | SOUL.md + MEMORY.md + LosslessClaw | Yes (multi-agent) | Mature (325K stars) | Medium |
| **openclaw-claude-code-skill** | Session-level (persistent, forkable) | Full (all Claude Code tools) | Via OpenClaw | Yes (agent teams) | Community | Medium |
| **Clautel** | Process-level (daemon) | Full (per-project) | Session persistence | No | Third-party | Low |
| **RichardAtCT/claude-code-telegram** | Per-user/project (SQLite) | Sandboxed directory | Session + SQLite | No | Community | Low |
| **Custom Agent SDK** | Full control | Full | Custom | Custom | DIY | High |
| **Perplexity Personal Computer** | Always-on cloud agent | Full (Mac mini) | Persistent | Yes | Commercial (new) | Zero (managed) |

### Recommended Path for Jake

**Phase 1 (This Week)**: Claude Code Channels + tmux
- Fastest to deploy, first-party Anthropic support
- Full computer access via native tools
- Jake's identity already persists via .claude/rules/
- tmux keeps it alive; launchd for production

**Phase 2 (Next Sprint)**: Add OpenClaw for multi-agent
- Install OpenClaw alongside Claude Code
- Use ACP to bridge Claude Code sessions
- Get LosslessClaw for context preservation
- Enable multi-agent orchestration (Susan's 73 agents)

**Phase 3 (Future)**: Custom daemon with Agent SDK
- Build a proper daemon using Claude Code Agent SDK (Python)
- Message queue for async processing
- Model routing for response speed
- Full health monitoring and auto-recovery

---

## Sources

- [Claude Code Channels Docs](https://code.claude.com/docs/en/channels)
- [Claude Code Headless/SDK Docs](https://code.claude.com/docs/en/headless)
- [OpenClaw ACP Agents Docs](https://docs.openclaw.ai/tools/acp-agents)
- [Enderfga/openclaw-claude-code-skill](https://github.com/Enderfga/openclaw-claude-code-skill)
- [RichardAtCT/claude-code-telegram](https://github.com/RichardAtCT/claude-code-telegram)
- [Clautel — Claude Code as Background Daemon](https://www.clautel.com/blog/how-to-run-claude-code-as-a-background-daemon)
- [Claude Code Channels — VentureBeat](https://venturebeat.com/orchestration/anthropic-just-shipped-an-openclaw-killer-called-claude-code-channels)
- [Claude Code Channels — MacStories](https://www.macstories.net/stories/first-look-hands-on-with-claude-codes-new-telegram-and-discord-integrations/)
- [OpenClaw Gateway Daemon Guide](https://www.crewclaw.com/blog/openclaw-gateway-daemon-guide)
- [OpenClaw Memory Masterclass](https://velvetshark.com/openclaw-memory-masterclass)
- [LosslessClaw GitHub](https://github.com/Martian-Engineering/lossless-claw)
- [LosslessClaw Deep Dive](https://vibetools.net/posts/say-goodbye-to-openclaw-amnesia-a-deep-dive-and-complete-guide-to-lossless-claw)
- [Sam Zoloth — Claude Code as Autonomous OS](https://samzoloth.com/blog/claude-code-setup-2026)
- [Perplexity Personal Computer — 9to5Mac](https://9to5mac.com/2026/03/11/perplexitys-personal-computer-is-a-cloud-based-ai-agent-running-on-mac-mini/)
- [Claude Computer Use on macOS — 9to5Mac](https://9to5mac.com/2026/03/23/anthropic-is-giving-claude-the-ability-to-use-your-mac-for-you/)
- [OpenClaw on Mac Mini](https://boilerplatehub.com/blog/openclaw-mac-mini)
- [Claude Code Cron Scheduling](https://winbuzzer.com/2026/03/09/anthropic-claude-code-cron-scheduling-background-worker-loop-xcxwbn/)
- [OpenClaw ACP Complete Guide](https://dev.to/czmilo/2026-complete-guide-openclaw-acp-bridge-your-ide-to-ai-agents-3hl8)
