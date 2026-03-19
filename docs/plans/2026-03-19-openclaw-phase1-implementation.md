# OpenClaw Intelligence Platform — Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Get sourced answers from Susan's RAG working via Telegram within one session — install Ollama for local inference, configure model routing, build the `susan-rag-query` skill, seed OpenClaw memory, and wire the daily brief to Telegram.

**Architecture:** OpenClaw (Telegram gateway) calls Susan's backend via `exec curl` to the FastAPI bridge server. A new `/api/susan/search` endpoint on the FastAPI bridge calls Susan's `search_company_knowledge()` function directly. OpenClaw's built-in agent topology handles model routing (Ollama for heartbeats, Groq for sub-agents, Sonnet for primary, Opus for deep work).

**Tech Stack:** OpenClaw (v2026.3.13), Ollama (local LLM), Groq API, FastAPI (Python 3.11+), Susan RAG (Voyage AI + Supabase), SKILL.md format.

**Design doc:** `docs/plans/2026-03-19-openclaw-intelligence-platform-design.md`

---

## Task 1: Install Ollama and Pull Local Models

**Files:**
- None (system setup)

**Step 1: Install Ollama via Homebrew**

Run:
```bash
brew install ollama
```

Expected: Ollama installed to `/opt/homebrew/bin/ollama`

**Step 2: Start Ollama server**

Run:
```bash
ollama serve &
```

Expected: Server starts on `http://127.0.0.1:11434`

**Step 3: Pull local models**

Run:
```bash
ollama pull llama3.2:8b
ollama pull llama3.2:3b
```

Expected: Both models downloaded. Verify with `ollama list`.

**Step 4: Test local inference**

Run:
```bash
curl -s http://127.0.0.1:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3.2:8b","messages":[{"role":"user","content":"Say hello in one word"}]}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```

Expected: A one-word greeting response. This confirms Ollama's OpenAI-compatible API works.

---

## Task 2: Configure OpenClaw Model Routing

**Files:**
- Modify: `~/.openclaw/openclaw.json`

**Step 1: Back up current config**

Run:
```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
```

**Step 2: Update openclaw.json with tiered model routing**

