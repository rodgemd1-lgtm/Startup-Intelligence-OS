---
name: jake-intelligence
description: V4 Proactive Intelligence — intent routing, priority engine, decision support, morning brief, SCOUT signals. Use /intel brief for morning brief, /intel decide for decisions, /intel priority for THE ONE THING.
---

# Jake Intelligence — V4 Proactive Intelligence

This skill provides access to Jake's V4 intelligence modules directly from Telegram/OpenClaw.

## Commands

### /intel brief
Generate today's V4 morning brief with THE ONE THING, calendar, email, signals.

```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 pai/pipelines/morning_briefing.py --v4
```

### /intel priority
Calculate THE ONE THING right now.

```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 -c "
import sys; sys.path.insert(0, '.')
from pai.intelligence.priority_engine import PriorityEngine, CandidateAction, ActionSource
engine = PriorityEngine(available_deep_work_hours=4.0)
one = engine.calculate_one_thing([
    CandidateAction(action='Check morning brief and act on top item', why='Start of day routine', impact='Set direction', estimated_minutes=15, source=ActionSource.GOAL),
])
print(one.to_text())
"
```

### /intel decide [question]
Run structured decision support on a question.

When the user asks "should I..." or faces a decision, run:

```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 -c "
import sys; sys.path.insert(0, '.')
from pai.intelligence.decision_support import DecisionSupport
ds = DecisionSupport()
brief = ds.full_analysis('QUESTION_HERE', context='USER_CONTEXT')
print(brief.to_markdown())
"
```

### /intel classify [message]
Classify a message using the KIRA intent router.

```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 -c "
import sys; sys.path.insert(0, '.')
from pai.intelligence.intent_router import IntentRouter
router = IntentRouter(log_classifications=True)
print(router.classify_and_format('MESSAGE_HERE'))
"
```

### /intel signals
Show recent competitive signals from SCOUT.

```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 -c "
import sys; sys.path.insert(0, '.')
from pai.intelligence.scout import Scout
scout = Scout()
print(scout.format_for_brief() or 'No signals detected. Run a scan first.')
"
```

### /intel eval
Run self-evaluation scorecard.

```bash
cd /Users/michaelrodgers/Desktop/Startup-Intelligence-OS && python3 -c "
import sys; sys.path.insert(0, '.')
from pai.learning.self_evaluation import SelfEvaluation
se = SelfEvaluation()
report = se.evaluate()
print(report.to_markdown())
"
```

## Automatic Behavior

When processing ANY message from Mike, Jake should:
1. Run the intent router to classify the message
2. Route to the appropriate model tier and agent
3. If intent is "decision", trigger decision support
4. If confidence < 0.6, escalate to Opus for disambiguation

## Integration Notes

- All modules live under `pai/intelligence/` and `pai/learning/`
- Logs written to `pai/intelligence/logs/` (JSONL)
- Config in `pai/config/` (notification-rules.json, scout-sources.json)
- Morning brief integrates V4 modules via `--v4` flag
