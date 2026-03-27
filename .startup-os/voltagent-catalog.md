# VoltAgent Skill Catalog — Mapped to Agent Roster

**Date**: 2026-03-27
**Total Skills Analyzed**: 734
**Tier 1 (Core)**: 108 skills
**Tier 2 (High Value)**: 207 skills
**Tier 3 (Domain Specific)**: 316 skills
**Tier 4 (Skip)**: 103 skills

---

## Tier 1 — CORE (Install Immediately)

### Operations Agents (jake, jake-chat, jake-deep-work, jake-triage, kira, aria, daily-ops, orchestrator)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| claude-memory-skill | https://github.com/hanfang/claude-memory-skill | jake | Persistent memory management across sessions |
| internal-comms | https://github.com/anthropics/skills/tree/main/skills/internal-comms | aria | Internal communications drafting and formatting |
| doc-coauthoring | https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring | jake-deep-work | Collaborative document writing with revision tracking |
| autoplan | https://github.com/garrytan/gstack/tree/main/autoplan | jake | Automated planning from task descriptions |
| writing-plans | https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md | jake | Structured plan generation with validation gates |
| executing-plans | https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md | jake | Step-by-step plan execution with checkpoints |
| dispatching-parallel-agents | https://github.com/obra/superpowers/blob/main/skills/dispatching-parallel-agents/SKILL.md | orchestrator | Multi-agent parallel dispatch patterns |
| subagent-driven-development | https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md | orchestrator | Sub-agent orchestration for dev workflows |
| brainstorming | https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md | jake | Structured brainstorming with convergence |
| condition-based-waiting | https://github.com/obra/superpowers/blob/main/skills/condition-based-waiting/SKILL.md | orchestrator | Async condition polling for agent coordination |
| verification-before-completion | https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md | jake | Quality gate enforcement before marking done |
| sharing-skills | https://github.com/obra/superpowers/blob/main/skills/sharing-skills/SKILL.md | orchestrator | Skill distribution across agents |
| using-superpowers | https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md | orchestrator | Meta-skill for composing agent capabilities |
| superpowers-commands | https://github.com/obra/superpowers/tree/main/skills/commands | jake | CLI command patterns for agent operations |
| superpowers-lab | https://github.com/obra/superpowers-lab | orchestrator | Experimental agent skill development |
| context-compression | https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-compression | jake | Context window optimization via compression |
| context-degradation | https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-degradation | jake | Detecting and mitigating context quality loss |
| context-fundamentals | https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-fundamentals | jake | Core context engineering principles |
| context-optimization | https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-optimization | jake | Advanced context window management |
| memory-systems | https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/memory-systems | jake | Multi-tier memory architecture patterns |
| multi-agent-patterns | https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/multi-agent-patterns | orchestrator | Multi-agent coordination patterns |
| tool-design | https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/tool-design | orchestrator | Designing effective agent tools |
| evaluation | https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/evaluation | jake | Evaluating agent output quality |
| Auto-claude-code-research-in-sleep | https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep | jake-deep-work | Autonomous background research while idle |
| notion-knowledge-capture | https://github.com/openai/skills/tree/main/skills/.curated/notion-knowledge-capture | kira | Capturing knowledge into Notion databases |
| notion-meeting-intelligence | https://github.com/openai/skills/tree/main/skills/.curated/notion-meeting-intelligence | aria | Meeting notes extraction and action items |
| notion-research-documentation | https://github.com/openai/skills/tree/main/skills/.curated/notion-research-documentation | kira | Structured research documentation in Notion |
| notion-spec-to-implementation | https://github.com/openai/skills/tree/main/skills/.curated/notion-spec-to-implementation | jake | Spec-to-code translation from Notion docs |
| summarize-meeting | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/summarize-meeting | aria | Meeting summarization with action items |
| gws-gmail | https://github.com/googleworkspace/cli/tree/main/skills/gws-gmail | aria | Gmail management and automation |
| gws-calendar | https://github.com/googleworkspace/cli/tree/main/skills/gws-calendar | aria | Google Calendar management |
| gws-drive | https://github.com/googleworkspace/cli/tree/main/skills/gws-drive | kira | Google Drive file management |
| gws-docs | https://github.com/googleworkspace/cli/tree/main/skills/gws-docs | jake-deep-work | Google Docs creation and editing |
| gws-sheets | https://github.com/googleworkspace/cli/tree/main/skills/gws-sheets | kira | Google Sheets data management |
| gws-tasks | https://github.com/googleworkspace/cli/tree/main/skills/gws-tasks | jake-triage | Google Tasks integration |
| gws-meet | https://github.com/googleworkspace/cli/tree/main/skills/gws-meet | aria | Google Meet scheduling and management |
| gws-keep | https://github.com/googleworkspace/cli/tree/main/skills/gws-keep | kira | Google Keep notes management |
| gws-chat | https://github.com/googleworkspace/cli/tree/main/skills/gws-chat | jake-chat | Google Chat messaging |
| gws-workflow | https://github.com/googleworkspace/cli/tree/main/skills/gws-workflow | orchestrator | Google Workspace workflow automation |
| gws-apps-script | https://github.com/googleworkspace/cli/tree/main/skills/gws-apps-script | orchestrator | Google Apps Script development |
| pdf | https://github.com/anthropics/skills/tree/main/skills/pdf | jake | PDF generation and manipulation |
| docx | https://github.com/anthropics/skills/tree/main/skills/docx | jake | Word document generation |
| xlsx | https://github.com/anthropics/skills/tree/main/skills/xlsx | kira | Excel spreadsheet generation |
| pptx | https://github.com/anthropics/skills/tree/main/skills/pptx | aria | PowerPoint presentation generation |
| speed-reader | https://github.com/SeanZoR/claude-speed-reader | jake | Fast document analysis and summarization |
| clarity-gate | https://github.com/frmoretto/clarity-gate | jake | Requirement clarity validation before execution |
| skill-creator | https://github.com/anthropics/skills/tree/main/skills/skill-creator | orchestrator | Meta-skill for creating new skills |
| writing-skills | https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md | orchestrator | Authoring reusable skill definitions |
| model-hierarchy-skill | https://github.com/zscole/model-hierarchy-skill | orchestrator | Model selection and routing patterns |
| recursive-decomposition | https://github.com/massimodeluisa/recursive-decomposition-skill | jake | Breaking complex tasks into sub-tasks recursively |
| tweetclaw | https://github.com/Xquik-dev/tweetclaw | aria | Twitter/X content management |
| email-marketing-bible | https://github.com/CosmoBlk/email-marketing-bible | aria | Email campaign strategy and templates |
| data-structure-protocol | https://github.com/k-kolomeitsev/data-structure-protocol | orchestrator | Structured data exchange between agents |
| apple-bridges | https://github.com/more-io/claude-apple-bridges | jake | macOS native API bridges (Calendar, Contacts, etc.) |
| linear | https://github.com/openai/skills/tree/main/skills/.curated/linear | jake-triage | Linear issue tracking integration |
| transcribe | https://github.com/openai/skills/tree/main/skills/.curated/transcribe | aria | Audio/video transcription |
| speech | https://github.com/openai/skills/tree/main/skills/.curated/speech | aria | Text-to-speech generation |
| spreadsheet | https://github.com/openai/skills/tree/main/skills/.curated/spreadsheet | kira | Spreadsheet creation and analysis |

