# Phase 2: Emerging & Open-Source Video AI Research

**Date**: 2026-03-23
**Researcher**: Jake (AI Co-Founder)
**Confidence**: DRAFT — based on web research, not hands-on testing
**Sources**: Brave Search, GitHub, Reddit, vendor blogs, review sites

---

## Open-Source Tools

### Wan 2.1 / 2.2 / 2.5 (Alibaba / Wan-Video)
- **Model**: DiT-based diffusion; Wan 2.2 introduces Mixture-of-Experts (MoE) architecture separating denoising across timesteps with specialized expert models; Wan 2.5 (Preview) adds native audio generation and 1080p/10s output
- **Parameters**: 1.3B (lightweight) and 14B (full quality) variants
- **Quality vs Commercial**: Exceeds 84.7% on temporal coherence benchmarks. Wan 2.1 14B produces smooth motion and consistent visual quality frame-to-frame. Wan 2.2 MoE brings notable improvements in generation quality. Community consensus: competitive with mid-tier commercial tools (Kling 2.x level), slightly below Sora 2 / Veo 3.1 for cinematic realism
- **Hardware Requirements**:
  - 1.3B model: 8GB VRAM minimum (runs on RTX 3060)
  - 14B model at 720p: 65-80GB VRAM natively (datacenter-class). Consumer workaround: Wan2GP optimizations allow 14B on 8-24GB GPUs with quality/speed tradeoffs
  - **Mac Studio**: Possible but slow. M1 Max 64GB ran Wan 2.1 14B I2V at 480x720 in ~90 minutes per 33 frames. Wan2mac fork exists (github.com/kbadri007/Wan2mac) but requires MPS backend adaptation — CUDA is default. No native Metal optimization yet.
- **Self-Host Cost Estimate**: Cloud GPU (H100 rental) ~$2-4/hr. A 5-second 720p clip takes ~2-5 min on H100 = ~$0.15-0.30/clip. For 5 reels/week (each needing ~5-10 generations for iteration): ~$5-15/week cloud cost
- **Fitness Content Suitability**: Good temporal coherence for movement, but rapid/complex human motion (burpees, jump squats) will likely show artifacts. Best for slow/controlled movements. LoRA fine-tuning available for custom styles.
- **Key Advantage**: Wan 2.5 Preview adds native audio — first open-source model with synchronized sound
- **Sources**:
  - https://github.com/Wan-Video/Wan2.1
  - https://github.com/Wan-Video/Wan2.2
  - https://github.com/deepbeepmeep/Wan2GP
  - https://github.com/kbadri007/Wan2mac
  - https://www.aiarty.com/ai-video-generator/wan-ai-video.htm

### HunyuanVideo 1.5 (Tencent)
- **Model**: Full Attention Transformer, "Dual-stream to Single-stream" hybrid design
- **Parameters**: 13B (original), 8.3B (v1.5 — lighter, consumer-friendly)
- **Quality vs Commercial**: Top-tier cinematic quality among open-source. Strong spatial/temporal consistency. Considered alongside Wan 2.2 as the best open-source options for cinematic output.
- **Hardware Requirements**: HunyuanVideo 1.5 (8.3B) runs on consumer GPUs (RTX 4090 / 16-24GB VRAM). Original 13B needs 40GB+ VRAM. On Mac M1 Max 64GB: ~30 min for 480x720 33-frame clip (faster than Wan 2.1)
- **Self-Host Cost Estimate**: Similar to Wan — $0.10-0.25/clip on cloud H100
- **Fitness Content Suitability**: Good for controlled demonstrations. Cinematic lighting quality is a strength. Motion quality comparable to Wan.
- **Key Advantage**: Tencent actively maintaining; I2V variant available; trained with Muon optimizer (open-sourced for fine-tuning)
- **Sources**:
  - https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5
  - https://huggingface.co/tencent/HunyuanVideo-1.5

