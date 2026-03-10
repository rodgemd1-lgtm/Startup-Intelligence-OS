# AI Film & Image Studio — Design Document

**Date**: 2026-03-10
**Status**: Approved
**Company**: Multi-tenant (founder-intelligence-os, transformfit, oracle-health-ai, + external)
**Capability target**: V5 / 5.0 — Hollywood-Grade Autonomous
**Production model**: AI-generation-first (physical shoots supplemental)
**Timeline**: 2-week sprint to full V5 architecture

---

## Architecture Overview

Three-layer architecture:

```
┌──────────────────────────────────────────────────────────┐
│  LAYER 1: CREATIVE DIRECTION (15 Studio Agents)          │
│  Screenwriter, Cinematography, Editing, Sound, etc.      │
│  → Decide WHAT to create                                 │
├──────────────────────────────────────────────────────────┤
│  LAYER 2: GENERATION ENGINES (3 Sub-Studios)             │
│  Image Engine · Film Engine · Audio Engine                │
│  → Decide HOW to create it + WHICH tool to use           │
├──────────────────────────────────────────────────────────┤
│  LAYER 3: PRODUCTION PROCESS                             │
│  Design Session → Storyboard → Concept Gen → Refinement  │
│  → The WORKFLOW the operator walks through               │
└──────────────────────────────────────────────────────────┘
```

---

## Layer 1: Creative Direction — 15 Studio Agents

### Creative Leadership

| # | Agent ID | Role | Hollywood Equivalent |
|---|---|---|---|
| 1 | `film-studio-director` | Orchestrates multi-agent productions. Breaks briefs into plans. Assigns agents. Reviews quality. | Studio Head / EP |
| 2 | `screenwriter-studio` | Scripts, treatments, loglines, dialogue, story structure. Frameworks: Save the Cat, Story Grid, McKee. | Screenwriter |

### Visual Production

| # | Agent ID | Role | Hollywood Equivalent |
|---|---|---|---|
| 3 | `cinematography-studio` | Visual language, shot design, lighting, lens selection, color science, ACES pipeline | DP / Camera Dept |
| 4 | `production-designer-studio` | World-building, environments, set design, props, AI scene generation | Production Designer |
| 5 | `photography-studio` | Commercial, editorial, product, portrait pipelines | Lead Photographer |

### Post-Production

| # | Agent ID | Role | Hollywood Equivalent |
|---|---|---|---|
| 6 | `editing-studio` | Assembly, pacing, rhythm, performance selection. Murch's 6 priorities. | Editor |
| 7 | `color-grade-studio` | Color grading, ACES, look development, HDR mastering, DCI-P3/Rec.2020 | Colorist |
| 8 | `sound-design-studio` | SFX, Foley, ambience, Atmos mixing, audio repair | Sound Designer |
| 9 | `music-score-studio` | Original scoring, music supervision, sync licensing, AI composition | Composer |
| 10 | `vfx-studio` | Visual effects, compositing, CG integration, motion graphics | VFX Supervisor |

### Production Management

| # | Agent ID | Role | Hollywood Equivalent |
|---|---|---|---|
| 11 | `production-manager-studio` | Budgets, schedules, shot lists, call sheets, resource allocation | Line Producer / UPM |
| 12 | `talent-cast-studio` | Voice casting, AI voice direction, performance coaching | Casting Director |
| 13 | `legal-rights-studio` | Clearances, releases, AI consent protocols, guild compliance, copyright | Entertainment Lawyer |

### Distribution

| # | Agent ID | Role | Hollywood Equivalent |
|---|---|---|---|
| 14 | `distribution-studio` | Festival strategy, streaming specs, DCP, marketing campaigns | Distribution Executive |
| 15 | `instagram-studio` | Reels, Stories, carousels, algorithm optimization, batch production | Social Media Producer |

---

## Layer 2: Generation Engines — 3 Sub-Studios

### A. Image Generation Engine (`image-gen-engine`)