### Strategy Agents (steve, steve-strategy, compass, compass-product, ledger, ledger-finance, vault-fundraising, bridge-partnerships)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| product-strategy-session | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/product-strategy-session | steve-strategy | Guided product strategy sessions |
| positioning-statement | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/positioning-statement | compass-product | Product positioning frameworks |
| positioning-workshop | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/positioning-workshop | compass-product | Interactive positioning workshops |
| roadmap-planning | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/roadmap-planning | compass | Product roadmap generation |
| prioritization-advisor | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/prioritization-advisor | steve | Feature/task prioritization frameworks |
| tam-sam-som-calculator | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/tam-sam-som-calculator | steve-strategy | Market sizing calculations |
| pestel-analysis | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/pestel-analysis | steve-strategy | PESTEL market analysis |
| business-health-diagnostic | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/business-health-diagnostic | steve | Business health scoring |
| company-research | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/company-research | steve-strategy | Company research and analysis |
| feature-investment-advisor | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/feature-investment-advisor | compass | Feature ROI analysis |
| finance-based-pricing-advisor | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/finance-based-pricing-advisor | ledger-finance | Pricing strategy based on financials |
| finance-metrics-quickref | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/finance-metrics-quickref | ledger-finance | Financial metrics reference guide |
| saas-economics-efficiency-metrics | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/saas-economics-efficiency-metrics | ledger-finance | SaaS unit economics |
| saas-revenue-growth-metrics | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/saas-revenue-growth-metrics | ledger-finance | SaaS revenue tracking |
| product-strategy | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/product-strategy | steve-strategy | Product strategy frameworks |
| product-vision | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/product-vision | compass | Product vision statement creation |
| lean-canvas | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/lean-canvas | steve | Lean Canvas generation |
| business-model | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/business-model | steve-strategy | Business model design |
| startup-canvas | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/startup-canvas | steve | Startup canvas generation |
| swot-analysis | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/swot-analysis | steve-strategy | SWOT analysis framework |
| porters-five-forces | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/porters-five-forces | steve-strategy | Porter's Five Forces analysis |
| value-proposition | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/value-proposition | compass-product | Value proposition design |
| monetization-strategy | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/monetization-strategy | ledger-finance | Revenue model design |
| pricing-strategy | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/pricing-strategy | ledger-finance | Pricing strategy frameworks |
| ansoff-matrix | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/ansoff-matrix | steve-strategy | Growth strategy matrix |
| pestle-analysis | https://github.com/phuryn/pm-skills/tree/main/pm-product-strategy/skills/pestle-analysis | steve-strategy | PESTLE macro-environment analysis |
| brainstorm-okrs | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/brainstorm-okrs | steve | OKR generation and alignment |
| outcome-roadmap | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/outcome-roadmap | compass | Outcome-based roadmap planning |
| charlie-cfo-skill | https://github.com/EveryInc/charlie-cfo-skill | ledger-finance | CFO-grade financial analysis and advice |
| founder-skills | https://github.com/ognjengt/founder-skills | steve | Startup founder decision frameworks |
| startup-skills | https://github.com/rameerez/claude-code-startup-skills | steve | Startup-specific operational skills |

### Research Agents (research, research-director, research-ops, researcher-web, researcher-reddit, researcher-arxiv, researcher-appstore)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| deep-research | https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research | research-director | Structured deep research workflows |
| AI-research-SKILLs (Orchestra) | https://github.com/Orchestra-Research/AI-research-SKILLs | research | Academic AI research methodology |
| AI-research-SKILLs (Zhang) | https://github.com/zechenzhangAGI/AI-research-SKILLs | research | AI research paper analysis |
| awesome-ai-agent-papers | https://github.com/VoltAgent/awesome-ai-agent-papers | research-director | Curated agent research papers |
| notebooklm-skill | https://github.com/PleasePrompto/notebooklm-skill | research | NotebookLM-style document analysis |
| competitor-analysis | https://github.com/phuryn/pm-skills/tree/main/pm-market-research/skills/competitor-analysis | research | Competitive intelligence frameworks |
| market-sizing | https://github.com/phuryn/pm-skills/tree/main/pm-market-research/skills/market-sizing | research | TAM/SAM/SOM market analysis |
| market-segments | https://github.com/phuryn/pm-skills/tree/main/pm-market-research/skills/market-segments | research | Market segmentation analysis |
| sentiment-analysis | https://github.com/phuryn/pm-skills/tree/main/pm-market-research/skills/sentiment-analysis | research-ops | Sentiment analysis on market data |
| user-personas | https://github.com/phuryn/pm-skills/tree/main/pm-market-research/skills/user-personas | research | User persona generation |
| user-segmentation | https://github.com/phuryn/pm-skills/tree/main/pm-market-research/skills/user-segmentation | research | User segmentation analysis |
| competitive-battlecard | https://github.com/phuryn/pm-skills/tree/main/pm-go-to-market/skills/competitive-battlecard | research | Competitive battlecard generation |
| x-article-publisher | https://github.com/wshuyi/x-article-publisher-skill | research-ops | Article publishing to X/Twitter |

### Growth Agents (aria-growth, beacon-aso, herald, herald-pr, prism-brand, x-growth-studio, haven-community, quest-gamification)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| claude-seo | https://github.com/AgriciDaniel/claude-seo | beacon-aso | SEO optimization and audit |
| ai-seo | https://github.com/coreyhaines31/marketingskills/tree/main/skills/ai-seo | beacon-aso | AI-powered SEO strategy |
| programmatic-seo | https://github.com/coreyhaines31/marketingskills/tree/main/skills/programmatic-seo | beacon-aso | Programmatic SEO at scale |
| seo-audit | https://github.com/coreyhaines31/marketingskills/tree/main/skills/seo-audit | beacon-aso | Technical SEO audit |
| schema-markup | https://github.com/coreyhaines31/marketingskills/tree/main/skills/schema-markup | beacon-aso | Structured data/schema markup |
| aso-skills | https://github.com/Eronred/aso-skills | beacon-aso | App Store Optimization |
| content-strategy | https://github.com/coreyhaines31/marketingskills/tree/main/skills/content-strategy | aria-growth | Content strategy planning |
| social-content | https://github.com/coreyhaines31/marketingskills/tree/main/skills/social-content | x-growth-studio | Social media content creation |
| copywriting | https://github.com/coreyhaines31/marketingskills/tree/main/skills/copywriting | aria-growth | Marketing copywriting |
| copy-editing | https://github.com/coreyhaines31/marketingskills/tree/main/skills/copy-editing | aria-growth | Copy editing and refinement |
| cold-email | https://github.com/coreyhaines31/marketingskills/tree/main/skills/cold-email | herald | Cold email outreach templates |
| email-sequence | https://github.com/coreyhaines31/marketingskills/tree/main/skills/email-sequence | aria-growth | Email sequence automation |
| launch-strategy | https://github.com/coreyhaines31/marketingskills/tree/main/skills/launch-strategy | herald-pr | Product launch planning |
| marketing-ideas | https://github.com/coreyhaines31/marketingskills/tree/main/skills/marketing-ideas | aria-growth | Marketing idea generation |
| marketing-psychology | https://github.com/coreyhaines31/marketingskills/tree/main/skills/marketing-psychology | aria-growth | Psychology-driven marketing |
| referral-program | https://github.com/coreyhaines31/marketingskills/tree/main/skills/referral-program | haven-community | Referral program design |
| competitor-alternatives | https://github.com/coreyhaines31/marketingskills/tree/main/skills/competitor-alternatives | aria-growth | Competitor alternative pages |
| ad-creative | https://github.com/coreyhaines31/marketingskills/tree/main/skills/ad-creative | aria-growth | Ad creative generation |
| paid-ads | https://github.com/coreyhaines31/marketingskills/tree/main/skills/paid-ads | aria-growth | Paid advertising strategy |
| brand-guidelines | https://github.com/anthropics/skills/tree/main/skills/brand-guidelines | prism-brand | Brand guideline creation |
| gtm-strategy | https://github.com/phuryn/pm-skills/tree/main/pm-go-to-market/skills/gtm-strategy | aria-growth | Go-to-market strategy |
| gtm-motions | https://github.com/phuryn/pm-skills/tree/main/pm-go-to-market/skills/gtm-motions | aria-growth | GTM motion design |
| growth-loops | https://github.com/phuryn/pm-skills/tree/main/pm-go-to-market/skills/growth-loops | aria-growth | Growth loop identification |
| beachhead-segment | https://github.com/phuryn/pm-skills/tree/main/pm-go-to-market/skills/beachhead-segment | aria-growth | Beachhead market selection |
| ideal-customer-profile | https://github.com/phuryn/pm-skills/tree/main/pm-go-to-market/skills/ideal-customer-profile | aria-growth | ICP definition |
| north-star-metric | https://github.com/phuryn/pm-skills/tree/main/pm-marketing-growth/skills/north-star-metric | aria-growth | North star metric identification |
| positioning-ideas | https://github.com/phuryn/pm-skills/tree/main/pm-marketing-growth/skills/positioning-ideas | prism-brand | Brand positioning ideas |
| value-prop-statements | https://github.com/phuryn/pm-skills/tree/main/pm-marketing-growth/skills/value-prop-statements | prism-brand | Value proposition crafting |
| product-name | https://github.com/phuryn/pm-skills/tree/main/pm-marketing-growth/skills/product-name | prism-brand | Product naming |
| ai-marketing-skills | https://github.com/BrianRWagner/ai-marketing-skills | aria-growth | AI-powered marketing toolkit |
| product-marketing-context | https://github.com/coreyhaines31/marketingskills/tree/main/skills/product-marketing-context | aria-growth | Product marketing framework |
| typefully | https://github.com/typefully/agent-skills/tree/main/skills/typefully | x-growth-studio | Typefully content scheduling |
| seo-aeo-best-practices | https://github.com/sanity-io/agent-toolkit/tree/main/skills/seo-aeo-best-practices | beacon-aso | SEO + Answer Engine Optimization |

