# VoltAgent x Susan: Agent Roster Overlap Analysis & Merged Plan

**Date**: 2026-03-25
**Rosters**: VoltAgent awesome-claude-code-subagents (126) + Susan (83) + Claude Code operational (15)
**Total input agents**: 224 (with duplicates across rosters)

---

## 1. OVERLAP MAPPING

Rating scale:
- **EXACT** = same role, same scope (keep one)
- **PARTIAL** = similar domain but different scope/depth (keep both, clarify lanes)
- **NONE** = entirely new capability (add to merged roster)

### 01-core-development (10 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| api-designer | atlas-engineering | PARTIAL | Atlas is broad engineering lead; api-designer is specialized |
| backend-developer | atlas-engineering | PARTIAL | Atlas covers backend but is architectural, not implementation-focused |
| electron-pro | -- | NONE | Desktop app specialization, no Susan equivalent |
| frontend-developer | atlas-engineering | PARTIAL | Atlas is full-stack lead, not frontend-specific |
| fullstack-developer | atlas-engineering | PARTIAL | Closest to Atlas's scope but implementation vs architecture |
| graphql-architect | -- | NONE | API protocol specialization |
| microservices-architect | atlas-engineering | PARTIAL | Atlas covers architecture but not microservices-specific |
| mobile-developer | -- | NONE | No Susan mobile dev agent |
| ui-designer | marcus-ux | PARTIAL | Marcus is UX research + design; ui-designer is implementation |
| websocket-engineer | -- | NONE | Real-time protocol specialization |

**Summary**: 0 EXACT, 6 PARTIAL, 4 NONE

### 02-language-specialists (28 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| angular-architect | -- | NONE | Framework specialist |
| cpp-pro | -- | NONE | Language specialist |
| csharp-developer | -- | NONE | Language specialist |
| django-developer | -- | NONE | Framework specialist |
| dotnet-core-expert | -- | NONE | Platform specialist |
| dotnet-framework-4.8-expert | -- | NONE | Legacy platform specialist |
| elixir-expert | -- | NONE | Language specialist |
| expo-react-native-expert | -- | NONE | Mobile framework specialist |
| fastapi-developer | -- | NONE | Framework specialist |
| flutter-expert | -- | NONE | Mobile framework specialist |
| golang-pro | -- | NONE | Language specialist |
| java-architect | -- | NONE | Language specialist |
| javascript-pro | -- | NONE | Language specialist |
| kotlin-specialist | -- | NONE | Language specialist |
| laravel-specialist | -- | NONE | Framework specialist |
| nextjs-developer | -- | NONE | Framework specialist |
| php-pro | -- | NONE | Language specialist |
| powershell-5.1-expert | -- | NONE | Scripting specialist |
| powershell-7-expert | -- | NONE | Scripting specialist |
| python-pro | -- | NONE | Language specialist |
| rails-expert | -- | NONE | Framework specialist |
| react-specialist | -- | NONE | Framework specialist |
| rust-engineer | -- | NONE | Language specialist |
| spring-boot-engineer | -- | NONE | Framework specialist |
| sql-pro | -- | NONE | Language specialist |
| swift-expert | -- | NONE | Language specialist |
| typescript-pro | -- | NONE | Language specialist |
| vue-expert | -- | NONE | Framework specialist |

**Summary**: 0 EXACT, 0 PARTIAL, 28 NONE -- Susan has zero language/framework specialists. This is the largest gap.

### 03-infrastructure (16 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| azure-infra-engineer | -- | NONE | Cloud platform specialist |
| cloud-architect | -- | NONE | Cloud architecture |
| database-administrator | -- | NONE | DB ops specialist |
| deployment-engineer | -- | NONE | Deployment specialist |
| devops-engineer | -- | NONE | DevOps generalist |
| devops-incident-responder | -- | NONE | Incident management |
| docker-expert | -- | NONE | Container specialist |
| incident-responder | -- | NONE | General incident response |
| kubernetes-specialist | -- | NONE | Orchestration specialist |
| network-engineer | -- | NONE | Network specialist |
| platform-engineer | -- | NONE | Platform engineering |
| security-engineer | sentinel-security | PARTIAL | Sentinel is security-focused but broader (AppSec + compliance); security-engineer is infra-security |
| sre-engineer | -- | NONE | Reliability engineering |
| terraform-engineer | -- | NONE | IaC specialist |
| terragrunt-expert | -- | NONE | IaC specialist |
| windows-infra-admin | -- | NONE | Windows administration |

**Summary**: 0 EXACT, 1 PARTIAL, 15 NONE -- Susan has almost no infrastructure capability.

