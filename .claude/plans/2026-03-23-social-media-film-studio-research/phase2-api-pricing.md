# Phase 2: API, SDK & Pricing Research

**Date**: 2026-03-23
**Status**: COMPLETE
**Confidence**: DRAFT (pricing changes frequently; verify before committing budget)

---

## Tool-by-Tool Technical Details

### 1. Higgsfield

- **API Available**: Yes
- **API Base URL**: `https://platform.higgsfield.ai`
- **Cloud Dashboard**: `https://cloud.higgsfield.ai`
- **Auth Method**: Bearer token (API Key + Secret). Env vars: `HF_KEY` or `HF_API_KEY` + `HF_API_SECRET`
- **Python SDK**: `pip install higgsfield-client` | [GitHub](https://github.com/higgsfield-ai/higgsfield-client)
- **Node SDK**: `npm install higgsfield-js` (unofficial name; see repo) | [GitHub](https://github.com/higgsfield-ai/higgsfield-js)
- **MCP Server**: None found (no dedicated Higgsfield MCP). Available via **krea-mcp** (multi-model aggregator).
- **Rate Limits**: Not publicly documented
- **Queue Time**: Not publicly documented
- **Export Formats**: MP4
- **Instagram-Ready Export (9:16)**: Supported (multi-model platform, aspect ratio depends on underlying model)
- **Fully Programmable (no browser)**: Yes, via Cloud API

**Subscription Pricing**:
| Plan | Price/mo | Credits/mo |
|------|----------|------------|
| Free | $0 | Limited |
| Basic | $9 | ~180 |
| Pro | $29 | ~580 |
| Ultimate | $49 | ~980 |
| Creator | $149 | ~2,980 |
| Custom | Contact | Negotiable |

**Credit Costs**: Basic videos 15-25 credits; premium models (Sora 2, Veo 3.1) 40-70 credits each.

**Third-party API pricing** (via Segmind): Text-to-Image $0.12-$0.23/gen; Speech-to-Video $0.86-$4.22/gen; Image-to-Video $0.16-$0.70/gen.

Sources: [Higgsfield Pricing](https://higgsfield.ai/pricing), [Segmind](https://blog.segmind.com/higgsfield-ai-features-pricing-guide/), [GitHub Python SDK](https://github.com/higgsfield-ai/higgsfield-client), [GitHub Node SDK](https://github.com/higgsfield-ai/higgsfield-js)

---

### 2. Runway (Gen-4 / Gen-4.5)

- **API Available**: Yes (production-ready)
- **API Base URL**: `https://api.dev.runwayml.com`
- **Auth Method**: API Key (Bearer token)
- **Python SDK**: `pip install runwayml` | [GitHub](https://github.com/runwayml/sdk-python)
- **Node SDK**: `npm install @runwayml/sdk` | [GitHub](https://github.com/runwayml/sdk-node)
- **MCP Server**: [mcp-video-gen](https://github.com/wheattoast11/mcp-video-gen) (community, RunwayML + Luma)
- **Rate Limits**: No RPM limit; concurrency limit 3-5 simultaneous tasks (tier-dependent). Excess tasks get THROTTLED status and queued.
- **Queue Time**: ~15 seconds for first batch; 2-3 min for a 10-sec clip total
- **Export Formats**: MP4 (H.264)
- **Instagram-Ready Export (9:16)**: Yes, supports 9:16 aspect ratio parameter
- **Fully Programmable (no browser)**: Yes

**API Credit Pricing** (1 credit = $0.01):
| Model | Credits/sec | Cost/sec | Cost/10s |
|-------|-------------|----------|----------|
| gen4.5 | 12 | $0.12 | $1.20 |
| gen4_turbo | 5 | $0.05 | $0.50 |
| gen4_aleph | 15 | $0.15 | $1.50 |
| gen3a_turbo | 5 | $0.05 | $0.50 |
| veo3 (via Runway) | 40 | $0.40 | $4.00 |
| veo3.1 (audio) | 40 | $0.40 | $4.00 |
| veo3.1 (no audio) | 20 | $0.20 | $2.00 |
| veo3.1_fast (audio) | 15 | $0.15 | $1.50 |
| veo3.1_fast (no audio) | 10 | $0.10 | $1.00 |

**Subscription Pricing**:
| Plan | Price/mo | Notes |
|------|----------|-------|
| Standard | $15 | 625 credits |
| Pro | $35 | More credits + priority |
| Unlimited | $95 | Unlimited relaxed generations |

Sources: [Runway API Pricing](https://docs.dev.runwayml.com/guides/pricing/), [Runway SDK Docs](https://docs.dev.runwayml.com/api-details/sdks/), [Runway API Tiers](https://docs.dev.runwayml.com/usage/tiers/)

---

### 3. Kling AI (Kuaishou)

- **API Available**: Yes (official developer portal)
- **API Base URL**: `https://klingai.com/global/dev/` (official) or via Atlas Cloud / PiAPI
- **Auth Method**: API Key (resource-unit billing)
- **Python SDK**: `pip install kling-api` (official) | Community: [GitHub](https://github.com/TechWithTy/kling)
- **Node SDK**: `npm install @kling-api/sdk` (official) | Community: `npm i @microfox/kling-ai`
- **MCP Server**: [mcp-kling](https://github.com/199-mcp/mcp-kling) (community, first Kling MCP)
- **Rate Limits**: Not publicly documented; volume discounts available via consultation
- **Queue Time**: 1-5 minutes depending on model/tier (paid tiers get priority)
- **Export Formats**: MP4
- **Instagram-Ready Export (9:16)**: Yes, native 9:16 aspect ratio support
- **Fully Programmable (no browser)**: Yes

**API Pricing (Kling-V3-Omni, latest)**:
| Mode | Cost/sec | Notes |
|------|----------|-------|
| Standard (no video input) | $0.084 | 0.6 resource units |
| Standard (with video) | $0.112 | 0.8 resource units |
| Pro (no video input) | $0.112 | 0.8 resource units |
| Pro (with video) | $0.168 | 1.2 resource units |

**Older Models**: Kling-V2-6 Standard: $0.21-$0.42/video; Pro: $0.35-$1.68/video.

**Consumer Subscription**: Free tier (66 daily credits), plans from $6.99-$180/month.

Sources: [Kling Dev Pricing](https://klingai.com/global/dev/pricing), [Atlas Cloud](https://www.atlascloud.ai/collections/kling), [PiAPI](https://piapi.ai/kling-api)

---

### 4. Pika

- **API Available**: Yes (via fal.ai partnership for Pika 2.2+)
- **API Base URL**: `https://fal.ai/models/fal-ai/pika/v2.2/` (hosted on fal.ai)
- **Auth Method**: fal.ai API key
- **Python SDK**: Via fal.ai Python client (`pip install fal-client`) | No dedicated Pika Python SDK
- **Node SDK**: `npm install @fal-ai/client` | No dedicated Pika Node SDK
- **MCP Server**: Available via **krea-mcp** (multi-model). No dedicated Pika MCP found.
- **Rate Limits**: fal.ai platform limits (varies by plan)
- **Queue Time**: ~1-3 minutes typical
- **Export Formats**: MP4
- **Instagram-Ready Export (9:16)**: Yes, supports 9:16 aspect ratio
- **Fully Programmable (no browser)**: Yes (via fal.ai API)

**API Pricing (via fal.ai)**:
| Feature | 720p | 1080p |
|---------|------|-------|
| Text-to-Video | $0.20/video | $0.45/video |
| Image-to-Video (Pikaframes) | $0.04/sec (min $0.20) | $0.06/sec (min $0.30) |

**Subscription Pricing**:
| Plan | Price/mo | Credits |
|------|----------|---------|
| Free | $0 | 80 credits (watermarked) |
| Standard | $10 | 700 credits |
| Pro | $35 | 2,300 credits |

Sources: [Pika API on fal.ai](https://fal.ai/models/fal-ai/pika/v2.2/text-to-video), [Pika Pricing](https://pika.art/pricing), [Pika API Info](https://pika.art/api)

---

### 5. Minimax / Hailuo

- **API Available**: Yes (official MiniMax platform + fal.ai)
- **API Base URL**: `https://platform.minimax.io` (official) | `https://fal.ai/models/fal-ai/minimax/` (fal.ai)
- **Auth Method**: API Key
- **Python SDK**: `pip install minimax` (official) | Community: [GitHub](https://github.com/jesuscopado/minimax-python)
- **Node SDK**: `npm i minimax` (official)
- **MCP Server**: Available via **krea-mcp** (Hailuo model), **video-gen-mcp** (Hailuo 02). No dedicated MiniMax MCP.
- **Rate Limits**: Not publicly documented
- **Queue Time**: ~2-4 minutes typical
- **Export Formats**: MP4
- **Instagram-Ready Export (9:16)**: Yes (aspect ratio configurable)
- **Fully Programmable (no browser)**: Yes

**API Pricing**:
| Model | Resolution | Cost/sec | Cost/6s video |
|-------|-----------|----------|---------------|
| Hailuo-02 Standard | 768p | $0.045 | $0.27 |
| Hailuo-02 Pro | 1080p | $0.08 | $0.48 |
| Hailuo-02 Standard | 512p | $0.017 | $0.10 |
| Hailuo 2.3 | 768p | ~$0.045 | ~$0.27 |
| Hailuo 2.3 Fast | 768p | ~$0.023 | ~$0.14 |

**Consumer Pricing**: Free tier available. Subscription starts at $9.99/month.

Sources: [MiniMax Platform](https://platform.minimax.io/docs/guides/pricing), [Segmind Pricing](https://www.segmind.com/models/minimax-ai/pricing), [fal.ai Hailuo](https://fal.ai/models/fal-ai/minimax/hailuo-02/pro/text-to-video)

---

### 6. Google Veo 2 (+ Veo 3 / 3.1)

- **API Available**: Yes (GA on Vertex AI + Gemini Developer API)
- **API Base URL**: Vertex AI: `https://us-central1-aiplatform.googleapis.com/` | Gemini API: `https://generativelanguage.googleapis.com/`
- **Auth Method**: Google Cloud IAM / API Key (Gemini API)
- **Python SDK**: `pip install google-genai` | [GitHub](https://github.com/googleapis/python-genai)
- **Node SDK**: `npm install @google/genai` (Google Gen AI SDK)
- **MCP Server**: None dedicated found. Could use Gemini MCP server for image tasks; video not confirmed.
- **Rate Limits**: Standard Vertex AI quotas (project-level). Not publicly documented per-model.
- **Queue Time**: ~2-5 minutes (varies by model + demand)
- **Export Formats**: MP4 (H.264), stored in GCS bucket
- **Instagram-Ready Export (9:16)**: Yes, supports 9:16 aspect ratio parameter
- **Fully Programmable (no browser)**: Yes

**API Pricing**:
| Model | Platform | Cost/sec | Cost/10s |
|-------|----------|----------|----------|
| Veo 2 | Gemini API | $0.35 | $3.50 |
| Veo 2 | Vertex AI | $0.50 | $5.00 |
| Veo 3 | Vertex AI | ~$0.50 | ~$5.00 |
| Veo 3.1 (audio) | Vertex AI | $0.75 | $7.50 |
| Veo 3.1 (no audio) | Vertex AI | ~$0.40 | ~$4.00 |
| Veo 3.1 Fast (audio) | Vertex AI | $0.15 | $1.50 |
| Veo 3.1 Fast (no audio) | Vertex AI | $0.10 | $1.00 |

**Note**: Veo 2 preview endpoints deprecated April 2, 2026. Migrate to GA endpoints.

**Free tier**: $300 Google Cloud free credits for new accounts (applies to Vertex AI).

Sources: [Vertex AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing), [Veo 2 Docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/2-0-generate), [Google Gen AI SDK](https://github.com/googleapis/python-genai)

---

### 7. OpenAI Sora 2

- **API Available**: Yes (launched September 30, 2025)
- **API Base URL**: `https://api.openai.com/v1/videos`
- **Auth Method**: OpenAI API Key (Bearer token). Minimum Tier 2 ($10 top-up) required.
- **Python SDK**: `pip install openai` (>=1.51.0) | Uses `client.videos` namespace
- **Node SDK**: `npm install openai` | Official OpenAI SDK
- **MCP Server**: Available via **krea-mcp** (Sora 2 model), **agent-media** CLI+MCP. No dedicated Sora MCP.
- **Rate Limits**: See tier table below
- **Queue Time**: ~1 minute typical (fastest of the bunch)
- **Export Formats**: MP4
- **Instagram-Ready Export (9:16)**: Yes, supports 9:16, 16:9, 1:1, 2:3, 3:2
- **Fully Programmable (no browser)**: Yes

**API Pricing**:
| Model | Resolution | Cost/sec | Cost/10s |
|-------|-----------|----------|----------|
| sora-2 | 720p | $0.10 | $1.00 |
| sora-2-pro | 720p | $0.30 | $3.00 |
| sora-2-pro | 1080p | $0.50 | $5.00 |

**Rate Limits by Tier**:
| Tier | RPM | Daily Limit |
|------|-----|-------------|
| ChatGPT Plus | 5 | 50 |
| ChatGPT Pro | 50 | 500 |
| API Tier 2 | 10 | 200 |
| API Tier 3 | 30 | 600 |
| API Tier 4 | 60 | 1,200 |
| Enterprise | 200+ | Custom |

**Subscription**: Plus ($20/mo, 1000 credits); Pro ($200/mo, 10,000 credits + unlimited relaxed).

Sources: [Sora 2 API Guide](https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas), [OpenAI Video Generation](https://platform.openai.com/docs/guides/video-generation), [OpenAI Pricing](https://platform.openai.com/docs/pricing)

---

### 8. Luma Dream Machine (Ray 2 / Ray 3)

- **API Available**: Yes (official + available on AWS Bedrock)
- **API Base URL**: `https://api.lumalabs.ai/`
- **Auth Method**: API Key (LUMAAI_API_KEY env var or auth_token parameter)
- **Python SDK**: `pip install lumaai` | [GitHub](https://github.com/lumalabs/lumaai-python)
- **Node SDK**: Available (check Luma GitHub) | Also on AWS Bedrock SDK
- **MCP Server**: [mcp-video-gen](https://github.com/wheattoast11/mcp-video-gen) (community, Luma + RunwayML)
- **Rate Limits**: Build tier: 10 concurrent video generations, 20 RPM. Higher tiers available.
- **Queue Time**: 2-5 min (5s video), 4-8 min (9s video). Fast Mode = priority; Relaxed Mode = slower queue.
- **Export Formats**: MP4
- **Instagram-Ready Export (9:16)**: Yes (aspect ratio parameter supported)
- **Fully Programmable (no browser)**: Yes

**Subscription Pricing**:
| Plan | Price/mo | Credits | Notes |
|------|----------|---------|-------|
| Free | $0 | Limited | Watermarked |
| Lite | $9.99 | 3,200 | ~4 videos |
| Plus | $29.99 | 10,000 | Priority queue |
| Unlimited | $94.99 | 10,000 fast + unlimited relaxed | Best for production |

**Cost per video**: ~800 credits per 10s video. At Plus tier: ~$2.40 per 10s video.
**Third-party API**: PiAPI offers $0.20/video for Dream Machine 2.

Sources: [Luma API](https://lumalabs.ai/api), [Luma Rate Limits](https://docs.lumalabs.ai/docs/rate-limits), [Luma Python SDK](https://github.com/lumalabs/lumaai-python)

---

### 9. Wan 2.1 / 2.2 (Open Source, Self-Hosted)

- **API Available**: Self-hosted only (no cloud API from Alibaba)
- **API Base URL**: N/A (run locally or on cloud GPU)
- **Auth Method**: N/A (self-hosted)
- **Python SDK**: N/A (use PyTorch + HuggingFace directly) | [GitHub](https://github.com/Wan-Video/Wan2.1)
- **Node SDK**: N/A
- **MCP Server**: None found
- **Rate Limits**: Hardware-dependent
- **Queue Time**: 4 min (480p/5s on RTX 4090 w/ 1.3B model); 20-25 min (720p on H100 w/ 14B model)
- **Export Formats**: MP4 (via ffmpeg post-processing)
- **Instagram-Ready Export (9:16)**: Manual configuration required
- **Fully Programmable (no browser)**: Yes (CLI/Python script)

**Hardware Requirements**:
| Model | VRAM Required | Notes |
|-------|--------------|-------|
| T2V-1.3B | 8 GB | Consumer GPU friendly (RTX 3060+) |
| T2V-14B | 65-80 GB | Datacenter GPU required (A100/H100) |
| T2V-14B (FP8) | 40-50 GB | Quantized, still needs pro GPU |

**Cost**: Free (open-source, Apache 2.0). Cloud GPU cost: ~$2-4/hr for H100 (RunPod, Lambda, etc.).
**Effective cost/min of video**: ~$0.50-$1.50 on cloud GPU (amortized over generation time).

**Third-party hosted API** (via fal.ai, Replicate, Novita): Available at varying prices.

Sources: [Wan2.1 GitHub](https://github.com/Wan-Video/Wan2.1), [Spheron Setup Guide](https://www.spheron.network/blog/deploy-wan-2-1-ai-video-generation-gpu-setup/), [Wan2GP](https://github.com/deepbeepmeep/Wan2GP)

---

## Pricing Comparison Table

### API Cost Per Second (pay-as-you-go)

| Tool | Cheapest/sec | Mid-tier/sec | Premium/sec | Best Resolution |
|------|-------------|-------------|-------------|-----------------|
| **Hailuo 2.3 Fast** | $0.023 | $0.045 | $0.08 | 1080p |
| **Pika 2.2** (fal.ai) | $0.033* | $0.04 | $0.06 | 1080p |
| **Runway gen4_turbo** | $0.05 | $0.12 | $0.15 | 1080p |
| **Kling V3-Omni** | $0.084 | $0.112 | $0.168 | 1080p+ (4K native) |
| **Sora 2** | $0.10 | $0.30 | $0.50 | 1080p |
| **Veo 3.1 Fast** | $0.10 | $0.15 | $0.75 | 1080p |
| **Google Veo 2** | $0.35 | $0.50 | - | 1080p |
| **Luma** | ~$0.24** | ~$0.30** | - | 1080p |

*Pika: $0.20/6s video = ~$0.033/sec at 720p
**Luma: estimated from credit pricing (~800 credits/10s at $29.99/10,000 credits)

### Subscription Plans Comparison

| Tool | Free | Starter | Mid | Pro/Unlimited |
|------|------|---------|-----|---------------|
| Higgsfield | Yes (limited) | $9/mo | $29/mo | $49-$149/mo |
| Runway | No | $15/mo | $35/mo | $95/mo |
| Kling | Yes (66 credits/day) | $6.99/mo | $30/mo | $180/mo |
| Pika | Yes (80 credits, watermark) | $10/mo | $35/mo | - |
| Hailuo/Minimax | Yes (limited) | $9.99/mo | - | - |
| Sora 2 | No (removed Jan 2026) | $20/mo (Plus) | - | $200/mo (Pro) |
| Luma | Yes (limited, watermark) | $9.99/mo | $29.99/mo | $94.99/mo |
| Veo 2 | $300 GCP credits (new) | Pay-per-use | - | Enterprise |
| Wan 2.1 | Free (self-host) | - | - | Cloud GPU ~$2-4/hr |

---

## Weekly Production Cost Estimate (5 Reels/Week, 30-60s Each)

**Assumptions**: 5 reels x 45s average = 225 seconds/week. ~3 attempts per reel (failed gens, iteration) = 675 seconds actual API usage. Monthly = 2,700 seconds.

| Tool | Cost/sec Used | Weekly Cost | Monthly Cost | Notes |
|------|--------------|-------------|-------------|-------|
| **Hailuo 2.3 Fast (768p)** | $0.023 | $15.53 | $62.10 | Cheapest API, 768p only |
| **Hailuo 02 Pro (1080p)** | $0.08 | $54.00 | $216.00 | 1080p native |
| **Pika 2.2 (720p via fal)** | ~$0.033 | $22.28 | $89.10 | Good value |
| **Runway gen4_turbo** | $0.05 | $33.75 | $135.00 | Solid mid-range |
| **Runway gen4.5** | $0.12 | $81.00 | $324.00 | Premium quality |
| **Kling V3-Omni Standard** | $0.084 | $56.70 | $226.80 | Good quality/price |
| **Sora 2 (720p)** | $0.10 | $67.50 | $270.00 | Fast processing |
| **Sora 2-pro (1080p)** | $0.50 | $337.50 | $1,350.00 | Expensive for volume |
| **Veo 3.1 Fast (no audio)** | $0.10 | $67.50 | $270.00 | Google ecosystem |
| **Veo 2 (Gemini API)** | $0.35 | $236.25 | $945.00 | Expensive |
| **Luma (Plus sub)** | ~$0.24 | $162.00 | $648.00 | Credit-based |
| **Wan 2.1 (self-hosted H100)** | ~$0.02-$0.05 | $13.50-$33.75 | $54-$135 | Requires GPU infra |

**Best value for 5 reels/week at acceptable quality**:
1. **Hailuo 2.3 Fast** (~$62/mo) - cheapest, 768p
2. **Pika 2.2 on fal.ai** (~$89/mo) - good quality at 720p
3. **Runway gen4_turbo** (~$135/mo) - best quality/price ratio at 1080p
4. **Subscription alternative**: Runway Unlimited ($95/mo) for unlimited relaxed gens

---

## MCP Server Availability Summary

| MCP Server | Models Supported | Install | GitHub |
|-----------|-----------------|---------|--------|
| **krea-mcp** | Hailuo, Kling 1.6, Runway Gen-4, Pika 2, Veo 3, Sora 2, Flux | npm/config | [keugenek/krea-mcp](https://github.com/keugenek/krea-mcp) |
| **mcp-kling** | Kling (all models, full suite) | npm/config | [199-mcp/mcp-kling](https://github.com/199-mcp/mcp-kling) |
| **mcp-video-gen** | Luma AI + RunwayML | npm/config | [wheattoast11/mcp-video-gen](https://github.com/wheattoast11/mcp-video-gen) |
| **agent-media** | Kling, Veo, Sora, Seedance, Flux, Grok | CLI + MCP | [GitHub](https://github.com/jayeshmepani/Media-AI) |
| **video-gen-mcp** | Kling 2.1, Hailuo 02 + music/speech | npm/config | [h2a-dev/video-gen-mcp-monolithic](https://mcpservers.org/servers/h2a-dev/video-gen-mcp-monolithic) |

**Best MCP for multi-model orchestration**: **krea-mcp** (covers the most models in one server)
**Best MCP for single-model depth**: **mcp-kling** (complete Kling suite including lip-sync, effects, virtual try-on)

---

## Social Media Integration Notes

### Instagram-Ready Export (1080x1920, 9:16, H.264)

All major tools support 9:16 aspect ratio natively:
- **Runway**: `ratio` parameter in API
- **Kling**: Aspect ratio selector (1:1, 16:9, 9:16)
- **Sora 2**: Supports 9:16, 16:9, 1:1, 2:3, 3:2
- **Veo**: `aspect_ratio` in GenerateVideosConfig
- **Pika**: 9:16 support
- **Luma**: Aspect ratio parameter
- **Hailuo**: Aspect ratio configurable

All output MP4/H.264 by default, which is Instagram-compatible.

### Built-in Publishing/Scheduling
- **None** of these tools have native Instagram publishing
- All require external orchestration (Buffer, Later, Hootsuite, or custom pipeline)

### FFmpeg Post-Processing
- All tools output standard MP4/H.264, fully compatible with FFmpeg
- Common post-processing: trimming, adding captions/text overlays, audio mixing, format conversion
- Wan 2.1 specifically requires FFmpeg for output handling

### Editing Tool Integration
- **Runway**: ComfyUI plugin available; exports compatible with Premiere/DaVinci/CapCut
- **Kling**: ComfyUI plugin ([KlingTeam/ComfyUI-KLingAI-API](https://github.com/KlingTeam/ComfyUI-KLingAI-API))
- **Luma**: ComfyUI plugin ([lumalabs/ComfyUI-LumaAI-API](https://github.com/lumalabs/ComfyUI-LumaAI-API))
- All tools output standard formats importable into any NLE (DaVinci Resolve, Premiere, CapCut, Final Cut)

---

## Recommendation: Best API for Programmatic Orchestration

### Tier 1: Best Overall for Automated Pipeline

**Runway Gen-4 Turbo** via API
- Mature API with official Python + Node SDKs
- Best documentation of any provider
- Reasonable pricing ($0.05/sec)
- No RPM limit (just concurrency)
- MCP server available
- Also provides access to Veo 3.1 models through the same API

### Tier 2: Best Budget Option

**Minimax Hailuo 2.3 Fast** via official API or fal.ai
- Cheapest per-second cost ($0.023/sec)
- Official Python/Node SDKs
- 1080p available on Pro tier
- Good quality for social media content

### Tier 3: Best for Quality + Speed

**OpenAI Sora 2** via API
- Fastest generation (~1 min)
- Official Python SDK (openai package)
- Well-documented API patterns (same as GPT)
- 720p at $0.10/sec is reasonable
- Familiar auth/SDK for teams already using OpenAI

### Wild Card: Best for Maximum Control

**Wan 2.1/2.2** (self-hosted)
- Free, open-source (Apache 2.0)
- Full control over generation parameters
- Can run 1.3B model on consumer GPU
- Requires infrastructure management
- Best for teams with GPU access who want zero per-generation cost

### Recommended Stack for Film Studio Agent

```
Primary:    Runway gen4_turbo (quality + API maturity)
Fallback:   Hailuo 2.3 Fast (cost savings for bulk generation)
Premium:    Sora 2-pro or Veo 3.1 (when quality > cost)
MCP Layer:  krea-mcp (unified access to all models)
Post-proc:  FFmpeg (trim, caption, format)
Publishing: Custom pipeline -> Buffer/Later API
```

**Estimated monthly cost for 5 reels/week**: $135-$200 (Runway primary + Hailuo fallback)
