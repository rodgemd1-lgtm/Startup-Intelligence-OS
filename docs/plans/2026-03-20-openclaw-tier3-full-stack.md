# OpenClaw Intelligence Platform — Tier 1→3 Full Stack Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform OpenClaw from a query engine into a full autonomous intelligence platform with skill chaining, proactive alerts, agent-to-agent delegation, learning loops, and desktop workflow automation.

**Architecture:** Three-layer stack — FastAPI connectors (port 7842) → OpenClaw skills (~/clawd/skills/) → OpenClaw gateway (port 7841) → Telegram. Susan MCP server (34 tools) provides agent execution and RAG. New capabilities are added as connectors + skills, keeping the architecture additive and each piece independently testable.

**Tech Stack:** Python 3.11+, FastAPI, httpx, python-telegram-bot, OpenClaw gateway, Susan MCP (Supabase pgvector, Voyage AI embeddings), Hammerspoon (Lua), launchd for scheduling.

**Repos:**
- `~/Desktop/jake-assistant/` — FastAPI server, bot, connectors
- `~/Startup-Intelligence-OS/susan-team-architect/backend/` — Susan MCP, control plane, RAG
- `~/clawd/` — OpenClaw workspace (skills, memory, identity)
- `~/.openclaw/` — OpenClaw config and state

