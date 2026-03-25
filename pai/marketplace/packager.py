"""Pattern & Skill Packager — V9 Marketplace

Packages battle-tested Fabric patterns and OpenClaw skills for distribution.

Workflow:
  1. Audit patterns: usage count, satisfaction rating, failure rate
  2. Select patterns with: 10+ uses, >4.0 avg rating, <5% failure
  3. Clean up (remove personal context, generalize)
  4. Package as ClawHub-compatible format
  5. Generate README, examples, configuration docs

Also handles TELOS onboarding wizard for other founders.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class PackageablePattern:
    """A pattern ready for marketplace distribution."""
    name: str
    description: str
    category: str  # "competitive", "decision", "meeting", "research", etc.
    usage_count: int = 0
    avg_rating: float = 0
    failure_rate: float = 0
    system_prompt: str = ""
    user_prompt_template: str = ""
    example_input: str = ""
    example_output: str = ""
    version: str = "1.0.0"
    author: str = "Jake PAI"
    license: str = "MIT"
    tags: list[str] = field(default_factory=list)

    def meets_quality_bar(self) -> bool:
        """Check if pattern meets marketplace quality thresholds."""
        return (
            self.usage_count >= 10
            and self.avg_rating >= 4.0
            and self.failure_rate < 0.05
        )

    def to_package_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "author": self.author,
            "license": self.license,
            "tags": self.tags,
            "stats": {
                "usage_count": self.usage_count,
                "avg_rating": self.avg_rating,
                "failure_rate": self.failure_rate,
            },
        }


@dataclass
class TELOSTemplate:
    """A TELOS onboarding template for other founders."""
    name: str
    description: str
    files: dict[str, str]  # filename → content template
    required_inputs: list[str] = field(default_factory=list)
    optional_inputs: list[str] = field(default_factory=list)


class MarketplacePackager:
    """Package patterns and skills for distribution."""

    PATTERNS_DIR = Path(__file__).parent / "patterns"
    PACKAGES_DIR = Path(__file__).parent / "packages"
    CUSTOM_PATTERNS_DIR = Path(__file__).parent.parent / "patterns" / "custom"

    def __init__(self):
        self.PACKAGES_DIR.mkdir(parents=True, exist_ok=True)

    def audit_patterns(self) -> list[PackageablePattern]:
        """Audit all custom patterns for marketplace readiness."""
        patterns = []
        if not self.CUSTOM_PATTERNS_DIR.exists():
            return patterns

        for pattern_dir in self.CUSTOM_PATTERNS_DIR.iterdir():
            if not pattern_dir.is_dir():
                continue

            meta_file = pattern_dir / "metadata.json"
            if not meta_file.exists():
                continue

            try:
                meta = json.loads(meta_file.read_text())
                system_prompt = ""
                system_file = pattern_dir / "system.md"
                if system_file.exists():
                    system_prompt = system_file.read_text()

                patterns.append(PackageablePattern(
                    name=meta.get("name", pattern_dir.name),
                    description=meta.get("description", ""),
                    category=meta.get("category", "general"),
                    usage_count=meta.get("usage_count", 0),
                    avg_rating=meta.get("avg_rating", 0),
                    failure_rate=meta.get("failure_rate", 0),
                    system_prompt=system_prompt,
                    tags=meta.get("tags", []),
                ))
            except (json.JSONDecodeError, OSError):
                continue

        return patterns

    def package_pattern(self, pattern: PackageablePattern) -> Path:
        """Package a pattern for distribution."""
        pkg_dir = self.PACKAGES_DIR / pattern.name
        pkg_dir.mkdir(parents=True, exist_ok=True)

        # Write package.json
        (pkg_dir / "package.json").write_text(
            json.dumps(pattern.to_package_json(), indent=2)
        )

        # Write system prompt (generalized — no personal context)
        if pattern.system_prompt:
            generalized = self._generalize_prompt(pattern.system_prompt)
            (pkg_dir / "system.md").write_text(generalized)

        # Write user prompt template
        if pattern.user_prompt_template:
            (pkg_dir / "user.md").write_text(pattern.user_prompt_template)

        # Write README
        readme = self._generate_readme(pattern)
        (pkg_dir / "README.md").write_text(readme)

        return pkg_dir

    def generate_telos_template(self) -> TELOSTemplate:
        """Generate a TELOS onboarding wizard template for other founders."""
        return TELOSTemplate(
            name="TELOS Founder Onboarding",
            description="Structured self-knowledge framework for AI-first founders",
            required_inputs=[
                "founder_name", "company_name", "role",
                "top_3_goals", "communication_style",
            ],
            optional_inputs=[
                "family_context", "work_schedule", "vip_contacts",
                "decision_style", "learning_preferences",
            ],
            files={
                "IDENTITY.md": "# Identity\n\nName: {founder_name}\nRole: {role}\nCompany: {company_name}\n",
                "GOALS.md": "# Goals\n\n{top_3_goals}\n",
                "SOUL.md": "# Soul\n\nCommunication style: {communication_style}\n",
                "LEARNED.md": "# Learned\n\n(Empty — Jake learns from interactions)\n",
                "WRONG.md": "# Wrong\n\n(Empty — Jake tracks mistakes here)\n",
            },
        )

    def _generalize_prompt(self, prompt: str) -> str:
        """Remove personal context from a prompt for distribution."""
        replacements = {
            "Mike": "{user_name}",
            "Oracle Health": "{company_1}",
            "Alex Recruiting": "{company_2}",
            "Startup Intelligence OS": "{company_3}",
            "Jacob": "{family_member}",
            "James": "{family_member}",
            "Matt Cohlmia": "{vip_contact}",
        }
        result = prompt
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result

    def _generate_readme(self, pattern: PackageablePattern) -> str:
        """Generate README for a packaged pattern."""
        return f"""# {pattern.name}

{pattern.description}

## Stats
- Usage: {pattern.usage_count} invocations
- Rating: {pattern.avg_rating}/5.0
- Failure rate: {pattern.failure_rate:.1%}

## Category
{pattern.category}

## Tags
{', '.join(pattern.tags)}

## Usage
```
fabric -p {pattern.name} < input.txt
```

## License
{pattern.license}
"""
