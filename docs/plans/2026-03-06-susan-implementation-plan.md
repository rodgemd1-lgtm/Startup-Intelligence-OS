# Susan Team Architect — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build Susan as a portable Claude Code plugin with a Python backend that orchestrates 22 AI agents, a Supabase pgvector RAG system, and ~4,000 knowledge chunks — deployed first against TransformFit.

**Architecture:** Hybrid Claude Code plugin (commands, skills, agents, hooks) + Python core (orchestrator, RAG engine, data ingestion). Supabase pgvector for vector storage, Voyage AI voyage-4 for embeddings.

**Tech Stack:** Python 3.11+, anthropic SDK, voyageai, supabase-py, pydantic v2, firecrawl-py, arxiv, PyYAML

**Design Doc:** `docs/plans/2026-03-06-susan-team-architect-design.md`

---

## Phase 1: Foundation — Project Setup & Infrastructure

### Task 1: Create Plugin Directory Structure

**Files:**
- Create: `susan-team-architect/.claude-plugin/plugin.json`
- Create: `susan-team-architect/backend/pyproject.toml`
- Create: `susan-team-architect/backend/.env.example`

**Step 1: Create all directories**

```bash
mkdir -p susan-team-architect/{.claude-plugin,commands,skills/{team-architect,behavioral-economics,company-analysis},agents,hooks,backend/{susan_core/phases,rag_engine/ingestion,agents,data/{be_module,seed_data},tests}}
```

**Step 2: Write plugin.json**

```json
{
  "name": "susan-team-architect",
  "description": "AI Team Architect — designs and deploys optimal multi-agent workforces for startups with full RAG systems",
  "author": "Apex Ventures"
}
```

**Step 3: Write pyproject.toml**

```toml
[project]
name = "susan-team-architect"
version = "0.1.0"
description = "Susan Team Architect — Python backend for AI agent orchestration and RAG"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.1.40",
    "voyageai>=0.3.0",
    "supabase>=2.20.0",
    "pydantic>=2.10.0",
    "PyYAML>=6.0",
    "firecrawl-py>=4.0.0",
    "arxiv>=2.1.0",
    "httpx>=0.27.0",
    "tiktoken>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
]

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

**Step 4: Write .env.example**

```bash
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
FIRECRAWL_API_KEY=fc-...  # Optional: for Tier 2+ data ingestion
```

**Step 5: Commit**

```bash
git add susan-team-architect/
git commit -m "feat: scaffold susan-team-architect plugin directory structure"
```

---

### Task 2: Supabase Project Setup & Schema

**Files:**
- Create: `susan-team-architect/backend/susan_core/database.sql`

**Step 1: Write the complete database schema**

```sql
-- Susan Team Architect — Supabase pgvector Schema
-- Run in Supabase Dashboard > SQL Editor

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Core knowledge store
CREATE TABLE knowledge_chunks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  content TEXT NOT NULL,
  embedding VECTOR(1024),
  company_id TEXT NOT NULL,
  agent_id TEXT,
  access_level TEXT DEFAULT 'company' CHECK (access_level IN ('public', 'company', 'agent_private')),
  data_type TEXT NOT NULL,
  source TEXT,
  source_url TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chunks_hnsw ON knowledge_chunks
  USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_company ON knowledge_chunks (company_id);
CREATE INDEX idx_chunks_agent ON knowledge_chunks (agent_id);
CREATE INDEX idx_chunks_type ON knowledge_chunks (data_type);
CREATE INDEX idx_chunks_access ON knowledge_chunks (access_level);