### 04-quality-security (14 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| accessibility-tester | lens-accessibility | PARTIAL | Lens is design-side accessibility; tester is QA-side |
| ad-security-reviewer | sentinel-security | PARTIAL | Active Directory security is a narrow slice |
| architect-reviewer | -- | NONE | Architecture review specialist |
| chaos-engineer | -- | NONE | Resilience testing |
| code-reviewer | -- | NONE | Code review specialist |
| compliance-auditor | shield-legal-compliance | PARTIAL | Shield is legal+compliance; auditor is technical compliance |
| debugger | -- | NONE | Debugging specialist |
| error-detective | -- | NONE | Error investigation |
| penetration-tester | sentinel-security | PARTIAL | Sentinel covers security broadly |
| performance-engineer | -- | NONE | Performance optimization |
| powershell-security-hardening | -- | NONE | Windows security hardening |
| qa-expert | forge-qa | EXACT | Direct match -- both are QA leads |
| security-auditor | sentinel-security | PARTIAL | Sentinel is broader; auditor is audit-specific |
| test-automator | forge-qa | PARTIAL | Forge is QA lead; test-automator is automation specialist |

**Summary**: 1 EXACT (qa-expert=forge-qa), 5 PARTIAL, 8 NONE

### 05-data-ai (13 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| ai-engineer | nova-ai | PARTIAL | Nova is AI/ML lead; ai-engineer is implementation |
| data-analyst | pulse-data-science | PARTIAL | Pulse is data science lead; analyst is narrower |
| data-engineer | -- | NONE | Data pipeline specialist |
| data-scientist | pulse-data-science | EXACT | Direct match on data science |
| database-optimizer | -- | NONE | DB performance specialist |
| llm-architect | nova-ai | PARTIAL | Nova covers AI broadly; llm-architect is LLM-specific |
| machine-learning-engineer | nova-ai | PARTIAL | Nova covers ML; this is implementation-focused |
| ml-engineer | nova-ai | PARTIAL | Near-duplicate with machine-learning-engineer |
| mlops-engineer | -- | NONE | ML operations specialist |
| nlp-engineer | -- | NONE | NLP specialist |
| postgres-pro | -- | NONE | Database specialist |
| prompt-engineer | -- | NONE | Prompt engineering specialist |
| reinforcement-learning-engineer | algorithm-lab | PARTIAL | Algorithm Lab covers advanced ML methods |

**Summary**: 1 EXACT (data-scientist=pulse-data-science), 5 PARTIAL, 7 NONE

### 06-developer-experience (13 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| build-engineer | -- | NONE | Build systems specialist |
| cli-developer | -- | NONE | CLI tooling specialist |
| dependency-manager | -- | NONE | Dependency management |
| documentation-engineer | -- | NONE | Technical docs specialist |
| dx-optimizer | -- | NONE | Developer experience |
| git-workflow-manager | -- | NONE | Git workflow specialist |
| legacy-modernizer | -- | NONE | Legacy code modernization |
| mcp-developer | -- | NONE | MCP integration specialist |
| powershell-module-architect | -- | NONE | PowerShell module design |
| powershell-ui-architect | -- | NONE | PowerShell UI specialist |
| refactoring-specialist | -- | NONE | Code refactoring |
| slack-expert | -- | NONE | Slack integration |
| tooling-engineer | -- | NONE | Developer tooling |

**Summary**: 0 EXACT, 0 PARTIAL, 13 NONE -- Susan has zero DevEx agents. Second largest gap.

### 07-specialized-domains (12 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| api-documenter | -- | NONE | API documentation |
| blockchain-developer | -- | NONE | Blockchain specialist |
| embedded-systems | -- | NONE | Embedded systems |
| fintech-engineer | ledger-finance | PARTIAL | Ledger is financial strategy; fintech is implementation |
| game-developer | -- | NONE | Game development |
| iot-engineer | -- | NONE | IoT specialist |
| m365-admin | -- | NONE | Microsoft 365 admin |
| mobile-app-developer | -- | NONE | Mobile development |
| payment-integration | -- | NONE | Payment systems |
| quant-analyst | -- | NONE | Quantitative analysis |
| risk-manager | -- | NONE | Risk management |
| seo-specialist | beacon-aso | PARTIAL | Beacon is ASO; SEO is broader web search optimization |

**Summary**: 0 EXACT, 2 PARTIAL, 10 NONE

### 08-business-product (11 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| business-analyst | steve-strategy | PARTIAL | Steve is strategic; BA is analytical |
| content-marketer | marketing-studio-director | PARTIAL | Marketing studio is broader creative direction |
| customer-success-manager | guide-customer-success | EXACT | Direct match |
| legal-advisor | shield-legal-compliance | EXACT | Direct match |
| product-manager | compass-product / ai-product-manager | EXACT | Susan has TWO PM agents |
| project-manager | -- | NONE | Project management (Susan uses Susan orchestrator) |
| sales-engineer | -- | NONE | Sales engineering |
| scrum-master | -- | NONE | Agile process management |
| technical-writer | article-studio / whitepaper-studio | PARTIAL | Susan has content studios, not a technical writer per se |
| ux-researcher | marcus-ux / ux-design-process | PARTIAL | Marcus covers UX research; VoltAgent is research-only |
| wordpress-master | -- | NONE | WordPress specialist |

