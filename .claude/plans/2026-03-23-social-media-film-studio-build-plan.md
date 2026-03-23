# Social Media Film Studio — Build Plan

**Date**: 2026-03-23
**Status**: PLAN (awaiting approval)
**Design Doc**: `2026-03-23-social-media-film-studio-design.md`
**Research**: `2026-03-23-social-media-film-studio-research/`
**Target**: Go live Friday March 28, 2026

---

## Architecture Summary

```
Claude Code (Jake) ──orchestrates──▶ Higgsfield API (characters + video)
                                    ▶ Kling 3.0 API (fitness motion)
                                    ▶ Gemini MCP (still images)
                                    ▶ ElevenLabs (voiceover)
                     ──posts via──▶ Viral Architect → Instagram Graph API
                                    repo: ~/viral-architect-hub
                                    endpoint: instagram_publisher.py
                                    account: @rodgemd1
```

---

## Build Steps (7 Steps, 3 Sessions)

### SESSION 1: Foundation (Today — March 23)
**Estimated context: MEDIUM (~40K tokens)**
**Files touched: ~6**

#### Step 1: Install & Configure Generation Tools
**What**: Get Higgsfield SDK and Kling MCP wired into this environment
**Files**:
- `~/.hermes/.env` — verify HIGGSFIELD keys (already stored ✅)
- MCP config — add krea-mcp or mcp-kling server
- Test script — validate API connectivity

**Actions**:
1. `pip install higgsfield-client` — Install Higgsfield Python SDK
2. Install krea-mcp: `npm install -g @keugenek/krea-mcp` (or clone repo)
3. Add to `.mcp.json` or Claude settings
4. Write a test script that:
   - Authenticates with Higgsfield API
   - Lists existing Soul Cast characters
   - Generates one test image (simple prompt, Location mode)
   - Confirms generation completes and returns URL
5. Test Kling API via krea-mcp or direct REST call

**Validation gate**: Test image generated successfully. Character list returns @Rogers, @James, @Birch UUIDs.

#### Step 2: Create Soul Cast Characters
**What**: Build TF-COACH and TF-ATHLETE in Higgsfield
**Dependencies**: Step 1 (API working)

**Actions**:
1. Generate character reference images using Imagen 4 (Gemini MCP — already connected):
   - TF-COACH: "Athletic male fitness trainer, 30s, clean-cut, visible muscle definition, wearing black compression shirt with blue trim, dark shorts, training shoes. Professional headshot, gym setting, 4 angles: front, 3/4 left, 3/4 right, profile. Photorealistic."
   - TF-ATHLETE: "Athletic person, mid-20s, fit but approachable build, gray workout clothes, determined expression. Professional headshot, gym setting, 4 angles. Photorealistic."
2. Save reference images to `~/Desktop/Social-Media-Film-Studio/assets/characters/`
3. Create Soul Cast characters via Higgsfield API:
   - POST `/v1/characters` with reference images for TF-COACH
   - POST `/v1/characters` with reference images for TF-ATHLETE
4. Record UUIDs in the design doc

**Validation gate**: Both characters created with UUIDs. Test generation with each character shows consistent face.

#### Step 3: Generate Location Library
**What**: Create the 6 reusable location images
**Dependencies**: Step 1 (API working)

**Actions**:
1. Generate 6 locations using Higgsfield Location mode (imageMode: location-creation):
   - TF-LOC-01: The Gym Floor (industrial-modern, amber lighting, blue LED accents)
   - TF-LOC-02: The Weight Room (close-up, dumbbells, chalk dust, tungsten)
   - TF-LOC-03: The Mirror Wall (full-length mirror, clean glass, good lighting)
   - TF-LOC-04: Outdoor Training Ground (urban park, golden hour, skyline)
   - MR-LOC-01: The Home Office (modern, monitor, warm lamp, natural light)
   - MR-LOC-02: The Golden Hour (outdoor, patio/rooftop, sunset, bokeh)
2. Save all to `~/Desktop/Social-Media-Film-Studio/assets/locations/`
3. Select best generation per location (may need 2-3 attempts each)

**Validation gate**: 6 location images saved. Each looks photorealistic and matches the design spec.

**SESSION 1 CHECKPOINT**: API working, 2 characters created, 6 locations generated. Commit progress.

---

