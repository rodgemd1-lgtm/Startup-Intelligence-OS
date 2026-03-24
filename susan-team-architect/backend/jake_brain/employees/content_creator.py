"""Content Creator — weekly accomplishments summarizer.

Runs every Monday at 9 AM. Reviews the past 7 days of episodic memory,
groups by project/topic, and generates a weekly summary document.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any

from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineTask

logger = logging.getLogger(__name__)

# Lookback window for weekly summary
WEEKLY_LOOKBACK_DAYS = 7

# Max episodic entries to review
MAX_EPISODES = 50

# Known project groupings for categorization
PROJECT_KEYWORDS = {
    "oracle-health": ["oracle", "cohlmia", "health", "ehr", "meddpicc", "epic", "battlecard"],
    "startup-os": ["susan", "jake", "startup", "intelligence", "hermes", "pipeline", "employee"],
    "alex-recruiting": ["jacob", "recruiting", "recruit", "football", "coach"],
    "hermes": ["hermes", "openclaw", "telegram", "cron", "bot"],
    "general": [],
}


def _detect_project(content: str, topics: list[str]) -> str:
    """Detect which project an episodic entry belongs to."""
    text = (content + " " + " ".join(topics)).lower()
    for project, keywords in PROJECT_KEYWORDS.items():
        if project == "general":
            continue
        if any(kw in text for kw in keywords):
            return project
    return "general"


class ContentCreator:
    """Weekly accomplishments and content summary employee.

    Groups episodic memories by project, identifies key decisions and actions,
    and produces a structured weekly summary.
    """

    EMPLOYEE_NAME = "content_creator"
    TASK_TYPE = "content"
    CONTEXT_HINTS = ["content", "summary", "weekly", "oracle", "projects"]
    SUCCESS_CRITERIA = [
        "content produced",
        "topics_covered list non-empty",
        "word_count > 0",
    ]

    def __init__(self, store=None):
        """
        Args:
            store: BrainStore instance. If None, pipeline runs without memory persistence.
        """
        self._store = store
        self._pipeline = AutonomousPipeline(store=store)

    def run(self, content_type: str = "weekly_summary") -> dict[str, Any]:
        """Run the Content Creator employee.

        Args:
            content_type: Type of content to create (default: 'weekly_summary').

        Returns:
            dict with content_type, content, topics_covered, word_count.
        """
        task = PipelineTask(
            task_type=self.TASK_TYPE,
            description=f"Generate {content_type}: review past {WEEKLY_LOOKBACK_DAYS} days of activity, group by project, summarize accomplishments.",
            success_criteria=self.SUCCESS_CRITERIA,
            context_hints=self.CONTEXT_HINTS,
            employee_name=self.EMPLOYEE_NAME,
            metadata={"content_type": content_type},
        )

        result = self._pipeline.run(task, build_fn=self._build)
        return result.outputs

    def _build(self, task: PipelineTask, context_data: dict) -> dict[str, Any]:
        """BUILD phase: load episodic entries, group, generate weekly summary."""
        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(days=WEEKLY_LOOKBACK_DAYS)).isoformat()
        content_type = getattr(task, "metadata", {}).get("content_type", "weekly_summary")

        # ── Load recent episodic memories ─────────────────────────────────
        episodes: list[dict] = []
        if self._store is not None:
            try:
                result = (
                    self._store.supabase.table("jake_episodic")
                    .select("id, content, occurred_at, topics, memory_type, project, metadata")
                    .gte("occurred_at", cutoff)
                    .order("occurred_at", desc=True)
                    .limit(MAX_EPISODES)
                    .execute()
                )
                episodes = result.data or []
            except Exception as exc:
                logger.warning("ContentCreator: failed to load episodic entries: %s", exc)

        if not episodes:
            # No episodes — return empty summary
            empty_content = (
                f"Weekly Summary — {now.strftime('%Y-%m-%d')}\n\n"
                f"No activity recorded in the past {WEEKLY_LOOKBACK_DAYS} days.\n"
                "Brain memory appears empty or unavailable."
            )
            return {
                "content_type": content_type,
                "content": empty_content,
                "topics_covered": [],
                "word_count": len(empty_content.split()),
                "episodes_reviewed": 0,
                "generated_at": now.isoformat(),
            }

        # ── Group episodes by project ──────────────────────────────────────
        project_groups: dict[str, list[dict]] = defaultdict(list)

        for ep in episodes:
            project = ep.get("project") or _detect_project(
                ep.get("content", ""),
                ep.get("topics") or [],
            )
            project_groups[project].append(ep)

        # ── Extract decisions and action items from metadata ───────────────
        all_decisions: list[str] = []
        all_actions: list[str] = []
        pipeline_events: list[str] = []

        for ep in episodes:
            meta = ep.get("metadata") or {}
            decisions = meta.get("decisions") or []
            actions = meta.get("action_items") or []
            memory_type = ep.get("memory_type", "")

            all_decisions.extend(decisions[:2])
            all_actions.extend(actions[:2])

            if memory_type == "pipeline_event":
                pipeline_events.append(ep.get("content", "")[:100])

        # ── Generate weekly summary document ──────────────────────────────
        week_start = (now - timedelta(days=WEEKLY_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
        week_end = now.strftime("%Y-%m-%d")

        lines = [
            f"# Weekly Summary: {week_start} → {week_end}",
            f"*Generated by {self.EMPLOYEE_NAME} on {now.strftime('%Y-%m-%d %H:%M UTC')}*",
            f"*{len(episodes)} episodic memories reviewed across {len(project_groups)} projects*",
            "",
        ]

        topics_covered: list[str] = []

        for project, eps in sorted(project_groups.items()):
            if not eps:
                continue
            topics_covered.append(project)

            lines.append(f"## {project.replace('-', ' ').title()} ({len(eps)} entries)")
            lines.append("")

            # Most recent 3 entries as highlights
            highlights = eps[:3]
            lines.append("**Highlights:**")
            for ep in highlights:
                content = ep.get("content", "").replace("\n", " ").strip()
                if content:
                    lines.append(f"- {content[:150]}")

            lines.append("")

        # ── Key decisions ──────────────────────────────────────────────────
        if all_decisions:
            lines.append("## Key Decisions")
            for decision in list(dict.fromkeys(all_decisions))[:5]:  # dedupe
                lines.append(f"- {decision[:150]}")
            lines.append("")

        # ── Action items ───────────────────────────────────────────────────
        if all_actions:
            lines.append("## Action Items")
            for action in list(dict.fromkeys(all_actions))[:5]:
                lines.append(f"- [ ] {action[:150]}")
            lines.append("")

        # ── Autonomous employee activity ───────────────────────────────────
        if pipeline_events:
            lines.append("## Autonomous Activity (AI Employees)")
            for event in pipeline_events[:5]:
                lines.append(f"- {event}")
            lines.append("")

        content = "\n".join(lines)

        # ── Store summary to episodic ──────────────────────────────────────
        if self._store is not None:
            try:
                self._store.store_episodic(
                    content=content,
                    occurred_at=now,
                    memory_type="weekly_content",
                    project="startup-os",
                    importance=0.8,
                    topics=["weekly_summary", "content"] + topics_covered[:3],
                    source=self.EMPLOYEE_NAME,
                    source_type="autonomous_employee",
                    metadata={
                        "content_type": content_type,
                        "episodes_reviewed": len(episodes),
                        "projects_covered": topics_covered,
                        "week_start": week_start,
                        "week_end": week_end,
                    },
                )
            except Exception as exc:
                logger.warning("ContentCreator: failed to store weekly content: %s", exc)

        return {
            "content_type": content_type,
            "content": content,
            "topics_covered": topics_covered,
            "word_count": len(content.split()),
            "episodes_reviewed": len(episodes),
            "decisions_captured": len(all_decisions),
            "actions_captured": len(all_actions),
            "generated_at": now.isoformat(),
        }
