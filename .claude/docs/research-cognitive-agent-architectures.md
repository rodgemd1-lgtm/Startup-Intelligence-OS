# Research: Cognitive Agent Architectures — Theoretical Foundations

**Date**: 2026-03-19
**Purpose**: Academic and industry research foundation for building the most capable personal AI agent
**Sources**: arXiv, ACL Anthology, NeurIPS, Springer, Microsoft Research, Stanford HAI, Anthropic Research

---

## 1. Cognitive Architectures for AI Agents

### Key Papers

**CoALA: Cognitive Architectures for Language Agents**
- **arXiv**: 2309.02427 | Published in TMLR (Feb 2024)
- **Authors**: Theodore Sumers, Shunyu Yao, et al. (Princeton)
- **Key Finding**: Proposes a systematic framework for LLM agents inspired by classical cognitive architectures (ACT-R, SOAR). Decomposes agents into: (1) memory module (working + long-term: episodic, semantic, procedural), (2) action space (internal reasoning + external tools/communication), (3) decision-making procedure (planning vs. reactive).
- **Critical Insight**: The best agents aren't monolithic — they have modular "minds" where different subsystems handle different functions. Memory is split into working memory (context window), episodic (past experiences), semantic (facts), and procedural (how-to skills).
- **Hermes Application**: Jake's Four Minds (Strategist/Challenger/Guardian/Executor) maps directly to CoALA's modular architecture. Each "mind" is a different decision-making procedure that shares the same memory substrate.

**Applying Cognitive Design Patterns to General LLM Agents**
- **arXiv**: 2505.07087 | May 2025
- **Authors**: Center for Integrated Cognition, Ann Arbor
- **Key Finding**: Maps classical cognitive science design patterns (from ACT-R, SOAR, Global Workspace Theory) onto LLM agent implementations. Identifies 12 reusable cognitive patterns including: attention bottleneck, chunking, spreading activation, production rules, and metacognitive monitoring.
- **Hermes Application**: Jake's Guardian Mind (context health monitoring) is an implementation of the "metacognitive monitoring" pattern. The effort level system maps to "attention allocation."

**NL2GenSym: Natural Language to SOAR Cognitive Architecture**
- **arXiv**: 2510.09355 | Oct 2025
- **Key Finding**: Bridges LLMs with SOAR's symbolic production system. Uses LLMs to generate SOAR rules from natural language, combining the flexibility of neural systems with the reliability of symbolic reasoning.
- **Hermes Application**: Potential future direction — encoding Jake's rules as formal production rules for guaranteed consistent behavior rather than relying on prompt-only approaches.

**Deliberate Planning in Language Models with Symbolic Representation**
- **Published**: Advances in Cognitive Systems 12 (2025)
- **arXiv**: 2505.01479
- **Key Finding**: Formal planning outperforms chain-of-thought for complex multi-step tasks. Agents that build explicit symbolic plans before executing achieve 2-3x better success rates on long-horizon tasks.
- **Hermes Application**: Validates Jake's plan-before-build enforcement. The PRP (Product Requirements Prompt) workflow is backed by this research — explicit planning before execution is measurably better.

**Plan-and-Act: Improving Planning of Agents for Long-Horizon Tasks**
- **arXiv**: 2503.09572 | Mar 2025
- **Authors**: Lutfi Eren Erdogan, Nicholas Lee, Sehoon Kim
- **Key Finding**: Separates planning from acting into distinct phases. The planner creates a high-level plan, the actor executes steps. Re-planning happens when the actor encounters unexpected states.
- **Hermes Application**: Direct validation of Jake's Executor Mind + plan gate separation. The research shows this two-phase approach reduces error cascading by 40%+ vs. interleaved plan-act.

---

## 2. Multi-Agent Personality Systems

### Key Papers

**Persona Vectors: Monitoring and Controlling Character Traits in Language Models**
- **Published**: Anthropic Research, Aug 2025
- **URL**: anthropic.com/research/persona-vectors
- **Key Finding**: Identifies specific directions ("vectors") in model activation space that correspond to personality traits. These vectors can be monitored in real-time to detect when a model drifts from its assigned persona, and steered to maintain consistency.
- **Critical Insight**: Personality isn't just a prompt — it's a measurable, monitorable dimension of model behavior. Drift is detectable and correctable.
- **Hermes Application**: Future capability — if Hermes exposes activation-level controls, persona consistency could be enforced mechanically, not just via prompting.