### SESSION 2: First Content (Monday March 24)
**Estimated context: HIGH (~60K tokens)**
**Files touched: ~8**

#### Step 4: Verify Viral Architect Instagram Pipeline
**What**: Confirm we can post to @rodgemd1 via Viral Architect
**Dependencies**: None (existing infrastructure)

**Actions**:
1. Navigate to `~/viral-architect-hub`
2. Read `backend/services/instagram_publisher.py` to understand the publishing interface
3. Read `.env` to confirm Instagram access token is configured for @rodgemd1
4. Check if the Supabase storage bucket `generated-assets` is accessible
5. Test the pipeline:
   - Upload a test image (simple graphic) to Supabase storage
   - Call `publish_image()` with test caption
   - Verify post appears on @rodgemd1
   - Delete test post manually
6. If Viral Architect pipeline works: use it as primary publishing path
7. If not: fall back to direct Instagram Graph API calls

**Validation gate**: Test image posted to @rodgemd1 and visible on Instagram.

#### Step 5: Produce Test Reel — "Behind the Build" (Mike's IG)
**What**: First end-to-end production. Mike at desk, cinematic, 30s reel.
**Dependencies**: Steps 1-3 (characters, locations ready), Step 4 (publishing works)
**Format**: Reel
**Pillar**: Behind the Build
**Character**: @Rogers (existing Soul Cast, UUID: 29e3722b-34de-4fe9-8652-c10b0c8670a4)
**Location**: MR-LOC-01 (The Home Office)

**Production Phases**:

**5a. Design** (creative direction):
- Tone: Warm, focused, cinematic
- Color grade: Golden warm, subtle film grain
- Aspect ratio: 9:16 (1080x1920)
- Duration: 25-30 seconds
- Audio: Lo-fi ambient beat (Suno) + subtle keyboard/mouse foley

**5b. Storyboard** (3 shots):
- Shot 1 (0-8s): Wide — Home office, @Rogers entering frame, sitting at desk. Camera slow push-in. Warm lamp light.
- Shot 2 (8-18s): Medium — Over-shoulder, code/dashboard on screen. Hands on keyboard. Focus shift from screen to hands.
- Shot 3 (18-28s): Close-up — @Rogers face, slight smile of satisfaction. Pull back to reveal full desk setup. Text overlay fades in: "Building the future, one line at a time."

**5c. Generate**:
- Generate start/end frames for each shot via Higgsfield Cinema Studio (Scenes mode, @Rogers character)
- Generate 3 video clips from frame pairs (5-10s each)
- Select best generation per shot (2-3 attempts each)
- Generate background music via Suno (30s lo-fi ambient)

**5d. Refine**:
- Quality gates: motion_quality, character_consistency, resolution
- Color grade via Higgsfield or FFmpeg LUT
- Assembly: FFmpeg concat with crossfade transitions
- Add text overlay for final shot
- Mix audio

**5e. Deliver**:
- Export to `~/Desktop/Social-Media-Film-Studio/output/mike-personal/`
- Post to @rodgemd1 via Viral Architect pipeline
- Caption: "Building the future with AI. Not just coding — creating. 🏗️ #founder #AI #building"

**Validation gate**: Reel posted to @rodgemd1. Passes the "scroll test" — looks like real footage at normal scroll speed.

---

### SESSION 3: TransformFit Content (Tuesday-Thursday, March 25-27)
**Estimated context: HIGH (~60K tokens)**
**Files touched: ~5**

#### Step 6: TransformFit Content Production (3 pieces)

**6a. Tuesday — "The Grind" (Atmosphere Reel)**
- No character needed — pure B-roll
- Tool: Higgsfield Cinema Studio (Veo 3.1 model for cinematic atmosphere)
- Shots: 4 atmospheric clips (equipment close-ups, gym lighting, chalk dust, weight rack)
- Audio: Deep bass beat (Suno), metallic gym sounds
- Duration: 20-30s
- Text overlays: "The grind doesn't stop." / TransformFit logo
- Post to @rodgemd1 as TransformFit test

