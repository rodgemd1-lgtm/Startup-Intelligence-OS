---
name: film-production
description: "Full film and image production lifecycle — orchestrate 18 AI agents across 6 formats (film, reel, photo, carousel, image, documentary) with quality gates, tool routing, and legal clearance. Use this skill whenever the user wants to create visual content, produce a video, make an Instagram reel, generate images, create a content calendar, or manage a production pipeline. Triggers on: /produce, create a film, make a reel, generate images, content production, visual content, Instagram content, brand video, photo shoot."
argument-hint: '"brief" [--company company_id] [--format film|reel|photo|carousel|image|documentary] [--auto]'
---

# Film & Image Studio — Production Skill

Orchestrate 18 AI agents across 2 layers (15 creative direction + 3 generation engines) to produce visual content in 6 formats. Each production moves through a gated lifecycle from brief to delivery.

## Overview

The Film & Image Studio is a production pipeline built on Susan's agent architecture. It accepts a creative brief, assigns specialist agents by format and phase, routes work to the right generation tools (image, video, audio), enforces quality gates, and manages legal clearance before delivery.

**Two agent layers:**
- **Creative Direction (15 agents):** Handle design, storyboarding, art direction, script, cinematography, editing, color, sound, typography, and brand compliance
- **Generation Engines (3 agents):** Route tasks to external tools for image generation, video generation, and audio generation

**Six production formats:**
- **Film** — Full narrative or brand video (60s+), multi-scene with dialogue, music, and transitions
- **Reel** — Short-form vertical video (15-90s), optimized for Instagram/TikTok with hooks and captions
- **Photo** — Single or series of still images, product photography, lifestyle shots, portraits
- **Carousel** — Multi-slide image sets (3-10 slides) for Instagram/LinkedIn with consistent styling
- **Image** — Single hero image, illustration, or graphic for web, social, or print
- **Documentary** — Long-form factual content (2-15min) with narration, b-roll, and data visualization

## Production Lifecycle

Every production moves through 5 phases in strict order:

```
design → storyboard → generation → refinement → delivered
```

### Phase 1: Design
The brief is broken into a creative direction document. Agents define the visual language, tone, color palette, typography, and brand constraints.

**Auto-assigned agents by format:**
- Film: art_director, cinematographer, colorist, brand_guardian
- Reel: art_director, motion_designer, brand_guardian
- Photo: art_director, colorist, brand_guardian
- Carousel: art_director, layout_designer, brand_guardian
- Image: art_director, colorist, brand_guardian
- Documentary: art_director, cinematographer, researcher

### Phase 2: Storyboard
Visual narrative is mapped scene-by-scene (video formats) or frame-by-frame (image formats). Shot lists, compositions, and timing are defined.

**Auto-assigned agents by format:**
- Film: storyboard_artist, script_writer, cinematographer, sound_designer
- Reel: storyboard_artist, script_writer, motion_designer
- Photo: storyboard_artist, stylist
- Carousel: storyboard_artist, copywriter
- Image: storyboard_artist, illustrator
- Documentary: storyboard_artist, script_writer, researcher

### Phase 3: Generation
Assets are produced by routing to external generation tools. The generation engine agents select the right tool for each task based on the tool routing table.

**Auto-assigned agents by format:**
- Film: image_engine, video_engine, audio_engine
- Reel: video_engine, audio_engine
- Photo: image_engine
- Carousel: image_engine
- Image: image_engine
- Documentary: video_engine, audio_engine

### Phase 4: Refinement
Generated assets are reviewed against quality gates. Agents iterate on failures, adjust color grading, tighten edits, fix artifacts, and ensure brand compliance.

**Auto-assigned agents by format:**
- Film: editor, colorist, sound_designer, brand_guardian
- Reel: editor, motion_designer, brand_guardian
- Photo: colorist, brand_guardian
- Carousel: layout_designer, brand_guardian
- Image: brand_guardian
- Documentary: editor, narrator, brand_guardian

### Phase 5: Delivered
All quality gates pass. Legal clearance is confirmed. Assets are packaged with metadata and delivery specs.

**Quality gate enforcement:** A production cannot advance from refinement to delivered until ALL quality gates for its format pass. This is the only hard gate in the lifecycle.

## Starting a Production

### Option 1: Guided (default)

```
/produce "TransformFit brand anthem showcasing real user transformations" --format film --company transformfit
```

