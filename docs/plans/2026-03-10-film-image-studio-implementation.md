# AI Film & Image Studio — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Hollywood-grade AI film and image production studio with 18 agents, 3 generation engine sub-studios, 10 MCP tools, 11 RAG scrape manifests, and a 4-phase production workflow — all at V5 maturity.

**Architecture:** Three-layer system: Layer 1 (15 creative direction agents), Layer 2 (3 generation engine sub-studios with tool routing), Layer 3 (4-phase production process). Multi-tenant across founder-intelligence-os, transformfit, oracle-health-ai, and external clients. AI-generation-first.

**Tech Stack:** Susan agent YAML (markdown frontmatter), Python MCP server (FastMCP), Supabase/pgvector RAG, Exa semantic search for scraping, Voyage AI embeddings.

**Design doc:** `docs/plans/2026-03-10-film-image-studio-design.md`

---

## Task 1: Capability Record

**Files:**
- Create: `.startup-os/capabilities/film-image-studio.yaml`

**Step 1: Write the capability record**

```yaml
id: film-image-studio
name: Film & Image Studio
maturity_current: 0
maturity_target: 5
wave: 1
owner_human: Mike Rodgers
owner_agent: Susan
gaps:
  - all 18 studio agents
  - generation engine sub-studios
  - film production RAG knowledge
  - MCP studio tools
  - production workflow engine
levels:
  1:
    name: Nascent
    items:
      - text: "Capability identified and scoped"
        done: true
      - text: "Design document approved"
        done: true
      - text: "Agent roster defined (18 agents)"
        done: false
      - text: "RAG data types registered"
        done: false
  2:
    name: Emerging
    items:
      - text: "All 15 creative direction agents operational"
        done: false
      - text: "All 3 generation engine sub-studios operational"
        done: false
      - text: "Agent registry updated with film studio agents"
        done: false
      - text: "RAG knowledge base populated (5,100+ chunks)"
        done: false
  3:
    name: Scaling
    items:
      - text: "10 MCP tools added to server.py"
        done: false
      - text: "Production engine manages lifecycle (start, status, review)"
        done: false
      - text: "Design session workflow operational"
        done: false
      - text: "Storyboard generation workflow operational"
        done: false
  4:
    name: Optimizing
    items:
      - text: "Full film production workflow tested end-to-end"
        done: false
      - text: "Instagram batch production workflow tested"
        done: false
      - text: "Multi-tenant production across 3+ companies"
        done: false
      - text: "Quality gates automated for all engines"
        done: false
  5:
    name: Hollywood-Grade Autonomous
    items:
      - text: "AI-directed multi-agent productions"
        done: false
      - text: "All tool routing logic validated"
        done: false
      - text: "Legal clearance workflow for every production"
        done: false
      - text: "External client capacity proven"
        done: false
```

**Step 2: Commit**

```bash
git add .startup-os/capabilities/film-image-studio.yaml
git commit -m "feat: add film-image-studio capability record (V5 target)"
```

---

## Task 2: Creative Direction Agents — Batch 1 (Leadership + Visual)

**Files:**
- Create: `susan-team-architect/agents/film-studio-director.md`
- Create: `susan-team-architect/agents/screenwriter-studio.md`
- Create: `susan-team-architect/agents/cinematography-studio.md`
- Create: `susan-team-architect/agents/production-designer-studio.md`
- Create: `susan-team-architect/agents/photography-studio.md`

**Step 1: Write film-studio-director.md**

Follow the exact pattern from `highlight-reel-studio.md`: YAML frontmatter (name, description, model) then markdown body with Identity, Role, Cognitive Architecture, Doctrine, Frameworks, Reasoning Modes, etc.

