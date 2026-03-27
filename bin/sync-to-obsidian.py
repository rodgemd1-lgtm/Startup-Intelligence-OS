#!/usr/bin/env python3
"""
Sync all Intelligence OS data to the JakeStudio Obsidian vault.
Copies agents, plans, docs, memory, decisions, capabilities → organized vault folders.
Adds Obsidian-compatible frontmatter where missing. Creates folder index (MOC) pages.
"""

import os
import shutil
import re
import yaml
from pathlib import Path
from datetime import datetime

# === PATHS ===
REPO = Path("/Users/mikerodgers/Startup-Intelligence-OS")
VAULT = Path("/Users/mikerodgers/Obsidian/JakeStudio")
MEMORY = Path("/Users/mikerodgers/.claude/projects/-Users-mikerodgers-Startup-Intelligence-OS/memory")
CLAUDE_AGENTS = REPO / ".claude" / "agents"
SUSAN_AGENTS = REPO / "susan-team-architect" / "agents"
CLAUDE_PLANS = REPO / ".claude" / "plans"
DOCS_PLANS = REPO / "docs" / "plans"
DOCS = REPO / "docs"
RULES = REPO / ".claude" / "rules"
STARTUP_OS = REPO / ".startup-os"

# === STATS ===
stats = {"copied": 0, "skipped": 0, "updated": 0, "indexes": 0}


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def has_frontmatter(content: str) -> bool:
    return content.strip().startswith("---")


def add_obsidian_frontmatter(content: str, tags: list[str], source: str, title: str = "") -> str:
    """Add Obsidian frontmatter if missing. Preserve existing frontmatter."""
    if has_frontmatter(content):
        # Inject obsidian tags into existing frontmatter
        lines = content.split("\n")
        end_idx = content.index("---", 3)
        front = content[3:end_idx].strip()
        body = content[end_idx + 3:].strip()
        # Add source tag if not present
        if "obsidian_source:" not in front:
            front += f"\nobsidian_source: {source}"
        if "obsidian_tags:" not in front:
            front += f"\nobsidian_tags: [{', '.join(tags)}]"
        return f"---\n{front}\n---\n\n{body}"
    else:
        fm = f"---\ntitle: {title or 'Untitled'}\ntags: [{', '.join(tags)}]\nsource: {source}\nsynced: {datetime.now().strftime('%Y-%m-%d')}\n---\n\n"
        return fm + content


def yaml_to_md(yaml_path: Path, tags: list[str], source: str) -> str:
    """Convert a YAML file to readable Obsidian markdown."""
    raw = yaml_path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        data = {}

    if not isinstance(data, dict):
        return add_obsidian_frontmatter(f"```yaml\n{raw}\n```", tags, source, yaml_path.stem)

    title = data.get("name", data.get("title", yaml_path.stem))
    desc = data.get("description", data.get("summary", ""))
    status = data.get("status", data.get("state", ""))

    lines = [f"# {title}", ""]
    if desc:
        lines += [f"> {desc}", ""]
    if status:
        lines += [f"**Status**: {status}", ""]

    # Render all fields as a readable table
    lines.append("## Properties")
    lines.append("")
    for k, v in data.items():
        if k in ("name", "title", "description", "summary"):
            continue
        if isinstance(v, (list, dict)):
            lines.append(f"**{k}**:")
            lines.append(f"```yaml\n{yaml.dump(v, default_flow_style=False).strip()}\n```")
        else:
            lines.append(f"**{k}**: {v}")
    lines.append("")

    content = "\n".join(lines)
    return add_obsidian_frontmatter(content, tags, source, title)


def sync_md_files(src_dir: Path, dest_dir: Path, tags: list[str], source_label: str, recursive: bool = False):
    """Copy .md files from src to dest with frontmatter injection."""
    ensure_dir(dest_dir)
    if not src_dir.exists():
        return

    pattern = "**/*.md" if recursive else "*.md"
    for md_file in sorted(src_dir.glob(pattern)):
        if md_file.name.startswith("."):
            continue

        rel = md_file.relative_to(src_dir)
        dest_file = dest_dir / rel
        ensure_dir(dest_file.parent)

        content = md_file.read_text(encoding="utf-8", errors="replace")
        enriched = add_obsidian_frontmatter(content, tags, source_label, md_file.stem)

        if dest_file.exists():
            existing = dest_file.read_text(encoding="utf-8", errors="replace")
            if existing.strip() == enriched.strip():
                stats["skipped"] += 1
                continue
            stats["updated"] += 1
        else:
            stats["copied"] += 1

        dest_file.write_text(enriched, encoding="utf-8")


