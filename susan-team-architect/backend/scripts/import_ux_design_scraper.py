"""Absorb the external UX design scraper repo into Susan's shared studio intelligence.

This script does two jobs:
1. Import the reusable method, schema, and workflow knowledge from the
   standalone UX scraper repo into curated shared studio assets.
2. Optionally import generated export folders from UX scraper runs so Susan can
   retain the learnings without keeping them trapped in a separate product.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from supabase import create_client

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor
from rag_engine.retriever import Retriever
from susan_core.config import config
from susan_core.schemas import KnowledgeChunk


DEFAULT_REPO_ROOT = Path("/Users/mikerodgers/ux-design-scraper")
GENERATED_ROOT = BACKEND_ROOT / "data" / "studio_assets" / "generated" / "ux_design_scraper"
ARTIFACT_ROOT = BACKEND_ROOT / "artifacts" / "ux_design_scraper_import"
VISUAL_BUCKET = "susan-studio-assets"


@dataclass(frozen=True)
class GeneratedDoc:
    path: Path
    data_type: str
    content: str


REPO_FILES = {
    "pipeline": "src/background/scrape-orchestrator.ts",
    "workflow_constants": "src/shared/workflow-constants.ts",
    "knowledge_base": "src/shared/ux-knowledge-base.ts",
    "industry_data": "src/shared/industry-design-data.ts",
    "schema": "supabase/migrations/001_initial_schema.sql",
    "output_manager": "src/background/file-output-manager.ts",
    "critique_engine": "src/background/design-critique-engine.ts",
    "supabase_sync": "src/background/supabase-sync.ts",
    "tailwind_config": "tailwind.config.js",
    "sidepanel_app": "src/sidepanel/App.tsx",
    "sidepanel_styles": "src/sidepanel/styles.css",
}


def read_repo_file(repo_root: Path, relative_path: str) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8")


def parse_pipeline_steps(source: str) -> list[tuple[str, str]]:
    return re.findall(r"id:\s*'([^']+)'\s*,\s*name:\s*'([^']+)'", source)


def parse_table_names(sql: str) -> list[str]:
    return re.findall(r"CREATE TABLE\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.IGNORECASE)


def list_prompt_templates(repo_root: Path) -> list[str]:
    prompt_root = repo_root / "src" / "shared" / "prompt-templates"
    return sorted(path.name for path in prompt_root.glob("*.ts"))


def summarize_prompt_roles(repo_root: Path) -> list[str]:
    prompt_root = repo_root / "src" / "shared" / "prompt-templates"
    lines: list[str] = []
    for path in sorted(prompt_root.glob("*.ts")):
        content = path.read_text(encoding="utf-8")
        match = re.search(r"export const [A-Z0-9_]+_SYSTEM_PROMPT = `You are ([^`]+?)\\.", content)
        role = match.group(1).strip() if match else "a structured design specialist"
        lines.append(f"- `{path.name}` -> {role}")
    return lines


def infer_industry_modules(source: str) -> list[str]:
    return sorted(set(re.findall(r"^\\s{2}([a-zA-Z][a-zA-Z0-9_]*)\\s*:\\s*\\{", source, flags=re.MULTILINE)))


def parse_workflow_phases(source: str) -> list[tuple[str, str, str]]:
    return re.findall(
        r"([a-z]+):\s*\{\s*id:\s*'[^']+'\s*,\s*name:\s*'([^']+)'\s*,\s*description:\s*'([^']+)'",
        source,
        flags=re.MULTILINE,
    )


def parse_sidepanel_components(source: str) -> list[str]:
    return sorted(set(re.findall(r"import\s+\{\s*([A-Za-z0-9_]+)\s*\}\s+from\s+'\.\/components\/", source)))


def parse_tailwind_token_preview(source: str) -> list[str]:
    return re.findall(r"(brand|surface|dark):\s*\{([^}]+)\}", source, flags=re.DOTALL)


def parse_css_utility_classes(source: str) -> list[str]:
    return sorted(set(re.findall(r"\.([a-z0-9-]+)\s*\{", source)))


def build_docs(repo_root: Path) -> list[GeneratedDoc]:
    pipeline_source = read_repo_file(repo_root, REPO_FILES["pipeline"])
    workflow_source = read_repo_file(repo_root, REPO_FILES["workflow_constants"])
    knowledge_source = read_repo_file(repo_root, REPO_FILES["knowledge_base"])
    industry_source = read_repo_file(repo_root, REPO_FILES["industry_data"])
    schema_source = read_repo_file(repo_root, REPO_FILES["schema"])
    output_source = read_repo_file(repo_root, REPO_FILES["output_manager"])
    critique_source = read_repo_file(repo_root, REPO_FILES["critique_engine"])
    sync_source = read_repo_file(repo_root, REPO_FILES["supabase_sync"])
    tailwind_source = read_repo_file(repo_root, REPO_FILES["tailwind_config"])
    sidepanel_app_source = read_repo_file(repo_root, REPO_FILES["sidepanel_app"])
    sidepanel_styles_source = read_repo_file(repo_root, REPO_FILES["sidepanel_styles"])

    pipeline_steps = parse_pipeline_steps(pipeline_source)
    workflow_phases = parse_workflow_phases(workflow_source)
    table_names = parse_table_names(schema_source)
    prompt_files = list_prompt_templates(repo_root)
    prompt_roles = summarize_prompt_roles(repo_root)
    industries = infer_industry_modules(industry_source)
    sidepanel_components = parse_sidepanel_components(sidepanel_app_source)
    tailwind_blocks = parse_tailwind_token_preview(tailwind_source)
    css_utilities = parse_css_utility_classes(sidepanel_styles_source)

    system_doc = f"""# UX Design Scraper To Susan System

