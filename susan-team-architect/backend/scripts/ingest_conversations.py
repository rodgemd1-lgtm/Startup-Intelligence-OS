#!/usr/bin/env python3
"""Conversation ingestion pipeline — embeds Hermes/Claude conversations into Susan RAG.

Usage:
    python scripts/ingest_conversations.py <file_or_dir> [--company <id>] [--project <name>]
    python scripts/ingest_conversations.py ~/.hermes/conversations/ --project oracle-health
    python scripts/ingest_conversations.py session_summary.md --company shared

Stores conversations as data_type="conversation" in the existing knowledge_chunks table.
Metadata includes: session_date, project_context, people_mentioned, decisions, action_items.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_text, chunk_markdown


class ConversationIngestor(BaseIngestor):
    """Ingest conversation logs/summaries into Susan's RAG for semantic recall."""

    # People Jake should tag when found in conversations
    KNOWN_PEOPLE = [
        "mike", "jacob", "james", "matt cohlmia", "matt", "cohlmia",
        "jordan voss", "jordan", "ellen", "myhelp",
    ]

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        project: str | None = None,
        session_date: str | None = None,
        **kwargs,
    ) -> int:
        """Ingest a conversation file or directory.

        Args:
            source: Path to .md/.txt/.jsonl file or directory
            company_id: Namespace (default "shared")
            project: Project context (startup-os, oracle-health, alex-recruiting)
            session_date: Override date (YYYY-MM-DD), defaults to file mtime
        """
        path = Path(source)
        if path.is_file():
            return self._ingest_file(path, company_id, project, session_date)
        elif path.is_dir():
            total = 0
            for f in sorted(path.glob("**/*")):
                if f.suffix in (".md", ".txt", ".jsonl"):
                    total += self._ingest_file(f, company_id, project, session_date)
            return total
        else:
            raise FileNotFoundError(f"Source not found: {source}")

    def _ingest_file(
        self,
        path: Path,
        company_id: str,
        project: str | None,
        session_date: str | None,
    ) -> int:
        """Ingest a single conversation file."""
        if path.suffix == ".jsonl":
            content = self._parse_jsonl(path)
        else:
            content = path.read_text(encoding="utf-8")

        if not content.strip():
            return 0

        # Extract metadata from content
        people = self._extract_people(content)
        decisions = self._extract_decisions(content)
        action_items = self._extract_action_items(content)
        date = session_date or datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")

        # Auto-detect project if not specified
        if not project:
            project = self._detect_project(content)

        # Chunk the conversation
        if path.suffix == ".md":
            text_chunks = chunk_markdown(content, max_tokens=500)
        else:
            text_chunks = chunk_text(content, max_tokens=500)

        # Build metadata
        metadata = {
            "session_date": date,
            "project_context": project or "general",
            "people_mentioned": people,
            "has_decisions": len(decisions) > 0,
            "has_action_items": len(action_items) > 0,
            "file_path": str(path),
        }
        if decisions:
            metadata["decisions"] = decisions[:10]  # Cap at 10
        if action_items:
            metadata["action_items"] = action_items[:10]

        chunks = self._make_chunks(
            texts=text_chunks,
            data_type="conversation",
            company_id=company_id,
            source=f"conversation:{path.stem}",
            source_url=f"file://{path}",
            metadata=metadata,
        )

        stored = self.retriever.store_chunks(chunks)
        print(f"  ✓ {path.name}: {stored} chunks | people: {people} | decisions: {len(decisions)} | actions: {len(action_items)}")
        return stored

    def _parse_jsonl(self, path: Path) -> str:
        """Parse Claude Code JSONL transcript into readable text."""
        lines = []
        for line in path.read_text(encoding="utf-8").strip().split("\n"):
            try:
                entry = json.loads(line)
                role = entry.get("role", "")
                content = entry.get("content", "")
                if isinstance(content, list):
                    # Handle content blocks
                    text_parts = [
                        b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text"
                    ]
                    content = "\n".join(text_parts)
                if content and role in ("user", "assistant"):
                    lines.append(f"[{role}]: {content[:2000]}")  # Cap per-message
            except json.JSONDecodeError:
                continue
        return "\n\n".join(lines)

    def _extract_people(self, content: str) -> list[str]:
        """Find known people mentioned in conversation."""
        lower = content.lower()
        return [p for p in self.KNOWN_PEOPLE if p in lower]

    def _extract_decisions(self, content: str) -> list[str]:
        """Extract decision-like statements."""
        decisions = []
        patterns = [
            r"(?:decided|decision|chose|going with|we'll use|settled on)\s*:?\s*(.{10,100})",
            r"(?:##\s*Decisions?\s*Made?)\s*\n([\s\S]*?)(?:\n##|\Z)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                decisions.append(match.group(1).strip()[:200])
        return decisions[:10]

    def _extract_action_items(self, content: str) -> list[str]:
        """Extract action items and TODOs."""
        items = []
        patterns = [
            r"- \[ \]\s+(.{5,150})",
            r"(?:TODO|FIXME|ACTION)[\s:]+(.{5,150})",
            r"(?:need to|should|must|will)\s+(.{10,100})",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                items.append(match.group(1).strip())
        return items[:10]

    def _detect_project(self, content: str) -> str | None:
        """Auto-detect project context from content."""
        lower = content.lower()
        if "oracle health" in lower or "oracle-health" in lower or "cohlmia" in lower:
            return "oracle-health"
        if "alex recruiting" in lower or "jacob" in lower and "recruit" in lower:
            return "alex-recruiting"
        if "startup intelligence" in lower or "susan" in lower:
            return "startup-os"
        return None


def main():
    parser = argparse.ArgumentParser(description="Ingest conversations into Susan RAG")
    parser.add_argument("source", help="Path to conversation file or directory")
    parser.add_argument("--company", default="shared", help="Company ID namespace")
    parser.add_argument("--project", help="Project context (oracle-health, startup-os, alex-recruiting)")
    parser.add_argument("--date", help="Session date override (YYYY-MM-DD)")
    args = parser.parse_args()

    print(f"Ingesting conversations from: {args.source}")
    print(f"  Company: {args.company} | Project: {args.project or 'auto-detect'}")

    ingestor = ConversationIngestor()
    count = ingestor.ingest(
        source=args.source,
        company_id=args.company,
        project=args.project,
        session_date=args.date,
    )
    print(f"\n✅ Total chunks stored: {count}")


if __name__ == "__main__":
    main()