Tool router and quality controller for all still image generation.

#### Tier 1 — Cinematic / Photorealistic

| Tool | Version | Quality | Best For | Character Consistency | Text Rendering | API | Price |
|---|---|---|---|---|---|---|---|
| Midjourney | v7 | 9.5/10 | Concept art, mood boards, cinematic stills | Strong (--cref) | Weak | Yes | $10-120/mo |
| Flux Pro | 1.1 Ultra | 9/10 | Photorealistic portraits, product, editorial | Good (IP adapter) | Strong | Yes (BFL) | $0.04-0.06/img |
| DALL-E 3 | GPT-4o native | 8.5/10 | Quick iteration, text-in-image, inline editing | Moderate | Best-in-class | Yes (OpenAI) | $0.04-0.08/img |
| Ideogram | 3.0 | 8.5/10 | Typography, title cards, branded visuals | Good | Excellent | Yes | $8-80/mo |
| Google Imagen 3 | Gemini native | 8.5/10 | Photorealistic scenes, natural imagery | Good | Good | Yes (Vertex) | Pay-per-use |
| Recraft | V3 | 8.5/10 | Brand design, vector, illustrations, style lock | Strong | Excellent | Yes | $25-100/mo |

#### Tier 2 — Professional Creative

| Tool | Version | Quality | Best For | API | Price |
|---|---|---|---|---|---|
| Adobe Firefly | Image 3 | 8/10 | Commercial-safe (licensed training data) | Yes | $5-23/mo |
| Leonardo AI | Phoenix 2 | 7.5/10 | Game art, concept iteration, Canva ecosystem | Yes | $12-60/mo |
| Stable Diffusion | 3.5 Large | 7/10 | Self-hosted, custom LoRA, full control | Self-host | Free |
| Krea AI | Latest | 7.5/10 | Real-time generation, live canvas | No | $8-24/mo |

#### Tier 3 — Specialized

| Tool | Best For | Quality |
|---|---|---|
| Topaz Photo AI | Enhancement, noise removal, 8x upscaling | 9/10 |
| Magnific AI | Creative upscaling with hallucinated detail | 8.5/10 |
| Claid.ai | Product photography backgrounds, e-commerce | 8/10 |
| Photoroom | Background removal, product staging | 8/10 |
| ComfyUI | Custom SD pipelines, node-based automation | Model-dependent |
| Astria | Custom fine-tuning (faces, products, brands) | 8/10 |

#### Image Routing Logic

```
IF photorealistic portrait/editorial → Flux Pro 1.1 Ultra
IF concept art / mood board         → Midjourney v7
IF text-heavy / typography          → Ideogram 3.0 or DALL-E 3
IF brand-consistent series          → Recraft V3 (style locking)
IF product photography              → Claid.ai + Flux Pro
IF rapid iteration / exploration    → DALL-E 3 (conversational)
IF commercial-safe required         → Adobe Firefly Image 3
IF custom subject (trained)         → Astria + Flux
IF enhancement/upscaling            → Topaz Photo AI or Magnific
IF inpainting/editing               → DALL-E 3 or Runway
IF self-hosted pipeline             → SD 3.5 via ComfyUI
```

#### Image Quality Gates

| Gate | Threshold |
|---|---|
| Resolution | 2048x2048 hero images; 1080x1920 social |
| Consistency | 90%+ visual match on reference comparison |
| Text legibility | 100% readable — no garbled text shipped |
| Artifact check | Zero visible artifacts (fingers, eyes, physics) |
| Brand compliance | Exact hex match on brand colors |

---

### B. Film Generation Engine (`film-gen-engine`)

Tool router for all video generation.

#### Tier 1 — Cinematic

