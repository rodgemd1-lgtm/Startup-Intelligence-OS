# Hermes Performance Evaluation Panel

**Panel Name:** The Hermes Review Board
**Mission:** Continuously assess Hermes (Jake's personal AI assistant) from 9 distinct domain perspectives, producing a single composite Hermes Health Score (HHS) on a regular cadence. The panel exists to ensure Hermes improves measurably and that no dimension of user experience degrades silently.

**Framework:** Brain / Hands / Feet (3 panelists per category)
**Evaluation cadence:** Weekly (Friday EOD), with monthly deep review
**Created:** 2026-03-21
**Owner:** Susan (orchestration)

---

## Panel Design Principles

1. Each panelist evaluates from a genuine user-experience angle, not a checklist. The question is always: "Does this work for Mike?"
2. Panelists are mapped to Susan agents who have the domain knowledge to assess meaningfully.
3. Scoring is 1-10 per panelist. The composite HHS is a weighted average that reflects the current build phase.
4. Weights shift as Hermes matures -- early phases weight Brain and Feet higher (infrastructure must work before Hands matter).

---

## The 9 Panelists

### BRAIN (Cognitive Capabilities)

These three panelists evaluate whether Hermes understands Mike, remembers what matters, and reasons well.

---

#### Panelist 1: Knowledge Engineer -- "The Librarian"

| Field | Value |
|-------|-------|
| Susan Agent | Knowledge Engineer (engineering group) |
| Panel Role | Memory Quality Assessor |
| Domains Covered | D1 (Cognitive Memory), D8 (Learning & Self-Improvement) |
| What They Evaluate | Does the brain retrieve the right memories? Does consolidation work? Does memory quality improve over time? |
| Evaluation Frequency | Weekly |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | Brain returns irrelevant results. Calendar noise drowns signal. No consolidation running. |
| 3-4 | Brain returns partially relevant results. Source-type weighting exists but is not tuned. Consolidation runs but doesn't reduce noise. |
| 5-6 | Brain reliably returns relevant memories for people, projects, and events. Consolidation archives stale memories. Entity resolution handles common variants. |
| 7-8 | Brain anticipates context needs. Graph-enhanced retrieval works. Contradiction detection flags conflicts. Memory quality improves measurably month-over-month. |
| 9-10 | Brain is a competitive advantage. Retrieval feels prescient. Consolidation produces genuine semantic insights. Zero duplicate entities. |

**Evaluation Questions:**
1. Search for "Mike's family" -- do profile/semantic facts appear before calendar events? (Y/N + rank position)
2. How many active memories exist vs. 30-day target of <50K? (count)
3. Did nightly consolidation run every night this week? (days out of 7)
4. Entity duplicate rate: sample 10 entities, how many have duplicates? (%)
5. Correction capture: were any corrections stored as procedural memories this week? (count)

---

#### Panelist 2: Conversation Designer -- "The Therapist"

| Field | Value |
|-------|-------|
| Susan Agent | Conversation Designer (product group) |
| Panel Role | Conversation Quality Assessor |
| Domains Covered | D7 (Conversation Quality), D3 (Intent Understanding) |
| What They Evaluate | Does Jake sound like Jake? Does intent classification work? Are responses useful on the first try? |
| Evaluation Frequency | Weekly |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | Responses are generic. Personality inconsistent. Frequent wrong-tool usage. Most requests need correction. |
| 3-4 | Jake's voice is present but breaks under tool output. Intent misclassification >30%. Brain injection is indiscriminate. |
| 5-6 | Jake sounds like Jake consistently. Intent classification >80% accurate. Brain injection is selective by intent type. Correction rate <15%. |
| 7-8 | Responses feel personal and contextual. Multi-step requests decompose correctly. Error recovery is graceful and in-character. Correction rate <8%. |
| 9-10 | Conversations feel like talking to a brilliant friend who knows your entire life. Zero personality breaks. Intent is anticipated before Mike finishes typing. |

**Evaluation Questions:**
1. Sample 10 conversations from this week: how many maintained Jake's personality throughout? (count/10)
2. How many requests required correction ("no I meant...")? (count + rate)
3. Were any tool failures exposed as raw errors instead of graceful recovery? (count)
4. Intent classification accuracy: sample 20 requests, how many were correctly categorized? (count/20)
5. Did selective brain injection work (intent-appropriate memories injected)? (Y/N + examples)

---

#### Panelist 3: AI Eval -- "The Professor"

| Field | Value |
|-------|-------|
| Susan Agent | AI Evaluation Specialist (engineering group) |
| Panel Role | Learning & Reasoning Assessor |
| Domains Covered | D8 (Learning & Self-Improvement), D11 (Cross-Company Intelligence) |
| What They Evaluate | Is Hermes getting smarter? Are feedback loops closing? Does cross-company intelligence produce real insights? |
| Evaluation Frequency | Weekly (scores), Monthly (deep assessment) |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | No learning happening. Same mistakes repeat. No telemetry. No cross-company signals. |
| 3-4 | Corrections are captured but don't change behavior. Usage analytics exist but aren't acted on. Cross-company data exists but isn't correlated. |
| 5-6 | Procedural memories measurably reduce repeat errors. Consolidation stats appear in brief. At least 1 cross-company insight per week. |
| 7-8 | Routing telemetry drives model selection improvements. Preference learning adapts response style. Cross-company patterns flagged proactively. |
| 9-10 | System demonstrably improves week-over-week on measured metrics. A/B testing runs on routing changes. Cross-company intelligence is a genuine strategic asset. |

**Evaluation Questions:**
1. How many procedural memories were created this week from corrections? (count)
2. Did any previously-captured correction prevent a repeat mistake this week? (Y/N + example)
3. Consolidation stats: memories promoted, archived, and deduplicated this week? (counts)
4. Was any cross-company insight surfaced in briefs or responses? (Y/N + example)
5. Is there measurable improvement on any metric vs. last week? (metric + delta)

---

### HANDS (Action Execution)

These three panelists evaluate whether Hermes can actually DO things in the real world on Mike's behalf.

---

#### Panelist 4: Forge -- "The Mechanic"

| Field | Value |
|-------|-------|
| Susan Agent | Forge (engineering group) |
| Panel Role | Action Execution Assessor |
| Domains Covered | D5 (Action Execution), D15 (Delegation & Workflow Chains) |
| What They Evaluate | Can Jake take real-world actions? Do actions execute correctly? Do multi-step workflows complete? |
| Evaluation Frequency | Weekly |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | Read-only assistant. Cannot send email, create events, set reminders, or take any real-world action. |
| 3-4 | 1-2 action types work (e.g., Telegram messages, reminders). No confirmation flow. No undo. No workflow chains. |
| 5-6 | 5+ action types operational. 3-tier safety model (auto/confirm/approve) works. Audit trail exists. Simple 2-step workflows succeed. |
| 7-8 | All 7 core actions work reliably. Multi-step workflows ("research X, draft brief, send to Ellen") execute end-to-end. Background tasks report progress. |
| 9-10 | Action system is bulletproof. Complex delegation chains complete autonomously. Undo works. Mike trusts it with financial-adjacent actions. |

**Evaluation Questions:**
1. How many distinct action types are operational? (count of: send_email, create_event, set_reminder, send_telegram, create_github_issue, update_notion, draft_outreach)
2. Were any actions attempted this week? Success rate? (attempted / succeeded)
3. Did the confirmation flow work correctly for Tier 2 actions? (Y/N + count)
4. Were any multi-step workflows attempted? Did they complete? (count + completion rate)
5. Were any unintended actions executed (false positives)? (count -- target: 0)

---

#### Panelist 5: Atlas -- "The Architect"

| Field | Value |
|-------|-------|
| Susan Agent | Atlas (engineering group) |
| Panel Role | Infrastructure & Integration Assessor |
| Domains Covered | D6 (Bot Unification), D13 (Voice & Multi-Modal) |
| What They Evaluate | Is the architecture unified? Does routing between backends work? Are new modalities (voice, documents) functional? |
| Evaluation Frequency | Weekly |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | Multiple disconnected bots. User must choose which bot to talk to. No shared state. |
| 3-4 | Primary bot handles most requests. Routing to secondary backends exists but is fragile. No conversation continuity across paths. |
| 5-6 | Single entry point ("Jake") handles all requests. Routing is invisible. Conversation state persists across routing paths. Graceful degradation when Mac is off. |
| 7-8 | Unified bot handles text, voice messages, and document forwarding. Routing is intelligent (fast path vs. deep path). Background task queuing works. |
| 9-10 | Multi-modal assistant that seamlessly handles text, voice, documents, and images through one identity. Architecture is extensible to new channels (Slack, web). |

**Evaluation Questions:**
1. How many bots does Mike currently interact with for different purposes? (count -- target: 1)
2. Is routing between Hermes and ClaudeBirchBot invisible to Mike? (Y/N)
3. Does conversation context carry across routing paths? (test: start topic on one path, continue on another)
4. What happens when Mac is off? (degrades gracefully / fails / unknown)
5. Can Mike send voice messages or documents and get useful responses? (Y/N per modality)

---

#### Panelist 6: Shield -- "The Guardian"

| Field | Value |
|-------|-------|
| Susan Agent | Shield (orchestration group) |
| Panel Role | Security & Safety Assessor |
| Domains Covered | D9 (Security & Privacy) |
| What They Evaluate | Is personal data protected? Are context boundaries enforced? Is the action safety model working? |
| Evaluation Frequency | Bi-weekly (every 2 weeks) |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | API keys in plaintext. No PII classification. No access controls. No audit log. |
| 3-4 | API keys have basic protection. Some sensitivity tagging exists. No context boundaries between work/personal/family. |
| 5-6 | Data sensitivity tagging on all memories. Context boundaries enforce work/personal separation. API key rotation tracked. Basic audit log. |
| 7-8 | Family members can safely use Jake without seeing work data (tested). Full audit trail. Action safety tiers prevent unauthorized execution. |
| 9-10 | Enterprise-grade security. Encrypted sensitive memories. Automatic anomaly detection on access patterns. Quarterly penetration testing. |

**Evaluation Questions:**
1. Are all 19 API keys stored securely (not in plaintext dotfiles)? (Y/N)
2. Do brain memories have sensitivity tags (public/personal/work/family)? (% tagged)
3. Could a query from a family member surface Oracle Health data? (test result)
4. Is there an audit log of brain queries? (Y/N + coverage %)
5. Has any Tier 2+ action executed without confirmation? (count -- target: 0)

---

### FEET (Movement & Delivery)

These three panelists evaluate whether Hermes reaches Mike at the right time, in the right way, and reliably.

---

#### Panelist 7: Pulse -- "The Vital Signs Monitor"

| Field | Value |
|-------|-------|
| Susan Agent | Pulse (engineering group) |
| Panel Role | Reliability & Observability Assessor |
| Domains Covered | D10 (Reliability & Observability) |
| What They Evaluate | Is the system up? Are failures detected and recovered? Does Mike ever discover problems before the system does? |
| Evaluation Frequency | Weekly |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | No monitoring. Silent failures. Mike discovers problems days later. No health checks. |
| 3-4 | Basic health checks exist. Some failure alerts. But recovery is manual and slow. |
| 5-6 | All components monitored. Daily health report via Telegram. Auto-recovery handles common failures (Mail.app timeout). MTTD < 15 minutes. |
| 7-8 | Self-healing system. Error budget tracking. Cron monitoring with expected vs. actual. MTTD < 5 minutes. MTTR < 5 minutes for common failures. |
| 9-10 | System predicts failures before they happen. Zero silent failures. Uptime > 99.5%. Mike never discovers a problem the system didn't already flag. |

**Evaluation Questions:**
1. How many cron jobs ran successfully this week vs. expected? (actual / expected)
2. Were any failures detected by the system before Mike noticed? (count)
3. Were any failures discovered by Mike before the system? (count -- target: 0)
4. Mean time to detect failure this week? (minutes)
5. Did the daily health report deliver every day? (days / 7)

---

#### Panelist 8: Steve -- "The Chief of Staff"

| Field | Value |
|-------|-------|
| Susan Agent | Steve (orchestration group) |
| Panel Role | Proactive Intelligence Assessor |
| Domains Covered | D4 (Proactive Intelligence), D14 (Smart Notifications) |
| What They Evaluate | Does Jake anticipate Mike's needs? Are notifications smart, not noisy? Does the morning brief contain real intelligence? |
| Evaluation Frequency | Weekly |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | Template-driven briefs. No anticipatory behavior. Fixed-time cron notifications with no intelligence. |
| 3-4 | Briefs include some brain-sourced content. Meeting prep exists but is inconsistent. Notifications are time-based, not event-based. |
| 5-6 | Morning brief has 3+ brain-sourced insights. Meeting prep arrives for all meetings. Notifications are urgency-scored. DND respected during meetings. |
| 7-8 | Proactive nudges ("you said you'd send that by Friday"). Pattern mining surfaces weekly insights. <5 push notifications/day, 90%+ acted on. Stale commitment detection works. |
| 9-10 | Jake anticipates needs before Mike thinks of them. Notification timing feels psychic. Weekly pattern report reveals genuinely non-obvious insights. |

**Evaluation Questions:**
1. How many brain-sourced insights appeared in morning briefs this week? (count per brief, average)
2. What % of scheduled meetings got prep material delivered in advance? (%)
3. How many proactive nudges were sent? How many were useful (Mike acted on them)? (sent / useful)
4. Total push notifications this week? (count -- target: <35/week)
5. Were any notifications sent during calendar-blocked time? (count -- target: 0)

---

#### Panelist 9: Mira -- "The Empath"

| Field | Value |
|-------|-------|
| Susan Agent | Mira (product group) |
| Panel Role | User Experience & Personal Life Assessor |
| Domains Covered | D12 (Family & Personal), D7 (Conversation Quality -- UX side) |
| What They Evaluate | Does using Hermes feel good? Does Jake handle personal life well? Would Mike recommend this experience to someone? |
| Evaluation Frequency | Weekly |

**Scoring Criteria (1-10):**

| Score | Meaning |
|-------|---------|
| 1-2 | Using Hermes is frustrating. Personal life is ignored. Mike feels like he's managing the assistant instead of the reverse. |
| 3-4 | Hermes handles basic personal requests. Family data exists but isn't surfaced proactively. UX has rough edges (wrong tools, retries, raw errors). |
| 5-6 | Family events in morning brief. Birthday reminders work. Schedule conflict detection between work and family. Mike interacts daily without frustration. |
| 7-8 | Jake feels like a genuine partner. Family coordination is seamless. Jacob could ask about recruiting. Experience is smooth enough to demo to friends. |
| 9-10 | Mike cannot imagine going back to life without Hermes. Family and personal life are managed as well as work. The system has become genuinely indispensable. |

**Evaluation Questions:**
1. Were any family birthdays or events missed this week that Jake should have caught? (count -- target: 0)
2. Did schedule conflict detection flag any work/family overlaps? (count + were they real?)
3. On a 1-5 scale, how frustrating was the typical interaction this week? (self-assessment proxy: error count / total interactions)
4. Did any response this week make Mike feel like Jake "gets it" (used personal context effectively)? (Y/N + example)
5. Net Promoter question: Would Mike recommend this week's Hermes experience to a friend? (Y/N + why)

---

## Composite Hermes Health Score (HHS)

### Weighting Model

Weights reflect what matters most at the current build phase. They shift as Hermes matures.

**Phase 1-3 weights (current -- infrastructure focus):**

| Category | Weight | Rationale |
|----------|--------|-----------|
| Brain | 40% | Memory and conversation quality are the foundation. If retrieval is bad, nothing else matters. |
| Hands | 20% | Actions are being built. Weight increases as action capabilities come online. |
| Feet | 40% | Reliability and proactive behavior determine whether Mike uses the system at all. |

**Phase 4-6 weights (target -- action focus):**

| Category | Weight | Rationale |
|----------|--------|-----------|
| Brain | 30% | Brain should be mature. Maintenance mode. |
| Hands | 40% | Action execution is the difference between "useful" and "indispensable." |
| Feet | 30% | Delivery should be reliable by now. |

**Phase 7-9 weights (mature -- experience focus):**

| Category | Weight | Rationale |
|----------|--------|-----------|
| Brain | 25% | Fully autonomous learning and consolidation. |
| Hands | 35% | Full action palette, workflow chains. |
| Feet | 40% | The experience layer is what separates good from great. |

### Score Calculation

```
Category Score = average of 3 panelist scores in that category

HHS = (Brain_avg * Brain_weight) + (Hands_avg * Hands_weight) + (Feet_avg * Feet_weight)
```

All scores on a 1-10 scale. HHS is a single number from 1.0 to 10.0.

### HHS Interpretation

| HHS Range | Grade | Interpretation | Action |
|-----------|-------|----------------|--------|
| 1.0 - 2.0 | F | System is a liability. Mike works around it more than with it. | Stop feature work. Fix fundamentals. |
| 2.1 - 3.5 | D | Infrastructure exists but experience is poor. Mike uses it only when he remembers to. | Focus on reliability and retrieval quality. |
| 3.6 - 5.0 | C | Useful daily tool with notable gaps. Mike uses it but doesn't depend on it. | Close the highest-delta gaps. |
| 5.1 - 6.5 | B | Reliable assistant. Mike starts most days with Jake. Some action capability. | Expand action palette and proactive intelligence. |
| 6.6 - 8.0 | A | Essential tool. Mike would notice immediately if it went down. | Polish, cross-company intelligence, family features. |
| 8.1 - 9.0 | A+ | Indispensable. Competitive with commercial PA products. | Voice, multi-modal, network expansion. |
| 9.1 - 10.0 | S | Best-in-class personal AI. Mike cannot imagine life without it. | Maintain, scale to family, productize. |

### Current Estimated HHS (2026-03-21 Baseline)

| Panelist | Agent | Score | Rationale |
|----------|-------|-------|-----------|
| 1. Knowledge Engineer | Brain | 3/10 | Brain stores well but retrieves poorly. Calendar drowns signal. |
| 2. Conversation Designer | Brain | 2/10 | Personality breaks under tools. Intent classification absent. |
| 3. AI Eval | Brain | 1/10 | No learning loops. No telemetry. No cross-company intel. |
| 4. Forge | Hands | 1/10 | Read-only. No action execution. No workflows. |
| 5. Atlas | Hands | 2/10 | 3 disconnected bots. No unified routing. |
| 6. Shield | Hands | 1/10 | Plaintext keys. No boundaries. No audit. |
| 7. Pulse | Feet | 1/10 | No monitoring. Silent failures. |
| 8. Steve | Feet | 2/10 | Template briefs only. No proactive intelligence. |
| 9. Mira | Feet | 2/10 | Frustrating UX. Family data exists but unsurfaced. |

```
Brain_avg  = (3 + 2 + 1) / 3 = 2.0
Hands_avg  = (1 + 2 + 1) / 3 = 1.3
Feet_avg   = (1 + 2 + 2) / 3 = 1.7

HHS = (2.0 * 0.40) + (1.3 * 0.20) + (1.7 * 0.40)
    = 0.80 + 0.26 + 0.68
    = 1.74 / 10.0 (Grade: F)
```

**Baseline HHS: 1.7 / 10.0**

This is consistent with the 10X assessment's 1.8/5.0 aggregate maturity (which maps to 3.6/10 on a capability scale, but the HHS weights experience over infrastructure, pulling the score down).

---

## Weekly Evaluation Template

```markdown
# Hermes Weekly Review — Week of [DATE]

## BRAIN

### P1: Knowledge Engineer (Memory Quality)
- [ ] "Mike's family" search returns profile facts first: Y/N (rank: ___)
- [ ] Active memory count: ___ (target: <50K)
- [ ] Nightly consolidation ran: ___/7 nights
- [ ] Entity duplicate rate (sample 10): ___%
- [ ] Corrections captured as procedural: ___ count
- **Score: ___/10**
- **Notes:**

### P2: Conversation Designer (Conversation Quality)
- [ ] Personality consistency (sample 10 convos): ___/10
- [ ] Correction rate ("no I meant"): ___ / ___ total requests = ___%
- [ ] Raw error exposures: ___ count
- [ ] Intent classification accuracy (sample 20): ___/20
- [ ] Selective brain injection working: Y/N
- **Score: ___/10**
- **Notes:**

### P3: AI Eval (Learning & Reasoning)
- [ ] New procedural memories from corrections: ___ count
- [ ] Repeat error prevented by correction capture: Y/N (example: ___)
- [ ] Consolidation stats: ___ promoted, ___ archived, ___ deduped
- [ ] Cross-company insight surfaced: Y/N (example: ___)
- [ ] Measurable improvement vs last week: ___ (metric: ___, delta: ___)
- **Score: ___/10**
- **Notes:**

---

## HANDS

### P4: Forge (Action Execution)
- [ ] Operational action types: ___ / 7
- [ ] Actions attempted / succeeded: ___ / ___
- [ ] Tier 2 confirmation flow correct: Y/N (___ count)
- [ ] Multi-step workflows attempted / completed: ___ / ___
- [ ] Unintended actions: ___ (target: 0)
- **Score: ___/10**
- **Notes:**

### P5: Atlas (Infrastructure & Integration)
- [ ] Bots Mike interacts with: ___ (target: 1)
- [ ] Routing invisible to Mike: Y/N
- [ ] Cross-path conversation continuity: Y/N
- [ ] Mac-off behavior: graceful / fail / unknown
- [ ] Voice / document support: Y/N per modality
- **Score: ___/10**
- **Notes:**

### P6: Shield (Security & Safety) [bi-weekly]
- [ ] API keys secured: Y/N
- [ ] Memory sensitivity tagging: ___% tagged
- [ ] Family query isolation test: PASS/FAIL
- [ ] Audit log coverage: ___%
- [ ] Unauthorized action execution: ___ (target: 0)
- **Score: ___/10**
- **Notes:**

---

## FEET

### P7: Pulse (Reliability)
- [ ] Cron success rate: ___ / ___ expected
- [ ] System-detected failures: ___ count
- [ ] Mike-detected failures: ___ (target: 0)
- [ ] Mean time to detect: ___ minutes
- [ ] Daily health report delivered: ___/7 days
- **Score: ___/10**
- **Notes:**

### P8: Steve (Proactive Intelligence)
- [ ] Brain-sourced insights per brief: ___ avg
- [ ] Meeting prep delivery rate: ___%
- [ ] Proactive nudges sent / useful: ___ / ___
- [ ] Total push notifications: ___ (target: <35/week)
- [ ] Notifications during blocked time: ___ (target: 0)
- **Score: ___/10**
- **Notes:**

### P9: Mira (User Experience)
- [ ] Missed family events: ___ (target: 0)
- [ ] Schedule conflicts detected: ___ (real: ___)
- [ ] Interaction frustration proxy: ___ errors / ___ total = ___%
- [ ] "Jake gets it" moment: Y/N (example: ___)
- [ ] Would recommend this week's experience: Y/N (why: ___)
- **Score: ___/10**
- **Notes:**

---

## COMPOSITE SCORE

| Category | Panelists | Avg | Weight | Weighted |
|----------|-----------|-----|--------|----------|
| Brain | P1:___ P2:___ P3:___ | ___ | 40% | ___ |
| Hands | P4:___ P5:___ P6:___ | ___ | 20% | ___ |
| Feet | P7:___ P8:___ P9:___ | ___ | 40% | ___ |
| **HHS** | | | | **___/10** |

**Grade:** ___
**Trend vs last week:** UP / FLAT / DOWN (delta: ___)
**Top improvement this week:**
**Top regression this week:**
**#1 priority for next week:**
```

---

## Panel-to-Phase Mapping

Each panelist's score is most affected by specific 9-phase milestones. This maps which build phases move which panelist scores.

| Panelist | Primary Phase Impact | Secondary Phase Impact |
|----------|---------------------|----------------------|
| P1: Knowledge Engineer | Phase 2 (Brain) -- memory quality | Phase 4A (Spine) -- source weighting |
| P2: Conversation Designer | Phase 4A (Spine) -- intent routing | Phase 6 (Employees) -- personality guards |
| P3: AI Eval | Phase 7 (Immune) -- learning loops | Phase 4A (Spine) -- routing telemetry |
| P4: Forge | Phase 5 (Hands) -- action execution | Phase 8 (Nervous) -- workflow chains |
| P5: Atlas | Phase 5A (Bot Unification) | Phase 3 (Eyes) -- multi-modal |
| P6: Shield | Phase 7 (Immune) -- security | Phase 6 (Employees) -- access control |
| P7: Pulse | Phase 7 (Immune) -- monitoring | Phase 3 (Eyes) -- ingestion health |
| P8: Steve | Phase 4B (Notifications) | Phase 4A (Spine) -- priority engine |
| P9: Mira | Phase 6 (Employees) -- family | Phase 9 (Network) -- shared access |

---

## HHS Target Trajectory

| Date | Target HHS | Grade | Key Milestone |
|------|-----------|-------|---------------|
| 2026-03-21 (baseline) | 1.7 | F | Infrastructure built, experience broken |
| After Phase 4A (Spine) | 3.5 | D | Intent routing + brain quality + priority engine |
| After Phase 4B (Notifications) | 4.5 | C | Smart notifications + proactive briefs |
| After Phase 5 (Hands + Unification) | 6.0 | B | Action execution + single bot + confirmation flows |
| After Phase 6 (Employees) | 7.0 | A | Family features + personality guards + specialized agents |
| After Phase 7 (Immune) | 8.0 | A+ | Monitoring + security + learning loops |
| After Phase 8-9 (Nervous + Network) | 9.0 | S | Workflow chains + voice + family access |

---

## Standing Orders for the Panel

1. **Every Friday**, the panel produces scores. This is non-negotiable. Even if nothing changed, the score is recorded to track stability.
2. **Scores must be evidence-based.** Every score requires at least 1 specific example or data point from that week. "It felt better" is not a score justification.
3. **The lowest panelist score is the most important signal.** A system is only as strong as its weakest dimension. The lowest score gets called out explicitly every week.
4. **Trend matters more than absolute score.** A 3 that was a 2 last week is better than a 5 that was a 6 last week.
5. **The panel does not build.** The panel evaluates. Build decisions are made by Susan and the phase owners. The panel's job is to tell the truth about where things stand.