This calls:
1. `start_production(brief, company_id, format)` — Creates the production record, returns `production_id`
2. `orchestrate_production(production_id)` — Auto-assigns design-phase agents, advances to design phase
3. User reviews design output, then manually advances through subsequent phases

### Option 2: Fully Autonomous

```
/produce "4 Instagram reels for March campaign" --format reel --company transformfit --auto
```

This calls:
1. `start_production(brief, company_id, format)` — Creates the production record
2. `auto_run_production(production_id)` — Runs the full pipeline autonomously through refinement
3. Production pauses at refinement for human review before delivery

### Option 3: Direct MCP calls

For fine-grained control, call MCP tools directly:

```python
# Start
start_production(brief="Product hero shots", company_id="transformfit", format="photo")

# Check status
get_production_status(production_id="prod_abc123")

# Advance manually
advance_production_phase(production_id="prod_abc123", target_phase="storyboard")

# Run a specific agent
run_production_agent(production_id="prod_abc123", agent_id="art_director")

# Review quality gates
check_quality_gates(production_id="prod_abc123")
```

## Agent Roster

### Creative Direction Agents (15)

| Agent | Role | Formats |
|-------|------|---------|
| `art_director` | Overall visual direction, style definition | All 6 |
| `cinematographer` | Camera angles, lighting, shot composition | Film, Documentary |
| `colorist` | Color grading, palette enforcement, mood | Film, Photo, Image |
| `brand_guardian` | Brand compliance, style guide enforcement | All 6 |
| `storyboard_artist` | Visual sequence planning, shot lists | All 6 |
| `script_writer` | Dialogue, narration, voiceover scripts | Film, Reel, Documentary |
| `sound_designer` | Sound effects, ambience, audio layering | Film, Documentary |
| `motion_designer` | Animations, transitions, kinetic type | Reel, Film |
| `editor` | Pacing, cuts, assembly, final timeline | Film, Reel, Documentary |
| `layout_designer` | Grid systems, slide structure, spacing | Carousel |
| `copywriter` | Headlines, captions, overlay text | Carousel, Reel |
| `stylist` | Props, wardrobe, set design direction | Photo |
| `illustrator` | Custom illustration, iconography | Image, Carousel |
| `narrator` | Voiceover direction, pacing, tone | Documentary |
| `researcher` | Fact verification, data visualization | Documentary |

### Generation Engine Agents (3)

| Agent | Capability | Tools Routed |
|-------|-----------|--------------|
| `image_engine` | Still image generation and editing | Flux, Midjourney, Ideogram, DALL-E 3, Stable Diffusion, Firefly |
| `video_engine` | Video clip generation and compositing | Sora 2, Veo 3.1, Runway Gen-4, Kling 2.1, Pika 2.2, Minimax |
| `audio_engine` | Music, voice, and sound effect generation | ElevenLabs, Suno, Udio, AIVA, Stable Audio |

## Agent Assignments by Format and Phase

| Format | Design | Storyboard | Generation | Refinement |
|--------|--------|------------|------------|------------|
| **Film** | art_director, cinematographer, colorist, brand_guardian (4) | storyboard_artist, script_writer, cinematographer, sound_designer (4) | image_engine, video_engine, audio_engine (3) | editor, colorist, sound_designer, brand_guardian (4) |
| **Reel** | art_director, motion_designer, brand_guardian (3) | storyboard_artist, script_writer, motion_designer (3) | video_engine, audio_engine (2) | editor, motion_designer, brand_guardian (3) |
| **Photo** | art_director, colorist, brand_guardian (3) | storyboard_artist, stylist (2) | image_engine (1) | colorist, brand_guardian (2) |
| **Carousel** | art_director, layout_designer, brand_guardian (3) | storyboard_artist, copywriter (2) | image_engine (1) | layout_designer, brand_guardian (2) |
| **Image** | art_director, colorist, brand_guardian (3) | storyboard_artist, illustrator (2) | image_engine (1) | brand_guardian (1) |
| **Documentary** | art_director, cinematographer, researcher (3) | storyboard_artist, script_writer, researcher (3) | video_engine, audio_engine (2) | editor, narrator, brand_guardian (3) |

## Quality Gates

Quality gates are enforced at the refinement-to-delivered transition. Every gate for the format must pass before delivery.

### Gates by Format

