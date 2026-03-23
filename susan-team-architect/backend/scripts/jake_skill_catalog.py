#!/usr/bin/env python3
"""Jake Skill Catalog — full skill marketplace across Hermes, auto-generated, and Susan agents.

Shows Mike every capability Jake has: manual Hermes skills, auto-generated skills,
and Susan agent definitions.

Run: on demand
  python jake_skill_catalog.py
  python jake_skill_catalog.py --json      # machine-readable output
  python jake_skill_catalog.py --summary   # totals only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

HERMES_SKILLS_DIR = Path.home() / ".hermes" / "skills"
GENERATED_SKILLS_DIR = HERMES_SKILLS_DIR / "_auto_generated"
AGENTS_DIR = Path("/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/agents")

# Box-drawing chars
BOX_TOP = "╔══════════════════════════════════════╗"
BOX_MID = "║  Jake Skill Marketplace               ║"
BOX_BOT = "╚══════════════════════════════════════╝"


# ---------------------------------------------------------------------------
# Env loader (needed if we ever query Supabase here)
# ---------------------------------------------------------------------------

def load_env() -> None:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


# ---------------------------------------------------------------------------
# YAML frontmatter parser (no external deps)
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter between --- markers. Returns {} if none found."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}
    fm: dict = {}
    for line in lines[1:end]:
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def read_skill_meta(skill_dir: Path) -> dict | None:
    """Read metadata from a skill directory (has SKILL.md) or a plain .md file."""
    if skill_dir.is_dir():
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        name = fm.get("name") or skill_dir.name
        description = fm.get("description", "No description")
        auto = fm.get("auto_generated", "false").lower() == "true"
        generated_at = fm.get("generated_at", "")
        return {
            "name": name,
            "description": description,
            "auto_generated": auto,
            "generated_at": generated_at,
            "path": str(skill_md),
        }
    elif skill_dir.suffix == ".md":
        text = skill_dir.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        name = fm.get("name") or skill_dir.stem
        description = fm.get("description", "No description")
        auto = fm.get("auto_generated", "false").lower() == "true"
        generated_at = fm.get("generated_at", "")
        return {
            "name": name,
            "description": description,
            "auto_generated": auto,
            "generated_at": generated_at,
            "path": str(skill_dir),
        }
    return None


# ---------------------------------------------------------------------------
# Skill scanners
# ---------------------------------------------------------------------------

def scan_hermes_skills() -> tuple[list[dict], list[dict]]:
    """Return (manual_skills, auto_generated_skills)."""
    manual: list[dict] = []
    auto_gen: list[dict] = []

    if not HERMES_SKILLS_DIR.exists():
        return manual, auto_gen

    for entry in sorted(HERMES_SKILLS_DIR.iterdir()):
        # Skip _auto_generated dir — handled separately
        if entry.name == "_auto_generated":
            continue
        meta = read_skill_meta(entry)
        if meta is None:
            continue
        if meta["auto_generated"]:
            auto_gen.append(meta)
        else:
            manual.append(meta)

    # Now scan _auto_generated dir (both .md files and subdirs)
    if GENERATED_SKILLS_DIR.exists():
        for entry in sorted(GENERATED_SKILLS_DIR.iterdir()):
            meta = read_skill_meta(entry)
            if meta is None:
                continue
            meta["auto_generated"] = True
            auto_gen.append(meta)

    return manual, auto_gen


def scan_agents() -> list[dict]:
    """Scan Susan agents directory for agent definitions."""
    agents: list[dict] = []

    if not AGENTS_DIR.exists():
        return agents

    for md_file in sorted(AGENTS_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)

        # Fall back to extracting name from first heading or filename
        name = fm.get("name") or fm.get("agent_name") or md_file.stem
        description = fm.get("description") or fm.get("role") or ""

        # If no frontmatter description, try first non-empty line after headers
        if not description:
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("---") and len(line) > 10:
                    description = line[:120]
                    break

        agents.append({
            "name": name,
            "description": description or "Susan agent",
            "path": str(md_file),
        })

    return agents


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def _truncate(text: str, max_len: int = 72) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) > max_len:
        return text[:max_len - 1] + "…"
    return text


def print_catalog(manual: list[dict], auto_gen: list[dict], agents: list[dict]) -> None:
    total = len(manual) + len(auto_gen) + len(agents)

    print(BOX_TOP)
    print(BOX_MID)
    print(BOX_BOT)
    print()

    # Manual Hermes skills
    print(f"HERMES SKILLS (manual): {len(manual)}")
    if manual:
        for s in manual:
            desc = _truncate(s["description"], 72)
            print(f"  • {s['name']:<32} — {desc}")
    else:
        print("  (none yet)")
    print()

    # Auto-generated skills
    print(f"AUTO-GENERATED SKILLS: {len(auto_gen)}")
    if auto_gen:
        for s in auto_gen:
            date_str = s.get("generated_at", "")[:10] if s.get("generated_at") else "unknown"
            desc = _truncate(s["description"], 60)
            print(f"  • {s['name']:<32} (generated {date_str}) — {desc}")
    else:
        print("  (none yet — run jake_skill_harvest.py to generate)")
    print()

    # Susan agents
    print(f"SUSAN AGENTS: {len(agents)}")
    if agents:
        for a in agents:
            desc = _truncate(a["description"], 72)
            print(f"  • {a['name']:<32} — {desc}")
    else:
        print("  (no agents found)")
    print()

    # Total
    print("─" * 60)
    print(f"TOTAL: {total} capabilities available to Jake")
    print()


def print_summary(manual: list[dict], auto_gen: list[dict], agents: list[dict]) -> None:
    total = len(manual) + len(auto_gen) + len(agents)
    print(f"Hermes manual skills  : {len(manual)}")
    print(f"Auto-generated skills : {len(auto_gen)}")
    print(f"Susan agents          : {len(agents)}")
    print(f"Total capabilities    : {total}")


def print_json(manual: list[dict], auto_gen: list[dict], agents: list[dict]) -> None:
    output = {
        "hermes_manual": manual,
        "auto_generated": auto_gen,
        "susan_agents": agents,
        "total": len(manual) + len(auto_gen) + len(agents),
    }
    print(json.dumps(output, indent=2, default=str))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Jake Skill Catalog — full capability marketplace")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true", help="Print totals only")
    args = parser.parse_args()

    load_env()

    manual, auto_gen = scan_hermes_skills()
    agents = scan_agents()

    if args.json:
        print_json(manual, auto_gen, agents)
    elif args.summary:
        print_summary(manual, auto_gen, agents)
    else:
        print_catalog(manual, auto_gen, agents)


if __name__ == "__main__":
    main()