### CogVideoX (Zhipu AI / Tsinghua)
- **Model**: Expert Transformer with progressive training and multi-resolution frame packing
- **Parameters**: 2B (lightweight) and 5B (quality)
- **Quality vs Commercial**: Mid-tier. Best-in-class for image-to-video among early open-source models. 5B pushes quality higher but still below Wan 2.2 / HunyuanVideo for cinematic output. Okara review: "cinematic quality not on par with HunyuanVideo or Wan 2.2"
- **Hardware Requirements**: 2B fits lighter hardware (8-12GB VRAM). 5B needs 16-24GB. One of the most accessible models.
- **Self-Host Cost Estimate**: Very cheap — runs on consumer GPUs. $0 if you own hardware, ~$0.05-0.10/clip on cloud
- **Fitness Content Suitability**: Limited — 6-second clips at 720x480 (5B). Too short for meaningful exercise demonstrations. Good for quick social media teasers only.
- **Key Advantage**: LoRA support (best ecosystem completeness among early models), good I2V quality
- **Limitation**: Resolution and duration caps are significant drawbacks vs newer models
- **Sources**:
  - https://github.com/zai-org/CogVideo
  - https://arxiv.org/abs/2408.06072

### MAGI-1 (Sand AI)
- **Model**: Autoregressive Diffusion — first of its kind for video. Generates frame-by-frame rather than all-at-once denoising.
- **Parameters**: 4.5B (planned larger versions)
- **Quality vs Commercial**: Claims state-of-the-art among open-source, surpassing Wan 2.1 in instruction following and motion quality. Particularly excels at temporal consistency due to autoregressive nature.
- **Hardware Requirements**: CUDA required. Cloud-tier GPU recommended (40GB+ VRAM). Not Mac-friendly.
- **Self-Host Cost Estimate**: Similar to Wan 14B — cloud H100 at $2-4/hr
- **Fitness Content Suitability**: POTENTIALLY STRONG — autoregressive architecture means each frame is conditioned on previous frames, which should handle sequential movements (exercise reps) better than diffusion-only models. UNVERIFIED for fitness specifically.
- **Key Advantage**: Unlimited duration via chunk-wise prompting. Smooth scene transitions. This is architecturally novel — could be a game-changer for longer-form content.
- **Sources**:
  - https://github.com/SandAI-org/MAGI-1
  - https://huggingface.co/sand-ai/MAGI-1
  - https://sand.ai/magi

### LTX-Video (Lightricks)
- **Model**: Lightweight DiT, optimized for speed
- **Parameters**: Smaller than competitors — designed for consumer hardware
- **Quality vs Commercial**: Fast but lower cinematic quality. "Close-ups often show flaws." Best for rapid prototyping, not final output.
- **Hardware Requirements**: Runs on 8-16GB VRAM. One of the most accessible models.
- **Self-Host Cost Estimate**: Near-zero on owned hardware
- **Fitness Content Suitability**: Low — quality limitations would show in human body rendering
- **Sources**: https://www.hyperstack.cloud/blog/case-study/best-open-source-video-generation-models

### SkyReels V1 (Kunlun)
- **Model**: Hybrid Stream DiT with advanced motion modeling
- **Parameters**: Large — cloud/enterprise tier
- **Quality vs Commercial**: Up to 1080p with strong spatial/temporal consistency. Top-tier among open-source for motion quality.
- **Hardware Requirements**: 40GB+ VRAM (cloud/enterprise)
- **Fitness Content Suitability**: Potentially good for motion — advanced motion modeling is a differentiator
- **Sources**: https://www.hyperstack.cloud/blog/case-study/best-open-source-video-generation-models

### Mochi 1 (Genmo)
- **Model**: Diffusion-based, optimized for text-to-video
- **Quality vs Commercial**: Best text-to-video quality among early open-source models (per community comparisons). Strong prompt following.
- **Hardware Requirements**: 40GB+ VRAM
- **Fitness Content Suitability**: Unknown for fitness specifically
- **Sources**: https://www.reddit.com/r/comfyui/comments/1h6lwe9/comparison_of_opensource_video_generation_models/

---

## Emerging Commercial Tools

### Seedance 2.0 (ByteDance)
- **Launch Date**: February 2026
- **Key Innovation**: Native audio generation, 2K resolution, 15s duration. 80% cheaper than Sora 2. Called "strongest video model" by multiple reviewers.
- **Quality Assessment**: Competitive with Kling 3.0 and approaching Sora 2 quality at a fraction of the cost. Character consistency and style transfer are strong.
- **Pricing**: ~$0.022/sec (Fast mode), ~$0.247/sec (Pro). Premium tier ~$9.60/month (69 RMB via Jimeng). Free daily credits on Dreamina platform.
- **API Access**: Yes — BytePlus API with 2M free tokens. Third-party providers offer ~$0.05 per 5-second 720p video.
- **Fitness Content Suitability**: Good motion quality. Worth testing for exercise demos.
- **Sources**:
  - https://soravideo.art/blog/seedance-2-pricing
  - https://kingsankalpa.com/blog/seedance-2-vs-sora-2-ai-video-pricing-war/

