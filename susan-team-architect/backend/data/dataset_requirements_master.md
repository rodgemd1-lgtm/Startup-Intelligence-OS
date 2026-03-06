# Susan Intelligence OS — Master Dataset Requirements

> **Purpose:** Comprehensive inventory of all datasets needed to power Susan's 22 AI agents.
> Each dataset maps to specific agents, data_types, and ingestion pipelines.
> Status: ✅ = ingested, 🔄 = partially done, ❌ = not started

---

## Current RAG Knowledge Base Status (698 chunks)

| data_type | chunks | status |
|-----------|--------|--------|
| user_research | 282 | ✅ app_store + reddit |
| behavioral_economics | 186 | ✅ BE module + books |
| exercise_science | 118 | ✅ exercise DB + books |
| ai_ml_research | 35 | ✅ arXiv papers |
| ux_research | 25 | ✅ web scraping |
| growth_marketing | 23 | ✅ web scraping |
| market_research | 12 | ✅ web scraping |
| sleep_recovery | 9 | ✅ books synthesis |
| business_strategy | 8 | ✅ books synthesis |

### Pending Ingestion (in progress)
- agent_prompts (TransformFit Elite Skillset) → company: transformfit
- ux_framework (Double Black Box Playbook) → company: shared

---

## TIER 1: CORE DATASETS (Critical for Susan to function)

### 1. Exercise Science & Biomechanics
**Agents:** Coach, Sage, Drift, Lens
**data_type:** `exercise_science`
**Status:** 🔄 118 chunks (need 500+)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Exercise database (500+ movements) | ACSM, NSCA, ACE databases | Manual/AI synthesis | ❌ HIGH — only 100 exercises now |
| Progressive overload protocols | Research papers + textbooks | arXiv + books | ❌ HIGH |
| Movement patterns by age group (30+) | PubMed, ACSM guidelines | Web + arXiv | ❌ HIGH |
| Injury prevention protocols | NSCA, physical therapy literature | Web + books | ❌ HIGH |
| Biomechanics reference data | OpenSim, movement science papers | arXiv | ❌ MEDIUM |
| Equipment-specific programming | Manufacturer guides, fitness sites | Web (Firecrawl) | ❌ MEDIUM |
| Flexibility/mobility protocols | FMS, yoga, physical therapy | Web + books | ❌ MEDIUM |
| Exercise regression/progression trees | Certified trainer knowledge | AI synthesis | ❌ HIGH |
| Form cues and common errors per exercise | NSCA, ACE, certified trainers | AI synthesis | ❌ HIGH |
| Warm-up/cool-down protocols | Exercise physiology textbooks | Books synthesis | ❌ MEDIUM |