### Knowledge Agents (knowledge-engineer, ai-evaluation-specialist, ai-product-manager, shield-legal-compliance, pulse-data-science)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| product-manager-skills (Digidai) | https://github.com/Digidai/product-manager-skills | ai-product-manager | PM decision frameworks |
| prd-development | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/prd-development | ai-product-manager | PRD authoring |
| create-prd | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/create-prd | ai-product-manager | PRD generation from specs |
| context-engineering-advisor | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/context-engineering-advisor | knowledge-engineer | Context engineering best practices |
| skill-authoring-workflow | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/skill-authoring-workflow | knowledge-engineer | Skill definition authoring |
| legal-skills | https://github.com/lawvable/awesome-legal-skills | shield-legal-compliance | Legal document generation |
| draft-nda | https://github.com/phuryn/pm-skills/tree/main/pm-toolkit/skills/draft-nda | shield-legal-compliance | NDA drafting |
| privacy-policy | https://github.com/phuryn/pm-skills/tree/main/pm-toolkit/skills/privacy-policy | shield-legal-compliance | Privacy policy generation |
| eval-audit | https://github.com/hamelsmu/prompts/tree/main/evals-skills/skills/eval-audit | ai-evaluation-specialist | AI evaluation auditing |
| evaluate-rag | https://github.com/hamelsmu/prompts/tree/main/evals-skills/skills/evaluate-rag | ai-evaluation-specialist | RAG system evaluation |
| write-judge-prompt | https://github.com/hamelsmu/prompts/tree/main/evals-skills/skills/write-judge-prompt | ai-evaluation-specialist | LLM-as-judge prompt authoring |
| validate-evaluator | https://github.com/hamelsmu/prompts/tree/main/evals-skills/skills/validate-evaluator | ai-evaluation-specialist | Evaluator validation |
| error-analysis | https://github.com/hamelsmu/prompts/tree/main/evals-skills/skills/error-analysis | ai-evaluation-specialist | AI error analysis patterns |
| generate-synthetic-data | https://github.com/hamelsmu/prompts/tree/main/evals-skills/skills/generate-synthetic-data | pulse-data-science | Synthetic data generation |
| build-review-interface | https://github.com/hamelsmu/prompts/tree/main/evals-skills/skills/build-review-interface | ai-evaluation-specialist | Review interface for AI outputs |
| sql-queries | https://github.com/phuryn/pm-skills/tree/main/pm-data-analytics/skills/sql-queries | pulse-data-science | SQL query generation and optimization |
| ab-test-analysis | https://github.com/phuryn/pm-skills/tree/main/pm-data-analytics/skills/ab-test-analysis | pulse-data-science | A/B test statistical analysis |
| cohort-analysis | https://github.com/phuryn/pm-skills/tree/main/pm-data-analytics/skills/cohort-analysis | pulse-data-science | Cohort analysis for retention |
| metrics-dashboard | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/metrics-dashboard | pulse-data-science | Metrics dashboard design |

---

## Tier 2 — HIGH VALUE

### Engineering Agents (atlas, atlas-engineering, forge, forge-qa, sentinel, sentinel-security, nova-ai, algorithm-lab)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| code-review (NeoLab) | https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/code-review | forge-qa | Structured code review protocol |
| code-review (Sentry) | https://github.com/getsentry/skills/tree/main/plugins/sentry-skills/skills/code-review | forge-qa | Sentry-style code review |
| find-bugs | https://github.com/getsentry/skills/tree/main/plugins/sentry-skills/skills/find-bugs | forge-qa | Bug detection patterns |
| commit | https://github.com/getsentry/skills/tree/main/plugins/sentry-skills/skills/commit | atlas | Clean commit workflow |
| create-pr | https://github.com/getsentry/skills/tree/main/plugins/sentry-skills/skills/create-pr | atlas | PR creation best practices |
| iterate-pr | https://github.com/getsentry/skills/tree/main/plugins/sentry-skills/skills/iterate-pr | atlas | PR iteration on review feedback |
| agents-md | https://github.com/getsentry/skills/tree/main/plugins/sentry-skills/skills/agents-md | atlas | Agent definition file authoring |
| claude-settings-audit | https://github.com/getsentry/skills/tree/main/plugins/sentry-skills/skills/claude-settings-audit | atlas | Claude Code settings optimization |
| systematic-debugging | https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md | forge-qa | Systematic bug diagnosis |
| root-cause-tracing | https://github.com/obra/superpowers/blob/main/skills/root-cause-tracing/SKILL.md | forge-qa | Root cause analysis methodology |
| test-driven-development | https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md | forge-qa | TDD workflow enforcement |
| testing-anti-patterns | https://github.com/obra/superpowers/blob/main/skills/testing-anti-patterns/SKILL.md | forge-qa | Test anti-pattern detection |
| testing-skills-with-subagents | https://github.com/obra/superpowers/blob/main/skills/testing-skills-with-subagents/SKILL.md | forge-qa | Sub-agent testing patterns |
| receiving-code-review | https://github.com/obra/superpowers/blob/main/skills/receiving-code-review/SKILL.md | atlas | Handling code review feedback |
| requesting-code-review | https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md | atlas | Requesting effective code reviews |
| finishing-a-development-branch | https://github.com/obra/superpowers/blob/main/skills/finishing-a-development-branch/SKILL.md | atlas | Branch completion workflow |
| using-git-worktrees | https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/SKILL.md | atlas | Git worktree parallel development |
| defense-in-depth | https://github.com/obra/superpowers/blob/main/skills/defense-in-depth/SKILL.md | sentinel-security | Layered security approach |
| mcp-builder (Anthropic) | https://github.com/anthropics/skills/tree/main/skills/mcp-builder | atlas-engineering | MCP server development |
| mcp-builder (Microsoft) | https://github.com/microsoft/skills/tree/main/.github/skills/mcp-builder | atlas-engineering | MCP server development (MS) |
| webapp-testing | https://github.com/anthropics/skills/tree/main/skills/webapp-testing | forge-qa | Web application testing |
| web-artifacts-builder | https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder | atlas | Web artifact generation |
| kaizen | https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/kaizen | atlas | Continuous improvement methodology |
| reflexion | https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/reflexion | atlas | Self-reflection and improvement loops |
| ddd | https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/ddd | atlas-engineering | Domain-driven design patterns |
| sadd | https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/sadd | atlas-engineering | Software architecture design docs |
| sdd | https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/sdd | atlas-engineering | Software design documents |
| write-concisely | https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/docs/skills/write-concisely | atlas | Concise technical writing |
| prompt-engineering | https://github.com/NeoLabHQ/context-engineering-kit/tree/master/plugins/customaize-agent/skills/prompt-engineering | nova-ai | Prompt engineering methodology |
| coderabbitai | https://github.com/coderabbitai/skills | forge-qa | AI code review integration |
| playwright-skill (lackey) | https://github.com/lackeyjb/playwright-skill | forge-qa | Playwright test automation |
| playwright-skill (testdino) | https://github.com/testdino-hq/playwright-skill | forge-qa | Playwright testing suite |
| playwright (OpenAI) | https://github.com/openai/skills/tree/main/skills/.curated/playwright | forge-qa | Playwright browser testing |
| screenshot | https://github.com/openai/skills/tree/main/skills/.curated/screenshot | forge-qa | Screenshot capture for testing |
| gh-fix-ci | https://github.com/openai/skills/tree/main/skills/.curated/gh-fix-ci | atlas | GitHub CI fix automation |
| gh-address-comments | https://github.com/openai/skills/tree/main/skills/.curated/gh-address-comments | atlas | PR comment resolution |
| github (Callstack) | https://github.com/callstackincubator/agent-skills/tree/main/skills/github | atlas | GitHub workflow automation |
| review | https://github.com/garrytan/gstack/tree/main/review | forge-qa | Code review workflow |
| qa | https://github.com/garrytan/gstack/tree/main/qa | forge-qa | QA testing workflow |
| qa-only | https://github.com/garrytan/gstack/tree/main/qa-only | forge-qa | Focused QA pass |
| ship | https://github.com/garrytan/gstack/tree/main/ship | atlas | Ship and deploy workflow |
| land-and-deploy | https://github.com/garrytan/gstack/tree/main/land-and-deploy | atlas | Landing and deployment |
| investigate | https://github.com/garrytan/gstack/tree/main/investigate | forge-qa | Bug investigation |
| guard | https://github.com/garrytan/gstack/tree/main/guard | sentinel-security | Security guard rails |
| careful | https://github.com/garrytan/gstack/tree/main/careful | atlas | Careful change methodology |
| canary | https://github.com/garrytan/gstack/tree/main/canary | atlas | Canary deployment |
| benchmark | https://github.com/garrytan/gstack/tree/main/benchmark | forge-qa | Performance benchmarking |
| retro | https://github.com/garrytan/gstack/tree/main/retro | atlas | Retrospective facilitation |
| freeze/unfreeze | https://github.com/garrytan/gstack/tree/main/freeze | atlas | Code freeze management |
| plan-eng-review | https://github.com/garrytan/gstack/tree/main/plan-eng-review | atlas-engineering | Engineering review planning |
| plan-ceo-review | https://github.com/garrytan/gstack/tree/main/plan-ceo-review | atlas-engineering | Executive review preparation |
| design-review | https://github.com/garrytan/gstack/tree/main/design-review | atlas | Design review workflow |
| document-release | https://github.com/garrytan/gstack/tree/main/document-release | atlas | Release documentation |
| supabase (garrytan) | https://github.com/garrytan/gstack/tree/main/supabase | atlas | Supabase development patterns |
| supabase-postgres-best-practices | https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices | atlas | Supabase Postgres optimization |
| property-based-testing | https://github.com/trailofbits/skills/tree/main/plugins/property-based-testing | forge-qa | Property-based test generation |
| static-analysis | https://github.com/trailofbits/skills/tree/main/plugins/static-analysis | forge-qa | Static code analysis |
| modern-python | https://github.com/trailofbits/skills/tree/main/plugins/modern-python | atlas | Modern Python best practices |
| fastapi-router-py | https://github.com/microsoft/skills/tree/main/.github/skills/fastapi-router-py | atlas | FastAPI routing patterns |
| pydantic-models-py | https://github.com/microsoft/skills/tree/main/.github/skills/pydantic-models-py | atlas | Pydantic model patterns |
| neon-postgres | https://github.com/neondatabase/agent-skills/tree/main/skills/neon-postgres | atlas | Neon Postgres database patterns |
| postgres | https://github.com/sanjay3290/ai-skills/tree/main/skills/postgres | atlas | PostgreSQL best practices |
| duckdb-skills | https://github.com/duckdb/duckdb-skills/tree/main/skills/query | pulse-data-science | DuckDB analytics queries |
| jupyter-notebook | https://github.com/openai/skills/tree/main/skills/.curated/jupyter-notebook | algorithm-lab | Jupyter notebook generation |
| varlock | https://github.com/wrsmith108/varlock-claude-skill | sentinel-security | Variable/secret locking |
| linear-claude-skill | https://github.com/wrsmith108/linear-claude-skill | atlas | Linear project management |
| mattpocock-skills | https://github.com/mattpocock/skills | atlas | TypeScript expert patterns |