**Summary**: 3 EXACT, 4 PARTIAL, 4 NONE

### 09-meta-orchestration (10 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| agent-installer | -- | NONE | Agent setup tooling |
| agent-organizer | -- | NONE | Agent management |
| context-manager | -- | NONE | Context window management |
| error-coordinator | -- | NONE | Error coordination |
| it-ops-orchestrator | -- | NONE | IT operations |
| knowledge-synthesizer | knowledge-engineer | PARTIAL | Knowledge engineer is broader |
| multi-agent-coordinator | susan (orchestrator) | PARTIAL | Susan orchestrates but is domain-specific |
| performance-monitor | -- | NONE | Performance monitoring |
| task-distributor | -- | NONE | Task distribution |
| workflow-orchestrator | susan (orchestrator) | PARTIAL | Susan orchestrates Susan agents specifically |

**Summary**: 0 EXACT, 3 PARTIAL, 7 NONE

### 10-research-analysis (7 VoltAgent agents)

| VoltAgent Agent | Closest Susan Agent | Overlap | Notes |
|---|---|---|---|
| competitive-analyst | research-director | PARTIAL | Research director is broader |
| data-researcher | researcher-web / researcher-arxiv | PARTIAL | Susan's researchers are source-specific |
| market-researcher | research-ops | PARTIAL | Research ops coordinates but isn't market-specific |
| research-analyst | research-director | PARTIAL | Research director leads; analyst does work |
| scientific-literature-researcher | researcher-arxiv | EXACT | Direct match |
| search-specialist | researcher-web | PARTIAL | Web researcher is similar but broader |
| trend-analyst | -- | NONE | Trend analysis specialist |

**Summary**: 1 EXACT, 5 PARTIAL, 1 NONE

---

## OVERLAP TOTALS

| Rating | Count | Percentage |
|---|---|---|
| EXACT | 6 | 4.8% |
| PARTIAL | 31 | 24.6% |
| NONE | 89 | 70.6% |
| **Total VoltAgent agents** | **126** | |

**Key finding**: 70.6% of VoltAgent agents are entirely new capabilities with no Susan equivalent. The overlap is surprisingly small -- the two rosters are highly complementary.

### EXACT matches (6 pairs -- keep the better version):

| VoltAgent | Susan | Winner | Reasoning |
|---|---|---|---|
| qa-expert | forge-qa | **forge-qa** | Susan's naming + existing routing |
| data-scientist | pulse-data-science | **pulse-data-science** | Susan's naming + domain context |
| customer-success-manager | guide-customer-success | **guide-customer-success** | Susan's naming + startup context |
| legal-advisor | shield-legal-compliance | **shield-legal-compliance** | Susan includes compliance |
| product-manager | compass-product | **compass-product** | Susan has richer product context |
| scientific-literature-researcher | researcher-arxiv | **researcher-arxiv** | Susan's source-specific design |

---

## 2. GAP ANALYSIS -- VoltAgent Agents with NO Susan Equivalent (89 agents)

These represent entirely new capabilities Susan gains from the merge.

### Software Engineering (28 language/framework specialists)
angular-architect, cpp-pro, csharp-developer, django-developer, dotnet-core-expert, dotnet-framework-4.8-expert, elixir-expert, expo-react-native-expert, fastapi-developer, flutter-expert, golang-pro, java-architect, javascript-pro, kotlin-specialist, laravel-specialist, nextjs-developer, php-pro, powershell-5.1-expert, powershell-7-expert, python-pro, rails-expert, react-specialist, rust-engineer, spring-boot-engineer, sql-pro, swift-expert, typescript-pro, vue-expert

### Infrastructure & Ops (15)
azure-infra-engineer, cloud-architect, database-administrator, deployment-engineer, devops-engineer, devops-incident-responder, docker-expert, incident-responder, kubernetes-specialist, network-engineer, platform-engineer, sre-engineer, terraform-engineer, terragrunt-expert, windows-infra-admin

### Developer Experience (13)
build-engineer, cli-developer, dependency-manager, documentation-engineer, dx-optimizer, git-workflow-manager, legacy-modernizer, mcp-developer, powershell-module-architect, powershell-ui-architect, refactoring-specialist, slack-expert, tooling-engineer

### Quality & Security (8)
architect-reviewer, chaos-engineer, code-reviewer, debugger, error-detective, performance-engineer, powershell-security-hardening, ad-security-reviewer

### Data & AI (7)
data-engineer, database-optimizer, llm-architect, mlops-engineer, nlp-engineer, postgres-pro, prompt-engineer

### Specialized Domains (10)
api-documenter, blockchain-developer, embedded-systems, game-developer, iot-engineer, m365-admin, mobile-app-developer, payment-integration, quant-analyst, risk-manager

### Meta-Orchestration (7)
agent-installer, agent-organizer, context-manager, error-coordinator, it-ops-orchestrator, performance-monitor, task-distributor

