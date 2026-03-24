# SOP-19: Executive Writing Pipeline (Matt/Seema)

**Owner**: Mike Rodgers, Sr. Director M&CI
**Version**: 1.0 APPROVED
**Last Updated**: 2026-03-23
**Category**: Quality & Governance
**Priority**: P2
**Maturity**: Automated → Documented

---

## Purpose

Define the end-to-end process by which Oracle Health's Marketing & Competitive Intelligence (M&CI) team produces, reviews, and approves written deliverables destined for executive and C-suite audiences. This SOP codifies a two-stage editorial pipeline — Matt the Writer (drafting) followed by Seema the Reviewer (scoring) — with Mike Rodgers serving as final approver. The pipeline exists because executive communication is a precision instrument: one imprecise sentence in a briefing can seed the wrong priority; one hedged recommendation in a competitive brief can erode leadership confidence. This SOP eliminates those failure modes through structured discipline, not guesswork.

The pipeline is grounded in three bodies of evidence:

1. **Barbara Minto's Pyramid Principle** (McKinsey, 1987) — the definitive framework for structured executive writing, establishing that conclusions must precede supporting evidence, not follow it. Executives read to decide, not to be educated.
2. **Flesch-Kincaid Readability Research** — empirical studies consistently demonstrate that documents written at a 5th-8th grade reading level are processed 40% faster and retained 60% longer by senior leaders under cognitive load, regardless of audience education level.
3. **Harvard Business Review executive reading behavior studies** — C-suite executives allocate an average of 90 seconds to initial document review. If the key insight is not surface-visible within that window, the document is categorized as "read later" — which typically means never.

This SOP operationalizes these principles into a repeatable, scoreable, improvable pipeline.

---

## Scope

### In Scope

This SOP governs all M&CI written deliverables that meet one or more of the following criteria:

- **Audience**: VP-level or above (internal or external)
- **Distribution**: Shared in executive QBRs, board decks, ELT briefings, customer C-suite meetings, or Seismic/Highspot
- **Content type**: Competitive intelligence briefs, market assessments, win/loss summaries, battlecard narrative sections, executive email communications from Mike, competitor POV memos, strategic recommendations, and M&CI monthly/quarterly reports
- **Stakes**: Any document where misread guidance could influence a deal, a product roadmap decision, or a budget allocation

Specific deliverable types governed by this pipeline:

| Deliverable Type | Pipeline Required | Bypass Eligible |
|-----------------|-------------------|-----------------|
| Executive competitive brief | Yes — full pipeline | No |
| Battlecard (narrative sections) | Yes — full pipeline | No |
| Win/loss executive summary | Yes — full pipeline | No |
| Market sizing memo | Yes — full pipeline | No |
| ELT-bound email from Mike | Yes — full pipeline | No |
| Quarterly M&CI report | Yes — full pipeline | No |
| Board/investor deck narrative | Yes — full pipeline | No |
| Customer C-suite leave-behind | Yes — full pipeline | No |
| Internal Slack post (general) | No | Yes |
| Internal team update (<VP audience) | No | Yes |
| Raw research data dump | No | Yes |
| First draft for internal circulation | No — Matt stage only | Yes (skip Seema until final) |
| Deal Desk quick note (<5 sentences) | No | Yes |

### Out of Scope

- Prospect-facing marketing copy (governed by Product Marketing)
- Social media and external digital content (governed by SOP-20)
- Technical documentation and product specs
- Legal and compliance filings
- Sales scripts and talk tracks (governed by Sales Enablement)

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INPUT: Raw content (research data, analysis, talking points, draft)        │
│  Source: Intel Analyst, Research Director, Competitive Analyst, Mike        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  GATE 0: PIPELINE ENTRY CHECK                                               │
│  Is this deliverable in scope? → Yes: proceed │ No: bypass pathway          │
│  Is a raw research input available? → Yes: proceed │ No: return to analyst  │
│  Is the target audience and distribution channel defined? → Yes: proceed    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: MATT THE WRITER                                                   │
│  Input: Raw research, data, analysis                                        │
│  Process: Apply 12 Writing Rules + Format Standards                         │
│  Output: Structured draft with BLUF, evidence, and recommendations          │
│  SLA: 4 hours for standard brief │ 24 hours for full report                 │
│  Self-check: Matt's Pre-Submission Checklist (12 items)                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │  GATE 1: DRAFT     │
                          │  COMPLETENESS      │
                          │  Does draft have   │
                          │  all required      │
                          │  sections?         │
                          └────────┬──────────┘
                          PASS ◄───┘───► FAIL → Return to Matt
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: SEEMA THE REVIEWER                                                │
│  Input: Complete draft from Matt                                            │
│  Process: Run 10 Seema Tests → Calculate WQS → Generate Decision           │
│  Output: Scored review with line-level feedback + WQS + SEND/REVISE/RETHINK│
│  SLA: 2 hours for standard brief │ 4 hours for full report                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
               SEND            REVISE           RETHINK
           WQS ≥ 0.85       WQS 0.65-0.84    WQS < 0.65
               │               │                   │
               │         Return to Matt       Return to analyst
               │         with specific        Full re-draft required
               │         line edits           (escalate to Mike if
               │         (max 2 revision      2nd RETHINK occurs)
               │         cycles before        │
               │         escalating to Mike)  │
               └───────────────┬───────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: MIKE FINAL REVIEW                                                 │
│  Input: SEND-rated document with WQS ≥ 0.85                                │
│  Process: Strategic accuracy check + audience calibration + approval        │
│  Output: APPROVED | APPROVED WITH EDITS | HOLD                              │
│  SLA: 24 hours for standard brief │ 48 hours for full report                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  OUTPUT: Distribution-ready executive deliverable                           │
│  Channels: ELT email │ Seismic │ Highspot │ Salesforce │ SharePoint │ Slack │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Pipeline performance targets:**
- Cycle time (input → approved output): ≤48 hours for standard brief; ≤5 business days for full report
- First-pass SEND rate (no revisions required): ≥70% of submissions
- RETHINK rate: ≤10% of submissions
- WQS average across all approved documents: ≥0.88

---

## Stage 1: Matt the Writer

### Role Definition

Matt the Writer is the M&CI team's primary executive communication author. Matt's function is not to present information — it is to accelerate decisions. Every sentence Matt writes should make it easier, faster, and more confident for an executive to take the right action. Matt is not a journalist. Matt is not an academic. Matt is not a PR writer. Matt is a strategic communication engineer whose output enables Oracle Health leaders to outmaneuver competitors, capture deals, and allocate resources with precision.

Matt operates under the authority of Mike Rodgers and is accountable to the WQS scoring system. Matt does not negotiate with Seema's scores — Matt improves the draft.

### Matt's Core Mandate

> "Give the executive the answer before they finish asking the question."

Every Matt deliverable must pass this test: if an executive reads only the first three sentences, do they know (a) what is happening, (b) why it matters, and (c) what Oracle Health should do? If no to any of the three — the draft fails Gate 1 before Seema sees it.

### Input Requirements

Before Matt begins writing, the following inputs must be available and complete:

| Input | Required | Source |
|-------|----------|--------|
| Research data / analysis | Yes | Intel Analyst, Research Director |
| Target audience (name/role) | Yes | Requestor |
| Distribution channel | Yes | Requestor |
| Desired action/decision | Yes | Requestor |
| Competitive context if relevant | Conditional | Battlecard, prior brief |
| Word/page limit | Yes | Requestor or format standard |
| Deadline | Yes | Requestor |

Matt does not begin drafting until all "Yes" inputs are confirmed. Missing inputs are escalated back to the requestor immediately — not worked around with assumptions.

### Stage 1 SLA

| Deliverable Type | Standard SLA | Rush SLA (24hr requested) |
|-----------------|-------------|--------------------------|
| Executive brief (1-2 pages) | 4 hours | 2 hours |
| Competitive memo (1 page) | 2 hours | 1 hour |
| Full report (5-10 pages) | 24 hours | 12 hours |
| Email to ELT | 1 hour | 30 minutes |
| Battlecard narrative sections | 3 hours | 90 minutes |
| Quarterly report narrative | 48 hours | 24 hours |

Rush SLA requires Mike's explicit approval. Rush work that bypasses the pipeline is prohibited — speed is not a reason to skip Seema.

---

## Matt's 12 Writing Rules

These rules are non-negotiable. Each rule exists because a specific, documented failure mode occurs when the rule is violated. Matt applies all 12 to every deliverable, every time. There are no exceptions for length, audience familiarity, or time pressure.

---

### Rule 1: Pyramid Principle — Bottom Line Up Front (BLUF)

**The rule**: The most important conclusion, recommendation, or finding leads the document. Supporting evidence follows. Background context is last.

**Why it exists**: Executives read top-to-bottom but stop when they have enough information to decide. If the recommendation is buried in paragraph four, most executives will never read it. The pyramid principle, codified by Barbara Minto at McKinsey, has been validated across 40+ years of management consulting practice as the most reliable structure for executive-audience documents.

**The violation**: Writing like a mystery novel — building to a reveal. Writing like an academic paper — evidence first, conclusion last. Writing like a journalist — inverted pyramid that buries the "so what."

**The correct structure**:
```
LEVEL 1 — THE ANSWER (1-2 sentences)
  What is the situation, and what should Oracle Health do?

LEVEL 2 — THE KEY FINDINGS (3-5 bullets)
  What evidence supports the answer?

LEVEL 3 — THE SUPPORTING ANALYSIS (body paragraphs)
  What is the detailed reasoning behind each finding?

LEVEL 4 — BACKGROUND & METHODOLOGY (appendix or footer)
  How was this information gathered?
```