### Kling 3.0 (Kuaishou)
- **Launch Date**: Q1 2026
- **Key Innovation**: Native 4K output at 60fps. 15-second duration. Multi-shot storyboarding (up to 6 cuts). Native audio-visual sync with character-specific speech, bilingual dialogue, lip-sync. Pixel-level regional inpainting. Precise text rendering.
- **Quality Assessment**: Major leap. "New King of AI Video Generators" per Curious Refuge. Cinematic physics including gymnastics and water simulation. Strong lighting, textures, "film-like" output.
- **Pricing**: $0.084-$0.126/sec (Standard), $0.112-$0.168/sec (Pro)
- **API Access**: Yes
- **Fitness Content Suitability**: HIGH POTENTIAL — specifically mentions "realistic simulation of complex motions including gymnastics." 4K/60fps would produce Instagram-quality fitness content. Character consistency across scenes is critical for exercise series.
- **Sources**:
  - https://kling3.net/blog/kling-3-features-guide
  - https://curiousrefuge.com/blog/kling-30-review
  - https://ir.kuaishou.com/news-releases/news-release-details/kling-ai-launches-30-model-ushering-era-where-everyone-can-be

### Veo 3.1 (Google DeepMind)
- **Launch Date**: Late 2025 / Early 2026
- **Key Innovation**: Extended duration, atmospheric scenes, large-scale motion. Strong lighting and environmental rendering.
- **Quality Assessment**: One of the top 3 models overall. "Most balanced and consistent" per letsenhance.io testing. Occasionally struggles with ultra-realistic human motion.
- **Pricing**: Available via Higgsfield and other platforms. Google's own pricing through Vertex AI.
- **API Access**: Via Google Cloud Vertex AI
- **Fitness Content Suitability**: MODERATE — great for atmospheric/lifestyle fitness content (gym environments, outdoor workouts) but human motion is occasional weakness
- **Sources**:
  - https://letsenhance.io/blog/all/best-ai-video-generators/
  - https://artsmart.ai/blog/top-ai-video-tools-2026/

### Sora 2 (OpenAI)
- **Launch Date**: 2025, iterating through 2026
- **Key Innovation**: Depth and realism, strong physics simulation, up to 20 seconds, 1080p
- **Quality Assessment**: Top-tier for cinematic depth and physical accuracy. Industry benchmark.
- **Pricing**: ~$0.15/sec. Requires ChatGPT Plus ($20/month) for limited access, or $200/month for advanced.
- **API Access**: Limited
- **Fitness Content Suitability**: Good physics but expensive for volume content creation
- **Sources**: https://www.atlascloud.ai/blog/guides/seedance-2-vs-sora-2-vs-kling-3-comparison

### Runway Gen-4.5
- **Launch Date**: March 2026
- **Key Innovation**: #1 on Artificial Analysis Text-to-Video benchmark (1,247 Elo). Dynamic/controllable action generation. Also introduced GWM-1 (General World Model) for real-time interactive simulation.
- **Quality Assessment**: Best text-to-video quality available to consumers per multiple reviews. Exceptional motion and physical accuracy.
- **Pricing**: Standard plan $12-15/month (625 credits). 5-second Gen-4.5 clip = ~25 credits. Pro plans scale up.
- **API Access**: Yes (Runway API)
- **Fitness Content Suitability**: Strong motion accuracy. But capped at 720p resolution — may not cut it for high-quality Instagram content.
- **Sources**:
  - https://runwayml.com/research/introducing-runway-gen-4.5
  - https://runwayml.com/pricing

### Luma Ray3 / Ray 3.14 (Luma Labs)
- **Launch Date**: Late 2025, Ray 3.14 in early 2026
- **Key Innovation**: First-to-market HDR pipeline (10/12/16-bit ACES2065-1 EXR). Reasoning-driven generation. Draft Mode for rapid exploration. Keyframe editing. Ray3 Modify for video-to-video with natural language editing.
- **Quality Assessment**: Production-grade fidelity. HDR output suitable for high-end film/advertising pipelines. Strong consistency and creative control.
- **Pricing**: Free and paid tiers via Dream Machine. Also integrates Sora 2, Veo 3, Kling, Seedance in paid plans.
- **API Access**: Yes
- **Fitness Content Suitability**: MODERATE-HIGH — Draft Mode is great for rapid iteration. HDR overkill for social media but quality headroom is nice. Ray3 Modify could edit real workout footage with AI enhancements.
- **Sources**:
  - https://lumalabs.ai/ray
  - https://lumalabs.ai/press/ray3

