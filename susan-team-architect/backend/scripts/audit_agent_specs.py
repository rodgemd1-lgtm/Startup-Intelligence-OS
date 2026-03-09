"""Audit agent markdown files against the expertise manifest."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT.parent / "agents"
MANIFEST_PATH = ROOT / "data" / "agent_expertise" / "manifest.yaml"


def headings(text: str) -> set[str]:
    return {match.group(1).strip() for match in re.finditer(r"^##\s+(.*)$", text, re.MULTILINE)}


def main() -> int:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    required = set(manifest["required_sections"])
    findings = []

    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        content = agent_file.read_text(encoding="utf-8")
        present = headings(content)
        missing = sorted(required - present)
        findings.append(
            {
                "agent": agent_file.stem,
                "missing_sections": missing,
                "passes": not missing,
            }
        )

    print(json.dumps(findings, indent=2))
    return 0 if all(item["passes"] for item in findings) else 1


if __name__ == "__main__":
    raise SystemExit(main())