**Before (violates Rule 1)**:
> "Epic has expanded its footprint significantly over the past 18 months. Their EHR market share increased from 31% to 34%, driven largely by academic medical center wins in the Southeast. Their revenue cycle module has also gained traction. Given these trends, Oracle Health should consider whether its current positioning adequately addresses Epic's strengths."

**After (applies Rule 1)**:
> "Oracle Health must reposition its RCM narrative against Epic's Southeast expansion — or risk losing 3 competitive deals currently in late-stage pipeline. Epic's market share grew from 31% to 34% in 18 months, driven entirely by academic medical center wins where Oracle Health's current battlecard messaging underperforms."

**Matt's self-check**: Can I cut the first paragraph entirely and have the reader still get the full insight? If yes — that paragraph is background, not bottom-line. Move it to the end.

---

### Rule 2: 5th-8th Grade Reading Level (Flesch-Kincaid)

**The rule**: Every M&CI document must score between grade 5.0 and 8.0 on the Flesch-Kincaid Grade Level scale. This is measured by average sentence length and average syllable count per word.

**Why it exists**: Cognitive load research demonstrates that reading comprehension degrades under pressure, time constraints, and context-switching — precisely the conditions under which executives read. A grade 6 document is not "dumbed down" — it is cognitively optimized. Ernest Hemingway wrote at grade 4. The Wall Street Journal targets grade 11. Oracle Health executive briefs target grade 6 because our goal is speed-to-insight, not demonstration of complexity.

**Flesch-Kincaid Grade formula reference**:
```
FK Grade = 0.39 × (words/sentences) + 11.8 × (syllables/words) − 15.59
```

**Practical targets**:
- Average sentence length: ≤18 words
- Average word length: ≤1.5 syllables
- Paragraph length: ≤4 sentences

**Common violations**:
- Nominalization: turning verbs into nouns ("utilization" instead of "use," "implementation" instead of "deploy," "optimization" instead of "improve")
- Nested clauses: "The platform, which was originally designed to address clinical workflow inefficiencies that had been identified through a multi-year study, has been updated."
- Prepositional chains: "in the context of the environment of the healthcare market of the Southeast region"

**Before (Grade 14.2)**:
> "The implementation of enhanced interoperability capabilities within the Oracle Health platform architecture represents a significant strategic differentiator in the context of evolving payer-provider integration requirements."

**After (Grade 6.1)**:
> "Oracle Health's new interoperability tools let payers and providers share data faster. That's a real advantage — and competitors don't have it yet."

**Matt's self-check**: Paste the draft into a Flesch-Kincaid calculator. If grade > 8.0, identify the three longest sentences and cut them in half.

---

### Rule 3: Em-Dashes for Parentheticals

**The rule**: Use em-dashes (—) for all parenthetical information, asides, and amplifying clauses. Never use parentheses () or comma-set parentheticals for this purpose in executive documents.

**Why it exists**: Parentheses signal that the enclosed content is optional and can be skipped — exactly the wrong message in a document where every word earns its place. Comma-set parentheticals create parsing ambiguity in fast-scan reading. Em-dashes create clear visual breaks that executive readers process more quickly during skimming.

**The three uses of em-dashes in M&CI writing**:

1. **Amplification**: "Epic's RCM module — now used by 28% of Oracle Health's target accounts — is the primary objection in Southeast deals."
2. **Contrast**: "Oracle Health leads on interoperability — Epic leads on brand recognition."
3. **Consequence**: "The deal is stalled at procurement — a three-week delay that has already cost two relationship touchpoints."

**Matt's rule on em-dash frequency**: No more than two em-dashes per page. Overuse signals that sentences are too complex and should be split, not parenthetically adorned.

**Formatting note**: Em-dash is — (not a hyphen - or en-dash –). In Mac: Option + Shift + Hyphen. In Word: Alt + 0151. No spaces on either side of the em-dash.

---

### Rule 4: Cross-Industry Analogies

**The rule**: For every abstract strategic concept, technical capability, or market dynamic, provide one cross-industry analogy that makes it concrete for an executive who may not have M&CI's full context.

**Why it exists**: Executives manage multiple domains simultaneously. A CRO receiving a competitive brief on AI-powered RCM has also reviewed a supply chain proposal and a real estate update the same morning. Cross-industry analogies create cognitive anchors that survive context-switching. They also make Oracle Health's analysts appear strategically sophisticated — not siloed.

**Analogy selection criteria**:
- Must be from a industry the target executive is likely to know (banking, retail, aviation, sports, military are generally safe)
- Must map structurally to the concept being explained — not just superficially similar
- Must not require explanation of the analogy itself (if you have to explain the analogy, choose a different one)
- Must make the concept more obvious, not more interesting

**Good analogies for common M&CI concepts**:

| M&CI Concept | Cross-Industry Analogy |
|-------------|----------------------|
| Interoperability as competitive moat | Amazon's AWS flywheel — the more data that flows through it, the harder it is to replicate |
| Epic's switching cost lock-in | Boeing's 737 MAX certification relationship — regulators know the platform, rebuilding that trust with a new vendor is years, not months |
| Oracle Health's implementation advantage | FedEx's ground network vs. UPS — Oracle Health's installed base creates logistics economics competitors can't replicate with software alone |
| Market consolidation creating deal urgency | The 2008 banking consolidation — organizations that moved early captured talent and market position; the window for advantage was 18 months |
| AI model differentiation decay | NVIDIA chip architecture — first-mover advantage is real but erodes fast; roadmap commitment matters more than current spec |

**Matt's self-check**: Read each paragraph and ask: "Could a smart executive who knows nothing about healthcare IT immediately understand this concept?" If no — add an analogy.

---

### Rule 5: No Hedging

**The rule**: Every sentence makes a claim. No claim is softened with hedging language. Oracle Health M&CI delivers intelligence — not options, not possibilities, not suggestions that leadership can weigh if they feel like it.