### PixVerse V5.5 (PixVerse)
- **Launch Date**: 2026 (iterating)
- **Key Innovation**: Multi-shot cinematic videos, hyperrealistic visuals, audio integration, pixel-perfect control. Trending social effects (AI Kiss, Hug, Muscle).
- **Quality Assessment**: Consumer-focused, viral-optimized. Good for social media trends.
- **Pricing**: Available via Pollo AI platform (multi-model hub)
- **Fitness Content Suitability**: The "Muscle" effect and social-first design make this interesting for fitness Instagram content specifically
- **Sources**: https://app.pixverse.ai

---

## Higgsfield Deep Dive

### What Higgsfield Actually Is
Higgsfield is NOT a model company — it is a **multi-model orchestration platform**. Think of it as a unified workspace that provides access to multiple leading AI video models with professional production controls layered on top.

### Models Available on Higgsfield (as of March 2026)
- **Sora 2** (OpenAI) — cinematic depth, physics, consistency
- **Veo 3.1** (Google) — atmospheric scenes, large-scale motion
- **Kling 3.0** (Kuaishou) — lip-sync, character control, 4K
- **Kling 2.5 Turbo** — faster generation
- **Wan 2.2 / 2.5** (Alibaba) — open-source quality option
- **Seedance Pro** (ByteDance)
- **MiniMax Hailuo 02**
- **Runway models**
- **Nano Banana / Nano Banana Pro** — UNVERIFIED, likely Higgsfield proprietary
- **DOP models** — UNVERIFIED, appears to be Higgsfield's own cinematic model

### Cinema Studio 2.5 Features
- **Soul Cast**: Consistent, directable characters (up to 3) across scenes. Character consistency is baked into the workflow from frame one.
- **Camera Controls**: Full 3D directing — camera body, lens type, focal length selection to define visual physics of each shot
- **Workflow**: Visual reference upload -> camera rig setup -> batch preview generation (21:9 stills) -> animate to video
- **Soul ID System**: Character identity preservation across formats and scenes

### Cosmos Studio
- UNVERIFIED — limited public information. Appears to be a higher-level production environment within Higgsfield, but details are sparse.

### Community Reception
- Positive reception for Cinema Studio's professional controls (camera simulation, character consistency)
- Viewed as the best "director's toolkit" among AI video platforms
- Pricing: $9-$119/month across tiers
- Reddit community (r/HiggsfieldAI) is active but small
- Criticism: credit consumption can be high, especially with Sora 2 / Veo 3.1 models

### Verdict on Higgsfield
It is a **platform play, not a model play**. The value is in the production controls and multi-model access. For fitness content, the Soul Cast feature (character consistency) is extremely valuable — you could create a consistent AI fitness instructor across dozens of clips. The camera controls add production value that standalone model APIs do not provide.

---

## Fitness Content Generation Analysis

### Dedicated Fitness Video AI Tools

#### Hyperhuman (hyperhuman.cc)
- **What It Is**: AI-powered Fitness OS specifically for workout video creation
- **How It Works**: NOT generative AI video — it is an AI-assisted editing/assembly platform. You upload raw trainer footage, AI extracts and labels exercises, then auto-assembles workout videos.
- **Key Features**: Smart Video Library, AI Workout Builder, text-to-speech voiceovers, 2,000+ premium stock exercise clips, Wix integration
- **API Available**: Yes — full Content API with free tier. AI-generated workouts, personalization, exercise video library.
- **Pricing**: API-based with free tier
- **Verdict**: DIFFERENT category than generative AI. This is for trainers who have footage and want to scale content production. Not for creating AI-generated exercise demos from scratch.
- **Sources**: https://hyperhuman.cc/

#### HeyGen Exercise Demo Maker
- **What It Is**: AI avatar-based exercise demo videos
- **How It Works**: Choose an AI avatar, it "demonstrates" exercises. Text-to-video from script. Dynamic personalization.
- **Limitation**: AI avatars are NOT doing real exercises — they are presenting/talking about exercises. This is for explainer videos, not exercise demonstrations.
- **Sources**: https://www.heygen.com/video/exercise-demo-video-maker