### Core Development (4)
electron-pro, graphql-architect, websocket-engineer, mobile-developer

### Business/Product (4)
project-manager, sales-engineer, scrum-master, wordpress-master

### Research (1)
trend-analyst

---

## 3. SUSAN UNIQUE -- Agents with NO VoltAgent Equivalent (67 agents)

These are preserved as-is in the merged roster. VoltAgent is purely an engineering/DevOps toolkit; Susan's domain expertise, creative studios, and vertical-specific agents are entirely unique.

### Strategy (6)
steve-strategy, bridge-partnerships, vault-fundraising, recruiting-strategy-studio, ledger-finance (PARTIAL overlap with fintech-engineer), shield-legal-compliance (EXACT with legal-advisor -- kept)

### Product (8, after PM dedup)
marcus-ux (PARTIAL overlap), mira-emotional-experience, ai-product-manager, conversation-designer, echo-neuro-design, lens-accessibility (PARTIAL overlap), prism-brand, ux-design-process

### Engineering (5, after dedup)
atlas-engineering (PARTIAL overlaps), nova-ai (PARTIAL overlaps), knowledge-engineer (PARTIAL overlap), ai-evaluation-specialist, algorithm-lab

### Science (7) -- entirely unique
coach-exercise-science, sage-nutrition, drift-sleep-recovery, workout-program-studio, coaching-architecture-studio, workout-session-studio, training-research-studio

### Psychology (3) -- entirely unique
freya-behavioral-economics, flow-sports-psychology, quest-gamification

### Growth (7)
aria-growth, haven-community, herald-pr, beacon-aso (PARTIAL overlap with seo-specialist), coach-outreach-studio, x-growth-studio, guide-customer-success (EXACT -- kept)

### Research (5, after dedup)
research-director, research-ops, researcher-web, researcher-reddit, researcher-appstore

### Studio (12) -- entirely unique
deck-studio, design-studio-director, landing-page-studio, app-experience-studio, marketing-studio-director, article-studio, memo-studio, social-media-studio, whitepaper-studio, instagram-studio, recruiting-dashboard-studio, photography-studio

### Film Studio (17) -- entirely unique
film-studio-director, screenwriter-studio, cinematography-studio, editing-studio, color-grade-studio, vfx-studio, sound-design-studio, music-score-studio, production-designer-studio, production-manager-studio, talent-cast-studio, distribution-studio, legal-rights-studio, highlight-reel-studio, audio-gen-engine, film-gen-engine, image-gen-engine

### Slideworks (3) -- entirely unique
slideworks-strategist, slideworks-creative-director, slideworks-builder

### Oracle Health (2) -- entirely unique
oracle-health-marketing-lead, oracle-health-product-marketing

### Claude Code Operational (15) -- entirely unique
jake, orchestrator, research, susan (CC version), kira, aria, digest, scout, herald, oracle-brief, ledger (CC), sentinel-health, pattern-matcher, antifragility-monitor, optionality-scout, link-validator

---

## 4. MERGED ROSTER

### New Group Structure (16 groups)

The merge combines VoltAgent's 10 engineering-heavy categories with Susan's 12 domain-heavy groups into 16 unified groups. The principle: **engineering groups absorb VoltAgent agents; domain groups preserve Susan agents; new groups emerge where neither had coverage.**

---

#### GROUP 1: orchestration (5 agents)
*Meta-level coordination and system management*

| Agent | Source | Role |
|---|---|---|
| susan | Susan | Domain orchestrator, capability foundry |
| jake | CC-Ops | Root interaction layer, co-founder operator |
| orchestrator | CC-Ops | Claude Code multi-agent coordinator |
| multi-agent-coordinator | VoltAgent | General multi-agent coordination |
| workflow-orchestrator | VoltAgent | Workflow design and execution |

#### GROUP 2: strategy (6 agents)
*Business strategy, legal, finance, fundraising, partnerships*

| Agent | Source | Role |
|---|---|---|
| steve-strategy | Susan | Chief strategist |
| shield-legal-compliance | Susan | Legal + compliance (absorbs VoltAgent legal-advisor) |
| bridge-partnerships | Susan | Partnership development |
| ledger-finance | Susan | Financial strategy |
| vault-fundraising | Susan | Fundraising strategy |
| recruiting-strategy-studio | Susan | Recruiting strategy |

#### GROUP 3: product (10 agents)
*Product management, UX, design, brand, accessibility*

| Agent | Source | Role |
|---|---|---|
| compass-product | Susan | Product strategy (absorbs VoltAgent product-manager) |
| ai-product-manager | Susan | AI-specific product management |
| marcus-ux | Susan | UX research and design |
| mira-emotional-experience | Susan | Emotional experience design |
| conversation-designer | Susan | Conversational UX |
| echo-neuro-design | Susan | Neuro-design patterns |
| lens-accessibility | Susan | Accessibility design (complements VoltAgent accessibility-tester) |
| prism-brand | Susan | Brand identity |
| ux-design-process | Susan | UX process frameworks |
| ui-designer | VoltAgent | UI implementation and component design |