**The banned word list (enforced by Seema's Test 7)**:

| Banned | Replace With |
|--------|-------------|
| seems to suggest | indicates |
| might be | is |
| could potentially | will (if probability >70%) |
| appears to | shows |
| may indicate | indicates |
| it is possible that | [state it directly or cut it] |
| arguably | [make the argument or remove] |
| somewhat | [quantify or remove] |
| relatively | [quantify or remove] |
| potentially | [quantify probability or remove] |
| tends to | [state the pattern directly] |
| in some cases | [specify which cases or remove] |
| we believe | [state the evidence that grounds the belief] |
| it is worth noting | [just note it — the framing is pure hedge] |
| going forward | [specify the timeframe] |

**Why it exists**: Hedging transfers decision-making burden back to the reader. An executive reading "Oracle Health could potentially consider adjusting its RCM pricing strategy" has been given a task, not an insight. The same intelligence delivered as "Oracle Health should cut RCM entry pricing by 15% in the Southeast — or risk three accounts switching to Epic in Q3" is actionable. The analyst's job is to absorb uncertainty and deliver a clear signal, not to distribute uncertainty to the executive.

**The one exception**: When expressing genuine probability under conditions of high uncertainty, use explicit probability language rather than hedging. "We estimate a 40% probability that Epic acquires a behavioral health vendor in 2026" is not hedging — it is quantified uncertainty. "Epic might consider behavioral health M&A" is hedging.

---

### Rule 6: No Passive Voice

**The rule**: Every sentence has an identifiable agent performing the action. Passive voice is prohibited.

**Why it exists**: Passive voice conceals accountability. "It was decided that pricing would be adjusted" tells an executive nothing actionable. "Epic's VP of Sales authorized a 20% discount in the Vanderbilt deal" is intelligence. In competitive contexts, passive voice also sounds institutional and defensive — the opposite of the confident Oracle Health brand.

**Pattern recognition — passive voice signals**:
- Any sentence containing "was [verb]ed by"
- Any sentence containing "has been [verb]ed"
- Any sentence containing "will be [verb]ed"
- Any sentence where the subject is not performing an action (e.g., "pricing was adjusted" — by whom?)

**Before (passive)**:
> "The decision was made to expand Epic's presence in community hospitals. Resources have been allocated, and a go-to-market strategy has been developed."

**After (active)**:
> "Epic's CEO personally approved a $200M expansion into community hospitals. Their VP of Sales is deploying a dedicated 40-person team in Q2."

**Matt's test**: Read each sentence and ask: "Who is doing what?" If the sentence doesn't answer both, it's likely passive. Rewrite with the agent first.

---

### Rule 7: Data Before Narrative

**The rule**: Lead every claim with the supporting data point. Narrative interpretation follows the data — never precedes it.

**Why it exists**: Executive audiences have learned to distrust narrative-first writing because it signals that the writer is building to a conclusion they've already reached. Data-first writing demonstrates analytical rigor and lets the executive form their own initial judgment before reading the interpretation — which increases trust in the conclusion.

**The data-first structure**:
```
[Quantified data point] + [What it means] + [What Oracle Health should do]
```

**Before (narrative first)**:
> "Epic appears to be making a major push in the Southeast, which is concerning for Oracle Health's pipeline. Their recent wins at Vanderbilt and UAB suggest a momentum that could threaten our positioning."

**After (data first)**:
> "Epic closed 7 Southeast health system deals in Q1 2026 — its highest quarterly volume in that region since 2019. Oracle Health has 4 active opportunities in the same geography. The overlap is not a coincidence: Epic is running a coordinated displacement campaign."

**The 3-fact rule**: Every paragraph of analysis must contain at least three independently verifiable data points. Paragraphs that cannot pass this test are opinion, not intelligence, and should be flagged as such or cut.

---

### Rule 8: One Idea Per Sentence

**The rule**: Each sentence contains exactly one complete thought. Compound sentences (joined by "and," "but," "however," "which," "who") are broken into separate sentences unless the compound structure is structurally necessary for the meaning.

**Why it exists**: Compound sentences slow executive reading speed by requiring the reader to track two concepts simultaneously while maintaining syntactic coherence. In a document read at skim speed, compound sentences cause insight to be lost. Single-idea sentences create a rhythm that accelerates comprehension.

**The practical test**: Read the sentence and find the word "and." If removing "and" and splitting the sentence into two creates no loss of meaning — split it. Do the same for "which," "who," "while," and "as."

**Before (compound)**:
> "Epic expanded its RCM capabilities with the acquisition of Strata Decision Technology, which allows them to offer an integrated clinical-financial platform that Oracle Health currently only partially matches, and this creates a significant gap in Oracle Health's ability to compete on total cost of care arguments."

**After (one idea per sentence)**:
> "Epic acquired Strata Decision Technology in Q3 2025. The acquisition gives Epic an integrated clinical-financial platform. Oracle Health does not currently offer equivalent integration. This gap costs Oracle Health deals where total cost of care is the primary evaluation criterion."

---

### Rule 9: Prescriptive, Not Descriptive

**The rule**: Every recommendation is stated as what Oracle Health should do — not what Oracle Health could consider, might want to explore, or may wish to evaluate.

**Why it exists**: Descriptive recommendations waste executive time. A CRO receiving a competitive brief expects the analyst to have already weighed the options and selected the best course of action. Presenting multiple options without a recommendation signals that M&CI has abdicated its analytical function. Executives can push back on a recommendation — they cannot efficiently evaluate five options under time pressure.

**The prescription structure**:
```
Oracle Health should [specific action] by [specific date/milestone]
because [specific evidence].
The risk of inaction is [specific consequence].
```

**Before (descriptive)**:
> "Oracle Health may want to consider whether its current messaging around interoperability adequately addresses Epic's recent product announcements, and might benefit from updating its competitive positioning materials."

**After (prescriptive)**:
> "Oracle Health must update its interoperability battlecard by April 15. Epic announced FHIR R4 compliance at HIMSS 2026 — a claim Oracle Health has not yet countered in sales materials. Three deals currently in competitive evaluation cite this as an open question."

**The one-recommendation rule**: Each memo or brief contains exactly one primary recommendation. Supporting sub-recommendations may follow, but the reader should never finish the document uncertain about what Oracle Health's #1 next action is.

---

### Rule 10: Active Verb Leads

**The rule**: Every sentence begins with its active verb phrase or with the agent performing the action — never with a preposition, an article, an adverb, or a subordinate clause.

**Why it exists**: Sentence-initial position carries the highest cognitive weight in executive reading. Words placed at the front of a sentence are processed first and weighted most heavily. Starting with action verbs creates urgency, clarity, and momentum. Starting with "In the context of," "Given the current environment," or "As we look forward to" creates cognitive fog before the actual content begins.

**Sentence-opening patterns that violate Rule 10**:
- "In order to..." → "To..."
- "There is/are..." → [rewrite with active subject]
- "It is important to note that..." → [just note it]
- "As a result of..." → "Because..."
- "In the event that..." → "If..."
- "Due to the fact that..." → "Because..."
- "In terms of..." → [rewrite with specific subject]
- "At this point in time..." → "Now..." or [remove entirely]

**Before (passive opening)**:
> "In light of the competitive dynamics observed in the Southeast market, there are several strategic considerations that Oracle Health should be aware of."

**After (active verb lead)**:
> "Oracle Health is losing Southeast deals to Epic. Three specific competitive patterns explain why — and each has a defined counter."

---

### Rule 11: The 3-Minute Skim Rule

**The rule**: The entire key argument of every document must be extractable by an executive reading only headings, bold text, and the first sentence of each paragraph — in 3 minutes or less.

**Why it exists**: Research on executive reading behavior from MIT Sloan and Stanford GSB consistently demonstrates that executives scan before they read. In a scan, only three content types are processed: headlines, bold/emphasized text, and paragraph-opening sentences. If the key intelligence is buried in sentence four of a paragraph — it is never seen in the scan pass. The scan pass must deliver 80% of the document's value. Full reading delivers the remaining 20%.

**Matt's skim-pass construction method**:

1. Write the full document first (content complete)
2. Read only: all headings + bold text + first sentence of each paragraph
3. Ask: "Does this skim pass tell the complete story?"
4. If no: rewrite first sentences to carry the key insight. Bold the one most important phrase per section. Revise headings to be informative, not categorical.

**Heading standards**:

| Poor heading (categorical) | Strong heading (informative) |
|---------------------------|------------------------------|
| Market Overview | Epic's Market Share Hit 34% — A 3-Point Gain in 18 Months |
| Competitive Positioning | Oracle Health's Interoperability Lead Is Narrowing |
| Recommendations | Three Actions to Protect Southeast Pipeline Before Q2 |
| Background | Why the Southeast Matters: $2.3B in Active Opportunities |

**Bold text rule**: Bold exactly one phrase per section — the single most important number, claim, or action in that section. Bolding multiple items dilutes the signal. Bolding zero items abandons the skim-pass reader.

---

### Rule 12: No Corporate Jargon

**The rule**: Every word must be the most direct available word for the concept. Corporate jargon, buzzwords, and industry euphemisms are banned. If a 7th grader wouldn't know the word — define it, replace it, or restructure the sentence.

**Why it exists**: Jargon creates two failure modes. First, it increases cognitive load by requiring the reader to translate before comprehending. Second, and more critically, it signals analytical insecurity — writers who don't fully understand their subject default to jargon as a cloaking mechanism. M&CI's credibility rests on clarity.

**The Oracle Health M&CI banned jargon list**:

| Banned Phrase | Replace With |
|--------------|-------------|
| leverage (as a verb) | use |
| synergies | specific shared benefit (name it) |
| best-in-class | [cite the specific benchmark] |
| world-class | [cite the specific benchmark] |
| robust | [describe what makes it strong] |
| scalable | [describe how it scales and to what] |
| innovative | [describe the specific innovation] |
| disruption | [describe what is changing and how] |
| ecosystem | [describe the specific network or relationships] |
| paradigm shift | [describe what is actually changing] |
| holistic | [describe what is included] |
| seamless | [describe the specific friction it eliminates] |
| value-add | [describe the specific value] |
| strategic | [describe the actual strategy] |
| bandwidth | capacity (for people), speed (for systems) |
| circle back | reply, respond, follow up |
| move the needle | [quantify the expected improvement] |
| deep dive | analysis, investigation |
| low-hanging fruit | [name the specific quick win] |
| boil the ocean | [name the specific overreach] |
| at the end of the day | [just say what you mean] |

**Matt's final check**: Ctrl+F each banned phrase before submitting. Zero tolerance.

### Matt's Pre-Submission Checklist

Before any draft proceeds to Gate 1, Matt confirms all 12 items:

```
[ ] 1.  BLUF: First 2 sentences contain the key conclusion and recommendation
[ ] 2.  Reading level: FK Grade between 5.0 and 8.0 (measured, not estimated)
[ ] 3.  Em-dashes used for all parentheticals; zero parentheses () in body text
[ ] 4.  At least one cross-industry analogy per major concept
[ ] 5.  Banned hedge words: zero (Ctrl+F scan complete)
[ ] 6.  Passive voice: zero instances (confirmed by read-aloud)
[ ] 7.  Data precedes narrative in every analytical paragraph
[ ] 8.  All compound sentences reviewed and split where applicable
[ ] 9.  All recommendations are prescriptive ("should"), not descriptive ("could")
[ ] 10. No sentence begins with forbidden openers (In order to / There is / It is)
[ ] 11. Skim pass tested: headings + bold + first sentences tell the full story
[ ] 12. Jargon scan complete: zero banned phrases
```

All 12 boxes must be checked before the draft advances to Gate 1.

---

## Stage 2: Seema the Reviewer

### Role Definition

Seema the Reviewer is M&CI's quality assurance gate. Seema's function is to prevent documents that fail executive communication standards from reaching Mike's review queue — and therefore to protect Mike's time, Oracle Health's credibility, and M&CI's analytical reputation.

Seema does not edit. Seema scores, identifies failure modes, and renders a verdict. When a document fails a test, Seema provides the specific location of the failure and the specific correction required. Seema does not rewrite Matt's work — Seema tells Matt exactly what to fix.

Seema's authority is absolute within her domain. A REVISE or RETHINK verdict is non-negotiable. Matt does not argue with Seema's scores — Matt improves the document.

### Seema's Scoring Architecture

Each of Seema's 10 tests produces a score from 0-10. The final Seema Score used in WQS calculation is the weighted average across all 10 tests.

**Test weight distribution**:

| Test | Weight | Rationale |
|------|--------|-----------|
| Test 1: So What | 15% | The single most important test — no insight = no document |
| Test 2: 90-Second | 15% | Executive reading behavior — speed matters more than completeness |
| Test 3: Action | 15% | M&CI's job is decisions, not information delivery |
| Test 4: Data | 12% | Credibility — unsourced claims destroy analytical trust |
| Test 5: Competitor | 10% | Field defensibility — claims must survive customer scrutiny |
| Test 6: Jargon | 8% | Accessibility — jargon reduces comprehension speed |
| Test 7: Hedging | 8% | Confidence — hedged language transfers burden to the reader |
| Test 8: Surprise | 7% | Value — if the exec already knew this, why did M&CI write it? |
| Test 9: Risk | 7% | Completeness — quantified risk is decision support; vague risk is noise |
| Test 10: Forward | 3% | Relevance — backward-looking intelligence without forward view is history, not intelligence |

### Stage 2 SLA

| Deliverable Type | Standard Review Time |
|-----------------|---------------------|
| Executive brief (1-2 pages) | 2 hours |
| Competitive memo (1 page) | 1 hour |
| Full report (5-10 pages) | 4 hours |
| Email to ELT | 45 minutes |
| Battlecard narrative | 2 hours |
| Quarterly report | 6 hours |

Seema's review output is a structured scoring document delivered alongside the marked draft.

---

## Seema's 10 Tests

### Test 1: The So What Test

**Weight**: 15%

**The question**: If a senior executive reads this document, does it change how they think, what they prioritize, or what they decide to do?

**What Seema is testing**: The fundamental value proposition of the document. Most M&CI failures happen here — not because the writing is bad, but because the underlying intelligence doesn't clear the bar of executive relevance. The So What Test is the only test that can trigger a RETHINK verdict in isolation, regardless of other test scores. A document with no "so what" is not a quality problem — it's a purpose problem.

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | The document would change a VP's calendar, budget allocation, or deal strategy |
| 7-8 | The document confirms and sharpens an existing executive belief with new precision |
| 5-6 | The document provides relevant context but does not shift executive thinking |
| 3-4 | The document adds information but no executive would act on it |
| 1-2 | The document reports what is already known or asks executives to weigh options |
| 0 | The document has no discoverable executive-relevance purpose |

**Pass threshold**: Score ≥ 7

**Failure example**: A 2-page brief documenting Epic's 2024 annual revenue growth (publicly available, widely known, no Oracle Health implication stated) scores 2-3. The data exists but does not change Oracle Health's decision landscape.

**Pass example**: A 2-page brief demonstrating that Epic is deploying a dedicated 40-person team targeting Oracle Health's 7 largest at-risk accounts in Q2 — with specific account names, estimated timing, and the one sales motion that has countered this pattern in comparable situations — scores 9-10.

**Seema's escalation protocol for Test 1 failure**: If Test 1 scores ≤ 4, Seema does not complete the remaining 9 tests. The document is returned to the requestor with a RETHINK verdict and a single question: "What decision does this document enable that Oracle Health could not make without it?" The requestor must answer that question before work resumes.

---

### Test 2: The 90-Second Test

**Weight**: 15%

**The question**: Can a busy executive extract the primary insight, the supporting rationale, and the recommended action in 90 seconds or less?

**Seema's testing method**: Seema reads only the document title, all section headings, all bold text, and the first sentence of each paragraph. This reading should take 60-90 seconds. At the end of the skim pass, Seema answers three questions from memory:

1. What is Oracle Health's key competitive situation as described in this document?
2. What is the evidence basis?
3. What does Oracle Health need to do?

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | All three questions answered correctly from skim pass alone |
| 7-8 | Two of three questions answered; third requires one targeted paragraph read |
| 5-6 | One question answered from skim; other two require full paragraph reading |
| 3-4 | Skim pass yields general topic only; no extractable argument or recommendation |
| 1-2 | Skim pass yields nothing; document requires full sequential reading |
| 0 | Document has no discernible structure; skim pass is impossible |

**Pass threshold**: Score ≥ 7

**Most common failure pattern**: Document title and headings are categorical ("Market Overview," "Competitive Analysis," "Recommendations") rather than informative ("Epic's Q1 Push Puts 7 Oracle Health Accounts at Risk"). The skim pass extracts structure — but no content.

**Remediation for Test 2 failure**:
1. Rewrite all headings to state the key finding, not the category
2. Rewrite first sentence of each paragraph to carry the section's most important claim
3. Bold the single most important number or action in each section

---

### Test 3: The Action Test

**Weight**: 15%

**The question**: Does this document recommend at least one specific, timed, owner-assigned action?

**What Seema is testing**: Whether M&CI has fulfilled its primary responsibility — not to inform, but to enable decisions. Intelligence that does not terminate in a recommended action is academic. Every M&CI deliverable must contain at least one recommendation in the form: "[Owner] should [specific action] by [specific date] because [specific evidence]."

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | Multiple tiered recommendations (primary + supporting), each with owner, action, date, and evidence basis |
| 7-8 | One clear recommendation with owner, action, and date. Evidence basis present but could be stronger |
| 5-6 | Recommendation present but missing owner, date, or specific action (e.g., "Oracle Health should consider improving its messaging") |
| 3-4 | Implied recommendation only — reader must infer what Oracle Health should do |
| 1-2 | No recommendation present; document ends with summary or open question |
| 0 | Document explicitly states it is "for informational purposes" |

**Pass threshold**: Score ≥ 7

**The Action Test and the Prescription Rule**: Test 3 directly enforces Matt's Rule 9 (Prescriptive, Not Descriptive). A document scoring ≤ 5 on Test 3 is structurally non-compliant with Rule 9.

**Required recommendation format**:
```
RECOMMENDATION: [Owner] should [specific action verb + object] by [date/milestone]
BECAUSE: [one sentence evidence basis with data point]
RISK OF INACTION: [specific consequence if recommendation is not followed]
```

Example:
```
RECOMMENDATION: Mike Rodgers should brief the Deal Desk on Epic's Southeast pricing playbook
before April 7.
BECAUSE: Epic's field team is offering 20% first-year discounts in competitive deals — a pattern
confirmed in 4 of 7 Southeast conversations in Q1.
RISK OF INACTION: Oracle Health's reps are losing pricing anchoring battles in 2 active deals
currently at procurement.
```

---

### Test 4: The Data Test

**Weight**: 12%

**The question**: Is every factual claim in the document backed by a sourced, verifiable data point?

**What Seema is testing**: Analytical credibility. M&CI's authority in the organization rests entirely on the defensibility of its data. A single unsourced claim in a brief delivered to the CRO can trigger an "I can't trust this" response that undermines weeks of relationship-building. Every number, every competitor claim, every market sizing figure, every behavioral assertion must have a source.

**Source quality tiers used by Seema**:

| Tier | Examples | Citation Required |
|------|----------|------------------|
| T1 — Primary | SEC filings, earnings transcripts, KLAS reports, patent filings | Full citation: source + date + page |
| T2 — Secondary | Industry analyst reports (Gartner, IDC, Forrester), peer-reviewed research | Citation: author + source + date |
| T3 — Tertiary | Trade press (Health IT News, HIMSS, Modern Healthcare) | Citation: publication + date + URL |
| T4 — Internal | Win/loss interviews, rep debriefs, deal desk data | Citation: source type + date range + N= |
| T5 — Derived | Calculations, models, estimates built from T1-T4 sources | Methodology note + source inputs cited |
| Unacceptable | "Industry consensus," "widely reported," "generally understood" | Not acceptable — find a source or remove the claim |

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | 100% of factual claims sourced at T1-T4; T5 derivations documented |
| 7-8 | ≥90% of claims sourced; T5 methodology documented |
| 5-6 | 70-90% of claims sourced; some claims pass on context inference |
| 3-4 | <70% of claims sourced; significant unsourced assertions present |
| 1-2 | Majority of claims unsourced; document is largely opinion |
| 0 | No sources present |

**Pass threshold**: Score ≥ 7

**Seema's data scan method**: Read through the document and highlight every sentence that makes a factual claim (a number, a competitor action, a market condition, a trend). Count highlighted sentences. Count how many have a T1-T4 citation. Score accordingly.

**Common sourcing failure pattern**: Claims about competitor behavior sourced only to press releases or social media. Seema flags any competitor claim sourced solely from the competitor's own communications — these are marketing, not intelligence.

---

### Test 5: The Competitor Test

**Weight**: 10%

**The question**: Are all competitor claims defensible if Oracle Health used this document in a customer meeting?

**What Seema is testing**: Field readiness. Competitive briefs and battlecard content are not just internal documents — they get shared, forwarded, printed, and sometimes inadvertently shown to the competitors they describe. More critically, sales reps trained on M&CI's competitor claims will repeat those claims in front of customers. A claim that cannot be defended in that context damages Oracle Health's credibility.

**The standard**: Every competitor claim in the document must be something an Oracle Health sales rep could say to a prospect with confidence — and substantiate if challenged. Claims that are directionally true but imprecisely worded are as dangerous as false claims, because they create exposure when challenged on specifics.

**Seema's competitor claim audit**:

For every competitor claim, Seema asks:
1. Is this claim based on T1-T3 source data (not competitor self-reporting)?
2. Is this claim precisely worded (not directionally vague)?
3. Would Oracle Health's legal team approve this language for customer use?
4. Does this claim withstand the scenario: "[Competitor] rep is in the room and challenges this"?

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | All competitor claims T1-T3 sourced, precisely worded, legal-safe |
| 7-8 | All claims sourced; 1-2 precision issues that don't create legal exposure |
| 5-6 | Claims directionally correct but some lack precision or T4 sourcing only |
| 3-4 | Multiple claims that could be challenged; at least one legal exposure risk |
| 1-2 | Several claims based on unverified sources or competitor self-reporting |
| 0 | Document contains claims that are factually inaccurate or legally exposed |

**Pass threshold**: Score ≥ 7

**Automatic RETHINK trigger**: Any document containing a competitor claim rated as legal exposure risk (libel, tortious interference, unverified accusation) triggers an automatic RETHINK and immediate escalation to Mike — not a revision cycle.

---

### Test 6: The Jargon Test

**Weight**: 8%

**The question**: Does the document contain zero unexplained jargon, buzzwords, or corporate-speak?

**What Seema is testing**: Accessibility and cognitive efficiency. Seema applies the banned jargon list from Matt's Rule 12 as her primary instrument. Additionally, Seema tests for unexplained acronyms and healthcare-specific terminology that would be opaque to a general executive audience.

**Seema's jargon categories**:

1. **Banned word list violations**: Any term from Matt's Rule 12 banned list
2. **Unexplained acronyms**: Any acronym not defined on first use (e.g., "EHR" should be defined as "electronic health record (EHR)" on first use, then EHR thereafter)
3. **Unexplained technical terms**: Healthcare IT terms not universally known at C-suite level (FHIR, HL7, ICD-10, value-based care, DSCSA, CMS MIPS — all require plain-language definitions on first use)
4. **Consultant buzzwords**: Synergize, leverage (verb), socialize (as in "socialize this decision"), circle back, bandwidth, ideate, monetize (when used loosely), transformation, journey
5. **Weasel superlatives**: Best-in-class, world-class, industry-leading, cutting-edge, state-of-the-art (all banned unless accompanied by a specific benchmark source)

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | Zero jargon; all acronyms defined on first use; all technical terms plain-languaged |
| 7-8 | 1-2 jargon instances, easily corrected; acronyms mostly defined |
| 5-6 | 3-5 jargon instances; some unexplained acronyms |
| 3-4 | Pervasive jargon requiring line-by-line correction |
| 1-2 | Document is predominantly jargon; meaning is obscured |
| 0 | Document is incomprehensible to a non-specialist executive |

**Pass threshold**: Score ≥ 8 (higher than other tests due to the mechanical, easily-correctable nature of this failure)

---

### Test 7: The Hedging Test

**Weight**: 8%

**The question**: Does the document contain zero hedge words, weasel phrases, or opinion-laundering qualifiers?

**What Seema is testing**: Analytical confidence and decision-forcing clarity. Seema runs a full scan of Matt's banned hedge word list (Rule 5). Each instance of a hedge word is counted. A document with more than two hedge-word instances scores ≤ 6 on Test 7, regardless of other quality.

**Seema's hedge detection protocol**:

Ctrl+F scan for the following terms (full list):
- might, could, may, possibly, potentially, perhaps, arguably, seemingly, apparently
- seems to, appears to, tends to, suggests that, indicates that (used as hedges)
- somewhat, relatively, fairly, rather, quite (used as vague intensifiers)
- in some cases, under certain circumstances, for the most part
- we believe, we think, we feel, it is our view that
- it is worth noting, it should be noted, it is important to note
- going forward (vague temporal hedge)
- at this point in time, currently at this juncture

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | Zero hedge words; all uncertainty expressed as quantified probability |
| 7-8 | 1-2 instances, easily removable without meaning loss |
| 5-6 | 3-5 instances; document tone is cautious but claims are recoverable |
| 3-4 | 6-10 instances; analytical confidence is seriously undermined |
| 1-2 | >10 instances; document reads as uncertain and unconfident throughout |
| 0 | Document is structurally hedged (e.g., "could potentially consider possibly...") |

**Pass threshold**: Score ≥ 8

---

### Test 8: The Surprise Test

**Weight**: 7%

**The question**: Does this document include at least one non-obvious insight — something the executive did not know and could not have easily found without M&CI?

**What Seema is testing**: Informational value-add. The organizational justification for an M&CI function rests on its ability to surface insights that leadership cannot generate independently. A brief that reports publicly available information, restates known competitive dynamics, or summarizes what the executive already told the analyst — is a waste of organizational resources. M&CI earns its seat at the table by consistently delivering the non-obvious.

**Non-obvious insight categories**:

1. **Pattern recognition**: A trend not yet visible from any single data source
2. **Signal detection**: An early indicator of a competitor behavior before it becomes market news
3. **Implication mapping**: A widely-known fact connected to an Oracle Health-specific consequence that others haven't drawn
4. **Contradiction exposure**: Evidence that contradicts a commonly held belief in the organization
5. **Blind spot illumination**: A competitive dynamic in a geography, segment, or product area that Oracle Health leadership isn't watching

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | 2+ non-obvious insights; one would materially change how the executive thinks |
| 7-8 | 1 clear non-obvious insight that M&CI uniquely surfaced |
| 5-6 | Insight is partially non-obvious; partially known or inferable |
| 3-4 | Document confirms what executive already believed; no new information |
| 1-2 | Document restates publicly available or widely known information |
| 0 | Document contains no information that the executive could not have accessed in 10 minutes of independent research |

**Pass threshold**: Score ≥ 6 (slightly lower threshold — non-obviousness is harder to guarantee than mechanical quality)

---

### Test 9: The Risk Test

**Weight**: 7%

**The question**: Are the risks described in this document quantified — not merely identified?

**What Seema is testing**: Decision quality support. Risk identification without quantification is noise. An executive reading "there is a risk that Epic could outperform Oracle Health in the Southeast" knows nothing more than before they read the sentence. An executive reading "Epic's current trajectory suggests a 60-70% probability of winning 2 of Oracle Health's 4 active Southeast opportunities in Q2, representing $18M in at-risk pipeline" can make a resource allocation decision.

**Risk quantification requirements**:

Every risk mentioned in an M&CI document must include at minimum:
- **Probability**: Expressed as a percentage range or categorical probability (Low/Medium/High with defined thresholds)
- **Impact**: Expressed as a dollar figure, deal count, market share point, or timeline consequence
- **Timeline**: When the risk materializes (specific quarter, milestone, or event trigger)
- **Mitigation**: At least one action Oracle Health can take to reduce the risk

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | All risks quantified on all four dimensions; mitigation actions specific and timed |
| 7-8 | All risks quantified on probability and impact; timeline and mitigation present but could be sharper |
| 5-6 | Most risks quantified on 2-3 dimensions; some vague risk statements present |
| 3-4 | Risks identified but mostly unquantified; impact statements are qualitative only |
| 1-2 | Risk section present but functionally useless for decision support |
| 0 | No risk content; or "see attached for risks" with no risks in the document |

**Pass threshold**: Score ≥ 7

---

### Test 10: The Forward Test

**Weight**: 3%

**The question**: Does this document look forward — what will happen — rather than only backward — what happened?

**What Seema is testing**: Temporal relevance. Intelligence is the discipline of reducing uncertainty about future conditions. A historical analysis with no forward implication is research, not intelligence. M&CI documents must always connect backward-looking data to forward-looking predictions, scenarios, or recommendations.

**Forward-looking content types**:

1. **Prediction**: "Epic will likely announce [X] at HIMSS 2026 based on their current product roadmap and hiring patterns"
2. **Scenario**: "If Epic closes the Vanderbilt health system, Oracle Health's Southeast pipeline exposure increases by $34M in 90 days"
3. **Signal watch**: "Three early indicators suggest Epic is preparing a community hospital campaign in the Midwest — expect market activity in Q3"
4. **Trend projection**: "At Epic's current Southeast win rate, Oracle Health will be in minority market position in that region by Q4 2027"

**Scoring criteria**:

| Score | Criteria |
|-------|----------|
| 9-10 | Document is primarily forward-looking; predictions are specific and timed |
| 7-8 | Clear forward section with at least one specific prediction or scenario |
| 5-6 | Forward implication present but vague (e.g., "this trend will likely continue") |
| 3-4 | Mostly backward; one passing reference to future implications |
| 1-2 | Entirely backward-looking; historical analysis only |
| 0 | Document explicitly presents itself as a historical record with no forward relevance |

**Pass threshold**: Score ≥ 6

---

### Seema's Decision Protocol

After scoring all 10 tests, Seema calculates the weighted Seema Score and issues a three-tier decision:

**SEND** (Seema Score ≥ 8.5):
> "Document passes all 10 tests at acceptable thresholds. WQS calculation pending. Proceeding to Mike's queue."

**REVISE** (Seema Score 6.5-8.4):
> "Document requires targeted revision on [list failing tests]. Specific corrections attached. Return to Matt. Turnaround: [SLA]. Max 2 revision cycles before escalating to Mike."

**RETHINK** (Seema Score < 6.5 OR Test 1 score ≤ 4):
> "Document does not meet minimum standards for executive audience. Root cause: [diagnosis]. Required action: [full re-draft / return to research / escalate to Mike]. This is not a writing quality issue — this is a [content / structure / purpose] issue."

**The revision cycle limit**: A document may go through a maximum of two REVISE → Matt → Seema cycles. If the document has not reached SEND after two revision cycles, it is automatically escalated to Mike with Seema's scoring history attached. Mike decides whether to approve, redirect, or terminate the deliverable.

---

## Stage 3: Mike Final Review

### Mike's Role in the Pipeline

Mike Rodgers serves as the final quality gate before distribution. By the time a document reaches Mike, it has already passed Matt's 12-rule checklist and Seema's 10-test scoring at WQS ≥ 0.85. Mike's review is not a re-edit of writing quality — that has already been validated. Mike's review focuses on three dimensions that neither Matt nor Seema can fully assess:

1. **Strategic accuracy**: Is the competitive intelligence correct as of today? Does Mike have information from sources (ELT conversations, deal desk, executive relationships) that would change the analysis?
2. **Audience calibration**: Is the tone, length, depth, and framing appropriate for the specific named executive(s) who will receive this document? Mike has relationship context that Matt and Seema do not.
3. **Organizational implications**: Does this document create any unintended internal dynamics — credit attribution, political sensitivity, message sequencing with other Oracle Health communications?

### Mike's Review Checklist

```
[ ] 1.  ACCURACY: Is every competitive claim current and correct to my knowledge?
[ ] 2.  GAPS: Is there material information I know that the document should include?
[ ] 3.  AUDIENCE FIT: Is this calibrated appropriately for [named recipient(s)]?
[ ] 4.  SEQUENCING: Should this be coordinated with any other Oracle Health communications?
[ ] 5.  TONE: Does this reflect Oracle Health M&CI's voice — confident, evidence-based, direct?
[ ] 6.  POLITICAL SENSITIVITY: Does this document inadvertently create internal friction?
[ ] 7.  RECOMMENDATION ENDORSEMENT: Do I personally endorse the primary recommendation?
[ ] 8.  DISTRIBUTION CHANNEL: Is the planned distribution channel appropriate for this content?
```

### Mike's Three Decisions

**APPROVED**: Document is distribution-ready. Mike clears for send/publish.

**APPROVED WITH EDITS**: Document is structurally sound but requires specific Mike-identified changes (accuracy corrections, audience calibration, addition of context Mike holds). Mike marks changes and returns to Matt for implementation, then self-approves the corrected version without re-running full pipeline.

**HOLD**: Document should not be distributed at this time due to timing, sequencing, accuracy, or strategic reasons. Mike provides specific hold rationale and resumption trigger. Hold documents return to the pipeline when the trigger condition is met.

### Mike's SLA

| Deliverable Type | Standard Review | Rush Review |
|-----------------|-----------------|------------|
| Executive brief | 24 hours | 4 hours |
| Competitive memo | 4 hours | 1 hour |
| Full report | 48 hours | 8 hours |
| ELT email | 2 hours | 30 minutes |
| Battlecard narrative | 8 hours | 2 hours |
| Quarterly report | 3 business days | 1 business day |

If Mike does not review within SLA, the document owner escalates via direct Slack message. Unreviewed documents do not self-approve.

---

## Pipeline Bypass Criteria

Certain deliverable types and situations warrant bypass of the full Matt/Seema pipeline. Bypass is not an exemption from quality — it is a recognition that the pipeline overhead is disproportionate to the deliverable stakes.

### Eligible for Bypass (Matt Stage Only — No Seema Review Required)

| Condition | Bypass Level | Approver |
|-----------|-------------|----------|
| Internal team communication, non-executive audience | Full bypass | Author |
| First draft for internal circulation and feedback | Matt stage only | Author |
| Data appendix or raw research attachment | Full bypass | Author |
| Short (≤5 sentence) deal desk update | Full bypass | Author |
| Forwarding external research with brief annotation | Full bypass | Author |
| Time-critical intelligence (breaking news, <1hr turnaround) | Mike-direct (skip Matt/Seema, Mike edits directly) | Mike |

### Never Eligible for Bypass

| Deliverable | Reason |
|-------------|--------|
| Any document going to VP+ | Stakes are too high |
| Competitive claims to be used with customers | Legal exposure |
| Anything in Mike's name going to ELT | Reputation risk |
| Battlecard narrative sections | Sales rep training multiplier effect |
| M&CI quarterly/annual reports | Permanent record |

### Rush Pipeline (Not Bypass — Compressed Timelines)

When a document is time-critical but cannot be bypassed, the Rush Pipeline applies:
- Matt SLA: 50% of standard SLA
- Seema SLA: 50% of standard SLA
- Mike SLA: 50% of standard SLA
- Seema score threshold reduced from 8.5 to 7.5 for SEND designation
- Mike's review is synchronous (live call) rather than async

Rush Pipeline requires Mike's explicit authorization. It may not be self-declared by an analyst.

---

## Predictive Algorithm: Writing Quality Score (WQS)

The Writing Quality Score is a composite, reproducible metric for evaluating executive communication quality. WQS enables M&CI to track writing quality over time, identify systematic improvement opportunities, and make pipeline routing decisions programmatically.

### WQS Architecture

```
WQS = (Automated Score × 0.60) + (Seema Score × 0.40)

Where:

Automated Score = weighted composite of 6 measurable text attributes

Seema Score = weighted composite of Seema's 10 tests (normalized to 0-1.0 scale)
```

### Automated Score Components

**Component 1: Flesch-Kincaid Grade Level Score**
```
Target range: Grade 5.0 to 8.0

Scoring:
  Grade 5.0-8.0:  1.00 (full score)
  Grade 4.0-4.9:  0.85 (slightly below target — too simple)
  Grade 8.1-10.0: 0.75 (above target — marginally too complex)
  Grade 10.1-12.0: 0.50 (significantly above target)
  Grade > 12.0:   0.20 (fails the readability standard entirely)
  Grade < 4.0:    0.70 (too simple for professional context)

Weight: 25% of Automated Score
```

**Component 2: Passive Voice Rate**
```
Target: < 5% of sentences

Scoring:
  0-4.9%:  1.00
  5-9.9%:  0.80
  10-14.9%: 0.55
  15-19.9%: 0.30
  ≥ 20%:   0.10

Weight: 20% of Automated Score
```

**Component 3: Average Sentence Length**
```
Target: ≤ 18 words per sentence (average)

Scoring:
  ≤ 15 words:  1.00
  16-18 words: 0.90
  19-22 words: 0.70
  23-26 words: 0.45
  ≥ 27 words:  0.20

Weight: 15% of Automated Score
```

**Component 4: Hedge Word Count**
```
Target: 0 hedge words

Scoring (per 1000 words):
  0 instances:    1.00
  1-2 instances:  0.85
  3-5 instances:  0.60
  6-10 instances: 0.35
  > 10 instances: 0.10

Weight: 20% of Automated Score
```

**Component 5: Data Density**
```
Target: ≥ 3 sourced facts per 100 words

Scoring:
  ≥ 5 facts/100w:  1.00
  3-4.9 facts/100w: 0.85
  2-2.9 facts/100w: 0.60
  1-1.9 facts/100w: 0.35
  < 1 fact/100w:   0.15

Weight: 10% of Automated Score
```

**Component 6: Action Verb Lead Rate**
```
Target: ≥ 40% of sentences begin with an action verb or active agent

Scoring:
  ≥ 50%:  1.00
  40-49%: 0.90
  30-39%: 0.70
  20-29%: 0.45
  < 20%:  0.20

Weight: 10% of Automated Score
```

### Full WQS Calculation

```
Automated Score (AS) =
  (FK_Score × 0.25) +
  (Passive_Score × 0.20) +
  (Sentence_Length_Score × 0.15) +
  (Hedge_Score × 0.20) +
  (Data_Density_Score × 0.10) +
  (Action_Verb_Score × 0.10)

Seema Score (SS) =
  (Test1 × 0.15) + (Test2 × 0.15) + (Test3 × 0.15) + (Test4 × 0.12) +
  (Test5 × 0.10) + (Test6 × 0.08) + (Test7 × 0.08) + (Test8 × 0.07) +
  (Test9 × 0.07) + (Test10 × 0.03)
  ÷ 10  [normalized to 0-1.0 scale]

WQS = (AS × 0.60) + (SS × 0.40)
```

### WQS Decision Thresholds

| WQS | Decision | Pipeline Action |
|-----|----------|----------------|
| ≥ 0.90 | SEND — Excellence | Advance to Mike queue; flag as exemplar for M&CI writing archive |
| 0.85-0.89 | SEND — Standard | Advance to Mike queue |
| 0.75-0.84 | REVISE — Minor | Return to Matt with Seema's line-level corrections; target 1 revision cycle |
| 0.65-0.74 | REVISE — Significant | Return to Matt with structural corrections; target 2 revision cycles |
| 0.50-0.64 | RETHINK — Writing | Full re-draft required; underlying content may be sound but execution fails |
| < 0.50 | RETHINK — Content | Content and/or purpose problem; escalate to Mike |

### WQS Benchmarks for M&CI

M&CI tracks rolling WQS performance to monitor team writing quality trends:

| Benchmark | Target |
|-----------|--------|
| Rolling 90-day average WQS | ≥ 0.87 |
| First-pass SEND rate (no revisions) | ≥ 70% |
| RETHINK rate | ≤ 10% |
| Average revision cycles per document | ≤ 1.2 |
| Documents achieving WQS ≥ 0.90 (excellence) | ≥ 25% |
| Documents requiring >2 revision cycles | ≤ 5% |

---

## Monte Carlo: Reader Engagement Modeling

M&CI uses a Monte Carlo simulation model to estimate the probability that a given document will be read fully and result in executive action. This model is run on Quarterly Reports, ELT briefings, and any document where distribution decisions involve trade-offs between comprehensiveness and accessibility.

### Model Variables

**Variable 1: Reading Time Available (RTA)**
Distribution: Triangular
- Minimum: 2 minutes (executive caught between meetings)
- Mode: 7 minutes (average executive document-reading session)
- Maximum: 20 minutes (dedicated reading time, e.g., flight, quiet office)

**Variable 2: Document Length (DL)**
Input: Actual word count converted to estimated reading time at 250 words/minute (executive reading pace, slightly above average due to trained scanning behavior)

**Variable 3: Writing Quality Score (WQS)**
Input: Calculated WQS from pipeline
Interpretation: WQS acts as a multiplier on both read probability and action probability
- WQS ≥ 0.90: Full multiplier (1.0)
- WQS 0.85-0.89: 0.95 multiplier
- WQS 0.75-0.84: 0.85 multiplier
- WQS < 0.75: Document should not reach this model (should be in REVISE/RETHINK)

**Variable 4: Audience Specificity (AS)**
Distribution: Binary
- 1.0 = Document is addressed to and relevant to the specific executive
- 0.70 = Document is broadly relevant but not specifically targeted

**Variable 5: Distribution Channel Quality (DCQ)**
Distribution: Categorical
- Direct email from Mike to named executive: 0.90
- Seismic/Highspot push with notification: 0.65
- SharePoint library post: 0.40
- Slack #intel channel: 0.55
- Attached to meeting deck: 0.75

### Model Outputs

The Monte Carlo runs 10,000 simulations and produces:

```
P(read fully) = P(RTA > DL × WQS_multiplier) × AS × DCQ

P(take action | read fully) = f(WQS, Test3_score, Test1_score)
  = (WQS × 0.50) + (Test3_score/10 × 0.30) + (Test1_score/10 × 0.20)

Expected Action Rate = P(read fully) × P(take action | read fully)

Output bands:
  P10 (pessimistic scenario):  10th percentile outcome
  P50 (median scenario):       50th percentile outcome
  P90 (optimistic scenario):   90th percentile outcome
```

### Benchmark Expected Action Rates

| Document Type | Target Expected Action Rate (P50) |
|--------------|----------------------------------|
| ELT executive brief | ≥ 55% |
| Competitive memo to Sales leadership | ≥ 65% |
| Quarterly M&CI report | ≥ 40% |
| Win/loss executive summary | ≥ 50% |
| Battlecard with narrative | ≥ 70% (field rep use) |

### Decision Rules from Monte Carlo

If P50 Expected Action Rate falls below target:
1. **Length check**: Is DL > recommended length for deliverable type? → Reduce
2. **Channel check**: Is DCQ the highest available? → Upgrade distribution
3. **WQS check**: Is WQS below 0.85? → Return to pipeline
4. **Targeting check**: Is the document broad vs. specific? → Personalize

---

## Executive Reading Behavior Model

Understanding how executives actually read enables M&CI to write for the real conditions under which documents are consumed — not the ideal conditions.

### The 4-Phase Executive Reading Pattern

Research from Harvard Business Review, MIT Sloan Management Review, and Stanford's executive decision-making research consistently documents a four-phase pattern in how senior leaders engage with written intelligence:

**Phase 1: Relevance Scan (3-8 seconds)**
The executive scans the document title, sender, and first visible content block. Decision: "Is this worth more time?" Documents fail this gate when titles are categorical ("Market Update Q1"), senders are unfamiliar, or the first visible content is background context rather than a key finding. Matt's Rule 1 and Rule 11 are specifically designed for this phase.

**Phase 2: Value Assessment (30-60 seconds)**
If the document passes Phase 1, the executive conducts a skim pass: headings, bold text, first sentences, any charts or tables. Decision: "Does this contain something I need to know or act on?" Documents fail this gate when headings are descriptive rather than informative, key findings are buried in paragraph bodies, or no visual hierarchy exists to guide the scan. Matt's Rule 11 (3-Minute Skim Rule) directly addresses Phase 2.

**Phase 3: Selective Deep Reading (2-10 minutes)**
If Phase 2 surfaces a relevant finding, the executive reads the specific section in depth. Most executives read 2-3 sections, not the full document. Decision: "What specifically does this mean for my decisions?" Documents fail this phase when sections require sequential reading (e.g., "as discussed in Section 2 above") or when recommendations are not co-located with evidence.

**Phase 4: Action Disposition (30-60 seconds)**
The executive decides: Do nothing, save for later, forward to a team member, or take the recommended action. Documents succeed at Phase 4 when recommendations are explicit, timed, and include the cost of inaction — making the "act now" path obviously easier than the "defer" path.

### Implications for Matt's Writing

| Executive Phase | Matt's Design Response |
|----------------|----------------------|
| Phase 1 (3-8 sec) | Title must state the finding, not the category. First sentence must be the BLUF. |
| Phase 2 (30-60 sec) | Every heading informative. Every first sentence carries section's key claim. Bold text on most important data point per section. |
| Phase 3 (2-10 min) | Evidence co-located with claim. No cross-references to other sections. Each section must be self-contained. |
| Phase 4 (30-60 sec) | Recommendation section at the end AND at the beginning. Action, owner, deadline explicit. Cost of inaction stated. |

### The Cognitive Load Model

Executives reading under time pressure operate at reduced working memory capacity. The implications for writing:

- **Chunk size**: 3-4 items per list. Never more than 5. Working memory holds 4±1 items.
- **Sentence length**: ≤18 words aligns with single working-memory processing load.
- **Paragraph length**: ≤4 sentences prevents executive from needing to track context across units.
- **Concept density**: One new concept per paragraph. Two concepts per paragraph require explicit signposting ("first... second...") to prevent blending.
- **Decision presentation**: When presenting options, limit to 3. Four or more options trigger "decide later" response.

### The Context-Switching Tax

Research on executive multitasking demonstrates that a document read while context-switching (between meetings, notifications, conversations) has 40-60% lower retention than one read in focused attention. M&CI cannot control when executives read — but can design documents to survive context-switching:

1. Every section must be independently meaningful (not dependent on prior sections)
2. Key numbers must be restated in the recommendation section even if stated earlier
3. Document must be interpretable after a multi-hour interruption at any point
4. The BLUF must deliver full value even if the executive never returns to finish reading

---

## Format Standards by Deliverable Type

### Executive Competitive Brief

**Purpose**: Deliver a competitive intelligence finding with strategic implications to VP+ audience.

**Specifications**:
- Length: 400-800 words (2-3 pages maximum with visual formatting)
- Structure: BLUF (1 paragraph) → Key Findings (3-5 bullets) → Analysis (2-3 paragraphs) → Recommendations (1-3 bullets with owner/date) → Sources (cited, not embedded)
- Headings: 2-4 informative headings (not categorical)
- Data: Minimum 8 sourced data points
- Bold text: One phrase per section
- WQS target: ≥ 0.87
- SLA: Input to approved output ≤ 24 hours

**Template heading structure**:
```
# [The Finding, Not the Category — e.g., "Epic's Southeast Push Threatens $18M in Oracle Health Pipeline"]

**Bottom Line**: [2-sentence BLUF — situation and recommendation]

## What Changed
[Most recent intelligence, newest first]

## Why It Matters for Oracle Health
[Direct Oracle Health implication of the intelligence]

## What Oracle Health Should Do
[Recommendation block with owner, action, date, risk of inaction]

## Sources
[Cited T1-T4 sources]
```

---

### Competitive Memo (1 Page)

**Purpose**: Rapid-turnaround competitive intelligence on a single topic for deal desk or field use.

**Specifications**:
- Length: 200-400 words (strict 1-page maximum)
- Structure: BLUF sentence → 3 key facts → 1 recommendation → source list
- No section headings (length doesn't warrant)
- Bold: One phrase maximum
- WQS target: ≥ 0.85
- SLA: Input to approved output ≤ 4 hours

---

### Win/Loss Executive Summary

**Purpose**: Summarize win/loss interview findings for Product, Sales leadership, and ELT with strategic implications.

**Specifications**:
- Length: 600-1200 words
- Structure: BLUF → Win/Loss count (N=) and period → Top 3 win themes → Top 3 loss themes → Primary competitive pattern → Recommendations
- Data: Include verbatim rep/customer quotes (de-identified if necessary)
- WQS target: ≥ 0.86
- Frequency: Monthly (standard) or deal-triggered (for major wins/losses)

---

### ELT Email from Mike

**Purpose**: Concise executive communication from Mike to Oracle Health ELT members.

**Specifications**:
- Length: 100-250 words (3-5 paragraphs maximum)
- Format: No headers. Paragraph prose. First sentence is the BLUF.
- Tone: Confident, direct, collegial. Not overly formal or corporate.
- Data: 1-3 key facts, prominently placed
- Recommendation: One clear ask or update
- WQS target: ≥ 0.88 (higher than briefs — Mike's name is attached)
- SLA: Input to approved send ≤ 2 hours

---

### M&CI Quarterly Report

**Purpose**: Comprehensive quarterly intelligence review for senior leadership.

**Specifications**:
- Length: 1,500-3,000 words
- Structure: Executive Summary (BLUF, 1 page) → Competitive Landscape Changes → Win/Loss Analysis → Key Intelligence Findings → Recommendations for Q+1 → Appendix (raw data, sources)
- Charts/Visuals: 2-4 maximum; each labeled with finding, not just topic (e.g., "Epic Gained 3 Points of Market Share in Q1" not "Market Share Chart")
- WQS target: ≥ 0.88
- SLA: Input to distribution ≤ 5 business days
- Distribution: ELT + Sales Leadership + Product Marketing

---

### Battlecard Narrative Sections

**Purpose**: Provide written strategic context and messaging guidance for competitive battlecards used by field reps.

**Applicable sections**: Oracle Health value narrative, competitor weakness framing, objection responses, proof points.

**Specifications**:
- Length: 50-150 words per section (battlecard real estate is constrained)
- Tone: Confident, affirmative, coach-voice. Written as if coaching the rep in the moment.
- Claims: 100% T1-T3 sourced (Competitor Test applies with full rigor)
- WQS target: ≥ 0.90 (field use multiplier effect requires highest standards)
- Rep readability test: If a rep cannot internalize and replay this content in 60 seconds, it fails

---

## RACI Matrix

| Activity | Mike Rodgers | Matt (Writer) | Seema (Reviewer) | Intel Analyst | Distribution |
|----------|-------------|---------------|------------------|---------------|-------------|
| Define deliverable scope and audience | A/R | I | I | C | I |
| Provide research inputs | A | I | I | R | - |
| Draft writing (Stage 1) | I | R | I | C | - |
| Gate 1 completeness check | I | A | - | - | - |
| Stage 2 review and scoring | C | I | R/A | - | - |
| SEND/REVISE/RETHINK decision | C | I | A/R | - | - |
| Revision cycles (max 2) | I | R | A | - | - |
| Stage 3 final review | R/A | I | I | - | - |
| Distribution approval | A/R | - | - | - | C |
| Pipeline bypass authorization | A/R | I | I | I | - |
| Rush pipeline authorization | A/R | I | I | I | - |
| WQS tracking and reporting | A | I | R | - | - |
| SOP maintenance and updates | A/R | C | C | - | - |

**RACI Key**: R = Responsible (does the work), A = Accountable (owns the outcome), C = Consulted, I = Informed

---

## Expert Panel Scoring

All M&CI documents produced under this pipeline are eligible for Expert Panel scoring — a simulated peer review by 8 weighted perspectives drawn from Oracle Health M&CI's full agent and stakeholder roster. Expert Panel scoring is applied to:
- All Quarterly Reports (mandatory)
- All ELT-bound documents (mandatory)
- Any document Mike flags for panel review
- Randomly sampled 10% of standard briefs (for calibration purposes)

### Panel Composition and Weights

| Panelist | Weight | Domain | Primary Review Focus |
|---------|--------|--------|---------------------|
| Matt (self-review) | 20% | Writing craft | 12 Rules compliance, structure, clarity |
| Seema | 20% | Quality assurance | 10 Tests scores, WQS |
| Steve | 15% | Strategy | Strategic accuracy, recommendation quality |
| Compass | 10% | Product | Product-market fit of claims, roadmap accuracy |
| Ledger | 10% | Finance | Data integrity, cost/revenue figures, ROI claims |
| Marcus | 10% | Marketing | Brand voice, audience calibration, positioning |
| Forge | 10% | Engineering | Technical claim accuracy, implementation feasibility |
| Herald | 5% | Distribution | Channel fit, timing, audience relevance |

### Scoring Method

Each panelist scores the document on a 1-10 scale across their domain. The weighted average constitutes the Panel Score.

**Panel Score targets**:

| Panel Score | Interpretation |
|-------------|----------------|
| 9.5-10.0 | Exemplar — archive as M&CI writing standard reference |
| 9.0-9.4 | Excellence — distribute with full confidence |
| 8.5-8.9 | Strong — distribute; note minor improvements for future drafts |
| 8.0-8.4 | Acceptable — distribute; address noted issues in next revision |
| 7.0-7.9 | Marginal — targeted revision recommended before distribution |
| < 7.0 | Fail — return to pipeline regardless of WQS |

**Target**: Panel Score ≥ 9.0 for ELT-bound documents; ≥ 8.5 for standard briefs.

---

## Key Performance Indicators

M&CI tracks the following pipeline KPIs on a rolling 90-day basis, reviewed monthly by Mike:

### Pipeline Efficiency KPIs

| KPI | Target | Calculation |
|-----|--------|-------------|
| First-pass SEND rate | ≥ 70% | Documents achieving SEND on first Seema review ÷ total documents submitted |
| RETHINK rate | ≤ 10% | Documents receiving RETHINK verdict ÷ total documents submitted |
| Average revision cycles | ≤ 1.2 | Total revision cycles ÷ total documents through pipeline |
| Average cycle time (input → approved) | ≤ 36 hours | Avg hours from research input receipt to Mike's APPROVED decision |
| SLA adherence rate | ≥ 90% | Stages completed within SLA ÷ total stage instances |

### Writing Quality KPIs

| KPI | Target | Calculation |
|-----|--------|-------------|
| Rolling 90-day average WQS | ≥ 0.87 | Mean WQS across all documents in period |
| WQS excellence rate | ≥ 25% | Documents scoring WQS ≥ 0.90 ÷ total documents |
| Average Flesch-Kincaid grade | 5.5-7.5 | Mean FK grade across all documents |
| Average passive voice rate | < 5% | Mean passive voice rate across all documents |
| Average hedge word density | < 1.5/1000w | Mean hedge word count per 1000 words |
| Average data density | ≥ 3.5 facts/100w | Mean sourced facts per 100 words |

### Impact KPIs

| KPI | Target | Measurement Method |
|-----|--------|-------------------|
| Executive read-through rate (confirmed) | ≥ 50% | Read receipts, reply rate, in-meeting reference |
| Recommendation adoption rate | ≥ 40% | Tracking whether recommended actions are taken within 30 days |
| Expected Action Rate (P50) — briefs | ≥ 55% | Monte Carlo model output |
| Expected Action Rate (P50) — quarterly reports | ≥ 40% | Monte Carlo model output |
| Seema 10-test average score | ≥ 8.0 | Mean test score across all 10 tests, all documents in period |
| Documents achieving Panel Score ≥ 9.0 | ≥ 50% of panel-reviewed documents | Expert Panel results |

### Quality Trend Indicators

M&CI tracks the following as leading indicators of pipeline health:

| Indicator | Signal | Action |
|-----------|--------|--------|
| First-pass SEND rate declining over 3 consecutive weeks | Pipeline input quality degrading | Review research handoff process; retrain analysts on input standards |
| RETHINK rate increasing | Content/purpose failures, not writing | Review deliverable scoping process; clarify M&CI mandate |
| Average revision cycles > 1.5 | Systematic Rule violations | Identify which Rules are failing; targeted Matt refresh |
| WQS 90-day average < 0.85 | Writing quality below standard | Full Rule refresh; consider exemplar document review session |
| Test 1 (So What) average < 7.5 | M&CI producing low-value intelligence | Review research pipeline; question deliverable selection criteria |
| Test 3 (Action) average < 7.5 | Recommendations too vague | Enforce prescription format; examples from exemplar archive |

---

## Appendix A: Banned Hedge Words — Master List

The following words and phrases are banned from all M&CI executive documents. This list is enforced by Seema's Test 7. Matt conducts a Ctrl+F scan before submission.

```
might          could          may (when used as hedge)    possibly
potentially    perhaps        arguably                    seemingly
apparently     seems to       appears to                  tends to
suggests that  indicates that (when used to hedge)       somewhat
relatively     fairly         rather (as qualifier)       quite
in some cases  under certain circumstances                for the most part
we believe     we think       we feel                     it is our view
it is worth noting            it should be noted          it is important to note
going forward  at this point  currently (when used to hedge)  at this juncture
could potentially             might consider              may want to
it is possible might be able  arguably could              seems like it might
```

---

## Appendix B: Corporate Jargon — Master List

The following terms are banned or restricted in M&CI documents. Restrictions noted where applicable.

```
leverage (as verb)    → use
synergies             → [name the specific shared benefit]
best-in-class         → [cite the specific benchmark]
world-class           → [cite the specific benchmark]
robust                → [describe what makes it strong]
scalable              → [describe how it scales]
innovative            → [describe the specific innovation]
disruption            → [describe what is actually changing]
ecosystem             → [describe the specific network]
paradigm shift        → [describe what is changing and how]
holistic              → [describe what is included]
seamless              → [describe the specific friction eliminated]
value-add             → [describe the specific value]
strategic             → [describe the actual strategy]
bandwidth             → capacity / speed (context-dependent)
circle back           → reply / respond / follow up
move the needle       → [quantify the expected improvement]
deep dive             → analysis / investigation
low-hanging fruit     → [name the specific quick win]
boil the ocean        → [name the specific overreach]
at the end of the day → [just say what you mean]
going forward         → [specify the timeframe]
socialize             → share / discuss / align on
ideate                → brainstorm / generate options
monetize (loosely)    → [describe the specific revenue mechanism]
transformation        → [describe what is specifically changing]
journey               → [describe the actual process or timeline]
stakeholder           → [name the specific people or roles]
alignment             → [describe what agreement is needed on]
visibility            → [describe what information is needed]
```

---

## Appendix C: Document Versioning and Archive

### Versioning Protocol

All M&CI documents produced under this pipeline follow a three-digit versioning scheme:

```
Document ID: [deliverable type]-[date]-[topic slug]
Example: competitive-brief-2026-03-23-epic-southeast

Version: v[major].[minor].[patch]
  Major: Full re-draft (RETHINK outcome)
  Minor: Significant revision (REVISE outcome, structural changes)
  Patch: Minor edit (REVISE outcome, targeted corrections, or Mike's APPROVED WITH EDITS)

  Example: v1.2.1 = first full draft, second revision cycle, first patch
```

### Archive Structure

Approved documents are archived in the M&CI SharePoint with the following metadata:

```
/M&CI/Executive Documents/
  /Approved/
    /[Year]/[Quarter]/[Deliverable Type]/
      [Document ID]_v[version]_APPROVED.[format]
  /In-Pipeline/
    [Document ID]_v[version]_[STAGE].[format]
  /Exemplars/
    [Document ID]_v[version]_EXEMPLAR.[format]  ← WQS ≥ 0.90
```

### Exemplar Archive

Documents achieving WQS ≥ 0.90 and Panel Score ≥ 9.5 are promoted to the Exemplar Archive. The Exemplar Archive serves as:
- Reference material for Matt's drafting
- Training examples for new team members
- Calibration samples for Seema's scoring consistency
- Evidence of M&CI's analytical standard for internal positioning

The Exemplar Archive should maintain a minimum of 10 documents across all deliverable types. When below 10, achieving Exemplar status is a stated team objective.

---

*SOP-19 v1.0 APPROVED — Oracle Health M&CI — Mike Rodgers, Sr. Director*
*Next review: 2026-09-23 (6-month cycle)*
