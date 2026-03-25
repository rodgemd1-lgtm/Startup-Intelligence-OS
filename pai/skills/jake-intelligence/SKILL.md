---
name: jake-intelligence
description: V4 Proactive Intelligence — intent routing, priority engine, decision support, morning brief, SCOUT signals. Use /intel brief for morning brief, /intel decide for decisions, /intel priority for THE ONE THING.
---

# Jake Intelligence — V4 Proactive Intelligence

This skill provides Jake's V4 intelligence pipeline. It classifies every message, routes to the right handler, and delivers structured responses.

## Automatic Behavior

When processing ANY message from Mike, run the intent classifier first:

```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 pai/cli/jake_dispatch.py classify "MESSAGE_TEXT"
```

This returns JSON with intent, confidence, model tier, and recommended agent. Use this to decide how to respond:

| Intent | Action |
|--------|--------|
| `quick_answer` | Answer directly — no agent needed |
| `status_check` | Run brief, calendar, or one-thing (see below) |
| `research` | Route to Susan bridge: `susan route COMPANY "TASK"` |
| `strategy` | Route to Steve Strategy via Susan |
| `build` | Route to Claude Code or Atlas Engineering |
| `decision` | Run decision support (see below) |
| `casual` | Answer naturally — keep it short |

If confidence < 0.6: ask Mike to clarify. Don't guess — wrong routing wastes time and money.

## Commands

### /intel brief — Morning Brief
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 pai/cli/jake_dispatch.py brief
```
Returns: Full V4 morning brief with THE ONE THING, calendar, email, signals.

### /intel decide [question] — Decision Support
When intent is `decision` or user asks "should I...":
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 pai/cli/jake_dispatch.py decide "QUESTION"
```
Returns: Structured decision analysis with options, risks, red team, recommendation.

### /intel priority — THE ONE THING
When user asks "what should I do today?" or "what's my priority?":
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 pai/cli/jake_dispatch.py one-thing
```
Returns: THE ONE THING with why, impact, time estimate, and blockers.

### /intel classify [message] — Intent Classification
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 pai/cli/jake_dispatch.py classify "MESSAGE"
```
Returns: JSON with intent, confidence, model tier, agent routing.

### Full Dispatch (any message)
Routes any message through the complete intelligence pipeline:
```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 -m pai.dispatcher "MESSAGE_TEXT"
```

## Response Formatting (Telegram)

- Use bold for headers and key metrics
- Keep messages scannable — bullet points over paragraphs
- Include confidence scores when routing to agents
- THE ONE THING always goes at the top
- Max 4096 chars per Telegram message — split if needed

## Integration Notes

- All modules live under `pai/intelligence/` and `pai/learning/`
- CLI entrypoints: `pai/cli/jake_dispatch.py`
- Dispatcher: `pai/dispatcher.py`
- Logs written to `pai/intelligence/logs/` (JSONL)
- Config in `pai/config/` (notification-rules.json, scout-sources.json)
- Morning brief integrates V4 modules via `--v4` flag