#### ImagineArt Workout Video Generator
- **What It Is**: Generative AI workout clips from prompts or reference images
- **How It Works**: Describe the exercise or upload reference image, AI generates fitness clips
- **Quality**: UNVERIFIED for actual exercise motion quality
- **Sources**: https://www.imagine.art/features/ai-workout-video-generator

#### VO3 AI Fitness Video Maker
- **What It Is**: Multi-model fitness video generation (uses Veo3, Seedance, 10+ models)
- **How It Works**: Generates gym/workout visuals with synchronized audio (clanking weights, breathing). 1080p cinematic in 41 seconds via Seedance.
- **Fitness Focus**: Pump-up reels, exercise form demos, transformation clips, gym branding
- **Sources**: https://www.vo3ai.com/ai-fitness-video-maker

### The Motion Quality Problem for Fitness Content

**Current State of AI + Human Motion (March 2026):**
1. **Slow/controlled movements** (yoga, stretching, planks): VIABLE with top models (Kling 3.0, Sora 2, Veo 3.1)
2. **Moderate movements** (bicep curls, squats, lunges): MOSTLY VIABLE but watch for joint artifacts
3. **Rapid/explosive movements** (burpees, box jumps, sprints): STILL PROBLEMATIC — temporal consistency breaks down with fast limb movement
4. **Repetitive movements** (sets of reps): CHALLENGING — models struggle with consistent repetitive motion over time

**Best Models for Human Motion Quality (ranked):**
1. **Kling 3.0** — specifically mentions gymnastics simulation, strong body physics
2. **Sora 2** — excellent physics but expensive
3. **Veo 3.1** — "occasionally struggles with ultra-realistic human motion"
4. **MAGI-1** — autoregressive architecture theoretically best for sequential/repetitive motion (UNVERIFIED)
5. **Wan 2.2/2.5** — good temporal coherence but not motion-specialized

**Recommendation for Fitness Content (March 2026):**
- Use Kling 3.0 for the actual exercise demonstration clips
- Use Hyperhuman or manual editing for assembly into full workout videos
- Use Higgsfield Cinema Studio for consistent character across a content series
- Supplement with real trainer footage for explosive/rapid movements — AI is not there yet

---

## Self-Host vs API Cost Comparison

### Scenario: 5 Instagram Reels per Week (each 15-30 seconds)

Assumptions:
- Each reel needs ~5-10 generation iterations to get right
- Each iteration = ~5 seconds of video
- Total: ~25-50 generations per week = 125-250 seconds of raw AI video

### Option A: Self-Hosted Open Source (Cloud GPU)

| Component | Cost |
|-----------|------|
| H100 rental (RunPod/Lambda) | $2-4/hr |
| Time per 5s clip (Wan 2.2 14B) | ~2-5 min |
| Weekly GPU time (50 clips) | ~2.5-4 hrs |
| **Weekly cost** | **$5-16** |
| **Monthly cost** | **$20-65** |

Additional: Model download bandwidth, storage, setup time. Requires ML engineering knowledge.

### Option B: Self-Hosted Open Source (Mac Studio M2 Ultra 192GB)

| Component | Cost |
|-----------|------|
| Hardware (one-time) | $5,000-8,000 |
| Per-clip generation time | ~30-90 min (480-720p) |
| Weekly generation time | ~25-75 hours |
| Electricity | ~$2-5/week |
| **Weekly ongoing cost** | **$2-5** |
| **Break-even vs cloud** | **~6-12 months** |

Verdict: TOO SLOW for production use. A 5-second clip taking 30-90 min is not viable for iterative content creation.

### Option C: Commercial API (Seedance 2.0 — Best Value)

| Component | Cost |
|-----------|------|
| Per 5s clip (720p Fast) | ~$0.05-0.11 |
| 50 clips/week | $2.50-5.50 |
| **Monthly cost** | **$10-22** |
| Monthly subscription (premium features) | $9.60 |
| **Total monthly** | **$20-32** |

### Option D: Commercial API (Kling 3.0 — Best Quality for Fitness)

| Component | Cost |
|-----------|------|
| Per 5s clip (Standard) | ~$0.42-0.63 |
| 50 clips/week | $21-31.50 |
| **Monthly cost** | **$84-126** |

### Option E: Higgsfield (Multi-Model + Production Tools)

| Component | Cost |
|-----------|------|
| Subscription | $9-119/month |
| Access to Sora 2, Veo 3.1, Kling 3.0, etc. | Included (credit-based) |
| Cinema Studio + Soul Cast | Included on higher tiers |
| **Monthly cost** | **$29-119** (depending on volume) |