Read the current `~/.openclaw/openclaw.json` and merge in the following changes to the `agents` section:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": [
          "groq/llama-3.3-70b-versatile",
          "ollama/llama3.2:8b"
        ]
      },
      "subagents": {
        "model": "groq/llama-3.3-70b-versatile",
        "maxConcurrent": 2,
        "archiveAfterMinutes": 60
      },
      "heartbeat": {
        "every": "30m",
        "model": "ollama/llama3.2:3b"
      },
      "bootstrapMaxChars": 150000,
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "1h"
      },
      "compaction": {
        "mode": "safeguard"
      },
      "contextTokens": 128000
    },
    "list": [
      { "id": "jake-chat", "model": "anthropic/claude-sonnet-4-20250514" },
      { "id": "jake-triage", "model": "groq/llama-3.3-70b-versatile" },
      { "id": "jake-deep-work", "model": "anthropic/claude-opus-4-20250514" },
      { "id": "daily-ops", "model": "groq/llama-3.3-70b-versatile" }
    ]
  }
}
```

Also add the Ollama provider config to the `models` section:

```json
{
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434/v1",
        "apiKey": "ollama-local",
        "api": "openai-completions",
        "models": [
          {
            "id": "llama3.2:8b",
            "name": "Llama 3.2 8B",
            "contextWindow": 65536,
            "maxTokens": 8192
          },
          {
            "id": "llama3.2:3b",
            "name": "Llama 3.2 3B",
            "contextWindow": 32768,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

Preserve all existing config (channels, gateway, tools, commands). Only merge the new fields.

**Step 3: Set Groq API key**

Run:
```bash
# Mike needs to provide his Groq API key
# Get one free at https://console.groq.com
export GROQ_API_KEY="<mike-provides-this>"
```

Add to `~/.zshrc` for persistence:
```bash
echo 'export GROQ_API_KEY="<key>"' >> ~/.zshrc
```

**Step 4: Restart OpenClaw gateway and verify**

Run:
```bash
openclaw gateway restart
openclaw doctor
```

Expected: Doctor reports all models configured, no errors.

---

## Task 3: Add Susan Search Endpoint to FastAPI Bridge

**Files:**
- Modify: `~/Desktop/jake-assistant/server.py` (add `/api/susan/search` endpoint)
- Create: `~/Desktop/jake-assistant/connectors/susan.py` (Susan RAG connector)
- Test: `~/Desktop/jake-assistant/tests/test_susan.py`

**Step 1: Write the failing test**

Create `~/Desktop/jake-assistant/tests/__init__.py` (empty) and `~/Desktop/jake-assistant/tests/test_susan.py`:

```python
"""Tests for Susan RAG connector."""
import pytest
from unittest.mock import patch, MagicMock


def test_search_returns_results():
    """search_knowledge returns formatted results."""
    from connectors.susan import search_knowledge

    # Mock the Supabase RPC call
    mock_results = [
        {
            "content": "Oracle Health payer strategy focuses on CMS interop mandates.",
            "source": "oracle-health-research",
            "data_type": "business_strategy",
            "similarity": 0.92,
        }
    ]

    with patch("connectors.susan._call_susan_search", return_value=mock_results):
        result = search_knowledge("payer strategy", company_id="oracle-health", top_k=5)
        assert result["total"] >= 1
        assert result["results"][0]["similarity"] >= 0.8
        assert "payer" in result["results"][0]["content"].lower() or "oracle" in result["results"][0]["content"].lower()


def test_search_empty_query():
    """Empty query returns empty results."""
    from connectors.susan import search_knowledge

    with patch("connectors.susan._call_susan_search", return_value=[]):
        result = search_knowledge("", company_id="shared", top_k=5)
        assert result["total"] == 0
        assert result["results"] == []


def test_search_company_detection():
    """Company detection from query keywords."""
    from connectors.susan import detect_company

    assert detect_company("prior auth payer strategy") == "oracle-health"
    assert detect_company("transformfit user retention") == "transformfit"
    assert detect_company("susan agent architecture") == "founder-intelligence-os"
    assert detect_company("random question") == "shared"
```

**Step 2: Run test to verify it fails**

Run:
```bash
cd ~/Desktop/jake-assistant && python3 -m pytest tests/test_susan.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'connectors.susan'`

**Step 3: Write the Susan connector**

Create `~/Desktop/jake-assistant/connectors/susan.py`:

```python
"""Susan RAG connector — bridges OpenClaw to Susan's knowledge base."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Company detection keywords
COMPANY_KEYWORDS = {
    "oracle-health": [
        "oracle", "health", "cerner", "ehr", "emr", "epic", "fhir",
        "prior auth", "payer", "cms", "himss", "interop", "clinical",
        "patient", "provider", "hospital", "health system", "matt",
    ],
    "transformfit": [
        "transformfit", "fitness", "workout", "exercise", "training",
        "jacob", "recruiting", "alex", "coach", "athlete", "retention",
        "gym", "weight", "nutrition",
    ],
    "founder-intelligence-os": [
        "susan", "agent", "rag", "intelligence", "startup", "mcp",
        "openclaw", "jake", "birch", "chains", "trust", "v4",
        "architecture", "platform", "skill",
    ],
}

# Path to Susan's backend
SUSAN_BACKEND = Path.home() / "Startup-Intelligence-OS" / "susan-team-architect" / "backend"
SUSAN_VENV_PYTHON = SUSAN_BACKEND / ".venv" / "bin" / "python3"


def detect_company(query: str) -> str:
    """Detect which company the query is about from keywords."""
    query_lower = query.lower()
    scores = {}
    for company, keywords in COMPANY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[company] = score
    if not scores:
        return "shared"
    return max(scores, key=scores.get)


def _call_susan_search(
    query: str,
    company_id: str = "shared",
    data_types: list[str] | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Call Susan's search_company_knowledge via subprocess.

    This avoids importing Susan's full backend into the FastAPI process.
    Instead, we run a small Python script in Susan's venv.
    """
    script = f"""
import json, sys
sys.path.insert(0, "{SUSAN_BACKEND}")
from control_plane.protocols import search_company_knowledge
results = search_company_knowledge(
    query={json.dumps(query)},
    company_id={json.dumps(company_id)},
    data_types={json.dumps(data_types)},
    top_k={top_k},
)
print(json.dumps(results))
"""
    try:
        result = subprocess.run(
            [str(SUSAN_VENV_PYTHON), "-c", script],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(SUSAN_BACKEND),
        )
        if result.returncode != 0:
            return []
        return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return []


def search_knowledge(
    query: str,
    company_id: str = "shared",
    data_types: list[str] | None = None,
    top_k: int = 5,
) -> dict[str, Any]:
    """Search Susan's RAG knowledge base. Returns formatted results."""
    if not query.strip():
        return {"results": [], "total": 0, "company": company_id}

    results = _call_susan_search(
        query=query,
        company_id=company_id,
        data_types=data_types,
        top_k=top_k,
    )

    return {
        "results": results,
        "total": len(results),
        "company": company_id,
        "query": query,
    }


def format_for_telegram(results: dict[str, Any]) -> str:
    """Format search results for Telegram display."""
    if results["total"] == 0:
        return "No results found. Want me to do a deeper dig?"

    lines = []
    for i, r in enumerate(results["results"][:5], 1):
        content = r.get("content", "")[:200]
        source = r.get("source", "unknown")
        score = r.get("similarity", 0)
        confidence = "HIGH" if score >= 0.85 else "MEDIUM" if score >= 0.70 else "LOW"
        lines.append(f"{i}. [{confidence}] {content}...")
        lines.append(f"   Source: {source}")

    return "\n".join(lines)
```

**Step 4: Add the endpoint to server.py**

Add at the top of `~/Desktop/jake-assistant/server.py`, after the existing imports:

```python
from connectors import susan
```

Add before the final line of the file:

```python
@app.get("/api/susan/search")
async def susan_search(
    query: str = Query(..., description="Search query"),
    company: Optional[str] = Query(None, description="Company ID (auto-detected if omitted)"),
    data_types: Optional[str] = Query(None, description="Comma-separated data types"),
    limit: int = Query(5, ge=1, le=20),
):
    """Search Susan's RAG knowledge base."""
    # Auto-detect company if not provided
    company_id = company or susan.detect_company(query)

    # Parse data types
    dt_list = [d.strip() for d in data_types.split(",")] if data_types else None

    results = susan.search_knowledge(
        query=query,
        company_id=company_id,
        data_types=dt_list,
        top_k=limit,
    )
    return results


@app.get("/api/susan/search/telegram")
async def susan_search_telegram(
    query: str = Query(..., description="Search query"),
    company: Optional[str] = Query(None, description="Company ID"),
    limit: int = Query(5, ge=1, le=10),
):
    """Search Susan's RAG and format for Telegram."""
    company_id = company or susan.detect_company(query)
    results = susan.search_knowledge(query=query, company_id=company_id, top_k=limit)
    return {
        "formatted": susan.format_for_telegram(results),
        "company_detected": company_id,
        "total": results["total"],
    }
```

**Step 5: Run tests to verify they pass**

Run:
```bash
cd ~/Desktop/jake-assistant && python3 -m pytest tests/test_susan.py -v
```

Expected: 3/3 PASS

**Step 6: Test the endpoint manually**

Run:
```bash
# Restart FastAPI server
cd ~/Desktop/jake-assistant && source .venv/bin/activate
uvicorn server:app --host 127.0.0.1 --port 7842 --reload &

# Test search
curl -s "http://localhost:7842/api/susan/search?query=payer+strategy+prior+auth&limit=3" | python3 -m json.tool
```

Expected: JSON response with results from Susan's RAG.

**Step 7: Commit**

```bash
cd ~/Desktop/jake-assistant
git add connectors/susan.py tests/ server.py
git commit -m "feat: add Susan RAG search endpoint for OpenClaw bridge"
```

---

## Task 4: Build the `susan-rag-query` OpenClaw Skill

**Files:**
- Create: `~/clawd/skills/susan-rag-query/SKILL.md`

**Step 1: Create skill directory**

Run:
```bash
mkdir -p ~/clawd/skills/susan-rag-query
```

**Step 2: Write SKILL.md**

Create `~/clawd/skills/susan-rag-query/SKILL.md`:

```markdown
---
name: susan-rag-query
version: 1.0.0
description: "Query Susan's 94K-chunk knowledge base for sourced business answers. Covers Oracle Health, TransformFit, and Startup Intelligence OS. Say 'what do we know about X' or 'research X' or ask any strategy question."
author: Mike Rodgers
tags: [rag, knowledge, search, business, strategy, research, oracle-health, transformfit]
---

# Susan RAG Query

You have access to a powerful knowledge base with 94,143+ research chunks across 22 data types. Use it whenever the user asks a knowledge question, strategy question, or wants sourced information.

## When to Activate

Activate this skill when the user:
- Asks "what do we know about..." or "research..."
- Asks about strategy, competitors, market, or business decisions
- Mentions specific topics: prior auth, payer, FHIR, EHR, fitness, recruiting, agents, RAG
- Says "find me...", "look up...", "what's our position on..."
- Asks any question that could benefit from sourced, factual answers

## How to Search

Use the exec tool to query the local knowledge base:

```
curl -s "http://localhost:7842/api/susan/search?query=USER_QUERY_HERE&limit=5"
```

For Telegram-formatted output:
```
curl -s "http://localhost:7842/api/susan/search/telegram?query=USER_QUERY_HERE&limit=5"
```

You can also specify a company:
```
curl -s "http://localhost:7842/api/susan/search?query=USER_QUERY_HERE&company=oracle-health&limit=5"
```

Valid company IDs: `oracle-health`, `transformfit`, `founder-intelligence-os`, `shared`

## Company Detection

If no company is specified, the system auto-detects from keywords:
- **Oracle Health**: oracle, health, ehr, emr, epic, fhir, prior auth, payer, cms, clinical, hospital
- **TransformFit**: fitness, workout, exercise, training, jacob, recruiting, coach, athlete
- **Startup Intelligence OS**: susan, agent, rag, intelligence, platform, architecture

## Response Format

**CRITICAL: Keep responses SHORT. This is Telegram, not an essay.**

Format your response as:

1. **Direct answer** (2-3 sentences maximum)
2. **Key sources** (bullet list with source names)
3. **Confidence** indicator:
   - HIGH: similarity scores >= 0.85
   - MEDIUM: similarity scores 0.70-0.84
   - LOW: similarity scores < 0.70

Example response:
```
Our payer strategy centers on CMS interoperability mandates (2026 deadline) forcing FHIR-based prior auth adoption. Oracle Health's angle: pre-built PA workflows that cut payer admin costs 30-40%.

Sources:
• CMS Prior Auth Final Rule (business_strategy)
• Competitor Analysis: Epic PA Module (market_research)
• Internal Strategy Brief 2026-03 (operational_protocols)

Confidence: HIGH
```

## Rules

1. **Always search before answering** knowledge questions. Never guess or make up information.
2. **Cite your sources.** Every factual claim must reference the source chunk.
3. **Oracle Health compliance**: NEVER include email bodies. Subject lines only. No PHI.
4. **Low confidence**: If results are LOW confidence, say so: "I found some related info but I'm not super confident. Want me to do a deeper dig?"
5. **No results**: If nothing comes back, say: "Nothing in the knowledge base on that. Want me to kick off a research task?"
6. **Be Jake**: You're still Jake. Be concise, be direct, add a comment if relevant. Don't be a corporate robot.
```

**Step 3: Verify skill is visible to OpenClaw**

Run:
```bash
openclaw skills list 2>/dev/null | grep susan || ls ~/clawd/skills/susan-rag-query/SKILL.md
```

Expected: Skill file exists and is discoverable.

---

## Task 5: Build the `company-context` OpenClaw Skill

**Files:**
- Create: `~/clawd/skills/company-context/SKILL.md`

**Step 1: Create skill directory**

Run:
```bash
mkdir -p ~/clawd/skills/company-context
```

**Step 2: Write SKILL.md**

Create `~/clawd/skills/company-context/SKILL.md`:

```markdown
---
name: company-context
version: 1.0.0
description: "Automatically detect which company Mike is asking about and load relevant context. Supports Oracle Health, TransformFit, and Startup Intelligence OS."
author: Mike Rodgers
tags: [context, company, multi-company, oracle-health, transformfit, startup-ios]
---

# Company Context Detector

Mike operates three companies. You must always be aware of which one he's asking about.

## The Three Companies

### Oracle Health AI Enablement
- **What**: Healthcare IT strategy for Oracle Health (Mike's employer)
- **Key people**: Matt Cohlmia (exec stakeholder), Berat (team)
- **Topics**: EHR, EMR, FHIR, prior auth, payer strategy, CMS mandates, clinical workflows, interoperability
- **Compliance**: Email bodies NEVER sent through you. Subject lines only. No PHI. Ever.
- **Trigger words**: oracle, health, ehr, emr, epic, fhir, prior auth, payer, cms, himss, clinical, patient, provider, hospital, health system, matt, berat

### TransformFit
- **What**: Fitness app (Alex Recruiting is the recruiting sub-project for Jacob)
- **Key people**: Jacob (Mike's son, plays OL/DL football), recruiting coaches
- **Topics**: User retention, workout programming, coaching, recruiting outreach, athlete profiles
- **Trigger words**: transformfit, fitness, workout, exercise, training, jacob, recruiting, alex, coach, athlete, gym, nutrition

### Startup Intelligence OS
- **What**: The meta-platform powering everything (Susan, Jake, RAG, agents)
- **Topics**: Agent architecture, RAG, Susan, capabilities, platform engineering
- **Trigger words**: susan, agent, rag, intelligence, startup, mcp, openclaw, jake, birch, chains, trust, platform, skill

## How to Use

When Mike sends a message:
1. Identify which company it's about (often obvious from keywords)
2. If ambiguous, ask: "Is this an Oracle Health thing, TransformFit, or the platform?"
3. Load relevant context from memory before answering
4. ALWAYS respect Oracle Health compliance boundaries

## Cross-Company Patterns

Sometimes Mike asks about patterns that span companies:
- "How does the outreach cadence from Alex Recruiting apply to Oracle Health?"
- "Can we use Susan's agent pattern for the fitness app?"

In these cases, reference both companies and highlight the connection.
```

---

## Task 6: Seed OpenClaw Memory with Cross-Company Context

**Files:**
- Create: `~/clawd/workspace/memory/companies/oracle-health.md`
- Create: `~/clawd/workspace/memory/companies/transformfit.md`
- Create: `~/clawd/workspace/memory/companies/startup-ios.md`
- Create: `~/clawd/workspace/memory/people/jacob.md`
- Create: `~/clawd/workspace/memory/preferences/mike-profile.md`

**Step 1: Create memory directory structure**

Run:
```bash
mkdir -p ~/clawd/workspace/memory/{companies,people,preferences,conversations,knowledge}
```

**Step 2: Seed Oracle Health context**

Create `~/clawd/workspace/memory/companies/oracle-health.md`:

```markdown
# Oracle Health AI Enablement

Mike works at Oracle Health. This is his day job.

## Strategy
- Focused on AI enablement for Oracle Health's EHR platform
- Key opportunity: CMS interoperability mandates driving FHIR-based prior auth adoption
- Competitive landscape: Epic, Cerner (legacy Oracle), athenahealth

## Key People
- **Matt Cohlmia** — Executive stakeholder, key decision maker
- **Berat** — Team member, technical

## Compliance Boundaries (NON-NEGOTIABLE)
- Email bodies NEVER get processed through Jake/OpenClaw
- Subject lines only
- No PHI (Protected Health Information) ever
- No patient data
- This is a compliance boundary, not a preference

## Active Initiatives
- Prior auth workflow automation
- Payer space entry strategy
- AI-powered clinical decision support
```

**Step 3: Seed TransformFit context**

Create `~/clawd/workspace/memory/companies/transformfit.md`:

```markdown
# TransformFit

Fitness application with recruiting sub-project (Alex Recruiting) for Jacob.

## Product
- Fitness app focused on user retention and workout programming
- Alex Recruiting: specialized recruiting tool for Jacob's football recruiting

## Key People
- **Jacob** — Mike's son, plays OL and DL in football, actively being recruited
- Recruiting coaches are key outreach targets

## Current Focus
- Phase 5 polish on Alex Recruiting
- User retention optimization
- Coach outreach cadence
```

**Step 4: Seed Startup Intelligence OS context**

Create `~/clawd/workspace/memory/companies/startup-ios.md`:

```markdown
# Startup Intelligence OS

The meta-platform that powers everything. Susan is the capability foundry.

## Architecture
- 73 Susan agents across 9 groups
- 94,143 RAG chunks across 22+ data types
- V4a complete: Chains, Birch, Trust modules (41/41 tests)
- KIRA (intent router), ARIA (daily briefs), LEDGER (funnel tracking)
- 30 scheduled tasks running

## Current State
- V4a merged to main
- V4b planned: real agent dispatch, Firehose SSE, trust graduation
- OpenClaw intelligence migration in progress (this project)

## Key Systems
- Susan MCP Server (7 tools)
- Supabase (persistence + vector search)
- Voyage AI embeddings (1024 dimensions)
```

**Step 5: Seed Jacob context**

Create `~/clawd/workspace/memory/people/jacob.md`:

```markdown
# Jacob

Mike's son. Plays offensive line (OL) and defensive line (DL) in football. Currently being actively recruited by colleges. Mike cares deeply about Jacob's progress — always ask how his games/practice went.
```

**Step 6: Seed Mike's profile**

Create `~/clawd/workspace/memory/preferences/mike-profile.md`:

```markdown
# Mike Rodgers — Profile

## Communication Style
- Prefers concise, direct answers (this is Telegram)
- Hates trailing summaries after every response
- Thinks in agent teams and system architectures
- Likes comprehensive automated solutions
- Gets excited about ideas and sometimes needs to be reined in (that's Jake's job)

## Work Patterns
- Morning: brief review and priorities
- Afternoon: deep work
- Evening: wind down, lighter tasks
- Late night sessions happen but shouldn't be encouraged

## Pet Peeves
- Sycophancy (don't agree just to agree)
- Overcomplication when simple works
- Building before planning
- Ignoring tech debt

## Personal
- Lives in the US
- Works at Oracle Health (day job)
- Building companies on the side
- Cares deeply about Jacob's football and recruiting
```

**Step 7: Verify memory is populated**

Run:
```bash
find ~/clawd/workspace/memory -name "*.md" | sort
```

Expected: 5 markdown files across companies/, people/, preferences/ directories.

---

## Task 7: Wire Daily Brief to Telegram

**Files:**
- Create: `~/clawd/skills/daily-brief-push/SKILL.md`

**Step 1: Create skill directory**

Run:
```bash
mkdir -p ~/clawd/skills/daily-brief-push
```

**Step 2: Write SKILL.md**

Create `~/clawd/skills/daily-brief-push/SKILL.md`:

```markdown
---
name: daily-brief-push
version: 1.0.0
description: "Push a morning intelligence brief combining calendar, company priorities, and Susan signals. Triggered by 'briefing' or scheduled via cron."
author: Mike Rodgers
tags: [briefing, daily, morning, intelligence, calendar, priorities]
---

# Daily Intelligence Brief

Generate a morning brief that combines personal calendar, company priorities, and intelligence signals.

## When to Activate

- User says "briefing", "morning brief", "what's today look like"
- Scheduled via cron at 6:30 AM

## How to Generate

### Step 1: Pull calendar
```
curl -s http://localhost:7842/api/calendar/today
```

### Step 2: Pull recent Susan signals (if available)
```
curl -s "http://localhost:7842/api/susan/search?query=latest+signals+alerts&limit=3"
```

### Step 3: Check system status
```
curl -s http://localhost:7842/api/system/battery
```

### Step 4: Format the brief

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAILY BRIEF — [Day], [Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CALENDAR
• [Time] — [Event] (company context if relevant)
• [Time] — [Event]

PRIORITIES
1. [Top priority from memory/context]
2. [Second priority]
3. [Third priority]

SIGNALS (from Susan)
• [Any competitive signals or alerts]
• [Any relevant research findings]

SYSTEM
• Battery: [X]%
• [Any system alerts]

ONE THING TODAY
[What matters most — one sentence]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Rules
- Keep it SHORT. This is a Telegram message, not a report.
- Lead with calendar — Mike needs to know what's on deck.
- Only include signals if they're actually relevant today.
- Battery only if below 30%.
- The "ONE THING" is the most important — make it count.
```

---

## Task 8: End-to-End Integration Test

**Step 1: Verify all services are running**

Run:
```bash
# Check Ollama
curl -s http://127.0.0.1:11434/v1/models | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"

# Check FastAPI
curl -s http://localhost:7842/api/status | python3 -m json.tool

# Check OpenClaw
curl -s -H "Authorization: Bearer 6780a038b8977368609b9d21566140dae01301f6d7ea5965" http://localhost:7841/api/health 2>/dev/null || echo "Check OpenClaw gateway"
```

**Step 2: Test Susan search via FastAPI**

Run:
```bash
curl -s "http://localhost:7842/api/susan/search?query=payer+strategy+prior+auth&limit=3" | python3 -m json.tool
```

Expected: JSON with results from Susan's RAG, auto-detected company "oracle-health".

**Step 3: Test Telegram-formatted search**

Run:
```bash
curl -s "http://localhost:7842/api/susan/search/telegram?query=user+retention+fitness&limit=3" | python3 -m json.tool
```

Expected: JSON with `formatted` field containing Telegram-friendly text, company "transformfit".

**Step 4: Test via Telegram (manual)**

Open Telegram, message @BirchRodgersbot:
> "What do we know about the payer space strategy for Oracle Health?"

Expected: Jake responds with sourced answer from Susan's RAG, short and concise, with source citations.

**Step 5: Test daily brief via Telegram**

Message @BirchRodgersbot:
> "briefing"

Expected: Formatted daily brief with calendar + priorities + signals.

---

## Task 9: Commit and Checkpoint

**Step 1: Commit jake-assistant changes**

```bash
cd ~/Desktop/jake-assistant
git add -A
git commit -m "feat: add Susan RAG bridge, company context, and intelligence skills"
```

**Step 2: Commit OpenClaw skills to Startup Intelligence OS**

```bash
cd ~/Startup-Intelligence-OS
# Copy skills for version control
mkdir -p .startup-os/openclaw-skills
cp -r ~/clawd/skills/susan-rag-query .startup-os/openclaw-skills/
cp -r ~/clawd/skills/company-context .startup-os/openclaw-skills/
cp -r ~/clawd/skills/daily-brief-push .startup-os/openclaw-skills/
git add .startup-os/openclaw-skills/ docs/plans/2026-03-19-*.md
git commit -m "feat(openclaw): Phase 1 skills — RAG query, company context, daily brief"
```

**Step 3: Verify checkpoint**

Run:
```bash
cd ~/Startup-Intelligence-OS && git log --oneline -3
cd ~/Desktop/jake-assistant && git log --oneline -3
```

Expected: Clean commits in both repos.

---

## Summary — Phase 1 Deliverables

| # | Deliverable | Status Check |
|---|------------|-------------|
| 1 | Ollama installed, 2 local models running | `ollama list` shows llama3.2:8b and 3b |
| 2 | OpenClaw model routing configured | `~/.openclaw/openclaw.json` has tiered agents |
| 3 | Susan RAG search endpoint on FastAPI | `curl localhost:7842/api/susan/search?query=test` returns results |
| 4 | `susan-rag-query` skill installed | `ls ~/clawd/skills/susan-rag-query/SKILL.md` |
| 5 | `company-context` skill installed | `ls ~/clawd/skills/company-context/SKILL.md` |
| 6 | OpenClaw memory seeded | 5 markdown files in `~/clawd/workspace/memory/` |
| 7 | `daily-brief-push` skill installed | `ls ~/clawd/skills/daily-brief-push/SKILL.md` |
| 8 | End-to-end Telegram test passes | Ask a question on Telegram, get sourced answer |

**After Phase 1:** Mike can open Telegram, ask "What's our payer strategy?" and get a sourced, concise answer from Susan's 94K-chunk knowledge base in under 8 seconds.

---

## Next Plans (Separate Sessions)

- **Phase 2: V4b Engine Wiring** — `docs/plans/2026-03-19-v4b-engine-wiring.md` (to be written)
- **Phase 3: Intelligence Layer** — competitive alerts, proactive monitoring, meeting prep
- **Phase 4: Mastery** — KIRA/ARIA/LEDGER migration to OpenClaw native
