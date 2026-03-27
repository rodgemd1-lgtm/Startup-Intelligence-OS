#!/usr/bin/env python3
"""
Sync Notion pages → Obsidian JakeStudio vault.

Reads all pages the Notion integration can access, converts blocks to markdown,
saves with Obsidian-compatible YAML frontmatter, and generates a folder MOC index.

Idempotent: skips pages unchanged since last sync (by last_edited_time).

Usage:
    python3 bin/sync-notion-obsidian.py
    python3 bin/sync-notion-obsidian.py --dry-run
    python3 bin/sync-notion-obsidian.py --verbose

Environment:
    NOTION_API_KEY or NOTION_API_TOKEN — Notion integration token
    Falls back to reading ~/.hermes/.env if not set in shell environment.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
VAULT_DIR = Path("/Users/mikerodgers/Obsidian/JakeStudio/Notion")
STATE_FILE = VAULT_DIR / ".sync-state.json"
INDEX_FILE = VAULT_DIR / "_Index.md"

DRY_RUN = "--dry-run" in sys.argv
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv


# ── Helpers ───────────────────────────────────────────────────────────

def log(msg: str):
    print(f"  {msg}")


def vlog(msg: str):
    if VERBOSE:
        print(f"  [debug] {msg}")


def load_env_file(path: str) -> dict:
    """Parse a KEY=VALUE env file, ignoring comments and blank lines."""
    env = {}
    p = Path(path)
    if not p.exists():
        return env
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip().strip("'\"")
    return env


def get_notion_token() -> str:
    """Resolve Notion API token from environment or ~/.hermes/.env."""
    token = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_API_TOKEN")
    if token:
        return token
    hermes_env = load_env_file(os.path.expanduser("~/.hermes/.env"))
    token = hermes_env.get("NOTION_API_KEY") or hermes_env.get("NOTION_API_TOKEN")
    if token:
        return token
    print("ERROR: No Notion token found. Set NOTION_API_KEY or add to ~/.hermes/.env")
    sys.exit(1)


def notion_request(path: str, method: str = "GET", body: dict | None = None) -> dict:
    """Make an authenticated request to the Notion API."""
    url = f"{NOTION_API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"ERROR: Notion API {e.code} on {path}: {error_body[:300]}")
        raise


# ── Notion Search (paginated) ────────────────────────────────────────

def search_all_pages() -> list[dict]:
    """Search for all pages the integration can access, handling pagination."""
    pages = []
    start_cursor = None
    while True:
        body = {"filter": {"value": "page", "property": "object"}, "page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor
        result = notion_request("/search", method="POST", body=body)
        pages.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        start_cursor = result.get("next_cursor")
    return pages


# ── Block → Markdown Conversion ──────────────────────────────────────

def rich_text_to_md(rich_texts: list[dict]) -> str:
    """Convert Notion rich_text array to markdown string."""
    parts = []
    for rt in rich_texts:
        text = rt.get("plain_text", "")
        annotations = rt.get("annotations", {})
        href = rt.get("href")
        if annotations.get("code"):
            text = f"`{text}`"
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"
        if href:
            text = f"[{text}]({href})"
        parts.append(text)
    return "".join(parts)


def get_block_children(block_id: str) -> list[dict]:
    """Fetch all child blocks for a given block, handling pagination."""
    blocks = []
    start_cursor = None
    while True:
        path = f"/blocks/{block_id}/children?page_size=100"
        if start_cursor:
            path += f"&start_cursor={start_cursor}"
        result = notion_request(path)
        blocks.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        start_cursor = result.get("next_cursor")
    return blocks


def blocks_to_markdown(blocks: list[dict], depth: int = 0) -> str:
    """Convert a list of Notion blocks into markdown text."""
    lines = []
    indent = "  " * depth

    for block in blocks:
        btype = block.get("type", "")
        bdata = block.get(btype, {})

        if btype == "paragraph":
            text = rich_text_to_md(bdata.get("rich_text", []))
            lines.append(f"{indent}{text}")
            lines.append("")

        elif btype in ("heading_1", "heading_2", "heading_3"):
            level = int(btype[-1])
            text = rich_text_to_md(bdata.get("rich_text", []))
            lines.append(f"{'#' * level} {text}")
            lines.append("")

        elif btype == "bulleted_list_item":
            text = rich_text_to_md(bdata.get("rich_text", []))
            lines.append(f"{indent}- {text}")

        elif btype == "numbered_list_item":
            text = rich_text_to_md(bdata.get("rich_text", []))
            lines.append(f"{indent}1. {text}")

        elif btype == "to_do":
            text = rich_text_to_md(bdata.get("rich_text", []))
            checked = bdata.get("checked", False)
            mark = "x" if checked else " "
            lines.append(f"{indent}- [{mark}] {text}")

        elif btype == "toggle":
            text = rich_text_to_md(bdata.get("rich_text", []))
            lines.append(f"{indent}<details><summary>{text}</summary>")
            lines.append("")

        elif btype == "code":
            text = rich_text_to_md(bdata.get("rich_text", []))
            lang = bdata.get("language", "")
            lines.append(f"{indent}```{lang}")
            lines.append(text)
            lines.append(f"{indent}```")
            lines.append("")

        elif btype == "quote":
            text = rich_text_to_md(bdata.get("rich_text", []))
            for qline in text.split("\n"):
                lines.append(f"{indent}> {qline}")
            lines.append("")

        elif btype == "callout":
            icon = bdata.get("icon", {}).get("emoji", "")
            text = rich_text_to_md(bdata.get("rich_text", []))
            lines.append(f"{indent}> {icon} {text}")
            lines.append("")

        elif btype == "divider":
            lines.append(f"{indent}---")
            lines.append("")

        elif btype == "image":
            img_data = bdata.get("file", bdata.get("external", {}))
            url = img_data.get("url", "")
            caption = rich_text_to_md(bdata.get("caption", []))
            lines.append(f"{indent}![{caption}]({url})")
            lines.append("")

        elif btype == "bookmark":
            url = bdata.get("url", "")
            caption = rich_text_to_md(bdata.get("caption", []))
            label = caption if caption else url
            lines.append(f"{indent}[{label}]({url})")
            lines.append("")

        elif btype == "table":
            # Tables need child rows fetched
            pass

        elif btype == "child_page":
            title = bdata.get("title", "Untitled")
            lines.append(f"{indent}**Sub-page:** [[{title}]]")
            lines.append("")

        elif btype == "child_database":
            title = bdata.get("title", "Untitled Database")
            lines.append(f"{indent}**Database:** {title}")
            lines.append("")

        elif btype == "embed":
            url = bdata.get("url", "")
            lines.append(f"{indent}[Embed]({url})")
            lines.append("")

        elif btype == "link_preview":
            url = bdata.get("url", "")
            lines.append(f"{indent}[Link]({url})")
            lines.append("")

        elif btype == "synced_block":
            # Synced blocks contain children
            pass

        elif btype == "column_list":
            # Column lists contain column children
            pass

        elif btype == "column":
            pass

        elif btype == "table_of_contents":
            lines.append(f"{indent}*[Table of Contents]*")
            lines.append("")

        else:
            vlog(f"Skipped unsupported block type: {btype}")

        # Recurse into children if present
        if block.get("has_children") and btype not in ("child_page", "child_database"):
            try:
                children = get_block_children(block["id"])
                child_md = blocks_to_markdown(children, depth=depth + 1)
                lines.append(child_md)
            except Exception as e:
                vlog(f"Could not fetch children for {block['id']}: {e}")

        # Close toggle
        if btype == "toggle":
            lines.append(f"{indent}</details>")
            lines.append("")

    return "\n".join(lines)


# ── Page Title Extraction ─────────────────────────────────────────────

def get_page_title(page: dict) -> str:
    """Extract the title from a Notion page object."""
    props = page.get("properties", {})
    # Try common title property names
    for key in ("title", "Title", "Name", "name"):
        prop = props.get(key, {})
        if prop.get("type") == "title":
            title_parts = prop.get("title", [])
            return rich_text_to_md(title_parts).strip() or "Untitled"
    # Fallback: scan all properties for a title type
    for prop in props.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            title_parts = prop.get("title", [])
            return rich_text_to_md(title_parts).strip() or "Untitled"
    return "Untitled"


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:200] if name else "Untitled"


# ── Page Tags Extraction ──────────────────────────────────────────────

def get_page_tags(page: dict) -> list[str]:
    """Extract tags from multi_select or select properties."""
    tags = []
    props = page.get("properties", {})
    for prop in props.values():
        if isinstance(prop, dict):
            if prop.get("type") == "multi_select":
                for opt in prop.get("multi_select", []):
                    tags.append(opt.get("name", ""))
            elif prop.get("type") == "select" and prop.get("select"):
                tags.append(prop["select"].get("name", ""))
    return [t for t in tags if t]


# ── Frontmatter ───────────────────────────────────────────────────────

def build_frontmatter(title: str, tags: list[str], notion_id: str, last_edited: str) -> str:
    """Build Obsidian-compatible YAML frontmatter."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_tags = ["notion"] + tags
    tag_str = "\n".join(f"  - {t}" for t in all_tags)
    return f"""---
title: "{title.replace('"', '\\"')}"
source: notion
notion_id: {notion_id}
last_edited: {last_edited}
synced: {now}
tags:
{tag_str}
---
"""