**Current State (what's working):**
- FastAPI server: 26 routes, 6 connectors (calendar, system, desktop, oracle_health, susan, supabase_multi)
- OpenClaw gateway: Telegram enabled, 3 custom skills (susan-rag-query, ellen-oracle-health, supabase-query)
- Oracle Health search: 0.03s (priority dir grep)
- Supabase: 4 accounts, 108+ tables
- Susan RAG: 94K chunks, 34 MCP tools
- Model routing: 4-tier (Ollama llama3.2:3b → Groq llama-3.3-70b → Claude Sonnet → Claude Opus)

---

## Phase 1: Skill Chaining & Compound Workflows (Tier 1, Tasks 1-2)

**Why first:** This is the architectural unlock. Every later phase benefits from skills that can call other skills.

### Task 1: Chain Engine — Multi-Step Skill Executor

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/chain_engine.py`
- Create: `~/Desktop/jake-assistant/tests/test_chain_engine.py`
- Modify: `~/Desktop/jake-assistant/server.py` (add chain endpoints)

**Step 1: Write failing test for chain engine**

```python
# tests/test_chain_engine.py
import pytest
from connectors.chain_engine import ChainEngine, ChainStep

def test_single_step_chain():
    """A chain with one step should execute and return results."""
    engine = ChainEngine()
    chain = [
        ChainStep(connector="oracle_health", action="search", params={"query": "pricing"})
    ]
    result = engine.execute(chain)
    assert result["steps_completed"] == 1
    assert result["final_output"] is not None

def test_multi_step_chain_passes_context():
    """Output from step 1 should be available as input to step 2."""
    engine = ChainEngine()
    chain = [
        ChainStep(connector="oracle_health", action="search", params={"query": "pricing"}),
        ChainStep(connector="susan", action="search", params={"query": "{prev.query} market context"}),
    ]
    result = engine.execute(chain)
    assert result["steps_completed"] == 2

def test_chain_stops_on_error():
    """Chain should stop and report if a step fails."""
    engine = ChainEngine()
    chain = [
        ChainStep(connector="nonexistent", action="search", params={"query": "test"}),
    ]
    result = engine.execute(chain)
    assert result["steps_completed"] == 0
    assert "error" in result

def test_template_substitution():
    """Chain params should support {prev.field} template syntax."""
    engine = ChainEngine()
    result = engine._substitute("{prev.total} results found", {"total": 5})
    assert result == "5 results found"
```

**Step 2: Run test to verify it fails**

Run: `cd ~/Desktop/jake-assistant && python3 -m pytest tests/test_chain_engine.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'connectors.chain_engine'`

**Step 3: Implement chain engine**

```python
# connectors/chain_engine.py
"""Chain Engine — execute multi-step workflows across connectors.

Chains are sequences of steps where each step can reference the output
of the previous step via {prev.field} template syntax.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from connectors import oracle_health, susan, supabase_multi


@dataclass
class ChainStep:
    connector: str  # "oracle_health", "susan", "supabase"
    action: str     # "search", "query", "read_file", "list_tables"
    params: dict[str, Any] = field(default_factory=dict)


CONNECTOR_MAP = {
    "oracle_health": {
        "search": oracle_health.search_repo,
        "read_file": oracle_health.read_file,
        "list_briefs": oracle_health.list_briefs,
    },
    "susan": {
        "search": lambda **kw: susan.search_knowledge(**kw),
    },
    "supabase": {
        "list_tables": supabase_multi.list_tables,
        "query": supabase_multi.query_table,
        "search": supabase_multi.search_table,
    },
}


class ChainEngine:
    def execute(self, steps: list[ChainStep]) -> dict[str, Any]:
        results = []
        prev_output: dict[str, Any] = {}

        for i, step in enumerate(steps):
            connector_actions = CONNECTOR_MAP.get(step.connector)
            if not connector_actions:
                return {
                    "steps_completed": i,
                    "error": f"Unknown connector: {step.connector}",
                    "results": results,
                    "final_output": prev_output,
                }

            action_fn = connector_actions.get(step.action)
            if not action_fn:
                return {
                    "steps_completed": i,
                    "error": f"Unknown action: {step.connector}.{step.action}",
                    "results": results,
                    "final_output": prev_output,
                }

            # Substitute {prev.field} references in params
            resolved_params = {}
            for key, val in step.params.items():
                if isinstance(val, str):
                    resolved_params[key] = self._substitute(val, prev_output)
                else:
                    resolved_params[key] = val

            try:
                output = action_fn(**resolved_params)
            except Exception as e:
                return {
                    "steps_completed": i,
                    "error": f"Step {i} failed: {e}",
                    "results": results,
                    "final_output": prev_output,
                }

            results.append({"step": i, "connector": step.connector, "action": step.action, "output": output})
            prev_output = output

        return {
            "steps_completed": len(steps),
            "results": results,
            "final_output": prev_output,
        }

    def _substitute(self, template: str, prev: dict[str, Any]) -> str:
        def replacer(match):
            field_name = match.group(1)
            return str(prev.get(field_name, match.group(0)))
        return re.sub(r"\{prev\.(\w+)\}", replacer, template)
```

**Step 4: Run tests**

Run: `cd ~/Desktop/jake-assistant && python3 -m pytest tests/test_chain_engine.py -v`
Expected: PASS (4/4)

**Step 5: Add chain API endpoint to server.py**

Add to `~/Desktop/jake-assistant/server.py` before the `if __name__` block:

```python
from connectors.chain_engine import ChainEngine, ChainStep
from pydantic import BaseModel

class ChainRequest(BaseModel):
    steps: list[dict]  # [{connector, action, params}]

@app.post("/api/chain")
async def run_chain(req: ChainRequest):
    """Execute a multi-step chain across connectors."""
    engine = ChainEngine()
    steps = [ChainStep(**s) for s in req.steps]
    return engine.execute(steps)
```

**Step 6: Commit**

```bash
cd ~/Desktop/jake-assistant
git add connectors/chain_engine.py tests/test_chain_engine.py server.py
git commit -m "feat: add chain engine for multi-step skill workflows"
```

---

### Task 2: Pre-Built Chain Templates + OpenClaw Skill

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/chain_templates.py`
- Create: `~/clawd/skills/chain-query/skill.md`
- Modify: `~/Desktop/jake-assistant/server.py` (add template endpoints)

**Step 1: Create chain templates**

```python
# connectors/chain_templates.py
"""Pre-built chain templates for common compound queries."""
from connectors.chain_engine import ChainStep

TEMPLATES = {
    "oracle_health_deep_dive": {
        "description": "Search Oracle Health repo + Susan RAG, synthesize both",
        "steps": [
            ChainStep(connector="oracle_health", action="search", params={"query": "{query}"}),
            ChainStep(connector="susan", action="search", params={"query": "{query}", "company_id": "oracle-health"}),
        ],
    },
    "cross_platform_search": {
        "description": "Search across Oracle Health, Susan RAG, and Supabase",
        "steps": [
            ChainStep(connector="oracle_health", action="search", params={"query": "{query}"}),
            ChainStep(connector="susan", action="search", params={"query": "{query}"}),
        ],
    },
    "supabase_explore": {
        "description": "List tables then query the most likely one",
        "steps": [
            ChainStep(connector="supabase", action="list_tables", params={"account_id": "{account}"}),
        ],
    },
}


def get_template(name: str, variables: dict) -> list[ChainStep]:
    """Get a chain template with variables substituted."""
    template = TEMPLATES.get(name)
    if not template:
        raise ValueError(f"Unknown template: {name}. Available: {list(TEMPLATES.keys())}")

    steps = []
    for step in template["steps"]:
        params = {}
        for k, v in step.params.items():
            if isinstance(v, str):
                for var_name, var_val in variables.items():
                    v = v.replace(f"{{{var_name}}}", str(var_val))
            params[k] = v
        steps.append(ChainStep(connector=step.connector, action=step.action, params=params))
    return steps
```

**Step 2: Add template endpoint to server.py**

```python
@app.post("/api/chain/template")
async def run_chain_template(
    template: str = Query(..., description="Template name"),
    query: str = Query("", description="Search query"),
    account: str = Query("susan", description="Supabase account for DB templates"),
):
    """Execute a pre-built chain template."""
    from connectors.chain_templates import get_template
    engine = ChainEngine()
    steps = get_template(template, {"query": query, "account": account})
    return engine.execute(steps)
```

**Step 3: Create OpenClaw chain skill**

Write `~/clawd/skills/chain-query/skill.md` with instructions for compound queries using the chain API.

**Step 4: Commit**

```bash
cd ~/Desktop/jake-assistant
git add connectors/chain_templates.py server.py
git commit -m "feat: add chain templates and compound query skill"
```

---

## Phase 2: Gmail VIP Alerts + Voice Input (Tier 1, Tasks 3-4)

**Why:** Gmail alerts unlock the Ellen use case (VIP email notifications). Voice input makes Telegram usable while driving.

### Task 3: Gmail VIP Alert Connector

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/gmail.py`
- Create: `~/Desktop/jake-assistant/tests/test_gmail.py`
- Modify: `~/Desktop/jake-assistant/config/settings.py` (add Gmail config)
- Modify: `~/Desktop/jake-assistant/server.py` (add Gmail endpoints)
- Create: `~/clawd/skills/gmail-alerts/skill.md`

**Architecture:** Use Google Gmail API (OAuth2) to poll for new VIP emails. Only expose subject + sender (compliance — no body content over Telegram). Push alerts via Telegram Bot API.

**Step 1: Write failing test**

Test Gmail connector with mocked API responses — verify VIP filtering, subject-only extraction, and Telegram formatting.

**Step 2: Implement Gmail connector**

- OAuth2 token storage in `~/Desktop/jake-assistant/config/gmail_token.json`
- Poll endpoint: `GET /api/gmail/vip` — returns recent emails from VIP_SENDERS
- Push endpoint: `POST /api/gmail/alert` — sends VIP alert to Telegram
- Compliance: NEVER include email body in any response. Subject line + sender only.

**Step 3: Create scheduled poll**

Use OpenClaw cron or launchd to poll every 5 minutes and push VIP alerts.

**Step 4: Commit**

---

### Task 4: Voice Input via Whisper

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/voice.py`
- Modify: `~/Desktop/jake-assistant/bot.py` (add voice message handler)

**Architecture:** Telegram voice messages → download .ogg → transcribe via OpenAI Whisper API (or local whisper.cpp) → feed transcription into existing intent detection → respond as text.

**Step 1: Add voice handler to bot.py**

Register a `MessageHandler(filters.VOICE | filters.VOICE_NOTE, handle_voice)` that:
1. Downloads the voice file
2. Transcribes via Whisper
3. Feeds text into `detect_intent()`
4. Returns normal text response

**Step 2: Test with a real Telegram voice message**

**Step 3: Commit**

---

## Phase 3: Cross-Account Intelligence (Tier 1, Task 5 — completes Tier 1)

### Task 5: Unified Cross-Account Search

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/unified_search.py`
- Create: `~/Desktop/jake-assistant/tests/test_unified_search.py`
- Modify: `~/Desktop/jake-assistant/server.py`
- Create: `~/clawd/skills/unified-search/skill.md`

**Architecture:** Fan-out search across Oracle Health repo + Susan RAG + all Supabase accounts in parallel. Merge, deduplicate, rank by relevance, return top N.

**Step 1: Write failing test**

Test that unified search queries all sources concurrently and merges results.

**Step 2: Implement with concurrent.futures.ThreadPoolExecutor**

```python
def unified_search(query: str, limit: int = 10) -> dict:
    """Search ALL data sources in parallel and merge results."""
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(oracle_health.search_repo, query): "oracle_health",
            pool.submit(susan.search_knowledge, query): "susan_rag",
            pool.submit(supabase_multi.search_table, "susan", "knowledge_chunks", "content", query): "supabase",
        }
        # ... merge results by source, rank, return top N
```

**Step 3: Add unified search endpoint + OpenClaw skill**

**Step 4: Commit**

---

## Phase 4: Proactive Intelligence (Tier 2, Task 6)

**Why:** Stop being reactive. Push insights before Mike asks.

### Task 6: Proactive Push Engine

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/proactive.py`
- Create: `~/Desktop/jake-assistant/tests/test_proactive.py`
- Modify: `~/Desktop/jake-assistant/server.py`
- Create: `~/Library/LaunchAgents/com.jake.proactive.plist` (or use OpenClaw cron)

**Architecture:** Scheduled jobs that run checks and push Telegram alerts when conditions are met.

**Proactive Checks:**

| Check | Schedule | Condition | Alert |
|-------|----------|-----------|-------|
| Morning brief | 6:00 AM daily | Always | Oracle Health brief + calendar + VIP emails |
| Market moves | Every 2 hours | TrendRadar P0/P1 signal | Competitive alert via Telegram |
| Stale data | Daily 9 AM | Any Susan data_type >14 days old | "Your X data is stale" |
| Supabase anomaly | Every 6 hours | Row count delta >20% | "TransformFit users jumped 25%" |

**Step 1: Write failing tests for each check type**

**Step 2: Implement proactive engine with check registry**

```python
class ProactiveEngine:
    checks: list[ProactiveCheck]

    def run_all(self) -> list[Alert]:
        """Run all checks and return triggered alerts."""

    def push_alerts(self, alerts: list[Alert]) -> None:
        """Send alerts to Telegram via Bot API."""
```

**Step 3: Wire up scheduling via launchd plist or OpenClaw cron**

**Step 4: Commit**

---

## Phase 5: V4b Engine Wiring (Tier 2, Task 7)

### Task 7: Chains, Birch, Trust — Decision Engine

**Files:**
- Modify: `~/Desktop/jake-assistant/connectors/chain_engine.py` (extend with Birch and Trust)
- Create: `~/Desktop/jake-assistant/connectors/birch.py` (decision trees)
- Create: `~/Desktop/jake-assistant/connectors/trust.py` (confidence scoring)
- Create: `~/Desktop/jake-assistant/tests/test_birch.py`
- Create: `~/Desktop/jake-assistant/tests/test_trust.py`

**Architecture:**

- **Chains** (Task 1): Already built. Multi-step skill execution.
- **Birch**: Decision tree router. Given a query, evaluate conditions and branch to different chain templates.
  - Example: "Oracle Health question?" → if yes, run ellen chain. If about fitness → run transformfit chain. If ambiguous → run unified search.
- **Trust**: Confidence scoring layer. After any response, score it 0.0-1.0 based on source count, source freshness, cross-source agreement.
  - HIGH (>0.8): "Confident answer, multiple recent sources agree"
  - MEDIUM (0.5-0.8): "Moderate confidence, limited sources"
  - LOW (<0.5): "Low confidence — recommend deeper research"

**Step 1: Write failing tests for Birch and Trust**

**Step 2: Implement Birch decision router**

**Step 3: Implement Trust confidence scorer**

**Step 4: Wire both into the chain engine**

**Step 5: Commit**

---

## Phase 6: Notion Integration (Tier 2, Task 8 — completes Tier 2)

### Task 8: Notion Capture from Telegram

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/notion_connector.py`
- Create: `~/Desktop/jake-assistant/tests/test_notion.py`
- Modify: `~/Desktop/jake-assistant/bot.py` (add notion intents)
- Modify: `~/Desktop/jake-assistant/server.py`
- Create: `~/clawd/skills/notion-capture/skill.md`

**Architecture:** Use Notion API to create pages in Mike's workspace. Intents: "note: [text]", "decision: [text]", "action item: [text]".

**Step 1: Write failing tests with mocked Notion API**

**Step 2: Implement Notion connector**

- Create page in specified database
- Support: notes, decisions, action items
- Tag with project, date, source

**Step 3: Add Telegram intents**

```python
if any(word in text_lower for word in ["note:", "decision:", "action item:", "capture:", "notion"]):
    return "notion_capture", {"text": text, "type": detected_type}
```

**Step 4: Commit**

---

## Phase 7: Agent-to-Agent Delegation (Tier 3, Task 9)

**Why:** This is the leap from "search tool" to "thinking system." OpenClaw asks Susan's specialized agents directly, not just RAG.

### Task 9: MCP Agent Bridge

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/agent_bridge.py`
- Create: `~/Desktop/jake-assistant/tests/test_agent_bridge.py`
- Modify: `~/Desktop/jake-assistant/server.py`
- Create: `~/clawd/skills/ask-agent/skill.md`

**Architecture:** The agent bridge calls Susan's MCP `run_agent` tool, which executes a specific agent (Steve, Compass, Freya, etc.) with RAG context injection. The bridge translates natural language into agent routing.

**Susan MCP `run_agent` signature:**
```python
run_agent(agent_id: str, prompt: str, company_id: str) -> dict
```

**Available agents (73 total):**
- Steve (strategy), Compass (product), Atlas (engineering), Sentinel (security)
- Freya (behavioral economics), Coach (exercise science), Sage (nutrition)
- Research Director, Forge (QA), Herald (PR), Beacon (ASO)
- 14 film studio agents, 12 design studios

**Step 1: Write failing tests**

```python
def test_agent_routing_detects_strategy():
    """'What's our competitive position' should route to Steve."""
    bridge = AgentBridge()
    agent = bridge.route_to_agent("What's our competitive position on prior auth?")
    assert agent == "steve"

def test_agent_routing_detects_product():
    """'Feature prioritization' should route to Compass."""
    bridge = AgentBridge()
    agent = bridge.route_to_agent("Help me prioritize the roadmap for Q2")
    assert agent == "compass"

def test_agent_execution_returns_response():
    """Agent should return structured response with sources."""
    bridge = AgentBridge()
    result = bridge.ask_agent("steve", "What's Oracle Health's pricing advantage?", "oracle-health")
    assert "response" in result
    assert "agent" in result
```

**Step 2: Implement agent bridge**

```python
# connectors/agent_bridge.py
"""Agent Bridge — delegate questions to Susan's specialist agents via MCP."""

AGENT_KEYWORDS = {
    "steve": ["strategy", "competitive", "pricing", "market", "positioning", "revenue"],
    "compass": ["product", "roadmap", "feature", "prioritize", "user story", "sprint"],
    "atlas": ["architecture", "api", "backend", "infrastructure", "deploy", "code"],
    "freya": ["behavioral", "retention", "engagement", "nudge", "psychology", "habit"],
    "sentinel": ["security", "audit", "vulnerability", "compliance", "risk"],
    "forge": ["test", "qa", "bug", "quality", "regression"],
    "coach": ["exercise", "workout", "training", "fitness", "programming"],
    "sage": ["nutrition", "diet", "macro", "supplement", "meal"],
    "herald": ["pr", "announcement", "press", "communication", "messaging"],
    "beacon": ["seo", "aso", "ranking", "keyword", "app store"],
    "aria": ["growth", "acquisition", "viral", "content", "marketing"],
    "ledger": ["finance", "budget", "runway", "unit economics", "pricing model"],
    "research-director": ["research", "study", "paper", "evidence", "benchmark"],
}

class AgentBridge:
    def route_to_agent(self, query: str) -> str:
        """Route a natural language query to the best Susan agent."""
        query_lower = query.lower()
        scores = {}
        for agent, keywords in AGENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[agent] = score
        if not scores:
            return "steve"  # default to strategy
        return max(scores, key=scores.get)

    def ask_agent(self, agent_id: str, prompt: str, company_id: str = "shared") -> dict:
        """Execute a Susan agent via subprocess (same pattern as susan.py)."""
        # Calls Susan's run_agent MCP tool via subprocess
        # Returns: {agent, response, sources, confidence}
        ...
```

**Step 3: Add API endpoints**

```python
@app.post("/api/agent/ask")
async def ask_agent(query: str, company: str = "shared"):
    """Route query to best Susan agent and return response."""

@app.get("/api/agent/list")
async def list_agents():
    """List available agents with descriptions."""
```

**Step 4: Create OpenClaw skill for agent delegation**

**Step 5: Wire into bot.py intent detection**

Queries that don't match specific intents but seem like strategy/product/engineering questions → route to agent bridge instead of returning "unknown."

**Step 6: Commit**

---

## Phase 8: Learning Loop + Desktop Automation (Tier 3, Task 10 — THE SUMMIT)

### Task 10A: Learning Loop — Query Analytics & Route Optimization

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/learning.py`
- Create: `~/Desktop/jake-assistant/data/query_log.jsonl` (append-only log)
- Create: `~/Desktop/jake-assistant/tests/test_learning.py`
- Modify: `~/Desktop/jake-assistant/server.py` (add logging middleware)

**Architecture:** Log every query + response + which connector answered + response time + user feedback (thumbs up/down on Telegram). Periodically analyze to optimize routing.

**Step 1: Write failing tests**

```python
def test_query_logging():
    """Every API call should append to query log."""
    logger = QueryLogger()
    logger.log(query="pricing strategy", connector="oracle_health", response_time=0.03, result_count=16)
    entries = logger.get_recent(1)
    assert len(entries) == 1
    assert entries[0]["connector"] == "oracle_health"

def test_analytics_top_queries():
    """Should identify most frequent query patterns."""
    logger = QueryLogger()
    # ... add 10 queries
    top = logger.top_queries(limit=5)
    assert len(top) <= 5

def test_route_recommendations():
    """Should recommend routing changes based on patterns."""
    analyzer = RouteAnalyzer()
    # If 80% of queries go to oracle_health, recommend pre-caching
    recommendations = analyzer.analyze()
    assert isinstance(recommendations, list)
```

**Step 2: Implement query logger (JSONL append-only)**

**Step 3: Add FastAPI middleware to log every request**

```python
@app.middleware("http")
async def log_queries(request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    if request.url.path.startswith("/api/"):
        query_logger.log(path=request.url.path, elapsed=elapsed, ...)
    return response
```

**Step 4: Implement route analyzer**

- Identify top queries by frequency
- Identify slow queries (>1s)
- Identify connectors with high error rates
- Generate recommendations: "Pre-cache top 10 Oracle Health queries", "Switch connector X to Y"

**Step 5: Add analytics endpoint**

```python
@app.get("/api/analytics/summary")
async def analytics_summary():
    """Return query analytics summary for the last 7 days."""
```

**Step 6: Commit**

---

### Task 10B: Desktop Workflow Automation

**Files:**
- Create: `~/Desktop/jake-assistant/connectors/workflows.py`
- Modify: `~/Desktop/jake-assistant/connectors/desktop.py` (extend Hammerspoon commands)
- Create: `~/Desktop/jake-assistant/tests/test_workflows.py`
- Create: `~/clawd/skills/workflow-automation/skill.md`

**Architecture:** Compound desktop workflows that combine multiple actions. "Prep for my 2pm meeting" → (1) fetch calendar event details, (2) search Oracle Health for related topics, (3) pull Supabase data, (4) format a brief, (5) open relevant docs on desktop, (6) send brief to Telegram.

**Step 1: Write failing tests**

```python
def test_meeting_prep_workflow():
    """Meeting prep should combine calendar + search + format."""
    wf = WorkflowEngine()
    result = wf.run("meeting_prep", {"time": "14:00"})
    assert "calendar_event" in result
    assert "research" in result
    assert "brief" in result

def test_focus_mode_workflow():
    """Focus mode should configure desktop for deep work."""
    wf = WorkflowEngine()
    result = wf.run("focus_mode", {"duration": 60})
    assert result["dnd_enabled"] is True
```

**Step 2: Implement workflow engine**

```python
WORKFLOWS = {
    "meeting_prep": [
        {"action": "calendar.get_events", "params": {"date": "today"}},
        {"action": "filter_by_time", "params": {"time": "{time}"}},
        {"action": "oracle_health.search", "params": {"query": "{event.title}"}},
        {"action": "format_brief"},
        {"action": "desktop.open_url", "params": {"url": "{event.meeting_link}"}},
        {"action": "telegram.send", "params": {"text": "{brief}"}},
    ],
    "focus_mode": [
        {"action": "desktop.toggle_dnd"},
        {"action": "desktop.launch_app", "params": {"app": "Cursor"}},
        {"action": "desktop.set_volume", "params": {"level": 0}},
        {"action": "telegram.send", "params": {"text": "Focus mode ON for {duration} min"}},
    ],
    "end_of_day": [
        {"action": "calendar.get_events", "params": {"date": "tomorrow"}},
        {"action": "supabase.query", "params": {"account": "susan", "table": "daily_actions"}},
        {"action": "format_eod_summary"},
        {"action": "telegram.send", "params": {"text": "{summary}"}},
    ],
}
```

**Step 3: Extend Hammerspoon commands**

Add to desktop.py:
- `toggle_dnd()` — macOS Do Not Disturb
- `open_file(path)` — Open specific file in default app
- `arrange_windows(layout)` — Tile windows for meeting/focus/presentation

**Step 4: Add Telegram intents**

```python
if any(phrase in text_lower for phrase in ["prep for", "get ready for", "prepare for"]):
    return "meeting_prep", {"query": text}
if any(phrase in text_lower for phrase in ["focus mode", "deep work", "do not disturb"]):
    return "focus_mode", {"duration": 60}
if any(phrase in text_lower for phrase in ["end of day", "wrap up", "eod"]):
    return "end_of_day", {}
```

**Step 5: Create OpenClaw workflow skill**

**Step 6: Commit**

---

## Execution Timeline

| Phase | Tasks | Est. Sessions | Dependencies |
|-------|-------|--------------|-------------|
| Phase 1: Skill Chaining | 1-2 | 1 session | None |
| Phase 2: Gmail + Voice | 3-4 | 1-2 sessions | Gmail OAuth setup (manual step) |
| Phase 3: Unified Search | 5 | 1 session | Phase 1 (chain engine) |
| Phase 4: Proactive Push | 6 | 1 session | Phase 2 (Gmail for VIP alerts) |
| Phase 5: V4b Engine | 7 | 1-2 sessions | Phase 1 (chain engine) |
| Phase 6: Notion | 8 | 1 session | Notion API key (manual step) |
| Phase 7: Agent Bridge | 9 | 1-2 sessions | Susan MCP running |
| Phase 8: Learning + Desktop | 10A-10B | 2 sessions | Phases 1-7 complete |

**Total: ~10-12 sessions to full Tier 3**

**Critical path:** Phase 1 → Phase 5 → Phase 7 → Phase 8 (the engine chain)
**Parallel track:** Phase 2 + Phase 6 can run alongside anything (independent connectors)

## Quality Gates

| Milestone | Gate | Who Reviews |
|-----------|------|-------------|
| Phase 1 complete | Chain engine tests pass, compound query works via Telegram | Forge (QA) |
| Phase 4 complete | Proactive alerts firing on schedule, no false positives for 24h | Sentinel (security) |
| Phase 7 complete | Agent delegation routes correctly 90%+ of test queries | Steve (strategy) + Compass (product) |
| Phase 8 complete | Full audit: all connectors tested, learning loop capturing, desktop workflows working | Full team sweep |

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Gmail OAuth complexity | Medium | Use App Password fallback if OAuth is too painful |
| Susan MCP subprocess latency | High | Add connection pooling or switch to direct import |
| Hammerspoon bridge flakiness | Medium | Add health check retry + graceful degradation |
| OpenClaw gateway skill cache | Low | Restart gateway after each new skill deployment |
| Context budget per session | High | Break phases into independent sessions, clean handoffs |
| Cost (API calls at scale) | Medium | Proactive checks use Ollama/Groq, save Claude for agent delegation |

## Cost Model

| Component | Model | Est. Cost/Month |
|-----------|-------|-----------------|
| Proactive checks (4x daily) | Ollama llama3.2:3b | $0 (local) |
| Telegram intent routing | Groq llama-3.3-70b | ~$2 |
| Agent delegation (10 queries/day) | Claude Sonnet | ~$15 |
| Deep research (2x/week) | Claude Opus | ~$20 |
| Voice transcription | Whisper API | ~$5 |
| **Total** | | **~$42/month** |

Well within Mike's $100-150/month budget.