| Format | Quality Gates |
|--------|--------------|
| **Film** | `physics_plausibility`, `character_consistency`, `motion_quality`, `audio_sync`, `resolution`, `continuity` |
| **Reel** | `hook_impact`, `aspect_ratio`, `duration`, `caption_safe`, `audio_sync` |
| **Photo** | `resolution`, `composition`, `color_accuracy`, `artifact_check` |
| **Carousel** | `slide_consistency`, `text_legibility`, `aspect_ratio`, `brand_compliance` |
| **Image** | `resolution`, `character_consistency`, `text_legibility`, `artifact_check`, `brand_compliance`, `style_consistency` |
| **Documentary** | `narrative_clarity`, `audio_quality`, `resolution`, `fact_check` |

### Gate Definitions

| Gate | What It Checks |
|------|---------------|
| `physics_plausibility` | Objects obey gravity, lighting is consistent, no impossible geometry |
| `character_consistency` | Same character looks the same across scenes/frames |
| `motion_quality` | No jitter, smooth transitions, natural movement |
| `audio_sync` | Dialogue matches lip movement, effects sync with action |
| `resolution` | Meets minimum output resolution for the delivery target |
| `continuity` | Props, wardrobe, lighting consistent across scenes |
| `hook_impact` | First 3 seconds grab attention, pattern-interrupt verified |
| `aspect_ratio` | Matches target platform (9:16 reel, 1:1 carousel, 16:9 film) |
| `duration` | Within platform limits (15-90s reel, 60s+ film) |
| `caption_safe` | Text and captions inside safe zones, not overlapping UI elements |
| `composition` | Rule of thirds, leading lines, visual balance |
| `color_accuracy` | Matches brand palette, no color banding or shifts |
| `artifact_check` | No AI artifacts, glitches, extra fingers, distorted text |
| `slide_consistency` | All carousel slides share style, spacing, typography |
| `text_legibility` | Text readable at target display size, contrast passes WCAG |
| `brand_compliance` | Logo placement, color usage, tone match brand guidelines |
| `style_consistency` | All outputs share a coherent visual style |
| `narrative_clarity` | Story arc is clear, information builds logically |
| `audio_quality` | No clipping, balanced levels, clean recording |
| `fact_check` | Claims are verifiable, data is sourced |

## Tool Routing

The generation engine agents route each task to the best external tool based on content type and requirements. 28 routing entries across 3 engines.

### Image Engine (9 routes)

| Content Type | Routed Tool | Reason |
|-------------|-------------|--------|
| `photorealistic` | Flux | Best photorealism, natural lighting |
| `concept_art` | Midjourney | Strongest artistic interpretation |
| `text_heavy` | Ideogram | Superior text rendering in images |
| `illustration` | Midjourney | Rich stylistic control |
| `product_shot` | Flux | Clean studio-quality output |
| `ui_mockup` | DALL-E 3 | Precise layout following |
| `texture_pattern` | Stable Diffusion | Fine-grained control via ControlNet |
| `composite_edit` | Firefly | Non-destructive editing, layer-aware |
| `brand_asset` | Ideogram | Logo-safe text + graphic integration |

### Video Engine (10 routes)

| Content Type | Routed Tool | Reason |
|-------------|-------------|--------|
| `dialogue_scene` | Sora 2 | Best lip sync and character acting |
| `long_establishing` | Veo 3.1 | Longest coherent clips, stable camera |
| `action_sequence` | Runway Gen-4 | Dynamic motion, physics-aware |
| `product_demo` | Kling 2.1 | Object manipulation, smooth transitions |
| `abstract_motion` | Pika 2.2 | Stylized animation, creative effects |
| `talking_head` | Sora 2 | Realistic face generation and animation |
| `timelapse` | Veo 3.1 | Temporal consistency over long spans |
| `screen_recording` | Minimax | UI animation, app walkthrough |
| `transition` | Runway Gen-4 | Morph and blend effects |
| `slow_motion` | Kling 2.1 | Frame interpolation, temporal upscaling |

### Audio Engine (9 routes)

| Content Type | Routed Tool | Reason |
|-------------|-------------|--------|
| `voice_dialogue` | ElevenLabs | Most natural voice cloning and acting |
| `voice_narration` | ElevenLabs | Consistent narrator voice, pacing control |
| `music_orchestral` | AIVA | Classical composition, film scoring |
| `music_pop` | Suno | Contemporary genres, vocals |
| `music_electronic` | Udio | EDM, ambient, synthwave |
| `music_ambient` | Stable Audio | Background textures, atmospheric |
| `sound_effect` | ElevenLabs Sound Effects | Foley, impacts, environmental |
| `jingle` | Suno | Short branded audio, catchy hooks |
| `podcast_voice` | ElevenLabs | Long-form narration, multi-speaker |