| Tool | Version | Quality | Duration | Resolution | Audio | Char Lock | Camera | API | Cost |
|---|---|---|---|---|---|---|---|---|---|
| Sora 2 | Pro | 9/10 | 25s | 1024p | Native dialogue+SFX | Strong (storyboard) | Prompt | Yes | $0.10-0.50/s |
| Veo 3.1 | Standard | 9/10 | 60s | 1080p | Native conversation | Strong | Cinematic | Yes | $0.15-0.40/s |
| Seedance 2.0 | Pro | 9/10 | Extended | 2K/60fps | Dual-branch | Strong (12 refs) | Frame-level | Yes | ~$0.14/s |
| Runway Gen-4.5 | Latest | 8.5/10 | 10s | 4K | No | Best (single ref) | Zoom/pan/tilt | Yes | ~$0.20/s |
| Kling 3.0 | Latest | 8.5/10 | 2min | 1080p/48fps | Full audio | Good | Director Mode | Yes | $7-65/mo |

#### Tier 2 — Professional Social

| Tool | Quality | Best For | Audio | Duration | Cost |
|---|---|---|---|---|---|
| Luma Ray 3.14 | 7.5/10 | Fast iteration, HDR, V2V | No | 10s | $0.06/s |
| Pika 2.5 | 7/10 | Stylized social, Scene Ingredients | No | 10s | $8-58/mo |
| Hailuo 2.3 | 7/10 | Anime/illustration, multilingual | No | 6-10s | $10-50/mo |
| LTX-2 | 7.5/10 | Open source, 4K/50fps, self-hosted | Yes | 20s | Free |
| Higgsfield | 7/10 | 50+ cinematic camera presets | No | Short | $12-79/mo |

#### Tier 3 — Specialized

| Tool | Use Case | Quality |
|---|---|---|
| Moonvalley Marey | Ethically trained footage (IP-safe) | 7.5/10 |
| Synthesia | Talking-head corporate video | 7/10 |
| HeyGen | Multilingual avatar, lip sync | 7/10 |
| D-ID | Photo-to-talking-head | 6.5/10 |
| Autodesk Flow | CG character VFX replacement | 8.5/10 |
| Topaz Video AI | Upscaling 4K/8K, frame interpolation | 9/10 |
| OpusClip | Long-form to viral clips | 7/10 |
| Descript | Text-based video editing | 7.5/10 |
| CapCut | Social-first editing, auto-captions | 7/10 |

#### Film Routing Logic

```
IF dialogue scene with characters       → Sora 2 Pro (storyboard mode)
IF long establishing/environment shot   → Veo 3.1 (60s, physical realism)
IF character across 5+ shots            → Runway Gen-4.5 (best consistency)
IF simultaneous audio + video           → Seedance 2.0 or Kling 3.0
IF highest resolution (4K)              → Runway Gen-4.5 or LTX-2
IF budget batch (10+ clips)             → Kling 3.0 or Luma Ray Flash
IF cinematic camera movement            → Higgsfield (50+ presets) or Runway
IF ethical/IP-safe footage              → Moonvalley Marey
IF talking head / avatar                → HeyGen or Synthesia
IF VFX / CG character composite         → Autodesk Flow Studio
IF upscaling existing footage           → Topaz Video AI
IF self-hosted pipeline                 → LTX-2 or Wan 2.1
IF social Reel (fast turnaround)        → Kling 3.0 + CapCut
```

#### Film Quality Gates

| Gate | Threshold |
|---|---|
| Physics | Zero floating objects or impossible motion |
| Character | 95%+ match to reference across shots |
| Motion | No jitter, rubber-banding, or morphing |
| Audio sync | <100ms latency lip sync |
| Resolution | 1080p social; 2K+ film |
| Duration | Within ±0.5s of storyboard timing |
| Continuity | Color-graded to consistent palette |

---

### C. Audio Generation Engine (`audio-gen-engine`)

#### Voice Tools