```markdown
---
name: film-studio-director
description: Film production orchestrator — assembles multi-agent teams, manages production lifecycle, enforces quality gates
model: claude-sonnet-4-6
---

You are the Film Studio Director, the executive producer and creative orchestrator for the AI Film & Image Studio.

## Identity
You run productions. You break briefs into production plans, assemble the right agent team, sequence phases, review quality, and deliver finished assets. You are the studio head — not a specialist, but the conductor who knows what every specialist does and when to call them.

## Your Role
- Intake production briefs from operators
- Assess scope (format, duration, complexity, budget)
- Assemble agent teams based on production needs
- Sequence production phases (Design Session → Storyboard → Concept Gen → Refinement)
- Route generation tasks to the correct engine (Image, Film, Audio)
- Run quality gate reviews at each phase
- Manage multi-tenant productions across companies

## Cognitive Architecture
- Start with the operator's intent, not production complexity
- Break every brief into: purpose, audience, tone, format, delivery specs
- Assemble the minimum viable team — don't over-staff productions
- Sequence for speed: parallelize where possible, serialize where dependencies exist
- Every production passes through Legal & Rights before delivery
- Save production patterns that work into memory for reuse

## Doctrine
- A production without a clear brief is a production that will fail.
- Quality gates exist to prevent garbage from shipping, not to slow things down.
- The right tool for each shot matters more than using the most expensive tool for every shot.
- Multi-tenant means brand isolation — never cross-contaminate company assets.

## Canonical Frameworks
- Brief → Scope → Team → Sequence → Generate → Review → Deliver
- Production types: film, reel, photo, series, carousel, brand-film, documentary
- Quality gate system: physics, character consistency, motion, audio sync, brand, legal

## Reasoning Modes
- production intake mode
- team assembly mode
- phase sequencing mode
- quality review mode
- delivery packaging mode

## Collaboration Triggers
- Script/narrative needed → screenwriter-studio
- Visual language needed → cinematography-studio
- Environments/worlds needed → production-designer-studio
- Stills/photos needed → photography-studio
- Editing/assembly needed → editing-studio
- Color work needed → color-grade-studio
- Sound work needed → sound-design-studio
- Music needed → music-score-studio
- VFX needed → vfx-studio
- Voices/cast needed → talent-cast-studio
- Budget/schedule needed → production-manager-studio
- Legal clearance needed → legal-rights-studio
- Distribution packaging → distribution-studio
- Social optimization → instagram-studio
- Image generation → image-gen-engine
- Video generation → film-gen-engine
- Audio generation → audio-gen-engine
```

**Step 2: Write screenwriter-studio.md**

Key sections: Identity (narrative craftsperson), Cognitive Architecture (premise → character → structure → scene → dialogue → revision), Frameworks (Save the Cat, Story Grid, McKee, Sequence approach), Reasoning Modes (feature screenplay, short film, reel script, brand narrative, treatment, dialogue polish). Include shot-by-shot description output format for storyboarding.

**Step 3: Write cinematography-studio.md**

Key sections: Identity (visual language architect), Cognitive Architecture (narrative intent → visual concept → shot design → lighting → color science), Knowledge domains (ARRI/RED/Sony/Blackmagic, ACES, Rec.709/DCI-P3/Rec.2020, ASC CDL, lens science), Frameworks (3-point lighting, exposure triangle, color temperature, depth of field control, camera movement vocabulary — dolly, crane, Steadicam, handheld, drone, locked-off), AI tool guidance (Midjourney for reference frames, Runway/Sora for pre-viz, Flux for stills).

**Step 4: Write production-designer-studio.md**

Key sections: Identity (visual world builder), Cognitive Architecture (script analysis → research → concept art → environment design → prop/wardrobe direction), AI tool guidance (Midjourney for concept art, DALL-E for iteration, SD for consistent style, Sora/Runway for environment generation).

**Step 5: Write photography-studio.md**

Key sections: Identity (still image production lead), Cognitive Architecture (brief → concept/mood → shot list → production → culling → retouching → delivery), Standards (Capture One tethering, Lightroom, frequency separation, on-white e-commerce), AI tool guidance (Midjourney for reference, Claid for product backgrounds, AfterShoot for culling, Topaz Photo AI for enhancement).

**Step 6: Commit**

```bash
git add susan-team-architect/agents/film-studio-director.md \
        susan-team-architect/agents/screenwriter-studio.md \
        susan-team-architect/agents/cinematography-studio.md \
        susan-team-architect/agents/production-designer-studio.md \
        susan-team-architect/agents/photography-studio.md
git commit -m "feat: add 5 creative direction agents — director, screenwriter, cinematography, prod design, photo"
```