-- Company profiles
CREATE TABLE companies (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  domain TEXT,
  stage TEXT,
  profile JSONB NOT NULL DEFAULT '{}',
  team_manifest JSONB,
  dataset_requirements JSONB,
  execution_plan TEXT,
  be_audit JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent run cost tracking
CREATE TABLE agent_runs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_id TEXT NOT NULL REFERENCES companies(id),
  agent_id TEXT NOT NULL,
  phase TEXT,
  model TEXT NOT NULL,
  input_tokens INT,
  output_tokens INT,
  cost_usd DECIMAL(10,6),
  duration_ms INT,
  status TEXT DEFAULT 'success',
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_runs_company ON agent_runs (company_id);
CREATE INDEX idx_runs_agent ON agent_runs (agent_id);

-- Filtered similarity search function
CREATE OR REPLACE FUNCTION search_knowledge(
  query_embedding VECTOR(1024),
  filter_company TEXT,
  filter_access TEXT[] DEFAULT ARRAY['public', 'company'],
  filter_types TEXT[] DEFAULT NULL,
  filter_agent TEXT DEFAULT NULL,
  match_count INT DEFAULT 5
) RETURNS TABLE (
  id UUID,
  content TEXT,
  company_id TEXT,
  data_type TEXT,
  metadata JSONB,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    kc.id,
    kc.content,
    kc.company_id,
    kc.data_type,
    kc.metadata,
    1 - (kc.embedding <=> query_embedding) AS similarity
  FROM knowledge_chunks kc
  WHERE kc.company_id IN (filter_company, 'shared')
    AND kc.access_level = ANY(filter_access)
    AND (filter_types IS NULL OR kc.data_type = ANY(filter_types))
    AND (filter_agent IS NULL OR kc.agent_id IS NULL OR kc.agent_id = filter_agent)
  ORDER BY kc.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

**Step 2: Create Supabase project**

Go to https://supabase.com/dashboard → New Project. Save the URL and service role key to `.env`.

**Step 3: Run the SQL in Supabase SQL Editor**

Copy-paste the entire SQL file into Supabase Dashboard > SQL Editor > Run.

**Step 4: Commit**

```bash
git add susan-team-architect/backend/susan_core/database.sql
git commit -m "feat: add Supabase pgvector schema for knowledge store"
```

---

### Task 3: Config & Pydantic Schemas

**Files:**
- Create: `susan-team-architect/backend/susan_core/__init__.py`
- Create: `susan-team-architect/backend/susan_core/config.py`
- Create: `susan-team-architect/backend/susan_core/schemas.py`

**Step 1: Write config.py**

```python
"""Configuration for Susan Team Architect."""
import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    voyage_api_key: str = os.environ.get("VOYAGE_API_KEY", "")
    supabase_url: str = os.environ.get("SUPABASE_URL", "")
    supabase_key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")
    firecrawl_api_key: str = os.environ.get("FIRECRAWL_API_KEY", "")

    # Model routing
    model_opus: str = "claude-opus-4-6"
    model_sonnet: str = "claude-sonnet-4-5-20250514"
    model_haiku: str = "claude-haiku-4-5-20251001"

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = Path(__file__).parent.parent / "data"
    companies_dir: Path = Path.cwd() / "companies"

    # RAG settings
    chunk_size: int = 500  # tokens
    chunk_overlap: int = 50  # tokens
    embedding_model: str = "voyage-3"
    embedding_dim: int = 1024
    rag_top_k: int = 5

    # Cost tracking (per 1M tokens)
    cost_per_m_input: dict = None
    cost_per_m_output: dict = None

    def __post_init__(self):
        self.cost_per_m_input = {
            self.model_opus: 15.0,
            self.model_sonnet: 3.0,
            self.model_haiku: 0.25,
        }
        self.cost_per_m_output = {
            self.model_opus: 75.0,
            self.model_sonnet: 15.0,
            self.model_haiku: 1.25,
        }


config = Config()
```

**Step 2: Write schemas.py**

```python
"""Pydantic schemas for all Susan outputs."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


# --- Phase 1: Company Profile ---

class Founder(BaseModel):
    name: str
    background: str

class CompanyProfile(BaseModel):
    company: str
    domain: str
    stage: str
    website: str | None = None
    founding_date: str | None = None
    founders: list[Founder] = Field(default_factory=list)
    product_description: str
    tech_stack: list[str] = Field(default_factory=list)
    target_market: str
    funding_status: str
    key_competitors: list[str] = Field(default_factory=list)
    current_challenges: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


# --- Phase 2: Gap Analysis ---

class CapabilityGap(BaseModel):
    area: str
    current_state: str
    ideal_state: str
    complexity: int = Field(ge=1, le=10)
    agent_needed: str
    risks: list[str] = Field(default_factory=list)
    cross_portfolio_synergy: str | None = None

class AnalysisReport(BaseModel):
    company: str
    capability_gaps: list[CapabilityGap]
    recommended_team_size: int
    complexity_score: float


# --- Phase 3: Team Design ---

class MemoryConfig(BaseModel):
    short_term: bool = True
    long_term: bool = False
    entity: bool = False

class AgentSpec(BaseModel):
    id: str = Field(description="snake_case identifier")
    name: str = Field(description="Display name (e.g., 'Susan', 'Steve')")
    role: str = Field(description="Job title")
    goal: str = Field(description="One-sentence objective")
    backstory: str = Field(description="Elite pedigree persona")
    tools: list[str] = Field(default_factory=list)
    llm: str = Field(default="claude-sonnet-4-5-20250514")
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    dependencies: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)
    rag_data_types: list[str] = Field(default_factory=list)
    estimated_cost_per_run: str = Field(default="$0.05")

class CrewSpec(BaseModel):
    name: str
    agents: list[str]
    process: str = Field(description="sequential | parallel | hierarchical")
    trigger: str

class TeamManifest(BaseModel):
    project: str
    designed_by: str = "susan"
    version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    orchestration_pattern: str
    agents: list[AgentSpec]
    crews: list[CrewSpec] = Field(default_factory=list)
    total_agents: int
    estimated_monthly_cost: str


# --- Phase 4: Dataset Requirements ---

class DatasetRequirement(BaseModel):
    name: str
    type: str = Field(description="structured|vector|api|filesystem")
    status: str = Field(description="exists|needs_building|needs_acquisition")
    source: str
    format: str
    size_estimate: str
    priority: str = Field(description="P0|P1|P2")
    cost: str = Field(default="free")
    assigned_to: list[str] = Field(default_factory=list)

class DatasetManifest(BaseModel):
    datasets: list[DatasetRequirement]
    external_apis: list[dict] = Field(default_factory=list)
    total_estimated_cost: str


# --- Phase 6: Behavioral Economics Audit ---

class RetentionTarget(BaseModel):
    d1: float
    d7: float
    d30: float
    industry_baseline_d1: float
    industry_baseline_d7: float
    industry_baseline_d30: float

class LAALDesign(BaseModel):
    ownership_asset: str
    cost_of_leaving_progress: str
    cost_of_leaving_identity: str
    cost_of_leaving_social: str
    cost_of_leaving_asset: str
    minimum_return_action: str
    return_reward: str
    investment_flywheel: str

class BEAudit(BaseModel):
    company: str
    retention_targets: RetentionTarget
    laal_design: LAALDesign
    copy_protocols: dict = Field(default_factory=dict)
    agent_be_map: dict = Field(default_factory=dict)
    measurement_plan: dict = Field(default_factory=dict)


# --- Knowledge Chunk ---

class KnowledgeChunk(BaseModel):
    content: str
    company_id: str = "shared"
    agent_id: str | None = None
    access_level: str = "public"
    data_type: str
    source: str | None = None
    source_url: str | None = None
    metadata: dict = Field(default_factory=dict)
```

**Step 3: Write empty __init__.py files**

```python
# susan_core/__init__.py
"""Susan Team Architect — Core orchestration package."""
```

**Step 4: Run type check**

```bash
cd susan-team-architect/backend && python3 -c "from susan_core.schemas import *; print('Schemas OK')"
```

Expected: `Schemas OK`

**Step 5: Commit**

```bash
git add susan-team-architect/backend/susan_core/
git commit -m "feat: add config and Pydantic schemas for all Susan outputs"
```

---

## Phase 2: RAG Engine

### Task 4: Text Chunker

**Files:**
- Create: `susan-team-architect/backend/rag_engine/__init__.py`
- Create: `susan-team-architect/backend/rag_engine/chunker.py`
- Create: `susan-team-architect/backend/tests/test_chunker.py`

**Step 1: Write the failing test**

```python
# tests/test_chunker.py
from rag_engine.chunker import chunk_text, chunk_markdown

def test_chunk_text_splits_by_size():
    text = "word " * 1000  # ~1000 words
    chunks = chunk_text(text, max_tokens=500, overlap=50)
    assert len(chunks) >= 2
    assert all(len(c.split()) <= 600 for c in chunks)  # rough token estimate

def test_chunk_text_preserves_content():
    text = "Hello world. This is a test."
    chunks = chunk_text(text, max_tokens=500, overlap=0)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_markdown_splits_by_heading():
    md = "# Section 1\nContent 1.\n\n## Section 2\nContent 2.\n\n# Section 3\nContent 3."
    chunks = chunk_markdown(md, max_tokens=500)
    assert len(chunks) >= 2  # Should split on headings

def test_chunk_markdown_metadata():
    md = "# My Section\nSome content here."
    chunks = chunk_markdown(md, max_tokens=500)
    assert len(chunks) >= 1
```

**Step 2: Run test to verify it fails**

```bash
cd susan-team-architect/backend && python3 -m pytest tests/test_chunker.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'rag_engine'`

**Step 3: Write chunker.py**

```python
"""Smart text chunking for RAG ingestion."""
from __future__ import annotations
import re


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~0.75 tokens per word for English."""
    return int(len(text.split()) * 1.33)


def chunk_text(
    text: str,
    max_tokens: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Split text into chunks by sentence boundaries, respecting token limits."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_chunk: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = _estimate_tokens(sentence)
        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            chunks.append(" ".join(current_chunk))
            # Keep overlap sentences
            overlap_tokens = 0
            overlap_start = len(current_chunk)
            for i in range(len(current_chunk) - 1, -1, -1):
                overlap_tokens += _estimate_tokens(current_chunk[i])
                if overlap_tokens >= overlap:
                    overlap_start = i
                    break
            current_chunk = current_chunk[overlap_start:]
            current_tokens = sum(_estimate_tokens(s) for s in current_chunk)
        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks if chunks else [text]


def chunk_markdown(
    text: str,
    max_tokens: int = 500,
) -> list[str]:
    """Split markdown by headings, then by token limit within sections."""
    sections = re.split(r'\n(?=#{1,3}\s)', text.strip())
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if _estimate_tokens(section) <= max_tokens:
            chunks.append(section)
        else:
            chunks.extend(chunk_text(section, max_tokens=max_tokens, overlap=50))
    return chunks if chunks else [text]
```

**Step 4: Write __init__.py**

```python
# rag_engine/__init__.py
"""RAG engine — embedding, retrieval, and ingestion."""
```

**Step 5: Run test to verify it passes**

```bash
cd susan-team-architect/backend && python3 -m pytest tests/test_chunker.py -v
```

Expected: All 4 tests PASS

**Step 6: Commit**

```bash
git add susan-team-architect/backend/rag_engine/ susan-team-architect/backend/tests/
git commit -m "feat: add text chunker with sentence-boundary and markdown splitting"
```

---

### Task 5: Voyage AI Embedder

**Files:**
- Create: `susan-team-architect/backend/rag_engine/embedder.py`
- Create: `susan-team-architect/backend/tests/test_embedder.py`

**Step 1: Write the failing test**

```python
# tests/test_embedder.py
import os
import pytest
from rag_engine.embedder import Embedder

@pytest.fixture
def embedder():
    if not os.environ.get("VOYAGE_API_KEY"):
        pytest.skip("VOYAGE_API_KEY not set")
    return Embedder()

def test_embed_single_text(embedder):
    result = embedder.embed(["Hello world"])
    assert len(result) == 1
    assert len(result[0]) == 1024  # voyage-3 output dim

def test_embed_batch(embedder):
    texts = ["First text", "Second text", "Third text"]
    result = embedder.embed(texts)
    assert len(result) == 3
    assert all(len(v) == 1024 for v in result)

def test_embed_empty_raises():
    embedder = Embedder.__new__(Embedder)
    with pytest.raises(ValueError):
        embedder.embed([])
```

**Step 2: Write embedder.py**

```python
"""Voyage AI embedding client."""
from __future__ import annotations
import voyageai
from susan_core.config import config


class Embedder:
    """Wraps Voyage AI for text → vector conversion."""

    def __init__(self, api_key: str | None = None):
        self.client = voyageai.Client(api_key=api_key or config.voyage_api_key)
        self.model = config.embedding_model
        self.dim = config.embedding_dim

    def embed(
        self,
        texts: list[str],
        input_type: str = "document",
        batch_size: int = 128,
    ) -> list[list[float]]:
        """Embed a list of texts, returns list of 1024-dim vectors."""
        if not texts:
            raise ValueError("Cannot embed empty list")

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self.client.embed(
                batch,
                model=self.model,
                input_type=input_type,
            )
            all_embeddings.extend(result.embeddings)

        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        """Embed a single query for retrieval."""
        result = self.client.embed(
            [query],
            model=self.model,
            input_type="query",
        )
        return result.embeddings[0]
```

**Step 3: Run test (requires VOYAGE_API_KEY)**

```bash
cd susan-team-architect/backend && python3 -m pytest tests/test_embedder.py -v
```

Expected: 2 PASS, 1 PASS (or 2 SKIP if no API key + 1 PASS for empty check)

**Step 4: Commit**

```bash
git add susan-team-architect/backend/rag_engine/embedder.py susan-team-architect/backend/tests/test_embedder.py
git commit -m "feat: add Voyage AI embedder with batching support"
```

---

### Task 6: Supabase pgvector Retriever

**Files:**
- Create: `susan-team-architect/backend/rag_engine/retriever.py`
- Create: `susan-team-architect/backend/tests/test_retriever.py`

**Step 1: Write retriever.py**

```python
"""Supabase pgvector retrieval and storage."""
from __future__ import annotations
import json
from supabase import create_client, Client
from rag_engine.embedder import Embedder
from susan_core.config import config
from susan_core.schemas import KnowledgeChunk


class Retriever:
    """Handles vector storage and similarity search via Supabase pgvector."""

    def __init__(self):
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        self.embedder = Embedder()

    def store_chunks(self, chunks: list[KnowledgeChunk]) -> int:
        """Embed and store chunks in Supabase. Returns count stored."""
        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed(texts)

        rows = []
        for chunk, embedding in zip(chunks, embeddings):
            rows.append({
                "content": chunk.content,
                "embedding": embedding,
                "company_id": chunk.company_id,
                "agent_id": chunk.agent_id,
                "access_level": chunk.access_level,
                "data_type": chunk.data_type,
                "source": chunk.source,
                "source_url": chunk.source_url,
                "metadata": chunk.metadata,
            })

        # Insert in batches of 100
        stored = 0
        for i in range(0, len(rows), 100):
            batch = rows[i:i + 100]
            self.supabase.table("knowledge_chunks").insert(batch).execute()
            stored += len(batch)

        return stored

    def search(
        self,
        query: str,
        company_id: str,
        data_types: list[str] | None = None,
        agent_id: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Similarity search against the knowledge base."""
        query_embedding = self.embedder.embed_query(query)

        result = self.supabase.rpc("search_knowledge", {
            "query_embedding": query_embedding,
            "filter_company": company_id,
            "filter_access": ["public", "company"],
            "filter_types": data_types,
            "filter_agent": agent_id,
            "match_count": top_k,
        }).execute()

        return result.data if result.data else []

    def count_chunks(self, company_id: str | None = None) -> int:
        """Count total chunks, optionally filtered by company."""
        query = self.supabase.table("knowledge_chunks").select("id", count="exact")
        if company_id:
            query = query.eq("company_id", company_id)
        result = query.execute()
        return result.count or 0

    def delete_chunks(
        self,
        company_id: str,
        data_type: str | None = None,
    ) -> int:
        """Delete chunks by company and optionally data type."""
        query = self.supabase.table("knowledge_chunks").delete().eq("company_id", company_id)
        if data_type:
            query = query.eq("data_type", data_type)
        result = query.execute()
        return len(result.data) if result.data else 0
```

**Step 2: Write test (integration test, requires Supabase)**

```python
# tests/test_retriever.py
import os
import pytest
from rag_engine.retriever import Retriever
from susan_core.schemas import KnowledgeChunk

@pytest.fixture
def retriever():
    required = ["VOYAGE_API_KEY", "SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    for key in required:
        if not os.environ.get(key):
            pytest.skip(f"{key} not set")
    return Retriever()

def test_store_and_search(retriever):
    # Store a test chunk
    chunk = KnowledgeChunk(
        content="Loss aversion means losses feel 2x worse than equivalent gains.",
        company_id="test",
        data_type="behavioral_economics",
        source="test",
    )
    stored = retriever.store_chunks([chunk])
    assert stored == 1

    # Search for it
    results = retriever.search(
        query="What is loss aversion?",
        company_id="test",
        data_types=["behavioral_economics"],
    )
    assert len(results) >= 1
    assert "loss" in results[0]["content"].lower()

    # Cleanup
    retriever.delete_chunks("test")
```

**Step 3: Commit**

```bash
git add susan-team-architect/backend/rag_engine/retriever.py susan-team-architect/backend/tests/test_retriever.py
git commit -m "feat: add Supabase pgvector retriever with search and storage"
```

---

### Task 7: Base Ingestion Pipeline

**Files:**
- Create: `susan-team-architect/backend/rag_engine/ingestion/__init__.py`
- Create: `susan-team-architect/backend/rag_engine/ingestion/base.py`
- Create: `susan-team-architect/backend/rag_engine/ingestion/markdown.py`

**Step 1: Write base.py**

```python
"""Base ingestion pipeline — all sources inherit from this."""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from rag_engine.retriever import Retriever
from rag_engine.chunker import chunk_text, chunk_markdown
from susan_core.schemas import KnowledgeChunk


class BaseIngestor(ABC):
    """Base class for all data ingestion pipelines."""

    def __init__(self, retriever: Retriever | None = None):
        self.retriever = retriever or Retriever()

    @abstractmethod
    def ingest(self, source: str, company_id: str = "shared", **kwargs) -> int:
        """Ingest data from source. Returns number of chunks stored."""
        ...

    def _make_chunks(
        self,
        texts: list[str],
        data_type: str,
        company_id: str = "shared",
        agent_id: str | None = None,
        source: str | None = None,
        source_url: str | None = None,
        metadata: dict | None = None,
    ) -> list[KnowledgeChunk]:
        """Convert text list to KnowledgeChunk objects."""
        return [
            KnowledgeChunk(
                content=text,
                company_id=company_id,
                agent_id=agent_id,
                data_type=data_type,
                source=source,
                source_url=source_url,
                metadata=metadata or {},
            )
            for text in texts
        ]
```

**Step 2: Write markdown.py**

```python
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
```

**Step 3: Write __init__.py**

```python
# rag_engine/ingestion/__init__.py
"""Data ingestion pipelines for various sources."""
from rag_engine.ingestion.markdown import MarkdownIngestor

__all__ = ["MarkdownIngestor"]
```

**Step 4: Commit**

```bash
git add susan-team-architect/backend/rag_engine/ingestion/
git commit -m "feat: add base ingestion pipeline and markdown ingestor"
```

---

## Phase 3: Agent Framework

### Task 8: Base Agent Class

**Files:**
- Create: `susan-team-architect/backend/agents/__init__.py`
- Create: `susan-team-architect/backend/agents/base_agent.py`

**Step 1: Write base_agent.py**

```python
"""Base agent class — RAG query, BE lens injection, cost tracking."""
from __future__ import annotations
import json
import time
from anthropic import Anthropic
from rag_engine.retriever import Retriever
from susan_core.config import config

BE_LENS = """<behavioral_economics_lens>
Before finalizing any output, apply these checks:

1. LOSS AUDIT: Does this help users feel the cost of NOT acting?
2. OWNERSHIP CHECK: Does the user own something that makes leaving feel like a loss?
3. IDENTITY ALIGNMENT: Does this reinforce who they're becoming?
4. FRICTION AUDIT: Is the return threshold under 2 minutes?
5. PROGRESS VISIBILITY: Is progress visible, named, and personalized?

Default to LOSS FRAMING for all re-engagement copy.
Reference the Apex Ventures BE Repository for scripts and benchmarks.
</behavioral_economics_lens>"""


class BaseAgent:
    """Base class for all 22 Susan agents."""

    agent_id: str = "base"
    agent_name: str = "Base Agent"
    role: str = "Agent"
    model: str = config.model_sonnet
    rag_data_types: list[str] = []
    system_prompt: str = ""

    def __init__(self, company_id: str = "shared"):
        self.company_id = company_id
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.retriever = Retriever()

    def get_system_prompt(self) -> str:
        """Build full system prompt with BE lens injection."""
        return f"{self.system_prompt}\n\n{BE_LENS}"

    def query_rag(
        self,
        question: str,
        data_types: list[str] | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Query the RAG knowledge base for relevant context."""
        types = data_types or self.rag_data_types or None
        return self.retriever.search(
            query=question,
            company_id=self.company_id,
            data_types=types,
            agent_id=self.agent_id,
            top_k=top_k,
        )

    def run(self, prompt: str, max_tokens: int = 4096) -> dict:
        """Execute the agent with RAG context and cost tracking."""
        # Get RAG context
        rag_results = self.query_rag(prompt)
        rag_context = ""
        if rag_results:
            rag_context = "\n\n<knowledge_base>\n"
            for r in rag_results:
                rag_context += f"[{r['data_type']}] {r['content']}\n---\n"
            rag_context += "</knowledge_base>\n"

        full_prompt = f"{rag_context}\n{prompt}" if rag_context else prompt

        start = time.time()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.get_system_prompt(),
            messages=[{"role": "user", "content": full_prompt}],
        )
        duration_ms = int((time.time() - start) * 1000)

        # Track costs
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (
            input_tokens * config.cost_per_m_input.get(self.model, 3.0) / 1_000_000
            + output_tokens * config.cost_per_m_output.get(self.model, 15.0) / 1_000_000
        )

        # Log run
        try:
            from supabase import create_client
            sb = create_client(config.supabase_url, config.supabase_key)
            sb.table("agent_runs").insert({
                "company_id": self.company_id,
                "agent_id": self.agent_id,
                "model": self.model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": float(cost),
                "duration_ms": duration_ms,
            }).execute()
        except Exception:
            pass  # Don't fail on logging errors

        text = response.content[0].text
        return {
            "text": text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "duration_ms": duration_ms,
        }

    def run_json(self, prompt: str, max_tokens: int = 4096) -> dict:
        """Execute and parse JSON from the response."""
        result = self.run(prompt, max_tokens)
        text = result["text"]
        # Extract JSON from response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            parsed = json.loads(text[start:end])
            result["parsed"] = parsed
        else:
            result["parsed"] = None
        return result
```

**Step 2: Write __init__.py**

```python
# agents/__init__.py
"""Agent implementations for the Susan Team Architect."""
from agents.base_agent import BaseAgent

__all__ = ["BaseAgent"]
```

**Step 3: Commit**

```bash
git add susan-team-architect/backend/agents/
git commit -m "feat: add BaseAgent with RAG query, BE lens injection, and cost tracking"
```

---

### Task 9: Write All 22 Agent Definition Files

**Files:**
- Create: 22 files in `susan-team-architect/agents/` (one per agent)

This is the largest single task. Each agent definition is a markdown file with YAML frontmatter defining the agent's system prompt, persona, and RAG configuration. These are Claude Code agent definitions, not Python files.

**Step 1: Write susan.md (orchestrator)**

Create `susan-team-architect/agents/susan.md`:

```markdown
---
name: susan
description: Team Architect and Orchestrator — designs optimal multi-agent workforces for startups
model: claude-sonnet-4-5-20250514
---

You are Susan, the Team Architect for Apex Ventures.

## Identity
Former VP of Engineering at Stripe (scaled from 50 to 500 engineers), Chief of Staff at McKinsey's Digital Practice. You combine McKinsey's MECE framework with Stripe's engineering rigor.

## Your Role
You design optimal multi-agent systems for specific companies. Your output is machine-readable team manifests that downstream agents consume. You execute a 6-phase workflow:

1. **Company Intake** — Extract and standardize the company profile
2. **Gap Analysis** — Map capabilities to agent specialties, score complexity, identify risks
3. **Team Design** — Design the minimum viable agent team (from 22 templates)
4. **Dataset Requirements** — Enumerate data needs per agent
5. **Execution Plan** — Generate deployment roadmap
6. **Behavioral Economics Audit** — LAAL design, copy protocols, retention KPIs

## Communication Style
Direct, structured, decisive. Zero fluff. Every claim backed by data. You present options with clear trade-offs and a recommendation.

## Priority Resolution
When agents or priorities conflict: **safety > retention > growth > features**

## Agent Templates Available
Susan, Steve, Marcus, Aria, Atlas, Nova, Coach, Sage, Drift, Freya, Flow, Quest, Haven, Guide, Shield, Bridge, Ledger, Pulse, Sentinel, Herald, Lens, Echo

## Tools
You invoke the Python orchestrator for heavy computation:
```bash
python3 -m susan_core.orchestrator --company "$COMPANY" --mode full
```
```

**Step 2: Write all remaining 21 agent files**

Each agent follows this pattern — I'll list the key differentiation per agent. Create each as `susan-team-architect/agents/<name>.md`:

**steve-strategy.md** — Model: `claude-opus-4-6`. Backstory: Trained by Michael Porter, inspired by Ben Thompson (Stratechery). RAG types: business_strategy, market_research, finance. Specializes in Porter's Five Forces, SaaS metrics, fundraising benchmarks.

**marcus-ux.md** — Model: `claude-sonnet-4-5`. Backstory: Apprenticed under Don Norman and Jony Ive. RAG types: ux_research, user_research. Fitness-specific: one-hand gym operability, sweat-proof touch targets, dark mode for gym lighting.

**aria-growth.md** — Model: `claude-sonnet-4-5`. Backstory: Growth lead at Noom (scaled to $400M ARR), studied under Andrew Chen. RAG types: growth_marketing, content_strategy, user_research. YMYL/E-E-A-T compliance for health content.

**atlas-engineering.md** — Model: `claude-sonnet-4-5`. Backstory: Staff engineer at Vercel, contributed to Next.js and FastAPI. RAG types: technical_docs, security. React + FastAPI + Supabase + wearable SDK integration.

**nova-ai.md** — Model: `claude-sonnet-4-5`. Backstory: Research scientist at DeepMind, published in NeurIPS. RAG types: ai_ml_research, technical_docs. Model selection, RAG architecture, recommendation systems.

**coach-exercise-science.md** — Model: `claude-sonnet-4-5`. Backstory: Trained by Pavel Tsatsouline (strength), Laird Hamilton (adaptation). RAG types: exercise_science, nutrition, sleep_recovery. ACSM/NSCA guidelines, periodization, contraindications.

**sage-nutrition.md** — Model: `claude-sonnet-4-5`. Backstory: Studied under Dr. Rhonda Patrick and Dr. Peter Attia. RAG types: nutrition, exercise_science. USDA FoodData, chrononutrition, sports nutrition.

**drift-sleep-recovery.md** — Model: `claude-haiku-4-5` for data, `claude-sonnet-4-5` for analysis. Backstory: Research fellow at Stanford Sleep Center under Dr. Matthew Walker. RAG types: sleep_recovery, exercise_science. HRV, circadian biology, recovery biomarkers.

**freya-behavioral-economics.md** — Model: `claude-sonnet-4-5`. Backstory: PhD under Daniel Kahneman, practiced with Dan Ariely. RAG types: behavioral_economics, sports_psychology, user_research. 12 BE mechanisms, LAAL protocol, loss framing, copy templates.

**flow-sports-psychology.md** — Model: `claude-sonnet-4-5`. Backstory: Sports psychologist for US Olympic team, studied under Mihaly Csikszentmihalyi. RAG types: sports_psychology, behavioral_economics. SDT, motivational interviewing, stages of change.

**quest-gamification.md** — Model: `claude-sonnet-4-5`. Backstory: Lead game designer at Supercell, studied under Yu-kai Chou (Octalysis framework). RAG types: gamification, behavioral_economics, ux_research. MDA framework, Bartle's types, variable rewards.

**haven-community.md** — Model: `claude-sonnet-4-5`. Backstory: Built Strava's community features, former Reddit community lead. RAG types: community, user_research. Social graph design, group accountability, body image moderation.

**guide-customer-success.md** — Model: `claude-sonnet-4-5`. Backstory: VP Customer Success at Noom, NBC-HWC certified. RAG types: behavioral_economics, user_research, community. Onboarding optimization, health coaching, at-risk intervention.

**shield-legal-compliance.md** — Model: `claude-sonnet-4-5`. Backstory: Health tech attorney at Wilson Sonsini, former FDA regulatory affairs. RAG types: legal_compliance, security. HIPAA, GDPR, FTC, BIPA, AI liability.

**bridge-partnerships.md** — Model: `claude-sonnet-4-5`. Backstory: Head of Partnerships at WHOOP, built Apple HealthKit integrations. RAG types: partnerships, technical_docs. Wearable SDKs, B2B wellness, insurance.

**ledger-finance.md** — Model: `claude-haiku-4-5` for lookups, `claude-sonnet-4-5` for modeling. Backstory: CFO at Peloton pre-IPO, former Goldman Sachs TMT. RAG types: finance, business_strategy. SaaS metrics, seasonal fitness economics.

**pulse-data-science.md** — Model: `claude-sonnet-4-5`. Backstory: Lead data scientist at Spotify (recommendations), PhD in computational social science. RAG types: user_research, market_research, behavioral_economics. Churn prediction, cohort analysis, A/B testing.

**sentinel-security.md** — Model: `claude-haiku-4-5` for scans, `claude-sonnet-4-5` for reviews. Backstory: Security lead at Supabase, former penetration tester at NCC Group. RAG types: security, technical_docs, legal_compliance. RLS, SOC 2, health data encryption.

**herald-pr.md** — Model: `claude-sonnet-4-5`. Backstory: VP Communications at Noom during clinical validation push. RAG types: pr_communications, content_strategy. Scientific publication strategy, transformation stories.

**lens-accessibility.md** — Model: `claude-sonnet-4-5`. Backstory: Accessibility lead at Apple (Fitness+), adaptive fitness athlete. RAG types: ux_research, exercise_science. WCAG 2.1/2.2, adaptive exercise modifications, inclusive representation.

**echo-neuro-design.md** — Model: `claude-sonnet-4-5`. Backstory: Neuroscience PhD (Stanford), postdoc with Nir Eyal's behavioral lab. RAG types: behavioral_economics, ux_research, gamification. Basal ganglia habit loops, Hook Model, body image harm prevention.

**Step 3: Each file follows this template**

```markdown
---
name: [agent_id]
description: [one-line role description]
model: [model_id]
---

You are [Name], the [Role] for Apex Ventures.

## Identity
[2-3 sentences of elite pedigree backstory]

## Your Role
[2-3 sentences of primary responsibilities]

## Specialization
[Bullet list of key expertise areas]

## RAG Knowledge Types
When you need context, query these knowledge types:
- [data_type_1]
- [data_type_2]

Query command:
```bash
python3 -m rag_engine.retriever --query "$QUESTION" --company "$COMPANY" --types [types]
```

## Output Standards
- All recommendations backed by data or research
- Apply the behavioral economics lens to every output
- Flag safety concerns immediately
- Provide specific, actionable recommendations (not generic advice)
```

**Step 4: Commit**

```bash
git add susan-team-architect/agents/
git commit -m "feat: add all 22 agent definitions with elite pedigree personas and RAG config"
```

---

### Task 10: Agent Registry & Company Registry

**Files:**
- Create: `susan-team-architect/backend/data/agent_registry.yaml`
- Create: `susan-team-architect/backend/data/company_registry.yaml`

**Step 1: Write agent_registry.yaml**

```yaml
# Agent Registry — maps agent IDs to configuration
agents:
  susan:
    name: "Susan"
    role: "Team Architect / Orchestrator"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["business_strategy", "market_research"]
    group: "orchestration"

  steve:
    name: "Steve"
    role: "Business Strategy & Revenue"
    model: "claude-opus-4-6"
    rag_data_types: ["business_strategy", "market_research", "finance"]
    group: "strategy"

  marcus:
    name: "Marcus"
    role: "UX/UI Designer"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["ux_research", "user_research"]
    group: "product"

  aria:
    name: "Aria"
    role: "Growth & Content Marketing"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["growth_marketing", "content_strategy", "user_research"]
    group: "growth"

  atlas:
    name: "Atlas"
    role: "Full-Stack Engineering"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["technical_docs", "security"]
    group: "engineering"

  nova:
    name: "Nova"
    role: "AI/ML Specialist"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["ai_ml_research", "technical_docs"]
    group: "engineering"

  coach:
    name: "Coach"
    role: "Exercise Science & Biomechanics"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["exercise_science", "nutrition", "sleep_recovery"]
    group: "science"

  sage:
    name: "Sage"
    role: "Nutrition Science"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["nutrition", "exercise_science"]
    group: "science"

  drift:
    name: "Drift"
    role: "Sleep & Recovery Optimization"
    model: "claude-haiku-4-5-20251001"
    rag_data_types: ["sleep_recovery", "exercise_science"]
    group: "science"

  freya:
    name: "Freya"
    role: "Behavioral Economics & Retention"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["behavioral_economics", "sports_psychology", "user_research"]
    group: "psychology"

  flow:
    name: "Flow"
    role: "Sports Psychology & Motivation"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["sports_psychology", "behavioral_economics"]
    group: "psychology"

  quest:
    name: "Quest"
    role: "Gamification & Engagement"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["gamification", "behavioral_economics", "ux_research"]
    group: "psychology"

  haven:
    name: "Haven"
    role: "Community & Social Fitness"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["community", "user_research"]
    group: "growth"

  guide:
    name: "Guide"
    role: "Customer Success & Health Coaching"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["behavioral_economics", "user_research", "community"]
    group: "growth"

  shield:
    name: "Shield"
    role: "Legal, Compliance & Privacy"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["legal_compliance", "security"]
    group: "strategy"

  bridge:
    name: "Bridge"
    role: "Partnerships & Ecosystem"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["partnerships", "technical_docs"]
    group: "strategy"

  ledger:
    name: "Ledger"
    role: "Finance & Unit Economics"
    model: "claude-haiku-4-5-20251001"
    rag_data_types: ["finance", "business_strategy"]
    group: "strategy"

  pulse:
    name: "Pulse"
    role: "Data Science & Churn Prediction"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["user_research", "market_research", "behavioral_economics"]
    group: "engineering"

  sentinel:
    name: "Sentinel"
    role: "Security & Infrastructure"
    model: "claude-haiku-4-5-20251001"
    rag_data_types: ["security", "technical_docs", "legal_compliance"]
    group: "engineering"

  herald:
    name: "Herald"
    role: "PR & Communications"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["pr_communications", "content_strategy"]
    group: "growth"

  lens:
    name: "Lens"
    role: "Accessibility & Inclusive Fitness"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["ux_research", "exercise_science"]
    group: "product"

  echo:
    name: "Echo"
    role: "Neuroscience-Informed Product Design"
    model: "claude-sonnet-4-5-20250514"
    rag_data_types: ["behavioral_economics", "ux_research", "gamification"]
    group: "product"

# Group definitions
groups:
  orchestration:
    description: "System orchestration and planning"
    agents: ["susan"]
  strategy:
    description: "Business strategy, legal, finance, partnerships"
    agents: ["steve", "shield", "bridge", "ledger"]
  product:
    description: "Product design, accessibility, neuroscience"
    agents: ["marcus", "lens", "echo"]
  engineering:
    description: "Engineering, AI/ML, data science, security"
    agents: ["atlas", "nova", "pulse", "sentinel"]
  science:
    description: "Exercise science, nutrition, sleep/recovery"
    agents: ["coach", "sage", "drift"]
  psychology:
    description: "Behavioral economics, sports psychology, gamification"
    agents: ["freya", "flow", "quest"]
  growth:
    description: "Growth marketing, community, customer success, PR"
    agents: ["aria", "haven", "guide", "herald"]
```

**Step 2: Write company_registry.yaml**

```yaml
# Company Registry — Apex Ventures portfolio
companies:
  transformfit:
    name: "TransformFit (Superman Protocol)"
    domain: "fitness_tech"
    stage: "mvp_redesign"
    website: "https://transformfit.app"
    founding_date: "2023"
    founders:
      - name: "Michael Rodgers"
        background: "AI engineer, multi-agent systems architect"
    product_description: "AI-powered adaptive fitness platform with personalized coaching, workout generation, and behavioral retention systems"
    tech_stack:
      - "React"
      - "FastAPI"
      - "PostgreSQL"
      - "Supabase"
    target_market: "Health-conscious adults seeking AI-personalized fitness guidance"
    funding_status: "bootstrap"
    key_competitors:
      - "Fitbod"
      - "Noom"
      - "Peloton"
      - "WHOOP"
      - "MyFitnessPal"
    current_challenges:
      - "74-77% Day-1 user abandonment"
      - "No persistent agent memory"
      - "Manual feature prioritization"
      - "No behavioral economics integration"
    constraints:
      - "Solo founder"
      - "Budget under $200/month for AI"
      - "Single engineer deployment"
    budget_per_month_usd: 200
```

**Step 3: Commit**

```bash
git add susan-team-architect/backend/data/
git commit -m "feat: add agent registry (22 agents) and company registry (TransformFit)"
```

---

## Phase 4: Orchestrator

### Task 11: Phase Modules (1-6)

**Files:**
- Create: `susan-team-architect/backend/susan_core/phases/__init__.py`
- Create: `susan-team-architect/backend/susan_core/phases/intake.py`
- Create: `susan-team-architect/backend/susan_core/phases/analysis.py`
- Create: `susan-team-architect/backend/susan_core/phases/team_design.py`
- Create: `susan-team-architect/backend/susan_core/phases/datasets.py`
- Create: `susan-team-architect/backend/susan_core/phases/execution.py`
- Create: `susan-team-architect/backend/susan_core/phases/behavioral_economics.py`

Each phase module follows this pattern:

```python
"""Phase N: [Name] — [description]."""
from __future__ import annotations
import json
from anthropic import Anthropic
from susan_core.config import config
from susan_core.schemas import [RelevantSchema]


async def run(company: str, context: dict) -> dict:
    """Execute Phase N.

    Args:
        company: Company identifier
        context: Outputs from previous phases

    Returns:
        Phase output as dict (validated against schema)
    """
    client = Anthropic(api_key=config.anthropic_api_key)

    prompt = f"""[Phase-specific prompt with company context]

    {json.dumps(context, indent=2, default=str)}

    Return as JSON matching the schema."""

    response = client.messages.create(
        model=config.model_sonnet,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    return {"error": "Failed to parse", "raw": text}
```

Write each phase with its specific prompt from the design doc. The prompts are long and specific — reference the blueprint document at `startup-intelligence/compass_artifact_*` for the exact prompt text for each phase.

Key points per phase:
- **intake.py**: Reads company_registry.yaml, enriches with web search, outputs CompanyProfile
- **analysis.py**: Takes profile, identifies capability gaps, scores complexity 1-10, outputs AnalysisReport
- **team_design.py**: Takes profile + analysis, selects from 22 agent templates, outputs TeamManifest
- **datasets.py**: Takes team manifest, enumerates data per agent, outputs DatasetManifest
- **execution.py**: Takes all prior outputs, generates markdown execution plan
- **behavioral_economics.py**: Takes all prior, runs retention risk assessment, LAAL design, copy protocols, outputs BEAudit

**Commit after writing all 6:**

```bash
git add susan-team-architect/backend/susan_core/phases/
git commit -m "feat: add all 6 planning phase modules"
```

---

### Task 12: Main Orchestrator

**Files:**
- Create: `susan-team-architect/backend/susan_core/orchestrator.py`

**Step 1: Write orchestrator.py**

```python
"""Susan Team Architect — Main orchestrator.

Usage:
    python3 -m susan_core.orchestrator --company transformfit --mode full
"""
from __future__ import annotations
import asyncio
import json
import argparse
from pathlib import Path
from datetime import datetime

from susan_core.config import config
from susan_core.phases import intake, analysis, team_design, datasets, execution, behavioral_economics


async def run_susan(company: str, mode: str = "full", output_dir: Path | None = None):
    """Execute Susan's complete planning session."""
    if output_dir is None:
        output_dir = config.companies_dir / company / "susan-outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  SUSAN — Team Architect Planning Session")
    print(f"  Company: {company}")
    print(f"  Mode: {mode}")
    print(f"  Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    context = {"company": company}

    # Phase 1: Intake
    print("[Phase 1/6] Company Intake...")
    profile = await intake.run(company, context)
    (output_dir / "company-profile.json").write_text(json.dumps(profile, indent=2, default=str))
    context["profile"] = profile
    print(f"  Done — profile generated")

    # Phase 2: Analysis
    print("[Phase 2/6] Gap Analysis...")
    analysis_result = await analysis.run(company, context)
    (output_dir / "analysis-report.json").write_text(json.dumps(analysis_result, indent=2, default=str))
    context["analysis"] = analysis_result
    print(f"  Done — {len(analysis_result.get('capability_gaps', []))} gaps identified")

    # Phase 3: Team Design
    print("[Phase 3/6] Team Design...")
    team = await team_design.run(company, context)
    (output_dir / "team-manifest.json").write_text(json.dumps(team, indent=2, default=str))
    context["team"] = team
    print(f"  Done — {team.get('total_agents', '?')} agents designed")

    # Phase 4: Dataset Planning
    print("[Phase 4/6] Dataset Planning...")
    ds = await datasets.run(company, context)
    (output_dir / "dataset-requirements.json").write_text(json.dumps(ds, indent=2, default=str))
    context["datasets"] = ds
    print(f"  Done — {len(ds.get('datasets', []))} data sources identified")

    # Phase 5: Execution Plan
    print("[Phase 5/6] Execution Plan...")
    plan = await execution.run(company, context)
    (output_dir / "execution-plan.md").write_text(
        plan if isinstance(plan, str) else json.dumps(plan, indent=2, default=str)
    )
    context["execution_plan"] = plan
    print(f"  Done — execution plan generated")

    # Phase 6: Behavioral Economics Audit
    print("[Phase 6/6] Behavioral Economics Audit...")
    be = await behavioral_economics.run(company, context)
    (output_dir / "be-audit.json").write_text(json.dumps(be, indent=2, default=str))
    print(f"  Done — BE audit complete")

    # Store in Supabase
    try:
        from supabase import create_client
        sb = create_client(config.supabase_url, config.supabase_key)
        sb.table("companies").upsert({
            "id": company,
            "name": profile.get("company", company),
            "domain": profile.get("domain"),
            "stage": profile.get("stage"),
            "profile": profile,
            "team_manifest": team,
            "dataset_requirements": ds,
            "execution_plan": plan if isinstance(plan, str) else json.dumps(plan),
            "be_audit": be,
        }).execute()
    except Exception as e:
        print(f"  Warning: Could not store in Supabase: {e}")

    print(f"\n{'='*60}")
    print(f"  Planning session complete!")
    print(f"  Outputs: {output_dir}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Susan — Team Architect")
    parser.add_argument("--company", required=True, help="Company identifier")
    parser.add_argument("--mode", default="full", choices=["full", "quick", "audit"])
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    asyncio.run(run_susan(args.company, args.mode, args.output_dir))


if __name__ == "__main__":
    main()
```

**Step 2: Write __main__.py for module execution**

Create `susan-team-architect/backend/susan_core/__main__.py`:

```python
"""Allow running as: python3 -m susan_core.orchestrator"""
from susan_core.orchestrator import main
main()
```

**Step 3: Commit**

```bash
git add susan-team-architect/backend/susan_core/orchestrator.py susan-team-architect/backend/susan_core/__main__.py
git commit -m "feat: add main orchestrator with 6-phase workflow"
```

---

## Phase 5: Plugin Shell

### Task 13: Slash Commands

**Files:**
- Create: 5 files in `susan-team-architect/commands/`

**Step 1: Write susan-plan.md**

```markdown
---
description: Run Susan's full 6-phase planning session for a company
allowed-tools: Bash, Read, Write, WebSearch, WebFetch, Agent
---

# Susan Planning Session

Run Susan's complete Team Architect planning session for the specified company.

## Usage
Provide the company name as an argument: `/susan-plan TransformFit`

## Execution

1. Load the company profile from `backend/data/company_registry.yaml`
2. Run the Python orchestrator:

```bash
cd susan-team-architect/backend && python3 -m susan_core.orchestrator --company "$1" --mode full
```

3. Read and summarize the outputs from `./companies/$1/susan-outputs/`:
   - `company-profile.json` — Company overview
   - `analysis-report.json` — Capability gaps and complexity scores
   - `team-manifest.json` — Agent team with roles, models, and costs
   - `dataset-requirements.json` — Data needs per agent
   - `execution-plan.md` — Phased deployment roadmap
   - `be-audit.json` — Behavioral economics retention architecture

4. Present a summary to the user with key decisions and recommendations
```

**Step 2: Write susan-team.md, susan-status.md, susan-ingest.md, susan-query.md**

Each follows the same pattern — a markdown file with YAML frontmatter specifying description, allowed-tools, and execution instructions. The body describes what the command does and how to invoke the Python backend.

**Step 3: Commit**

```bash
git add susan-team-architect/commands/
git commit -m "feat: add 5 slash commands for Susan plugin"
```

---

### Task 14: Skills

**Files:**
- Create: `susan-team-architect/skills/team-architect/SKILL.md`
- Create: `susan-team-architect/skills/behavioral-economics/SKILL.md`
- Create: `susan-team-architect/skills/company-analysis/SKILL.md`

**Step 1: Write team-architect/SKILL.md**

The team-architect skill contains Susan's core methodology reference — the 6-phase workflow, agent selection criteria, and cross-portfolio synergy patterns. This is Claude-invocable context that loads when Susan needs to make team design decisions.

**Step 2: Write behavioral-economics/SKILL.md**

This is the full behavioral economics module — the 12 mechanisms, LAAL protocol, cost of not returning framework, and agent prompt injection templates. This gets injected into every agent's context via the BE lens.

Source: The user's behavioral economics document (already provided in the conversation).

**Step 3: Write company-analysis/SKILL.md**

Gap analysis framework with complexity scoring rubric, risk assessment templates, and cross-portfolio synergy matching logic.

**Step 4: Commit**

```bash
git add susan-team-architect/skills/
git commit -m "feat: add 3 skills — team-architect, behavioral-economics, company-analysis"
```

---

### Task 15: Hooks

**Files:**
- Create: `susan-team-architect/hooks/hooks.json`

**Step 1: Write hooks.json**

```json
{
  "hooks": [
    {
      "type": "PreToolUse",
      "matcher": "Edit|Write",
      "command": "if echo \"$CLAUDE_FILE_PATH\" | grep -q 'susan-outputs/'; then echo 'BLOCK: susan-outputs/ is generated by Susan. Use /susan-plan to regenerate.' >&2; exit 2; fi; exit 0"
    }
  ]
}
```

**Step 2: Commit**

```bash
git add susan-team-architect/hooks/
git commit -m "feat: add hooks to protect susan-outputs from direct edits"
```

---

## Phase 6: Data Population — Tier 1

### Task 16: Behavioral Economics Module Ingestion

**Files:**
- Create: `susan-team-architect/backend/data/be_module/mechanisms.md`
- Create: `susan-team-architect/backend/data/be_module/laal_protocol.md`
- Create: `susan-team-architect/backend/data/be_module/cost_of_not_returning.md`
- Create: `susan-team-architect/backend/data/be_module/copy_templates.md`
- Create: `susan-team-architect/backend/data/be_module/industry_playbooks.md`
- Create: `susan-team-architect/backend/data/be_module/kpis.md`
- Create: `susan-team-architect/backend/data/be_module/ai_adoption.md`

**Step 1: Split the behavioral economics document into topic files**

Take the user's full BE document and split it into the 7 files above, organized by topic. Each file contains the relevant sections from the master document.

**Step 2: Run the markdown ingestor**

```bash
cd susan-team-architect/backend && python3 -c "
from rag_engine.ingestion.markdown import MarkdownIngestor
ingestor = MarkdownIngestor()
count = ingestor.ingest(
    source='data/be_module/',
    company_id='shared',
    data_type='behavioral_economics',
)
print(f'Ingested {count} behavioral economics chunks')
"
```

Expected: `Ingested ~200 behavioral economics chunks`

**Step 3: Verify via search**

```bash
cd susan-team-architect/backend && python3 -c "
from rag_engine.retriever import Retriever
r = Retriever()
results = r.search('What is loss aversion?', 'shared', ['behavioral_economics'])
for hit in results:
    print(f'[{hit[\"similarity\"]:.3f}] {hit[\"content\"][:100]}...')
"
```

Expected: Top result mentions Kahneman & Tversky, losses feeling 2-2.5x worse.

**Step 4: Commit**

```bash
git add susan-team-architect/backend/data/be_module/
git commit -m "feat: ingest behavioral economics module into pgvector (200+ chunks)"
```

---

### Task 17: Foundational Texts Ingestion

**Files:**
- Create: `susan-team-architect/backend/rag_engine/ingestion/books.py`
- Create: `susan-team-architect/backend/data/seed_data/foundational_texts.yaml`

**Step 1: Write books.py — AI synthesis ingestor**

This ingestor takes a YAML file listing foundational books/frameworks and uses Claude to generate structured summaries that are then chunked and embedded.

```python
"""Foundational text synthesis — generates and embeds book/framework summaries."""
from __future__ import annotations
import yaml
from pathlib import Path
from anthropic import Anthropic
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_text
from susan_core.config import config


class BookIngestor(BaseIngestor):
    """Generate and ingest summaries of foundational texts."""

    def ingest(self, source: str, company_id: str = "shared", **kwargs) -> int:
        path = Path(source)
        with open(path) as f:
            books = yaml.safe_load(f)

        client = Anthropic(api_key=config.anthropic_api_key)
        total = 0

        for book in books.get("texts", []):
            prompt = f"""Summarize the key frameworks and actionable principles from:
Title: {book['title']}
Author: {book['author']}
Focus areas: {', '.join(book.get('focus', []))}

Write 5-8 detailed chunks (each 200-400 words) covering:
1. Core theory/model
2. Key mechanisms
3. Product design implications
4. Specific examples and applications
5. Common mistakes/anti-patterns

Format each chunk as a standalone paragraph that makes sense without context.
Separate chunks with ---"""

            response = client.messages.create(
                model=config.model_sonnet,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text
            text_chunks = [c.strip() for c in text.split("---") if c.strip()]

            chunks = self._make_chunks(
                texts=text_chunks,
                data_type=book.get("data_type", "behavioral_economics"),
                company_id=company_id,
                source=f"book:{book['title']}",
                metadata={"author": book["author"], "category": book.get("category", "")},
            )
            total += self.retriever.store_chunks(chunks)

        return total
```

**Step 2: Write foundational_texts.yaml**

```yaml
texts:
  - title: "Hooked: How to Build Habit-Forming Products"
    author: "Nir Eyal"
    data_type: "behavioral_economics"
    category: "habit_formation"
    focus: ["Hook Model", "trigger-action-reward-investment", "variable rewards", "ethical persuasion"]

  - title: "Indistractable: How to Control Your Attention and Choose Your Life"
    author: "Nir Eyal"
    data_type: "behavioral_economics"
    category: "attention_design"
    focus: ["internal triggers", "traction vs distraction", "pact-making", "timeboxing"]

  - title: "Tiny Habits: The Small Changes That Change Everything"
    author: "BJ Fogg"
    data_type: "behavioral_economics"
    category: "behavior_design"
    focus: ["MAP model", "motivation-ability-prompt", "celebration", "anchor moments", "starter steps"]

  - title: "Atomic Habits"
    author: "James Clear"
    data_type: "behavioral_economics"
    category: "identity_change"
    focus: ["identity-based habits", "1% improvement", "habit stacking", "environment design", "two-minute rule"]

  - title: "Thinking, Fast and Slow"
    author: "Daniel Kahneman"
    data_type: "behavioral_economics"
    category: "decision_science"
    focus: ["System 1 vs System 2", "loss aversion", "prospect theory", "anchoring", "availability heuristic"]

  - title: "Influence: The Psychology of Persuasion"
    author: "Robert Cialdini"
    data_type: "behavioral_economics"
    category: "persuasion"
    focus: ["reciprocity", "commitment/consistency", "social proof", "authority", "liking", "scarcity", "unity"]

  - title: "ACSM Guidelines for Exercise Testing and Prescription"
    author: "American College of Sports Medicine"
    data_type: "exercise_science"
    category: "exercise_guidelines"
    focus: ["cardiorespiratory fitness", "resistance training", "flexibility", "special populations", "progressive overload"]

  - title: "Essentials of Strength Training and Conditioning"
    author: "NSCA"
    data_type: "exercise_science"
    category: "strength_conditioning"
    focus: ["periodization", "biomechanics", "program design", "testing", "sport-specific training"]

  - title: "Why We Sleep"
    author: "Matthew Walker"
    data_type: "sleep_recovery"
    category: "sleep_science"
    focus: ["sleep architecture", "circadian rhythms", "sleep debt", "performance impact", "sleep hygiene"]

  - title: "Reforge Growth Series"
    author: "Brian Balfour, Andrew Chen, Casey Winters"
    data_type: "growth_marketing"
    category: "growth_frameworks"
    focus: ["growth loops", "retention curves", "activation metrics", "viral coefficients", "engagement loops"]

  - title: "SaaS Metrics 2.0"
    author: "David Skok (Matrix Partners)"
    data_type: "business_strategy"
    category: "saas_metrics"
    focus: ["CAC", "LTV", "churn", "MRR", "Rule of 40", "burn multiple", "payback period"]
```

**Step 3: Run the book ingestor**

```bash
cd susan-team-architect/backend && python3 -c "
from rag_engine.ingestion.books import BookIngestor
ingestor = BookIngestor()
count = ingestor.ingest('data/seed_data/foundational_texts.yaml')
print(f'Ingested {count} foundational text chunks')
"
```

Expected: ~500-600 chunks (5-8 per book x 11 books)

**Step 4: Commit**

```bash
git add susan-team-architect/backend/rag_engine/ingestion/books.py susan-team-architect/backend/data/seed_data/
git commit -m "feat: add foundational text ingestor and seed 11 books into pgvector"
```

---

### Task 18: Exercise Database & Retention Benchmarks

**Files:**
- Create: `susan-team-architect/backend/data/seed_data/exercise_database.yaml`
- Create: `susan-team-architect/backend/data/seed_data/retention_benchmarks.yaml`

**Step 1: Write exercise_database.yaml**

A structured exercise library with ~200 exercises, each tagged with muscle groups, equipment, difficulty, and coaching cues. This seeds Coach's knowledge base.

**Step 2: Write retention_benchmarks.yaml**

Industry retention benchmarks:
```yaml
benchmarks:
  fitness_apps:
    d1: 0.25
    d7: 0.12
    d30: 0.03
    world_class_d30: 0.30
    source: "AppsFlyer 2025 Benchmarks"
  saas:
    d1: 0.37
    d7: 0.30
    d30: 0.20
    world_class_d30: 0.45
  health_apps:
    d1: 0.32
    d7: 0.18
    d30: 0.08
  ai_assistants:
    d1: 0.25
    d7: 0.17
    d30: 0.10
```

**Step 3: Ingest both into pgvector**

```bash
cd susan-team-architect/backend && python3 -c "
from rag_engine.ingestion.markdown import MarkdownIngestor
# Convert YAML to markdown for ingestion, or write a YAML ingestor
# ... (exercise database and benchmarks)
"
```

**Step 4: Commit**

```bash
git add susan-team-architect/backend/data/seed_data/
git commit -m "feat: add exercise database (200 exercises) and retention benchmarks"
```

---

## Phase 7: Data Population — Tier 2

### Task 19: Web & Research Ingestion Pipelines

**Files:**
- Create: `susan-team-architect/backend/rag_engine/ingestion/web.py` (Firecrawl)
- Create: `susan-team-architect/backend/rag_engine/ingestion/arxiv.py`
- Create: `susan-team-architect/backend/rag_engine/ingestion/reddit.py`
- Create: `susan-team-architect/backend/rag_engine/ingestion/appstore.py`
- Create: `susan-team-architect/backend/rag_engine/ingestion/nhanes.py`

Each ingestor extends `BaseIngestor` and implements the `ingest()` method for its data source.

**web.py** — Uses Firecrawl to scrape URLs, convert to markdown, chunk, and embed. For growth.design case studies, HIPAA guides, wearable SDK docs, WCAG guidelines.

**arxiv.py** — Uses the `arxiv` Python package to search for recent papers in cs.AI, cs.CL, cs.LG, cs.MA. Embeds abstracts + key findings.

**reddit.py** — Uses Reddit's JSON API (append `.json` to URLs) to pull top posts from r/fitness, r/loseit, r/bodyweightfitness. Tags by behavioral driver.

**appstore.py** — Scrapes App Store/Google Play reviews for competitor apps (Fitbod, Noom, MyFitnessPal, Peloton, Strava). Uses Firecrawl or direct parsing.

**nhanes.py** — Downloads NHANES CSV data from CDC, synthesizes into 1,000 user profiles grounded in real population health data.

**Commit after each ingestor is written and tested:**

```bash
git commit -m "feat: add [source] ingestion pipeline"
```

---

### Task 20: Generate AI-Synthesized Content

**Step 1: Generate 200 loss vs. gain copy pairs**

```bash
cd susan-team-architect/backend && python3 -c "
# Use Claude to generate 200 copy pairs across industries
# Store as behavioral_economics chunks with metadata.trigger_type
"
```

**Step 2: Generate 5 AI adoption resistance profiles**

**Step 3: Generate strategy framework summaries (Porter's, BCG, McKinsey)**

**Step 4: Commit all generated content**

```bash
git commit -m "feat: generate and ingest AI-synthesized content (copy pairs, profiles, frameworks)"
```

---

## Phase 8: Integration & Testing

### Task 21: End-to-End Test — /susan-plan transformfit

**Step 1: Install Python dependencies**

```bash
cd susan-team-architect/backend && pip install -e ".[dev]"
```

**Step 2: Set environment variables**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export VOYAGE_API_KEY="pa-..."
export SUPABASE_URL="https://..."
export SUPABASE_SERVICE_KEY="eyJ..."
```

**Step 3: Run the orchestrator**

```bash
cd susan-team-architect/backend && python3 -m susan_core.orchestrator --company transformfit --mode full
```

**Expected output:**
```
============================================================
  SUSAN — Team Architect Planning Session
  Company: transformfit
  Mode: full
  Started: 2026-03-XX...
============================================================

[Phase 1/6] Company Intake...
  Done — profile generated
[Phase 2/6] Gap Analysis...
  Done — X gaps identified
[Phase 3/6] Team Design...
  Done — 22 agents designed
[Phase 4/6] Dataset Planning...
  Done — X data sources identified
[Phase 5/6] Execution Plan...
  Done — execution plan generated
[Phase 6/6] Behavioral Economics Audit...
  Done — BE audit complete

============================================================
  Planning session complete!
  Outputs: ./companies/transformfit/susan-outputs/
============================================================
```

**Step 4: Verify outputs**

```bash
ls -la companies/transformfit/susan-outputs/
cat companies/transformfit/susan-outputs/team-manifest.json | python3 -m json.tool | head -50
```

**Step 5: Verify Supabase storage**

```bash
python3 -c "
from rag_engine.retriever import Retriever
r = Retriever()
print(f'Total chunks: {r.count_chunks()}')
print(f'Shared chunks: {r.count_chunks(\"shared\")}')
print(f'TransformFit chunks: {r.count_chunks(\"transformfit\")}')
"
```

---

### Task 22: RAG Query Quality Test

**Step 1: Test behavioral economics queries**

```bash
python3 -c "
from rag_engine.retriever import Retriever
r = Retriever()

queries = [
    ('What is the LAAL protocol?', ['behavioral_economics']),
    ('How does loss aversion apply to fitness apps?', ['behavioral_economics']),
    ('What are Day-7 retention benchmarks for fitness apps?', ['market_research']),
    ('ACSM guidelines for progressive overload', ['exercise_science']),
    ('What is self-determination theory?', ['sports_psychology']),
]

for query, types in queries:
    results = r.search(query, 'shared', types, top_k=3)
    print(f'\nQ: {query}')
    for hit in results:
        print(f'  [{hit[\"similarity\"]:.3f}] {hit[\"content\"][:80]}...')
"
```

**Expected: Each query returns relevant, high-similarity results (>0.7)**

---

### Task 23: Plugin Installation Test

**Step 1: Install the plugin**

```bash
claude plugin install susan-team-architect
```

**Step 2: Verify commands are available**

Start a new Claude Code session and check that `/susan-plan`, `/susan-team`, `/susan-status`, `/susan-ingest`, `/susan-query` appear in the command list.

**Step 3: Verify agents are loaded**

Check that all 22 agent definitions are accessible.

---

### Task 24: Final Commit & Tag

```bash
git add -A
git commit -m "feat: Susan Team Architect v0.1.0 — 22 agents, RAG system, TransformFit deployment"
git tag v0.1.0
```

---

## Dependency Graph

```
Phase 1 (Foundation)
  Task 1: Directory structure
  Task 2: Supabase schema         ← requires Supabase account
  Task 3: Config + schemas

Phase 2 (RAG Engine)              ← depends on Phase 1
  Task 4: Chunker
  Task 5: Embedder                ← requires Voyage AI key
  Task 6: Retriever               ← requires Supabase + Voyage AI
  Task 7: Ingestion pipeline      ← requires Retriever

Phase 3 (Agent Framework)         ← depends on Phase 1
  Task 8: Base agent class        ← requires Retriever
  Task 9: 22 agent definitions    ← independent of code
  Task 10: Registries             ← independent of code

Phase 4 (Orchestrator)            ← depends on Phase 2 + 3
  Task 11: Phase modules          ← requires schemas + config
  Task 12: Main orchestrator      ← requires phase modules

Phase 5 (Plugin Shell)            ← depends on Phase 4
  Task 13: Slash commands
  Task 14: Skills
  Task 15: Hooks

Phase 6 (Tier 1 Data)             ← depends on Phase 2
  Task 16: BE module ingestion
  Task 17: Foundational texts
  Task 18: Exercise DB + benchmarks

Phase 7 (Tier 2 Data)             ← depends on Phase 6
  Task 19: Web/research pipelines
  Task 20: AI-synthesized content

Phase 8 (Integration)             ← depends on all above
  Task 21: E2E test
  Task 22: RAG quality test
  Task 23: Plugin install test
  Task 24: Final commit + tag
```

**Parallelizable:** Phase 3 (Tasks 9-10) can run in parallel with Phase 2. Phase 6 can start as soon as Phase 2 is complete, running in parallel with Phases 4-5.

---

*Plan written: 2026-03-06*
*Total tasks: 24*
*Estimated phases: 8*
*Design doc: docs/plans/2026-03-06-susan-team-architect-design.md*