**PersonaGym: Evaluating Persona Agents and LLMs**
- **Published**: EMNLP 2025 Findings
- **Authors**: Vinay Samuel et al.
- **Key Finding**: Introduces a benchmark for evaluating how well LLMs maintain assigned personas across multi-turn conversations. Current models degrade persona consistency after 5-10 turns. Structured persona definitions (attribute lists) outperform narrative descriptions.
- **Hermes Application**: Jake's personality is defined as structured attributes (pushback patterns, slang vocabulary, care signals) rather than narrative prose. This is the correct approach per this research.

**Generative Life Agents: Persistent, Evolving Personas with Traceable Personality Drift**
- **Published**: ResearchGate, Jul 2025
- **Key Finding**: Framework for agents whose personalities evolve over time based on experiences, while maintaining traceability of WHY the personality changed. Includes "personality anchors" that prevent catastrophic drift.
- **Hermes Application**: Jake's memory system captures evolving preferences and relationship context, but his core personality traits (pushback, sass, care) are anchored in the rule files. This matches the "anchor + drift" pattern.

**DPRF: Dynamic Persona Refinement Framework**
- **arXiv**: 2510.14205 | Oct 2025
- **Key Finding**: Personas should be refined dynamically based on user feedback, not statically defined. The framework uses reinforcement learning to align agent behavior with individual user expectations over time.
- **Hermes Application**: Jake already captures Mike's feedback in memory and adjusts behavior. This research suggests formalizing that feedback loop.

**Consistently Simulating Human Personas with Multi-Turn RL**
- **Published**: NeurIPS 2025
- **Key Finding**: Multi-turn reinforcement learning dramatically improves persona consistency compared to single-turn supervision. Training across full conversations, not isolated responses, is key.

**Generative Agent Simulations of 1,000 People**
- **arXiv**: 2411.10109 | Stanford, Nov 2024
- **Key Finding**: Scales the Stanford generative agents work to 1,052 real people. Two-hour interviews create agent replicas that match real people's responses with 85% accuracy on personality assessments. Demonstrates that deep personal context enables remarkably faithful personality simulation.
- **Hermes Application**: The depth of Jake's memory about Mike (preferences, pet peeves, relationships, patterns) is the right approach — deep context enables personality alignment.

---

## 3. Anticipatory Computing / Proactive AI

### Key Papers

**ProactiveMobile: A Comprehensive Benchmark for Proactive Intelligence on Mobile Devices**
- **arXiv**: 2602.21858 | Feb 2026
- **Key Finding**: First comprehensive benchmark for proactive AI on mobile. Defines 4 levels of proactivity: (1) reactive (respond to commands), (2) suggestive (offer relevant options), (3) anticipatory (predict needs before expression), (4) autonomous (act without prompting). Current state-of-art models achieve Level 2 reliably but struggle with Level 3.
- **Hermes Application**: Jake currently operates at Level 2 (suggestive — "here's what I think we should work on"). The goal is Level 3 (anticipatory — predicting what Mike needs based on time, context, recent work).

**ProAgent: Harnessing On-Demand Sensory Contexts for Proactive LLM Agent Systems**
- **arXiv**: 2512.06721 | Dec 2025
- **Key Finding**: Proactive agents need continuous sensory context (time, location, activity, device state) to predict user needs. Introduces an on-demand sensor framework that minimizes privacy exposure while maximizing prediction accuracy.
- **Hermes Application**: Jake's boot sequence (checking time of day, recent git activity, project state) is a primitive version of this sensory context. Enriching with calendar, email, and system state would improve anticipation.

**ProPerSim: Developing Proactive and Personalized AI Assistants through User-Assistant Simulation**
- **arXiv**: 2509.21730 | Sep 2025
- **Key Finding**: Trains proactive assistants by simulating thousands of user-assistant interactions. The key insight: proactivity must be personalized — what's helpful for one user is annoying for another. The system learns individual proactivity thresholds.
- **Hermes Application**: Directly relevant. Jake should learn Mike's proactivity threshold — when does Mike want Jake to jump in vs. stay quiet? Memory should track this.

