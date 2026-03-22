"""Meeting Orchestrator — The "I already did the work for your meeting" engine.

Architecture:
  1. Extract context from calendar event (attendees, topic, meeting type)
  2. Classify meeting type → match or auto-create a recipe
  3. Spawn Claude Code with live MCP research prompts (Exa, Firecrawl, Susan)
  4. Run Susan agents for strategic deliverables
  5. Save docs to docs/meeting-prep/{date}-{slug}/
  6. Send detailed Telegram brief
  7. Store episode in brain memory

Usage (from nervous daemon):
  orchestrator = MeetingOrchestrator()
  orchestrator.orchestrate(calendar_event)

Usage (CLI):
  python scripts/jake_meeting_orchestrator.py run --event-json '{"summary": "..."}'
  python scripts/jake_meeting_orchestrator.py test
  python scripts/jake_meeting_orchestrator.py upcoming
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

CLAUDE_CLI = "/Users/mikerodgers/.local/bin/claude"
STARTUP_OS_DIR = Path("/Users/mikerodgers/Startup-Intelligence-OS")
BACKEND_DIR = STARTUP_OS_DIR / "susan-team-architect" / "backend"
RECIPES_DIR = Path.home() / ".hermes" / "recipes"
MEETING_PREP_DIR = STARTUP_OS_DIR / "docs" / "meeting-prep"
CLAUDE_TIMEOUT = 300  # 5 minutes per research call
CLAUDE_BUDGET = "4.00"  # per meeting

# Meeting type → recipe file mapping
MEETING_TYPE_MAP = {
    "deal": "deal-analysis",
    "win": "deal-analysis",
    "loss": "deal-analysis",
    "meddpicc": "deal-analysis",
    "battlecard": "oracle-battlecard-update",
    "competitive": "oracle-battlecard-update",
    "standup": "weekly-standup",
    "sync": "partner-sync",
    "review": "exec-review",
    "partner": "partner-sync",
    "exec": "exec-briefing",
    "executive": "exec-briefing",
    "brief": "exec-briefing",
    "research": "morning-research",
    "intel": "morning-research",
}

# Susan agents most useful for meeting prep
SUSAN_MEETING_AGENTS = {
    "deal-analysis": ["steve", "freya", "atlas"],
    "partner-sync": ["steve", "bridge", "marcus"],
    "exec-briefing": ["steve", "compass", "herald"],
    "oracle-battlecard-update": ["sentinel", "nova", "pulse"],
    "weekly-standup": ["compass", "forge"],
    "exec-review": ["steve", "ledger", "compass"],
    "default": ["steve", "compass"],
}


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class MeetingContext:
    """Normalized meeting context extracted from a calendar event."""
    event_id: str
    summary: str
    start: str
    minutes_left: float
    location: str = ""
    description: str = ""
    attendees: list[str] = field(default_factory=list)
    hangout: str = ""
    source: str = "google"
    meeting_type: str = "general"
    keywords: list[str] = field(default_factory=list)
    slug: str = ""
    output_dir: Path = field(default_factory=lambda: MEETING_PREP_DIR)

    def __post_init__(self):
        if not self.slug:
            self.slug = _slugify(self.summary)
        today = datetime.now().strftime("%Y-%m-%d")
        self.output_dir = MEETING_PREP_DIR / f"{today}-{self.slug}"


@dataclass
class ResearchResult:
    """Output from one research phase."""
    phase: str      # "attendees", "topic", "competitive", "agents"
    content: str
    success: bool = True
    error: str = ""
    tokens_used: int = 0


@dataclass
class PrepPackage:
    """Complete meeting prep package."""
    context: MeetingContext
    research: list[ResearchResult] = field(default_factory=list)
    deliverables: dict[str, Path] = field(default_factory=dict)  # name → file path
    telegram_brief: str = ""
    brain_episode_id: str = ""
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:40]


def _run_claude(prompt: str, timeout: int = CLAUDE_TIMEOUT, budget: str = CLAUDE_BUDGET) -> str:
    """Run Claude Code CLI synchronously and return output text.

    Claude Code uses its MCP tools (Exa, Firecrawl, Susan Intelligence) for live research.
    This is the ONLY way we do research — no training data, no hallucination.
    """
    cmd = [
        CLAUDE_CLI,
        "-p", prompt,
        "--model", "sonnet",
        "--output-format", "text",
        "--max-budget-usd", budget,
        "--no-session-persistence",
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(STARTUP_OS_DIR),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            logger.warning("Claude CLI error (exit %d): %s", result.returncode, err[:200])
            return f"[Claude error exit {result.returncode}]: {err[:200]}"
        output = result.stdout.strip()
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        logger.error("Claude CLI timed out after %ds", timeout)
        return f"[Timeout after {timeout}s]"
    except Exception as exc:
        logger.error("Claude CLI failed: %s", exc)
        return f"[Error: {exc}]"


def _run_susan_agent(agent_name: str, task: str) -> str:
    """Run a Susan agent via the MCP server's run_agent endpoint."""
    try:
        import httpx
        resp = httpx.post(
            "http://localhost:8765/run_agent",
            json={"agent": agent_name, "task": task},
            timeout=120,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("result", data.get("output", str(data)))
        return f"[Susan {agent_name} HTTP {resp.status_code}]"
    except Exception:
        # Fall back: spawn Claude with Susan agent context inline
        prompt = f"""You are Susan's {agent_name} agent. Complete this task with your expertise.

Task: {task}

Provide a concise, actionable response. Use any available MCP tools for live research.
Keep response under 400 words."""
        return _run_claude(prompt, timeout=60, budget="1.00")


def _send_telegram(text: str) -> bool:
    """Send Telegram message via env vars."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        logger.warning("Telegram not configured — TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing")
        return False
    import urllib.request
    try:
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception as exc:
        logger.error("Telegram failed: %s", exc)
        return False


def _store_in_brain(context: MeetingContext, package: PrepPackage) -> str:
    """Store meeting prep episode in Jake's brain."""
    try:
        sys.path.insert(0, str(BACKEND_DIR))
        from jake_brain.store import BrainStore
        store = BrainStore()

        summary_parts = [f"Meeting prep: {context.summary}"]
        for r in package.research:
            if r.success and r.content and not r.content.startswith("["):
                summary_parts.append(f"\n## {r.phase.upper()}\n{r.content[:500]}")

        episode_id = store.add_episodic(
            content="\n".join(summary_parts),
            summary=f"Meeting prep delivered for: {context.summary}",
            people=[a.split("@")[0] for a in context.attendees if "@" in a],
            tags=["meeting-prep", context.meeting_type] + context.keywords[:3],
            source="meeting_orchestrator",
        )
        return episode_id or ""
    except Exception as exc:
        logger.warning("Brain store failed: %s", exc)
        return ""


# ── Main Orchestrator ─────────────────────────────────────────────────────────

class MeetingOrchestrator:
    """Full autonomous meeting prep — research, deliverables, Telegram brief, brain storage."""

    def __init__(self):
        MEETING_PREP_DIR.mkdir(parents=True, exist_ok=True)

    # ── Context extraction ────────────────────────────────────────────────

    def extract_context(self, event: dict[str, Any], minutes_left: float) -> MeetingContext:
        """Build MeetingContext from a raw calendar event dict."""
        summary = event.get("summary", "Untitled Meeting")
        keywords = self._extract_keywords(summary, event.get("description", ""))
        meeting_type = self._classify_type(summary, keywords, event.get("attendees", []))

        return MeetingContext(
            event_id=event.get("id", _slugify(summary)),
            summary=summary,
            start=event.get("start", ""),
            minutes_left=minutes_left,
            location=event.get("location", ""),
            description=(event.get("description", "") or "")[:300],
            attendees=event.get("attendees", []),
            hangout=event.get("hangout", ""),
            source=event.get("source", "google"),
            meeting_type=meeting_type,
            keywords=keywords,
        )

    def _extract_keywords(self, summary: str, description: str) -> list[str]:
        """Extract meaningful keywords from meeting title and description."""
        text = f"{summary} {description}".lower()
        # Oracle-specific patterns
        oracle_terms = ["oracle", "health", "meddpicc", "deal", "battlecard", "epic",
                        "cerner", "ehr", "interop", "tefca", "rcm", "payer", "provider"]
        # General business terms
        biz_terms = ["competitive", "partner", "exec", "review", "standup", "q1", "q2",
                     "q3", "q4", "budget", "roadmap", "strategy", "ai", "ml"]

        found = []
        for term in oracle_terms + biz_terms:
            if term in text:
                found.append(term)

        # Also extract capitalized proper nouns from summary (company names, person names)
        words = re.findall(r"\b[A-Z][a-z]{2,}\b", summary)
        found.extend([w.lower() for w in words[:3]])

        return list(dict.fromkeys(found))[:8]  # dedupe, max 8

    def _classify_type(self, summary: str, keywords: list[str], attendees: list[str]) -> str:
        """Classify meeting type from title and keywords."""
        text = summary.lower()
        for kw, recipe in MEETING_TYPE_MAP.items():
            if kw in text or kw in keywords:
                return recipe
        # Attendee-based heuristics
        if any("oracle" in a.lower() for a in attendees):
            return "exec-briefing"
        if attendees and len(attendees) > 5:
            return "weekly-standup"
        return "exec-briefing"  # safe default

    # ── Recipe matching ───────────────────────────────────────────────────

    def match_recipe(self, context: MeetingContext) -> dict[str, Any] | None:
        """Find the best matching recipe for this meeting type."""
        # 1. Try exact match by meeting type
        recipe_file = RECIPES_DIR / f"{context.meeting_type}.yaml"
        if recipe_file.exists():
            try:
                import yaml
                with open(recipe_file) as f:
                    return yaml.safe_load(f)
            except Exception:
                pass

        # 2. Try keyword match
        for kw in context.keywords:
            for recipe_name, rtype in MEETING_TYPE_MAP.items():
                if kw == recipe_name:
                    recipe_file = RECIPES_DIR / f"{rtype}.yaml"
                    if recipe_file.exists():
                        try:
                            import yaml
                            with open(recipe_file) as f:
                                return yaml.safe_load(f)
                        except Exception:
                            pass
        return None

    def auto_create_recipe(self, context: MeetingContext) -> dict[str, Any]:
        """Generate a recipe dynamically based on meeting context."""
        agents = SUSAN_MEETING_AGENTS.get(context.meeting_type, SUSAN_MEETING_AGENTS["default"])
        return {
            "name": f"auto-{context.meeting_type}",
            "description": f"Auto-generated prep for: {context.summary}",
            "version": "auto",
            "tags": [context.meeting_type] + context.keywords[:3],
            "steps": [
                {"name": "Attendee research", "phase": "attendees"},
                {"name": "Topic research", "phase": "topic"},
                {"name": "Competitive landscape", "phase": "competitive"},
                {"name": "Susan strategic analysis", "phase": "agents", "agents": agents},
            ],
        }

    # ── Research phases ───────────────────────────────────────────────────

    def research_attendees(self, context: MeetingContext) -> ResearchResult:
        """Research each attendee: role, company, recent news, LinkedIn activity."""
        if not context.attendees:
            return ResearchResult(
                phase="attendees",
                content="No attendees listed in calendar event.",
                success=True,
            )

        attendee_list = "\n".join(f"- {a}" for a in context.attendees[:8])

        prompt = f"""Research these meeting attendees for an upcoming meeting in ~{int(context.minutes_left)} minutes.

MEETING: {context.summary}
ATTENDEES:
{attendee_list}

For each attendee with an email, research:
1. Their current role and company (from their email domain and any public info)
2. Recent LinkedIn activity or public announcements (last 30 days)
3. Any news about their company in the last 30 days
4. Their likely agenda/priorities for this meeting

CRITICAL: Use only live MCP research tools — DO NOT rely on your training data:
- Use mcp__tavily__tavily_search or mcp__tavily__tavily_research for web searches
- Use mcp__firecrawl__firecrawl_search for specific company pages
- Search for each attendee's full name + company + recent news

Format output as:
## [Attendee Email]
**Role**: ...
**Company context**: ...
**Recent news**: ...
**Likely agenda**: ...

Keep each attendee section under 150 words. Lead with the most important insight."""

        content = _run_claude(prompt)
        return ResearchResult(phase="attendees", content=content, success=not content.startswith("["))

    def research_topic(self, context: MeetingContext) -> ResearchResult:
        """Research the meeting topic: market data, recent developments, context."""
        keywords_str = ", ".join(context.keywords) if context.keywords else context.summary

        prompt = f"""Research this meeting topic for prep in ~{int(context.minutes_left)} minutes.

MEETING: {context.summary}
DESCRIPTION: {context.description or "No description provided"}
KEY TOPICS: {keywords_str}

Research (using ONLY live MCP tools — no training data):
1. Recent news about these topics (last 7 days) — use mcp__tavily__tavily_search
2. Relevant market data, analyst reports, or benchmarks — use mcp__tavily__tavily_research
3. Any notable announcements from key players (Oracle, Epic, Microsoft Health, Google Health if relevant)
4. Key stats or data points Mike should have ready

Format as:
## Recent Developments
[Top 3 news items with source and date]

## Key Data Points
[3-5 stats/benchmarks that might come up]

## What to Watch For
[2-3 things this meeting might hinge on]

Stay factual. Use live search. Under 400 words total."""

        content = _run_claude(prompt)
        return ResearchResult(phase="topic", content=content, success=not content.startswith("["))

    def research_competitive(self, context: MeetingContext) -> ResearchResult:
        """Research competitive landscape relevant to this meeting."""
        # Only do competitive research for relevant meeting types
        if context.meeting_type not in ("deal-analysis", "oracle-battlecard-update",
                                         "exec-briefing", "exec-review", "partner-sync"):
            return ResearchResult(
                phase="competitive",
                content="Competitive research skipped (not applicable for this meeting type).",
                success=True,
            )

        oracle_context = "oracle" in " ".join(context.keywords)
        competitor_focus = "Oracle Health competitors (Epic, Cerner legacy, Microsoft Health, AWS HealthLake)" if oracle_context else "key market players"

        prompt = f"""Research competitive landscape for this meeting: {context.summary}

Focus areas: {competitor_focus}
Topics: {", ".join(context.keywords[:5])}

Using LIVE MCP research only (mcp__tavily__tavily_search, mcp__firecrawl__firecrawl_search):
1. Latest moves by {competitor_focus} in the last 30 days
2. Any announcements, partnerships, or product launches relevant to this meeting
3. Pricing intelligence or positioning changes (if available publicly)
4. What the competition will likely say against Oracle/Mike's position

Format as:
## Competitor Moves (Last 30 Days)
[2-3 bullets with sources]

## Positioning Intel
[What they're saying in market]

## Counter-Arguments Mike Should Have Ready
[2-3 specific responses]

Under 350 words. Only cite real, recent sources."""

        content = _run_claude(prompt)
        return ResearchResult(phase="competitive", content=content, success=not content.startswith("["))

    def run_susan_agents(self, context: MeetingContext, recipe: dict[str, Any]) -> ResearchResult:
        """Run Susan's specialist agents for strategic deliverables."""
        agents = SUSAN_MEETING_AGENTS.get(context.meeting_type, SUSAN_MEETING_AGENTS["default"])

        # Build agent task
        agent_task = f"""Meeting: {context.summary}
Type: {context.meeting_type}
Attendees: {", ".join(context.attendees[:5]) if context.attendees else "Not specified"}
Keywords: {", ".join(context.keywords[:5])}
Description: {context.description or "None"}
Time until meeting: ~{int(context.minutes_left)} minutes

Provide Mike's strategic prep:
1. Top 3 talking points (opening strong)
2. Key questions to ask
3. Win conditions (what does success look like for this meeting)
4. Risk flags (what could go wrong, how to handle it)
5. Recommended follow-up actions to create after the meeting

Be direct and actionable. Mike has {int(context.minutes_left)} minutes. Under 400 words."""

        # Try primary agent, fall back to default claude if all fail
        results_parts = []
        primary_agent = agents[0] if agents else "steve"

        agent_output = _run_susan_agent(primary_agent, agent_task)
        if not agent_output.startswith("["):
            results_parts.append(f"## Strategic Analysis (via {primary_agent})\n{agent_output}")
        else:
            # Direct Claude fallback
            fallback_prompt = f"""You are Jake, Mike's AI co-founder. Prepare a meeting brief.

{agent_task}

Focus on what matters most in the next {int(context.minutes_left)} minutes. Be direct."""
            fallback = _run_claude(fallback_prompt, timeout=60, budget="1.00")
            results_parts.append(f"## Strategic Brief\n{fallback}")

        content = "\n\n".join(results_parts) if results_parts else "Agent analysis unavailable."
        return ResearchResult(phase="agents", content=content, success=bool(results_parts))

    # ── Deliverables ──────────────────────────────────────────────────────

    def save_deliverables(self, package: PrepPackage) -> dict[str, Path]:
        """Write research phases to files in the output directory."""
        context = package.context
        output_dir = context.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        deliverables: dict[str, Path] = {}

        # Master brief
        brief_path = output_dir / "BRIEF.md"
        brief_lines = [
            f"# Meeting Prep: {context.summary}",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Type**: {context.meeting_type}",
            f"**Starts in**: ~{int(context.minutes_left)} minutes",
        ]
        if context.attendees:
            brief_lines.append(f"**Attendees**: {', '.join(context.attendees[:6])}")
        if context.hangout:
            brief_lines.append(f"**Join**: {context.hangout}")
        brief_lines.append(f"\n---\n")

        for result in package.research:
            if result.success and result.content and not result.content.startswith("["):
                phase_title = {
                    "attendees": "Attendee Intelligence",
                    "topic": "Topic Research",
                    "competitive": "Competitive Landscape",
                    "agents": "Strategic Analysis",
                }.get(result.phase, result.phase.title())

                brief_lines.append(f"## {phase_title}\n")
                brief_lines.append(result.content)
                brief_lines.append("\n---\n")

                # Also save individual phase files
                phase_path = output_dir / f"{result.phase}.md"
                phase_path.write_text(f"# {phase_title}\n\n{result.content}")
                deliverables[result.phase] = phase_path

        brief_path.write_text("\n".join(brief_lines))
        deliverables["brief"] = brief_path
        logger.info("Saved %d deliverables to %s", len(deliverables), output_dir)
        return deliverables

    # ── Telegram brief ────────────────────────────────────────────────────

    def build_telegram_brief(self, package: PrepPackage) -> str:
        """Format a Telegram message: punchy summary of prep work done."""
        context = package.context
        lines = [
            f"📋 *Meeting Prep Ready* — {context.summary}",
            f"⏱ Starts in ~{int(context.minutes_left)} min",
        ]

        if context.hangout:
            lines.append(f"🔗 [Join]({context.hangout})")

        # Research phases summary
        phases_done = [r.phase for r in package.research if r.success and not r.content.startswith("[")]
        if phases_done:
            phase_labels = {
                "attendees": "Attendee intel",
                "topic": "Topic research",
                "competitive": "Competitive landscape",
                "agents": "Strategic analysis",
            }
            done_str = " · ".join(phase_labels.get(p, p) for p in phases_done)
            lines.append(f"\n✅ *Completed*: {done_str}")

        # Pull out first 2 talking points from agent analysis if present
        agent_result = next((r for r in package.research if r.phase == "agents" and r.success), None)
        if agent_result and "talking point" in agent_result.content.lower():
            # Extract first bullet after "talking points" header
            tp_match = re.search(
                r"[Tt]alking [Pp]oints?.*?\n((?:[-•*\d].*\n?){1,3})",
                agent_result.content
            )
            if tp_match:
                lines.append(f"\n💬 *Top talking points*:\n{tp_match.group(1).strip()}")

        # Output location
        if package.deliverables.get("brief"):
            brief_path = package.deliverables["brief"]
            lines.append(f"\n📁 `{brief_path.relative_to(STARTUP_OS_DIR)}`")

        lines.append("\n_Full prep package ready. Ask Jake for any section._")
        return "\n".join(lines)

    # ── Main orchestration entry point ────────────────────────────────────

    def orchestrate(self, event: dict[str, Any], minutes_left: float) -> PrepPackage:
        """Full autonomous meeting prep. Call this from the nervous daemon.

        Returns a PrepPackage with all research, deliverables, and brief.
        Runs synchronously — caller should thread this if needed.
        """
        logger.info("Orchestrating meeting prep: %s (%.0f min away)",
                    event.get("summary", "?"), minutes_left)

        # 1. Extract context
        context = self.extract_context(event, minutes_left)
        package = PrepPackage(context=context)
        logger.info("Meeting type: %s | Keywords: %s", context.meeting_type, context.keywords)

        # 2. Match or create recipe
        recipe = self.match_recipe(context) or self.auto_create_recipe(context)
        logger.info("Using recipe: %s", recipe.get("name", "auto"))

        # 3. Research phases (sequential — each informs the next)
        # Phase A: Attendees
        logger.info("Phase A: Attendee research...")
        attendee_result = self.research_attendees(context)
        package.research.append(attendee_result)
        logger.info("Attendee research: %s (%d chars)",
                    "OK" if attendee_result.success else "FAILED", len(attendee_result.content))

        # Phase B: Topic
        logger.info("Phase B: Topic research...")
        topic_result = self.research_topic(context)
        package.research.append(topic_result)
        logger.info("Topic research: %s (%d chars)",
                    "OK" if topic_result.success else "FAILED", len(topic_result.content))

        # Phase C: Competitive (only for relevant types)
        logger.info("Phase C: Competitive research...")
        competitive_result = self.research_competitive(context)
        package.research.append(competitive_result)

        # Phase D: Susan agents / strategic analysis
        logger.info("Phase D: Susan agent analysis...")
        agent_result = self.run_susan_agents(context, recipe)
        package.research.append(agent_result)
        logger.info("Agent analysis: %s (%d chars)",
                    "OK" if agent_result.success else "FAILED", len(agent_result.content))

        # 4. Save deliverables
        logger.info("Saving deliverables...")
        package.deliverables = self.save_deliverables(package)

        # 5. Build and send Telegram brief
        package.telegram_brief = self.build_telegram_brief(package)
        sent = _send_telegram(package.telegram_brief)
        logger.info("Telegram brief sent: %s", sent)

        # 6. Store in brain
        episode_id = _store_in_brain(context, package)
        package.brain_episode_id = episode_id
        package.completed_at = datetime.now(timezone.utc).isoformat()

        logger.info(
            "Meeting prep complete — %d phases, %d deliverables, brain_id=%s",
            len(package.research),
            len(package.deliverables),
            episode_id or "none",
        )
        return package

    def orchestrate_background(self, event: dict[str, Any], minutes_left: float) -> threading.Thread:
        """Run orchestration in a background thread. Returns the thread."""
        def _run():
            try:
                # Load env from ~/.hermes/.env
                env_file = Path.home() / ".hermes" / ".env"
                if env_file.exists():
                    for line in env_file.read_text().splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, _, v = line.partition("=")
                            os.environ.setdefault(k.strip(), v.strip())
                self.orchestrate(event, minutes_left)
            except Exception as exc:
                logger.exception("Background orchestration failed: %s", exc)

        t = threading.Thread(target=_run, daemon=True, name=f"meeting-prep-{_slugify(event.get('summary', 'meeting'))}")
        t.start()
        return t