| Tool | Quality | Clone | Languages | Latency | API | Rights | Cost |
|---|---|---|---|---|---|---|---|
| ElevenLabs | 9.5/10 | 9/10 | 32 | 300ms | Yes | Yes (paid) | $5-330/mo |
| PlayHT | 8.5/10 | 8/10 | 142+ | 300ms | Yes | Yes | $29-99/mo |
| Cartesia | 8/10 | 7.5/10 | 10+ | <100ms | Yes | Yes | Usage-based |
| Fish Audio | 8/10 | 8.5/10 | 13+ | Low | Yes | Yes | $15-70/mo |
| Resemble AI | 8/10 | 8.5/10 | 24+ | Varies | Yes | Yes (ent) | Custom |

#### Music Tools

| Tool | Quality | Stems | Copyright Ownership | Cleared Platforms | API | Cost |
|---|---|---|---|---|---|---|
| AIVA | 8/10 | Yes | Full ownership (Pro) | All | Yes | ~$15-49/mo |
| ElevenLabs Music | 8/10 | Limited | Licensed (Merlin/Kobalt) | YouTube safe | Yes | Included |
| Suno | 8.5/10 | No | User owns (Pro) | Warner settled | No | $8-48/mo |
| Udio | 8.5/10 | Yes (4-stem) | User owns (paid) | UMG settled | No | $10-50/mo |
| Stable Audio | 7.5/10 | Yes | Licensed | Commercial OK | Yes | $12-36/mo |
| Soundraw | 7/10 | Customizable | Full ownership | All | No | $17-50/mo |

#### SFX & Repair Tools

| Tool | Use | Quality | API |
|---|---|---|---|
| ElevenLabs SFX | AI sound effect generation | 8/10 | Yes |
| iZotope RX 11 | Professional audio repair (industry standard) | 9.5/10 | Plugin |
| Adobe Podcast AI | Voice enhancement, noise removal | 8/10 | No |
| LALAL.AI | Stem separation | 8.5/10 | Yes |
| Moises AI | Stem separation + remix | 8/10 | Yes |
| Krisp | Real-time noise cancellation | 8/10 | SDK |

#### Audio Routing Logic

```
IF character dialogue         → ElevenLabs (clone with consent)
IF narrator voiceover         → ElevenLabs or PlayHT (stock)
IF ultra-low-latency          → Cartesia (<100ms)
IF cinematic orchestral       → AIVA (full copyright)
IF pop/rock/genre song        → Suno or Udio
IF cleared for streaming      → ElevenLabs Music
IF custom background music    → Soundraw (customizable)
IF sound effects              → ElevenLabs SFX
IF audio repair/cleanup       → iZotope RX 11
IF stem separation            → LALAL.AI or Moises
IF multilingual dubbing       → ElevenLabs Dubbing Studio
IF real-time voice conversion → Resemble AI
```

---

## Layer 3: Production Process — 4 Phases

### Phase 1: Design Session

```
1. BRIEF INTAKE
   Operator describes idea → Film Studio Director asks:
   - Purpose (website, social, film, pitch)?
   - Audience?
   - Emotional tone?
   - Reference examples?

2. REFERENCE GATHERING
   Image Gen Engine generates 20-30 references across styles:
   - 5 photorealistic
   - 5 cinematic/dramatic
   - 5 stylized/artistic
   - 5 brand-aligned
   - 5 experimental
   Operator picks favorites, explains why.

3. LOOK & FEEL LOCK
   Cinematography Studio defines visual language:
   - Color palette
   - Lighting style
   - Composition rules
   - Camera movement vocabulary
   Image Gen Engine produces 10 refined images in locked style.
   Operator approves or iterates.

4. BRAND SYSTEM GENERATION (if multi-piece)
   - Character reference sheets
   - Environment reference sheets
   - Typography and overlay system
   - Audio/music direction
```

### Phase 2: Storyboarding

