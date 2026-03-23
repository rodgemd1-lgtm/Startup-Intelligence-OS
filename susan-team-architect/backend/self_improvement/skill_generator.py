"""Auto Skill Generator — create Hermes skills from successful pipeline patterns.

When a pipeline run succeeds with quality_score > 0.85, extract the pattern
and generate a reusable Hermes skill definition (.md file in ~/.hermes/skills/).
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


HERMES_SKILLS_DIR = Path.home() / ".hermes" / "skills"
GENERATED_SKILLS_DIR = HERMES_SKILLS_DIR / "_auto_generated"


@dataclass
class SkillTemplate:
    name: str
    description: str
    trigger: str
    pipeline_type: str
    prompt_template: str
    success_criteria: list[str]
    source_run_id: Optional[str] = None


class SkillGenerator:
    """Extract successful pipeline patterns and write them as Hermes skills."""

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or GENERATED_SKILLS_DIR

    def _ensure_dir(self) -> None:
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def generate_from_pipeline(
        self,
        pipeline_name: str,
        task_description: str,
        task_type: str,
        phases_completed: dict,
        quality_score: float = 0.9,
        run_id: str | None = None,
    ) -> Path | None:
        """Generate a skill from a successful pipeline run. Returns skill file path."""
        if quality_score < 0.80:
            return None  # Only extract high-quality patterns

        skill_name = self._derive_skill_name(pipeline_name, task_type)
        skill_path = self.skills_dir / f"{skill_name}.md"

        # Don't overwrite existing manually-created skills
        if skill_path.exists() and not str(skill_path).startswith(str(GENERATED_SKILLS_DIR)):
            return None

        self._ensure_dir()
        skill = self._build_skill(pipeline_name, task_description, task_type, phases_completed, run_id)
        skill_path.write_text(self._render_skill(skill), encoding="utf-8")
        return skill_path

    def generate_from_episodic(self, episodic_data: list[dict]) -> list[Path]:
        """Scan episodic memories for successful patterns and generate skills."""
        generated = []
        # Group by data_type
        by_type: dict[str, list[dict]] = {}
        for e in episodic_data:
            dtype = e.get("data_type", "general")
            by_type.setdefault(dtype, []).append(e)

        for dtype, entries in by_type.items():
            if len(entries) >= 3:  # Only generate if we have 3+ examples
                high_quality = [e for e in entries if float(e.get("importance", 0)) > 0.75]
                if len(high_quality) >= 2:
                    path = self._generate_type_skill(dtype, high_quality)
                    if path:
                        generated.append(path)
        return generated

    def _derive_skill_name(self, pipeline_name: str, task_type: str) -> str:
        """Create a safe filename for the skill."""
        combined = f"{pipeline_name}-{task_type}".lower()
        return combined.replace(" ", "-").replace("_", "-")[:40]

    def _build_skill(
        self,
        pipeline_name: str,
        task_description: str,
        task_type: str,
        phases: dict,
        run_id: str | None,
    ) -> SkillTemplate:
        phases_str = ", ".join(str(p) for p in (phases or {}).keys())
        return SkillTemplate(
            name=self._derive_skill_name(pipeline_name, task_type),
            description=f"Auto-generated from successful {task_type} pipeline run",
            trigger=f"User requests {task_type} for: {task_description[:50]}",
            pipeline_type=task_type,
            prompt_template=f"Execute {pipeline_name} pipeline for: {{task}}\nPhases: {phases_str}",
            success_criteria=[
                f"All pipeline phases complete: {phases_str}",
                "Quality score > 0.80",
                "No unresolved errors",
            ],
            source_run_id=run_id,
        )

    def _generate_type_skill(self, dtype: str, examples: list[dict]) -> Path | None:
        """Generate a skill from a cluster of episodic memories of the same type."""
        skill_name = f"auto-{dtype.replace('_', '-')}"
        skill_path = self.skills_dir / f"{skill_name}.md"
        if skill_path.exists():
            return None  # Don't overwrite

        self._ensure_dir()
        example_text = "\n".join([
            f"Example {i+1}: {e.get('content', '')[:100]}..."
            for i, e in enumerate(examples[:3])
        ])

        content = f"""---
name: {skill_name}
auto_generated: true
generated_at: {datetime.now(timezone.utc).isoformat()}
source_type: episodic_cluster
data_type: {dtype}
example_count: {len(examples)}
---

# {skill_name} (Auto-Generated)

Auto-generated skill from {len(examples)} episodic memory examples of type `{dtype}`.

## Pattern Examples

{example_text}

## Trigger

Use when: task involves {dtype.replace('_', ' ')} operations or similar patterns.

## Instructions

Follow the established pattern from memory. Check jake_episodic for recent examples
of this pattern before executing. Store results back to episodic with data_type='{dtype}'.

## Success Criteria

- Result matches quality of historical examples
- Output stored to jake_episodic
- No PII in stored content
"""
        skill_path.write_text(content, encoding="utf-8")
        return skill_path

    def _render_skill(self, skill: SkillTemplate) -> str:
        criteria_text = "\n".join(f"- {c}" for c in skill.success_criteria)
        return f"""---
name: {skill.name}
auto_generated: true
generated_at: {datetime.now(timezone.utc).isoformat()}
source_run_id: {skill.source_run_id or 'unknown'}
pipeline_type: {skill.pipeline_type}
---

# {skill.name} (Auto-Generated Pipeline Skill)

{skill.description}

## Trigger

{skill.trigger}

## Prompt Template

```
{skill.prompt_template}
```

## Success Criteria

{criteria_text}

## Notes

This skill was automatically generated from a successful pipeline run.
Review and edit before promoting to production skills.
"""

    def list_generated(self) -> list[Path]:
        """List all auto-generated skills."""
        if not self.skills_dir.exists():
            return []
        return list(self.skills_dir.glob("*.md"))

    def report(self) -> str:
        """Report on auto-generated skills."""
        skills = self.list_generated()
        if not skills:
            return "No auto-generated skills yet."
        lines = [f"Auto-generated skills ({len(skills)} total):"]
        for s in skills:
            lines.append(f"  • {s.stem}")
        return "\n".join(lines)


skill_generator = SkillGenerator()
