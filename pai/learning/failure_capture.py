"""Failure Capture System — V5 Learning Engine

Full context dumps when things go wrong:
  - Pipeline failure (exception in autonomous pipeline)
  - Low rating (<= 2 from Mike)
  - Tool failure (MCP tool returns error)
  - Timeout (response took too long)
  - Hallucination detected (Mike flags inaccurate information)

Stores detailed failure reports for weekly pattern analysis.
"""
from __future__ import annotations

import json
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class FailureType(str, Enum):
    PIPELINE = "pipeline"       # Exception in autonomous pipeline
    LOW_RATING = "low_rating"   # Mike rated <= 2
    TOOL_ERROR = "tool_error"   # MCP tool returned error
    TIMEOUT = "timeout"         # Response took too long
    HALLUCINATION = "hallucination"  # Mike flagged inaccurate info
    ROUTING_ERROR = "routing_error"  # Intent classified wrong
    CORRECTION = "correction"   # Mike corrected Jake


@dataclass
class FailureReport:
    """A detailed failure context dump."""
    failure_type: FailureType
    summary: str
    context: str = ""
    recent_messages: list[str] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)
    error_trace: str = ""
    root_cause: str = ""  # Populated by analysis
    suggested_fix: str = ""  # Populated by analysis
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "failure_type": self.failure_type.value,
            "summary": self.summary,
            "context": self.context[:500],
            "recent_messages": self.recent_messages[-5:],
            "tool_calls": self.tool_calls[-5:],
            "error_trace": self.error_trace[:1000],
            "root_cause": self.root_cause,
            "suggested_fix": self.suggested_fix,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_markdown(self) -> str:
        """Render as a markdown failure report."""
        lines = [
            f"# Failure Report: {self.failure_type.value}",
            f"**Time:** {self.timestamp.isoformat()}",
            f"**Summary:** {self.summary}",
            "",
            "## Context",
            self.context[:500] if self.context else "(no context)",
            "",
        ]

        if self.recent_messages:
            lines.append("## Recent Messages")
            for msg in self.recent_messages[-5:]:
                lines.append(f"  > {msg[:200]}")
            lines.append("")

        if self.error_trace:
            lines.append("## Error Trace")
            lines.append(f"```\n{self.error_trace[:1000]}\n```")
            lines.append("")

        if self.root_cause:
            lines.append(f"## Root Cause\n{self.root_cause}")
            lines.append("")

        if self.suggested_fix:
            lines.append(f"## Suggested Fix\n{self.suggested_fix}")
            lines.append("")

        return "\n".join(lines)