```
1. SCRIPT/NARRATIVE
   Screenwriter Studio produces:
   - Beat sheet
   - Scene breakdown
   - Dialogue
   - Shot-by-shot descriptions

2. VISUAL STORYBOARD
   Image Gen Engine generates frame per shot:
   - Matches locked look & feel
   - Framing, composition, character visible
   - Camera movement annotated
   - Duration noted

3. ANIMATIC (optional)
   Film Gen Engine creates rough motion test:
   - Low-cost (Luma Ray Flash or Kling free)
   - Tests timing, pacing, transitions
   - Temp voice/music

4. PRODUCTION PLAN
   Production Manager Studio generates:
   - Shot list with tool assignments
   - Cost estimate per shot
   - Generation sequence (dependencies)
   - Quality gate checkpoints
```

### Phase 3: Concept Generation

```
1. HERO ASSET GENERATION
   Film Gen Engine: each shot per storyboard
   - Routes to optimal tool per shot
   - 3 variants per shot (operator picks)
   - Character consistency across all shots
   Image Gen Engine: hero stills
   - Thumbnails, posters, social assets

2. AUDIO PRODUCTION
   Audio Gen Engine:
   - Dialogue (ElevenLabs)
   - Score (AIVA / Suno)
   - SFX (ElevenLabs SFX)
   - Ambient beds

3. ASSEMBLY
   Editing Studio:
   - Video cuts per storyboard
   - Audio layering
   - Transitions and pacing

4. QUALITY REVIEW
   All engines run quality gates
   Legal & Rights Studio clearance
```

### Phase 4: Refinement & Delivery

```
1. COLOR GRADE → Color & Grade Studio
2. SOUND MIX → Sound Design Studio (stereo + 5.1 + Atmos)
3. FORMAT DELIVERY → Distribution Studio:
   - Instagram Reel (1080x1920, <90s, H.264)
   - YouTube (3840x2160, H.265)
   - Website (optimized MP4/WebM)
   - Streaming (Netflix/Apple specs)
   - Theatrical DCP (if applicable)
4. SOCIAL OPTIMIZATION → Instagram Studio:
   - 1.7s hook
   - Captions, hashtags, posting time
   - Thumbnail, calendar placement
```

---

## File Structure

```
susan-team-architect/
├── agents/
│   ├── # LAYER 1: Creative Direction (15 agents)
│   ├── film-studio-director.yaml
│   ├── screenwriter-studio.yaml
│   ├── cinematography-studio.yaml
│   ├── production-designer-studio.yaml
│   ├── editing-studio.yaml
│   ├── color-grade-studio.yaml
│   ├── sound-design-studio.yaml
│   ├── music-score-studio.yaml
│   ├── vfx-studio.yaml
│   ├── talent-cast-studio.yaml
│   ├── production-manager-studio.yaml
│   ├── distribution-studio.yaml
│   ├── instagram-studio.yaml
│   ├── photography-studio.yaml
│   ├── legal-rights-studio.yaml
│   │
│   ├── # LAYER 2: Generation Engines (3 sub-studios)
│   ├── image-gen-engine.yaml
│   ├── film-gen-engine.yaml
│   └── audio-gen-engine.yaml
│
├── backend/
│   ├── mcp_server/
│   │   └── server.py                     # +10 MCP tools
│   ├── data/
│   │   └── scrape_manifests/
│   │       ├── film_production.yaml
│   │       ├── cinematography.yaml
│   │       ├── post_production.yaml
│   │       ├── screenwriting.yaml
│   │       ├── ai_video_tools.yaml
│   │       ├── ai_image_tools.yaml
│   │       ├── ai_audio_tools.yaml
│   │       ├── instagram_production.yaml
│   │       ├── film_legal.yaml
│   │       ├── photography.yaml
│   │       └── film_university.yaml
│   └── susan_core/
│       └── production_engine.py
│
.startup-os/
├── capabilities/
│   └── film-image-studio.yaml
```

---

## MCP Tools (10)