### Cost Comparison Summary

| Approach | Monthly Cost | Quality | Speed | Fitness Suitability |
|----------|-------------|---------|-------|-------------------|
| Self-host cloud (Wan 2.2) | $20-65 | High | Fast | Good |
| Self-host Mac Studio | $2-5 ongoing | Medium | VERY SLOW | Poor (too slow to iterate) |
| Seedance 2.0 API | $20-32 | High | Fast | Good |
| Kling 3.0 API | $84-126 | Highest | Fast | Best |
| Higgsfield platform | $29-119 | Highest (multi) | Fast | Best (character consistency) |
| Runway Gen-4.5 | $12-45 | Highest | Fast | Good (720p cap) |

**Winner for fitness social media content: Higgsfield ($29-59/month tier) or Kling 3.0 direct API if budget allows.**
**Budget winner: Seedance 2.0 at ~$20-32/month for surprisingly good quality.**

---

## Dark Horse Recommendations

### 1. MAGI-1 (Sand AI) — The Architectural Innovator
**Why it is a dark horse**: Autoregressive generation means each frame knows about all previous frames. This is architecturally superior for sequential, repetitive content like exercise demonstrations. While current quality is competitive with Wan 2.1, the fundamental approach could leapfrog diffusion-based models for fitness content specifically. Watch for their larger model releases.

### 2. Wan 2.5 (Alibaba) — The Open-Source Kingmaker
**Why it is a dark horse**: Preview already showing major quality jumps + native audio. If weights are released as open-source, this becomes the first open model with synchronized sound. Combined with Wan2GP optimizations for consumer hardware, this could make self-hosted production viable. VRAM requirements are "significantly more" than 2.2 though — likely 48GB+ minimum.

### 3. Hyperhuman + Kling 3.0 Hybrid Workflow
**Why it is a dark horse**: Use Kling 3.0 to generate individual exercise clips (leveraging its gymnastics-grade motion physics), then use Hyperhuman's AI Workout Builder to assemble them into branded workout videos with voiceovers, transitions, and personalization. This hybrid approach could produce the highest quality fitness content at scale.

### 4. Seedance 2.0 (ByteDance) — The Price Destroyer
**Why it is a dark horse**: At $0.05 per 5-second clip via third-party APIs, this is 100x cheaper than Sora 2 at equivalent resolution. ByteDance's motion AI (from TikTok's recommendation engine heritage) means they understand social media content generation at a fundamental level. The free daily credits on Dreamina make this zero-risk to test.

### 5. DeepMotion — The Motion Capture Angle
**Why it is a dark horse**: Instead of generating exercise videos from scratch, DeepMotion converts regular video to 3D animation via AI motion capture. A trainer could record a workout on their phone, and DeepMotion extracts the 3D motion data. This could feed into video generation models as motion guidance — creating a "real motion, AI visuals" pipeline.

### 6. Pollo AI — The Multi-Model Hub
**Why it is a dark horse**: Aggregates Kling, Hailuo, PixVerse, Runway, Luma, Vidu, Pika, Seaweed, and their own Pollo 2.5 model in one platform. Free tier available. For someone who wants to test multiple models without managing separate subscriptions, this is the laziest path to finding what works for fitness content.

---

## Key Takeaways

1. **Open-source is 6-12 months behind commercial** for quality, but the gap is closing fast. Wan 2.5 (if open-sourced) could narrow it to 3-6 months.

2. **Mac Studio self-hosting is NOT viable** for production video generation in 2026. Generation times of 30-90 minutes per 5-second clip make iterative content creation impractical. Cloud GPUs or commercial APIs are the way.

3. **Kling 3.0 is the best model for fitness content** due to explicit gymnastics/motion physics capabilities, 4K/60fps output, and character consistency.

4. **Higgsfield is the best platform** for production-quality social media content — multi-model access + Cinema Studio + Soul Cast character consistency.

5. **Seedance 2.0 is the budget play** — test with free credits, scale at $0.05/clip. ByteDance's social-media DNA makes this surprisingly good for the price.

6. **No AI tool currently handles explosive/rapid exercise movements well.** Plan hybrid workflows: AI for controlled movements + real footage for explosive movements.

7. **The fitness-specific tools (Hyperhuman, HeyGen) are assembly/editing tools**, not generative AI. They complement but do not replace video generation models.