**6b. Wednesday — "The Move" (Exercise Demo)**
- Character: TF-COACH
- Tool: Kling 3.0 API (best motion physics)
- Exercise: Dumbbell Bicep Curl (controlled movement — plays to AI strengths)
- Location: TF-LOC-02 (Weight Room)
- Shots: 3 angles (side wide, rear 3/4, front close-up) + 1 full rep cycle
- Audio: Gym ambient + motivational VO (ElevenLabs): "Control the negative. Feel every fiber. This is where growth happens."
- Duration: 40-50s
- Post to @rodgemd1

**6c. Thursday — "The Transformation" (Narrative Reel)**
- Characters: TF-ATHLETE (dual portrayal: "Day 1" tired vs "Day 90" strong)
- Tool: Higgsfield Cinema Studio (Soul Cast critical for consistency)
- Story arc: Alarm goes off → reluctant start → gym entrance → first workout (struggling) → TIME SKIP → confident workout → mirror check → smile
- Shots: 6 shots, 5-8s each
- Audio: Motivational beat building from quiet to powerful + VO
- Duration: 50-70s
- Post to @rodgemd1

**Validation gate per piece**: Passes scroll test, quality gates clear, posted successfully.

#### Step 7: Go Live — Friday March 28
**What**: Select best-performing content from tests, refine, and publish as first official TransformFit content.
**Dependencies**: Steps 5-6 complete

**Actions**:
1. Review engagement metrics on test posts (likes, saves, shares, reach)
2. Select highest performer
3. If needed: refine based on learnings (re-generate weak shots, adjust color, fix audio)
4. Publish refined version with full TransformFit branding
5. Write first week's content calendar for the following week
6. Set up recurring production schedule

**Validation gate**: First official TransformFit content live on @rodgemd1. Engagement rate > 2% (nano account benchmark per Viral Architect knowledge base).

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Higgsfield API returns 720p (not 1080p) | HIGH | MEDIUM | Upscale via FFmpeg or use Kling for critical shots |
| Exercise motion looks uncanny | MEDIUM | HIGH | Start with controlled movements only (curls, planks). No explosive moves. |
| Soul Cast face drifts between shots | LOW | HIGH | Generate all shots in one Cinema Studio session. Manual QA each cut. |
| Viral Architect IG token expired | MEDIUM | LOW | Refresh token. Fallback: direct Graph API. |
| Kling API queue times >5min | MEDIUM | LOW | Generate overnight. Use Higgsfield as backup. |
| Content doesn't pass scroll test | MEDIUM | HIGH | Don't publish it. Iterate. Quality > schedule. |

---

## Files We'll Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `~/Desktop/Social-Media-Film-Studio/scripts/test_higgsfield.py` | CREATE | API connectivity test |
| `~/Desktop/Social-Media-Film-Studio/scripts/generate_characters.py` | CREATE | Soul Cast character creation |
| `~/Desktop/Social-Media-Film-Studio/scripts/generate_locations.py` | CREATE | Location library generation |
| `~/Desktop/Social-Media-Film-Studio/scripts/produce_reel.py` | CREATE | End-to-end reel production |
| `~/Desktop/Social-Media-Film-Studio/scripts/publish.py` | CREATE | Publishing bridge to Viral Architect |
| `~/Desktop/Social-Media-Film-Studio/prompts/` | CREATE | Prompt templates per content pillar |
| `.mcp.json` or settings | MODIFY | Add krea-mcp or mcp-kling |
| `~/viral-architect-hub/.env` | VERIFY | Confirm IG token for @rodgemd1 |

**Total new files**: ~6 scripts + prompt templates
**Total modified files**: ~2
**Scope check**: ✅ Under 8 files. Clean scope.

---

## Session Plan Summary

| Session | When | What | Deliverable |
|---------|------|------|-------------|
| **Session 1** | Today (March 23) | Foundation: APIs, characters, locations | Working pipeline, 2 characters, 6 locations |
| **Session 2** | Monday (March 24) | First reel: Mike's "Behind the Build" | Test reel posted to @rodgemd1 |
| **Session 3** | Tue-Thu (March 25-27) | TransformFit content: 3 pieces | 3 test posts on @rodgemd1 |
| **Launch** | Friday (March 28) | Go live with best performer | First official TransformFit content |

---

## Approval Needed

Mike: Review this plan. If approved, I start executing Step 1 immediately (today).

Key question: **Do you want me to start Session 1 now (install tools, create characters, generate locations), or should we start fresh tomorrow?**

Context health is GREEN. We have runway for Session 1 today if you want to move.