---

## Task 3: Creative Direction Agents — Batch 2 (Post-Production)

**Files:**
- Create: `susan-team-architect/agents/editing-studio.md`
- Create: `susan-team-architect/agents/color-grade-studio.md`
- Create: `susan-team-architect/agents/sound-design-studio.md`
- Create: `susan-team-architect/agents/music-score-studio.md`
- Create: `susan-team-architect/agents/vfx-studio.md`

**Step 1: Write all 5 agent files**

Each follows the same YAML frontmatter + markdown pattern. Key details per agent:

- **editing-studio**: Murch's 6 priorities (emotion, story, rhythm, eye-trace, 2D plane, 3D space), Eisenstein montage theory, NLE knowledge (Premiere, DaVinci, Avid), Reel-specific rules (1.7s hook, 30-90s optimal)
- **color-grade-studio**: ACES AP0/AP1, Rec.709, DCI-P3, Rec.2020 PQ, Dolby Vision, primary/secondary/shot-matching/creative-look/output-transform pipeline, AI tools (Colourlab.ai, DaVinci Neural Engine)
- **sound-design-studio**: Spotting → sound map → layers (dialogue, SFX, ambience, Foley) → pre-mix → final mix, standards (24-bit/48kHz, Dolby Atmos, 5.1/7.1, Netflix audio specs), AI tools (iZotope RX, Adobe Podcast, ElevenLabs)
- **music-score-studio**: Music spotting → emotional mapping → genre/palette → composition → mixing → clearance, AI tools (AIVA full copyright, ElevenLabs Music cleared, Suno/Udio for drafts), sync+master license knowledge
- **vfx-studio**: VFX breakdown → shot classification → pipeline selection → execution → comp, AI tools (Autodesk Flow for CG characters, Runway for roto/inpainting, Topaz for upscaling, After Effects Firefly)

**Step 2: Commit**

```bash
git add susan-team-architect/agents/editing-studio.md \
        susan-team-architect/agents/color-grade-studio.md \
        susan-team-architect/agents/sound-design-studio.md \
        susan-team-architect/agents/music-score-studio.md \
        susan-team-architect/agents/vfx-studio.md
git commit -m "feat: add 5 post-production agents — editing, color, sound, music, vfx"
```

---

## Task 4: Creative Direction Agents — Batch 3 (Management + Distribution)

**Files:**
- Create: `susan-team-architect/agents/production-manager-studio.md`
- Create: `susan-team-architect/agents/talent-cast-studio.md`
- Create: `susan-team-architect/agents/legal-rights-studio.md`
- Create: `susan-team-architect/agents/distribution-studio.md`
- Create: `susan-team-architect/agents/instagram-studio.md`

**Step 1: Write all 5 agent files**

Key details:

- **production-manager-studio**: Brief → script breakdown → schedule → budget → resource plan → daily tracking → wrap report. Outputs: production schedules, budgets, shot lists, call sheets.
- **talent-cast-studio**: Character analysis → voice profile → casting brief → audition eval → direction notes. AI tools: ElevenLabs voice cloning (consent protocol), voice direction.
- **legal-rights-studio**: Production audit → rights inventory → clearance checklist → consent → compliance. Knowledge: SAG-AFTRA digital replica, WGA AI, IATSE, US Copyright Office, music licensing. Critical: every production must pass legal before distribution.
- **distribution-studio**: Content assessment → strategy → specs → submissions → marketing. Standards: Netflix/Apple specs, DCP, festival requirements. AI tools: ElevenLabs dubbing, thumbnail A/B.
- **instagram-studio**: Content pillar mapping → monthly calendar → batch sprint → hook optimization → schedule → analytics. Standards: 1080x1920, H.264/H.265, 1.7s hook, 30-90s optimal, 3-5 Reels/week. AI tools: CapCut, Runway/Kling B-roll, Suno music, ElevenLabs voiceover.

**Step 2: Commit**

```bash
git add susan-team-architect/agents/production-manager-studio.md \
        susan-team-architect/agents/talent-cast-studio.md \
        susan-team-architect/agents/legal-rights-studio.md \
        susan-team-architect/agents/distribution-studio.md \
        susan-team-architect/agents/instagram-studio.md
git commit -m "feat: add 5 management/distribution agents — prod mgr, talent, legal, distribution, instagram"
```

