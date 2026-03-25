# Research Packet: Agent Skills & Papers — Submodule Candidates

**Date:** 2026-03-25
**Researcher:** Jake (submodule research agent)
**Decision:** 5 submodules in vendor/ (all-in, no phasing)

---

## Submodule Assessment

### 1. danielmiessler/fabric — STRONG YES

| Field | Value |
|-------|-------|
| Stars | 40,200 |
| Last Update | March 2026 (active) |
| Patterns | **252 patterns** in `data/patterns/` |
| Structure | Each pattern = directory with `system.md` + optional `user.md`. Naming: `analyze_*`, `create_*`, `extract_*`, `summarize_*`. Machine-readable index at `pattern_descriptions.json` |
| License | MIT |
| Size | ~147 MB (includes Go CLI, web UI — we only need `data/patterns/`) |
| Integration | Index `data/patterns/` only. Each `system.md` is a self-contained prompt directly usable by Susan agents |
| Priority | **#1** — Miessler's own repo, referenced in process doctrine |

### 2. papers-we-love/papers-we-love — CONDITIONAL YES

| Field | Value |
|-------|-------|
| Stars | 104,000 |
| Last Update | June 2024 (stale, community-maintained) |
| Papers | **77 topic directories** — relevant: `artificial_intelligence/`, `distributed_systems/`, `machine_learning/`, `data_science/`, `operating_systems/` |
| Structure | Flat directory per topic. README files contain paper links/descriptions. Some PDFs hosted directly |
| License | Individual per paper |
| Size | ~225 MB (heavy — includes some PDF files) |
| Integration | Shallow clone, consider sparse checkout of relevant dirs only. Index README files for metadata |
| Concern | Size. Sparse checkout mitigates |

### 3. mergisi/awesome-openclaw-agents — YES

| Field | Value |
|-------|-------|
| Description | 162 production-ready AI agent templates for OpenClaw |
| Structure | SOUL.md configs across 19 categories |
| Integration | Direct reference for OpenClaw agent deployment patterns |
| Priority | **#2** — directly relevant to Phase 3X-D |

### 4. raulvidis/openclaw-multi-agent-kit — YES

| Field | Value |
|-------|-------|
| Description | Production-tested multi-agent orchestration with Telegram supergroup integration |
| Content | 10 agent personalities, shared context workflows, bot-to-bot communication |
| Integration | Architecture patterns for our 83-agent deployment |
| Priority | **#3** — THE deployment reference for Phase 3X-D |

### 5. NousResearch/hermes-agent — YES

| Field | Value |
|-------|-------|
| Stars | 6,000+ |
| Description | Self-improving agent with gateway, cron, memory patterns |
| Content | Python runtime, messaging gateway (Telegram/Discord/Slack), cron scheduler, tool framework |
| Size | ~50 MB |
| Integration | Reference implementation for agent architecture patterns |

### Rejected Candidates

| Repo | Stars | Reason |
|------|-------|--------|
| e2b-dev/awesome-ai-agents | 26,800 | Curated link list, not executable templates. 115MB for a README. Low value as submodule |
| kyrolabs/awesome-langchain | — | Link collection, no executable content |

## Final Submodule Selection

```bash
vendor/
├── fabric/                    # 252 prompt patterns (Miessler)
├── papers-we-love/            # 500+ CS papers (research layer)
├── awesome-openclaw-agents/   # 162 agent templates (deployment ref)
├── openclaw-multi-agent-kit/  # Multi-agent orchestration (architecture ref)
└── hermes-agent/              # Self-improving agent (runtime ref)
```

**Total indexed content:** ~5,000+ skills/patterns/papers/templates
**Total size:** ~640 MB (mitigated by shallow clones)