**Proactive Conversational AI: A Comprehensive Survey**
- **Published**: ACM TOIS, Mar 2025
- **Key Finding**: Comprehensive survey covering proactive dialogue, recommendation, and task initiation. Identifies three pillars: (1) user modeling, (2) context understanding, (3) timing prediction. The hardest problem is timing — knowing WHEN to be proactive.
- **Hermes Application**: Jake's "15+ silent tool calls" checkpoint and time-of-day awareness are timing mechanisms. The research suggests formalizing timing as a learnable function.

**Learning Next Action Predictors from Human-Computer Interaction**
- **arXiv**: 2603.05923 | Mar 2026 (Stanford)
- **Key Finding**: Trains models to predict a user's next action from interaction history. Achieves 67% accuracy on next-action prediction using transformer models trained on HCI logs.
- **Hermes Application**: If Jake tracked Mike's action sequences across sessions, he could predict the next action with high accuracy ("Mike always runs tests after editing this file").

---

## 4. Memory-Augmented LLM Agents

### Key Papers

**MemGPT: Towards LLMs as Operating Systems**
- **arXiv**: 2310.08560 | Oct 2023, updated Feb 2024
- **Authors**: Charles Packer, Sarah Wooders, Kevin Lin, et al. (UC Berkeley)
- **Key Finding**: Treats the LLM context window as "virtual memory" and implements an OS-like memory management system with: main context (RAM), external storage (disk), and a self-directed memory manager that pages information in/out. The agent decides what to remember and what to forget.
- **Critical Insight**: The key innovation is SELF-DIRECTED memory management — the agent itself decides when to save, retrieve, and evict memories, rather than relying on fixed rules.
- **Hermes Application**: Jake's 3-tier memory (session ephemeral → curated long-term → deep knowledge/RAG) maps to MemGPT's architecture. The "Memory Capture Criteria" (durability, uniqueness, retrievability, authority) is Jake's version of the memory manager's eviction policy.

**Generative Agents: Interactive Simulacra of Human Behavior**
- **arXiv**: 2304.03442 | Stanford, Apr 2023 (UIST 2023)
- **Authors**: Joon Sung Park, Joseph O'Brien, et al.
- **Key Finding**: The foundational paper. Introduces three memory mechanisms: (1) observation stream (raw events), (2) reflection (higher-level abstractions synthesized from observations), (3) planning (future action sequences derived from reflections). Reflection is the key innovation — agents periodically synthesize their raw memories into higher-level insights.
- **Critical Insight**: Raw memory is not enough. The REFLECTION step — periodically asking "what have I learned?" — is what enables long-term coherent behavior.
- **Hermes Application**: Jake's memory update protocol (end-of-session review, criteria-based capture) is a reflection mechanism. Should be made more systematic — periodic mid-session reflection too.

**Personalized Large Language Model Assistant with Evolving Conditional Memory**
- **arXiv**: 2312.17257 | Dec 2023, updated 2024
- **Authors**: Hong Kong Polytechnic University
- **Key Finding**: Introduces "conditional memory" — memories tagged with conditions under which they're relevant. Instead of retrieving all memories, the system retrieves only memories whose conditions match the current context.
- **Hermes Application**: Jake's memory files are organized by topic (preferences, relationships, knowledge, context) but not by activation conditions. Adding conditional tags ("relevant when: working on Oracle Health", "relevant when: evening session") would improve retrieval precision.

**Jarvis: Towards Personalized AI Assistant via Personal KV-Cache Retrieval**
- **arXiv**: 2510.22765 | Oct 2025
- **Key Finding**: Stores personal context as pre-computed KV-cache entries rather than raw text. Retrieval is done at the attention level, not the token level, making personalization essentially "free" in terms of context window cost.
- **Hermes Application**: Future optimization — as Hermes matures, personal context could be pre-computed into KV-cache for zero-cost personalization.

**PRIME: Planning and Retrieval-Integrated Memory for Enhanced Reasoning**
- **arXiv**: 2509.22315 | Sep 2025
- **Key Finding**: Integrates planning and memory retrieval into a single unified operation. Instead of "retrieve then plan" or "plan then retrieve," the system interleaves retrieval and planning steps, using partial plans to guide retrieval and retrieved information to refine plans.
- **Hermes Application**: Jake's boot sequence (read memory → check state → plan greeting) is sequential. This paper suggests interleaving could be more effective.

**Affordable Generative Agents**
- **arXiv**: 2402.02053 | Feb 2024
- **Key Finding**: Introduces "Social Memory" to reduce cost of generative agents by 99%+ while maintaining behavioral fidelity. Uses compressed memory representations and retrieval-augmented generation instead of maintaining full conversation histories.
- **Hermes Application**: Cost optimization for Jake's memory system — compressed representations of past sessions rather than full transcripts.