#### GROUP 4: engineering-core (14 agents)
*Architecture, full-stack development, APIs, real-time systems*

| Agent | Source | Role |
|---|---|---|
| atlas-engineering | Susan | Engineering lead and architecture |
| api-designer | VoltAgent | API design specialist |
| backend-developer | VoltAgent | Backend implementation |
| frontend-developer | VoltAgent | Frontend implementation |
| fullstack-developer | VoltAgent | Full-stack implementation |
| graphql-architect | VoltAgent | GraphQL API design |
| microservices-architect | VoltAgent | Microservices architecture |
| mobile-developer | VoltAgent | Mobile development |
| mobile-app-developer | VoltAgent | Mobile app specialist |
| electron-pro | VoltAgent | Desktop app development |
| websocket-engineer | VoltAgent | Real-time communications |
| api-documenter | VoltAgent | API documentation |
| mcp-developer | VoltAgent | MCP protocol integration |
| cli-developer | VoltAgent | CLI tooling |

#### GROUP 5: language-specialists (28 agents)
*Language and framework experts -- entirely from VoltAgent*

| Agent | Source | Role |
|---|---|---|
| angular-architect | VoltAgent | Angular framework |
| cpp-pro | VoltAgent | C++ |
| csharp-developer | VoltAgent | C# |
| django-developer | VoltAgent | Django framework |
| dotnet-core-expert | VoltAgent | .NET Core |
| dotnet-framework-4.8-expert | VoltAgent | .NET Framework 4.8 |
| elixir-expert | VoltAgent | Elixir/OTP |
| expo-react-native-expert | VoltAgent | React Native/Expo |
| fastapi-developer | VoltAgent | FastAPI |
| flutter-expert | VoltAgent | Flutter/Dart |
| golang-pro | VoltAgent | Go |
| java-architect | VoltAgent | Java |
| javascript-pro | VoltAgent | JavaScript |
| kotlin-specialist | VoltAgent | Kotlin |
| laravel-specialist | VoltAgent | Laravel/PHP |
| nextjs-developer | VoltAgent | Next.js |
| php-pro | VoltAgent | PHP |
| powershell-5.1-expert | VoltAgent | PowerShell 5.1 |
| powershell-7-expert | VoltAgent | PowerShell 7 |
| python-pro | VoltAgent | Python |
| rails-expert | VoltAgent | Ruby on Rails |
| react-specialist | VoltAgent | React |
| rust-engineer | VoltAgent | Rust |
| spring-boot-engineer | VoltAgent | Spring Boot |
| sql-pro | VoltAgent | SQL |
| swift-expert | VoltAgent | Swift |
| typescript-pro | VoltAgent | TypeScript |
| vue-expert | VoltAgent | Vue.js |

#### GROUP 6: infrastructure (16 agents)
*Cloud, containers, networking, platform, SRE -- entirely from VoltAgent*

| Agent | Source | Role |
|---|---|---|
| azure-infra-engineer | VoltAgent | Azure cloud |
| cloud-architect | VoltAgent | Cloud architecture |
| database-administrator | VoltAgent | Database operations |
| deployment-engineer | VoltAgent | Deployment automation |
| devops-engineer | VoltAgent | DevOps practices |
| devops-incident-responder | VoltAgent | DevOps incident response |
| docker-expert | VoltAgent | Docker/containers |
| incident-responder | VoltAgent | General incident response |
| kubernetes-specialist | VoltAgent | Kubernetes orchestration |
| network-engineer | VoltAgent | Network design |
| platform-engineer | VoltAgent | Platform engineering |
| sre-engineer | VoltAgent | Site reliability engineering |
| terraform-engineer | VoltAgent | Terraform IaC |
| terragrunt-expert | VoltAgent | Terragrunt IaC |
| windows-infra-admin | VoltAgent | Windows server admin |
| m365-admin | VoltAgent | Microsoft 365 admin |

#### GROUP 7: quality-security (15 agents)
*QA, security, testing, compliance, code review*

| Agent | Source | Role |
|---|---|---|
| forge-qa | Susan | QA lead (absorbs VoltAgent qa-expert) |
| sentinel-security | Susan | Security lead |
| ai-evaluation-specialist | Susan | AI model evaluation |
| accessibility-tester | VoltAgent | Accessibility testing (complements lens-accessibility) |
| ad-security-reviewer | VoltAgent | Active Directory security |
| architect-reviewer | VoltAgent | Architecture review |
| chaos-engineer | VoltAgent | Chaos/resilience testing |
| code-reviewer | VoltAgent | Code review |
| compliance-auditor | VoltAgent | Technical compliance (complements shield) |
| debugger | VoltAgent | Debugging specialist |
| error-detective | VoltAgent | Error investigation |
| penetration-tester | VoltAgent | Penetration testing |
| performance-engineer | VoltAgent | Performance optimization |
| powershell-security-hardening | VoltAgent | Windows security hardening |
| test-automator | VoltAgent | Test automation |