def sync_yaml_files(src_dir: Path, dest_dir: Path, tags: list[str], source_label: str):
    """Convert .yaml files to .md and copy to dest."""
    ensure_dir(dest_dir)
    if not src_dir.exists():
        return

    for yaml_file in sorted(src_dir.glob("*.yaml")):
        if yaml_file.name.startswith("."):
            continue

        dest_file = dest_dir / (yaml_file.stem + ".md")
        content = yaml_to_md(yaml_file, tags, source_label)

        if dest_file.exists():
            existing = dest_file.read_text(encoding="utf-8", errors="replace")
            if existing.strip() == content.strip():
                stats["skipped"] += 1
                continue
            stats["updated"] += 1
        else:
            stats["copied"] += 1

        dest_file.write_text(content, encoding="utf-8")


def create_folder_index(folder: Path, title: str, description: str):
    """Create an _Index.md MOC (Map of Content) for a folder."""
    ensure_dir(folder)
    md_files = sorted([f for f in folder.rglob("*.md") if f.name != "_Index.md"])

    lines = [
        "---",
        f"title: {title}",
        "tags: [index, moc]",
        f"updated: {datetime.now().strftime('%Y-%m-%d')}",
        "---",
        "",
        f"# {title}",
        "",
        f"> {description}",
        "",
        f"**{len(md_files)} documents**",
        "",
    ]

    # Group by subfolder
    by_folder: dict[str, list[Path]] = {}
    for f in md_files:
        rel = f.relative_to(folder)
        group = str(rel.parent) if str(rel.parent) != "." else "Root"
        by_folder.setdefault(group, []).append(f)

    for group, files in sorted(by_folder.items()):
        if group != "Root":
            lines.append(f"## {group}")
            lines.append("")
        for f in files:
            name = f.stem
            rel_link = f.relative_to(folder)
            lines.append(f"- [[{rel_link.with_suffix('')}|{name}]]")
        lines.append("")

    index_path = folder / "_Index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    stats["indexes"] += 1


def create_master_index():
    """Create master MOC at vault root."""
    folders = sorted([d for d in VAULT.iterdir() if d.is_dir() and not d.name.startswith(".")])

    total_files = len(list(VAULT.rglob("*.md")))

    lines = [
        "---",
        "title: JakeStudio — Master Index",
        "tags: [index, moc, master]",
        f"updated: {datetime.now().strftime('%Y-%m-%d')}",
        "---",
        "",
        "# JakeStudio — Intelligence OS Vault",
        "",
        f"> Mike Rodgers' unified knowledge base. **{total_files} documents** synced from the Startup Intelligence OS.",
        "",
        "## Navigation",
        "",
    ]

    folder_descriptions = {
        "Agents": "All 104 agents — Claude root agents + Susan specialist agents",
        "Capabilities": "27 capability records from the Decision & Capability OS",
        "Companies": "Company profiles and operating models",
        "Daily Notes": "Daily logs and session notes",
        "Decisions": "18 decision records with rationale and status",
        "Docs": "Reference documentation, research, design docs",
        "Memory": "Jake's persistent memory — preferences, feedback, project context",
        "People": "Key contacts and relationship context",
        "Plans": "108 implementation plans, designs, and roadmaps",
        "Projects": "Active project records and portfolio overview",
        "Reference": "Rules, conventions, and reference material",
    }

    for folder in folders:
        name = folder.name
        count = len(list(folder.rglob("*.md")))
        desc = folder_descriptions.get(name, "")
        lines.append(f"### [[{name}/_Index|{name}]]")
        if desc:
            lines.append(f"{desc}")
        lines.append(f"*{count} documents*")
        lines.append("")

    lines += [
        "## Quick Links",
        "",
        "- [[Agents/Claude/_Index|Claude Agents]] — Root orchestration layer",
        "- [[Agents/Susan/_Index|Susan Agents]] — Specialist foundry",
        "- [[Memory/_Index|Jake's Memory]] — What Jake knows about Mike",
        "- [[Plans/_Index|All Plans]] — Past and current implementation plans",
        "- [[Decisions/_Index|Decision Log]] — Every major decision with rationale",
        "",
        "---",
        f"*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"*Source: Startup Intelligence OS (`~/Startup-Intelligence-OS`)*",
    ]

    (VAULT / "_Index.md").write_text("\n".join(lines), encoding="utf-8")
    stats["indexes"] += 1