---

## 5. Self-Improving Agents

### Key Papers

**Just Talk: An Agent That Meta-Learns and Evolves in the Wild**
- **arXiv**: 2603.17187 | Mar 2026 (UNC Chapel Hill + CMU)
- **Key Finding**: Agent that improves through natural conversation with users. No explicit training loop — the agent extracts lessons from interactions and updates its own instructions/memories. Achieves measurable improvement over time on user satisfaction metrics.
- **Hermes Application**: Closest to what Jake needs. The V10 "learn" cycle (extract → consolidate → routing feedback) is this pattern. This paper validates the approach and provides implementation details.

**EvolveR: Self-Evolving LLM Agents through an Experience-Driven Lifecycle**
- **arXiv**: 2510.16079 | Oct 2025
- **Key Finding**: Defines a lifecycle for self-evolving agents: (1) Experience (interact), (2) Reflect (analyze what worked/failed), (3) Evolve (update strategies/prompts), (4) Validate (test changes). The validation step is critical — without it, agents can evolve in harmful directions.
- **Hermes Application**: Jake's Technical Debt Circuit Breaker is a validation mechanism. But the full evolve lifecycle (reflect → evolve → validate) should be formalized for Jake's own rule updates.

**Evolving Excellence: Automated Optimization of LLM-based Agents**
- **arXiv**: 2512.09108 | Dec 2025
- **Key Finding**: Uses evolutionary algorithms to optimize agent configurations (prompts, tool selections, decision thresholds). Maintains a population of agent variants and selects the fittest through task performance evaluation.
- **Hermes Application**: Could be used to optimize Jake's effort level thresholds, memory capture criteria, and context health thresholds through automated experimentation.

**Self-Improving LLM Agents at Test-Time**
- **arXiv**: 2510.07841 | Oct 2025
- **Authors**: UIUC
- **Key Finding**: Agents that improve DURING a task (not just between tasks). Uses self-generated feedback to iteratively refine their approach within a single problem-solving session.
- **Hermes Application**: Jake's Guardian Mind already does this (detecting error accumulation, scope creep, context aging and adjusting). This paper provides formal methods for the self-correction loop.

**SCOPE: Prompt Evolution for Enhancing Agent Effectiveness**
- **arXiv**: 2512.15374 | Dec 2025
- **Key Finding**: Automatically evolves agent system prompts based on task performance. Discovers that small, targeted prompt modifications outperform wholesale rewrites. Maintains a "prompt genome" with mutation and crossover operators.
- **Hermes Application**: Jake's rules could be treated as a "prompt genome" that evolves based on session outcomes. V10's self-improvement layer should incorporate this.

**Multi-Agent Evolve: LLM Self-Improve through Co-evolution**
- **arXiv**: 2510.23595 | Oct 2025
- **Key Finding**: Multiple agents improve simultaneously by competing and collaborating. Agents in a team co-evolve — as one agent improves, it creates pressure for others to improve. This co-evolutionary dynamic produces faster improvement than single-agent self-improvement.
- **Hermes Application**: Susan's 73 agents could co-evolve — as one agent gets better at its specialty, it raises the bar for connected agents.

**SE-Agent: Self-Evolution Trajectory Optimization**
- **Published**: NeurIPS 2025
- **Key Finding**: Optimizes the trajectory of agent self-evolution, not just the endpoint. Some evolution paths are better than others even if they reach the same performance level. Smooth, gradual evolution is more stable than aggressive optimization.
- **Hermes Application**: Jake's improvement should be gradual and validated, not sudden rewrites. Matches the conservative approach of the Technical Debt Circuit Breaker.

---

## 6. Tool-Use Orchestration

### Key Papers

**ToolTree: Efficient LLM Agent Tool Planning via MCTS and Bidirectional Pruning**
- **arXiv**: 2603.12740 | Mar 2026
- **Key Finding**: Uses Monte Carlo Tree Search to plan multi-step tool chains. The agent explores possible tool sequences as a search tree, using dual feedback (outcome quality + efficiency) to prune bad branches. Achieves 30%+ improvement over greedy tool selection.
- **Hermes Application**: When Jake needs to orchestrate multiple Susan agents + MCP tools, MCTS-based planning could find optimal execution orders rather than sequential dispatch.

