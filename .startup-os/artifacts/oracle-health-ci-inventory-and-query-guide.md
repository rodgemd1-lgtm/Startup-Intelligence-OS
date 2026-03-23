# Oracle Health Competitive Intelligence — Complete Inventory & Query Guide

**Generated**: 2026-03-22  
**Scope**: All Oracle Health CI data across Susan's knowledge base, data directories, and ingestion infrastructure  
**Audience**: Mike, Matt Cohlmia, Seema Verma, product and strategy teams  

---

## PART 1: COMPETITIVE INTELLIGENCE INVENTORY

### 1. Relational Data Layer (Supabase Tables)

**Location**: `susan-team-architect/backend/data/company_registry.yaml`  
**Activation**: `susan-team-architect/backend/scripts/bootstrap_oracle_health_db.py`  
**Company ID**: `oracle-health-ai-enablement`  

**What It Contains**:
- Oracle Health company metadata (identity, foundry config, team structure)
- Company relationships (parent/subsidiary, partnerships, competitive positioning)
- Leadership and stakeholder records
- Strategic positioning anchors (Seema Verma's "built for Agentic AI era" narrative)

**Utility for Battlecards**: **MEDIUM**  
- Provides structural foundation for Oracle Health as the "our company" anchor
- Supports internal company context but not competitive positioning details
- Use case: Verify company identity, leadership chain, strategic positioning statements

**Query Pattern**: Direct relational table read via Supabase client (not RAG-based)

---

### 2. Signal Triage & Scoring Methodology (SOP-02)

**Location**: `docs/sops/SOP-02-signal-triage-urgency-classification.md` (401 lines)  
**Created**: 2026-03-22  
**Version**: 1.0 APPROVED  

**What It Contains**:
- **Three-layer signal triage architecture**: Priority Engine (general signals), Birch Scorer (competitive signals), Nervous System (real-time email alerts)
- **Priority Engine scoring formula**: urgency × importance × recency_factor × source_weight × vip_boost × imminence_boost
- **Priority tiers**: P0 (≥0.75, interrupt), P1 (≥0.50, morning brief), P2 (≥0.25, daily summary), P3 (<0.25, background log)
- **VIP detection**: Matt Cohlmia (VP), Seema Verma (SVP), Bharat Sutariya (SVP Clinical), Elizabeth Krulish (EA)
- **Birch Scorer three-axis formula**: (relevance×0.40) + (actionability×0.35) + (urgency×0.25), range 0–100
- **Competitive signal tiers**: Tier 1 (≥80, route to competitive-response), Tier 2 (≥50, monitoring), Tier 3 (<50, archive)
- **"So What" framework**: Every signal must answer What Happened / Why It Matters / What We Should Do

**Utility for Battlecards**: **VERY HIGH**  
- Defines how competitive signals are classified and routed
- Birch scoring directly applies to competitive battlecard triggers (85% Epic adoption = high relevance + actionability → Tier 1)
- "So What" framework ensures battlecard messages are actionable and relevant
- Use case: Understand signal maturity, know when to promote a competitive insight to battlecard status, structure battlecard narrative

**Reference Implementation**: `Birch Scorer` (birch/scorer.py) — applies relevance/actionability/urgency scoring to competitive signals

---

### 3. Win-Loss Analysis & Loss Driver Evidence (SOP-09)

**Location**: `docs/sops/SOP-09-win-loss-analysis.md` (517 lines)  
**Created**: 2026-03-22  
**Version**: 1.0 APPROVED  

**What It Contains**:
- **Five loss driver categories with statistical weight**:
  - IMPL-RISK: 23.8% (implementation risk, timeline delays, support concerns)
  - CHAMP-FAIL: 21.3% (champion departure, internal advocacy loss, stakeholder change)
  - PRICE: 18.1% (pricing, cost justification, ROI concerns)
  - TTV: 16.9% (time-to-value, go-live delays, expectations gap)
  - COMP-POS: 11.4% (competitive positioning, feature comparison, incumbent strength)
- **Healthcare-specific buying committee**: CMO, CMIO, CIO, CFO, VP Revenue Cycle, Procurement
- **Loss interview protocol**: 6-question structure, stakeholder mapping, champion mapping
- **Competitor loss messaging**: Frame Oracle Health's differentiators to address top loss drivers

**Utility for Battlecards**: **VERY HIGH**  
- Battlecard messaging should address loss drivers (especially COMP-POS 11.4% + TTV 16.9%)
- Provides evidence-based weighting for what matters in head-to-head sales conversations
- Use case: Shape battlecard talking points around actual buying committee pain points, structure Epic/Waystar/Microsoft positioning to address IMPL-RISK and CHAMP-FAIL narratives

**Evidence Base**: Healthcare Deals Outlook 2026 (Black Book, consulting firms), Oracle Health win-loss database

---

### 4. Competitive Signals — Scout Report (March 18 Brief)

**Location**: `.startup-os/briefs/scout-signals-2026-03-18.md` (109 lines)  
**Date**: 2026-03-18  
**Classification**: CLEAR  

**What It Contains**:
- **P0 Signals (Respond Today)**:
  - Epic Agent Factory: no-code AI agent builder, 85% customer adoption, three named agents (Art, Penny, Emmie), 69% vs 46% lung cancer detection (Christ Hospital), 42% prior auth reduction (Summit Health)
  - athenahealth AI-native EHR: agentic patient communication live, ambient documentation (athenaAmbient) entering testing, athenaConnect for real-time data exchange

- **P1 Signals (Respond This Week)**:
  - Microsoft DAX Copilot: 600+ health systems, now embedded in MEDITECH Expanse (20+ provider groups), HCA deployment
  - Waystar AltitudeAI: agentic RCM at J.P. Morgan Healthcare Conference, autonomous revenue cycle positioning

- **P2 Signals (Monitor)**:
  - Oracle Health executive departures: Bloomberg visibility (EVP Sanga Viswanathan, SVP Suhas Uliyar) — now external and visible to customers/press
  - Healthcare IT M&A: 43% of 2025 deals involve distressed parties (record high), AI workflow automation as primary acquisition target
  - AI fitness coaching: Whoop Coach, Zing Coach, Luna Band, Speediance all claiming "agentic AI coach" positioning

- **Content White Space**:
  - AI agent outcomes data (competitors have quantified, Oracle doesn't)
  - Ambient documentation (DAX Copilot at 600+ systems, Oracle's story incomplete)
  - Validated agentic AI deployment (Oracle could own "responsible AI" narrative)
  - AI-native RCM (both Epic Penny and Waystar claiming autonomous RCM)
  - AI fitness coaching with no-subscription model

**Utility for Battlecards**: **VERY HIGH**  
- Epic and Waystar signals are P0/P1 — immediate battlecard priority
- Content white space directly identifies what battlecards should address (outcomes, validation, responsible deployment)
- Evidence: HIT Consultant, Fierce Healthcare, BusinessWire, MedCity News, Digital Health News
- Use case: Battlecard content roadmap, feature comparison positioning, customer objection handling

**Source**: Oracle Health Morning Intel + ARIA Daily Brief + TrendRadar (no data available)

---

### 5. Executive Brief — Competitive Context (March 18)

**Location**: `.startup-os/briefs/oracle-brief-2026-03-18.md` (66 lines)  
**Date**: 2026-03-18  
**Prepared for**: Matt Cohlmia  

**What It Contains**:
- **Strategic imperatives**:
  1. Counter Epic's Agent Factory narrative with outcomes comparison
  2. Amplify VA expansion story (9 new sites 2026, full deployment 2031)
  3. Monitor Microsoft DAX Copilot footprint (600+ systems, MEDITECH integration)

- **Market intelligence**:
  - Epic Agent Factory: 85% adoption, 69% vs 46% lung cancer detection, 42% prior auth reduction
  - VA EHR expansion: 9 new sites (Michigan, Ohio, Indiana, Alaska), 2031 acceleration
  - Microsoft DAX Copilot: 600+ systems, MEDITECH Expanse integration
  - Nuance/Geisinger breach: $5M settlement, March 18 claim deadline (reputational exposure)

- **Forward-ready blurbs**:
  - Matt Cohlmia: Positioning narrative for general use
  - Bharat Sutariya: Federal health focus (VA momentum story)
  - Seema Verma: Strategy focus (outcomes proof points, acute care launch 2026)

- **Competitive landscape table**: Epic, Microsoft/Nuance, Waystar positioning with recommended responses

**Utility for Battlecards**: **VERY HIGH**  
- Executive-ready messaging structures (forward-ready blurbs) show how to frame competitive advantage at different stakeholder levels
- Emphasizes evidence gaps ("we need outcomes data alongside narrative") — directly informs battlecard content strategy
- Cloud-native architecture + OCI infrastructure + VA scale are Oracle differentiators
- Use case: Message architecture for Epic/Microsoft battlecards, executive communication templates, stakeholder-specific positioning

**Classification**: CLEAR (appropriate for general distribution)

---

### 6. Battlecard Competitive Intelligence Research (March 22)

**Location**: `docs/research/battlecard-competitive-intelligence-research-packet-2026-03-22.md` (414 lines)  
**Date**: 2026-03-22  
**Research Basis**: Crayon (1,200+ respondents), Klue (313 leaders), Forrester, Gartner  

**What It Contains**:
- **Battlecard effectiveness metrics**:
  - 77% of winning reps use battlecards daily or weekly (Crayon)
  - 67% of sales teams with battlecards report improved competitive win rates
  - 63% of teams use FIA (Fact, Impact, Act) content structure

- **Seven battlecard types with FIA framework**:
  1. Competitor Overview (general positioning)
  2. Feature Comparison (side-by-side, with messaging)
  3. Win Scenario (how to win when competitor is in deal)
  4. Loss Scenario (how to recover from competitive loss)
  5. Proof Point (customer evidence, ROI, outcome data)
  6. Pricing (cost justification, value proposition)
  7. Industry Vertical (healthcare-specific, vertical-specific messaging)

- **Klue's Know-Say-Show delivery structure**:
  - Know: Intel summary (what we know about competitor)
  - Say: Messaging (what we tell customers)
  - Show: Proof (demos, evidence, customer references)

- **Healthcare-specific battlecard considerations**:
  - Buying committee roles: CMO, CMIO, CIO, CFO, VP Revenue Cycle, Procurement
  - Loss drivers: IMPL-RISK (23.8%), CHAMP-FAIL (21.3%), COMP-POS (11.4%)
  - Vertical selling points: EHR architecture, compliance/security, vendor stability, long-term roadmap

- **Content audit findings**:
  - Epic: Strong outcomes data, AI agents with names, 85% adoption story
  - Waystar: Emerging agentic RCM positioning, J.P. Morgan visibility
  - Microsoft/DAX: Scale story (600+ systems), MEDITECH integration
  - Oracle gaps: Outcomes data, validated deployment narrative, RCM story

**Utility for Battlecards**: **CRITICAL**  
- This IS the battlecard methodology guide for Oracle Health
- Klue Know-Say-Show structure directly maps to how to build Oracle Health battlecards
- FIA framework is the content structure to use
- Healthcare-specific considerations ensure vertical relevance
- Use case: Template for all battlecards, messaging framework, proof point strategy, vertical customization

**Implementation**: See "Building Oracle Health Battlecards" section below

---

### 7. Signal Corpus — Storage Bucket (Supabase Storage)

**Location**: `Supabase Storage` → `oracle-health-corpus` bucket  
**Prefix**: `oracle-health-ai-enablement/market-intelligence/`  
**Ingestion Script**: `susan-team-architect/backend/scripts/upload_oracle_health_corpus.py` (291 lines)  

**What It Contains**:
- Raw market intelligence documents (PDFs, markdown, text)
- Source: `data/studio_assets/companies/oracle-health-ai-enablement/raw-docs/`
- Files: HIMSS 2026 coverage, competitor press releases, analyst reports, win-loss interviews, customer research, healthcare market research
- Indexing: File manifest tracked for idempotency, retry logic (3 attempts), size verification

**Ingestion Pattern**:
```python
# From upload_oracle_health_corpus.py
COMPANY_ID = "oracle-health-ai-enablement"
BUCKET_NAME = "oracle-health-corpus"
PREFIX = f"{COMPANY_ID}/market-intelligence"

# Upload all files from raw-docs with retry + chunking
upload_one(file_path, bucket_name=BUCKET_NAME, object_key=f"{PREFIX}/{filename}")
```

**Utility for Battlecards**: **HIGH**  
- Raw document corpus is the source for all competitive intelligence
- Files are chunked and embedded into RAG vector store
- Direct access to original source documents for battlecard evidence
- Use case: Retrieve raw evidence (press releases, analyst reports), verify claims, find customer quotes

**How to Access**:
1. Via Storage bucket browser in Supabase console (manual inspection)
2. Via RAG Retriever.search() (vector-based semantic search — see Part 2)

---

### 8. Vector Embeddings — RAG Search Layer (Supabase pgvector)

**Location**: Supabase vector embeddings for `oracle-health-corpus`  
**Embedding Model**: Voyage AI `voyage-3` (1024 dimensions)  
**Retriever Class**: `susan-team-architect/backend/rag_engine/retriever.py`  

**What It Contains**:
- All documents from oracle-health-corpus bucket chunked and embedded
- Semantic search enabled: find competitive intelligence by concept (not just keywords)
- Data types tracked: market_research, competitive_intel, content_strategy, legal_compliance, technical_docs, etc.

**Utility for Battlecards**: **CRITICAL**  
- This is how to programmatically query competitive intelligence
- Vector search finds relevant passages across all stored documents
- Enables automation: build battlecards by querying RAG for Epic/Waystar/Microsoft evidence
- Use case: Populate battlecard sections with relevant evidence, automate white-space detection, support battlecard maintenance

---

## PART 2: QUERYING ORACLE HEALTH COMPETITIVE INTELLIGENCE

### How to Use Retriever.search() for Competitive Intelligence

**Reference Implementation**: `susan-team-architect/backend/scripts/query_fitness_intelligence.py` (40 lines)

**Pattern**:
```python
from susan_core.rag_engine.retriever import Retriever

retriever = Retriever(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY"),
    embedding_model="voyage-3"  # Must be Voyage AI, not OpenAI
)

# Query for competitive intelligence
results = retriever.search(
    query="Epic Agent Factory clinical outcomes and adoption rates",
    company_id="oracle-health-ai-enablement",  # Oracle Health namespace
    data_types=["market_research", "competitive_intel"],
    top_k=5  # Return top 5 most relevant chunks
)

for result in results:
    print(f"Source: {result['source']}")
    print(f"Relevance: {result['similarity_score']:.2f}")
    print(f"Content: {result['content']}\n")
```

### CLI Command Examples

**1. Query for Epic Competitive Intelligence**:
```bash
cd susan-team-architect/backend
source .venv/bin/activate

python scripts/query_fitness_intelligence.py \
  "Epic Agent Factory outcomes data lung cancer detection prior authorization" \
  --company-id oracle-health-ai-enablement \
  --types market_research,competitive_intel \
  --top-k 10
```

**2. Query for Waystar RCM Positioning**:
```bash
python scripts/query_fitness_intelligence.py \
  "Waystar AltitudeAI autonomous revenue cycle agentic RCM" \
  --company-id oracle-health-ai-enablement \
  --types market_research,competitive_intel \
  --top-k 8
```

**3. Query for Microsoft DAX/Ambient Documentation Strategy**:
```bash
python scripts/query_fitness_intelligence.py \
  "Microsoft DAX Copilot ambient documentation MEDITECH integration health systems" \
  --company-id oracle-health-ai-enablement \
  --types market_research,competitive_intel \
  --top-k 10
```

**4. Query for Outcomes Data & Proof Points**:
```bash
python scripts/query_fitness_intelligence.py \
  "clinical outcomes AI detection rates prior authorization reduction" \
  --company-id oracle-health-ai-enablement \
  --types market_research \
  --top-k 15
```

**5. Query for Content White Space Opportunities**:
```bash
python scripts/query_fitness_intelligence.py \
  "validated deployment responsible AI clinical validation framework healthcare" \
  --company-id oracle-health-ai-enablement \
  --types market_research,content_strategy \
  --top-k 8
```

### Creating a Custom Oracle Health Competitive Intelligence Query Script

**Option 1: Adapt query_fitness_intelligence.py**

```bash
cp susan-team-architect/backend/scripts/query_fitness_intelligence.py \
   susan-team-architect/backend/scripts/query_oracle_health_competitive.py
```

Edit the script:
```python
#!/usr/bin/env python3
"""Query Oracle Health competitive intelligence from RAG."""

import os
import sys
from susan_core.rag_engine.retriever import Retriever

def query_oracle_health_competitive(query: str, top_k: int = 10):
    """Query Oracle Health competitive intelligence corpus."""
    
    retriever = Retriever(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
        embedding_model="voyage-3"
    )
    
    results = retriever.search(
        query=query,
        company_id="oracle-health-ai-enablement",
        data_types=["market_research", "competitive_intel", "content_strategy"],
        top_k=top_k
    )
    
    print(f"\n📊 Oracle Health Competitive Intelligence Query Results\n")
    print(f"Query: {query}\n")
    print(f"Results: {len(results)} chunks found\n")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] Source: {result['source']}")
        print(f"    Relevance Score: {result['similarity_score']:.3f}")
        print(f"    Data Type: {result.get('data_type', 'unknown')}")
        print(f"    Content:\n    {result['content'][:500]}...")
        print("-" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: query_oracle_health_competitive.py \"<query>\" [--top-k N]")
        sys.exit(1)
    
    query = sys.argv[1]
    top_k = 10
    
    if "--top-k" in sys.argv:
        top_k = int(sys.argv[sys.argv.index("--top-k") + 1])
    
    query_oracle_health_competitive(query, top_k=top_k)
```

Run it:
```bash
python scripts/query_oracle_health_competitive.py "Epic Agent Factory adoption rates and outcomes" --top-k 10
```

---

## PART 3: BUILDING ORACLE HEALTH BATTLECARDS

### Using Retriever + Klue Know-Say-Show Framework

**Step 1: Query Competitive Intelligence**
```bash
# Get Intel for Know section
python scripts/query_oracle_health_competitive.py \
  "Epic Agent Factory architecture features adoption rates customer base" \
  --top-k 8
```

**Step 2: Map to Know-Say-Show Sections**

**Know** (What we know about competitor):
- Use RAG results directly
- Summarize competitive positioning, features, outcomes, customer adoption

**Say** (What we tell customers):
- Reference SOP-09 loss drivers → address COMP-POS, TTV, IMPL-RISK
- Use executive brief forward-ready blurbs as messaging templates
- Map Oracle differentiators to buying committee roles (CMO, CMIO, CIO, CFO, VP RCM, Procurement)

**Show** (Proof points):
- Query for outcomes data: "clinical outcomes detection rates prior authorization reduction"
- Query for customer evidence: "health system customer case studies implementations"
- Reference VA expansion story (Bharat Sutariya narrative)

**Step 3: Apply FIA Content Structure**
- **Fact**: What we know (from RAG Know section)
- **Impact**: Why it matters (from SOP-09 loss drivers, buying committee pain points)
- **Act**: What we do/say differently (Oracle's differentiators: cloud-native, OCI, VA scale, responsible AI)

---

## PART 4: ORACLE HEALTH COMPETITIVE DATA MATURITY ASSESSMENT

| Data Source | Layer | Completeness | Quality | Actionability | Best Use Case |
|---|---|---|---|---|---|
| SOP-02 (Signal Triage) | Methodology | 100% | High | Critical | Determine when to elevate signal to battlecard |
| SOP-09 (Win-Loss) | Evidence Base | 100% | High | Critical | Structure battlecard messaging around loss drivers |
| Scout Signals Brief | Current State | 100% | High | Critical | Content roadmap, P0/P1 competitors, white space |
| Executive Brief | Strategy | 100% | High | High | Executive messaging, stakeholder-specific positioning |
| Battlecard Research | Framework | 100% | High | Critical | Battlecard template, FIA structure, healthcare vertical considerations |
| oracle-health-corpus (Storage) | Raw Docs | 95% | Medium | High | Source evidence for battlecard claims |
| RAG Vector Embeddings | Semantic Search | 90% | High | Critical | Automated battlecard population, evidence retrieval |
| Company Registry | Relational | 90% | High | Medium | Oracle Health identity, leadership context |

---

## PART 5: IMMEDIATE NEXT STEPS FOR ORACLE HEALTH BATTLECARDS

### 1. Priority Battlecards (P0/P1 Competitors)

| Competitor | Type | Priority | Evidence Source | Owner |
|---|---|---|---|---|
| **Epic** | Competitor Overview + Feature Comparison | P0 | Scout Signals, Executive Brief, RAG queries | Matt / Seema |
| **Epic Agent Factory** | Proof Point + Win Scenario | P0 | RAG outcomes query, HIMSS 2026 coverage, customer research | Product / Sales |
| **Waystar** | Competitor Overview + Win Scenario | P1 | Scout Signals, RAG RCM query | Product / Sales |
| **Microsoft DAX Copilot** | Competitor Overview + Loss Scenario | P1 | Scout Signals, RAG ambient documentation query | Product |

### 2. Content White Space Battlecards (Oracle Differentiators)

| Topic | Battlecard Type | Evidence Source | Owner |
|---|---|---|---|
| AI Outcomes Data | Proof Point | RAG outcomes query + SOP-09 loss drivers | Product / Marketing |
| Validated AI Deployment | Industry Vertical | RAG validation framework query + STAT News coverage | Strategy / Product |
| RCM-EHR Integration | Feature Comparison | RAG RCM query + Oracle Health platform docs | Product / Sales |
| Federal AI Scale | Industry Vertical | VA expansion story (Executive Brief) + OCI infrastructure | Strategy / Bharat |

### 3. Battlecard Maintenance Automation

Create a recurring task:
```bash
# Weekly competitive intelligence refresh
0 9 * * 1 python scripts/query_oracle_health_competitive.py \
  "competitor moves announcements product launches new features" \
  --top-k 15 > /tmp/oracle-ci-weekly-digest.txt

# Send digest to Matt + Seema
mail -s "Weekly Oracle Health CI Digest" \
  matt.cohlmia@oracle.com,seema.verma@oracle.com < /tmp/oracle-ci-weekly-digest.txt
```

---

## APPENDIX: FILE LOCATIONS REFERENCE

| Data Source | File Path | Purpose |
|---|---|---|
| Signal Triage | `docs/sops/SOP-02-signal-triage-urgency-classification.md` | Competitive signal classification methodology |
| Win-Loss Analysis | `docs/sops/SOP-09-win-loss-analysis.md` | Evidence-based competitive loss drivers |
| Scout Signals | `.startup-os/briefs/scout-signals-2026-03-18.md` | P0/P1/P2 competitive signals and white space |
| Executive Brief | `.startup-os/briefs/oracle-brief-2026-03-18.md` | Executive-level competitive context |
| Battlecard Research | `docs/research/battlecard-competitive-intelligence-research-packet-2026-03-22.md` | Methodology + healthcare vertical |
| Company Registry | `susan-team-architect/backend/data/company_registry.yaml` | Oracle Health company metadata |
| Corpus Upload Script | `susan-team-architect/backend/scripts/upload_oracle_health_corpus.py` | How CI documents are ingested |
| RAG Query Reference | `susan-team-architect/backend/scripts/query_fitness_intelligence.py` | Retriever.search() pattern |
| RAG Engine | `susan-team-architect/backend/rag_engine/retriever.py` | Supabase pgvector + Voyage AI search |
| Storage Bucket | `oracle-health-corpus` (Supabase Storage) | Raw competitive intelligence documents |

---

**Generated by Jake on behalf of Mike Rodgers**  
**Classification**: CLEAR (appropriate for general Oracle Health distribution)  
**Next Update**: 2026-03-29 (weekly refresh)

