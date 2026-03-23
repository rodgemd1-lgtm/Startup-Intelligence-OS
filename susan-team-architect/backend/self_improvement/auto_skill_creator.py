"""Auto-Skill Creator — Generate Hermes skills from repeated pipeline patterns.

Analyzes jake_procedural memory and pipeline run history to detect
patterns that repeat 3+ times, then auto-generates a Hermes skill YAML
and Python handler that encodes the pattern.

Skills are written to ~/.hermes/skills/auto-generated/ and registered
in ~/.hermes/skills/auto-generated/registry.json.

Usage:
    creator = AutoSkillCreator()
    patterns = creator.detect_patterns(min_frequency=3)
    skills_created = creator.create_skills_from_patterns(patterns)
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SKILLS_DIR = Path.home() / ".hermes" / "skills" / "auto-generated"
_REGISTRY_FILE = _SKILLS_DIR / "registry.json"


class AutoSkillCreator:
    """Detect pipeline patterns and generate Hermes skills from them."""

    def __init__(self) -> None:
        _SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        if not _REGISTRY_FILE.exists():
            _REGISTRY_FILE.write_text(json.dumps({"skills": [], "created_at": datetime.now(timezone.utc).isoformat()}))

    # ------------------------------------------------------------------
    # Pattern detection
    # ------------------------------------------------------------------

    def detect_patterns(self, min_frequency: int = 3) -> list[dict]:
        """Scan jake_procedural for repeated patterns. Returns list of pattern dicts."""
        patterns = self._load_procedural_patterns()
        pattern_counts: Counter = Counter()

        for p in patterns:
            # Normalize the pattern key: task_type + action sequence
            key = self._normalize_pattern(p)
            pattern_counts[key] += 1

        detected = []
        for key, count in pattern_counts.items():
            if count >= min_frequency:
                # Find a representative pattern for this key
                examples = [p for p in patterns if self._normalize_pattern(p) == key]
                detected.append({
                    "key": key,
                    "frequency": count,
                    "task_type": examples[0].get("task_type", "general"),
                    "actions": examples[0].get("actions", []),
                    "success_rate": self._compute_success_rate(examples),
                    "avg_duration_ms": self._avg_duration(examples),
                    "examples": examples[:3],  # keep 3 representative examples
                })

        logger.info("Detected %d patterns with frequency >= %d", len(detected), min_frequency)
        return sorted(detected, key=lambda x: x["frequency"], reverse=True)

    def create_skills_from_patterns(self, patterns: list[dict]) -> list[str]:
        """Create Hermes skill files for each detected pattern. Returns list of skill names."""
        registry = self._load_registry()
        existing_keys = {s["pattern_key"] for s in registry.get("skills", [])}
        created = []

        for pattern in patterns:
            if pattern["key"] in existing_keys:
                logger.debug("Skill already exists for pattern: %s", pattern["key"])
                continue
            if pattern["success_rate"] < 0.7:
                logger.info("Skipping low-success pattern: %s (%.0f%%)", pattern["key"], pattern["success_rate"] * 100)
                continue

            skill_name = self._generate_skill_name(pattern)
            skill_dir = _SKILLS_DIR / skill_name
            skill_dir.mkdir(exist_ok=True)

            # Write skill config
            self._write_skill_config(skill_dir, skill_name, pattern)
            # Write skill handler
            self._write_skill_handler(skill_dir, skill_name, pattern)

            # Register
            registry["skills"].append({
                "name": skill_name,
                "pattern_key": pattern["key"],
                "task_type": pattern["task_type"],
                "frequency": pattern["frequency"],
                "success_rate": pattern["success_rate"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            created.append(skill_name)
            logger.info("Created auto-skill: %s (freq=%d, success=%.0f%%)",
                        skill_name, pattern["frequency"], pattern["success_rate"] * 100)

        registry["updated_at"] = datetime.now(timezone.utc).isoformat()
        _REGISTRY_FILE.write_text(json.dumps(registry, indent=2))
        return created

    def list_generated_skills(self) -> list[dict]:
        """Return all auto-generated skills from registry."""
        return self._load_registry().get("skills", [])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_procedural_patterns(self) -> list[dict]:
        """Load patterns from jake_procedural via Supabase. Falls back to empty list."""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from jake_brain.config import get_supabase_client
            client = get_supabase_client()
            result = client.table("jake_procedural").select(
                "content,metadata,created_at"
            ).order("created_at", desc=True).limit(200).execute()
            patterns = []
            for row in (result.data or []):
                meta = row.get("metadata") or {}
                patterns.append({
                    "content": row.get("content", ""),
                    "task_type": meta.get("task_type", "general"),
                    "actions": meta.get("actions", []),
                    "success": meta.get("success", True),
                    "duration_ms": meta.get("duration_ms", 0),
                })
            return patterns
        except Exception as exc:
            logger.warning("Could not load procedural patterns: %s", exc)
            return []

    def _normalize_pattern(self, pattern: dict) -> str:
        """Create a stable key from task_type + action list."""
        task_type = pattern.get("task_type", "general")
        actions = pattern.get("actions", [])
        if isinstance(actions, list):
            action_str = ",".join(sorted(str(a) for a in actions[:5]))
        else:
            action_str = str(actions)
        return f"{task_type}:{action_str}"

    def _compute_success_rate(self, examples: list[dict]) -> float:
        if not examples:
            return 0.0
        successes = sum(1 for e in examples if e.get("success", True))
        return successes / len(examples)

    def _avg_duration(self, examples: list[dict]) -> float:
        durations = [e.get("duration_ms", 0) for e in examples if e.get("duration_ms")]
        return sum(durations) / len(durations) if durations else 0.0

    def _generate_skill_name(self, pattern: dict) -> str:
        task_type = re.sub(r"[^a-z0-9]", "-", pattern["task_type"].lower())
        short_id = str(uuid.uuid4())[:4]
        return f"auto-{task_type}-{short_id}"

    def _write_skill_config(self, skill_dir: Path, skill_name: str, pattern: dict) -> None:
        config = {
            "name": skill_name,
            "version": "1.0.0",
            "description": (
                f"Auto-generated skill from {pattern['frequency']} repeated "
                f"'{pattern['task_type']}' pipeline runs. "
                f"Success rate: {pattern['success_rate']:.0%}."
            ),
            "author": "Jake AutoSkill",
            "auto_generated": True,
            "pattern_key": pattern["key"],
            "frequency": pattern["frequency"],
            "success_rate": pattern["success_rate"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        (skill_dir / "skill.yaml").write_text(
            "\n".join(f"{k}: {json.dumps(v)}" for k, v in config.items())
        )

    def _write_skill_handler(self, skill_dir: Path, skill_name: str, pattern: dict) -> None:
        actions_repr = json.dumps(pattern.get("actions", []), indent=4)
        handler = f'''"""Auto-generated skill: {skill_name}

Task type: {pattern["task_type"]}
Frequency: {pattern["frequency"]} occurrences
Success rate: {pattern["success_rate"]:.0%}
Generated: {datetime.now(timezone.utc).isoformat()}

This skill encodes the following action pattern:
{actions_repr}
"""

from __future__ import annotations

import logging

logger = logging.getLogger("{skill_name}")


async def run(context: dict) -> dict:
    """Execute the {pattern["task_type"]} pattern."""
    logger.info("Running auto-skill: {skill_name}")
    # Pattern actions (auto-detected):
    actions = {actions_repr}
    return {{
        "skill": "{skill_name}",
        "task_type": "{pattern["task_type"]}",
        "actions": actions,
        "status": "completed",
    }}
'''
        (skill_dir / "handler.py").write_text(handler)

    def _load_registry(self) -> dict:
        try:
            return json.loads(_REGISTRY_FILE.read_text())
        except Exception:
            return {"skills": []}