### Security Agents (sentinel, sentinel-security)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| VibeSec-Skill | https://github.com/BehiSecc/VibeSec-Skill | sentinel-security | Security posture assessment |
| security-bluebook-builder | https://github.com/SHADOWPR0/security-bluebook-builder | sentinel-security | Security playbook generation |
| cybersecurity-skills | https://github.com/mukul975/Anthropic-Cybersecurity-Skills | sentinel-security | Cybersecurity frameworks |
| clawsec | https://github.com/prompt-security/clawsec | sentinel-security | Prompt injection defense |
| snyk-agent-scan | https://github.com/snyk/agent-scan | sentinel-security | Dependency vulnerability scanning |
| security-best-practices | https://github.com/openai/skills/tree/main/skills/.curated/security-best-practices | sentinel-security | Security best practices |
| security-ownership-map | https://github.com/openai/skills/tree/main/skills/.curated/security-ownership-map | sentinel-security | Security ownership mapping |
| security-threat-model | https://github.com/openai/skills/tree/main/skills/.curated/security-threat-model | sentinel-security | Threat modeling |
| audit-context-building | https://github.com/trailofbits/skills/tree/main/plugins/audit-context-building | sentinel-security | Security audit context |
| building-secure-contracts | https://github.com/trailofbits/skills/tree/main/plugins/building-secure-contracts | sentinel-security | Secure contract patterns |
| constant-time-analysis | https://github.com/trailofbits/skills/tree/main/plugins/constant-time-analysis | sentinel-security | Timing attack analysis |
| differential-review | https://github.com/trailofbits/skills/tree/main/plugins/differential-review | sentinel-security | Security diff review |
| entry-point-analyzer | https://github.com/trailofbits/skills/tree/main/plugins/entry-point-analyzer | sentinel-security | Attack surface mapping |
| insecure-defaults | https://github.com/trailofbits/skills/tree/main/plugins/insecure-defaults | sentinel-security | Insecure default detection |
| semgrep-rule-creator | https://github.com/trailofbits/skills/tree/main/plugins/semgrep-rule-creator | sentinel-security | Semgrep rule generation |
| semgrep-rule-variant-creator | https://github.com/trailofbits/skills/tree/main/plugins/semgrep-rule-variant-creator | sentinel-security | Semgrep rule variants |
| sharp-edges | https://github.com/trailofbits/skills/tree/main/plugins/sharp-edges | sentinel-security | Dangerous API detection |
| spec-to-code-compliance | https://github.com/trailofbits/skills/tree/main/plugins/spec-to-code-compliance | sentinel-security | Spec compliance checking |
| testing-handbook-skills | https://github.com/trailofbits/skills/tree/main/plugins/testing-handbook-skills | sentinel-security | Security testing handbook |
| variant-analysis | https://github.com/trailofbits/skills/tree/main/plugins/variant-analysis | sentinel-security | Vulnerability variant analysis |
| fix-review | https://github.com/trailofbits/skills/tree/main/plugins/fix-review | sentinel-security | Security fix review |
| ffuf-skill | https://github.com/jthack/ffuf_claude_skill | sentinel-security | Fuzzing with ffuf |
| firebase-apk-scanner | https://github.com/trailofbits/skills/tree/main/plugins/firebase-apk-scanner | sentinel-security | Firebase/APK security scanning |

### Design Agents (marcus-ux, mira-emotional-experience, lens-accessibility, guide-customer-success, conversation-designer)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| frontend-design | https://github.com/anthropics/skills/tree/main/skills/frontend-design | marcus-ux | Frontend design patterns |
| canvas-design | https://github.com/anthropics/skills/tree/main/skills/canvas-design | marcus-ux | Canvas-based visual design |
| theme-factory | https://github.com/anthropics/skills/tree/main/skills/theme-factory | marcus-ux | Theme generation system |
| ui-skills | https://github.com/ibelick/ui-skills | marcus-ux | UI component patterns |
| ui-ux-pro-max | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill | marcus-ux | Advanced UI/UX design |
| color-expert | https://github.com/meodai/skill.color-expert | marcus-ux | Color theory and palette design |
| web-design-guidelines | https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines | marcus-ux | Web design best practices |
| creative-director | https://github.com/smixs/creative-director-skill | marcus-ux | Creative direction methodology |
| apple-hig-skills | https://github.com/raintree-technology/apple-hig-skills | marcus-ux | Apple Human Interface Guidelines |
| iOS-Accessibility-Audit | https://github.com/ramzesenok/iOS-Accessibility-Audit-Skill | lens-accessibility | iOS accessibility auditing |
| customer-journey-map | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/customer-journey-map | guide-customer-success | Customer journey mapping |
| customer-journey-mapping-workshop | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/customer-journey-mapping-workshop | guide-customer-success | CJM workshop facilitation |
| discovery-interview-prep | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/discovery-interview-prep | guide-customer-success | User interview preparation |
| discovery-process | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/discovery-process | guide-customer-success | Product discovery process |
| lean-ux-canvas | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/lean-ux-canvas | marcus-ux | Lean UX Canvas framework |
| interview-script | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/interview-script | guide-customer-success | User interview scripts |
| summarize-interview | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/summarize-interview | guide-customer-success | Interview summarization |
| customer-journey-map (phuryn) | https://github.com/phuryn/pm-skills/tree/main/pm-market-research/skills/customer-journey-map | guide-customer-success | Customer journey mapping |
| analyze-feature-requests | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/analyze-feature-requests | guide-customer-success | Feature request analysis |
| figma-implement-design | https://github.com/figma/mcp-server-guide/tree/main/skills/figma-implement-design | marcus-ux | Figma-to-code implementation |
| figma-generate-design | https://github.com/figma/mcp-server-guide/tree/main/skills/figma-generate-design | marcus-ux | Design generation in Figma |
| figma-create-design-system-rules | https://github.com/figma/mcp-server-guide/tree/main/skills/figma-create-design-system-rules | marcus-ux | Design system rules |
| figma-code-connect | https://github.com/figma/mcp-server-guide/tree/main/skills/figma-code-connect-components | marcus-ux | Figma-code connection |
| figma-generate-library | https://github.com/figma/mcp-server-guide/tree/main/skills/figma-generate-library | marcus-ux | Component library generation |
| figma-create-new-file | https://github.com/figma/mcp-server-guide/tree/main/skills/figma-create-new-file | marcus-ux | Figma file creation |
| figma-use | https://github.com/figma/mcp-server-guide/tree/main/skills/figma-use | marcus-ux | Figma general usage |
| stitch-design-md | https://github.com/google-labs-code/stitch-skills/tree/main/skills/design-md | marcus-ux | Design documentation |
| stitch-react-components | https://github.com/google-labs-code/stitch-skills/tree/main/skills/react-components | marcus-ux | React component design |
| stitch-shadcn-ui | https://github.com/google-labs-code/stitch-skills/tree/main/skills/shadcn-ui | marcus-ux | shadcn/ui component usage |
| platform-design-skills | https://github.com/ehmo/platform-design-skills | marcus-ux | Platform design methodology |

