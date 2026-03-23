#!/usr/bin/env python3
"""Jake Identity Consistency Check — verify Jake is the same across all systems."""
import os
import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

# ── Personality keywords to scan for ──────────────────────────────────────────
PERSONALITY_KEYWORDS = [
    "sassy", "15", "prodigy", "pushback", "push back", "humor",
    "roast", "co-founder", "cofounder", "irreverent", "teenager",
    "partner", "challenger",
]

ROLE_KEYWORDS = [
    "co-founder", "cofounder", "assistant", "advisor", "operator",
    "strategist", "conductor", "guardian",
]


# ── Env loader ────────────────────────────────────────────────────────────────
def load_env() -> None:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


# ── Source checkers ───────────────────────────────────────────────────────────
def check_hermes_soul() -> dict:
    soul_path = Path.home() / ".hermes" / "SOUL.md"
    result = {"source": "Hermes SOUL.md", "found": False, "path": str(soul_path),
              "name": None, "role": None, "traits": []}
    if not soul_path.exists():
        return result

    text = soul_path.read_text(errors="replace")
    result["found"] = True

    # Name
    name_match = re.search(r"\*\*Name\*\*[:\s]+(\w+)", text)
    if name_match:
        result["name"] = name_match.group(1)
    elif "Jake" in text[:200]:
        result["name"] = "Jake"

    # Role
    role_match = re.search(r"\*\*Role\*\*[:\s]+(.+)", text)
    if role_match:
        result["role"] = role_match.group(1).strip()
    else:
        found_roles = [kw for kw in ROLE_KEYWORDS if kw.lower() in text.lower()]
        result["role"] = ", ".join(found_roles[:3]) if found_roles else None

    # Traits
    result["traits"] = [kw for kw in PERSONALITY_KEYWORDS if kw.lower() in text.lower()]
    return result


def check_claude_md() -> dict:
    claude_md_path = Path("/Users/mikerodgers/Startup-Intelligence-OS/CLAUDE.md")
    result = {"source": "Claude Code CLAUDE.md", "found": False, "path": str(claude_md_path),
              "name": None, "role": None, "traits": []}
    if not claude_md_path.exists():
        return result

    text = claude_md_path.read_text(errors="replace")
    result["found"] = True

    # Name — look for "Jake" as the identity
    if "Jake" in text:
        result["name"] = "Jake"

    # Role — extract from Identity Layer section
    role_match = re.search(r"Jake is[:\n\-\s]+([\w ,/\-]+)", text)
    if role_match:
        result["role"] = role_match.group(1).strip()[:80]
    else:
        found_roles = [kw for kw in ROLE_KEYWORDS if kw.lower() in text.lower()]
        result["role"] = ", ".join(found_roles[:3]) if found_roles else None

    result["traits"] = [kw for kw in PERSONALITY_KEYWORDS if kw.lower() in text.lower()]
    return result


def check_brain_entity() -> dict:
    result = {"source": "Brain Entity (Supabase jake_entities)", "found": False,
              "entity_name": None, "entity_type": None, "attributes": None, "error": None}
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        result["error"] = "SUPABASE_URL or SUPABASE_SERVICE_KEY not set"
        return result

    try:
        from supabase import create_client
        client = create_client(url, key)
        rows = client.table("jake_entities").select("*").ilike("name", "jake").execute()
        if rows.data:
            entity = rows.data[0]
            result["found"] = True
            result["entity_name"] = entity.get("name")
            result["entity_type"] = entity.get("entity_type")
            result["attributes"] = entity.get("properties") or entity.get("metadata")
        else:
            result["error"] = "No entity named 'jake' found in jake_entities"
    except Exception as exc:
        result["error"] = f"Supabase error: {exc}"

    return result


def check_employee_registry() -> dict:
    result = {"source": "Employee Registry (jake_brain/employees)", "found": False,
              "count": 0, "actors": [], "jake_prefix_consistent": False, "error": None}
    try:
        from jake_brain.employees import EMPLOYEE_REGISTRY
        result["found"] = True
        result["count"] = len(EMPLOYEE_REGISTRY)
        result["actors"] = [spec.actor for spec in EMPLOYEE_REGISTRY.values()]
        # Convention check: all actors should be snake_case descriptive names
        # (they don't need jake_ prefix — employees are Jake's workers, not Jake himself)
        result["jake_prefix_consistent"] = all(
            "_" in actor for actor in result["actors"]
        )
    except Exception as exc:
        result["error"] = f"Import error: {exc}"
    return result


