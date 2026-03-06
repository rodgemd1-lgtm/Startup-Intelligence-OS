"""Ingest two extracted .docx documents into the Susan RAG knowledge base.

Documents:
  1. TransformFit Elite AI Skillset & Persona Architecture  (agent_prompts)
  2. UX/UI Design Enterprise Framework & Playbook           (ux_framework)

Usage:
    cd backend && python -m scripts.ingest_docx
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the backend package root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rag_engine.chunker import chunk_markdown
from rag_engine.retriever import Retriever
from susan_core.schemas import KnowledgeChunk

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TEXT_FILE = Path(
    "/Users/mikerodgers/.claude/projects/"
    "-Users-mikerodgers-Startup-Intelligence-OS/"
    "4f97efbe-b716-491a-87af-37c65d84b2ae/"
    "tool-results/biznsibt7.txt"
)

SEPARATOR = "=== UXUI_Framework_Playbook_Double_Black_Box.docx ==="

DOC_CONFIGS = [
    {
        "name": "TransformFit Elite Skillset Prompts",
        "data_type": "agent_prompts",
        "company_id": "transformfit",
        "source": "docx:TransformFit_Elite_Skillset_Prompts",
        "metadata": {"title": "TransformFit Elite AI Skillset & Persona Architecture"},
    },
    {
        "name": "UX/UI Framework Playbook - Double Black Box",
        "data_type": "ux_framework",
        "company_id": "shared",
        "source": "docx:UXUI_Framework_Playbook_Double_Black_Box",
        "metadata": {"title": "UX/UI Design Enterprise Framework & Playbook - Double Black Box Method"},
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_documents(raw: str) -> tuple[str, str]:
    """Split the combined text file into two document bodies."""
    # The first line is the doc-1 header; strip it.
    # The separator line marks the start of doc-2.
    parts = raw.split(SEPARATOR, maxsplit=1)
    if len(parts) != 2:
        raise ValueError(f"Expected separator '{SEPARATOR}' not found in file.")

    doc1_text = parts[0].strip()
    doc2_text = parts[1].strip()

    # Remove the leading header line from doc1
    # "=== TransformFit_Elite_Skillset_Prompts.docx ==="
    first_newline = doc1_text.index("\n")
    doc1_text = doc1_text[first_newline:].strip()

    return doc1_text, doc2_text


def _make_chunks(
    texts: list[str],
    data_type: str,
    company_id: str,
    source: str,
    metadata: dict,
) -> list[KnowledgeChunk]:
    """Convert chunked text strings into KnowledgeChunk objects."""
    return [
        KnowledgeChunk(
            content=text,
            company_id=company_id,
            data_type=data_type,
            source=source,
            metadata=metadata,
        )
        for text in texts
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Reading source file ...")
    raw = TEXT_FILE.read_text(encoding="utf-8")
    doc1_text, doc2_text = _split_documents(raw)
    doc_texts = [doc1_text, doc2_text]

    retriever = Retriever()

    total_stored = 0
    for doc_text, cfg in zip(doc_texts, DOC_CONFIGS):
        name = cfg["name"]
        print(f"\n--- {name} ---")
        print(f"  Text length : {len(doc_text):,} chars")

        # Chunk using markdown-aware splitter
        text_chunks = chunk_markdown(doc_text)
        print(f"  Chunks      : {len(text_chunks)}")

        # Build KnowledgeChunk objects
        chunks = _make_chunks(
            texts=text_chunks,
            data_type=cfg["data_type"],
            company_id=cfg["company_id"],
            source=cfg["source"],
            metadata=cfg["metadata"],
        )

        # Embed + store via Supabase pgvector
        stored = retriever.store_chunks(chunks)
        print(f"  Stored      : {stored}")
        total_stored += stored

    print(f"\nDone. Total chunks stored: {total_stored}")


if __name__ == "__main__":
    main()