### Intel Agents (scout, oracle-brief, pattern-matcher, digest)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| sentry | https://github.com/openai/skills/tree/main/skills/.curated/sentry | digest | Error monitoring intelligence |
| rootly-incident-responder | https://github.com/Rootly-AI-Labs/Rootly-MCP-server/blob/main/examples/skills/rootly-incident-responder.md | digest | Incident response automation |
| Rootly-MCP-server | https://github.com/Rootly-AI-Labs/Rootly-MCP-server | digest | Incident management MCP |
| analytics-tracking | https://github.com/coreyhaines31/marketingskills/tree/main/skills/analytics-tracking | scout | Analytics setup and tracking |
| churn-prevention | https://github.com/coreyhaines31/marketingskills/tree/main/skills/churn-prevention | scout | Churn prediction and prevention |
| revops | https://github.com/coreyhaines31/marketingskills/tree/main/skills/revops | scout | Revenue operations |

### Product Discovery & Execution (compass, ai-product-manager)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| jobs-to-be-done | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/jobs-to-be-done | compass-product | JTBD framework |
| opportunity-solution-tree | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/opportunity-solution-tree | compass | Opportunity-Solution Tree |
| problem-framing-canvas | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/problem-framing-canvas | compass | Problem framing |
| problem-statement | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/problem-statement | compass | Problem statement crafting |
| proto-persona | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/proto-persona | compass-product | Proto-persona creation |
| recommendation-canvas | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/recommendation-canvas | compass | Recommendation analysis |
| user-story | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/user-story | compass | User story authoring |
| user-story-mapping | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/user-story-mapping | compass | Story mapping workshops |
| user-story-splitting | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/user-story-splitting | compass | Story splitting techniques |
| epic-breakdown-advisor | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/epic-breakdown-advisor | compass | Epic decomposition |
| epic-hypothesis | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/epic-hypothesis | compass | Epic hypothesis testing |
| storyboard | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/storyboard | compass-product | Product storyboarding |
| press-release | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/press-release | compass | Amazon-style press release |
| eol-message | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/eol-message | compass | End-of-life messaging |
| pol-probe | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/pol-probe | compass | Pattern of Life analysis |
| workshop-facilitation | https://github.com/deanpeters/Product-Manager-Skills/tree/main/skills/workshop-facilitation | compass | Workshop design |
| sprint-plan | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/sprint-plan | compass | Sprint planning |
| release-notes | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/release-notes | compass | Release notes generation |
| retro (phuryn) | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/retro | compass | Retrospective facilitation |
| stakeholder-map | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/stakeholder-map | compass | Stakeholder mapping |
| test-scenarios | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/test-scenarios | forge-qa | Test scenario generation |
| user-stories (phuryn) | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/user-stories | compass | User story generation |
| prioritization-frameworks | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/prioritization-frameworks | compass | Prioritization methods (RICE, MoSCoW) |
| pre-mortem | https://github.com/phuryn/pm-skills/tree/main/pm-execution/skills/pre-mortem | compass | Pre-mortem risk analysis |
| opportunity-solution-tree (phuryn) | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/opportunity-solution-tree | compass | OST facilitation |
| prioritize-features | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/prioritize-features | compass | Feature prioritization |
| prioritize-assumptions | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/prioritize-assumptions | compass | Assumption prioritization |
| brainstorm-experiments | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/brainstorm-experiments-existing | compass | Experiment ideation |
| brainstorm-ideas | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/brainstorm-ideas-existing | compass | Idea brainstorming |
| identify-assumptions | https://github.com/phuryn/pm-skills/tree/main/pm-product-discovery/skills/identify-assumptions-existing | compass | Assumption identification |

### CRO & Conversion (Growth sub-category)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| form-cro | https://github.com/coreyhaines31/marketingskills/tree/main/skills/form-cro | aria-growth | Form conversion optimization |
| onboarding-cro | https://github.com/coreyhaines31/marketingskills/tree/main/skills/onboarding-cro | aria-growth | Onboarding flow optimization |
| page-cro | https://github.com/coreyhaines31/marketingskills/tree/main/skills/page-cro | aria-growth | Landing page CRO |
| paywall-upgrade-cro | https://github.com/coreyhaines31/marketingskills/tree/main/skills/paywall-upgrade-cro | aria-growth | Paywall optimization |
| popup-cro | https://github.com/coreyhaines31/marketingskills/tree/main/skills/popup-cro | aria-growth | Popup conversion optimization |
| signup-flow-cro | https://github.com/coreyhaines31/marketingskills/tree/main/skills/signup-flow-cro | aria-growth | Signup flow optimization |
| ab-test-setup | https://github.com/coreyhaines31/marketingskills/tree/main/skills/ab-test-setup | aria-growth | A/B test configuration |
| site-architecture | https://github.com/coreyhaines31/marketingskills/tree/main/skills/site-architecture | aria-growth | Site architecture for SEO |
| sales-enablement | https://github.com/coreyhaines31/marketingskills/tree/main/skills/sales-enablement | aria-growth | Sales enablement materials |
| free-tool-strategy | https://github.com/coreyhaines31/marketingskills/tree/main/skills/free-tool-strategy | aria-growth | Free tool lead gen |

### DevOps & Infrastructure

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| cloudflare-agents-sdk | https://github.com/cloudflare/skills/tree/main/skills/agents-sdk | atlas-engineering | Cloudflare Agents SDK |
| cloudflare-ai-agent | https://github.com/cloudflare/skills/tree/main/skills/building-ai-agent-on-cloudflare | atlas-engineering | Building AI agents on CF Workers |
| cloudflare-mcp-server | https://github.com/cloudflare/skills/tree/main/skills/building-mcp-server-on-cloudflare | atlas-engineering | MCP servers on CF Workers |
| cloudflare-durable-objects | https://github.com/cloudflare/skills/tree/main/skills/durable-objects | atlas-engineering | Durable Objects patterns |
| cloudflare-web-perf | https://github.com/cloudflare/skills/tree/main/skills/web-perf | atlas | Web performance optimization |
| cloudflare-wrangler | https://github.com/cloudflare/skills/tree/main/skills/wrangler | atlas | Wrangler CLI for CF Workers |
| cloudflare-commands | https://github.com/cloudflare/skills/tree/main/commands | atlas | CF CLI commands |
| terraform-skill | https://github.com/antonbabenko/terraform-skill | atlas-engineering | Terraform IaC |
| terraform-code-gen | https://github.com/hashicorp/agent-skills/tree/main/terraform/code-generation | atlas-engineering | Terraform code generation |
| terraform-module-gen | https://github.com/hashicorp/agent-skills/tree/main/terraform/module-generation | atlas-engineering | Terraform module generation |
| terraform-provider-dev | https://github.com/hashicorp/agent-skills/tree/main/terraform/provider-development | atlas-engineering | Terraform provider development |
| vercel-deploy | https://github.com/openai/skills/tree/main/skills/.curated/vercel-deploy | atlas | Vercel deployment |
| vercel-deploy-claimable | https://github.com/vercel-labs/agent-skills/tree/main/skills/claude.ai/vercel-deploy-claimable | atlas | Claimable Vercel deploys |
| netlify-deploy | https://github.com/netlify/context-and-tools/tree/main/skills/netlify-deploy | atlas | Netlify deployment |
| netlify-cli-and-deploy | https://github.com/netlify/context-and-tools/tree/main/skills/netlify-cli-and-deploy | atlas | Netlify CLI |
| netlify-edge-functions | https://github.com/netlify/context-and-tools/tree/main/skills/netlify-edge-functions | atlas | Edge function development |
| netlify-functions | https://github.com/netlify/context-and-tools/tree/main/skills/netlify-functions | atlas | Serverless functions |
| render-deploy | https://github.com/openai/skills/tree/main/skills/.curated/render-deploy | atlas | Render deployment |
| cloudflare-deploy | https://github.com/openai/skills/tree/main/skills/.curated/cloudflare-deploy | atlas | Cloudflare Pages deploy |
| setup-deploy | https://github.com/garrytan/gstack/tree/main/setup-deploy | atlas | Deployment setup |
| aws-skills | https://github.com/zxkane/aws-skills | atlas-engineering | AWS service patterns |

