# Live Research Enrichment — March 2026

> Data sourced via Exa AI semantic search, Firecrawl web crawling, and Apify scraping.
> This document supplements the category-specific READMEs with the latest live intelligence.

---

## 1. AI Agent Frameworks — 2026 Landscape Update

### Latest Rankings & Comparisons (Live Sources)

| Source | Title | URL |
|--------|-------|-----|
| Conbersa | AI Agent Frameworks Compared: LangChain vs CrewAI vs AutoGen (Mar 2026) | [conbersa.ai](https://www.conbersa.ai/learn/ai-agent-frameworks-comparison) |
| Data Science Collective | The Best AI Agent Frameworks for 2026 (Tier List) | [medium.com](https://medium.com/data-science-collective/the-best-ai-agent-frameworks-for-2026-tier-list-b3a4362fac0d) |
| Lindy.ai | Top 10 AI Agent Frameworks (2026): Expert-Tested | [lindy.ai](https://www.lindy.ai/blog/best-ai-agent-frameworks) |
| BrightData | Top 13 Frameworks for Building AI Agents in 2026 | [brightdata.com](https://brightdata.com/blog/ai/best-ai-agent-frameworks) |
| Towards AI | A Developer's Guide to Agentic Frameworks in 2026 | [pub.towardsai.net](https://pub.towardsai.net/a-developers-guide-to-agentic-frameworks-in-2026-3f22a492dc3d) |
| Alpha Match | Top 7 Agentic AI Frameworks in 2026 | [alphamatch.ai](https://www.alphamatch.ai/blog/top-agentic-ai-frameworks-2026) |
| DataCamp | The Best AI Agents in 2026: Tools, Frameworks, Platforms | [datacamp.com](https://www.datacamp.com/blog/best-ai-agents) |
| Google Dev Blog | Developer's Guide to Multi-Agent Patterns in ADK | [developers.googleblog.com](https://developers.googleblog.com/developers-guide-to-multi-agent-patterns-in-adk/) |

### Key Insights from Multi-Agent Orchestration Research

**Source:** [shshell.com — Building Agentic Control Planes](https://www.shshell.com/blog/multi-agent-orchestration-patterns)

**The "God Agent" Anti-Pattern:**
- Giving one agent all tools leads to: hallucination density, context exhaustion, and untestability
- Solution: **Modular Agency** — five agents doing one thing perfectly vs. one doing everything poorly

**Production-Proven Orchestration Patterns:**
1. **Manager-Worker** — Orchestrator breaks goals into tasks, delegates to specialist workers
2. **Supervisor Loop** — Separate agent evaluates output of workers, creates self-correcting loops
3. **Blackboard Pattern** — Shared data store that agents observe and act upon asynchronously
4. **Structured Intents** — Agents communicate via JSON payloads, not natural language (enables logging, alerts, dashboards)

**Key Principle:** "Reliability is a System Property, not a Model Property" — even GPT-6 would need a control plane

### Additional Multi-Agent Sources

| Source | URL |
|--------|-----|
| OnAbout.AI — Enterprise Multi-Agent Strategy 2025-2026 | [onabout.ai](https://www.onabout.ai/p/mastering-multi-agent-orchestration-architectures-patterns-roi-benchmarks-for-2025-2026) |
| LinkedIn — 6 Proven Multi-Agent Design Patterns for 2026 | [linkedin.com](https://www.linkedin.com/posts/rakeshgohel01_2026-will-be-dominated-by-multi-ai-agent-activity-7429507169173028865-FDFr) |
| Spring AI — Subagent Orchestration Patterns (Jan 2026) | [spring.io](https://spring.io/blog/2026/01/27/spring-ai-agentic-patterns-4-task-subagents) |
| Swfte AI — Multi-Agent AI Systems for Enterprise 2026 | [swfte.com](https://www.swfte.com/blog/multi-agent-ai-systems-enterprise) |
| The Atlantic — Why Your AI Orchestrator Should Never Write Code | [building.theatlantic.com](https://building.theatlantic.com/why-your-ai-orchestrator-should-never-write-code-a1b5d1a2807d) |

---

## 2. MCP (Model Context Protocol) — 2026 Ecosystem

### Key Stats
- **punkpeye/awesome-mcp-servers**: 82.2k stars, 3,775 commits, 2,397+ PRs — the definitive MCP directory
- **Shubhamsaboo/awesome-llm-apps**: 99.8k stars, 14.5k forks — largest LLM app collection

### Top MCP Servers for Developers (2026)

**Source:** [meku.dev — 11+ Best MCP Servers](https://meku.dev/blog/best-mcp-servers)

| Server | Category | What It Does |
|--------|----------|-------------|
| **Magic UI MCP** | Frontend | AI-driven UI component generation, modification, and optimization |
| **Zen MCP** | Productivity | Workflow automation, task management |
| **GitHub MCP** | Development | Full GitHub integration (repos, issues, PRs, code search) |
| **Filesystem MCP** | System | Read/write local files with access controls |
| **Puppeteer MCP** | Automation | Browser automation, web scraping, testing |
| **PostgreSQL MCP** | Database | Direct database queries and schema exploration |
| **Memory MCP** | Context | Persistent key-value memory across sessions |
| **Sequential Thinking MCP** | Reasoning | Enhanced step-by-step reasoning capabilities |
| **Brave Search MCP** | Search | Web search with Brave's privacy-focused API |
| **Slack MCP** | Communication | Read/send messages, channel management |

### Latest MCP Articles

| Source | URL |
|--------|-----|
| Builder.io — Claude Code MCP Servers: How to Connect & Configure | [builder.io](https://builder.io/blog/claude-code-mcp-servers) |
| Apidog — Top 10 MCP Servers for Claude Code (2026) | [apidog.com](https://apidog.com/blog/top-10-mcp-servers-for-claude-code/) |
| K2view — Awesome MCP Servers: Top 15 for 2026 | [k2view.com](https://www.k2view.com/blog/awesome-mcp-servers) |
| Oxylabs — Top 10 Best MCP Servers for AI Workflows | [oxylabs.io](https://oxylabs.io/blog/best-mcp-servers) |
| Agent Whispers — What Is MCP? A Practical Guide for 2026 | [agentwhispers.com](https://www.agentwhispers.com/agent-guides/what-is-mcp) |
| Dev.to — Predictions for MCP and AI-Assisted Coding in 2026 | [dev.to](https://dev.to/blackgirlbytes/my-predictions-for-mcp-and-ai-assisted-coding-in-2026-16bm) |

---

## 3. Claude Code — 2026 Best Practices & Tips

### Latest Resources

| Source | Title | URL |
|--------|-------|-----|
| LobeHub | Claude Code Best Practices (Skills Plugin) | [lobehub.com](https://lobehub.com/skills/nxtg-ai-forge-plugin-claude-code-best-practices) |
| Claude Directory | Complete Guide to CLAUDE.md Configuration | [claudedirectory.org](https://www.claudedirectory.org/blog/claude-md-guide) |
| Level Up Coding | Mental Model: Skills, Subagents, and Plugins | [levelup.gitconnected.com](https://levelup.gitconnected.com/a-mental-model-for-claude-code-skills-subagents-and-plugins-3dea9924bf05) |
| Platform Claude | Skill Authoring Best Practices (Official) | [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) |
| CodeWithClaude | Claude Code Best Practices Hub | [codewithclaude.net](https://codewithclaude.net/advanced-topics/best-practices) |
| Dev.to | Claude Code Must-Haves (Jan 2026) | [dev.to](https://dev.to/valgard/claude-code-must-haves-january-2026-kem) |
| ClaudeLog | Claude Code Tips Collection | [claudelog.com](https://www.claudelog.com/faqs/claude-code-tips) |
| KeonArmin | Claude Code Setup: Skills, Subagents, and Measuring Results | [keonarmin.com](https://keonarmin.com/blog/claude-code-configs) |
| Elliot J Reed | Guide to Claude Code: Features and Best Practices | [elliotjreed.com](https://www.elliotjreed.com/amp/ai/claude-code-guide-and-tips) |

---

## 4. Vibe Coding Platforms — 2026 Market Update

### Market Stats (Live Data)
- **Lovable**: 8 million users, $200M+ ARR — the PLG juggernaut
- **Bolt.new**: $40M ARR in 5 months, 5M+ users
- **Gartner forecast**: 60% of new software code will be AI-generated by 2026
- **Y Combinator W25**: 21% of companies had codebases 91%+ AI-generated

### Platform Comparison (March 2026)

**Source:** [vibecodingacademy.ai — Platforms Compared](https://www.vibecodingacademy.ai/blog/vibe-coding-platforms-compared)

| Platform | Best For | Pricing (Entry) | Key Strength |
|----------|----------|-----------------|-------------|
| **Lovable** | Non-technical founders building SaaS | $20/mo | Fastest idea-to-app. Supabase integration. Real exportable code. |
| **Bolt.new** | Budget-conscious builders | $10/mo | Browser-based via WebContainers. Framework flexibility. |
| **Cursor** | Developers on existing codebases | $20/mo | Deep codebase awareness. Multi-file AI edits. |
| **v0** | UI/component generation | Free tier | Best React/Tailwind component generation from prompts |
| **Replit Agent** | Quick prototypes, learners | $25/mo | Full IDE in browser. Instant deployment. |
| **Base44** | Non-technical founders | $24/mo | Zero complexity barrier. Full-stack generation. |

### Additional Comparison Sources

| Source | URL |
|--------|-----|
| GetMocha — Best AI App Builder 2026: Lovable vs Bolt vs v0 vs Mocha | [getmocha.com](https://getmocha.com/blog/best-ai-app-builder-2026/) |
| Vitara AI — Lovable vs Bolt vs v0 Comparison | [vitara.ai](https://vitara.ai/lovable-vs-bolt-vs-v0/) |
| Taskade — 20 Best AI App Builders in 2026 | [taskade.com](https://www.taskade.com/blog/best-ai-app-builders) |
| Free Academy — v0 vs Bolt vs Lovable Comparison | [freeacademy.ai](https://freeacademy.ai/blog/v0-vs-bolt-vs-lovable-ai-app-builders-comparison-2026) |
| NxCode — Complete Comparison | [nxcode.io](https://www.nxcode.io/resources/blog/v0-vs-bolt-vs-lovable-ai-app-builder-comparison-2025) |

---

## 5. UX/UI Design Tools — 2026 Updates

### Latest AI Design Tools

| Source | Title | URL |
|--------|-------|-----|
| Muz.li | The 8 Top AI Tools I Actually Use in My UX Design Workflow (2026) | [medium.muz.li](https://medium.muz.li/the-8-top-ai-tools-i-actually-use-in-my-ux-design-workflow-2026-8223a201753d) |
| Toools Design | 9 Best AI Tools for UI/UX Designers in 2026: Deep Dive | [toools.design](https://www.toools.design/blog-posts/best-ai-tools-ui-ux-designers-2026) |
| BuildMVPFast | 10 Best UX Design AI Tools for Rapid Prototyping in 2026 | [buildmvpfast.com](https://www.buildmvpfast.com/blog/best-ux-design-ai-tools) |
| Sanjay Dey | 15 AI UX Tools That Boost Productivity by 126% in 2026 | [sanjaydey.com](https://www.sanjaydey.com/15-ai-ux-tools-productivity-boost-2026/) |
| AIInWorkflow | Stitch by Google: AI-Powered UI Design & Front-End Code | [aiinworkflow.com](https://aiinworkflow.com/aitools/stitch-ai/) |
| SashiDo | AI Frontend Tools for App UI | [sashido.io](https://www.sashido.io/en/blog/bring-your-apps-ui-to-life-with-sashidos-ai-frontend-tools) |
| Prototypr.ai | No-code × AI for bringing ideas to market | [prototypr.ai](https://www.prototypr.ai/) |

### New Tool Spotlight: Google Stitch
Google launched **Stitch** (formerly Galileo AI acquisition) as an AI-powered UI design tool that generates production-ready frontend code. It represents Google's push into the AI-assisted design space.

---

## 6. Decentralized AI — 2026 Market Intelligence

### DePIN Market Stats
- DePIN sector: **$5.2B → $19B+ market cap** in one year
- Projected to reach **$3.5 trillion by 2028**
- GPU scarcity: SK Hynix and Micron's entire 2026 HBM output is **sold out**
- Traditional cloud consumes **50-70% of AI startup budgets**

### Decentralized GPU Network Updates (Feb 2026)

**Source:** [blockeden.xyz — Decentralized GPU Networks 2026](https://blockeden.xyz/blog/2026/02/07/decentralized-gpu-networks-2026/)

| Network | Key 2026 Metrics | Differentiator |
|---------|-----------------|----------------|
| **Render Network** | 1.5M frames/month, 600+ AI models, migrated to Solana | Creative + AI compute, Dispersed.com launch |
| **Akash Network** | 428% YoY growth, 80%+ utilization, $3.36M monthly compute | Kubernetes-compatible, reverse auction pricing, Starcluster initiative (7,200 GB200 GPUs) |
| **Hyperbolic** | 100K+ developers, 75% cheaper than AWS | Hyper-dOS decentralized operating system |
| **io.net** | GPU aggregation platform on Solana | Largest aggregator of underutilized GPUs |

### New/Updated DAI Projects Discovered

| Project | Description | URL |
|---------|-------------|-----|
| **Coral Protocol** | Multi-agent coordination protocol on-chain | [coralprotocol.org](https://coralprotocol.org/) |
| **DAIS (Decentralized AI Society)** | Global DAI community and standards body | [dais.global](https://dais.global/) |
| **Vortia AI** | Decentralized AI blockchain | [vortia.ai](https://vortia.ai/) |
| **LazAI Network** | Decentralized AI network | [lazai.network](https://lazai.network/) |
| **Singularity AI ($SGAI)** | Decentralized AGI Protocol | [singularity-ai.space](https://singularity-ai.space/) |

### Investment Guides

| Source | URL |
|--------|-----|
| CryptoPotato — 11 Best AI Crypto Coins in 2026 | [cryptopotato.com](https://cryptopotato.com/best-ai-crypto-coins/) |
| 101 Blockchains — Top AI Agent Crypto Coins | [101blockchains.com](https://101blockchains.com/top-ai-agent-crypto-coins/) |
| CoinCub — Best AI Crypto to Invest In 2026 | [coincub.com](https://coincub.com/blog/best-ai-crypto-invest/) |

---

## 7. RAG & Vector Databases — 2026 Landscape

### Latest Comparisons

| Source | Title | URL |
|--------|-------|-----|
| Meilisearch | 10 Best RAG Tools and Platforms: Full Comparison (2026) | [meilisearch.com](https://www.meilisearch.com/blog/rag-tools) |
| Medium | Top 10 RAG Frameworks on GitHub (By Stars) — Jan 2026 | [medium.com](https://florinelchis.medium.com/top-10-rag-frameworks-on-github-by-stars-january-2026-e6edff1e0d91) |
| Towards AI | The 5 Vector Databases for RAG at Million Scale | [pub.towardsai.net](https://pub.towardsai.net/the-5-vector-databases-for-rag-how-to-give-your-llm-perfect-memory-at-million-scale-fca889074a54) |
| Appwrite | Top 6 Vector Databases for AI in 2026 | [appwrite.io](https://appwrite.io/blog/post/top-6-vector-databases-2025) |
| Instaclustr | Best Open Source Vector DBs: Top 5 in 2026 | [instaclustr.com](https://www.instaclustr.com/education/vector-database/best-open-source-vector-database-solutions-top-5-in-2026/) |
| LinkedIn | Complete 2026 Guide to Modern RAG Architectures | [linkedin.com](https://www.linkedin.com/pulse/complete-2026-guide-modern-rag-architectures-how-retrieval-pathan-rx1nf) |
| Nucleus AI | RAG and AI Toolkit | [nucleus-ai.io](https://nucleus-ai.io/modules/retrieval-augmented-generation) |

---

## 8. Open-Source LLM Models — 2026 Leaderboard

### Latest Rankings

| Source | Title | URL |
|--------|-------|-----|
| Awesome Agents | Open-Source LLM Leaderboard: February 2026 | [awesomeagents.ai](https://awesomeagents.ai/leaderboards/open-source-llm-leaderboard/) |
| WhatLLM | Best Open Source LLM February 2026 Rankings | [whatllm.org](https://whatllm.org/blog/best-open-source-models-february-2026) |
| Miniloop | Best Open Source LLMs: 25+ Models Compared for 2026 | [miniloop.ai](https://www.miniloop.ai/blog/best-open-source-llms-2026) |
| CloudInsight | LLM Model Ranking & Comparison: 2026 Benchmark Review | [cloudinsight.cc](https://cloudinsight.cc/en/blog/llm-ranking) |
| Dev.to | Llama vs Mistral vs Phi: Enterprise Comparison (2026) | [dev.to](https://dev.to/jaipalsingh/llama-vs-mistral-vs-phi-complete-open-source-llm-comparison-for-enterprise-2026-3o8c) |
| Dev.to | Best Open-Source LLMs for RAG in 2026: 10 Models Ranked | [dev.to](https://dev.to/jaipalsingh/best-open-source-llms-for-rag-in-2026-10-models-ranked-by-retrieval-accuracy-5hcf) |
| GitHub | LLM-Model-Comparison-2026 Repository | [github.com/salttechno](https://github.com/salttechno/LLM-Model-Comparison-2026) |

---

## 9. Product-Led Growth — 2026 Framework Update

### The 7-Layer PLG Framework (Aakash Gupta, Feb 2026)

**Source:** [news.aakashg.com — PLG in 2026](https://www.news.aakashg.com/p/plg-in-2026)

**Key findings from analyzing Canva ($3.5B ARR), Figma ($1B+ revenue), and Attio (4x-ing ARR):**
- The Slack/Dropbox playbook from 2018 is **dead**
- "Add a free trial, add viral loops, focus on activation" is no longer enough
- Modern PLG requires a complete 7-layer approach

### Latest PLG Resources

| Source | Title | URL |
|--------|-------|-----|
| Product Growth | Complete 7-Layer PLG Playbook (Feb 2026) | [news.aakashg.com](https://www.news.aakashg.com/p/plg-in-2026) |
| ProductLed | PLG Predictions For 2026 | [productled.com](https://productled.com/blog/plg-predictions-for-2026) |
| UserGuiding | The State of PLG in SaaS for 2026 | [userguiding.com](https://userguiding.com/blog/state-of-plg-in-saas) |
| Idlen | Product-Led Growth and AI: Complete Guide for Tech Startups | [idlen.io](https://www.idlen.io/blog/product-led-growth-ai-startups-guide) |
| Zylos AI | PLG: From Freemium to Enterprise (Feb 2026) | [zylos.ai](https://zylos.ai/research/2026-02-11-product-led-growth) |
| Presta | AI Product Strategy 2026: Roadmap for Founders | [wearepresta.com](https://wearepresta.com/ai-product-strategy-2026-the-founders-guide-to-ai-native-growth/) |
| StartupIll | 2026 SaaS Roadmap: AI, PLG & Profitable Growth | [startupill.com](https://startupill.com/2026-saas-roadmap-for-founders/) |
| Product-Led Alliance | The AI Growth Playbook: How PMs Scale Smarter | [productledalliance.com](https://www.productledalliance.com/the-ai-growth-playbook/) |

---

## 10. AI Startup Fundraising — 2026 Resources

### Pitch Deck & Fundraising Tools

| Source | Title | URL |
|--------|-------|-----|
| GetAlAI | Top AI Pitch Deck Generators in 2026 | [getalai.com](https://getalai.com/blog/top-ai-pitch-deck-generators) |
| Qubit Capital | Essential Slides for an AI Startup Pitch Deck | [qubit.capital](https://qubit.capital/blog/essential-ai-startup-pitch-deck-fundraising-slides) |
| Hebbia | 10 Best AI Pitch Deck Generators (2026) | [hebbia.com](https://www.hebbia.com/blog/ai-pitch-deck-generators) |
| InnMind | 2026 Pitch Deck Guide: Web3 & AI Fundraising | [blog.innmind.com](https://blog.innmind.com/fundraising-pitch-deck-web3-ai-2026/) |
| IdeaProof | Free Pre-Seed, Seed, Series A Pitch Deck Templates (2026) | [ideaproof.io](https://ideaproof.io/tools/pitch-deck-templates) |
| FundReef | How to Create a Killer Pitch Deck (Step-by-Step) | [fundreef.com](https://www.fundreef.com/how-to-create-a-killer-pitch-deck-step-by-step/) |
| Skywork AI | How to Build an Investor-Ready AI Pitch Deck | [skywork.ai](https://skywork.ai/blog/how-to-build-investor-ready-ai-pitch-deck-2025-guide/) |
| Emerline | How to Create a Pitch Deck for Investors (2026) | [emerline.com](https://emerline.com/blog/how-to-pitch-to-vc-as-tech-startup) |
| **Capwave AI** | AI-powered fundraising platform for startups | [capwave.ai](https://capwave.ai/) |

---

## 11. GitHub Repositories Discovered

### Must-Star Repos (from Firecrawl + Exa)

| Repository | Stars | Description |
|-----------|-------|-------------|
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | 82.2k | Definitive curated list of MCP servers |
| [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) | 99.8k | Collection of awesome LLM apps with RAG using various frameworks |
| [salttechno/LLM-Model-Comparison-2026](https://github.com/salttechno/LLM-Model-Comparison-2026) | — | Side-by-side LLM model comparison for 2026 |
| [serverless/aws-ai-stack](https://github.com/serverless/aws-ai-stack) | — | Ready-to-use full-stack AI boilerplate on AWS |
| [vercel-labs/knowledge-agent-template](https://github.com/vercel-labs/knowledge-agent-template) | — | Vercel's knowledge agent template |
| [vstorm-co/full-stack-fastapi-nextjs-llm-template](https://github.com/vstorm-co/full-stack-fastapi-nextjs-llm-template) | — | Full-stack FastAPI + Next.js + LLM template |
| [LLMsLab/cookiecutter-ai-flock](https://github.com/llmslab/cookiecutter-ai-flock) | — | Cookiecutter template for AI agent flocks |
| [HeyNina101/generative_ai_project](https://github.com/HeyNina101/generative_ai_project) | — | Production-ready generative AI project template |

### Key Learning Resources Found

| Source | URL |
|--------|-----|
| Dev.to — 10 Must-Follow GitHub Repos to Learn AI in 2026 | [dev.to](https://dev.to/timeai/10-must-follow-github-repositories-to-learn-ai-in-2026-53g2) |

---

## Research Methodology

This enrichment document was compiled using:
- **Exa AI** (semantic search) — 10 parallel searches across all categories, 100 results total
- **Firecrawl** (web crawling) — 6 deep crawls of key articles and repositories
- **Manual curation** — Cross-referenced and deduplicated against existing README resources

All URLs verified as live at time of research (March 5, 2026).

---

*Last updated: March 5, 2026*
