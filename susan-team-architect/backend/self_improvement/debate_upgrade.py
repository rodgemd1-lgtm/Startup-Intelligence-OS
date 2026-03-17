"""LLM-grounded debate engine upgrade.

Provides a multi-position debate system that grounds arguments in
evidence files rather than relying on template-only generation.
Each position (builder, skeptic, contrarian, operator, red_team)
produces arguments backed by concrete evidence references.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from self_improvement.schemas import DebateArgument


def _safe_load_yaml(path: Path) -> dict | None:
    """Load a YAML file, returning None on any failure."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return None


def _tokenize(text: str) -> set[str]:
    """Split text into lowercase word tokens for matching."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _keyword_relevance(topic_tokens: set[str], evidence_text: str) -> float:
    """Score how relevant an evidence item is to the topic (0-1)."""
    if not topic_tokens or not evidence_text:
        return 0.0

    evidence_tokens = _tokenize(evidence_text)
    if not evidence_tokens:
        return 0.0

    overlap = topic_tokens & evidence_tokens
    # Jaccard-like score weighted toward topic coverage
    topic_coverage = len(overlap) / len(topic_tokens) if topic_tokens else 0.0
    return min(1.0, topic_coverage)


def _extract_searchable_text(evidence: dict) -> str:
    """Extract all searchable text from an evidence record."""
    parts: list[str] = []

    for key in ("title", "content", "source_url"):
        val = evidence.get(key, "")
        if isinstance(val, str):
            parts.append(val)

    tags = evidence.get("topic_tags", [])
    if isinstance(tags, list):
        parts.extend(str(t) for t in tags)

    domain = evidence.get("domain", "")
    if domain:
        parts.append(str(domain))

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Position framing templates
# ---------------------------------------------------------------------------

_POSITION_FRAMINGS: dict[str, dict[str, str]] = {
    "builder": {
        "stance": "optimistic and forward-looking",
        "frame": (
            "This is an opportunity to build. The evidence supports moving forward "
            "because it shows positive signals and feasible paths."
        ),
        "lens": "What can we build? What does the evidence enable?",
    },
    "skeptic": {
        "stance": "cautious and evidence-demanding",
        "frame": (
            "We should proceed only with strong evidence. The current data "
            "may not be sufficient to justify the cost and risk."
        ),
        "lens": "What gaps remain? Is the evidence strong enough?",
    },
    "contrarian": {
        "stance": "alternative-seeking",
        "frame": (
            "There may be a fundamentally different approach that the "
            "conventional framing misses. Consider orthogonal options."
        ),
        "lens": "What if we took a completely different path?",
    },
    "operator": {
        "stance": "practical and execution-focused",
        "frame": (
            "What matters is whether this can actually ship and operate. "
            "Focus on feasibility, team capacity, and operational readiness."
        ),
        "lens": "Can we execute this? What are the operational constraints?",
    },
    "red_team": {
        "stance": "adversarial and failure-seeking",
        "frame": (
            "This could fail. The job is to find the weakest assumptions, "
            "the most likely failure modes, and the hidden costs."
        ),
        "lens": "How does this fail? What are we not seeing?",
    },
}


# ---------------------------------------------------------------------------
# GroundedDebateEngine
# ---------------------------------------------------------------------------

class GroundedDebateEngine:
    """Multi-position debate engine grounded in evidence files.

    Rather than generating arguments from templates alone, this engine
    searches evidence and capability files, scores them for relevance,
    and constructs arguments that reference specific evidence items.
    """

    def __init__(
        self,
        evidence_dir: Path,
        capabilities_dir: Path,
    ) -> None:
        self._evidence_dir = evidence_dir
        self._capabilities_dir = capabilities_dir

    # ------------------------------------------------------------------
    # Gather evidence
    # ------------------------------------------------------------------

    def gather_evidence(self, decision_topic: str) -> list[dict]:
        """Search evidence and capability files for data relevant to the topic.

        Reads all YAML files in the evidence and capabilities directories,
        scores them by keyword relevance to the decision topic, and returns
        sorted results.
        """
        topic_tokens = _tokenize(decision_topic)
        scored_items: list[tuple[float, dict]] = []

        # Scan evidence directory
        if self._evidence_dir.exists():
            for yaml_file in self._evidence_dir.glob("**/*.yaml"):
                data = _safe_load_yaml(yaml_file)
                if data is None:
                    continue

                searchable = _extract_searchable_text(data)
                relevance = _keyword_relevance(topic_tokens, searchable)

                if relevance > 0.05:
                    scored_items.append((relevance, {
                        "id": data.get("id", yaml_file.stem),
                        "title": data.get("title", yaml_file.stem),
                        "source_type": data.get("source_type", "yaml"),
                        "domain": data.get("domain", ""),
                        "confidence": data.get("confidence", 0.5),
                        "relevance_score": round(relevance, 3),
                        "topic_tags": data.get("topic_tags", []),
                        "content_preview": str(data.get("content", ""))[:300],
                        "file_path": str(yaml_file),
                    }))

        # Scan capabilities directory
        if self._capabilities_dir.exists():
            for yaml_file in self._capabilities_dir.glob("*.yaml"):
                data = _safe_load_yaml(yaml_file)
                if data is None:
                    continue

                # Capabilities have different structure
                name = data.get("name", "")
                mission = data.get("mission", "")
                keywords = data.get("routing_keywords", [])
                searchable = f"{name} {mission} {' '.join(str(k) for k in keywords)}"
                relevance = _keyword_relevance(topic_tokens, searchable)

                if relevance > 0.05:
                    scored_items.append((relevance, {
                        "id": data.get("id", yaml_file.stem),
                        "title": name or yaml_file.stem,
                        "source_type": "capability",
                        "domain": "capability_map",
                        "confidence": 0.9,
                        "relevance_score": round(relevance, 3),
                        "topic_tags": keywords if isinstance(keywords, list) else [],
                        "content_preview": mission[:300] if mission else "",
                        "file_path": str(yaml_file),
                    }))

        # Sort by relevance descending
        scored_items.sort(key=lambda x: x[0], reverse=True)

        return [item for _, item in scored_items]

    # ------------------------------------------------------------------
    # Generate a grounded argument
    # ------------------------------------------------------------------

    def generate_grounded_argument(
        self,
        position: str,
        topic: str,
        evidence: list[dict],
    ) -> DebateArgument:
        """Create an argument grounded in evidence for a given position.

        The position determines the framing lens:
        - builder: optimistic, what can we build?
        - skeptic: cautious, is the evidence sufficient?
        - contrarian: alternative paths, what are we missing?
        - operator: practical, can we execute this?
        - red_team: adversarial, how does this fail?

        Confidence is scored based on evidence quality and quantity.
        """
        framing = _POSITION_FRAMINGS.get(position, _POSITION_FRAMINGS["builder"])
        stance = framing["stance"]
        frame = framing["frame"]
        lens = framing["lens"]

        # Select the most relevant evidence for this position
        position_evidence = self._select_evidence_for_position(position, evidence)

        evidence_ids = [e.get("id", "") for e in position_evidence]
        evidence_summaries = [
            f"{e.get('title', 'Unknown')}: {e.get('content_preview', '')[:100]}"
            for e in position_evidence
        ]

        # Build argument text
        argument_parts: list[str] = []

        argument_parts.append(
            f"Position: {position} ({stance})\n"
            f"Topic: {topic}\n\n"
            f"{frame}\n\n"
            f"Analysis lens: {lens}\n"
        )

        if position_evidence:
            argument_parts.append("\nEvidence basis:")
            for i, ev in enumerate(position_evidence[:5], 1):
                title = ev.get("title", "Untitled")
                preview = ev.get("content_preview", "")[:150]
                relevance = ev.get("relevance_score", 0.0)
                argument_parts.append(
                    f"\n  {i}. [{title}] (relevance: {relevance:.2f}): {preview}"
                )

            argument_parts.append(
                f"\n\nSynthesis ({position} view):"
            )
            argument_parts.append(
                self._synthesize_position(position, topic, position_evidence)
            )
        else:
            argument_parts.append(
                "\nNo directly relevant evidence found. "
                "This argument is template-based only."
            )

        argument_text = "\n".join(argument_parts)

        # Compute confidence
        confidence = self._compute_argument_confidence(
            position, position_evidence,
        )

        # Determine source type
        source = "rag_grounded" if position_evidence else "template"

        return DebateArgument(
            position=position,
            argument=argument_text,
            evidence_ids=evidence_ids,
            evidence_summaries=evidence_summaries,
            confidence=confidence,
            source=source,
        )

    # ------------------------------------------------------------------
    # Run full debate
    # ------------------------------------------------------------------

    def run_debate(
        self,
        topic: str,
        num_rounds: int = 5,
    ) -> list[DebateArgument]:
        """Run a full multi-position debate with evidence grounding.

        Executes all five positions (builder, skeptic, contrarian,
        operator, red_team) for up to num_rounds, gathering fresh
        evidence for each round.
        """
        positions = ["builder", "skeptic", "contrarian", "operator", "red_team"]
        active_positions = positions[:num_rounds]

        # Gather evidence once for the topic
        evidence = self.gather_evidence(topic)

        arguments: list[DebateArgument] = []
        for position in active_positions:
            arg = self.generate_grounded_argument(position, topic, evidence)
            arguments.append(arg)

        return arguments

    # ------------------------------------------------------------------
    # Synthesize recommendation
    # ------------------------------------------------------------------

    def synthesize_recommendation(
        self, arguments: list[DebateArgument]
    ) -> dict:
        """Weighted synthesis of all debate arguments.

        Higher-confidence, better-evidenced arguments get more weight.
        Returns a recommendation dict with:
        - recommendation: primary path forward
        - counter_recommendation: alternative if primary is blocked
        - key_evidence: most-cited evidence IDs
        - confidence: weighted overall confidence
        """
        if not arguments:
            return {
                "recommendation": "No arguments provided.",
                "counter_recommendation": "Gather evidence and re-run debate.",
                "key_evidence": [],
                "confidence": 0.0,
            }

        # Weight each argument by confidence and evidence count
        weighted_args: list[tuple[float, DebateArgument]] = []
        for arg in arguments:
            evidence_bonus = min(0.3, len(arg.evidence_ids) * 0.05)
            source_bonus = 0.1 if arg.source == "rag_grounded" else 0.0
            weight = arg.confidence + evidence_bonus + source_bonus
            weighted_args.append((weight, arg))

        weighted_args.sort(key=lambda x: x[0], reverse=True)

        # Primary recommendation: highest-weighted constructive argument
        # (builder or operator tend to be constructive)
        constructive = [
            (w, a) for w, a in weighted_args
            if a.position in ("builder", "operator")
        ]
        primary = constructive[0] if constructive else weighted_args[0]

        # Counter recommendation: highest-weighted cautious argument
        cautious = [
            (w, a) for w, a in weighted_args
            if a.position in ("skeptic", "contrarian", "red_team")
        ]
        counter = cautious[0] if cautious else weighted_args[-1]

        # Collect all evidence IDs with frequency counts
        evidence_counts: dict[str, int] = {}
        for _, arg in weighted_args:
            for eid in arg.evidence_ids:
                evidence_counts[eid] = evidence_counts.get(eid, 0) + 1

        # Sort evidence by citation frequency
        key_evidence = sorted(
            evidence_counts.keys(),
            key=lambda x: evidence_counts[x],
            reverse=True,
        )[:10]

        # Weighted confidence
        total_weight = sum(w for w, _ in weighted_args)
        if total_weight > 0:
            overall_confidence = sum(
                w * a.confidence for w, a in weighted_args
            ) / total_weight
        else:
            overall_confidence = 0.0

        # Build recommendation text
        recommendation_lines = [
            f"Based on {len(arguments)}-position debate:",
            "",
            f"Primary path ({primary[1].position}, confidence {primary[1].confidence:.2f}):",
            _extract_synthesis_from_argument(primary[1]),
            "",
        ]

        counter_lines = [
            f"Alternative path ({counter[1].position}, confidence {counter[1].confidence:.2f}):",
            _extract_synthesis_from_argument(counter[1]),
        ]

        return {
            "recommendation": "\n".join(recommendation_lines),
            "counter_recommendation": "\n".join(counter_lines),
            "key_evidence": key_evidence,
            "confidence": round(min(1.0, overall_confidence), 3),
            "argument_count": len(arguments),
            "grounded_count": sum(
                1 for a in arguments if a.source == "rag_grounded"
            ),
            "position_confidences": {
                a.position: round(a.confidence, 3) for a in arguments
            },
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _select_evidence_for_position(
        self,
        position: str,
        evidence: list[dict],
    ) -> list[dict]:
        """Select and prioritize evidence items based on the debate position.

        Different positions benefit from different evidence characteristics:
        - builder/operator: high-confidence, high-relevance
        - skeptic: any evidence, especially low-confidence items
        - contrarian: less obvious, tangential evidence
        - red_team: failure-related evidence, low-confidence items
        """
        if not evidence:
            return []

        scored: list[tuple[float, dict]] = []

        for ev in evidence:
            base_relevance = ev.get("relevance_score", 0.0)
            confidence = ev.get("confidence", 0.5)
            tags = ev.get("topic_tags", [])
            tag_set = set(str(t).lower() for t in tags)

            position_score = base_relevance

            if position == "builder":
                # Prefer high-confidence, high-relevance evidence
                position_score = base_relevance * 0.6 + confidence * 0.4

            elif position == "skeptic":
                # Prefer evidence that reveals gaps or low confidence
                if confidence < 0.7:
                    position_score += 0.2
                # Value any evidence (skeptics examine everything)
                position_score = max(position_score, base_relevance * 0.8)

            elif position == "contrarian":
                # Prefer tangential evidence that might reveal alternatives
                if base_relevance < 0.5 and base_relevance > 0.1:
                    position_score += 0.3
                # Boost diverse domain evidence
                if ev.get("source_type") == "capability":
                    position_score += 0.15

            elif position == "operator":
                # Prefer operational, practical evidence
                operational_tags = {"operational", "process", "workflow", "cadence", "team"}
                if tag_set & operational_tags:
                    position_score += 0.25
                position_score = base_relevance * 0.5 + confidence * 0.5

            elif position == "red_team":
                # Prefer failure-related, risk evidence
                risk_tags = {"risk", "failure", "compliance", "governance", "security"}
                if tag_set & risk_tags:
                    position_score += 0.3
                # Red team values low-confidence evidence as attack surface
                if confidence < 0.6:
                    position_score += 0.2

            scored.append((position_score, ev))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Return top items, at most 5
        return [item for _, item in scored[:5]]

    def _synthesize_position(
        self,
        position: str,
        topic: str,
        evidence: list[dict],
    ) -> str:
        """Generate a synthesis paragraph for the given position and evidence."""
        if not evidence:
            return f"Without specific evidence, the {position} position on '{topic}' is speculative."

        # Count evidence characteristics
        high_conf = sum(1 for e in evidence if e.get("confidence", 0) >= 0.8)
        low_conf = sum(1 for e in evidence if e.get("confidence", 0) < 0.6)
        total = len(evidence)
        avg_relevance = sum(e.get("relevance_score", 0) for e in evidence) / total

        titles = [e.get("title", "Unknown") for e in evidence[:3]]
        title_list = ", ".join(titles)

        if position == "builder":
            return (
                f"The evidence supports forward motion. {high_conf} of {total} "
                f"evidence items have high confidence (>=0.8). Key sources: "
                f"{title_list}. Average relevance to topic: {avg_relevance:.2f}. "
                f"The path forward has evidentiary support for execution."
            )

        elif position == "skeptic":
            return (
                f"Caution is warranted. {low_conf} of {total} evidence items "
                f"have confidence below 0.6. Average relevance: {avg_relevance:.2f}. "
                f"Key gaps may exist in: {title_list}. "
                f"More evidence should be gathered before committing resources."
            )

        elif position == "contrarian":
            domains = set(e.get("domain", "") for e in evidence if e.get("domain"))
            return (
                f"The evidence spans {len(domains)} domain(s): {', '.join(domains)}. "
                f"Consider whether the framing of '{topic}' is the right lens. "
                f"Sources like {title_list} suggest alternative framings may exist. "
                f"Average relevance ({avg_relevance:.2f}) leaves room for "
                f"orthogonal approaches."
            )

        elif position == "operator":
            return (
                f"From an execution standpoint, {total} evidence items were found "
                f"with average relevance {avg_relevance:.2f}. "
                f"{high_conf} have high confidence, suggesting operational feasibility. "
                f"Key references: {title_list}. The question is whether team "
                f"capacity and systems are ready to execute."
            )

        elif position == "red_team":
            return (
                f"Attack surface: {low_conf} of {total} items have low confidence, "
                f"indicating weak spots. Average relevance is only {avg_relevance:.2f}, "
                f"meaning the evidence may not fully cover the topic. "
                f"Sources: {title_list}. "
                f"Failure modes include: insufficient evidence depth, "
                f"overconfidence in synthetic data, and unvalidated assumptions."
            )

        return f"Position '{position}' synthesis based on {total} evidence items."

    def _compute_argument_confidence(
        self,
        position: str,
        evidence: list[dict],
    ) -> float:
        """Compute confidence for an argument based on evidence quality and quantity."""
        if not evidence:
            return 0.2  # Template-only arguments have low confidence

        # Base from evidence count (diminishing returns)
        count_score = min(0.4, len(evidence) * 0.08)

        # Average evidence confidence
        avg_confidence = sum(
            e.get("confidence", 0.5) for e in evidence
        ) / len(evidence)

        # Average relevance
        avg_relevance = sum(
            e.get("relevance_score", 0.0) for e in evidence
        ) / len(evidence)

        # Position-specific adjustments
        position_bonus = 0.0
        if position in ("builder", "operator"):
            # Constructive positions get a small boost with good evidence
            if avg_confidence > 0.7 and avg_relevance > 0.3:
                position_bonus = 0.05
        elif position in ("skeptic", "red_team"):
            # Critical positions gain confidence from finding weak evidence
            low_conf_count = sum(1 for e in evidence if e.get("confidence", 1.0) < 0.6)
            if low_conf_count > 0:
                position_bonus = 0.1

        raw_confidence = count_score + avg_confidence * 0.3 + avg_relevance * 0.2 + position_bonus
        return max(0.1, min(1.0, raw_confidence))


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _extract_synthesis_from_argument(arg: DebateArgument) -> str:
    """Extract the synthesis section from an argument's text."""
    text = arg.argument
    # Look for the synthesis section
    marker = f"Synthesis ({arg.position} view):"
    idx = text.find(marker)
    if idx >= 0:
        synthesis = text[idx + len(marker):].strip()
        return synthesis[:500] if len(synthesis) > 500 else synthesis

    # Fall back to last paragraph
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if paragraphs:
        last = paragraphs[-1]
        return last[:500] if len(last) > 500 else last

    return text[:300]