### Frontend Development

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| react-best-practices | https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices | atlas | React best practices |
| next-best-practices | https://github.com/vercel-labs/next-skills/tree/main/skills/next-best-practices | atlas | Next.js patterns |
| next-cache-components | https://github.com/vercel-labs/next-skills/tree/main/skills/next-cache-components | atlas | Next.js caching |
| next-upgrade | https://github.com/vercel-labs/next-skills/tree/main/skills/next-upgrade | atlas | Next.js version upgrade |
| composition-patterns | https://github.com/vercel-labs/agent-skills/tree/main/skills/composition-patterns | atlas | Component composition |
| frontend-dev (MiniMax) | https://github.com/MiniMax-AI/skills/tree/main/skills/frontend-dev | atlas | Frontend development |
| fullstack-dev | https://github.com/MiniMax-AI/skills/tree/main/skills/fullstack-dev | atlas | Full-stack patterns |
| react-flow-node-ts | https://github.com/microsoft/skills/tree/main/.github/skills/react-flow-node-ts | atlas | React Flow node graphs |
| zustand-store-ts | https://github.com/microsoft/skills/tree/main/.github/skills/zustand-store-ts | atlas | Zustand state management |
| frontend-ui-dark-ts | https://github.com/microsoft/skills/tree/main/.github/skills/frontend-ui-dark-ts | atlas | Dark mode UI patterns |

### AI/ML Agents (nova-ai, algorithm-lab)

| Skill | URL | Maps To | What It Adds |
|-------|-----|---------|--------------|
| claude-scientific-skills | https://github.com/K-Dense-AI/claude-scientific-skills | algorithm-lab | Scientific computing patterns |
| hugging-face-cli | https://github.com/huggingface/skills/tree/main/skills/hugging-face-cli | nova-ai | HuggingFace CLI operations |
| hugging-face-datasets | https://github.com/huggingface/skills/tree/main/skills/hugging-face-datasets | nova-ai | Dataset management |
| hugging-face-evaluation | https://github.com/huggingface/skills/tree/main/skills/hugging-face-evaluation | ai-evaluation-specialist | Model evaluation |
| hugging-face-model-trainer | https://github.com/huggingface/skills/tree/main/skills/hugging-face-model-trainer | nova-ai | Model fine-tuning |
| hugging-face-vision-trainer | https://github.com/huggingface/skills/tree/main/skills/hugging-face-vision-trainer | nova-ai | Vision model training |
| hugging-face-paper-pages | https://github.com/huggingface/skills/tree/main/skills/hugging-face-paper-pages | research | ML paper analysis |
| hugging-face-tool-builder | https://github.com/huggingface/skills/tree/main/skills/hugging-face-tool-builder | nova-ai | HF tool building |
| hugging-face-trackio | https://github.com/huggingface/skills/tree/main/skills/hugging-face-trackio | nova-ai | Experiment tracking |
| huggingface-gradio | https://github.com/huggingface/skills/tree/main/skills/huggingface-gradio | nova-ai | Gradio app building |
| transformers-js | https://github.com/huggingface/skills/tree/main/skills/transformers.js | nova-ai | Transformers.js in-browser ML |
| gemini-api-dev | https://github.com/google-gemini/gemini-skills/tree/main/skills/gemini-api-dev | nova-ai | Gemini API development |
| vertex-ai-api-dev | https://github.com/google-gemini/gemini-skills/tree/main/skills/vertex-ai-api-dev | nova-ai | Vertex AI development |
| fal-generate | https://github.com/fal-ai-community/skills/blob/main/skills/claude.ai/fal-generate/SKILL.md | nova-ai | Image generation via fal.ai |
| fal-image-edit | https://github.com/fal-ai-community/skills/blob/main/skills/claude.ai/fal-image-edit/SKILL.md | nova-ai | Image editing via fal.ai |
| fal-audio | https://github.com/fal-ai-community/skills/blob/main/skills/claude.ai/fal-audio/SKILL.md | nova-ai | Audio generation via fal.ai |
| fal-upscale | https://github.com/fal-ai-community/skills/blob/main/skills/claude.ai/fal-upscale/SKILL.md | nova-ai | Image upscaling |
| fal-workflow | https://github.com/fal-ai-community/skills/blob/main/skills/claude.ai/fal-workflow/SKILL.md | nova-ai | fal.ai workflow orchestration |
| fal-platform | https://github.com/fal-ai-community/skills/blob/main/skills/claude.ai/fal-platform/SKILL.md | nova-ai | fal.ai platform usage |
| replicate | https://github.com/replicate/skills/tree/main/skills/replicate | nova-ai | Replicate model deployment |
| imagegen | https://github.com/openai/skills/tree/main/skills/.curated/imagegen | nova-ai | Image generation |
| imagen | https://github.com/sanjay3290/ai-skills/tree/main/skills/imagen | nova-ai | Google Imagen generation |
| sora | https://github.com/openai/skills/tree/main/skills/.curated/sora | nova-ai | Video generation with Sora |
| video-db-skills | https://github.com/video-db/skills | nova-ai | Video database operations |
| youtube-clipper | https://github.com/op7418/Youtube-clipper-skill | nova-ai | YouTube video clipping |

---

## Tier 3 — Domain Specific (by domain)

### Blockchain / Web3
- https://github.com/binance/binance-skills-hub/tree/main/skills/binance-web3/crypto-market-rank
- https://github.com/binance/binance-skills-hub/tree/main/skills/binance-web3/meme-rush
- https://github.com/binance/binance-skills-hub/tree/main/skills/binance-web3/query-address-info
- https://github.com/binance/binance-skills-hub/tree/main/skills/binance-web3/query-token-audit
- https://github.com/binance/binance-skills-hub/tree/main/skills/binance-web3/query-token-info
- https://github.com/binance/binance-skills-hub/tree/main/skills/binance-web3/trading-signal
- https://github.com/binance/binance-skills-hub/tree/main/skills/binance/spot
- https://github.com/helius-labs/core-ai/tree/main/helius-skills (Solana)
- https://github.com/trailofbits/skills/tree/main/plugins/building-secure-contracts

### WordPress
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wordpress-router
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-abilities-api
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-block-development
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-block-themes
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-interactivity-api
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-performance
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-phpstan
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-playground
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-plugin-development
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-project-triage
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-rest-api
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wp-wpcli-and-ops
- https://github.com/WordPress/agent-skills/tree/trunk/skills/wpds

### React Native / Mobile
- https://github.com/callstackincubator/agent-skills/blob/main/skills/react-native-best-practices/SKILL.md
- https://github.com/callstackincubator/agent-skills/tree/main/skills/upgrading-react-native
- https://github.com/MiniMax-AI/skills/tree/main/skills/android-native-dev
- https://github.com/MiniMax-AI/skills/tree/main/skills/ios-application-dev
- https://github.com/vercel-labs/agent-skills/tree/main/skills/react-native-skills
- https://github.com/conorluddy/ios-simulator-skill
- https://github.com/rudrankriyam/app-store-connect-cli-skills
- https://github.com/truongduy2611/app-store-preflight-skills

### Expo (React Native)
- https://github.com/expo/skills/tree/main/plugins/expo/skills/building-native-ui
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-api-routes
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-cicd-workflows
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-deployment
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-dev-client
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-tailwind-setup
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-ui-jetpack-compose
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-ui-swift-ui
- https://github.com/expo/skills/tree/main/plugins/expo/skills/native-data-fetching
- https://github.com/expo/skills/tree/main/plugins/expo/skills/upgrading-expo
- https://github.com/expo/skills/tree/main/plugins/expo/skills/use-dom

### Swift / iOS Native
- https://github.com/AvdLee/SwiftUI-Agent-Skill/tree/main/swiftui-expert-skill
- https://github.com/efremidze/swift-patterns-skill/tree/main/swift-patterns
- https://github.com/Joannis/claude-skills (Swift server-side)

### Azure (Microsoft) — 100+ SDK skills
- https://github.com/microsoft/skills/tree/main/.github/skills/azure-ai-agents-persistent-dotnet
- https://github.com/microsoft/skills/tree/main/.github/skills/agents-v2-py
- https://github.com/microsoft/skills/tree/main/.github/skills/azd-deployment
- (and 95+ more Azure SDK skills across Java, Python, .NET, TypeScript, Rust — see lines 377-508 in source)