# ── Comparison logic ──────────────────────────────────────────────────────────
def compare_identities(sources: dict) -> tuple[bool, list[str]]:
    issues = []
    checks_passed = []

    soul = sources.get("soul", {})
    claude = sources.get("claude", {})
    brain = sources.get("brain", {})
    employees = sources.get("employees", {})

    # --- Name check ---
    names = {}
    if soul.get("found") and soul.get("name"):
        names["Hermes SOUL.md"] = soul["name"]
    if claude.get("found") and claude.get("name"):
        names["Claude Code CLAUDE.md"] = claude["name"]

    if names:
        unique_names = set(names.values())
        if len(unique_names) == 1:
            checks_passed.append(f"Name matches across all sources: {list(unique_names)[0]}")
        else:
            issues.append(f"Name mismatch: {names}")
    else:
        issues.append("Name 'Jake' not found in any readable source")

    # --- Role check ---
    roles = {}
    if soul.get("found") and soul.get("role"):
        roles["soul"] = soul["role"]
    if claude.get("found") and claude.get("role"):
        roles["claude"] = claude["role"]

    if roles:
        # Soft check — look for overlap in role keywords
        all_role_text = " ".join(roles.values()).lower()
        matched = [kw for kw in ROLE_KEYWORDS if kw in all_role_text]
        if matched:
            checks_passed.append(f"Role keywords present across sources: {matched[:4]}")
        else:
            issues.append(f"Role descriptions found but no shared keywords: {roles}")
    else:
        issues.append("No role information found in any source")

    # --- Trait overlap ---
    trait_sets = []
    if soul.get("traits"):
        trait_sets.append(set(soul["traits"]))
    if claude.get("traits"):
        trait_sets.append(set(claude["traits"]))

    if len(trait_sets) >= 2:
        overlap = trait_sets[0] & trait_sets[1]
        if overlap:
            checks_passed.append(f"Personality traits overlap: {sorted(overlap)}")
        else:
            issues.append("No overlapping personality traits between SOUL.md and CLAUDE.md")
    elif len(trait_sets) == 1:
        checks_passed.append(f"Personality traits found in one source: {sorted(trait_sets[0])}")

    # --- Brain entity check ---
    if brain.get("found"):
        checks_passed.append(
            f"Brain entity exists: '{brain['entity_name']}' (type={brain['entity_type']})"
        )
    elif brain.get("error"):
        issues.append(f"Brain entity: {brain['error']}")
    else:
        issues.append("Brain entity for Jake not found in jake_entities")

    # --- Employee registry check ---
    if employees.get("found"):
        checks_passed.append(
            f"Employee registry loaded: {employees['count']} employees defined"
        )
    elif employees.get("error"):
        issues.append(f"Employee registry: {employees['error']}")

    consistent = len(issues) == 0
    return consistent, checks_passed, issues


# ── Pretty printing ───────────────────────────────────────────────────────────
def print_source(info: dict) -> None:
    icon = "✓" if info["found"] else "✗"
    status = "" if info["found"] else " — NOT FOUND"
    print(f"\nSource: {info['source']} {icon}{status}")

    if not info["found"]:
        if info.get("error"):
            print(f"  Error: {info['error']}")
        elif info.get("path"):
            print(f"  Path:  {info['path']}")
        return

    if "name" in info and info["name"]:
        print(f"  Name:  {info['name']}")
    if "role" in info and info["role"]:
        print(f"  Role:  {info['role']}")
    if "traits" in info and info["traits"]:
        print(f"  Traits: {info['traits']}")

    # Brain-specific
    if "entity_name" in info:
        print(f"  entity_name: {info['entity_name']}")
        print(f"  entity_type: {info['entity_type']}")
        if info.get("attributes"):
            print(f"  attributes:  {info['attributes']}")
    if info.get("error"):
        print(f"  Warning: {info['error']}")

    # Employee-specific
    if "count" in info:
        print(f"  Employees defined: {info['count']}")
        print(f"  Actors: {info['actors']}")
        print(f"  All actors snake_case: {info['jake_prefix_consistent']}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    load_env()

    print("╔══════════════════════════════════╗")
    print("║  Jake Identity Consistency Check ║")
    print("╚══════════════════════════════════╝")

    soul = check_hermes_soul()
    claude = check_claude_md()
    brain = check_brain_entity()
    employees = check_employee_registry()

    for info in [soul, claude, brain, employees]:
        print_source(info)

    sources = {"soul": soul, "claude": claude, "brain": brain, "employees": employees}
    consistent, passed, issues = compare_identities(sources)

    print("\nCONSISTENCY CHECK:")
    for check in passed:
        print(f"  ✓ {check}")
    for issue in issues:
        print(f"  ✗ {issue}")

    print()
    if consistent:
        print("RESULT: CONSISTENT ✓")
        return 0
    else:
        print(f"RESULT: {len(issues)} ISSUE(S) FOUND ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