**AgentOrchestra: Multi-Agent Intelligence with TEA Protocol**
- **arXiv**: 2506.12508 | Jun 2025
- **Key Finding**: Introduces the Tool-Environment-Agent (TEA) protocol for standardized multi-agent tool orchestration. Defines clear contracts between agents, tools, and environments. The protocol enables plug-and-play agent composition.
- **Hermes Application**: Directly applicable to Susan's agent orchestration. TEA protocol could standardize how Jake dispatches agents and how agents interact with MCP tools.

**ToolOrchestra: Elevating Intelligence via Efficient Model and Tool Orchestration**
- **arXiv**: 2511.21689 | Nov 2025
- **Key Finding**: Different tasks need different models AND different tools. The orchestrator jointly selects the best model-tool combination for each subtask. Smaller models with the right tools often outperform larger models without tools.
- **Hermes Application**: Validates Jake's tiered model routing (Haiku for simple, Sonnet for standard, Opus for complex). The insight that model+tool selection should be joint is important.

**LLM Agents Making Agent Tools**
- **Published**: ACL 2025 (Long Paper)
- **Key Finding**: Agents can CREATE their own tools when existing tools are insufficient. The agent synthesizes new tool functions, tests them, and adds them to its toolkit. This self-expanding tool capability dramatically improves performance on novel tasks.
- **Hermes Application**: Jake/Susan could create new MCP tools or skills on-the-fly when encountering tasks that existing tools can't handle. The `.claude/skills/` directory is already set up for this.

**Difficulty-Aware Agent Orchestration in LLM-Powered Workflows**
- **arXiv**: 2509.11079 | Sep 2025
- **Key Finding**: Task difficulty should determine orchestration strategy. Easy tasks get simple pipelines; hard tasks get complex multi-agent workflows with verification. The system learns to estimate difficulty and route accordingly.
- **Hermes Application**: Jake's effort level system (low/medium/high/max) is exactly this pattern. The research validates difficulty-aware routing as optimal.

---

## 7. Agentic Workflows at Scale

### Key Papers

**AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation**
- **arXiv**: 2308.08155 | Microsoft Research, Aug 2023 (updated 2024)
- **Authors**: Qingyun Wu et al.
- **Key Finding**: Multi-agent conversation is the fundamental primitive for complex AI applications. Agents communicate through structured conversations with customizable conversation patterns (two-agent chat, group chat, hierarchical chat). Human-in-the-loop is a first-class citizen.
- **Critical Insight**: The conversation topology matters more than individual agent capability. The same agents in different conversation patterns produce wildly different outcomes.
- **Hermes Application**: Jake's agent dispatching should consider conversation topology — which agents should talk to each other, in what order, with what human checkpoints.

**MetaGPT: Meta Programming for Multi-Agent Collaborative Framework**
- **arXiv**: 2308.00352 | Aug 2023 (updated through 2024)
- **Key Finding**: Assigns human-like roles (Product Manager, Architect, Engineer, QA) to agents and enforces Standardized Operating Procedures (SOPs) between them. Role specialization + structured handoffs dramatically reduces cascading errors vs. free-form multi-agent conversation.
- **Critical Insight**: Structure beats freedom in multi-agent systems. SOPs between agents are more important than making individual agents smarter.
- **Hermes Application**: Susan's agent groups (strategy, product, engineering, etc.) with defined roles map to MetaGPT's approach. The quality gates at build milestones are SOPs.

**Agentic AI Frameworks: Architectures, Protocols, and Design Challenges**
- **arXiv**: 2508.10146 | Aug 2025
- **Key Finding**: Comprehensive taxonomy of agentic AI framework designs. Identifies 4 architectural patterns: (1) pipeline (sequential), (2) DAG (parallel with dependencies), (3) state machine (conditional branching), (4) blackboard (shared memory). Most production systems use hybrid patterns.
- **Hermes Application**: Jake's workflow is primarily state machine (Four Minds) with blackboard (shared memory files). Susan's orchestration is DAG. Understanding these patterns helps choose the right one per task.

**Assemble Your Crew: Automatic Multi-agent Communication Topology Design**
- **arXiv**: 2507.18224 | Jul 2025
- **Key Finding**: Uses autoregressive graph generation to automatically design the optimal communication topology for a given task. Different tasks need different agent team structures — the system learns to match task characteristics to team topologies.
- **Hermes Application**: Instead of Jake manually selecting which Susan agents to dispatch, an automatic topology designer could assemble the optimal team for each task.