### Google Workspace (Admin)
- https://github.com/googleworkspace/cli/tree/main/skills/gws-admin
- https://github.com/googleworkspace/cli/tree/main/skills/gws-admin-reports
- https://github.com/googleworkspace/cli/tree/main/skills/gws-alertcenter
- https://github.com/googleworkspace/cli/tree/main/skills/gws-classroom
- https://github.com/googleworkspace/cli/tree/main/skills/gws-cloudidentity
- https://github.com/googleworkspace/cli/tree/main/skills/gws-events
- https://github.com/googleworkspace/cli/tree/main/skills/gws-forms
- https://github.com/googleworkspace/cli/tree/main/skills/gws-groupssettings
- https://github.com/googleworkspace/cli/tree/main/skills/gws-licensing
- https://github.com/googleworkspace/cli/tree/main/skills/gws-modelarmor
- https://github.com/googleworkspace/cli/tree/main/skills/gws-people
- https://github.com/googleworkspace/cli/tree/main/skills/gws-reseller
- https://github.com/googleworkspace/cli/tree/main/skills/gws-shared
- https://github.com/googleworkspace/cli/tree/main/skills/gws-slides
- https://github.com/googleworkspace/cli/tree/main/skills/gws-vault

### n8n Workflow Automation
- https://github.com/czlonkowski/n8n-skills/tree/main/skills/n8n-code-javascript
- https://github.com/czlonkowski/n8n-skills/tree/main/skills/n8n-code-python
- https://github.com/czlonkowski/n8n-skills/tree/main/skills/n8n-expression-syntax
- https://github.com/czlonkowski/n8n-skills/tree/main/skills/n8n-mcp-tools-expert
- https://github.com/czlonkowski/n8n-skills/tree/main/skills/n8n-node-configuration
- https://github.com/czlonkowski/n8n-skills/tree/main/skills/n8n-validation-expert
- https://github.com/czlonkowski/n8n-skills/tree/main/skills/n8n-workflow-patterns

### Netlify (Platform-Specific)
- https://github.com/netlify/context-and-tools/tree/main/skills/netlify-ai-gateway
- https://github.com/netlify/context-and-tools/tree/main/skills/netlify-blobs
- https://github.com/netlify/context-and-tools/tree/main/skills/netlify-caching
- https://github.com/netlify/context-and-tools/tree/main/skills/netlify-config
- https://github.com/netlify/context-and-tools/tree/main/skills/netlify-db
- https://github.com/netlify/context-and-tools/tree/main/skills/netlify-forms
- https://github.com/netlify/context-and-tools/tree/main/skills/netlify-frameworks
- https://github.com/netlify/context-and-tools/tree/main/skills/netlify-image-cdn
- https://github.com/openai/skills/tree/main/skills/.curated/netlify-deploy

### Authentication (better-auth)
- https://github.com/better-auth/skills/blob/main/better-auth/commands/explain-error.md
- https://github.com/better-auth/skills/blob/main/better-auth/commands/providers.md
- https://github.com/better-auth/skills/tree/main/better-auth/best-practices
- https://github.com/better-auth/skills/tree/main/better-auth/create-auth
- https://github.com/better-auth/skills/tree/main/better-auth/emailAndPassword
- https://github.com/better-auth/skills/tree/main/better-auth/organization
- https://github.com/better-auth/skills/tree/main/better-auth/twoFactor

### GSAP Animation
- https://github.com/greensock/gsap-skills/tree/main/skills/gsap-core
- https://github.com/greensock/gsap-skills/tree/main/skills/gsap-frameworks
- https://github.com/greensock/gsap-skills/tree/main/skills/gsap-performance
- https://github.com/greensock/gsap-skills/tree/main/skills/gsap-plugins
- https://github.com/greensock/gsap-skills/tree/main/skills/gsap-react
- https://github.com/greensock/gsap-skills/tree/main/skills/gsap-scrolltrigger
- https://github.com/greensock/gsap-skills/tree/main/skills/gsap-timeline
- https://github.com/greensock/gsap-skills/tree/main/skills/gsap-utils

### WhatsApp Integration
- https://github.com/gokapso/agent-skills/tree/master/skills/automate-whatsapp
- https://github.com/gokapso/agent-skills/tree/master/skills/integrate-whatsapp
- https://github.com/gokapso/agent-skills/tree/master/skills/observe-whatsapp

### Firecrawl (Already have MCP)
- https://github.com/firecrawl/cli/tree/main/skills/firecrawl-agent
- https://github.com/firecrawl/cli/tree/main/skills/firecrawl-browser
- https://github.com/firecrawl/cli/tree/main/skills/firecrawl-cli
- https://github.com/firecrawl/cli/tree/main/skills/firecrawl-crawl
- https://github.com/firecrawl/cli/tree/main/skills/firecrawl-download
- https://github.com/firecrawl/cli/tree/main/skills/firecrawl-map
- https://github.com/firecrawl/cli/tree/main/skills/firecrawl-scrape
- https://github.com/firecrawl/cli/tree/main/skills/firecrawl-search

### Stripe Payments
- https://github.com/stripe/ai/tree/main/skills/stripe-best-practices
- https://github.com/stripe/ai/tree/main/skills/upgrade-stripe

### Sanity CMS
- https://github.com/sanity-io/agent-toolkit/tree/main/skills/content-experimentation-best-practices
- https://github.com/sanity-io/agent-toolkit/tree/main/skills/content-modeling-best-practices
- https://github.com/sanity-io/agent-toolkit/tree/main/skills/sanity-best-practices

### Tinybird Analytics
- https://github.com/tinybirdco/tinybird-agent-skills/tree/main/skills/tinybird-best-practices
- https://github.com/tinybirdco/tinybird-agent-skills/tree/main/skills/tinybird-cli-guidelines
- https://github.com/tinybirdco/tinybird-agent-skills/tree/main/skills/tinybird-python-sdk-guidelines
- https://github.com/tinybirdco/tinybird-agent-skills/tree/main/skills/tinybird-typescript-sdk-guidelines

### Transloadit Media Processing
- https://github.com/transloadit/skills/tree/main/skills/docs-transloadit-robots
- https://github.com/transloadit/skills/tree/main/skills/integrate-asset-delivery-with-transloadit-smartcdn-in-nextjs
- https://github.com/transloadit/skills/tree/main/skills/integrate-uppy-transloadit-s3-uploading-to-nextjs
- https://github.com/transloadit/skills/tree/main/skills/transform-encode-hls-video-with-transloadit
- https://github.com/transloadit/skills/tree/main/skills/transform-generate-image-with-transloadit
- https://github.com/transloadit/skills/tree/main/skills/transloadit

### DuckDB
- https://github.com/duckdb/duckdb-skills/tree/main/skills/attach-db
- https://github.com/duckdb/duckdb-skills/tree/main/skills/duckdb-docs
- https://github.com/duckdb/duckdb-skills/tree/main/skills/install-duckdb
- https://github.com/duckdb/duckdb-skills/tree/main/skills/read-file
- https://github.com/duckdb/duckdb-skills/tree/main/skills/read-memories

### Materials Science
- https://github.com/HeshamFS/materials-simulation-skills

### Healthcare
- https://github.com/huifer/Claude-Ally-Health

### Home Automation
- https://github.com/komal-SkyNET/claude-skill-homeassistant

### ClickHouse
- https://github.com/ClickHouse/agent-skills

### Shader/3D Graphics
- https://github.com/MiniMax-AI/skills/tree/main/skills/shader-dev
- https://github.com/CloudAI-X/threejs-skills

### Makepad UI Framework
- https://github.com/ZhangHanDong/makepad-skills

### Ruby on Rails
- https://github.com/ethos-link/rails-conventions
- https://github.com/robzolkos/skill-rails-upgrade

### VMware/AIOps
- https://github.com/zw008/VMware-AIops

### E-commerce
- https://github.com/takechanman1228/claude-ecom

### Music Production
- https://github.com/bitwize-music-studio/claude-ai-music-skills
- https://github.com/NoizAI/skills

### Windows
- https://github.com/NotMyself/claude-win11-speckit-update-skill

### Gemini Live/Interactions API
- https://github.com/google-gemini/gemini-skills/tree/main/skills/gemini-interactions-api
- https://github.com/google-gemini/gemini-skills/tree/main/skills/gemini-live-api-dev

### ComposioHQ (Multi-tool integration)
- https://github.com/ComposioHQ/skills

### Microsoft M365 Agents
- https://github.com/microsoft/skills/tree/main/.github/skills/m365-agents-dotnet
- https://github.com/microsoft/skills/tree/main/.github/skills/m365-agents-py
- https://github.com/microsoft/skills/tree/main/.github/skills/m365-agents-ts

### Document Processing
- https://github.com/kreuzberg-dev/kreuzberg/tree/main/skills/kreuzberg
- https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-docx
- https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-pdf
- https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-xlsx
- https://github.com/MiniMax-AI/skills/tree/main/skills/pptx-generator

### Presentation Slides
- https://github.com/op7418/NanoBanana-PPT-Skills
- https://github.com/zarazhangrui/frontend-slides

### Neon Postgres (additional)
- https://github.com/neondatabase/agent-skills/tree/main/skills/claimable-postgres
- https://github.com/neondatabase/agent-skills/tree/main/skills/neon-postgres-egress-optimizer