> Source repo: `{repo_root}`
> Purpose: absorb the standalone UX scraper's reusable knowledge into Susan's design and studio system instead of maintaining a separate intelligence repo.

## Keep vs discard

Keep:
- pipeline method
- UX doctrine and heuristics
- design-review and critique methodology
- export packaging conventions
- schema lessons from the original Supabase model

Discard as standalone source of truth:
- separate product-level Supabase schema
- duplicate knowledge base ownership
- extension-specific storage model as the long-term system

## What the UX scraper actually contributes

### 1. Capture pipeline
The scraper already broke the problem into reusable extraction waves. Those are valuable as studio methodology even if the extension UI eventually goes away.

Key pipeline steps ({len(pipeline_steps)} total):
{chr(10).join(f"- `{step_id}`: {step_name}" for step_id, step_name in pipeline_steps[:20])}
{"- `...` additional steps omitted for brevity" if len(pipeline_steps) > 20 else ""}

### 2. Embedded UX doctrine
`ux-knowledge-base.ts` packages:
- Nielsen heuristics
- WCAG criteria
- UI patterns
- component blueprints
- design-token guidance
- quality checks
- interaction principles

### 3. Design intelligence library
`industry-design-data.ts` packages:
- industry palettes
- typography pairings
- style definitions
- landing-page patterns
- reasoning rules

Sample industries represented ({len(industries)} inferred from exported palettes/config):
{chr(10).join(f"- `{name}`" for name in industries[:18])}
{"- `...` more industries exist in the source file" if len(industries) > 18 else ""}

### 4. Structured prompt workflow
The repo ships a strong design workflow instead of one-off prompts. Susan should retain the method, not the repo.

Prompt templates ({len(prompt_files)}):
{chr(10).join(f"- `{name}`" for name in prompt_files)}

Prompt roles:
{chr(10).join(prompt_roles[:14])}

## Susan-side mapping

| UX scraper layer | Susan destination |
|---|---|
| UX heuristics and design system doctrine | `studio_expertise` |
| Double Black Box workflow and prompt chain | `studio_templates` |
| Teardown / critique / output examples | `studio_case_library` |
| Lessons learned from the repo architecture | `studio_memory` |
| What not to replicate | `studio_antipatterns` |
| Schema and capture model | `ux_research` |
| Future exported screenshots | `visual_asset` |

