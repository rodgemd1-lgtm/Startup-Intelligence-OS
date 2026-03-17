# Agentic Systems Knowledge Map — Q1 2026

Compiled: 2026-03-16. Full research packet at:
/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/artifacts/research/agentic-systems-state-of-art-2026-03-16.md

---

## Key Definitions (stable)

- Anthropic distinguishes: **workflow** (predefined code paths) vs. **agent** (LLM dynamically controls own process)
- **Augmented LLM** = base unit: LLM + retrieval + tools + memory
- **Orchestrator** = lead agent (Opus-class), **Subagent/Worker** = parallel specialists (Sonnet-class)
- **Trajectory** = complete execution history (reasoning + tool calls + outcomes) — raw material for self-improvement
- **Memory tip** = structured, reusable insight extracted from trajectories; injected at future task start

## Canonical Patterns (production-validated)

1. Prompt chaining (sequential, gated)
2. Routing (classifier → specialized downstream)
3. Parallelization (sectioning or voting)
4. Orchestrator-workers (dominant for complex open-ended tasks)
5. Evaluator-optimizer (generator + critic loop)
6. Full autonomous agent (open-ended tool-use loop with stopping conditions)

## Critical Benchmarks

- Multi-agent (Opus 4 + Sonnet 4 workers) vs. single Opus 4: +90.2% on research eval (Anthropic)
- TIMG memory tips on hard tasks: 19.1% → 47.6% SGC (+149% relative gain) (arXiv 2603.10600)
- Mem0 memory layer: 90% token reduction, 91% latency reduction (arXiv 2504.19413)
- Token overhead: single agent = 4x chat; multi-agent = 15x chat (Anthropic internal)
- 80% of BrowseComp performance variance explained by token budget alone (Anthropic)
- Model routing: 60-80% cost reduction documented in production

## Self-Improvement Methods (in order of production-readiness)

1. **TIMG** (trajectory-informed memory generation): no fine-tuning, inference-time only. arXiv 2603.10600
2. **Mem0** memory architecture: extract → consolidate → retrieve. arXiv 2504.19413
3. **DSPy**: automatic prompt optimization, gradient-free. dspy.ai
4. **TextGrad**: text backpropagation through LLM computation graphs
5. **Experience replay**: contextual replay buffers adapted for language agents (ACL 2025)

## Claude Code Hooks (all production-stable Q1 2026)

Full spec: code.claude.com/docs/en/hooks

Key hooks for automation:
- SessionStart: inject context, set env via $CLAUDE_ENV_FILE
- PreToolUse: approve/deny/modify tool calls before execution
- PostToolUse: audit, trigger side effects, inject additionalContext
- Stop: quality gate — can force Claude to continue (exit 2)
- SubagentStop: per-agent quality gate

Execution models: command (shell) | http (POST endpoint) | prompt (Haiku-class LLM) | agent (full Claude)

Hook scope: user settings | project settings | local settings | skill/agent frontmatter | managed policy

## Research API Landscape (Q1 2026)

- **Exa Deep**: $12-15/1k requests, 4-50s latency, parallel subagent search + LLM synthesis, structured JSON + citations
- **Exa Deep-Reasoning**: extended LLM reasoning, 12-50s, $15/1k
- **Tavily**: tiered pricing, general web research, has rate limits per plan
- **Firecrawl**: web crawl + structured extraction, per-page pricing
- **Perplexity Sonar**: fast factual retrieval, search-augmented generation

## Multi-Agent Memory Architecture (best practice)

Three tiers:
1. Working memory (in-context, per-agent, ephemeral)
2. Session memory (shared cache within a run — write plan here to survive context truncation)
3. Long-term memory (persistent vector store — Supabase pgvector, Pinecone, Weaviate + Mem0 extraction layer)

Conflict resolution hierarchy: timestamp < versioning < LLM arbitration < voting (by cost/quality)

## Production Failure Modes (Anthropic Research system)

1. Subagent spawning explosion — fix: explicit spawning budget in orchestrator prompt
2. Endless search loops — fix: quality-based stopping, not iteration count
3. Context overflow on lead agent — fix: write plan to memory at session start
4. Vague task delegation — fix: structured task format (objective, output format, tool guidance, boundaries)
5. Excessive inter-agent updates — fix: minimal structured update formats

## Authoritative Sources

- https://www.anthropic.com/research/building-effective-agents (Dec 2024)
- https://www.anthropic.com/engineering/multi-agent-research-system (Jun 2025)
- https://code.claude.com/docs/en/hooks
- arXiv 2603.10600 (TIMG, Mar 2026)
- arXiv 2504.19413 (Mem0, Apr 2025)
- dspy.ai — automatic prompt optimization
- mem0.ai — memory layer
- exa.ai/blog/exa-deep