### Stitch Design (Google Labs)
- https://github.com/google-labs-code/stitch-skills/tree/main/skills/enhance-prompt
- https://github.com/google-labs-code/stitch-skills/tree/main/skills/remotion
- https://github.com/google-labs-code/stitch-skills/tree/main/skills/stitch-loop

### Remotion (Video)
- https://github.com/remotion-dev/skills/tree/main/skills/remotion

### PSPDFKit/Nutrient
- https://github.com/PSPDFKit-labs/nutrient-agent-skill

### OPC (Open Process Control)
- https://github.com/ReScienceLab/opc-skills

### Codex/OpenAI
- https://github.com/Kevin7Qi/codex-collab
- https://github.com/garrytan/gstack/tree/main/codex
- https://github.com/openai/skills/tree/main/skills/.curated/openai-docs

### Miscellaneous Domain
- https://github.com/mcollina/skills/tree/main/skills (Node.js patterns)
- https://github.com/Leonxlnx/taste-skill (food/taste)
- https://github.com/deusyu/translate-book (book translation)
- https://github.com/uucz/moyu (time management/slacking)
- https://github.com/scarletkc/vexor (payments)
- https://github.com/microsoft/skills/tree/main/.github/skills/podcast-generation
- https://github.com/fvadicamo/dev-agent-skills

---

## Tier 4 — Skip

**103 skills skipped.** Reasons: duplicates of built-in capabilities, broken/empty links, asset files, trivially small, or user profile pages.

### Broken/Invalid Links
- https://github.com/user-attachments/assets/3a9d4cb3-04bd-4fb1-9146-fd3b53d26961 (image asset)
- https://github.com/user-attachments/assets/5d8822c0-e97b-4183-a71e-a922ab88e1a0 (image asset)
- https://github.com/coreyhaines31 (user profile, not a skill)
- https://github.com/deanpeters (user profile, not a skill)
- https://github.com/garrytan (user profile, not a skill)
- https://github.com/phuryn (user profile, not a skill)
- https://github.com/VoltAgent/awesome-agent-skills/issues (issues page, not a skill)

### Duplicates of Existing MCP/Built-in Capabilities
- https://github.com/Shpigford/skills/tree/main/readme (README generator — built-in)
- https://github.com/Shpigford/skills/tree/main/screenshots (screenshot — already have Playwright)
- https://github.com/anthropics/skills/tree/main/skills/algorithmic-art (niche art)
- https://github.com/anthropics/skills/tree/main/skills/slack-gif-creator (Slack GIF — no Slack)
- https://github.com/anthropics/skills/tree/main/template (template only)
- https://github.com/openai/skills/tree/main/skills/.curated/develop-web-game (game dev)
- https://github.com/openai/skills/tree/main/skills/.curated/doc (generic doc — built-in)
- https://github.com/openai/skills/tree/main/skills/.curated/yeet (deployment helper — redundant)
- https://github.com/openai/skills/tree/main/skills/.curated/pdf (duplicate — Anthropic has one)

### VoltAgent Meta/Self-Referencing
- https://github.com/VoltAgent/awesome-openclaw-skills (meta list)
- https://github.com/VoltAgent/awesome-claude-code-subagents (meta list)
- https://github.com/VoltAgent/awesome-codex-subagents (meta list)
- https://github.com/VoltAgent/skills/tree/main/skills/create-voltagent (VoltAgent self-promo)
- https://github.com/VoltAgent/skills/tree/main/skills/voltagent-best-practices (VA internal)
- https://github.com/VoltAgent/skills/tree/main/skills/voltagent-core-reference (VA internal)
- https://github.com/VoltAgent/skills/tree/main/skills/voltagent-docs-bundle (VA internal)
- https://github.com/VoltAgent/voltagent (framework itself)

### Trivially Small / Low Value
- https://github.com/blader/humanizer (text humanizer — gimmick)
- https://github.com/jeffersonwarrior/claudisms (Claude personality — trivial)
- https://github.com/SHADOWPR0/beautiful_prose (prose styling — trivial)
- https://github.com/omkamal/pypict-claude-skill/blob/main/SKILL.md (pict image — niche)
- https://github.com/muthuishere/hand-drawn-diagrams (hand-drawn diagrams — gimmick)
- https://github.com/yusufkaraaslan/Skill_Seekers (skill discovery — meta)
- https://github.com/ShunsukeHayashi/agent-skill-bus (agent bus — framework)
- https://github.com/alinaqi/claude-bootstrap (bootstrap — basic)
- https://github.com/RoundTable02/tutor-skills (tutoring — not relevant)
- https://github.com/Paramchoudhary/ResumeSkills (resume builder — niche)

### Remaining Domain-Specific Skips (already covered by MCP or irrelevant)
- Firecrawl skills (8) — already have firecrawl MCP server connected
- Microsoft Azure SDK skills (98) — not using Azure, massive volume with no current need
- Various platform-specific auth/identity skills already covered by built-in tools
- gws-slides — not currently using Google Slides in workflows
- Multiple duplicate PM skill sets that overlap heavily

---

## Summary Statistics

### Skills Per Agent Group

| Agent Group | Tier 1 | Tier 2 | Total Mapped |
|-------------|--------|--------|-------------|
| **Operations** (jake, kira, aria, orchestrator) | 57 | 0 | 57 |
| **Strategy** (steve, compass, ledger) | 31 | 0 | 31 |
| **Research** (research, research-director) | 13 | 0 | 13 |
| **Growth** (aria-growth, beacon-aso, herald, prism) | 33 | 10 | 43 |
| **Knowledge** (knowledge-engineer, ai-eval, shield) | 19 | 0 | 19 |
| **Engineering** (atlas, forge, sentinel, nova) | 0 | 75 | 75 |
| **Security** (sentinel-security) | 0 | 24 | 24 |
| **Design** (marcus-ux, lens, guide) | 0 | 31 | 31 |
| **Intel** (scout, digest) | 0 | 6 | 6 |
| **Product** (compass, ai-product-manager) | 0 | 32 | 32 |
| **AI/ML** (nova-ai, algorithm-lab) | 0 | 29 | 29 |

### Coverage Gaps

| Agent Group | Gap Analysis |
|-------------|-------------|
| **Science** (coach, sage, drift, flow) | NO matching skills found — fitness, nutrition, sleep, sports psychology not represented in VoltAgent |
| **Psychology** (freya, quest) | NO matching skills — behavioral economics, gamification not in community |
| **Film Studio** (14 agents) | MINIMAL — only video-db and youtube-clipper tangentially relevant |
| **Design Studios** (12 studios) | PARTIAL — Figma/Stitch skills help but no deck/landing-page/marketing studio matches |
| **Intel** (antifragility-monitor, pattern-matcher, optionality-scout) | LOW — only 6 skills mapped, mostly monitoring/analytics |
| **Recruiting** (coach-outreach) | ZERO — no recruiting or outreach automation skills in community |

### Recommended Install Order

**Wave 1 — Immediate (Week 1)**: Context engineering + orchestration foundations
1. obra/superpowers (all 18 skills) — dispatching, planning, testing, debugging, git workflows
2. muratcankoylan/Agent-Skills-for-Context-Engineering (8 skills) — context management
3. anthropics/skills (pdf, docx, xlsx, pptx, mcp-builder, skill-creator) — document generation
4. hanfang/claude-memory-skill — memory management
5. garrytan/gstack (autoplan, review, qa, ship, guard, investigate) — dev workflow

**Wave 2 — Strategy & Growth (Week 2)**: Product and business skills
6. deanpeters/Product-Manager-Skills (46 skills) — product management frameworks
7. phuryn/pm-skills (58 skills) — PM execution, strategy, discovery, GTM
8. coreyhaines31/marketingskills (32 skills) — marketing, SEO, CRO
9. EveryInc/charlie-cfo-skill — financial analysis

**Wave 3 — Engineering & Security (Week 3)**: Dev toolchain
10. getsentry/skills (7 skills) — code review, PR, bug finding
11. trailofbits/skills (22 skills) — security auditing
12. hamelsmu/prompts/evals-skills (7 skills) — AI evaluation
13. cloudflare/skills (7 skills) — Cloudflare Workers development
14. supabase/agent-skills — Postgres best practices

**Wave 4 — Design & AI (Week 4)**: Polish layer
15. figma/mcp-server-guide (7 skills) — Figma integration
16. huggingface/skills (14 skills) — ML model management
17. fal-ai-community/skills (6 skills) — generative AI
18. googleworkspace/cli (core skills) — Google Workspace automation

**Wave 5 — Domain-Specific (As Needed)**: Install when projects require them
- Expo/React Native skills — when building Alex Recruiting mobile
- Stripe skills — when adding payments
- n8n skills — if adopting n8n for workflow automation
- WhatsApp skills — if adding WhatsApp channel