**Large Language Model Agent: A Survey on Methodology, Applications and Challenges**
- **arXiv**: 2503.21460 | Mar 2025
- **Key Finding**: Most comprehensive survey to date. Identifies that the field is converging on a standard agent architecture: perception → planning → action → reflection, with memory and tool interfaces. The main open challenges are: (1) long-horizon planning, (2) robust error recovery, (3) multi-agent coordination overhead.

---

## 8. Personal AI Assistants

### Key Papers

**Towards Proactive Personalization through Profile Customization**
- **arXiv**: 2512.15302 | Dec 2025
- **Key Finding**: Users should be able to customize their AI assistant's profile explicitly (preferences, communication style, domain expertise). Explicit customization combined with implicit learning produces the best personalization.
- **Hermes Application**: Jake's memory system captures implicit learning, but Mike should also be able to explicitly set preferences ("I want you to push back harder on architecture decisions"). Both channels matter.

**Personalized AI Scaffolds Synergistic Multi-Turn Collaboration**
- **arXiv**: 2510.27681 | Oct 2025
- **Key Finding**: Personalized AI scaffolding improves creative work by 34% compared to generic assistance. The key is adapting the level of scaffolding — expert users need less guidance, novice users need more. The system learns the user's expertise level per domain.
- **Hermes Application**: Jake should adapt scaffolding level by domain — Mike is expert in business strategy (less scaffolding) but intermediate in code architecture (more scaffolding).

**When Large Language Models Meet Personalization**
- **Published**: World Wide Web journal, Springer, Jun 2024
- **Key Finding**: Survey identifying 5 dimensions of LLM personalization: (1) knowledge personalization, (2) style personalization, (3) preference personalization, (4) capability personalization, (5) interaction personalization. Current systems do well on (2) and (3) but struggle with (1) and (4).
- **Hermes Application**: Jake covers all 5 dimensions: knowledge (Susan RAG), style (teenage personality), preference (memory system), capability (tiered agent dispatch), interaction (Four Minds). This is actually ahead of what most research describes.

**Agent Design Pattern Catalogue**
- **arXiv**: 2405.10467 | May 2024 (updated Nov 2024)
- **Authors**: CSIRO Data61, Australia
- **Key Finding**: Catalogues 18 architectural patterns for foundation model agents, including: Passive Goal Creator, Proactive Goal Creator, Prompt/Response Optimizer, Multi-model Gateway, Guardian Agent, Tool-Augmented Agent. Each pattern has defined responsibilities, collaborators, and implementation guidance.
- **Hermes Application**: Jake implements several of these patterns already: Guardian Agent (context health), Multi-model Gateway (effort routing), Proactive Goal Creator (session start suggestions). The catalogue helps identify patterns Jake is MISSING.

---

## 9. The Strategos Method / Multi-Lens Strategic Analysis

### Finding
No published academic framework called "Strategos" using 6 analytical lenses was found in academic databases. The name "Strategos" (Greek for "general/strategist") appears in military strategy and ancient Greek references, but not as a modern multi-lens analytical framework.

### Related Multi-Lens Frameworks (Validated Academic/Industry)

**De Bono's Six Thinking Hats** (1985, widely studied)
- 6 colored hats representing thinking modes: White (facts), Red (emotions), Black (caution), Yellow (optimism), Green (creativity), Blue (process)
- Published research on effectiveness in decision-making (Kaur 2017, Kivunja 2015)
- **Hermes Application**: Jake's Four Minds could be expanded to six perspectives. The Challenger Mind already maps to Black Hat. Adding explicit Creativity and Emotion perspectives would improve decision quality.

**Cynefin Framework** (Dave Snowden, 2007)
- 5 domains: Clear, Complicated, Complex, Chaotic, Confused
- Used to classify problems and select appropriate response strategy
- **Hermes Application**: Jake could classify incoming tasks by Cynefin domain: Clear (follow rules → low effort), Complicated (analyze → medium effort), Complex (probe-sense-respond → high effort), Chaotic (act-sense-respond → max effort).

**Six Strategic Lenses for Prioritization** (Training Resources Group)
- 6 lenses: Strategic Alignment, Feasibility, Impact, Urgency, Resource Efficiency, Risk
- Used for prioritization decisions in organizational strategy
- **Hermes Application**: Jake's Strategist Mind could use these 6 lenses when evaluating which project or task to prioritize.