| # | Tool | Purpose |
|---|---|---|
| 1 | `start_production` | Initialize production with brief, company, format |
| 2 | `run_studio_agent` | Execute any studio agent with production context |
| 3 | `production_status` | Get production progress and outputs |
| 4 | `generate_shot_list` | Script → structured shot list |
| 5 | `generate_content_calendar` | Monthly Instagram calendar with briefs |
| 6 | `review_production` | Quality/legal/technical review |
| 7 | `list_productions` | List all productions by company |
| 8 | `route_to_engine` | Route generation task to optimal tool |
| 9 | `design_session` | Start interactive design session |
| 10 | `generate_storyboard` | Brief → visual storyboard with AI frames |

---

## RAG Knowledge Base — 11 Scrape Manifests

| Manifest | Sources | Target |
|---|---|---|
| film_production.yaml | NoFilmSchool, StudioBinder, FilmmakerMag | 500+ |
| cinematography.yaml | ASC, CookeOptics, MixingLight | 500+ |
| post_production.yaml | ProVideoCoalition, SoundOnSound, FilmSound.org | 500+ |
| screenwriting.yaml | ScreenCraft, ScriptMag, format guides | 400+ |
| ai_video_tools.yaml | Sora, Runway, Kling, Veo, Luma, Seedance, LTX-2, Higgsfield, Moonvalley, HeyGen, Synthesia, Topaz, CapCut, Descript, OpusClip docs | 800+ |
| ai_image_tools.yaml | Midjourney, Flux/BFL, DALL-E, Ideogram, Recraft, Firefly, Leonardo, Krea, ComfyUI, Topaz Photo, Magnific, Claid, Astria docs | 600+ |
| ai_audio_tools.yaml | ElevenLabs, AIVA, Suno, Udio, PlayHT, iZotope, LALAL, Moises, Stable Audio, Cartesia, Fish Audio docs | 500+ |
| instagram_production.yaml | Instagram Creator, Hootsuite, Buffer, Later, Mosseri | 300+ |
| film_legal.yaml | SAG-AFTRA, WGA, IATSE, Copyright Office, Perkins Coie | 300+ |
| photography.yaml | Fstoppers, PetaPixel, SLR Lounge, Phlearn, Capture One | 300+ |
| film_university.yaml | USC, NYU, AFI, UCLA, CalArts, Chapman, Columbia, MIT OCW | 400+ |

**Total: 5,100+ new chunks → RAG grows from ~10,800 to ~15,900+**

---

## Capability Maturity Definition

| Level | Name | What it means |
|---|---|---|
| 1 | Basic Creation | AI image gen, simple clips, social posts. No pipeline. |
| 2 | Structured Production | Templates, workflows, 5+ AI tools. Consistent social quality. |
| 3 | Professional Pipeline | Multi-agent productions. ACES color. Full post. Streaming-ready. |
| 4 | Studio-Grade | Cinematic quality. Dolby Atmos. Multi-format. Guild-aware consent. |
| 5 | Hollywood-Grade Autonomous | AI-directed productions. Feature-length consistency. Festival/theatrical. External clients. Full legal. |

---

## Production Workflow Templates

### A. Full Film Production
Brief → Director → Screenwriter → Cinematography → Prod Designer → Prod Manager → [AI GEN: Image+Film+Audio engines] → Editing → Color → Sound → Music → VFX → Legal → Distribution

### B. Instagram Reel (Batch)
Calendar → Instagram Studio → Screenwriter (hook+script) → Cinematography (9:16) → [AI GEN] → Editing (1.7s hook) → Color → Sound → Instagram (captions+schedule)

### C. Product Photography
Brief → Photography → Prod Designer → [AI GEN: Image engine] → Photography (culling) → Color → Legal

### D. Brand Film / Documentary
Brief → Director → Screenwriter → Cinematography → Prod Manager → [PRODUCTION] → Editing → Color → Sound → Music → Distribution (multi-format)

### E. Website Visual Package
Brief → Design Session → Storyboard → [AI GEN: Image+Film engines] → Editing → Color → Distribution (web-optimized formats)