---

## Task 5: Generation Engine Sub-Studios

**Files:**
- Create: `susan-team-architect/agents/image-gen-engine.md`
- Create: `susan-team-architect/agents/film-gen-engine.md`
- Create: `susan-team-architect/agents/audio-gen-engine.md`

**Step 1: Write image-gen-engine.md**

This agent is a tool router. Its system prompt must contain the FULL tool capability map (all tiers), the routing logic decision tree, and the quality gates. It is the most knowledge-dense agent — it must know every image generation tool's strengths, limitations, pricing, API availability, and optimal use case. Include the complete routing logic from the design doc.

**Step 2: Write film-gen-engine.md**

Same pattern — FULL tool map for all video generation tools (Sora 2, Veo 3.1, Seedance 2.0, Runway Gen-4.5, Kling 3.0, Luma Ray 3.14, Pika, Hailuo, LTX-2, Higgsfield, Moonvalley, Synthesia, HeyGen, D-ID, Autodesk Flow, Topaz Video AI, OpusClip, Descript, CapCut). Full routing logic. Full quality gates.

**Step 3: Write audio-gen-engine.md**

Same pattern — FULL tool map for voice (ElevenLabs, PlayHT, Cartesia, Fish Audio, Resemble), music (AIVA, ElevenLabs Music, Suno, Udio, Stable Audio, Soundraw), SFX (ElevenLabs SFX), repair (iZotope RX, Adobe Podcast, LALAL, Moises, Krisp). Full routing logic including copyright ownership status per tool.

**Step 4: Commit**

```bash
git add susan-team-architect/agents/image-gen-engine.md \
        susan-team-architect/agents/film-gen-engine.md \
        susan-team-architect/agents/audio-gen-engine.md
git commit -m "feat: add 3 generation engine sub-studios — image, film, audio with tool routing"
```

---

## Task 6: Agent Registry Update

**Files:**
- Modify: `susan-team-architect/backend/data/agent_registry.yaml`

**Step 1: Add all 18 new agents to the registry**

Append to the `agents:` section. Each entry needs: name, role, model, rag_data_types, group, expertise_types.

Group all under `group: "film_studio"`. Use `model: "claude-sonnet-4-6"` for all.

RAG data types per agent:
- film-studio-director: `["film_production", "cinematography", "post_production", "screenwriting"]`
- screenwriter-studio: `["screenwriting", "film_production"]`
- cinematography-studio: `["cinematography", "film_production", "ai_video_tools", "ai_image_tools"]`
- production-designer-studio: `["cinematography", "ai_image_tools", "film_production"]`
- photography-studio: `["photography", "ai_image_tools"]`
- editing-studio: `["post_production", "film_production", "instagram_production"]`
- color-grade-studio: `["post_production", "cinematography"]`
- sound-design-studio: `["post_production", "ai_audio_tools"]`
- music-score-studio: `["ai_audio_tools", "film_legal"]`
- vfx-studio: `["post_production", "ai_video_tools"]`
- production-manager-studio: `["film_production"]`
- talent-cast-studio: `["ai_audio_tools", "film_production"]`
- legal-rights-studio: `["film_legal"]`
- distribution-studio: `["film_production", "instagram_production"]`
- instagram-studio: `["instagram_production", "ai_video_tools", "ai_image_tools", "ai_audio_tools"]`
- image-gen-engine: `["ai_image_tools", "photography"]`
- film-gen-engine: `["ai_video_tools", "cinematography"]`
- audio-gen-engine: `["ai_audio_tools"]`

**Step 2: Commit**

```bash
git add susan-team-architect/backend/data/agent_registry.yaml
git commit -m "feat: register 18 film studio agents in agent_registry.yaml"
```

---

## Task 7: RAG Scrape Manifests — Batch 1 (Film Craft)

**Files:**
- Create: `susan-team-architect/backend/data/scrape_manifests/film_production.yaml`
- Create: `susan-team-architect/backend/data/scrape_manifests/cinematography.yaml`
- Create: `susan-team-architect/backend/data/scrape_manifests/post_production.yaml`
- Create: `susan-team-architect/backend/data/scrape_manifests/screenwriting.yaml`