## Legal Clearance

Every production must clear legal review before delivery. The clearance system tracks 7 types across 4 statuses.

### Clearance Types

| Type | What It Covers |
|------|---------------|
| `music_license` | Rights for background music, score, jingles |
| `voice_rights` | Consent for AI-generated or cloned voices |
| `likeness_rights` | Permission for real person depiction |
| `brand_usage` | Authorization to use brand marks, logos, colors |
| `stock_license` | License status for any stock footage or images |
| `location_release` | Rights for recognizable locations |
| `talent_release` | Model/actor consent and usage terms |

### Clearance Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Clearance requested, not yet reviewed |
| `cleared` | Approved for use |
| `flagged` | Issue identified, requires resolution |
| `denied` | Cannot be used, must be replaced |

### Delivery Gating

A production cannot reach `delivered` status if ANY clearance item is `flagged` or `denied`. All clearances must be `cleared` before final delivery. The `check_legal_clearance` tool reports outstanding items.

## Example Workflows

### 1. Full film production

```
/produce "TransformFit brand anthem — 90 second hero video showcasing real user transformation journeys, cinematic tone, motivational arc" --format film --company transformfit
```

Pipeline:
1. `start_production` creates the production with format=film
2. `orchestrate_production` assigns art_director, cinematographer, colorist, brand_guardian to design phase
3. Design phase outputs: visual language doc, color palette, shot style reference
4. Advance to storyboard: storyboard_artist, script_writer, cinematographer, sound_designer
5. Storyboard outputs: 12-scene shot list, dialogue script, music brief
6. Advance to generation: image_engine, video_engine, audio_engine route to Sora 2 (dialogue), Veo 3.1 (establishing), ElevenLabs (VO), AIVA (score)
7. Advance to refinement: editor, colorist, sound_designer, brand_guardian check 6 quality gates
8. All gates pass + legal clearances cleared = delivered

### 2. Instagram reel batch

```
/produce "4 Instagram reels for TransformFit March campaign — each 30s, hook-first, featuring before/after transformations" --format reel --company transformfit --auto
```

Pipeline:
1. `start_production` + `auto_run_production` runs the full pipeline
2. Auto-assigns reel agents per phase
3. Generation routes to Runway Gen-4 (action), ElevenLabs (VO), Suno (music)
4. Quality gates check: hook_impact, aspect_ratio (9:16), duration (30s), caption_safe, audio_sync
5. Pauses at refinement for human review

### 3. Product photo shoot

```
/produce "Product photography for TransformFit landing page — hero shots of the app on iPhone, lifestyle gym setting, warm lighting" --format photo --company transformfit
```

Pipeline:
1. `start_production` with format=photo
2. `orchestrate_production` assigns art_director, colorist, brand_guardian
3. Design outputs: mood board, lighting reference, composition guides
4. Storyboard: storyboard_artist, stylist define 6 shots with prop/set direction
5. Generation: image_engine routes to Flux (photorealistic product shots)
6. Refinement: colorist, brand_guardian check resolution, composition, color_accuracy, artifact_check

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `start_production` | Create a new production from a brief, format, and company |
| `get_production_status` | Check current phase, assigned agents, and gate results |
| `orchestrate_production` | Auto-assign agents for the current phase and advance |
| `auto_run_production` | Run the full pipeline autonomously through refinement |
| `advance_production_phase` | Manually move to the next phase |
| `run_production_agent` | Execute a specific agent's task within the current phase |
| `check_quality_gates` | Evaluate all quality gates for the current format |
| `check_legal_clearance` | Review legal clearance status for all items |
| `update_legal_clearance` | Set clearance status for a specific item |
| `list_productions` | List all productions for a company, optionally filtered by status |
| `get_production_assets` | Retrieve generated assets and their metadata |
| `update_production_brief` | Modify the brief or parameters mid-production |
| `assign_agent` | Manually assign an agent to the current phase |
| `remove_agent` | Remove an agent from the current phase |
| `get_tool_routing` | View the routing table for a generation engine |
| `deliver_production` | Mark a production as delivered after all gates and clearances pass |

## Error Handling

- If a generation tool is unavailable, the engine agent falls back to the next-best tool in the routing table
- If a quality gate fails, the refinement agent receives the failure details and iterates
- If legal clearance is denied for an asset, the production loops back to generation for that specific asset
- If `auto_run_production` stalls, call `get_production_status` to identify the blocked phase and agent
- A production can be paused at any phase and resumed later without losing state