## Recommended operating model

1. Keep the UX scraper repo as a tooling archive or browser-side extractor.
2. Promote all reusable learnings into Startup Intelligence OS.
3. Import exported runs into Susan instead of storing the intelligence in a parallel schema.
4. Route Marcus, Mira, Prism, Lens, Echo, Design Studio Director, and App Experience Studio through these imported assets.
"""

    case_library_doc = f"""# UX Design Scraper Case Library

> Source repo: `{repo_root}`
> This document captures the patterns from the UX scraper that are worth reusing in Susan's studios.

## Case 1: Topological scrape orchestration

Source:
- `{REPO_FILES["pipeline"]}`

Why it matters:
- the extension separates independent DOM extraction, dependent extraction, screenshots, external APIs, and enhanced MCP/API enrichment into waves
- this is a good precedent for Susan-side design intelligence jobs because it models dependencies explicitly instead of relying on one giant scrape

What Susan should keep:
- wave-based orchestration
- dependency-aware execution
- enhancement layers: Firecrawl, Exa, MCP, screenshots, motion capture

## Case 2: Output packaging into reusable artifacts

Source:
- `{REPO_FILES["output_manager"]}`

Reusable pattern:
- produce a design package rather than raw scrape results
- package includes `CLAUDE.md`, research insights, prompts, analysis docs, tokens, component artifacts, screenshots, accessibility, performance, and knowledge-base summaries

Susan-side implication:
- any future UX scraper export folder should be treated as a compound studio asset pack
- markdown should go into `studio_templates`, `studio_case_library`, and `ux_research`
- screenshots should go into `visual_asset`

## Case 3: Structured critique engine

Source:
- `{REPO_FILES["critique_engine"]}`

Reusable pattern:
- critique should cover visual hierarchy, whitespace, color harmony, typography, CTA effectiveness, mobile-first quality, emotional design, consistency, microinteractions, and innovation

Susan-side implication:
- use this as a design review rubric input for Marcus, Mira, Prism, and Design Studio Director

## Case 4: Schema lessons from the original Supabase model

Source:
- `{REPO_FILES["schema"]}`

Tables already modeled there:
{chr(10).join(f"- `{name}`" for name in table_names)}

Susan-side implication:
- keep the entity ideas, not the duplicate database
- merge them into Susan's foundry via `ux_research`, `studio_memory`, `studio_templates`, and `visual_asset`
"""

    antipattern_doc = f"""# UX Design Scraper Anti-Pattern Dataset

> Source repo: `{repo_root}`

## Anti-pattern 1: Parallel source-of-truth database

Signal:
- a second Supabase schema is used to store design intelligence separately from Susan

Why it is bad:
- duplicate retrieval systems
- drift between repos
- the design team learns things that Susan cannot naturally route

Rescue move:
- treat the UX scraper repo as an ingestion/source tool
- keep Susan's backend as the intelligence system of record

## Anti-pattern 2: Repo-bound knowledge instead of shared studio memory

Signal:
- heuristics, prompt methodology, and design patterns only exist in extension source files

Why it is bad:
- studio agents cannot retrieve them directly
- the methodology disappears from company work unless someone remembers it manually

Rescue move:
- normalize those learnings into `studio_expertise`, `studio_templates`, and `studio_memory`

## Anti-pattern 3: Tool-specific schema over reusable ontology

Signal:
- tables were designed around scrape sessions and extension outputs, not long-lived foundry knowledge

Why it is bad:
- hard to share across TransformFit, Alex Recruiting, Oracle Health, and founder work
- makes cross-company design memory harder

Rescue move:
- preserve the concepts: screenshots, flow analysis, competitor analysis, components, tokens
- map them into Susan's existing knowledge and asset model

## Anti-pattern 4: Raw extraction without studio curation

Signal:
- raw design tokens, HTML, CSS, and screenshots are stored, but not consistently turned into precedent, lessons, anti-patterns, or operating doctrine

