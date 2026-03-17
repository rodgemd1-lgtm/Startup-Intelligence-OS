# Codex Prompt: Oracle Health AI Strategy SharePoint Site

**Purpose:** Hand this prompt to OpenAI Codex (or Claude Code) to build a SharePoint site that teaches the Oracle Health strategy team how to use GenChat, Claude, and ChatGPT with the LEGO piece prompt system.

**Companion:** Use `sharepoint-stitch-design-brief.md` with Stitch, Galileo AI, or Relume to generate visual mockups first, then feed the approved designs into this Codex prompt.

---

## System Prompt for Codex

```
You are building a SharePoint Online site for Oracle Health's AI Strategy team. The site is an internal enablement hub that teaches 6 strategists how to use AI tools — specifically Oracle GenChat (internal), Claude (Anthropic), and ChatGPT (OpenAI) — with a modular prompt system called "LEGO pieces."

## CONTEXT: What This Site Replaces

The team currently has:
- 180 LEGO prompt pieces as slash commands in a 411KB markdown file
- 41 GenChat knowledge base files covering market data, personas, competitive intel, regulatory briefs, and document templates
- An 8-week workshop series (facilitation guides, slide outlines, activities)
- 119 healthcare stakeholder personas across 6 priority packs
- 18 care setting contexts
- 7 domain knowledge packs
- Tier 1-3 prompt architecture (universal protocols → research/analysis → domain context)
- A TypeScript scraper with 6 data source clients (Brave, Exa, Firecrawl, Apify, Jina, DHC/KLAS)
- Strict data confidentiality rules separating what goes into GenChat vs Claude vs external tools

The problem: all of this lives in markdown files, a GitHub repo, and tribal knowledge. The SharePoint site makes it visual, navigable, and usable by strategists who don't live in code.

## ARCHITECTURE: Site Structure

Build a SharePoint Communication Site with Hub Navigation using these pages and sections:

### 1. HOME PAGE — "AI Strategy Command Center"
- Hero banner: "Oracle Health AI Strategy Hub — Your AI Thought Partner System"
- Quick links tile grid (6 tiles):
  1. "Get Started" → Getting Started page
  2. "LEGO Pieces" → Prompt Library
  3. "GenChat" → GenChat Guide
  4. "Claude & ChatGPT" → External AI Guide
  5. "Training" → Workshop Hub
  6. "Data Rules" → Confidentiality Guide
- "What's New" news web part showing latest updates
- "Quick Win of the Week" — highlighted prompt technique with before/after example
- Team metrics dashboard section (placeholder for Power BI embed):
  - Prompts used this month
  - Documents drafted with AI assist
  - Time saved estimate

### 2. GETTING STARTED — "Your First 15 Minutes"
- Step-by-step onboarding flow with numbered sections:
  1. "Understand the 3 Pillars" — Systemize Workflows | Encode Context | Human-in-the-Loop
  2. "Pick Your First LEGO Piece" — link to top 5 starter prompts
  3. "Know Your Data Rules" — quick visual showing GenChat vs Claude boundaries
  4. "Try It Now" — embedded walkthrough with screen captures
- Video embed section: "Watch: Your First GenChat Session" (placeholder for MP4/Stream)
- Downloadable PDF: "AI Strategy Quick Reference Card"

### 3. PROMPT LIBRARY — "LEGO Piece Catalog"
This is the core of the site. Build as a filterable gallery.

- **Filter bar** at top: by Tier (1/2a/2b/2c/3a/3b/3c), by Workflow (Research, Analysis, Deliverable, Strategy), by AI Tool (GenChat, Claude, Any)
- **Card layout** for each LEGO piece showing:
  - Piece name and slash command (e.g., `/competitive-landscape`)
  - Tier badge (color-coded: Tier 1 = blue, Tier 2 = green, Tier 3 = purple)
  - One-line description
  - Recommended AI tool icon (GenChat logo, Claude logo, or "Any")
  - Click to expand: full prompt text, example input, example output, tips
- **Categories** (tabs or sections):
  - Universal Protocols (Tier 1): Anti-hallucination, source verification, red teaming, confidence scoring, semantic diffing, structured output, citation
  - Research & Analysis (Tier 2a): Market sizing, competitive landscape, Porter's 5 Forces, SWOT, pricing analysis, trend analysis
  - Thought Leadership (Tier 2b): Strategic framing, innovation narratives, scenario planning, thesis development
  - Deliverable Assembly (Tier 2c): White papers, executive memos, slide decks, citations, executive summaries
  - Domain Packs (Tier 3a): EHR/Clinical, Revenue Cycle, Population Health, Life Sciences, Payer, International, Regulatory
  - Persona Packs (Tier 3b): C-Suite, Clinical, IT, Financial, Operational, Government
  - Care Settings (Tier 3c): 18 care settings from Academic Medical Centers to Behavioral Health

- **Composition Guide section**: "How to Stack LEGO Pieces"
  - Visual diagram showing: Tier 1 (always loaded) → Tier 2 (pick workflow) → Tier 3 (add context)
  - 3 example compositions with screen captures:
    1. "Competitive Memo" = Anti-Hallucination + Competitive Landscape + EHR Domain + CIO Persona + Exec Memo Template
    2. "Market Sizing Brief" = Source Verification + Market Sizing + Revenue Cycle Domain + CFO Persona + White Paper Template
    3. "Regulatory Impact Analysis" = Confidence Scoring + Trend Analysis + Regulatory Domain + CMIO Persona + Strategic Framing

### 4. GENCHAT GUIDE — "Using Oracle GenChat (Internal AI)"
- **What is GenChat**: Overview section with Oracle branding
- **Screen capture gallery** (image web part, 6-8 annotated screenshots):
  1. GenChat home screen with Ellen identity loaded
  2. How to paste a LEGO piece slash command
  3. The piece menu in action — showing available commands
  4. Example: running `/competitive-landscape` with real output
  5. Example: loading a knowledge base file
  6. Example: multi-piece composition (stacking 3 pieces)
  7. Example: source-tagged output showing [SOURCED] vs [AI-SOURCED] labels
  8. Example: red teaming a draft
- **Video tutorials** section (Stream/video embeds, placeholder):
  - "GenChat 101: Your First Session" (3 min)
  - "Loading Knowledge Bases" (2 min)
  - "Composing Multi-Piece Prompts" (4 min)
  - "Source Verification Workflow" (3 min)
- **Confidentiality callout box** (red/warning styling):
  "GenChat is the ONLY approved platform for Oracle-internal data: financials, customer accounts, pricing, P-01/P-02 protocols, R-05 analysis. Never paste this data into Claude, ChatGPT, or any external tool."
- **Tips & Tricks** accordion:
  - "How to get better outputs from Ellen"
  - "When to use /red-team"
  - "How to handle confidence scoring"
  - "Troubleshooting: when outputs miss the mark"

### 5. EXTERNAL AI GUIDE — "Using Claude & ChatGPT"
- **When to use external AI**: Visual decision tree
  - Public research → Claude or ChatGPT ✅
  - Competitive analysis (public sources) → Claude ✅
  - Training content development → Claude ✅
  - Oracle financials → GenChat ONLY ❌
  - Customer data → GenChat ONLY ❌
- **Screen capture gallery** (6-8 annotated screenshots):
  1. Claude.ai interface — pasting a LEGO piece
  2. Claude — example output from `/market-sizing`
  3. Claude — using Projects feature to store domain packs
  4. ChatGPT — pasting a LEGO piece
  5. ChatGPT — using Custom GPTs for Oracle Health research
  6. Side-by-side: same prompt in GenChat vs Claude showing output differences
  7. Claude Code — running the scraper for market intelligence
- **Model selection guide** (comparison table):

  | Use Case | Best Tool | Why |
  |----------|-----------|-----|
  | Internal data analysis | GenChat | Data stays on Oracle infrastructure |
  | Market research synthesis | Claude | Superior reasoning, longer context |
  | Quick competitive scan | ChatGPT | Fast, good with web search |
  | Slide deck drafting | Claude | Better structured output |
  | Persona simulation | Claude | Nuanced role-play |
  | Data scraping orchestration | Claude Code | Direct API integration |

### 6. WORKSHOP HUB — "8-Week AI Strategy Training"
- **Workshop arc overview** with timeline visual (8 weeks)
- **Per-week pages** (expandable sections or sub-pages):

  | Week | Topic | Key Activities |
  |------|-------|----------------|
  | 1 | AI Foundations & Mental Models | 3 Pillars, TCREI Framework, first LEGO piece |
  | 2 | Research & Analysis Workflows | Market sizing, competitive landscape |
  | 3 | Thought Leadership & Framing | Strategic narratives, scenario planning |
  | 4 | Deliverable Assembly | White papers, memos, slide decks |
  | 5 | Domain Deep Dive: EHR & Clinical | Loading domain packs, persona stacking |
  | 6 | Domain Deep Dive: RCM & Payer | Revenue cycle workflows, payer intelligence |
  | 7 | Advanced Composition | Multi-piece stacking, red teaming, confidence |
  | 8 | Capstone: Build Your Own Workflow | Team presentations, playbook creation |

- Each week section includes:
  - Learning objectives
  - Facilitator notes link
  - Slide deck link (PowerPoint embed or link)
  - Activity instructions
  - Homework/practice prompt
  - Video recording (Stream embed, placeholder)

### 7. KNOWLEDGE BASE EXPLORER — "Domain Intelligence"
- **Interactive catalog** of 41 GenChat KB files organized by category:
  - Market Data (market share, hospital financials, labor stats)
  - Competitive Intelligence (revenue, KLAS rankings, product updates)
  - Clinical Roles & Personas (20+ clinical personas)
  - Care Settings (18 settings with Oracle positioning)
  - Regulatory (CMS, FDA, ONC, TEFCA)
  - Document Templates (slides, memos, white papers)
  - Pricing Intelligence
  - Install Base Analysis (1,757 facilities, DHC data)
- Each KB entry shows:
  - File name and category
  - Last updated date
  - Summary of contents (2-3 sentences)
  - "Load into GenChat" instructions
  - Preview of first 500 characters

### 8. DATA & CONFIDENTIALITY — "What Goes Where"
- **Traffic light system** (visual, color-coded):
  - 🟢 GREEN — Public research, market analysis, training content → Claude, ChatGPT, GenChat
  - 🟡 YELLOW — Oracle product details, non-public roadmap → GenChat only
  - 🔴 RED — Customer data, financials, P-01/P-02, R-05 pricing → GenChat only, never external
- **Protocol reference cards** (expandable):
  - P-01 Matt Cohlmia Protocol — what it covers, when it applies
  - P-02 Seema Verma Protocol — what it covers, when it applies
  - R-05 Pricing Analysis Protocol — what it covers, when it applies
- **Decision flowchart**: "Is this data safe for Claude?" (yes/no tree with examples)
- **Incident response**: "What to do if you accidentally paste internal data into Claude/ChatGPT"

### 9. METRICS & INTELLIGENCE — "How We're Using AI"
- Power BI dashboard embed (placeholder) showing:
  - Prompts executed per week (by person, by tier)
  - Documents drafted with AI assist
  - Time saved estimates
  - Most popular LEGO pieces
  - Research pipeline status (scraper runs, sources ingested)
- **Susan's Foundry Status** section:
  - Current RAG chunk count (6,693+)
  - Domain coverage scores
  - Capability maturity radar chart
  - Research daemon last run / gaps detected
- **Team leaderboard** (gamification, optional):
  - "Most prompts composed this month"
  - "New workflow created" badges

## DESIGN SPECIFICATIONS

### Branding
- Primary color: Oracle Red (#C74634)
- Secondary: Dark charcoal (#312D2A)
- Accent: White (#FFFFFF)
- Font: Oracle Sans (fallback: Segoe UI for SharePoint)
- Tone: Professional, approachable, empowering — not technical or intimidating

### SharePoint Technical Requirements
- SharePoint Online (Microsoft 365)
- Communication Site template
- Hub site navigation connecting all pages
- Responsive design (strategists use laptops + mobile)
- Web parts used: Hero, Quick Links, Image Gallery, News, Embed (video/Power BI), Accordion/FAQ, Document Library, Highlighted Content
- No custom SPFx web parts in Phase 1 — use OOTB components only
- Phase 2 consideration: SPFx web part for interactive LEGO piece composer

### Media Assets Needed
- 15-20 annotated screen captures (GenChat, Claude, ChatGPT interfaces)
- 4-6 tutorial videos (2-5 min each, can be Loom or Stream recordings)
- LEGO piece composition diagram (visual showing tier stacking)
- Data confidentiality traffic light infographic
- Workshop timeline visual (8-week arc)
- Hero banner image (AI + healthcare themed)
- Icons for each tile on home page

### Content Sources (Pull From These Files)
All content lives in the Oracle Health AI Enablement repo:

| Content | Source File |
|---------|------------|
| LEGO piece catalog (180 pieces) | `gen-chat-deploy/oracle-gen-chat-prompt-library.md` |
| System prompt / Ellen identity | `gen-chat-deploy/GLOBAL-SYSTEM-PROMPT.txt` |
| 41 KB files | `gen-chat-deploy/kb-uploads/*.md` |
| Workshop facilitation guides | `workshop/week-01/ through week-08/` |
| Workshop arc overview | `workshop/WORKSHOP_ARC.md` |
| Slide outlines | `workshop/SLIDE_OUTLINES.md` |
| Tier architecture | `CLAUDE.md` (tier loading order section) |
| LEGO piece summary table | `gen-chat-deploy/lego-piece-summary.md` |
| Deployment guides | `gen-chat-deploy/COWORK_*.md` |
| Confidentiality rules | `KNOWLEDGE_BASE_LOAD_PROTOCOL.md` |
| Persona packs | `tier-3b-persona-packs/` (6 directories) |
| Domain packs | `tier-3a-domain-packs/` (7 directories) |
| Care settings | `tier-3c-care-settings/` (18 files) |
| Data source pipeline | `CLAUDE_PROMPT_MASTER.md` (5-source section) |
| DHC install base analysis | `data-exports/dhc/` |
| Research library | `research-library/` |

### Susan's Foundry Integration Points
The Startup Intelligence OS provides these capabilities that feed the SharePoint site:

| Foundry Capability | How It Feeds SharePoint |
|-------------------|------------------------|
| `search_knowledge` MCP tool | Enables searching 6,693+ RAG chunks for content to surface on site pages |
| `oracle_health_intelligence` domain pack | 4-layer architecture (market, clinical, regulatory, narrative) structures the Knowledge Base Explorer |
| `capability-gap-map` skill | Identifies what training content is missing — feeds Workshop Hub priorities |
| `research-packet` skill | Generates deep research that becomes KB uploads and site content |
| `/scrape` command | Harvests fresh market data, competitive intel, regulatory updates for site refresh |
| `/research-daemon` | Autonomous gap detection ensures the site stays current |
| `training-factory` skill | Produces workshop materials, facilitator packets, activity designs |
| `ellen-oracle-enablement` skill | Produces GenChat workflow maps, prompt references, training examples |
| `behavioral-economics` skill | Designs adoption mechanics — gamification, habit loops for the Metrics page |
| 27 Susan agents | Specialized agents (oracle-health-marketing-lead, oracle-health-product-marketing, etc.) produce domain-specific content |
| Company registry | Oracle Health AI Enablement entry defines challenges, tech stack, competitors |
| 580 binary files on disk | Word docs, PowerPoints, PDFs available for conversion to site content |

## IMPLEMENTATION PHASES

### Phase 1: Foundation (Week 1-2)
- Create Communication Site with hub navigation
- Build Home, Getting Started, and Data & Confidentiality pages
- Set up page templates and branding
- Create image placeholders for screen captures

### Phase 2: Core Content (Week 3-4)
- Build Prompt Library with filterable gallery
- Build GenChat Guide with screen capture gallery
- Build External AI Guide with decision tree
- Create the LEGO piece composition diagram

### Phase 3: Training & Knowledge (Week 5-6)
- Build Workshop Hub with 8-week arc
- Build Knowledge Base Explorer with 41 KB entries
- Create video embed placeholders
- Link to existing PowerPoint materials

### Phase 4: Intelligence & Polish (Week 7-8)
- Build Metrics & Intelligence page
- Set up Power BI embed placeholders
- Add Susan's Foundry Status section
- Final branding pass, accessibility check, mobile testing
- User acceptance testing with 2-3 strategists

## SUCCESS CRITERIA
- All 9 pages built and navigable
- LEGO piece catalog shows all 180 pieces with filtering
- Screen capture placeholders in place for 15-20 images
- Video embed placeholders for 4-6 tutorials
- Confidentiality rules clearly displayed with traffic light system
- Mobile-responsive on all pages
- No custom SPFx code required (OOTB only)
- Site loads in < 3 seconds on corporate network
```

---

## Usage

1. **Design first**: Hand `sharepoint-stitch-design-brief.md` to Stitch/Galileo AI to generate visual mockups
2. **Approve mockups**: Review with stakeholders, iterate on layout
3. **Build with Codex**: Feed this prompt + approved mockups to Codex or Claude Code
4. **Content population**: Use the source file table above to pull real content from the Oracle Health AI Enablement repo
5. **Screen captures**: Record GenChat, Claude, and ChatGPT sessions and annotate with callout boxes
6. **Video recording**: Use Loom or Microsoft Stream to record the 4-6 tutorial walkthroughs
