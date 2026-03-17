# Job Studio Training Factory Data Program

**Date:** 2026-03-12  
**Owner:** Job Studio  
**Purpose:** Build the data, extraction, access, and refresh program behind the Job Studio Training Factory.

## Objective
Create a local-first, large-scale corpus program that supports strategist AI training, Ellen enablement, market and competitive intelligence training, behavioral-science grounding, and transcript-based evaluation.

## Current Base Corpus

### Local corpora already available
- Oracle Health market and competitive intelligence desktop mirror: `580 files`, `3.9 GB`
- `AI-Enablement-Oracle-Chat` local repo: `1.7 MB`
- `oracle-health-vendor-intelligence` local repo: `289 MB`
- `founder-intelligence-os` local repo: `12 MB`
- `ux-design-scraper` local repo: `4.6 MB`
- Susan local behavioral-science and training docs: available in `be_module`, training/editorial docs, agent and skill prompts

### Immediate size target
- Working local source base now: `4+ GB`
- Normalized extracted text target: `100+ MB`
- Training-specific normalized corpus target: `1+ GB`
- Full long-horizon acquisition target: `10+ GB` across local corpora, extracted corpora, live crawls, and evaluation data

### Current extraction checkpoint
- Normalized corpus generated so far: approximately `2.15 GB`
- Current extracted character count: `2,303,899,845`
- Normalized markdown files generated: `1,398`
- Documents extracted or cached in the completed run: `1,398`
- Current skipped documents: `93`
- Current visible extraction failures: `226`
- Current run status: local extraction is complete and the corpus is ready for targeted public-doc refresh waves

## Source Layers

### Layer 1: Local Oracle binary corpus
- Source: `/Users/mikerodgers/Desktop/OH Marketing and Competitive Intelligence`
- Role: foundational enterprise training, market intelligence, competitive intelligence, deck and memo examples, process artifacts
- Priority: highest

### Layer 2: Local repo harvest
- `AI-Enablement-Oracle-Chat`
- `oracle-health-vendor-intelligence`
- `founder-intelligence-os`
- `ux-design-scraper`
- Role: Ellen workflows, prompt systems, competitive intel, experience references, reusable skills and operating patterns

### Layer 3: Local Susan domain and behavioral-science corpus
- `susan-team-architect/backend/data/be_module`
- `susan-team-architect/backend/data/domains/transformfit_training_intelligence/editorial`
- `susan-team-architect/skills/behavioral-economics/SKILL.md`
- `susan-team-architect/agents/training-research-studio.md`
- Role: training psychology, behavior change, evaluation, instructional mechanisms, AI adoption resistance

### Layer 4: Live crawl layer
- Role: latest documentation, public best-practice training references, MCP ecosystem docs, official AI docs, official tool docs
- Tools: Firecrawl, Playwright, Jina, Git harvest, local extraction
- Constraint: external API keys are required before live crawl jobs can run end to end in this environment

## Required Tools and Their Jobs

| Tool | Job |
|---|---|
| Local file extraction | Convert Oracle binaries and local repos into normalized text |
| Firecrawl | Crawl docs sites, knowledge bases, and public reference surfaces |
| Playwright | Capture dynamic pages, JS-heavy sites, and UI-grounded evidence |
| Jina | Read canonical pages fast when crawl depth is not needed |
| Git harvest | Pull repo docs, prompts, code patterns, and examples from local or cloned repos |
| Supabase storage and pgvector | Store, index, and serve the harvested corpus to agents |

## Persona and Agent Access Protocol

1. Every routed Job Studio ask must attach the relevant context sources in the action packet.
2. Personal memory, training factory data, and linked company corpora must stay namespace-separated.
3. Training asks should attach all of:
   - `studio_memory`
   - `training_research`
   - `operational_protocols`
   - `market_research`
4. Ellen and the supporting team should work from named examples and verified source bundles, not only generic instructions.
5. Evaluation artifacts and transcript critiques should be written back into reusable corpus layers, not left as ephemeral outputs.

## Corpus Build Protocol

### Phase 1: Extract local corpora
- Run the Job Studio training corpus builder over the Oracle desktop mirror, local repos, and local Susan training/behavioral documents.
- Produce:
  - normalized markdown/text files
  - manifest and summary JSON
  - locator file
  - failure log by file type

### Phase 2: Create named example libraries
- Competitive briefs
- market intelligence packets
- strategy decks
- white papers and memos
- Ellen transcripts
- bad-vs-good prompt comparisons
- bad-vs-good facilitation and training examples

### Phase 3: Ingest for agent use
- Ingest normalized outputs into Susan data types for Job Studio and linked company contexts.
- Keep training, market, memory, and protocol layers separately queryable.

### Phase 4: Refresh live docs
- Run the new manifests across official docs and known public sources once keys are configured.
- Record freshness and coverage at every run.

## Non-Negotiable Completion Conditions
- Corpus size is measured, not guessed.
- Extraction failures are visible, not silent.
- Agents have an explicit data-access protocol.
- The training factory has its own locator and writeback path.
- Latest/live crawl remains part of the system design, but local data keeps the factory useful even when external keys are absent.
