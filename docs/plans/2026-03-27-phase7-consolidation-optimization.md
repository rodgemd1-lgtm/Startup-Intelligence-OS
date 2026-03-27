# V15 Phase 7: Consolidation & Optimization — PARKING LOT → PLAN

**Date**: 2026-03-27
**Author**: Jake
**Status**: PARKED — dedicated session needed
**Priority**: HIGH — cost reduction + complexity reduction
**Effort**: MAX (cross-system audit, multi-session)

---

## The Problem

Mike's infrastructure is sprawling across too many services, tools, and execution venues. Cost is untracked. Redundancies everywhere. This phase consolidates everything into clean, minimal channels.

---

## Inventory (Known Moving Pieces)

### Communication/Delivery
| Service | Used For | Cost | Status |
|---------|----------|------|--------|
| Resend | Email delivery (briefs, alerts) | ? | Active |
| ClickSend | SMS/voice? | ? | Active? |
| Telegram Bot (Big Birch) | Jake → Mike messaging | Free | Active |
| Apple Mail (osascript) | Oracle Health email access | Free | Active |

### Infrastructure
| Service | Used For | Cost | Status |
|---------|----------|------|--------|
| Cloudflare Workers + R2 + KV | Jake gateway, state, cache | Free tier | Active |
| Cloudflare (Alex Recruiting domain) | Email sending for Jacob | ? | Active |
| Fly.io | James's OS hosting | ? | Active |
| Voyeur.ai | ? (through James's OS) | ? | Active? |
| Supabase | Susan RAG, Jake Brain, goals, tasks | Free tier | Active |
| SuperMemory.ai Pro | Memory infrastructure | $19/mo | Active |
| Vercel | OpenClaw Studio dashboard | Free tier | Active |

### AI/Model Costs
| Service | Used For | Cost | Status |
|---------|----------|------|--------|
| Anthropic API (Claude) | All agents | ~$150/mo budget | Active |
| OpenAI API | ? | ? | ? |
| Voyage AI | Embeddings (1024d) | ? | Active |

### Execution Venues
| Venue | What Runs There | Count |
|-------|----------------|-------|
| launchd (local cron) | Proactive PA scripts | 3 active + 1 claude-remote |
| Claude scheduled tasks | Briefs, intel, monitoring | ~20? |
| Hermes cron (DEPRECATED) | Was: morning brief, triage, etc. | 16 disabled |
| Paperclip heartbeats | Agent scheduling | 21 agents registered |
| OpenClaw | Agent runtime | 65 agents with SYSTEM.md |

### Agent Platforms
| Platform | Agent Count | Status |
|----------|------------|--------|
| OpenClaw | 65 agents | SYSTEM.md complete |
| Susan (backend) | 73+ agent definitions | Active |
| Paperclip | 21 registered | Active |
| Claude Code subagents | ~112 (wshobson plugins) | Available |
| VoltAgent skills | 5,400+ community skills | Not yet imported |

---

## Optimization Goals

### 1. Reduce Cost
- Evaluate open-source models: GLM-5-Turbo, MiniMax v2.7, Qwen, DeepSeek
- Route Haiku-tier tasks to cheaper/free models
- Track actual spend per agent per month
- Target: reduce from ~$150/mo to <$100/mo without quality loss

### 2. Consolidate Execution Venues
- Move ALL scheduled tasks through OpenClaw + launchd (kill Claude scheduled tasks?)
- Or: move everything through Paperclip heartbeats
- ONE place for scheduling, not three

### 3. Import VoltAgent Skills
- Clone: https://github.com/VoltAgent/awesome-agent-skills
- Clone: https://github.com/VoltAgent (full org)
- Ingest all community skills into Obsidian + Susan RAG
- Map to existing agent roster — what fills gaps?
- Build meta-agents, super-agents, sub-agents hierarchy

### 4. Service Consolidation
- Map all services → determine which are redundant
- Cloudflare as single infrastructure provider where possible
- Minimize API key sprawl (currently 19+ in ~/.hermes/.env)

### 5. Full Inventory & Audit
- Catalog every API key and what it's for
- Catalog every cron/scheduled task and what it does
- Catalog every domain and what it hosts
- Find dead/unused services and kill them

---

## Execution Approach

### Session 1: Inventory Pull
- Audit ALL scheduled tasks (Claude, launchd, Paperclip)
- Audit ALL API keys and services
- Audit ALL domains and hosting
- Produce a complete inventory spreadsheet

### Session 2: Model Optimization
- Research GLM-5-Turbo, MiniMax v2.7, open-source alternatives
- Design tiered model routing (Opus → Sonnet → Haiku → open-source)
- Implement routing rules in OpenClaw/Paperclip

### Session 3: VoltAgent Import
- Clone repos, ingest skills into Obsidian + RAG
- Map skills to agent roster
- Build meta/super/sub-agent hierarchy

### Session 4: Service Consolidation
- Migrate what can move to Cloudflare
- Kill redundant services
- Consolidate API keys
- Update all scripts to use consolidated config

### Session 5: Testing & Validation
- End-to-end test all pipelines
- Cost tracking verification
- Performance benchmarks before/after

---

## Sources to Research
- https://github.com/VoltAgent/awesome-agent-skills
- https://github.com/VoltAgent
- GLM-5-Turbo pricing and capabilities
- MiniMax v2.7 API and pricing
- Current Anthropic spend (check billing dashboard)