def main():
    print("=== JakeStudio Vault Sync ===")
    print(f"Vault: {VAULT}")
    print()

    # 1. Claude Agents
    print("Syncing Claude agents...")
    sync_md_files(CLAUDE_AGENTS, VAULT / "Agents" / "Claude", ["agent", "claude"], "claude-agents")

    # 2. Susan Agents
    print("Syncing Susan agents...")
    sync_md_files(SUSAN_AGENTS, VAULT / "Agents" / "Susan", ["agent", "susan"], "susan-agents")

    # 3. Plans (merged from two sources)
    print("Syncing plans (.claude)...")
    sync_md_files(CLAUDE_PLANS, VAULT / "Plans" / "Claude", ["plan", "claude"], "claude-plans")

    print("Syncing plans (docs)...")
    sync_md_files(DOCS_PLANS, VAULT / "Plans" / "Docs", ["plan", "docs"], "docs-plans", recursive=True)

    # 4. Docs (non-plans)
    print("Syncing docs...")
    for subdir in sorted(DOCS.iterdir()):
        if subdir.is_dir() and subdir.name != "plans":
            sync_md_files(subdir, VAULT / "Docs" / subdir.name, ["docs", subdir.name], f"docs-{subdir.name}", recursive=True)
    # Root-level docs
    for md in sorted(DOCS.glob("*.md")):
        dest = VAULT / "Docs" / md.name
        ensure_dir(dest.parent)
        content = md.read_text(encoding="utf-8", errors="replace")
        enriched = add_obsidian_frontmatter(content, ["docs"], "docs-root", md.stem)
        if not dest.exists():
            dest.write_text(enriched, encoding="utf-8")
            stats["copied"] += 1
        else:
            stats["skipped"] += 1

    # 5. Memory files
    print("Syncing memory files...")
    sync_md_files(MEMORY, VAULT / "Memory", ["memory", "jake"], "jake-memory")

    # 6. Rules
    print("Syncing rules...")
    sync_md_files(RULES, VAULT / "Reference" / "Rules", ["rules", "reference"], "claude-rules")

    # 7. Decisions (YAML → MD)
    print("Syncing decisions...")
    sync_yaml_files(STARTUP_OS / "decisions", VAULT / "Decisions", ["decision", "startup-os"], "startup-os-decisions")

    # 8. Capabilities (YAML → MD)
    print("Syncing capabilities...")
    sync_yaml_files(STARTUP_OS / "capabilities", VAULT / "Capabilities", ["capability", "startup-os"], "startup-os-capabilities")

    # 9. Companies (YAML → MD)
    print("Syncing companies...")
    sync_yaml_files(STARTUP_OS / "companies", VAULT / "Companies", ["company", "startup-os"], "startup-os-companies")

    # 10. Projects (YAML → MD)
    print("Syncing projects...")
    sync_yaml_files(STARTUP_OS / "projects", VAULT / "Projects", ["project", "startup-os"], "startup-os-projects")

    # === CREATE INDEXES ===
    print("\nCreating folder indexes...")
    create_folder_index(VAULT / "Agents" / "Claude", "Claude Agents", "Root orchestration agents — Jake, KIRA, ARIA, LEDGER, Orchestrator, and more")
    create_folder_index(VAULT / "Agents" / "Susan", "Susan Agents", "85 specialist agents across strategy, product, engineering, science, growth, research, and studio departments")
    create_folder_index(VAULT / "Agents", "All Agents", "Complete agent roster — 104 agents across Claude root layer and Susan specialist foundry")
    create_folder_index(VAULT / "Plans", "Plans", "Implementation plans, designs, roadmaps, and research findings")
    create_folder_index(VAULT / "Docs", "Documentation", "Reference docs, research, design documents, SOPs, and battlecards")
    create_folder_index(VAULT / "Memory", "Jake's Memory", "Persistent memory about Mike — preferences, feedback, project context, relationships")
    create_folder_index(VAULT / "Decisions", "Decision Log", "Major decisions from the Decision & Capability OS with rationale and status")
    create_folder_index(VAULT / "Capabilities", "Capabilities", "Capability records — maturity levels, ownership, and roadmaps")
    create_folder_index(VAULT / "Reference", "Reference", "Rules, conventions, and reference material for the Intelligence OS")
    create_folder_index(VAULT / "Companies", "Companies", "Company profiles and operating models")
    create_folder_index(VAULT / "Projects", "Projects", "Active project records and portfolio overview")
    create_folder_index(VAULT / "People", "People", "Key contacts and relationship context")

    # Master index
    print("Creating master index...")
    create_master_index()

    # === SUMMARY ===
    print("\n=== SYNC COMPLETE ===")
    print(f"  Copied:  {stats['copied']}")
    print(f"  Updated: {stats['updated']}")
    print(f"  Skipped: {stats['skipped']} (unchanged)")
    print(f"  Indexes: {stats['indexes']}")
    print(f"  Total:   {stats['copied'] + stats['updated'] + stats['indexes']} new/updated files")


if __name__ == "__main__":
    main()