Rescue move:
- every UX scraper import should yield:
  - a case library entry
  - a template or workflow artifact
  - a memory note
  - optional visual assets
"""

    memory_doc = f"""# UX Design Scraper Memory Seed

> Imported from `{repo_root}`

## What we learned

- The UX scraper proved that design intelligence is best captured as a pipeline, not a single scrape.
- The strongest reusable parts are not the browser extension UI; they are the structured method, critique framing, and export packaging.
- The original schema was good at session capture but not ideal as Susan's long-term system of record.
- The Double Black Box prompt chain is valuable and should be reused by Susan's design studios rather than left in an isolated repo.

## What Susan should remember

- Preserve the wave-based architecture for future design intelligence collectors.
- Preserve the critique dimensions for design reviews and red-team passes.
- Preserve the export bundle shape because it turns design analysis into reusable assets.
- Do not preserve a separate product database as the intelligence source of truth.

## Next experiments

1. Import real output folders from UX scraper runs into TransformFit visual and UX research corpora.
2. Attach screenshot imports to `visual_asset` and use them in design and workout-session teardowns.
3. Translate the Double Black Box phases into Susan-native design protocols.
4. Promote the strongest captured patterns into studio templates and anti-pattern rubrics.
"""

    templates_doc = f"""# UX Design Scraper Double Black Box Templates

> Source repo: `{repo_root}`

This is the part Susan should keep: the structured design workflow, not the separate repo.

## Workflow phases extracted from prompt templates

{chr(10).join(f"- `{name}`" for name in prompt_files)}

## Susan-native adaptation

### Discover
- synthesize raw research
- define target users, jobs to be done, moments of truth, and competitive patterns

### Define
- turn research into design principles, accessibility requirements, and journey maps

### Diverge
- create multiple distinct directions rather than iterating one obvious answer

### Gate
- explicitly approve or reject the research basis before downstream design work

### Develop
- turn the winning direction into design systems, tokens, flows, and implementation rules

### Deliver
- produce the implementation package that engineering or Claude can execute

### Measure
- define instrumentation, experiments, and learning loops

## Reuse rule

When Marcus or the design studios need deeper structure, Susan should pull this workflow instead of defaulting to a loose design brainstorm.
"""

    ux_research_doc = f"""# UX Design Scraper Schema And Import Model

> Source repo: `{repo_root}`
> Source schema: `{REPO_FILES["schema"]}`

## Original tables

{chr(10).join(f"- `{name}`" for name in table_names)}

## What those tables mean in Susan

| Original table | Susan-side meaning |
|---|---|
| `projects` | scrape session / imported design analysis package |
| `design_tokens` | structured design token evidence |
| `components` | component precedent and implementation reference |
| `screenshots` | visual assets |
| `heatmaps` | experience evidence / behavior signal |
| `knowledge_base` | studio knowledge and prompt artifacts |
| `competitor_analysis` | case library / competitive design intelligence |
| `flow_analysis` | UX research / journey and friction analysis |
| `design_versions` | precedent history / visual evolution |

## Import protocol

### Repo knowledge import
- normalize source methodology into curated shared markdown docs
- ingest them into:
  - `studio_expertise`
  - `studio_case_library`
  - `studio_antipatterns`
  - `studio_memory`
  - `studio_templates`
  - `ux_research`

### Export folder import
- markdown analysis files -> `ux_research` or `studio_templates`
- `CLAUDE.md` and prompt packs -> `studio_templates`
- research summaries and teardowns -> `studio_case_library`
- screenshots -> `visual_asset`
- JSON artifacts -> summarized `ux_research`

## Why this is better than keeping a separate repo

- Susan can route and retrieve the intelligence natively
- TransformFit, Alex Recruiting, Oracle Health, and founder work all benefit from the same memory
- the extension becomes a tool, not a second intelligence platform
"""

    gold_standard_doc = f"""# UX Scraper Gold Standard Reference

> Source repo: `{repo_root}`
> Position: this repo is the gold-standard reference for Susan's design studios because it encodes a full-stack design workflow, a quality critique model, exportable implementation artifacts, and a disciplined operator UI.

