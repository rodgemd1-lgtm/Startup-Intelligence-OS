"""Memory Consolidation Pipeline — V5 Learning Engine

Nightly (2 AM): episodic → semantic promotion
  - Scan for clusters: same topic 3+ times in 14 days
  - Promote clustered facts to semantic with synthesized content
  - Mark source records as consolidated

Weekly (Sunday): semantic → wisdom promotion
  - Scan for stable facts (unchanged 30+ days)
  - Cross-reference with LEARNED.md and WRONG.md
  - Promote validated facts to WISDOM.md
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ConsolidationResult:
    """Result of a consolidation run."""
    run_type: str  # "nightly" or "weekly"
    records_scanned: int = 0
    clusters_found: int = 0
    promoted: int = 0
    skipped: int = 0
    errors: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_type": self.run_type,
            "records_scanned": self.records_scanned,
            "clusters_found": self.clusters_found,
            "promoted": self.promoted,
            "skipped": self.skipped,
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details[:20],
        }

    def summary(self) -> str:
        return (
            f"Consolidation ({self.run_type}): "
            f"scanned={self.records_scanned}, clusters={self.clusters_found}, "
            f"promoted={self.promoted}, skipped={self.skipped}, errors={self.errors}"
        )


class ConsolidationPipeline:
    """Memory consolidation: episodic → semantic → wisdom."""

    MEMORY_DIR = Path(__file__).parent.parent / "MEMORY"
    STATE_DIR = MEMORY_DIR / "STATE"
    LEARNING_DIR = MEMORY_DIR / "LEARNING"
    WISDOM_DIR = MEMORY_DIR / "WISDOM"

    CLUSTER_THRESHOLD = 3     # Minimum mentions to form a cluster
    CLUSTER_WINDOW_DAYS = 14  # Window for clustering
    STABILITY_DAYS = 30       # How long a fact must be stable for wisdom promotion

    def __init__(self):
        for d in [self.STATE_DIR, self.LEARNING_DIR, self.WISDOM_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    def run_nightly(self) -> ConsolidationResult:
        """Nightly episodic → semantic consolidation.

        Reads ratings, corrections, and failure logs to find clusters
        of related information that should be promoted to stable knowledge.
        """
        result = ConsolidationResult(run_type="nightly")

        # Read recent episodic data (ratings, corrections, patterns)
        ratings = self._read_jsonl(self.STATE_DIR / "ratings.jsonl", days=self.CLUSTER_WINDOW_DAYS)
        corrections = self._read_jsonl(self.STATE_DIR / "corrections.jsonl", days=self.CLUSTER_WINDOW_DAYS)

        result.records_scanned = len(ratings) + len(corrections)

        # Find topic clusters in corrections
        correction_rules = [c.get("rule_extracted", "") for c in corrections if c.get("rule_extracted")]
        clusters = self._find_clusters(correction_rules)
        result.clusters_found = len(clusters)

        # Promote clusters to semantic knowledge
        for cluster_topic, items in clusters.items():
            if len(items) >= self.CLUSTER_THRESHOLD:
                self._promote_to_semantic(cluster_topic, items)
                result.promoted += 1
                result.details.append(f"Promoted: {cluster_topic} ({len(items)} occurrences)")
            else:
                result.skipped += 1

        # Find rating patterns (consistently low-rated topics)
        low_rated = [r for r in ratings if r.get("rating", 3) <= 2]
        if len(low_rated) >= 3:
            result.details.append(f"Warning: {len(low_rated)} low-rated interactions in last {self.CLUSTER_WINDOW_DAYS} days")

        self._persist_result(result)
        return result

    def run_weekly(self) -> ConsolidationResult:
        """Weekly semantic → wisdom promotion.

        Promotes stable, validated facts to WISDOM.md.
        """
        result = ConsolidationResult(run_type="weekly")

        # Read semantic knowledge (promoted corrections + rules)
        semantic_file = self.LEARNING_DIR / "semantic-knowledge.jsonl"
        if not semantic_file.exists():
            result.details.append("No semantic knowledge to promote yet")
            self._persist_result(result)
            return result

        entries = self._read_jsonl(semantic_file, days=None)  # All entries
        result.records_scanned = len(entries)

        # Find stable entries (created > STABILITY_DAYS ago, not contradicted)
        cutoff = datetime.now(timezone.utc).timestamp() - (self.STABILITY_DAYS * 86400)
        stable = []
        for entry in entries:
            try:
                created = datetime.fromisoformat(entry.get("promoted_at", entry.get("timestamp", "")))
                if created.timestamp() < cutoff:
                    stable.append(entry)
            except (ValueError, TypeError):
                continue

        result.clusters_found = len(stable)

        # Check against WRONG.md — don't promote contradicted facts
        wrong_entries = self._read_wrong_md()

        for entry in stable:
            topic = entry.get("topic", "")
            content = entry.get("content", "")

            # Skip if contradicted by WRONG.md
            if any(w.lower() in content.lower() for w in wrong_entries):
                result.skipped += 1
                result.details.append(f"Skipped (contradicted): {topic[:60]}")
                continue

            self._promote_to_wisdom(entry)
            result.promoted += 1
            result.details.append(f"Wisdom: {topic[:60]}")

        self._persist_result(result)
        return result

    def get_consolidation_stats(self) -> dict:
        """Get stats from recent consolidation runs."""
        log_file = self.STATE_DIR / "consolidation.jsonl"
        if not log_file.exists():
            return {"nightly_runs": 0, "weekly_runs": 0, "total_promoted": 0}

        entries = self._read_jsonl(log_file, days=30)
        nightly = [e for e in entries if e.get("run_type") == "nightly"]
        weekly = [e for e in entries if e.get("run_type") == "weekly"]

        return {
            "nightly_runs": len(nightly),
            "weekly_runs": len(weekly),
            "total_promoted": sum(e.get("promoted", 0) for e in entries),
            "total_scanned": sum(e.get("records_scanned", 0) for e in entries),
            "last_nightly": nightly[-1].get("timestamp") if nightly else None,
            "last_weekly": weekly[-1].get("timestamp") if weekly else None,
        }

    def _find_clusters(self, items: list[str]) -> dict[str, list[str]]:
        """Find topic clusters using simple word overlap."""
        if not items:
            return {}

        clusters: dict[str, list[str]] = {}
        for item in items:
            words = set(item.lower().split())
            placed = False
            for topic, members in clusters.items():
                topic_words = set(topic.lower().split())
                overlap = len(words & topic_words) / max(len(words), 1)
                if overlap > 0.4:
                    members.append(item)
                    placed = True
                    break
            if not placed:
                clusters[item] = [item]

        return {k: v for k, v in clusters.items() if len(v) >= 2}

    def _promote_to_semantic(self, topic: str, items: list[str]):
        """Write a clustered fact to semantic knowledge."""
        semantic_file = self.LEARNING_DIR / "semantic-knowledge.jsonl"
        entry = {
            "topic": topic,
            "content": f"Consolidated from {len(items)} observations: {topic}",
            "evidence_count": len(items),
            "promoted_at": datetime.now(timezone.utc).isoformat(),
            "source": "nightly_consolidation",
        }
        try:
            with open(semantic_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass

    def _promote_to_wisdom(self, entry: dict):
        """Append a stable fact to WISDOM.md."""
        wisdom_file = self.WISDOM_DIR / "wisdom.md"
        topic = entry.get("topic", "Unknown")
        content = entry.get("content", "")
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        text = f"\n## [{date}] {topic}\n{content}\n*Evidence: {entry.get('evidence_count', 1)} observations*\n"

        try:
            if wisdom_file.exists():
                with open(wisdom_file, "a") as f:
                    f.write(text)
            else:
                with open(wisdom_file, "w") as f:
                    f.write("# Jake's Wisdom\n\nStable knowledge promoted from learning pipeline.\n")
                    f.write(text)
        except OSError:
            pass

    def _read_wrong_md(self) -> list[str]:
        """Read WRONG.md entries to avoid promoting contradicted facts."""
        wrong_path = Path(__file__).parent.parent / "TELOS" / "WRONG.md"
        if not wrong_path.exists():
            return []
        try:
            content = wrong_path.read_text()
            # Extract wrong assumptions (lines starting with "**Wrong assumption:**")
            entries = []
            for line in content.split("\n"):
                if "wrong assumption" in line.lower() or "reality:" in line.lower():
                    entries.append(line.strip())
            return entries
        except OSError:
            return []

    def _read_jsonl(self, path: Path, days: int | None = 7) -> list[dict]:
        """Read entries from a JSONL file, optionally filtered by age."""
        if not path.exists():
            return []

        cutoff = None
        if days is not None:
            cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)

        entries = []
        with open(path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if cutoff:
                        ts_str = entry.get("timestamp", entry.get("promoted_at", ""))
                        if ts_str:
                            ts = datetime.fromisoformat(ts_str)
                            if ts.timestamp() < cutoff:
                                continue
                    entries.append(entry)
                except (json.JSONDecodeError, ValueError):
                    continue
        return entries

    def _persist_result(self, result: ConsolidationResult):
        """Save consolidation result to log."""
        log_file = self.STATE_DIR / "consolidation.jsonl"
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(result.to_dict()) + "\n")
        except OSError:
            pass