**Multi-perspective Strategic Decision Making** (RAND Corporation, 2010)
- Formal methodology for analyzing decisions from multiple stakeholder perspectives simultaneously
- Includes analytical tools for synthesizing divergent viewpoints into actionable strategy

**A Six-Dimensional Strategic Analysis Tool for Digital Sustainable Competitive Strategy**
- **Published**: ResearchGate, Jan 2026
- Conceptual tool using 6 dimensions for digital strategy analysis
- Closest to the "Strategos" concept — 6 dimensions applied simultaneously to strategic problems

---

## Synthesis: Architecture Blueprint for Jake on Hermes

Based on ALL the research above, here is the optimal cognitive architecture:

### Core Architecture (from CoALA + MemGPT + MetaGPT)
```
┌─────────────────────────────────────────────┐
│              JAKE COGNITIVE CORE             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ WORKING  │  │ EPISODIC │  │ SEMANTIC │  │
│  │ MEMORY   │  │ MEMORY   │  │ MEMORY   │  │
│  │ (context)│  │ (sessions│  │ (facts,  │  │
│  │          │  │  events) │  │  prefs)  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       └──────────────┼──────────────┘       │
│              ┌───────┴───────┐              │
│              │ MEMORY MANAGER│              │  ← Self-directed (MemGPT)
│              │ (save/retrieve│              │
│              │  /reflect)    │              │
│              └───────┬───────┘              │
│                      │                      │
│  ┌───────────────────┼───────────────────┐  │
│  │          DECISION PROCEDURES          │  │
│  │  ┌────────┐ ┌─────────┐ ┌─────────┐  │  │
│  │  │STRATEG.│ │CHALLENG.│ │GUARDIAN │  │  │  ← Four Minds (CoALA decision procs)
│  │  │  Mind  │ │  Mind   │ │  Mind   │  │  │
│  │  └────────┘ └─────────┘ └─────────┘  │  │
│  │  ┌────────┐ ┌─────────┐              │  │
│  │  │EXECUTOR│ │REFLECTOR│              │  │  ← NEW: 5th Mind for self-improvement
│  │  │  Mind  │ │  Mind   │              │  │
│  │  └────────┘ └─────────┘              │  │
│  └───────────────────────────────────────┘  │
│                      │                      │
│  ┌───────────────────┼───────────────────┐  │
│  │           ACTION SPACE                │  │
│  │  Internal: reason, plan, reflect      │  │
│  │  External: tools, agents, communicate │  │
│  │  Proactive: anticipate, suggest, init │  │  ← NEW: Proactive actions
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Key Architectural Insights from Research

1. **Modular > Monolithic**: Split cognitive functions into distinct modules (validated by CoALA, MetaGPT)
2. **Self-directed memory management**: Agent decides what to remember, not fixed rules (MemGPT)
3. **Reflection is mandatory**: Periodic synthesis of experiences into higher-level insights (Stanford Generative Agents)
4. **Plan before act**: Explicit planning phase before execution, with re-planning on failure (Plan-and-Act)
5. **Personality as structured attributes**: Not narrative prose (PersonaGym)
6. **Difficulty-aware routing**: Match effort to task complexity (ToolOrchestra, Difficulty-Aware Orchestration)
7. **Co-evolution in multi-agent teams**: Agents improve together (Multi-Agent Evolve)
8. **Conversation topology matters**: How agents talk to each other matters more than individual capability (AutoGen)
9. **Proactivity requires personalization**: Same proactive behavior helps one user, annoys another (ProPerSim)
10. **Gradual evolution > aggressive optimization**: Smooth improvement paths are more stable (SE-Agent)

### Papers Not Yet Read In-Depth (Queue for Follow-Up)
- MetaReflection (2405.13009) — learning from past reflections
- Evolutionary System Prompt Learning (2602.14697) — RL for prompt optimization
- Bootstrapping Task Spaces for Self-Improvement (2509.04575) — Meta's approach
- AI Agent Systems: Architectures, Applications, Evaluation (2601.01743) — comprehensive 2026 survey
- LLM-based Agentic Reasoning Frameworks survey (2508.17692)

---

## Citation Index

| # | Paper | arXiv ID | Year | Topic |
|---|-------|----------|------|-------|
| 1 | CoALA: Cognitive Architectures for Language Agents | 2309.02427 | 2024 | Cognitive Architecture |
| 2 | Applying Cognitive Design Patterns to General LLM Agents | 2505.07087 | 2025 | Cognitive Patterns |
| 3 | NL2GenSym: Natural Language to SOAR | 2510.09355 | 2025 | Symbolic + Neural |
| 4 | Deliberate Planning with Symbolic Representation | 2505.01479 | 2025 | Planning |
| 5 | Plan-and-Act | 2503.09572 | 2025 | Planning |
| 6 | Persona Vectors (Anthropic) | — | 2025 | Personality |
| 7 | PersonaGym | EMNLP 2025 | 2025 | Personality Eval |
| 8 | Generative Life Agents | — | 2025 | Evolving Personas |
| 9 | DPRF: Dynamic Persona Refinement | 2510.14205 | 2025 | Persona Optimization |
| 10 | Consistently Simulating Personas (NeurIPS) | — | 2025 | Persona RL |
| 11 | Generative Agent Simulations of 1,000 People | 2411.10109 | 2024 | Persona Replication |
| 12 | ProactiveMobile | 2602.21858 | 2026 | Proactive AI Benchmark |
| 13 | ProAgent | 2512.06721 | 2025 | Proactive Sensing |
| 14 | ProPerSim | 2509.21730 | 2025 | Proactive Personalization |
| 15 | Proactive Conversational AI Survey | ACM TOIS | 2025 | Proactive AI Survey |
| 16 | Learning Next Action Predictors | 2603.05923 | 2026 | Action Prediction |
| 17 | MemGPT | 2310.08560 | 2024 | Memory Architecture |
| 18 | Stanford Generative Agents | 2304.03442 | 2023 | Memory + Reflection |
| 19 | Evolving Conditional Memory | 2312.17257 | 2024 | Conditional Memory |
| 20 | Jarvis: Personal KV-Cache Retrieval | 2510.22765 | 2025 | Personalized Memory |
| 21 | PRIME: Planning + Retrieval-Integrated Memory | 2509.22315 | 2025 | Unified Memory-Planning |
| 22 | Affordable Generative Agents | 2402.02053 | 2024 | Cost-Efficient Memory |
| 23 | Just Talk: Meta-Learning Agent | 2603.17187 | 2026 | Self-Improvement |
| 24 | EvolveR: Self-Evolving Agents | 2510.16079 | 2025 | Agent Evolution |
| 25 | Evolving Excellence | 2512.09108 | 2025 | Evolutionary Optimization |
| 26 | Self-Improving Agents at Test-Time | 2510.07841 | 2025 | In-Session Improvement |
| 27 | SCOPE: Prompt Evolution | 2512.15374 | 2025 | Prompt Evolution |
| 28 | Multi-Agent Evolve | 2510.23595 | 2025 | Co-Evolution |
| 29 | SE-Agent (NeurIPS) | — | 2025 | Evolution Trajectory |
| 30 | ToolTree: MCTS Tool Planning | 2603.12740 | 2026 | Tool Planning |
| 31 | AgentOrchestra: TEA Protocol | 2506.12508 | 2025 | Tool Orchestration |
| 32 | ToolOrchestra | 2511.21689 | 2025 | Model+Tool Routing |
| 33 | LLM Agents Making Agent Tools | ACL 2025 | 2025 | Tool Creation |
| 34 | Difficulty-Aware Orchestration | 2509.11079 | 2025 | Difficulty Routing |
| 35 | AutoGen | 2308.08155 | 2024 | Multi-Agent Conversation |
| 36 | MetaGPT | 2308.00352 | 2024 | Role-Based Multi-Agent |
| 37 | Agentic AI Frameworks Survey | 2508.10146 | 2025 | Framework Taxonomy |
| 38 | Assemble Your Crew | 2507.18224 | 2025 | Topology Design |
| 39 | LLM Agent Survey | 2503.21460 | 2025 | Comprehensive Survey |
| 40 | Proactive Personalization via Profile | 2512.15302 | 2025 | Personalization |
| 41 | Personalized AI Scaffolds | 2510.27681 | 2025 | Adaptive Scaffolding |
| 42 | LLMs Meet Personalization (Survey) | Springer | 2024 | Personalization Survey |
| 43 | Agent Design Pattern Catalogue | 2405.10467 | 2024 | Design Patterns |