**Step 1: Write film_production.yaml**

Follow the exact pattern from `exercise_science.yaml`. Use `tool: exa` with semantic queries and `tool: firecrawl` for specific URLs.

```yaml
manifest:
  name: "Film Production Core"
  company: shared
  data_type: film_production
  priority: high
  description: "Production management, crew workflows, scheduling, budgeting, set operations"

sources:
  - tool: exa
    query: "film production management scheduling budgeting crew workflow"
    num_results: 10

  - tool: exa
    query: "script breakdown production schedule shot list call sheet creation"
    num_results: 10

  - tool: exa
    query: "indie film production workflow pre-production checklist"
    num_results: 10

  - tool: exa
    query: "film crew hierarchy roles responsibilities department structure"
    num_results: 10

  - tool: exa
    query: "production design set decoration props art department workflow"
    num_results: 8

  - tool: firecrawl
    url: "https://www.studiobinder.com/blog/film-production-process/"

  - tool: firecrawl
    url: "https://nofilmschool.com/film-production"

  - tool: exa
    query: "location scouting permits film production logistics"
    num_results: 8

  - tool: exa
    query: "on-set protocol first AD director workflow production day"
    num_results: 8
```

**Step 2: Write cinematography.yaml, post_production.yaml, screenwriting.yaml**

Same pattern. Key exa queries:
- cinematography: "cinematography shot composition framing rules", "lighting design three-point key fill back", "camera movement dolly crane steadicam meaning", "ACES color management workflow", "lens selection focal length depth of field cinematic"
- post_production: "film editing workflow assembly rough cut fine cut picture lock", "color grading DaVinci Resolve primary secondary", "sound design foley SFX mixing workflow", "VFX compositing pipeline rotoscoping", "Dolby Atmos mixing spatial audio film"
- screenwriting: "screenplay structure three act five act", "scene construction objective obstacle tactics", "dialogue writing subtext economy craft", "screenplay format industry standard", "story structure save the cat beat sheet"

**Step 3: Commit**

```bash
git add susan-team-architect/backend/data/scrape_manifests/film_production.yaml \
        susan-team-architect/backend/data/scrape_manifests/cinematography.yaml \
        susan-team-architect/backend/data/scrape_manifests/post_production.yaml \
        susan-team-architect/backend/data/scrape_manifests/screenwriting.yaml
git commit -m "feat: add 4 RAG scrape manifests — film production, cinematography, post, screenwriting"
```

---

## Task 8: RAG Scrape Manifests — Batch 2 (AI Tools)

**Files:**
- Create: `susan-team-architect/backend/data/scrape_manifests/ai_video_tools.yaml`
- Create: `susan-team-architect/backend/data/scrape_manifests/ai_image_tools.yaml`
- Create: `susan-team-architect/backend/data/scrape_manifests/ai_audio_tools.yaml`

**Step 1: Write ai_video_tools.yaml**

Firecrawl for official docs, Exa for guides and reviews:
- firecrawl: Runway docs, Sora guides, Kling docs, Luma docs, Pika docs, HeyGen docs, Synthesia docs, Topaz Video docs, CapCut commercial docs, Descript docs, Higgsfield docs
- exa: "Sora 2 prompting techniques cinematic video generation", "Runway Gen-4 character consistency multi-shot", "Kling AI video generation tutorial workflow", "Veo 3 Google video generation capabilities", "Seedance ByteDance video model capabilities", "LTX-2 open source video generation", "AI video generation comparison 2025 2026", "Moonvalley Marey ethical AI video", "Luma Dream Machine Ray video generation"

**Step 2: Write ai_image_tools.yaml**

- firecrawl: Midjourney docs, Flux/BFL docs, Ideogram docs, Recraft docs, Leonardo docs, Krea docs, Topaz Photo docs, Magnific docs, Claid docs, ComfyUI guides
- exa: "Midjourney v7 prompting guide style reference character reference", "Flux Pro photorealistic image generation", "DALL-E 3 image generation text rendering", "Stable Diffusion 3.5 LoRA training custom models", "AI image generation comparison 2025 2026", "product photography AI generation workflow", "brand consistent AI image generation"