#### GROUP 8: data-ai (14 agents)
*Data science, ML, AI, LLMs, data engineering*

| Agent | Source | Role |
|---|---|---|
| nova-ai | Susan | AI/ML lead |
| pulse-data-science | Susan | Data science lead (absorbs VoltAgent data-scientist) |
| algorithm-lab | Susan | Advanced algorithm R&D |
| knowledge-engineer | Susan | Knowledge architecture |
| ai-engineer | VoltAgent | AI implementation |
| data-analyst | VoltAgent | Data analysis |
| data-engineer | VoltAgent | Data pipeline engineering |
| database-optimizer | VoltAgent | Database performance |
| llm-architect | VoltAgent | LLM architecture |
| ml-engineer | VoltAgent | ML implementation |
| mlops-engineer | VoltAgent | ML operations |
| nlp-engineer | VoltAgent | NLP specialist |
| postgres-pro | VoltAgent | PostgreSQL specialist |
| prompt-engineer | VoltAgent | Prompt engineering |

Note: VoltAgent's machine-learning-engineer and ml-engineer are merged into **ml-engineer** (they are redundant).

#### GROUP 9: developer-experience (12 agents)
*Build systems, DX, tooling, refactoring -- entirely from VoltAgent*

| Agent | Source | Role |
|---|---|---|
| build-engineer | VoltAgent | Build systems |
| dependency-manager | VoltAgent | Dependency management |
| documentation-engineer | VoltAgent | Technical documentation |
| dx-optimizer | VoltAgent | Developer experience |
| git-workflow-manager | VoltAgent | Git workflows |
| legacy-modernizer | VoltAgent | Legacy modernization |
| powershell-module-architect | VoltAgent | PowerShell modules |
| powershell-ui-architect | VoltAgent | PowerShell UI |
| refactoring-specialist | VoltAgent | Code refactoring |
| slack-expert | VoltAgent | Slack integration |
| tooling-engineer | VoltAgent | Developer tooling |
| wordpress-master | VoltAgent | WordPress specialist |

#### GROUP 10: specialized-domains (8 agents)
*Blockchain, embedded, fintech, gaming, IoT, payments*

| Agent | Source | Role |
|---|---|---|
| blockchain-developer | VoltAgent | Blockchain/Web3 |
| embedded-systems | VoltAgent | Embedded systems |
| fintech-engineer | VoltAgent | Fintech implementation |
| game-developer | VoltAgent | Game development |
| iot-engineer | VoltAgent | IoT systems |
| payment-integration | VoltAgent | Payment processing |
| quant-analyst | VoltAgent | Quantitative analysis |
| risk-manager | VoltAgent | Risk management |

#### GROUP 11: business-ops (7 agents)
*Business analysis, project management, sales, marketing, SEO*

| Agent | Source | Role |
|---|---|---|
| guide-customer-success | Susan | Customer success (absorbs VoltAgent CSM) |
| business-analyst | VoltAgent | Business analysis |
| content-marketer | VoltAgent | Content marketing |
| project-manager | VoltAgent | Project management |
| sales-engineer | VoltAgent | Sales engineering |
| scrum-master | VoltAgent | Agile process |
| seo-specialist | VoltAgent | SEO optimization |

#### GROUP 12: meta-orchestration (12 agents)
*Agent management, context, monitoring, task distribution*

| Agent | Source | Role |
|---|---|---|
| kira | CC-Ops | Intelligence coordinator |
| aria | CC-Ops | Growth intelligence |
| digest | CC-Ops | Intelligence digest |
| scout | CC-Ops | Opportunity scout |
| oracle-brief | CC-Ops | Oracle briefing |
| sentinel-health | CC-Ops | System health monitoring |
| pattern-matcher | CC-Ops | Pattern detection |
| antifragility-monitor | CC-Ops | Antifragility assessment |
| optionality-scout | CC-Ops | Option space exploration |
| agent-installer | VoltAgent | Agent setup tooling |
| agent-organizer | VoltAgent | Agent management |
| context-manager | VoltAgent | Context window management |

#### GROUP 13: research-analysis (14 agents)
*Research coordination, source-specific researchers, analysis*

| Agent | Source | Role |
|---|---|---|
| research-director | Susan | Research coordination lead |
| research-ops | Susan | Research operations |
| researcher-web | Susan | Web research |
| researcher-arxiv | Susan | Academic research (absorbs VoltAgent scientific-literature-researcher) |
| researcher-reddit | Susan | Reddit/community research |
| researcher-appstore | Susan | App store research |
| research (CC) | CC-Ops | Claude Code research agent |
| competitive-analyst | VoltAgent | Competitive analysis |
| data-researcher | VoltAgent | Data research |
| market-researcher | VoltAgent | Market research |
| research-analyst | VoltAgent | Research analysis |
| search-specialist | VoltAgent | Search optimization |
| trend-analyst | VoltAgent | Trend analysis |
| link-validator | CC-Ops | Link validation |

