---
name: Cloud Python Hosting & GPU Inference Pricing Q1 2026
description: Verified pricing for Fly.io, Railway, Modal, Replicate, Cloudflare Workers, Render, Hugging Face, Together AI — plus Claude Code scheduled triggers and MCP server ecosystem. Sourced March 2026.
type: reference
---

## Always-On Python FastAPI (cheapest to most expensive, 24/7)

| Platform | Min cost/mo | RAM | Notes |
|---|---|---|---|
| Fly.io | ~$2.02 | 256MB | shared-cpu-1x; no free always-on as of 2026 |
| Fly.io | ~$3.32 | 512MB | shared-cpu-1x |
| Fly.io | ~$5.92 | 1GB | shared-cpu-1x |
| Railway | ~$5 | up to 48GB | Hobby plan; $5 credit included, usage-billed |
| Render | $7 | 512MB | Starter; paid plan required for always-on |
| Render | $25 | 2GB | Standard |

**Render free tier**: spins down after inactivity (cold starts on request). Not suitable for always-on.

**Fly.io free tier**: deprecated for new orgs. Existing orgs keep 3x shared-cpu-1x 256MB VMs free.

**Railway free tier**: 30-day trial with $5 credit, then $1/month minimum with $5 minimum Hobby plan for sustained use.

**Winner — cheapest always-on**: Fly.io shared-cpu-1x 256MB at $2.02/mo or 512MB at $3.32/mo. Fly auto-scales to zero is opt-in; machines can be configured always-on.

## GPU Inference — Per-Second Pricing (March 2026)

### Modal (serverless, Python-native)
- T4: $0.000164/sec = $0.59/hr
- A10: $0.000306/sec = $1.10/hr
- L4: $0.000222/sec = $0.80/hr
- A100 40GB: $0.000583/sec = $2.10/hr
- A100 80GB: $0.000694/sec = $2.50/hr
- H100: $0.001097/sec = $3.95/hr
- H200: $0.001261/sec = $4.54/hr
- B200: $0.001736/sec = $6.25/hr
- Free: $30/mo credits (Starter), $100/mo (Team)
- Billing: pay-per-second, no idle cost

### Replicate
- CPU small: $0.000025/sec
- T4: $0.000225/sec = $0.81/hr
- L40S: $0.000975/sec = $3.51/hr
- A100 80GB: $0.001400/sec = $5.04/hr
- H100: $0.001525/sec = $5.49/hr
- No free tier. Private models billed for all online time.

### Hugging Face Inference Endpoints (hourly, always-on)
- T4 (AWS): $0.50/hr
- L4 (AWS): $0.80/hr
- A10G (AWS): $1.00/hr
- L40S (AWS): $1.80/hr
- A100 80GB (AWS): $2.50/hr
- H100 80GB (AWS): $4.50/hr
- H200 141GB (AWS): $5.00/hr
- B200: $9.25/hr
- CPU from $0.03/hr
- ZeroGPU: free H200 (70GB VRAM) for Spaces via PRO plan ($9/mo). Dynamic allocation, not dedicated.

### Cloudflare Workers AI (serverless, per Neuron)
- $0.011 per 1,000 Neurons
- Free: 10,000 Neurons/day (~910K input tokens on a 7B model at 11 neurons/token)
- Models available: Llama 3, Mistral, Gemma, Phi, SDXL, Whisper, BGE embeddings + more
- No GPU provisioning required — fully managed

## Together AI — Open Source Model Inference (per 1M tokens)
- Mistral 7B: $0.20 input / $0.20 output
- Llama 3.3 70B: $0.88 / $0.88
- Llama 4 Maverick: $0.27 / $0.85
- DeepSeek-V3.1: $0.60 / $1.70
- Qwen3.5-397B: $0.80 / $2.40
- Dedicated H100: $3.99/hr
- Dedicated H200: $5.49/hr
- Dedicated B200: $9.95/hr

## Cloudflare Workers — Python Support

**YES — Python is officially supported (beta as of Q1 2026).**
- Runtime: Pyodide (CPython compiled to WebAssembly via v8 isolate)
- Cold starts: 2.4x faster than AWS Lambda, 3x faster than Google Cloud Run (with Wasm snapshots)
- Supported frameworks: FastAPI, LangChain, httpx, Pydantic explicitly listed
- Package manager: pywrangler (uv-based, pyproject.toml)
- Compatibility flag: `python_workers` required
- FFI to JS Runtime APIs: KV, D1, Workers AI, R2 all accessible from Python
- Python Workflows: in beta
- Limitation: still beta, not all packages available (pure Python + Pyodide-compiled C extensions only)

## Claude Code Scheduled Triggers + MCP

- `/loop` command: repeats a prompt at a fixed interval (cron-like) as a background worker
- Scheduled tasks automatically inherit MCP servers connected via web account
- MCP servers can call external APIs (Telegram, DexScreener, databases, GitHub, etc.)
- Pattern: deploy MCP server to Cloudflare Workers / Fly.io / Vercel — Claude Code calls it on schedule
- MCP spec donated to Linux Foundation Dec 2025; now supported by OpenAI, Google, Anthropic

## MCP Server Ecosystem (March 2026)

### Web Scraping / Research
- **Firecrawl MCP**: 12 tools (scrape, search, crawl, extract, map, batch, browser automation). 83% accuracy, 7s avg. Official server.
- **Tavily MCP**: web search + extract. 45% success rate in benchmarks, 41s avg. Rate-limited on free tier.
- **One Search MCP**: unified wrapper over SearxNG + Tavily + Firecrawl

### Email
- **Gmail MCP** (GongRzhe): Claude Desktop integration, auto OAuth, natural language Gmail management
- **Google Workspace MCP** (taylorwilsdon): Gmail + Calendar + Docs + Sheets + Slides + Chat + Forms — most complete
- **mcp-google-workspace** (j3k0): Gmail + Calendar via MCP protocol

### Communication
- **Slack MCP** (official): 47 tools, search channels, send messages
- **Slack MCP** (korotovsky): no permission requirements, DMs, Group DMs, smart history fetch, OAuth or stealth mode

### Directory
- PulseMCP: 11,870+ servers updated daily — pulsemcp.com
- MCP Registry: official searchable registry

## Cost Benchmarks (GPU Inference, H100 per hour)
| Platform | H100 $/hr | Billing model |
|---|---|---|
| Modal | $3.95 | per-second, no idle |
| Together AI dedicated | $3.99 | per-hour, always-on |
| Replicate | $5.49 | per-second, idle billed for private |
| HuggingFace Endpoints | $4.50 | per-hour, always-on |
| Together AI on-demand | $3.49 | per-hour |

**Winner — cheapest GPU inference**: Modal at pay-per-second with $30/mo free credits. Best for bursty workloads.

**Winner — cheapest serverless GPU**: Cloudflare Workers AI at $0.011/1K Neurons with 10K free/day. Best for inference-only (no custom model training).

**Winner — cheapest dedicated GPU**: Together AI on-demand H100 at $3.49/hr.