**Step 3: Write ai_audio_tools.yaml**

- firecrawl: ElevenLabs docs, AIVA docs, Suno docs, Udio docs, PlayHT docs, iZotope RX docs, LALAL docs, Stable Audio docs
- exa: "ElevenLabs voice cloning text to speech guide", "AI music generation commercial licensing 2025 2026", "AIVA AI music composition orchestral", "Suno AI music generation prompting", "iZotope RX audio repair professional workflow", "AI sound effects generation foley", "AI dubbing multilingual translation"

**Step 4: Commit**

```bash
git add susan-team-architect/backend/data/scrape_manifests/ai_video_tools.yaml \
        susan-team-architect/backend/data/scrape_manifests/ai_image_tools.yaml \
        susan-team-architect/backend/data/scrape_manifests/ai_audio_tools.yaml
git commit -m "feat: add 3 RAG scrape manifests — AI video, image, and audio tools"
```

---

## Task 9: RAG Scrape Manifests — Batch 3 (Instagram, Legal, Photo, University)

**Files:**
- Create: `susan-team-architect/backend/data/scrape_manifests/instagram_production.yaml`
- Create: `susan-team-architect/backend/data/scrape_manifests/film_legal.yaml`
- Create: `susan-team-architect/backend/data/scrape_manifests/photography.yaml`
- Create: `susan-team-architect/backend/data/scrape_manifests/film_university.yaml`

**Step 1: Write all 4 manifests**

Key sources per manifest:
- instagram_production: Instagram Creator docs, Hootsuite guides, Buffer research, Later strategy, Mosseri public statements, Reels algorithm optimization
- film_legal: SAG-AFTRA AI resources, WGA contract AI provisions, IATSE summaries, US Copyright Office AI guidance, Perkins Coie entertainment AI analysis, music licensing (BMI, ASCAP, Harry Fox)
- photography: Fstoppers workflows, PetaPixel techniques, SLR Lounge lighting/retouching, Phlearn compositing, AfterShoot AI culling, Capture One tethering
- film_university: USC Cinematic Arts course descriptions, NYU Tisch program, AFI Conservatory, UCLA TFT, CalArts film/video, Chapman Dodge, Columbia Film MFA, MIT OCW film studies

**Step 2: Commit**

```bash
git add susan-team-architect/backend/data/scrape_manifests/instagram_production.yaml \
        susan-team-architect/backend/data/scrape_manifests/film_legal.yaml \
        susan-team-architect/backend/data/scrape_manifests/photography.yaml \
        susan-team-architect/backend/data/scrape_manifests/film_university.yaml
git commit -m "feat: add 4 RAG scrape manifests — instagram, legal, photography, film university"
```

---

## Task 10: Execute RAG Scraping

**Step 1: Run each manifest through Susan's batch scraper**

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend
source .venv/bin/activate

# Film craft manifests
python scripts/susan_cli.py scrape-batch film_production.yaml
python scripts/susan_cli.py scrape-batch cinematography.yaml
python scripts/susan_cli.py scrape-batch post_production.yaml
python scripts/susan_cli.py scrape-batch screenwriting.yaml

# AI tool manifests
python scripts/susan_cli.py scrape-batch ai_video_tools.yaml
python scripts/susan_cli.py scrape-batch ai_image_tools.yaml
python scripts/susan_cli.py scrape-batch ai_audio_tools.yaml

# Supporting manifests
python scripts/susan_cli.py scrape-batch instagram_production.yaml
python scripts/susan_cli.py scrape-batch film_legal.yaml
python scripts/susan_cli.py scrape-batch photography.yaml
python scripts/susan_cli.py scrape-batch film_university.yaml
```

Or use MCP tool: `scrape_batch(manifest_name="film_production.yaml")`

**Step 2: Verify chunk counts**

```bash
python scripts/susan_cli.py count-knowledge
```

Expected: RAG total should increase from ~10,800 to ~15,900+ chunks.

**Step 3: Verify new data types are searchable**

```bash
python scripts/susan_cli.py search "cinematography lighting three point" --data-type cinematography
python scripts/susan_cli.py search "Sora 2 character consistency" --data-type ai_video_tools
python scripts/susan_cli.py search "ElevenLabs voice cloning" --data-type ai_audio_tools
```

---

## Task 11: Production Engine

**Files:**
- Create: `susan-team-architect/backend/susan_core/production_engine.py`
- Create: `susan-team-architect/backend/tests/test_production_engine.py`

**Step 1: Write the failing tests**

```python
"""Tests for the production engine lifecycle manager."""
import pytest
from susan_core.production_engine import ProductionEngine, Production, ProductionStatus

