# Social Media Film Studio — Design Document

**Date**: 2026-03-23
**Status**: DESIGN (awaiting approval before build)
**Target**: Go live Friday March 28, 2026
**Confidence**: DRAFT

---

## 1. Studio Identity

**Name**: Viral Architect — Film Studio
**Mission**: Produce ultra-realistic AI-generated video content for TransformFit and Mike's personal Instagram that is indistinguishable from professionally shot footage.

**Design Principle**: "If someone has to zoom in to tell it's AI, we've won."

---

## 2. Content Tracks

### Track A: TransformFit (@transformfit_ai)

**Brand Voice**: Motivational but not cheesy. Think Nike meets science. Clean, powerful, aspirational.

**Visual Language**:
- Color palette: Deep blacks, electric blue (#0066FF) accents, warm skin tones, gym amber lighting
- Aspect ratio: 9:16 (Reels primary), 1:1 (feed posts)
- Resolution: 1080x1920 minimum
- Frame rate: 30fps (matches phone-shot feel — 60fps looks "too smooth" per Reddit)
- Color grade: High contrast, slightly desaturated backgrounds, warm highlights on skin
- Typography: Bold sans-serif (Montserrat or Inter), white with subtle drop shadow

**Content Pillars** (rotating weekly):

| Pillar | Format | Description | Generation Strategy |
|--------|--------|-------------|-------------------|
| **The Move** | Reel (30-60s) | Single exercise demo, perfect form, multiple angles | Kling 3.0 (best motion physics) |
| **The Transformation** | Reel (60-90s) | Before/after narrative, cinematic mini-story | Higgsfield Cinema Studio (Soul Cast for consistency) |
| **The Science** | Carousel (5-8 slides) | Exercise science explainer, clean infographics | Image gen + typography |
| **The Grind** | Reel (15-30s) | Gym atmosphere, aesthetic B-roll, motivational | Higgsfield (Veo 3.1 model for atmosphere) |
| **The Quote** | Image (1:1) | Motivational quote over cinematic gym background | Image gen + brand template |

**Weekly Cadence** (5 posts/week):
- Monday: The Move (exercise demo reel)
- Tuesday: The Science (carousel)
- Wednesday: The Grind (atmosphere reel)
- Thursday: The Transformation (story reel)
- Friday: The Quote (image post)

### Track B: Mike's Personal IG (@mikerodgers)

**Brand Voice**: Authentic founder journey. Real but elevated. Cinematic lifestyle with substance.

**Visual Language**:
- Color palette: Warm earth tones, golden hour, rich blacks, natural greens
- Aspect ratio: 9:16 (Reels), 4:5 (feed posts)
- Resolution: 1080x1920
- Color grade: Warm, slightly filmic, subtle grain (Kodak Portra feel)
- Typography: Clean serif (Playfair Display) for quotes, sans-serif for captions

**Content Pillars**:

| Pillar | Format | Description | Generation Strategy |
|--------|--------|-------------|-------------------|
| **Behind the Build** | Reel (30-60s) | Building companies with AI — founder journey | Higgsfield Cinema Studio |
| **The Life** | Reel (15-30s) | Lifestyle moments, family vibes, real + AI hybrid | Kling 3.0 + real footage |
| **Founder Wisdom** | Carousel (3-5 slides) | Lessons learned, decision frameworks | Image gen + clean design |
| **The Vision** | Reel (60-90s) | Cinematic "what we're building" narrative | Higgsfield (full Cinema Studio production) |

**Weekly Cadence** (3-4 posts/week):
- Monday: Behind the Build (reel)
- Wednesday: Founder Wisdom (carousel)
- Friday: The Life or The Vision (reel)
- Sunday (optional): Reflection post (image)

---

## 3. Soul Cast Character System

### TransformFit Characters

#### TF-COACH (Primary Character)
- **Role**: TransformFit's AI fitness coach / brand face
- **Look**: Athletic male, 30s, clean-cut, visible muscle definition but not bodybuilder
- **Wardrobe**: Black compression shirt with subtle blue trim (TransformFit brand), dark athletic shorts, training shoes
- **Personality**: Confident, focused, approachable. Think "the trainer everyone wants"
- **Expression baseline**: Determined focus during exercises, warm smile during rest/transitions
- **Reference images needed**: 3-5 athletic male reference photos (various angles, gym setting)
- **Higgsfield UUID**: TBD (create in Soul Cast)

#### TF-ATHLETE (Secondary Character)
- **Role**: "The Client" — shows transformation journey, follows TF-COACH
- **Look**: Athletic male or female, mid-20s, relatable build (fit but not intimidating)
- **Wardrobe**: Gray/neutral workout clothes (contrast with coach's black)
- **Personality**: Eager, determined, slightly uncertain at first → confident by end
- **Reference images needed**: 3-5 reference photos
- **Higgsfield UUID**: TBD

### Mike's Personal IG Characters

#### MIKE (Primary Character)
- **Role**: Mike Rodgers — founder, builder, family man
- **Look**: Mike's actual likeness (reference photos from real life)
- **Wardrobe**: Casual-professional (clean tee or henley, well-fitted jeans/joggers, nice watch)
- **Personality**: Thoughtful, driven, warm
- **Reference images needed**: 5-8 photos of Mike (headshot, casual, working, lifestyle)
- **Higgsfield UUID**: Can reuse existing @Rogers (29e3722b-34de-4fe9-8652-c10b0c8670a4) if likeness matches, or create new

### Asset Requirements Checklist

**What Mike needs to provide:**
- [ ] 3-5 photos for TF-COACH character (or approve AI-generated reference)
- [ ] 3-5 photos for TF-ATHLETE character (or approve AI-generated reference)
- [ ] 5-8 photos of Mike for personal IG character
- [ ] TransformFit logo (PNG, transparent background)
- [ ] Any existing brand guidelines or color preferences
- [ ] Gym/location reference photos (or approve AI-generated locations)
- [ ] Any real workout footage clips (for hybrid content)

**What we generate:**
- [ ] Location library (6 locations — see Section 4)
- [ ] Character reference sheets (multiple angles per character)
- [ ] Brand template overlays (caption safe zones, logo placement)
- [ ] Music/audio library curation

---

## 4. Location Library

Each location is generated once in Higgsfield (Location mode) and reused across productions for visual consistency.

### TransformFit Locations

| Location ID | Name | Description | Use In |
|-------------|------|-------------|--------|
| TF-LOC-01 | **The Gym Floor** | Industrial-modern gym interior. Exposed brick walls, matte black equipment, amber overhead lighting, rubber flooring. Clean and minimal — not cluttered. Blue LED accent strips along ceiling edges. | The Move, The Grind |
| TF-LOC-02 | **The Weight Room** | Close-up environment. Rack of dumbbells, bench press, squat rack. Shallow depth of field. Warm tungsten overhead. Chalk dust particles visible in light beams. | The Move (close-up shots) |
| TF-LOC-03 | **The Mirror Wall** | Full-length gym mirror section. Clean glass, good lighting for form checks. Character reflected in mirror (dual angle). | The Transformation |
| TF-LOC-04 | **Outdoor Training Ground** | Urban outdoor gym or park workout area. Dawn/golden hour lighting. City skyline in soft background. Pull-up bars, open space. | The Grind, variety shots |

### Mike's Personal IG Locations

| Location ID | Name | Description | Use In |
|-------------|------|-------------|--------|
| MR-LOC-01 | **The Home Office** | Clean, modern home office. Large monitor showing code/dashboards. Warm desk lamp, plant, coffee. Books on shelf. Window with natural light. | Behind the Build |
| MR-LOC-02 | **The Golden Hour** | Outdoor lifestyle — patio, park, or rooftop at golden hour. Warm, cinematic. Bokeh background. | The Life, The Vision |

---

## 5. Production Pipeline (Technical Architecture)

### Generation Routing (Updated from Research)

| Content Type | Primary Tool | Fallback | Why |
|-------------|-------------|----------|-----|
| Exercise demos (controlled) | Kling 3.0 API | Higgsfield (Kling model) | Best motion physics, 3-min clips |
| Exercise demos (explosive) | Real footage | Kling 3.0 (test first) | AI not reliable for rapid motion yet |
| Cinematic narrative | Higgsfield Cinema Studio | Runway Gen-4.5 | Soul Cast + camera controls |
| Atmosphere/B-roll | Higgsfield (Veo 3.1 model) | Kling 3.0 | Best cinematic polish |
| Character close-ups | Higgsfield Cinema Studio | Runway Act-Two | Soul Cast face consistency |
| Location establishing | Higgsfield Location mode | Kling 3.0 | Consistent location library |
| Still images/graphics | Imagen 4 (via Gemini MCP) | Flux/Ideogram | Already connected |
| Audio/music | ElevenLabs + Suno | Licensed stock | VO + custom music |
| Captions/text | CapCut or FFmpeg | Manual | Auto-caption |

### Tool Stack

```
┌───────────────────────────────────────────────────────┐
│ ORCHESTRATION: Claude Code (Jake)                      │
│  Skills: /produce, film-production                     │
│  MCP: krea-mcp (multi-model), mcp-kling (Kling deep)  │
│  SDK: higgsfield-client (Python)                       │
├───────────────────────────────────────────────────────┤
│ GENERATION                                             │
│  ┌─────────────────┐ ┌──────────────┐ ┌─────────────┐│
│  │ Higgsfield      │ │ Kling 3.0    │ │ Gemini      ││
│  │ Cinema Studio   │ │ Direct API   │ │ Imagen 4    ││
│  │ - Soul Cast     │ │ - Motion     │ │ - Stills    ││
│  │ - Multi-model   │ │ - 3-min clip │ │ - Already   ││
│  │ - Camera ctrl   │ │ - 4K/60fps   │ │   connected ││
│  │ - Color grade   │ │ - mcp-kling  │ │             ││
│  └─────────────────┘ └──────────────┘ └─────────────┘│
├───────────────────────────────────────────────────────┤
│ POST-PRODUCTION                                        │
│  FFmpeg: trim, transitions, audio mix, format convert  │
│  CapCut/Vizard: captions, text overlays                │
│  Higgsfield Nano Banana Pro: color grading             │
├───────────────────────────────────────────────────────┤
│ DELIVERY                                               │
│  Instagram Graph API → @transformfit_ai                │
│  Instagram Graph API → @mikerodgers                    │
│  Buffer/Later → scheduling                             │
│  ~/Desktop/Social-Media-Film-Studio/output/ → archive  │
└───────────────────────────────────────────────────────┘
```

### Workflow Per Reel (The Move — Exercise Demo)

```
Step 1: BRIEF
  Input: "Dumbbell Romanian Deadlift — 3 angles, perfect form"
  Output: Creative direction (camera angles, timing, mood)

Step 2: STORYBOARD
  Shot 1: Wide angle, full body, side view (5s)
  Shot 2: Medium, rear 3/4 angle, focus on hamstrings (5s)
  Shot 3: Close-up, hands gripping dumbbell, slow descent (5s)
  Shot 4: Wide, front angle, full rep cycle (10s)

Step 3: GENERATE
  Tool: Kling 3.0 API (best motion physics)
  Character: TF-COACH (Soul Cast reference fed as image input)
  Location: TF-LOC-02 (Weight Room)
  Generate: 4 clips, 3 iterations each = 12 API calls
  Duration: 5-10s per clip
  Cost: ~$5-8 total

Step 4: REFINE
  Quality gates: motion_quality, character_consistency, resolution
  Color grade: Apply TransformFit grade (high contrast, blue accent)
  Assembly: FFmpeg concat with 0.5s crossfade transitions
  Audio: Gym ambient + motivational beat (Suno or licensed)
  Captions: Exercise name, rep count, form cues

Step 5: DELIVER
  Export: 1080x1920, H.264, 30fps, AAC audio
  Output: ~/Desktop/Social-Media-Film-Studio/output/transformfit/
  Post: Instagram Reel with caption + hashtags
```

---

## 6. First Week Content Slate (March 24-28)

### Pre-Production (Today, March 23)
- [ ] Mike provides character reference photos
- [ ] Create TF-COACH Soul Cast character in Higgsfield
- [ ] Generate location library (4 TF + 2 MR locations)
- [ ] Install Higgsfield Python SDK
- [ ] Install krea-mcp or mcp-kling
- [ ] Test API connection with a simple generation

### Test Day (Monday March 24)
**Mike's Personal IG — Test Post**

| | Details |
|---|---|
| Format | Reel (30s) |
| Pillar | Behind the Build |
| Concept | "Building the future with AI" — Mike at desk, cinematic zoom-in, code on screen, transition to product vision |
| Tool | Higgsfield Cinema Studio (existing @Rogers character) |
| Shots | 3 shots: wide office → medium Mike working → close-up screen with code |
| Goal | Test full pipeline end-to-end. Post to Mike's IG. Gauge quality. |

### Production Days (Tuesday-Thursday)

**Tuesday March 25 — TransformFit Test**

| | Details |
|---|---|
| Format | Reel (30s) |
| Pillar | The Grind |
| Concept | Gym atmosphere reel — moody lighting, equipment close-ups, chalk dust, weights racking. No character needed (B-roll style). |
| Tool | Higgsfield (Veo 3.1 model for cinematic atmosphere) |
| Goal | Test TransformFit visual language without needing character references yet |

**Wednesday March 26 — First Exercise Demo**

| | Details |
|---|---|
| Format | Reel (45s) |
| Pillar | The Move |
| Concept | Dumbbell Bicep Curl — controlled movement, 3 angles, perfect form |
| Tool | Kling 3.0 API (best motion for exercise) |
| Character | TF-COACH (if ready) or generic athletic figure |
| Goal | Test exercise motion quality. This is the hardest content type. |

**Thursday March 27 — Transformation Story**

| | Details |
|---|---|
| Format | Reel (60s) |
| Pillar | The Transformation |
| Concept | "Day 1 vs Day 90" — cinematic mini-story of someone starting their fitness journey |
| Tool | Higgsfield Cinema Studio (Soul Cast for character consistency across scenes) |
| Goal | Test multi-scene character consistency — the core TransformFit narrative format |

### Launch Day (Friday March 28)

**Best-performing test content gets refined and published as the official first TransformFit post.**

Decision framework:
- If Tuesday's atmosphere reel tested well → publish a refined version
- If Wednesday's exercise demo looked realistic → lead with that (higher impact)
- If Thursday's transformation story has good consistency → that's the flagship

---

## 7. Quality Standards

### The "Scroll Test"
Every piece of content must pass this: **"Would someone scrolling Instagram at normal speed think this was filmed with a phone or professional camera?"**

If the answer is no — if it looks obviously AI — it doesn't ship. Period.

### Specific Quality Bars

| Quality Dimension | Minimum Standard | How We Check |
|---|---|---|
| **Motion realism** | No jitter, no floating, natural weight | Frame-by-frame review of key joints |
| **Face consistency** | Same face across all shots in a reel | Side-by-side Soul Cast reference comparison |
| **Lighting** | Consistent direction, no impossible shadows | Single light source per scene, verified |
| **Skin tone** | Natural, no wax/plastic look | Compare to real fitness photography |
| **Clothing** | No morphing, consistent throughout | Check seams, logos, wrinkles frame-by-frame |
| **Background** | No warping, no suddenly appearing objects | Stabilize and review background layer |
| **Text/graphics** | Crisp, readable, brand-compliant | Template overlay verification |
| **Audio** | Clean, mixed properly, synced | Listen without video to check quality |

### Kill Criteria (immediate redo)
- Extra or missing fingers/limbs
- Face morphing or identity shift mid-clip
- Gravity-defying objects or movements
- Text that's unreadable or garbled
- Uncanny valley facial expressions
- Equipment clipping through body
- Background objects warping or teleporting

---

## 8. Cost Projection

### Monthly Budget (Steady State)

| Item | Cost/mo | Notes |
|------|---------|-------|
| Higgsfield Pro/Ultimate | $29-49 | Soul Cast + Cinema Studio + multi-model |
| Kling 3.0 API (supplemental) | $40-80 | Exercise demos, 3-min clips |
| Gemini (Imagen 4 for stills) | ~$5-10 | Already included in existing API budget |
| Suno/ElevenLabs (audio) | $10-20 | Music + occasional VO |
| Buffer or Later (scheduling) | $0-15 | Free tier may suffice initially |
| **Monthly Total** | **$85-175** | |

### Content Output at This Budget
- TransformFit: 5 posts/week = 20/month
- Mike's IG: 3-4 posts/week = 12-16/month
- **Total: 32-36 pieces of content/month**
- **Cost per piece: ~$2.50-5.50**

For reference: A single professional fitness video shoot costs $500-2,000. We're producing 32+ pieces for under $175.

---

## 9. Future Capabilities (Post-Launch)

### Week 2-4 (April)
- Refine prompts based on engagement data
- Build prompt template library for repeatable content types
- Add TF-ATHLETE character for two-person scenes
- Experiment with Seedance 2.0 when API launches

### Month 2 (May)
- A/B test different visual styles per pillar
- Build content calendar automation (scheduled tasks)
- Add TikTok as secondary platform
- Explore hybrid workflow: real footage + AI enhancement

### Month 3+ (June)
- Full automation: content calendar → generation → review → publish
- Analytics dashboard tracking engagement per content type
- Multi-brand expansion (Alex Recruiting content?)
- Explore long-form content (YouTube documentary style)

---

## 10. Decisions (LOCKED — March 23, 2026)

| # | Decision | Answer | Notes |
|---|----------|--------|-------|
| 1 | TF Characters | **AI-generated faces** | Full creative control, no likeness rights needed |
| 2 | Mike's likeness | **Yes — use real photos + full Soul Cast** | Existing @Rogers character + Mike's real photos |
| 3 | Audio | **Voiceover narration on TransformFit reels** | ElevenLabs for VO + Suno for music |
| 4 | Budget | **$85-175/mo approved** | Upper end comfortable |
| 5 | Test account | **Main account: @rodgemd1** | Connected via Viral Architect API to Instagram |
| 6 | Approval flow | **Jake auto-publishes after quality gates** | Mike reviews post-publish, flags issues |

### Instagram Integration
- **Account**: @rodgemd1
- **Integration**: Viral Architect app has existing Instagram API connection
- **Repo**: Viral Architect (check for Instagram Graph API integration)
- **Fallback**: Direct Instagram Graph API if Viral Architect integration isn't ready