# ── Sync State ────────────────────────────────────────────────────────

def load_state() -> dict:
    """Load the last-sync state (notion_id → last_edited_time)."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict):
    """Persist sync state."""
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── Main Sync ─────────────────────────────────────────────────────────

def sync():
    print("=== Notion → Obsidian Sync ===")
    if DRY_RUN:
        print("  (dry run — no files will be written)")

    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    new_state = {}

    # 1. Fetch all pages
    print("  Searching Notion for all accessible pages...")
    pages = search_all_pages()
    print(f"  Found {len(pages)} pages")

    stats = {"synced": 0, "skipped": 0, "errors": 0}
    page_entries = []  # For the MOC index

    for page in pages:
        page_id = page["id"]
        last_edited = page.get("last_edited_time", "")
        title = get_page_title(page)
        safe_title = sanitize_filename(title)
        tags = get_page_tags(page)

        vlog(f"Processing: {title} ({page_id})")

        # Idempotent check: skip if unchanged
        if state.get(page_id) == last_edited:
            vlog(f"  Unchanged, skipping")
            stats["skipped"] += 1
            new_state[page_id] = last_edited
            page_entries.append({"title": title, "filename": f"{safe_title}.md", "tags": tags})
            continue

        # 2. Fetch blocks and convert to markdown
        try:
            blocks = get_block_children(page_id)
            body = blocks_to_markdown(blocks)
        except Exception as e:
            print(f"  ERROR fetching blocks for '{title}': {e}")
            stats["errors"] += 1
            # Preserve old state so we retry next time
            if page_id in state:
                new_state[page_id] = state[page_id]
            continue

        # 3. Build full document
        frontmatter = build_frontmatter(title, tags, page_id, last_edited)
        content = frontmatter + "\n" + body.strip() + "\n"

        # 4. Write file
        filepath = VAULT_DIR / f"{safe_title}.md"
        if not DRY_RUN:
            filepath.write_text(content, encoding="utf-8")

        log(f"{'[dry] ' if DRY_RUN else ''}Synced: {safe_title}.md")
        stats["synced"] += 1
        new_state[page_id] = last_edited
        page_entries.append({"title": title, "filename": f"{safe_title}.md", "tags": tags})

    # 5. Save state
    if not DRY_RUN:
        save_state(new_state)

    # 6. Build MOC index
    page_entries.sort(key=lambda x: x["title"].lower())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    moc_lines = [
        "---",
        "title: Notion Pages Index",
        "source: notion",
        f"generated: {now}",
        "tags:",
        "  - notion",
        "  - MOC",
        "---",
        "",
        "# Notion Pages",
        "",
        f"*{len(page_entries)} pages synced from Notion*",
        "",
    ]

    # Group by first letter
    current_letter = ""
    for entry in page_entries:
        first = entry["title"][0].upper() if entry["title"] else "#"
        if first != current_letter:
            current_letter = first
            moc_lines.append(f"## {current_letter}")
            moc_lines.append("")
        tag_str = ""
        if entry["tags"]:
            tag_str = " — " + ", ".join(f"`{t}`" for t in entry["tags"])
        link_name = entry["title"]
        moc_lines.append(f"- [[{link_name}]]{tag_str}")

    moc_lines.append("")
    moc_content = "\n".join(moc_lines)

    if not DRY_RUN:
        INDEX_FILE.write_text(moc_content, encoding="utf-8")
    log(f"{'[dry] ' if DRY_RUN else ''}Generated _Index.md ({len(page_entries)} entries)")

    # 7. Summary
    print("")
    print(f"  Done: {stats['synced']} synced, {stats['skipped']} unchanged, {stats['errors']} errors")


# ── Entry Point ───────────────────────────────────────────────────────

if __name__ == "__main__":
    TOKEN = get_notion_token()
    sync()
