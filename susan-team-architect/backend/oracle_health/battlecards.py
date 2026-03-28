"""Battlecard generation and management for Oracle Health.

Produces Klue Know-Say-Show format battlecards from RAG data.
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

from oracle_health.schemas import (
    Competitor, Priority, Freshness, Persona,
    Battlecard, BattlecardSection, TalkTrack, WinLossRecord,
)
from oracle_health.director import (
    COMPETITORS, DATA_DIR, BATTLECARD_DIR, search_competitor_intel, freshness_check,
)


def generate_battlecard(competitor: Competitor) -> str:
    """Generate a Klue Know-Say-Show battlecard from RAG data.

    Returns markdown string ready for file or display.
    """
    meta = COMPETITORS[competitor]
    intel = search_competitor_intel(competitor, "strategy product pricing wins losses weaknesses", top_k=20)

    # Classify intel into KNOW/SAY/SHOW buckets
    strategy_chunks = []
    wins_chunks = []
    losses_chunks = []
    pricing_chunks = []
    weakness_chunks = []
    general_chunks = []

    for item in intel:
        content = item.get("content", "").lower()
        data_type = item.get("data_type", "")

        if any(w in content for w in ["strategy", "direction", "invest", "roadmap", "vision"]):
            strategy_chunks.append(item)
        elif any(w in content for w in ["won", "win", "selected", "chose", "deployed"]):
            wins_chunks.append(item)
        elif any(w in content for w in ["lost", "loss", "replaced", "switched from", "migrated away"]):
            losses_chunks.append(item)
        elif any(w in content for w in ["pricing", "cost", "license", "subscription", "per-bed", "tco"]):
            pricing_chunks.append(item)
        elif any(w in content for w in ["weakness", "limitation", "complaint", "issue", "problem", "gap"]):
            weakness_chunks.append(item)
        else:
            general_chunks.append(item)

    # Build markdown
    now = datetime.now()
    template = DATA_DIR / "gold_standards" / "battlecard-template.md"

    md = f"""# BATTLECARD: Oracle Health vs. {meta['name']}

**Updated:** {now.strftime('%Y-%m-%d')} | **Freshness:** FRESH
**Priority:** {meta['priority'].value}
**Owner:** Battlecard Manager → Sales Enablement
**RAG chunks analyzed:** {len(intel)}

---

## KNOW (Internal Only — Not For Customers)

### Current Strategy
{_summarize_chunks(strategy_chunks, 'No strategy intelligence available. Harvest needed.')}

### Recent Wins
{_format_win_loss(wins_chunks, 'won')}

### Recent Losses
{_format_win_loss(losses_chunks, 'lost')}

### Pricing Intelligence
{_summarize_chunks(pricing_chunks, 'No pricing intelligence available. Harvest needed.')}

### Known Weaknesses (With Evidence)
{_format_list(weakness_chunks, 'No documented weaknesses. Research needed.')}

---

## SAY (Talk Tracks For Sales)

### Opening Positioning Statement
> "Oracle Health delivers the deepest clinical workflow integration in the industry, backed by Oracle's enterprise infrastructure. Unlike {meta['name']}, we offer a single-vendor stack that eliminates integration complexity and reduces total cost of ownership."

### Per-Persona Talk Tracks

#### For CIO
- **Lead with**: Total cost of ownership and single-vendor advantage
- **Key proof**: Oracle Cloud infrastructure eliminates middleware costs
- **Avoid**: Feature-by-feature comparisons where {meta['name']} may have point advantages

#### For CMIO
- **Lead with**: Clinical workflow depth from Cerner heritage
- **Key proof**: Workflow demonstration showing click reduction
- **Avoid**: AI feature comparisons without concrete accuracy data

#### For VP Operations
- **Lead with**: Implementation methodology and Oracle's support infrastructure
- **Key proof**: Go-live success rates and stabilization timelines
- **Avoid**: Promises about timelines without qualification

#### For Clinical Director
- **Lead with**: Configurable workflows for their specific specialty
- **Key proof**: Demo with their actual order sets and documentation templates
- **Avoid**: Generic "better workflow" claims without screenshots

#### For Implementation Lead
- **Lead with**: Oracle's data migration tools and conversion utilities
- **Key proof**: Specific data mapping capabilities and FHIR support
- **Avoid**: Minimizing migration complexity — be honest about effort

### Landmine Questions
1. "How does {meta['name']} handle data migration from legacy systems?"
2. "What's your total cost including middleware and integration?"
3. "Can you show me how a [specific clinical workflow] works end-to-end?"

### Trap-Setting Questions
1. "How does your database layer handle real-time clinical data at scale?"
2. "What's your approach to single sign-on across the entire clinical stack?"

---

## SHOW (Proof and Evidence)

### Evidence From RAG
{_format_evidence(general_chunks)}

### Analyst Ratings
_[Requires fresh KLAS/Gartner/Forrester data — flag for Market Intelligence harvest]_

### TCO Comparison
_[Requires pricing intelligence — flag for competitive monitor]_

---

## FRESHNESS LOG
| Date | What Changed | Updated By |
|------|-------------|-----------|
| {now.strftime('%Y-%m-%d')} | Initial generation from RAG ({len(intel)} chunks) | oracle-health/battlecards.py |

---

_Generated by Oracle Health Department — Battlecard Manager_
_Gold standard template: {template}_
"""
    return md


def _summarize_chunks(chunks: list[dict], empty_msg: str) -> str:
    if not chunks:
        return f"_{empty_msg}_"
    summaries = []
    for c in chunks[:5]:  # Top 5
        content = c.get("content", "")[:300]
        source = c.get("source", "RAG")
        summaries.append(f"- {content}... _(Source: {source})_")
    return "\n".join(summaries)


def _format_win_loss(chunks: list[dict], direction: str) -> str:
    if not chunks:
        return f"_No {direction} deal intelligence available. Flag for Sales Enablement._"
    header = "| Customer | Context | Source |\n|----------|---------|--------|\n"
    rows = []
    for c in chunks[:5]:
        content = c.get("content", "")[:200]
        source = c.get("source", "RAG")
        rows.append(f"| _See detail_ | {content}... | {source} |")
    return header + "\n".join(rows)


def _format_list(chunks: list[dict], empty_msg: str) -> str:
    if not chunks:
        return f"_{empty_msg}_"
    items = []
    for i, c in enumerate(chunks[:5], 1):
        content = c.get("content", "")[:200]
        source = c.get("source", "RAG")
        items.append(f"{i}. **{content[:80]}...** — _(Source: {source})_")
    return "\n".join(items)


def _format_evidence(chunks: list[dict]) -> str:
    if not chunks:
        return "_No general evidence available in RAG._"
    items = []
    for c in chunks[:5]:
        content = c.get("content", "")[:200]
        data_type = c.get("data_type", "general")
        items.append(f"- [{data_type}] {content}...")
    return "\n".join(items)


def save_battlecard(competitor: Competitor) -> Path:
    """Generate and save a battlecard to disk."""
    BATTLECARD_DIR.mkdir(parents=True, exist_ok=True)
    md = generate_battlecard(competitor)
    path = BATTLECARD_DIR / f"battlecard-{competitor.value}.md"
    path.write_text(md, encoding="utf-8")
    return path


def save_all_battlecards() -> list[Path]:
    """Generate battlecards for all P0 and P1 competitors."""
    paths = []
    for comp, meta in COMPETITORS.items():
        if meta["priority"] in (Priority.P0, Priority.P1):
            paths.append(save_battlecard(comp))
    return paths
