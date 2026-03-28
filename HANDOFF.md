# Session Handoff — V20 Cloud Deployment
Date: 2026-03-28 20:45
Branch: main
Context: ~58% — clean exit after successful deploy

## What This Session Delivered

### DEPLOYED TO PRODUCTION

#### Susan Cloud Brain — LIVE on Fly.io
- **URL:** https://susan-cloud-brain.fly.dev
- **App:** susan-cloud-brain, DFW region, shared-cpu-1x, 512MB
- **Machines:** 2x (high availability), auto-stop/start
- **Cost:** ~$3-6/mo
- **Endpoints verified:**
  - GET /health → 73 agents, 6 modules (config, foundry, rag, oracle, memory, research)
  - GET /agents → 10 groups, full roster
  - POST /route → task routing
  - POST /rag/query → Supabase vector search
  - GET /oracle/status → Oracle Health dashboard
  - GET /oracle/battlecard/{competitor} → Klue-format battlecards
  - GET /oracle/freshness → competitor data freshness
  - POST /research/gaps → knowledge gap detection
  - GET /memory/stats → TIMG memory statistics
  - GET /cost/report → model pricing and config
- **Secrets set:** VOYAGE_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY, ANTHROPIC_API_KEY

#### Jake Gateway V20 — LIVE on Cloudflare Workers
- **URL:** https://jake-gateway.rodgemd1.workers.dev
- **Version:** v20 (Version ID: 7ea7f259-f716-4154-b0cd-b53fcee3e3a7)
- **Size:** 29.34 KiB / gzip 6.89 KiB
- **Bindings:** D1 (jake-ops), Workers AI, R2 (jake-state), KV (JAKE_CACHE)
- **Endpoints (30+):**
  - Legacy: /health, /api, /tunnel/status, /memory/search, /rag/query, /oracle/brief, /oracle/signals
  - D1 CRUD: /goals, /tasks, /briefs, /growth, /scrape-queue, /status
  - Susan proxy: /susan/route, /susan/agents, /susan/foundry, /susan/rag/query, /susan/ingest, /susan/oracle/*, /susan/evolve/propose
  - Workers AI: /ai/classify, /ai/summarize, /ai/embed

#### D1 Database (jake-ops) — LIVE
- **Database ID:** 0897dcd9-9984-423f-a5bc-bedfa00aa196
- **Region:** ENAM
- **Tables (7):** goals, tasks, briefs, capability_growth, scrape_queue, agent_performance, events
- **First goal created:** "Deploy V20 — Full Cloud Team" (75/100)
- **First task created:** "Deploy Dashboard to CF Pages" (queued, P1)

### BUILT (Not Yet Deployed)

#### Scheduled Trigger Definitions (10 YAMLs)
- `infrastructure/triggers/01-morning-brief.yaml` — 06:00 CT daily
- `infrastructure/triggers/02-midday-update.yaml` — 12:00 CT daily
- `infrastructure/triggers/03-evening-summary.yaml` — 20:00 CT daily
- `infrastructure/triggers/04-overnight-worker.yaml` — 01:00 CT daily
- `infrastructure/triggers/05-research-harvest.yaml` — 03:00 CT daily
- `infrastructure/triggers/06-goal-checkin.yaml` — Mon/Thu 09:00 CT
- `infrastructure/triggers/07-source-discovery.yaml` — Sun 05:00 CT
- `infrastructure/triggers/08-evolution-cycle.yaml` — Sun 22:00 CT
- `infrastructure/triggers/oh-01-morning-intel.yaml` — 06:30 CT daily
- `infrastructure/triggers/oh-02-weekly-digest.yaml` — Fri 16:00 CT

#### Business Workspaces (3 repos)
- `~/Desktop/Oracle-Health-Intelligence/` — CLAUDE.md, .aider.conf.yml
- `~/Desktop/Alex-Recruiting/` — CLAUDE.md, .aider.conf.yml
- `~/Desktop/Fitness-App/` — CLAUDE.md, .aider.conf.yml

#### Ollama Model Fleet (5 models, 47GB)
- qwen2.5-coder:32b (19GB) — primary coding
- deepseek-r1:14b (9GB) — local reasoning
- llama3.1:8b (5GB) — fast tasks
- nomic-embed-text (274MB) — local embeddings
- gpt-oss:20b (13GB) — general purpose

#### Aider v0.23.0
- Installed via pipx with Python 3.12
- Global config at ~/.aider.conf.yml (defaults to DeepSeek V3 via OpenRouter)
- OpenRouter API key already set in ~/.hermes/.env

#### Strategic Plans (Approved)
- `docs/plans/2026-03-28-always-on-jake-cloudflare-plan.md` — 3-option analysis, Option B approved
- `docs/plans/2026-03-28-operator-layer-multi-session.md` — 125x throughput architecture

#### Research (Saved)
- `.claude/agent-memory/research/cloud-python-hosting-q1-2026.md`
- `.claude/agent-memory/research/strategic-frameworks-future-back-6lens-pai.md`

### Files Created/Modified This Session

```
NEW FILES:
  susan-team-architect/backend/api.py                          (~300 lines)
  susan-team-architect/backend/Dockerfile                      (~8 lines)
  susan-team-architect/backend/fly.toml                        (~20 lines)
  susan-team-architect/backend/.dockerignore                   (~6 lines)
  infrastructure/cloudflare-worker/src/index.ts                (971 lines — rewritten)
  infrastructure/cloudflare-worker/migrations/0001_*.sql       (~90 lines)
  infrastructure/triggers/*.yaml                               (10 files, ~390 lines)
  bin/launch-sessions                                          (~40 lines)
  bin/setup-triggers                                           (~30 lines)
  docs/v20-quick-reference.md                                  (~40 lines)
  docs/plans/2026-03-28-always-on-jake-cloudflare-plan.md     (~600 lines)
  docs/plans/2026-03-28-operator-layer-multi-session.md       (~600 lines)

MODIFIED:
  infrastructure/cloudflare-worker/wrangler.toml               (D1 + AI bindings, v20)

EXTERNAL:
  ~/Desktop/Oracle-Health-Intelligence/CLAUDE.md + README.md
  ~/Desktop/Alex-Recruiting/CLAUDE.md + README.md
  ~/Desktop/Fitness-App/CLAUDE.md + README.md
  ~/.aider.conf.yml
```

## Live Endpoints (Test From Any Device)

```bash
# Susan Cloud Brain
curl https://susan-cloud-brain.fly.dev/health
curl https://susan-cloud-brain.fly.dev/agents

# Jake Gateway V20
curl https://jake-gateway.rodgemd1.workers.dev/health
curl https://jake-gateway.rodgemd1.workers.dev/status
curl https://jake-gateway.rodgemd1.workers.dev/goals
curl https://jake-gateway.rodgemd1.workers.dev/tasks

# Jake → Susan proxy
curl https://jake-gateway.rodgemd1.workers.dev/susan/agents

# Workers AI (free)
curl -X POST https://jake-gateway.rodgemd1.workers.dev/ai/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "categories": ["a","b"]}'
```

## Next Session Priorities

1. **Deploy Dashboard to CF Pages** — `cd apps/v5 && npm run build && wrangler pages deploy`
2. **Create first scheduled trigger** — morning brief using /schedule
3. **Custom domains** — susan.jakestudio.ai, dashboard.jakestudio.ai
4. **Create Mike's Q2 goals** — populate D1 with real goals
5. **Set up Resend email** — wire briefs to email delivery
6. **Test overnight worker trigger** — prove autonomous execution works
7. **Start scrape queue** — populate initial URLs for 50%/week growth

## Auth Notes
- **Fly.io:** Authenticated as rodgemd1@gmail.com (fly auth login)
- **Cloudflare:** Wrangler OAuth active with full permissions (D1, Workers, Pages, AI, KV, R2)
- **CF API Token:** ~/.hermes/.env — has Workers permissions but NOT D1. Use `npx wrangler` directly for D1 ops.

## Architecture (Deployed)

```
CLOUD (LIVE):
  Fly.io      → susan-cloud-brain.fly.dev   (73 agents, FastAPI, $3-6/mo)
  CF Workers  → jake-gateway V20            (30+ endpoints, free)
  CF D1       → jake-ops                    (7 tables, free)
  CF Workers AI → Llama 3.1, Mistral, BGE   (free inference)
  CF R2       → jake-state                  (artifact storage)
  CF KV       → JAKE_CACHE                  (hot cache)
  Supabase    → pgvector (10,788 chunks)    (vector store)

BUILT (pending deploy):
  CF Pages    → dashboard PWA               (apps/v5)
  Triggers    → 10 scheduled agents         (infrastructure/triggers/)

LOCAL:
  Ollama      → 5 models, 47GB             ($0 inference)
  Aider       → v0.23.0 + OpenRouter       (multi-session coding)
  Cursor      → local IDE                  ($20/mo)
```

## Key Decisions
- Option B (CF + Fly.io) deployed — Susan on Fly, Jake on CF Workers
- D1 as operations brain (goals, tasks, briefs, growth tracking)
- Workers AI for free inference (classify, summarize, embed)
- Susan proxy through Jake gateway — one API surface for everything
- Mac Studio = dev workstation, not server
- 10 scheduled triggers defined, pending activation
- 3 business workspaces created with per-business CLAUDE.md
