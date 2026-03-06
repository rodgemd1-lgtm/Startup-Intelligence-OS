"""Markdown file ingestion — chunks by heading and stores in pgvector."""
from __future__ import annotations
from pathlib import Path
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown


class MarkdownIngestor(BaseIngestor):
    """Ingest markdown files into the knowledge base."""

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "behavioral_economics",
        agent_id: str | None = None,
        **kwargs,
    ) -> int:
        """Ingest a markdown file or directory of markdown files.

        Args:
            source: Path to a .md file or directory containing .md files
            company_id: Namespace for multi-tenancy
            data_type: Knowledge taxonomy category
            agent_id: Optional agent-specific assignment
        """
        path = Path(source)
        if path.is_file():
            return self._ingest_file(path, company_id, data_type, agent_id)
        elif path.is_dir():
            total = 0
            for md_file in sorted(path.glob("**/*.md")):
                total += self._ingest_file(md_file, company_id, data_type, agent_id)
            return total
        else:
            raise FileNotFoundError(f"Source not found: {source}")

    def _ingest_file(
        self,
        path: Path,
        company_id: str,
        data_type: str,
        agent_id: str | None,
    ) -> int:
        """Ingest a single markdown file."""
        content = path.read_text(encoding="utf-8")
        text_chunks = chunk_markdown(content, max_tokens=500)

        chunks = self._make_chunks(
            texts=text_chunks,
            data_type=data_type,
            company_id=company_id,
            agent_id=agent_id,
            source=f"file:{path.name}",
            metadata={"file_path": str(path)},
        )

        return self.retriever.store_chunks(chunks)