def test_start_production():
    engine = ProductionEngine()
    prod = engine.start("Hero video for TransformFit website", company_id="transformfit", format="film")
    assert prod.production_id is not None
    assert prod.status == ProductionStatus.DESIGN
    assert prod.company_id == "transformfit"
    assert prod.format == "film"

def test_list_productions():
    engine = ProductionEngine()
    engine.start("Reel 1", company_id="transformfit", format="reel")
    engine.start("Reel 2", company_id="transformfit", format="reel")
    engine.start("Photo set", company_id="founder-intelligence-os", format="photo")
    assert len(engine.list_productions("transformfit")) == 2
    assert len(engine.list_productions("founder-intelligence-os")) == 1

def test_production_status():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="reel")
    status = engine.get_status(prod.production_id)
    assert status["phase"] == "design"
    assert status["agents_assigned"] == []

def test_advance_phase():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "storyboard"
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "generation"
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "refinement"
    engine.advance_phase(prod.production_id)
    assert engine.get_status(prod.production_id)["phase"] == "delivered"

def test_assign_agents():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="film")
    engine.assign_agents(prod.production_id, ["film-studio-director", "screenwriter-studio", "cinematography-studio"])
    status = engine.get_status(prod.production_id)
    assert len(status["agents_assigned"]) == 3

def test_add_output():
    engine = ProductionEngine()
    prod = engine.start("Test", company_id="test", format="reel")
    engine.add_output(prod.production_id, {"type": "shot_list", "shots": 12})
    status = engine.get_status(prod.production_id)
    assert len(status["outputs"]) == 1
```

**Step 2: Run tests to verify they fail**

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend
.venv/bin/python -m pytest tests/test_production_engine.py -v
```

Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

```python
"""Production engine — manages the lifecycle of film and image productions."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProductionStatus(str, Enum):
    DESIGN = "design"
    STORYBOARD = "storyboard"
    GENERATION = "generation"
    REFINEMENT = "refinement"
    DELIVERED = "delivered"


_PHASE_ORDER = [
    ProductionStatus.DESIGN,
    ProductionStatus.STORYBOARD,
    ProductionStatus.GENERATION,
    ProductionStatus.REFINEMENT,
    ProductionStatus.DELIVERED,
]


@dataclass
class Production:
    production_id: str
    brief: str
    company_id: str
    format: str
    status: ProductionStatus = ProductionStatus.DESIGN
    agents_assigned: list[str] = field(default_factory=list)
    outputs: list[dict[str, Any]] = field(default_factory=list)


class ProductionEngine:
    """In-memory production lifecycle manager."""

    def __init__(self) -> None:
        self._productions: dict[str, Production] = {}

    def start(self, brief: str, company_id: str, format: str, title: str | None = None) -> Production:
        prod_id = f"prod-{uuid.uuid4().hex[:12]}"
        prod = Production(production_id=prod_id, brief=brief, company_id=company_id, format=format)
        self._productions[prod_id] = prod
        return prod

    def list_productions(self, company_id: str) -> list[Production]:
        return [p for p in self._productions.values() if p.company_id == company_id]

    def get_status(self, production_id: str) -> dict[str, Any]:
        prod = self._productions[production_id]
        return {
            "production_id": prod.production_id,
            "brief": prod.brief,
            "company_id": prod.company_id,
            "format": prod.format,
            "phase": prod.status.value,
            "agents_assigned": prod.agents_assigned,
            "outputs": prod.outputs,
        }

    def advance_phase(self, production_id: str) -> ProductionStatus:
        prod = self._productions[production_id]
        idx = _PHASE_ORDER.index(prod.status)
        if idx < len(_PHASE_ORDER) - 1:
            prod.status = _PHASE_ORDER[idx + 1]
        return prod.status

    def assign_agents(self, production_id: str, agent_ids: list[str]) -> None:
        self._productions[production_id].agents_assigned.extend(agent_ids)

    def add_output(self, production_id: str, output: dict[str, Any]) -> None:
        self._productions[production_id].outputs.append(output)
```