### 2. Nutrition Science
**Agents:** Sage, Coach
**data_type:** `nutrition`
**Status:** ❌ 0 chunks (CRITICAL GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Macronutrient guidelines by goal | ISSN, AND position papers | Web + arXiv | ❌ CRITICAL |
| Meal plan templates (cut/maintain/bulk) | Certified nutrition databases | AI synthesis | ❌ CRITICAL |
| Food database (macros per serving) | USDA FoodData Central API | Custom API ingestor | ❌ HIGH |
| Supplement evidence base | Examine.com, ISSN reviews | Web (Firecrawl) | ❌ HIGH |
| Nutrient timing research | Sports nutrition journals | arXiv | ❌ MEDIUM |
| Dietary restriction accommodations | AND, food allergy databases | Web | ❌ MEDIUM |
| Hydration guidelines | ACSM fluid replacement | Web | ❌ LOW |
| Meal prep strategies & recipes | Popular fitness nutrition sites | Web (Firecrawl) | ❌ MEDIUM |
| Metabolic adaptation research (30+) | Endocrine/aging journals | arXiv | ❌ HIGH |

### 3. Sleep & Recovery
**Agents:** Drift, Coach
**data_type:** `sleep_recovery`
**Status:** 🔄 9 chunks (need 100+)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Sleep hygiene protocols | Sleep Foundation, AASM | Web (Firecrawl) | ❌ HIGH |
| Recovery modality evidence | Cold plunge, sauna, massage research | arXiv + Web | ❌ HIGH |
| Circadian rhythm optimization | Chronobiology research | arXiv | ❌ MEDIUM |
| Overtraining syndrome markers | Sports medicine literature | arXiv | ❌ MEDIUM |
| Stress-recovery balance models | HRV research, autonomic nervous system | arXiv | ❌ HIGH |
| Wearable sleep metrics interpretation | Whoop, Oura, Fitbit research | Web | ❌ MEDIUM |
| Age-related recovery considerations | Geriatric exercise medicine | arXiv | ❌ HIGH |

### 4. Behavioral Economics & Retention
**Agents:** Freya, Flow, Quest, Guide, Echo
**data_type:** `behavioral_economics`
**Status:** ✅ 186 chunks (good base, expand)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Fitness habit formation research | BJ Fogg, James Clear, academic | Books + arXiv | 🔄 MEDIUM |
| Gamification frameworks for health | Octalysis, Yu-kai Chou | Web + books | ❌ HIGH |
| Loss aversion in fitness apps | Behavioral economics journals | arXiv | ❌ HIGH |
| Streak/reward system case studies | Duolingo, Strava, Peloton analysis | Web | ❌ HIGH |
| Notification timing psychology | Push notification research | arXiv + Web | ❌ MEDIUM |
| Social proof mechanisms | Community fitness research | arXiv | ❌ MEDIUM |
| Variable reward schedules | Slot machine psychology applied to UX | Books + arXiv | ❌ MEDIUM |
| Commitment device research | StickK, GymPact studies | arXiv | ❌ LOW |

### 5. User Research & Customer Data
**Agents:** Freya, Pulse, Haven, Guide, Aria
**data_type:** `user_research`
**Status:** ✅ 282 chunks (strong base, expand)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Target audience psychographics (30-55) | Market research reports | Web + AI synthesis | ❌ HIGH |
| Fitness app churn reasons | App store reviews (expanded) | App Store ingestor | 🔄 MEDIUM |
| User journey mapping data | UX research databases | Web | ❌ HIGH |
| Competitor user reviews (Fitbod, Future, Noom, etc.) | App Store, Google Play | App Store ingestor | ❌ HIGH |
| Reddit fitness communities (expanded) | r/fitness, r/over30, r/bodybuilding | Reddit ingestor | 🔄 MEDIUM |
| Customer persona research | Survey data, interview transcripts | Manual + AI | ❌ HIGH |
| Pain point analysis by demographic | Forum mining, social listening | Reddit + Web | ❌ MEDIUM |
| Feature request analysis | App reviews, forums, ProductHunt | App Store + Web | ❌ MEDIUM |
| NPS benchmark data for fitness apps | Industry reports | Web | ❌ LOW |

---

## TIER 2: BUSINESS & STRATEGY DATASETS

### 6. Market Research & Competitive Intelligence
**Agents:** Steve, Susan, Ledger, Pulse
**data_type:** `market_research`
**Status:** 🔄 12 chunks (need 100+)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Connected fitness market sizing (TAM/SAM/SOM) | Statista, IBISWorld, Grand View | Web | ❌ HIGH |
| Competitor feature matrices | App analysis, product pages | Web (Firecrawl) | ❌ HIGH |
| Subscription fitness pricing benchmarks | Competitor app stores | App Store + Web | ❌ HIGH |
| Fitness tech funding landscape | Crunchbase, PitchBook | Web | ❌ MEDIUM |
| Consumer fitness spending trends | BLS, industry reports | Web | ❌ MEDIUM |
| Digital health regulation trends | FDA, FTC guidance | Web | ❌ MEDIUM |
| Wearable device market penetration | IDC, Statista | Web | ❌ LOW |
| Corporate wellness market data | Industry reports | Web | ❌ MEDIUM |

### 7. Business Strategy & Finance
**Agents:** Steve, Ledger, Bridge
**data_type:** `business_strategy`, `finance`
**Status:** 🔄 8 chunks (need 80+)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| SaaS/subscription unit economics benchmarks | SaaS Capital, Bessemer | Web | ❌ HIGH |
| Fitness app monetization models | Industry analysis | Web + AI synthesis | ❌ HIGH |
| Startup financial model templates | YC, a16z resources | Web | ❌ MEDIUM |
| Pricing strategy frameworks | Van Westendorp, conjoint analysis | Books + Web | ❌ MEDIUM |
| Churn reduction case studies | SaaS/subscription businesses | Web | ❌ HIGH |
| LTV/CAC optimization research | Subscription economy literature | Web + books | ❌ MEDIUM |
| Fundraising benchmarks (pre-seed/seed) | VC blog posts, reports | Web | ❌ LOW |

### 8. Growth Marketing & Content
**Agents:** Aria, Haven, Herald
**data_type:** `growth_marketing`, `content_strategy`
**Status:** 🔄 23 chunks (need 100+)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Instagram algorithm best practices (2026) | Social media marketing blogs | Web (Firecrawl) | ❌ HIGH |
| Fitness influencer marketing data | HypeAuditor, Grin research | Web | ❌ HIGH |
| Content marketing frameworks for D2C | HubSpot, Buffer research | Web | ❌ MEDIUM |
| Email/SMS nurture sequence templates | SaaS marketing resources | Web + AI synthesis | ❌ MEDIUM |
| SEO keyword data (fitness vertical) | SEMrush, Ahrefs public data | Web | ❌ MEDIUM |
| Referral program design patterns | Viral loop case studies | Web | ❌ MEDIUM |
| Community building playbooks (Skool, Discord) | Community management resources | Web | ❌ MEDIUM |
| UGC campaign frameworks | Brand examples, case studies | Web | ❌ LOW |

### 9. Legal & Compliance
**Agents:** Shield, Sentinel
**data_type:** `legal_compliance`
**Status:** ❌ 0 chunks (CRITICAL GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| HIPAA requirements for fitness apps | HHS.gov, legal guides | Web (Firecrawl) | ❌ CRITICAL |
| GDPR compliance checklist | GDPR.eu, ICO guidance | Web | ❌ HIGH |
| FTC fitness/health claims guidelines | FTC.gov | Web | ❌ HIGH |
| CCPA/CPRA requirements | CA AG office | Web | ❌ HIGH |
| Apple Health & Google Fit data policies | Developer docs | Web | ❌ HIGH |
| Terms of Service templates (subscription) | Legal template databases | Web + AI synthesis | ❌ MEDIUM |
| Privacy policy frameworks | IAPP resources | Web | ❌ MEDIUM |
| Influencer disclosure requirements (FTC) | FTC endorsement guides | Web | ❌ MEDIUM |

---

## TIER 3: PRODUCT & DESIGN DATASETS

### 10. UX/UI Research & Design Patterns
**Agents:** Marcus, Echo, Lens
**data_type:** `ux_research`
**Status:** 🔄 25 chunks (need 200+)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Mobile fitness app UI patterns | Mobbin, Screenlane, Pttrns | Web (Firecrawl) | ❌ HIGH |
| Interaction design principles | NNGroup, Laws of UX | Web | ❌ HIGH |
| Information architecture best practices | IA Institute, Rosenfeld Media | Web + books | ❌ HIGH |
| User flow optimization patterns | UX research databases | Web | ❌ HIGH |
| Behavioral design frameworks | BJ Fogg, Don Norman | Books synthesis | ❌ HIGH |
| Accessibility guidelines (WCAG 2.2) | W3C, WebAIM | Web | ❌ HIGH |
| Design system best practices | Shopify Polaris, Material Design | Web | ❌ MEDIUM |
| Onboarding UX patterns | Appcues, UserPilot research | Web | ❌ HIGH |
| Dark mode design guidelines | Apple HIG, Material Design | Web | ❌ MEDIUM |
| Fitness app design case studies | UX case study sites | Web | ❌ MEDIUM |
| Double Black Box framework (expanded) | Internal playbook | ✅ Ingesting |

### 11. Technical Documentation
**Agents:** Atlas, Nova, Sentinel
**data_type:** `technical_docs`
**Status:** ❌ 0 chunks (CRITICAL GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| React Native best practices | React Native docs | Web | ❌ HIGH |
| Next.js 14 App Router patterns | Vercel docs | Web | ❌ HIGH |
| Supabase pgvector documentation | Supabase docs | Web | ❌ HIGH |
| Stripe subscription integration | Stripe docs | Web | ❌ HIGH |
| RevenueCat mobile payments | RevenueCat docs | Web | ❌ HIGH |
| Claude API / Anthropic SDK | Anthropic docs | Web | ❌ HIGH |
| Apple HealthKit / Google Health Connect | Apple/Google developer docs | Web | ❌ MEDIUM |
| Push notification best practices | Firebase, OneSignal docs | Web | ❌ MEDIUM |
| CI/CD for mobile apps | GitHub Actions, Fastlane | Web | ❌ LOW |

### 12. Security
**Agents:** Sentinel, Shield
**data_type:** `security`
**Status:** ❌ 0 chunks (CRITICAL GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| OWASP Mobile Top 10 | OWASP.org | Web | ❌ HIGH |
| Health data encryption requirements | HIPAA technical safeguards | Web | ❌ HIGH |
| API security best practices | OWASP API Security | Web | ❌ HIGH |
| Authentication patterns (JWT, OAuth) | Auth0, Clerk docs | Web | ❌ MEDIUM |
| Mobile app security checklist | OWASP MASTG | Web | ❌ MEDIUM |

---

## TIER 4: DOMAIN-SPECIFIC DATASETS

### 13. Sports Psychology & Motivation
**Agents:** Flow, Quest, Freya
**data_type:** `sports_psychology`
**Status:** ❌ 0 chunks (GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Self-determination theory in fitness | Research papers | arXiv + books | ❌ HIGH |
| Motivation science (intrinsic vs extrinsic) | Deci & Ryan, Daniel Pink | Books synthesis | ❌ HIGH |
| Exercise adherence research | Health psychology journals | arXiv | ❌ HIGH |
| Goal-setting theory (SMART, implementation intentions) | Academic + practical | Books + Web | ❌ MEDIUM |
| Self-efficacy and exercise | Bandura's work applied | arXiv | ❌ MEDIUM |
| Flow state in physical activity | Csikszentmihalyi applied | Books | ❌ MEDIUM |
| Mindfulness and exercise performance | MBSR + sport psych | arXiv | ❌ LOW |

### 14. Gamification
**Agents:** Quest, Echo, Flow
**data_type:** `gamification`
**Status:** ❌ 0 chunks (GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Octalysis framework | Yu-kai Chou materials | Web + books | ❌ HIGH |
| Health gamification case studies | Pokémon Go, Zombies Run, Ring Fit | Web | ❌ HIGH |
| FitCoin/token economy design | Virtual economy design patterns | Web + books | ❌ HIGH |
| Leaderboard psychology | Competition research | arXiv | ❌ MEDIUM |
| Achievement system design | Game design literature | Books + Web | ❌ MEDIUM |
| Wager/challenge mechanics | StickK, DietBet analysis | Web | ❌ MEDIUM |
| Progression system design | RPG game design applied to fitness | Web + AI synthesis | ❌ MEDIUM |

### 15. Community & Social Fitness
**Agents:** Haven, Guide, Herald
**data_type:** `community`
**Status:** ❌ 0 chunks (GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Online community building frameworks | CMX Hub, community management | Web | ❌ HIGH |
| Accountability partner research | Health behavior studies | arXiv | ❌ HIGH |
| Social fitness features analysis | Strava, Peloton, Nike Run Club | Web + App Store | ❌ HIGH |
| Moderation best practices | Community management resources | Web | ❌ MEDIUM |
| Group challenge design | CrossFit, Orangetheory models | Web | ❌ MEDIUM |
| Ambassador/champion programs | Community-led growth resources | Web | ❌ MEDIUM |

### 16. Partnerships & Ecosystem
**Agents:** Bridge, Aria
**data_type:** `partnerships`
**Status:** ❌ 0 chunks (GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Fitness influencer landscape | HypeAuditor, Instagram analysis | Web | ❌ HIGH |
| Affiliate program structures | ShareASale, Impact benchmarks | Web | ❌ MEDIUM |
| Corporate wellness market | Industry reports | Web | ❌ MEDIUM |
| Brand partnership frameworks | D2C partnership case studies | Web | ❌ LOW |
| Wearable integration partnerships | Garmin, Apple, Fitbit programs | Web | ❌ MEDIUM |

### 17. PR & Communications
**Agents:** Herald
**data_type:** `pr_communications`
**Status:** ❌ 0 chunks (GAP)

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Startup launch PR playbooks | First Round, YC resources | Web | ❌ MEDIUM |
| Fitness media landscape | Health/fitness publication list | Web | ❌ MEDIUM |
| Press release templates | PR Newswire resources | Web + AI | ❌ LOW |
| Crisis communication frameworks | PR best practices | Web | ❌ LOW |

---

## TIER 5: BIOMETRIC & PUBLIC HEALTH DATA

### 18. Public Health & Fitness Biometrics
**Agents:** Coach, Sage, Drift, Pulse
**data_type:** `biometrics`, `exercise_science`
**Status:** ❌ 0 chunks

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| NHANES physical activity data | CDC NHANES API | NHANES ingestor | ❌ HIGH |
| Body composition norms by age/sex | CDC, WHO | Web + NHANES | ❌ HIGH |
| VO2max norms and age-adjusted targets | ACSM fitness testing | Web + books | ❌ HIGH |
| Heart rate training zones by age | Karvonen formula data | AI synthesis | ❌ MEDIUM |
| Strength standards by age/weight | ExRx, Strength Level data | Web (Firecrawl) | ❌ HIGH |
| Flexibility norms by age | ACSM sit-and-reach data | Web | ❌ MEDIUM |
| Caloric expenditure by activity (MET values) | Compendium of Physical Activities | Web | ❌ HIGH |
| Resting metabolic rate formulas | Mifflin-St Jeor, Harris-Benedict | AI synthesis | ❌ HIGH |
| Blood pressure/cholesterol norms | AHA guidelines | Web | ❌ MEDIUM |
| Wearable accuracy studies | Validation research | arXiv | ❌ MEDIUM |

---

## TIER 6: TRANSFORMFIT-SPECIFIC DATA

### 19. TransformFit Agent Prompts & Skillsets
**Agents:** All 22
**data_type:** `agent_prompts`
**Status:** 🔄 Ingesting now

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Elite Skillset Prompts (28 agents x 8 platforms) | .docx file | ✅ Ingesting | HIGH |
| Expanded agent skill prompts (90% remaining) | Must be created | AI synthesis | ❌ CRITICAL |
| Platform integration guides | RelevanceAI, n8n, Dify docs | Web | ❌ HIGH |
| Agent communication protocols | Must be designed | AI synthesis | ❌ HIGH |
| Cross-agent workflow definitions | Must be designed | AI synthesis | ❌ MEDIUM |

### 20. TransformFit Product Data
**Agents:** Marcus, Atlas, Coach
**data_type:** `product_specs`
**Status:** ❌ 0 chunks

| Dataset | Source | Pipeline | Priority |
|---------|--------|----------|----------|
| Feature specification documents | Must be created per feature | Manual | ❌ HIGH |
| App wireframes/mockup descriptions | Design files | Manual | ❌ HIGH |
| Subscription tier definitions | Business planning | AI synthesis | ❌ HIGH |
| Onboarding flow specifications | UX design | Manual | ❌ HIGH |
| FitCoin economy design | Gamification design doc | AI synthesis | ❌ MEDIUM |

---

## SUMMARY: DATA GAPS BY SEVERITY

### CRITICAL GAPS (0 chunks, required for core agents)
1. **nutrition** — Sage has zero data to work with
2. **legal_compliance** — Shield has zero data
3. **technical_docs** — Atlas has zero data
4. **security** — Sentinel has zero data
5. **sports_psychology** — Flow has zero data
6. **gamification** — Quest has zero data
7. **community** — Haven has zero data

### HIGH PRIORITY GAPS (some data, need 5-10x more)
8. **sleep_recovery** — Only 9 chunks (Drift needs 100+)
9. **market_research** — Only 12 chunks (Steve needs 100+)
10. **ux_research** — Only 25 chunks (Marcus needs 200+)
11. **growth_marketing** — Only 23 chunks (Aria needs 100+)
12. **exercise_science** — Only 118 chunks (Coach needs 500+)

### ADEQUATE (good base, continue expanding)
13. **behavioral_economics** — 186 chunks ✅
14. **user_research** — 282 chunks ✅
15. **ai_ml_research** — 35 chunks (Nova, adequate for now)

---

## TOTAL DATASETS IDENTIFIED: 150+ individual datasets across 20 categories

## INGESTION PIPELINE MAPPING

| Pipeline | Datasets It Can Serve | Status |
|----------|----------------------|--------|
| Markdown ingestor | Local .md files, manual data | ✅ Ready |
| Books ingestor (AI synthesis) | Textbook knowledge, frameworks | ✅ Ready |
| Web ingestor (Firecrawl) | Any URL, documentation sites | ✅ Ready |
| arXiv ingestor | Research papers | ✅ Ready |
| Reddit ingestor | Community discussions | ✅ Ready |
| App Store ingestor | User reviews, competitor data | ✅ Ready |
| NHANES ingestor | CDC public health data | ✅ Ready |
| DOCX ingestor | Word documents | ✅ Building |
| **USDA FoodData API** | Nutrition database | ❌ Needs building |
| **SEC EDGAR** | Company filings | ❌ Needs building |
| **GitHub repo ingestor** | Code documentation | ❌ Needs building |

---

## EXTERNAL REPOS TO INTEGRATE

| Repo | What It Has | Integration Strategy |
|------|------------|---------------------|
| ios-intelligence-engine | iOS app intelligence | Link/reference |
| oracle-health-ai-enablement | Health AI tooling | Fold into Susan |
| ux-design-scraper | 12-table Supabase with UX data | Direct data sharing |

---

*Last updated: 2026-03-06*
*Generated by Susan Intelligence OS*