## What makes it the standard

- it does not stop at inspiration; it turns analysis into deliverables
- it packages design work into reusable artifacts rather than loose notes
- it has a real operator interface, not just prompt text
- it blends research, critique, reconstruction, design system work, and handoff

## Gold-standard layers Susan should inherit

### 1. Workflow operating system
The workflow is not a generic brainstorm. It is an explicit sequence of research, definition, checkpointing, divergence, build, handoff, and measurement.

### 2. Operator shell quality
The sidepanel app demonstrates a compact operator shell:
- left navigation with badges
- dense but readable dark surfaces
- streaming/chat patterns
- progress and preview panels
- compare/critique/persona/results tabs
- workflow and batch queue views

### 3. Design-system discipline
The repo has a normalized token language:
{chr(10).join(f"- `{name}` palette block with structured token steps" for name, _ in tailwind_blocks)}

Typography:
- `Inter` for primary sans UI
- `JetBrains Mono` for system and technical detail

Useful CSS utilities:
{chr(10).join(f"- `{name}`" for name in css_utilities[:16])}

### 4. Deliverable completeness
The output package expects:
- tokens
- screenshots
- analysis docs
- prompt packs
- CLAUDE execution files
- Storybook artifacts
- prototype output
- performance and accessibility guidance

## Adoption rule

When Mike says the UX scraper is the gold standard, Susan should interpret that as:
1. use its workflow structure
2. use its critique and deliverable rigor
3. use its operator-shell clarity and compactness
4. do not blindly copy the browser-extension UI into product surfaces
5. translate the standard into company-specific UX, especially TransformFit
"""

    workflow_os_doc = f"""# UX Scraper Workflow Operating System

> Source repo: `{repo_root}`
> Source file: `{REPO_FILES["workflow_constants"]}`

## Canonical phases

{chr(10).join(f"- `{phase_id}` / `{name}` -> {description}" for phase_id, name, description in workflow_phases)}

## Why this matters for Susan

This is the clearest reusable design workflow currently in your system:
- Discover gathers evidence
- Define converts evidence into principles and requirements
- Gate forces review before more expensive design work
- Diverge creates multiple routes instead of locking onto the first idea
- Develop turns a direction into a buildable system
- Deliver packages the work for execution
- Measure closes the loop with post-ship learning

## Susan-native translation

- `susan-fast` should use a compressed Discover + Define + Deliver path
- `susan-design` should use the full workflow with Gate and Diverge
- `susan-foundry` should capture Deliver + Measure outputs into foundry memory

## TransformFit implication

TransformFit UI/UX work should stop skipping from concept to code. The minimum standard becomes:
1. discover the workout context and moments of truth
2. define gym-state constraints, emotional goals, and a11y rules
3. gate the experience direction
4. diverge on session, onboarding, and dashboard concepts
5. develop with tokens, component rules, and coaching behaviors
6. deliver engineering-ready specs and prompts
7. measure adherence, friction, trust, and session completion
"""

    sidepanel_ui_doc = f"""# UX Scraper Sidepanel UI System

> Source repo: `{repo_root}`
> Source files:
> - `{REPO_FILES["sidepanel_app"]}`
> - `{REPO_FILES["sidepanel_styles"]}`
> - `{REPO_FILES["tailwind_config"]}`

## Core shell

The sidepanel is a compact operator interface with:
- persistent sidebar navigation
- badge-based information scent
- compact header with live run state
- a single main content frame that swaps tools without losing shell stability

## Imported component patterns

Primary components discovered from the app shell:
{chr(10).join(f"- `{name}`" for name in sidepanel_components)}

## Reusable interaction patterns

- streaming status indicator instead of blocking spinners
- glass-card surfaces for dense operator contexts
- shimmer loading for data-heavy panels
- badge counts for queue/workflow awareness
- compact typography and dense spacing without collapsing readability

## Reuse rule for company apps

Use this shell as precedent for:
- design/research studios
- founder operator consoles
- internal dashboards
- QA, workflow, and review panels