#### GROUP 14: science-psychology (10 agents)
*Exercise science, nutrition, sleep, psychology -- entirely Susan*

| Agent | Source | Role |
|---|---|---|
| coach-exercise-science | Susan | Exercise science |
| sage-nutrition | Susan | Nutrition science |
| drift-sleep-recovery | Susan | Sleep and recovery |
| workout-program-studio | Susan | Workout programming |
| coaching-architecture-studio | Susan | Coaching system design |
| workout-session-studio | Susan | Session design |
| training-research-studio | Susan | Training research |
| freya-behavioral-economics | Susan | Behavioral economics |
| flow-sports-psychology | Susan | Sports psychology |
| quest-gamification | Susan | Gamification design |

#### GROUP 15: growth-marketing (7 agents)
*Growth, community, PR, ASO, outreach -- entirely Susan*

| Agent | Source | Role |
|---|---|---|
| aria-growth | Susan | Growth strategy |
| haven-community | Susan | Community building |
| herald-pr | Susan | PR and communications |
| herald (CC) | CC-Ops | CC PR briefing agent |
| beacon-aso | Susan | App Store Optimization |
| coach-outreach-studio | Susan | Outreach campaigns |
| x-growth-studio | Susan | X/Twitter growth |

#### GROUP 16: creative-studio (32 agents)
*Design, content, film, slideworks, photography -- entirely Susan*

| Agent | Source | Role |
|---|---|---|
| deck-studio | Susan | Presentation design |
| design-studio-director | Susan | Design direction |
| landing-page-studio | Susan | Landing page design |
| app-experience-studio | Susan | App experience design |
| marketing-studio-director | Susan | Marketing creative direction |
| article-studio | Susan | Article creation |
| memo-studio | Susan | Memo/brief creation |
| social-media-studio | Susan | Social media content |
| whitepaper-studio | Susan | Whitepaper creation |
| instagram-studio | Susan | Instagram content |
| recruiting-dashboard-studio | Susan | Recruiting dashboards |
| photography-studio | Susan | Photography direction |
| film-studio-director | Susan | Film direction |
| screenwriter-studio | Susan | Screenwriting |
| cinematography-studio | Susan | Cinematography |
| editing-studio | Susan | Video editing |
| color-grade-studio | Susan | Color grading |
| vfx-studio | Susan | Visual effects |
| sound-design-studio | Susan | Sound design |
| music-score-studio | Susan | Music composition |
| production-designer-studio | Susan | Production design |
| production-manager-studio | Susan | Production management |
| talent-cast-studio | Susan | Talent casting |
| distribution-studio | Susan | Distribution |
| legal-rights-studio | Susan | Media legal/rights |
| highlight-reel-studio | Susan | Highlight reels |
| audio-gen-engine | Susan | Audio generation |
| film-gen-engine | Susan | Film generation |
| image-gen-engine | Susan | Image generation |
| slideworks-strategist | Susan | Presentation strategy |
| slideworks-creative-director | Susan | Presentation creative |
| slideworks-builder | Susan | Presentation building |

#### GROUP 17: vertical-specific (4 agents)
*Industry-specific agents*

| Agent | Source | Role |
|---|---|---|
| oracle-health-marketing-lead | Susan | Oracle Health marketing |
| oracle-health-product-marketing | Susan | Oracle Health product marketing |
| ledger (CC) | CC-Ops | CC financial intelligence |
| susan (CC) | CC-Ops | CC Susan interface |

#### Ungrouped VoltAgent infrastructure agents absorbed:
- error-coordinator -> GROUP 12 (meta-orchestration)
- it-ops-orchestrator -> GROUP 6 (infrastructure)
- performance-monitor -> GROUP 12 (meta-orchestration)
- task-distributor -> GROUP 12 (meta-orchestration)
- technical-writer -> GROUP 9 (developer-experience, as documentation-engineer covers this)

**REVISED GROUP 12 (meta-orchestration): 15 agents** (add error-coordinator, performance-monitor, task-distributor)
**REVISED GROUP 6 (infrastructure): 17 agents** (add it-ops-orchestrator)

---

### MERGED ROSTER TOTALS

| Group | Count | VoltAgent | Susan | CC-Ops |
|---|---|---|---|---|
| 1. orchestration | 5 | 2 | 1 | 2 |
| 2. strategy | 6 | 0 | 6 | 0 |
| 3. product | 10 | 1 | 9 | 0 |
| 4. engineering-core | 14 | 13 | 1 | 0 |
| 5. language-specialists | 28 | 28 | 0 | 0 |
| 6. infrastructure | 17 | 16 | 0 | 0 |
| 7. quality-security | 15 | 12 | 3 | 0 |
| 8. data-ai | 14 | 10 | 4 | 0 |
| 9. developer-experience | 12 | 12 | 0 | 0 |
| 10. specialized-domains | 8 | 8 | 0 | 0 |
| 11. business-ops | 7 | 6 | 1 | 0 |
| 12. meta-orchestration | 15 | 6 | 0 | 9 |
| 13. research-analysis | 14 | 6 | 6 | 2 |
| 14. science-psychology | 10 | 0 | 10 | 0 |
| 15. growth-marketing | 7 | 0 | 6 | 1 |
| 16. creative-studio | 32 | 0 | 32 | 0 |
| 17. vertical-specific | 4 | 0 | 2 | 2 |
| **TOTAL** | **218** | **120** | **81** | **16** |

