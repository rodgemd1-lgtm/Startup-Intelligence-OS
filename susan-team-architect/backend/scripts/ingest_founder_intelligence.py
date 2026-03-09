"""Ingest Founder Intelligence OS into Susan's foundry knowledge base."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

from supabase import create_client
import yaml

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.chunker import chunk_markdown, chunk_text
from rag_engine.ingestion.markdown import MarkdownIngestor
from rag_engine.ingestion.web import WebIngestor
from rag_engine.retriever import Retriever
from susan_core.config import config
from susan_core.schemas import KnowledgeChunk


FOUNDER_ROOT = Path.home() / "founder-intelligence-os"
PERSONAS_DIR = FOUNDER_ROOT / "intelligence" / "personas"
FRAMEWORKS_DIR = FOUNDER_ROOT / "intelligence" / "frameworks"
SKILLS_DIR = FOUNDER_ROOT / "automation" / "skills"
DOCS_DIR = FOUNDER_ROOT / "docs"

DOMAIN_ROOT = BACKEND_ROOT / "data" / "domains" / "founder_foundry_intelligence"
MANIFEST_PATH = DOMAIN_ROOT / "datasets" / "open_sources.yaml"

EDITORIAL_PATHS = {
    "business_strategy": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_FOUNDRY_DOMAIN_BRIEF.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_FOUNDRY_BUILD_MATRIX.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_COMPANY_GENOME_SPEC.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_KPI_TREE_AND_SCORECARDS.md",
    ],
    "operational_protocols": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_FOUNDRY_OPERATING_CADENCE.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_DECISION_LOG_PROTOCOL.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_EXPERIMENT_REGISTRY_PROTOCOL.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_MEMORY_WRITEBACK_PROTOCOL.md",
    ],
    "technical_docs": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_TECHNICAL_SYSTEMS_BASELINE.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_EVIDENCE_GRAPH_SPEC.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_EVENT_TAXONOMY.md",
    ],
    "legal_compliance": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_TRUST_GOVERNANCE_BASELINE.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_LAUNCH_READINESS_CHECKLIST.md",
    ],
    "security": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_SECURITY_BASELINE.md",
    ],
    "ux_research": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_PRODUCT_EXPERIENCE_BASELINE.md",
    ],
    "studio_open_research": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_STUDIO_OPEN_RESEARCH_MAP.md",
    ],
    "finance": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_FINANCE_OPERATING_BASELINE.md",
    ],
    "user_research": [
        DOMAIN_ROOT / "editorial" / "FOUNDER_USER_RESEARCH_OPERATING_BASELINE.md",
        DOMAIN_ROOT / "editorial" / "FOUNDER_SUPPORT_OPERATIONS_BASELINE.md",
    ],
}

RESET_TYPES = [
    "business_strategy",
    "market_research",
    "expert_knowledge",
    "operational_protocols",
    "technical_docs",
    "legal_compliance",
    "security",
    "ux_research",
    "studio_open_research",
    "finance",
    "user_research",
]


def _delete_existing(company_id: str, data_type: str) -> None:
    supabase = create_client(config.supabase_url, config.supabase_key)
    supabase.table("knowledge_chunks").delete().eq("company_id", company_id).eq("data_type", data_type).execute()


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text.strip()


def _extract_name_from_heading(text: str) -> str:
    match = re.search(r"^#\s+(.+?)(?:\s*[—–-]\s*.+)?$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown"


def _split_by_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_name = "header"
    current_lines: list[str] = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_lines:
                sections[current_name] = "\n".join(current_lines).strip()
            current_name = line.lstrip("# ").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_name] = "\n".join(current_lines).strip()

    return sections


def _doc_data_type(path: Path) -> str | None:
    name = path.stem.upper()
    if name == "INDEX":
        return None
    if "ROLE_ATLAS" in name:
        return "expert_knowledge"
    if "DOMAIN_ATLAS" in name or "ECOSYSTEM" in name:
        return "market_research"
    if "GAMEPLAN" in name:
        return "operational_protocols"
    if "STRATEGY" in name:
        return "business_strategy"
    return "business_strategy"


def _ingest_personas(retriever: Retriever, company_id: str) -> int:
    if not PERSONAS_DIR.exists():
        return 0

    total = 0
    files = sorted(f for f in PERSONAS_DIR.glob("*.md") if not f.name.startswith("_TEMPLATE"))

    for md_file in files:
        raw = md_file.read_text(encoding="utf-8")
        content = _strip_frontmatter(raw)
        name = _extract_name_from_heading(content)
        sections = _split_by_sections(content)
        metadata = {
            "type": "persona",
            "name": name,
            "source_repo": "founder-intelligence-os",
            "file": md_file.name,
        }
        chunks: list[KnowledgeChunk] = []

        mental_model = sections.get("Mental Model", "")
        if mental_model:
            chunks.append(
                KnowledgeChunk(
                    content=f"[Persona: {name}] {mental_model}",
                    company_id=company_id,
                    data_type="expert_knowledge",
                    source=f"persona:{md_file.stem}",
                    source_url=str(md_file),
                    metadata=metadata,
                )
            )

        rules = sections.get("Operational Rules", "")
        if rules:
            for piece in chunk_text(f"[Persona: {name} — Operational Rules]\n{rules}", max_tokens=500):
                chunks.append(
                    KnowledgeChunk(
                        content=piece,
                        company_id=company_id,
                        data_type="expert_knowledge",
                        source=f"persona:{md_file.stem}",
                        source_url=str(md_file),
                        metadata=metadata,
                    )
                )

        frameworks = sections.get("Key Frameworks", "")
        insights = sections.get("Counter-Intuitive Insights", "")
        combined = ""
        if frameworks:
            combined += f"[Persona: {name} — Key Frameworks]\n{frameworks}\n"
        if insights:
            combined += f"\n[Counter-Intuitive Insights]\n{insights}"
        if combined.strip():
            for piece in chunk_text(combined.strip(), max_tokens=500):
                chunks.append(
                    KnowledgeChunk(
                        content=piece,
                        company_id=company_id,
                        data_type="expert_knowledge",
                        source=f"persona:{md_file.stem}",
                        source_url=str(md_file),
                        metadata=metadata,
                    )
                )

        if not chunks:
            for piece in chunk_markdown(content, max_tokens=500):
                chunks.append(
                    KnowledgeChunk(
                        content=piece,
                        company_id=company_id,
                        data_type="expert_knowledge",
                        source=f"persona:{md_file.stem}",
                        source_url=str(md_file),
                        metadata=metadata,
                    )
                )

        total += retriever.store_chunks(chunks)

    return total


def _ingest_frameworks(retriever: Retriever, company_id: str) -> int:
    if not FRAMEWORKS_DIR.exists():
        return 0

    total = 0
    files = sorted(f for f in FRAMEWORKS_DIR.glob("*.md") if not f.name.startswith("_TEMPLATE"))

    for md_file in files:
        raw = md_file.read_text(encoding="utf-8")
        content = _strip_frontmatter(raw)
        name = _extract_name_from_heading(content)
        metadata = {
            "type": "framework",
            "name": name,
            "source_repo": "founder-intelligence-os",
            "file": md_file.name,
        }
        chunks = [
            KnowledgeChunk(
                content=piece,
                company_id=company_id,
                data_type="operational_protocols",
                source=f"framework:{md_file.stem}",
                source_url=str(md_file),
                metadata=metadata,
            )
            for piece in chunk_markdown(content, max_tokens=500)
        ]
        total += retriever.store_chunks(chunks)

    return total


def _ingest_skills(retriever: Retriever, company_id: str) -> int:
    if not SKILLS_DIR.exists():
        return 0

    total = 0
    files = sorted(f for f in SKILLS_DIR.glob("*.md") if not f.name.startswith("_TEMPLATE"))

    for md_file in files:
        raw = md_file.read_text(encoding="utf-8")
        content = _strip_frontmatter(raw)
        name = _extract_name_from_heading(content)
        metadata = {
            "type": "skill",
            "name": name,
            "source_repo": "founder-intelligence-os",
            "file": md_file.name,
        }
        chunks = [
            KnowledgeChunk(
                content=piece,
                company_id=company_id,
                data_type="operational_protocols",
                source=f"skill:{md_file.stem}",
                source_url=str(md_file),
                metadata=metadata,
            )
            for piece in chunk_markdown(content, max_tokens=500)
        ]
        total += retriever.store_chunks(chunks)

    return total


def _ingest_founder_docs(markdown_ingestor: MarkdownIngestor, company_id: str) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    if not DOCS_DIR.exists():
        return totals

    files = sorted(DOCS_DIR.glob("*.md"))
    for path in files:
        data_type = _doc_data_type(path)
        if not data_type:
            continue
        totals[data_type] += markdown_ingestor.ingest(str(path), company_id=company_id, data_type=data_type)
    return totals


def _ingest_editorial(markdown_ingestor: MarkdownIngestor, company_id: str) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for data_type, paths in EDITORIAL_PATHS.items():
        for path in paths:
            if path.exists():
                totals[data_type] += markdown_ingestor.ingest(str(path), company_id=company_id, data_type=data_type)
    return totals


def _ingest_web_sources(web_ingestor: WebIngestor, company_id: str, manifest: dict) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for source in manifest.get("web_sources", []):
        totals[source["data_type"]] += web_ingestor.ingest(
            source["url"],
            company_id=company_id,
            data_type=source["data_type"],
        )
    return totals


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Founder Intelligence OS into Susan's foundry knowledge base.")
    parser.add_argument(
        "--skip-web",
        action="store_true",
        help="Skip the slower official-source web crawl and ingest only local founder/editorial material.",
    )
    parser.add_argument(
        "--editorial-only",
        action="store_true",
        help="Ingest only editorial founder domain files and skip founder repo docs, personas, frameworks, skills, and web sources.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if not FOUNDER_ROOT.exists():
        print(f"ERROR: founder-intelligence-os not found at {FOUNDER_ROOT}")
        return 1

    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8")) or {}
    company_id = manifest.get("company_id", "founder-intelligence-os")

    for data_type in RESET_TYPES:
        _delete_existing(company_id, data_type)

    retriever = Retriever()
    markdown_ingestor = MarkdownIngestor()
    totals: dict[str, int] = defaultdict(int)

    for data_type, count in _ingest_editorial(markdown_ingestor, company_id).items():
        totals[data_type] += count
    if not args.editorial_only:
        for data_type, count in _ingest_founder_docs(markdown_ingestor, company_id).items():
            totals[data_type] += count
        totals["expert_knowledge"] += _ingest_personas(retriever, company_id)
        totals["operational_protocols"] += _ingest_frameworks(retriever, company_id)
        totals["operational_protocols"] += _ingest_skills(retriever, company_id)
    if not args.skip_web and not args.editorial_only:
        web_ingestor = WebIngestor()
        for data_type, count in _ingest_web_sources(web_ingestor, company_id, manifest).items():
            totals[data_type] += count

    print(
        json.dumps(
            {
                "company_id": company_id,
                "manifest": str(MANIFEST_PATH),
                "founder_root": str(FOUNDER_ROOT),
                "skip_web": args.skip_web,
                "editorial_only": args.editorial_only,
                "stored": dict(totals),
                "total": sum(totals.values()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