class FailureCapture:
    """Capture and analyze failures for learning."""

    FAILURES_DIR = Path(__file__).parent.parent / "MEMORY" / "LEARNING" / "failures"
    LOG_DIR = Path(__file__).parent.parent / "MEMORY" / "STATE"

    def __init__(self):
        self.FAILURES_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def capture(
        self,
        failure_type: FailureType | str,
        summary: str,
        context: str = "",
        recent_messages: list[str] | None = None,
        tool_calls: list[dict] | None = None,
        exception: Exception | None = None,
    ) -> FailureReport:
        """Capture a failure with full context."""
        if isinstance(failure_type, str):
            failure_type = FailureType(failure_type)

        error_trace = ""
        if exception:
            error_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

        report = FailureReport(
            failure_type=failure_type,
            summary=summary,
            context=context,
            recent_messages=recent_messages or [],
            tool_calls=tool_calls or [],
            error_trace=error_trace,
        )

        # Basic root cause analysis
        report.root_cause = self._analyze_root_cause(report)
        report.suggested_fix = self._suggest_fix(report)

        self._persist(report)
        return report

    def capture_exception(self, exception: Exception, context: str = "") -> FailureReport:
        """Convenience: capture a pipeline exception."""
        return self.capture(
            failure_type=FailureType.PIPELINE,
            summary=f"{type(exception).__name__}: {str(exception)[:200]}",
            context=context,
            exception=exception,
        )

    def capture_low_rating(self, rating: int, jake_response: str, mike_message: str) -> FailureReport:
        """Convenience: capture a low satisfaction rating."""
        return self.capture(
            failure_type=FailureType.LOW_RATING,
            summary=f"Rating {rating}/5 from Mike",
            context=f"Jake said: {jake_response[:200]}\nMike said: {mike_message[:200]}",
            recent_messages=[jake_response[:200], mike_message[:200]],
        )

    def capture_tool_error(self, tool_name: str, error: str, context: str = "") -> FailureReport:
        """Convenience: capture a tool/MCP error."""
        return self.capture(
            failure_type=FailureType.TOOL_ERROR,
            summary=f"Tool '{tool_name}' failed: {error[:200]}",
            context=context,
            tool_calls=[{"tool": tool_name, "error": error}],
        )

    def get_recent_failures(self, days: int = 7) -> list[dict]:
        """Get failures from the last N days."""
        log_file = self.LOG_DIR / "failures.jsonl"
        if not log_file.exists():
            return []

        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        recent = []
        with open(log_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = datetime.fromisoformat(entry["timestamp"])
                    if ts.timestamp() > cutoff:
                        recent.append(entry)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        return recent

    def failure_patterns(self, days: int = 30) -> dict[str, int]:
        """Aggregate failure types over a period."""
        failures = self.get_recent_failures(days)
        counts: dict[str, int] = {}
        for f in failures:
            ft = f.get("failure_type", "unknown")
            counts[ft] = counts.get(ft, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _analyze_root_cause(self, report: FailureReport) -> str:
        """Basic root cause analysis from the failure context."""
        ft = report.failure_type

        if ft == FailureType.PIPELINE:
            if "timeout" in report.error_trace.lower():
                return "External service timeout — likely API or MCP server slow response"
            if "connection" in report.error_trace.lower():
                return "Connection error — network or service unavailable"
            if "json" in report.error_trace.lower():
                return "Malformed response — upstream service returned unexpected format"
            return "Pipeline exception — review error trace for specifics"

        if ft == FailureType.LOW_RATING:
            return "Response quality — Jake's answer didn't meet Mike's expectations"

        if ft == FailureType.TOOL_ERROR:
            return "Tool/MCP failure — external tool returned an error"

        if ft == FailureType.TIMEOUT:
            return "Response too slow — consider model tier downgrade or query simplification"

        if ft == FailureType.HALLUCINATION:
            return "Inaccurate information — Jake stated something factually wrong"

        return "Unknown root cause — needs manual review"

    def _suggest_fix(self, report: FailureReport) -> str:
        """Suggest a fix based on failure type and root cause."""
        ft = report.failure_type

        if ft == FailureType.PIPELINE:
            return "Add retry logic with exponential backoff; add timeout handling"

        if ft == FailureType.LOW_RATING:
            return "Review the interaction — was context missing? Was the response format wrong?"

        if ft == FailureType.TOOL_ERROR:
            return "Check tool availability; add fallback path; verify credentials"

        if ft == FailureType.HALLUCINATION:
            return "Add fact to LEARNED.md or WRONG.md; increase retrieval before answering"

        return "Manual investigation needed"

    def _persist(self, report: FailureReport):
        """Save failure report to JSONL and individual markdown file."""
        # JSONL log
        log_file = self.LOG_DIR / "failures.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(report.to_dict()) + "\n")
        except OSError:
            pass

        # Individual markdown report
        ts = report.timestamp.strftime("%Y-%m-%d")
        ftype = report.failure_type.value
        # Simple counter for same-day same-type failures
        existing = list(self.FAILURES_DIR.glob(f"{ts}-{ftype}-*.md"))
        idx = len(existing) + 1
        file_path = self.FAILURES_DIR / f"{ts}-{ftype}-{idx:03d}.md"
        try:
            with open(file_path, "w") as f:
                f.write(report.to_markdown())
        except OSError:
            pass