**Dedup accounting**: 126 VoltAgent - 6 EXACT duplicates = 120. Susan 83 - 2 absorbed = 81. Plus 1 VoltAgent redundancy (machine-learning-engineer merged with ml-engineer). CC-Ops 15 + 1 (link-validator) = 16.

**Final merged roster: 218 unique agents across 17 groups.**

---

## 5. CATEGORY MAPPING

### How VoltAgent's 10 Categories Map to Merged Groups

| VoltAgent Category | Merged Group(s) | Notes |
|---|---|---|
| 01-core-development (10) | 4. engineering-core (9), 3. product (1: ui-designer) | ui-designer moves to product group |
| 02-language-specialists (28) | 5. language-specialists (28) | 1:1 mapping, new dedicated group |
| 03-infrastructure (16) | 6. infrastructure (16) | 1:1 mapping, absorbs m365-admin from cat 07 |
| 04-quality-security (14) | 7. quality-security (12) | qa-expert merged with forge-qa; security-auditor absorbed by sentinel |
| 05-data-ai (13) | 8. data-ai (10) | data-scientist merged with pulse; ml-engineer deduped; reinforcement-learning merged conceptually with algorithm-lab |
| 06-developer-experience (13) | 9. developer-experience (12), 4. engineering-core (1: mcp-developer + cli-developer) | Build-adjacent tooling stays in DevEx; MCP/CLI move to engineering-core |
| 07-specialized-domains (12) | 10. specialized-domains (8), 6. infrastructure (1: m365-admin), 4. engineering-core (2: mobile-app-dev, api-documenter) | Scattered by function |
| 08-business-product (11) | 11. business-ops (6), 3. product (0, absorbed), 2. strategy (0, absorbed) | product-manager -> compass-product; legal-advisor -> shield; CSM -> guide |
| 09-meta-orchestration (10) | 1. orchestration (2), 12. meta-orchestration (6) | Coordination splits between high-level (orchestration) and tooling (meta) |
| 10-research-analysis (7) | 13. research-analysis (6) | scientific-lit-researcher merged with researcher-arxiv |

### How Susan's 12 Groups Map to Merged Groups

| Susan Group | Merged Group | Notes |
|---|---|---|
| orchestration (1) | 1. orchestration | Susan stays as domain orchestrator |
| strategy (6) | 2. strategy | 1:1, absorbs legal-advisor |
| product (9) | 3. product | Gains ui-designer from VoltAgent |
| engineering (8) | 4. engineering-core + 7. quality-security + 8. data-ai | Split by function: atlas->core, sentinel+forge->quality, nova+pulse+algo->data-ai |
| science (7) | 14. science-psychology | Merged with psychology |
| psychology (3) | 14. science-psychology | Merged with science |
| growth (7) | 15. growth-marketing | 1:1 with herald (CC) addition |
| research (6) | 13. research-analysis | Gains VoltAgent research agents |
| studio (12) | 16. creative-studio | Merged with film_studio and slideworks |
| film_studio (17) | 16. creative-studio | Merged with studio and slideworks |
| slideworks (3) | 16. creative-studio | Merged with studio and film_studio |
| oracle_health (2) | 17. vertical-specific | Industry-specific vertical |

---

## STRATEGIC SUMMARY

### What VoltAgent brings that Susan lacks entirely:
1. **Language/framework expertise** (28 agents) -- the single biggest gap
2. **Infrastructure/DevOps** (16 agents) -- cloud, containers, IaC, SRE
3. **Developer experience** (13 agents) -- build systems, tooling, refactoring
4. **Specialized engineering domains** (10 agents) -- blockchain, IoT, embedded, gaming

### What Susan has that VoltAgent lacks entirely:
1. **Creative studios** (32 agents) -- film, design, content, photography
2. **Science/psychology** (10 agents) -- exercise, nutrition, behavioral economics
3. **Growth/marketing** (7 agents) -- PR, community, ASO, outreach
4. **Strategy** (6 agents) -- fundraising, partnerships, legal, finance
5. **Vertical-specific** (2 agents) -- Oracle Health

### The complementary thesis:
VoltAgent is an **engineering-first** toolkit. Susan is a **business/creative-first** platform. The overlap is only 4.8% EXACT, meaning 95.2% of the combined roster brings unique value. The merge transforms the system from a startup intelligence OS into a **full-spectrum software + business intelligence OS**.