Do not copy it literally for:
- consumer landing pages
- active workout screens
- emotionally warm coaching moments

For TransformFit specifically:
- borrow the operator clarity for internal studio tools and coach/admin views
- borrow the streaming/chat/container patterns for coach threads
- do not turn the consumer workout session into an extension-style dashboard
"""

    return [
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_TO_SUSAN_SYSTEM.md", "studio_expertise", system_doc),
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_GOLD_STANDARD_REFERENCE.md", "studio_expertise", gold_standard_doc),
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_WORKFLOW_OPERATING_SYSTEM.md", "studio_templates", workflow_os_doc),
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_SIDEPANEL_UI_SYSTEM.md", "studio_case_library", sidepanel_ui_doc),
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_CASE_LIBRARY.md", "studio_case_library", case_library_doc),
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_ANTIPATTERNS.md", "studio_antipatterns", antipattern_doc),
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_MEMORY_SEED.md", "studio_memory", memory_doc),
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_DOUBLE_BLACK_BOX_TEMPLATES.md", "studio_templates", templates_doc),
        GeneratedDoc(GENERATED_ROOT / "UX_SCRAPER_SCHEMA_AND_IMPORT_MODEL.md", "ux_research", ux_research_doc),
    ]


def write_docs(docs: list[GeneratedDoc]) -> None:
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    for doc in docs:
        doc.path.write_text(doc.content, encoding="utf-8")


def ingest_docs(docs: list[GeneratedDoc], company_id: str = "shared") -> int:
    ingestor = MarkdownIngestor()
    stored = 0
    for doc in docs:
        stored += ingestor.ingest(str(doc.path), company_id=company_id, data_type=doc.data_type)
    return stored


def ensure_bucket(supabase) -> None:
    buckets = supabase.storage.list_buckets()
    names = {b.name if hasattr(b, "name") else b.get("name") for b in buckets}
    if VISUAL_BUCKET not in names:
        supabase.storage.create_bucket(
            VISUAL_BUCKET,
            name=VISUAL_BUCKET,
            options={"public": True, "file_size_limit": 10 * 1024 * 1024},
        )


def upload_bytes(supabase, path: str, payload: bytes, content_type: str) -> str:
    bucket = supabase.storage.from_(VISUAL_BUCKET)
    if bucket.exists(path):
        bucket.remove([path])
    bucket.upload(path, payload, {"content-type": content_type})
    public = bucket.get_public_url(path)
    return public if isinstance(public, str) else public.get("publicUrl") or public.get("public_url")


def classify_markdown_export(path: Path) -> str:
    rel = path.as_posix().lower()
    if rel.endswith("/claude.md") or "/prompts/" in rel:
        return "studio_templates"
    if rel.endswith("/readme.md") or rel.endswith("/knowledge-base.md"):
        return "studio_case_library"
    return "ux_research"


def json_summary_chunk(path: Path, company_id: str, export_name: str) -> KnowledgeChunk:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {"raw_excerpt": path.read_text(encoding="utf-8", errors="ignore")[:3000]}

    summary_bits: list[str] = []
    if isinstance(data, dict):
        summary_bits.append(f"Top-level keys: {', '.join(sorted(data.keys())[:25])}")
        sample = json.dumps(data, indent=2)[:3000]
    elif isinstance(data, list):
        summary_bits.append(f"Array length: {len(data)}")
        sample = json.dumps(data[:3], indent=2)[:3000]
    else:
        sample = str(data)[:3000]

    content = (
        f"Imported UX scraper JSON artifact from export `{export_name}`.\n"
        f"Artifact: {path.name}\n"
        f"Relative path: {path}\n"
        f"{' '.join(summary_bits)}\n"
        f"Sample:\n{sample}"
    )
    return KnowledgeChunk(
        content=content,
        company_id=company_id,
        access_level="company" if company_id != "shared" else "public",
        data_type="ux_research",
        source="ux_design_scraper_export",
        source_url=str(path),
        metadata={
            "import_kind": "json_artifact",
            "export_name": export_name,
            "file_name": path.name,
        },
    )


def screenshot_chunk(
    *,
    company_id: str,
    export_name: str,
    title: str,
    local_path: Path,
    public_url: str,
    storage_path: str,
) -> KnowledgeChunk:
    content = (
        f"Imported UX scraper screenshot asset.\n"
        f"Export: {export_name}\n"
        f"Title: {title}\n"
        f"Local path: {local_path}\n"
        f"Storage URL: {public_url}"
    )
    return KnowledgeChunk(
        content=content,
        company_id=company_id,
        access_level="company" if company_id != "shared" else "public",
        data_type="visual_asset",
        source="ux_design_scraper_export",
        source_url=str(local_path),
        metadata={
            "asset_type": "screenshot",
            "export_name": export_name,
            "title": title,
            "storage_bucket": VISUAL_BUCKET,
            "storage_path": storage_path,
            "public_url": public_url,
        },
    )


def import_export_folder(exports_root: Path, company_id: str) -> dict[str, int]:
    if not exports_root.exists():
        raise FileNotFoundError(f"Exports root not found: {exports_root}")

    ingestor = MarkdownIngestor()
    retriever = Retriever()
    supabase = create_client(config.supabase_url, config.supabase_key)
    ensure_bucket(supabase)

    totals: dict[str, int] = {
        "markdown": 0,
        "json": 0,
        "screenshots": 0,
    }
    json_chunks: list[KnowledgeChunk] = []
    image_chunks: list[KnowledgeChunk] = []

    export_dirs = sorted(
        path for path in exports_root.iterdir()
        if path.is_dir() and ((path / "CLAUDE.md").exists() or (path / "README.md").exists())
    )

    for export_dir in export_dirs:
        export_name = export_dir.name
        for md in export_dir.rglob("*.md"):
            data_type = classify_markdown_export(md.relative_to(export_dir))
            totals["markdown"] += ingestor.ingest(str(md), company_id=company_id, data_type=data_type)

        for artifact in export_dir.rglob("*.json"):
            json_chunks.append(json_summary_chunk(artifact, company_id=company_id, export_name=export_name))

        for image in export_dir.rglob("*.png"):
            raw = image.read_bytes()
            digest = hashlib.sha256(str(image).encode("utf-8")).hexdigest()[:12]
            filename = f"{export_name}-{image.stem}-{digest}.png"
            storage_path = f"{company_id}/ux-design-scraper/{filename}"
            content_type = mimetypes.guess_type(filename)[0] or "image/png"
            public_url = upload_bytes(supabase, storage_path, raw, content_type)
            image_chunks.append(
                screenshot_chunk(
                    company_id=company_id,
                    export_name=export_name,
                    title=image.stem,
                    local_path=image,
                    public_url=public_url,
                    storage_path=storage_path,
                )
            )

    if json_chunks:
        totals["json"] = retriever.store_chunks(json_chunks)
    if image_chunks:
        totals["screenshots"] = retriever.store_chunks(image_chunks)
    return totals


def build_report(*, repo_root: Path, docs: list[GeneratedDoc], repo_stored: int, export_totals: dict[str, int] | None) -> dict:
    return {
        "repo_root": str(repo_root),
        "generated_root": str(GENERATED_ROOT),
        "generated_docs": [
            {"path": str(doc.path), "data_type": doc.data_type}
            for doc in docs
        ],
        "repo_chunks_stored": repo_stored,
        "export_import": export_totals or {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--company-id", default="shared")
    parser.add_argument("--exports-root", type=Path, default=None)
    args = parser.parse_args()

    docs = build_docs(args.repo_root)
    write_docs(docs)
    repo_stored = ingest_docs(docs, company_id="shared")

    export_totals: dict[str, int] | None = None
    if args.exports_root:
        export_totals = import_export_folder(args.exports_root, company_id=args.company_id)

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    report = build_report(
        repo_root=args.repo_root,
        docs=docs,
        repo_stored=repo_stored,
        export_totals=export_totals,
    )
    (ARTIFACT_ROOT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