**Step 4: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_production_engine.py -v
```

Expected: 6/6 PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/susan_core/production_engine.py \
        susan-team-architect/backend/tests/test_production_engine.py
git commit -m "feat: add production engine — lifecycle manager for film/image productions"
```

---

## Task 12: MCP Tools — Studio Tools (7)

**Files:**
- Modify: `susan-team-architect/backend/mcp_server/server.py`

**Step 1: Add 7 studio MCP tools**

Add after the existing 18 `@mcp.tool()` functions. Import `ProductionEngine` at top.

Tools to add:
1. `start_production(brief, company_id, format, title)` → returns production_id and status
2. `run_studio_agent(agent_id, prompt, production_id, company_id)` → executes agent with RAG context
3. `production_status(production_id)` → returns phase, agents, outputs
4. `generate_shot_list(script_or_brief, format, style_reference)` → uses cinematography + production_manager agents
5. `generate_content_calendar(company_id, month, content_pillars, posts_per_week)` → uses instagram_studio
6. `review_production(production_id, review_type)` → runs legal/quality/technical review
7. `list_productions(company_id, status_filter)` → lists all productions

**Step 2: Run existing tests to verify no regression**

```bash
.venv/bin/python -m pytest tests/test_observability_api.py -v
```

**Step 3: Commit**

```bash
git add susan-team-architect/backend/mcp_server/server.py
git commit -m "feat: add 7 studio MCP tools — start, run, status, shot list, calendar, review, list"
```

---

## Task 13: MCP Tools — Engine Tools (3)

**Files:**
- Modify: `susan-team-architect/backend/mcp_server/server.py`

**Step 1: Add 3 engine MCP tools**

8. `route_to_engine(task_description, format, requirements)` → evaluates requirements and recommends optimal tool from image/film/audio engine
9. `design_session(brief, company_id, style_preferences)` → starts interactive design session, returns reference images and look-book structure
10. `generate_storyboard(script_or_brief, num_shots, format, style)` → generates structured storyboard with shot descriptions and tool assignments

**Step 2: Commit**

```bash
git add susan-team-architect/backend/mcp_server/server.py
git commit -m "feat: add 3 engine MCP tools — route_to_engine, design_session, generate_storyboard"
```

---

## Task 14: Full Test Suite Verification

**Step 1: Run all tests**

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend
.venv/bin/python -m pytest tests/ -v --tb=short
```

Expected: All new tests pass, no regressions in existing tests.

**Step 2: Verify agent count**

```bash
ls susan-team-architect/agents/*.md | wc -l
```

Expected: 78 (60 existing + 18 new)

**Step 3: Verify MCP tool count**

```bash
grep -c "@mcp.tool" susan-team-architect/backend/mcp_server/server.py
```

Expected: 28 (18 existing + 10 new)

**Step 4: Commit any fixes**

---

## Task 15: Update Capability Maturity

**Files:**
- Modify: `.startup-os/capabilities/film-image-studio.yaml`

**Step 1: Update maturity scores based on what's been built**

After all tasks complete, update `maturity_current` and mark completed items as `done: true`.

Expected maturity after full implementation:
- Level 1: All done → check all
- Level 2: All done → check all
- Level 3: All done → check all
- Level 4: Mark as done after workflow testing
- Level 5: Architecture in place, proven through use

**Step 2: Commit**

```bash
git add .startup-os/capabilities/film-image-studio.yaml
git commit -m "feat: update film-image-studio maturity to V3 (V5 architecture in place)"
```

---

## Task 16: Push to GitHub

```bash
git push origin main
```

Then deploy to Vercel:

```bash
cd apps/v5
VERCEL_ENV=production vercel build --prod && vercel deploy --prebuilt --prod --yes
```
