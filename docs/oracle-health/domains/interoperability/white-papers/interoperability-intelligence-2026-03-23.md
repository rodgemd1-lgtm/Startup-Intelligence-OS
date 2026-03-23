# Oracle Health: Interoperability Domain Intelligence Report
**Date**: March 23, 2026
**Classification**: Internal - M&CI Team
**Prepared by**: Jake, Oracle Health M&CI Intelligence Analyst
**Review Cycle**: Weekly refresh recommended given regulatory velocity

---

## Executive Summary

The interoperability landscape is undergoing its most significant structural transformation since the passage of the 21st Century Cures Act. As of Q1 2026, three converging forces are redefining who wins and who gets left behind: the explosive growth of TEFCA, CMS enforcement deadlines bearing down on payers, and the commercial collapse of Mirth Connect's open-source community.

Oracle Health is positioned advantageously but must move with urgency. In November 2025, Oracle Health Information Network became a Designated Qualified Health Information Network (QHIN) under TEFCA — available to all existing customers at no cost with zero setup. Meanwhile, TEFCA itself achieved a 50x volume surge in just 13 months, growing from approximately 10 million health records exchanged in January 2025 to nearly 500 million by February 2026. This is not incremental growth; it is infrastructure tipping point behavior.

The regulatory clock is also ticking for payers. The CMS-0057-F Final Rule activated public reporting requirements on January 1, 2026, with full FHIR-compliant Prior Authorization APIs mandated by January 1, 2027. This creates an 8-month urgency window in which Oracle's QHIN designation and payer connectivity story is directly monetizable.

On the competitive front, the Mirth Connect commercialization shock of March 2025 — when NextGen ended the open-source licensing model at version 4.5.2 — has left approximately one-third of public HIEs in the US evaluating their integration engine strategy. Two open-source forks (BridgeLink and OIE) have emerged, but neither provides enterprise-grade TEFCA connectivity. This is a displacement window that Oracle can capture with Oracle Health Seamless Exchange.

The HL7 FHIR compliance market was valued at $2.3 billion in 2025 and is projected to reach $2.6 billion in 2026 before scaling to $8.6 billion by 2036 (CAGR ~14%). The HIE market is on a parallel trajectory: $2.49 billion in 2026, growing at 8.7-9.7% CAGR through 2035. Market forces and regulatory forces are aligned.

The single most important signal: TEFCA has crossed the adoption chasm. With Epic mandating its customer base transition to TEFCA and Carequality actively pivoting its framework to align with TEFCA's SOPs, the entire ecosystem is reorganizing around the QHIN model. Oracle's QHIN designation is not a feature — it is now a prerequisite for competitive survival and a direct revenue driver.

---

## 1. Market Overview

### 1.1 FHIR Adoption Rates

HL7 FHIR has crossed from "emerging standard" to "baseline expectation" in 2026. Key indicators:

- FHIR Compliance Market: $2.3B (2025) → $2.6B (2026) projected → $8.6B (2036) at ~14% CAGR
- Q2 2026 CMS goals require applications to formally adopt FHIR APIs
- The "big three" EHR/cloud ecosystem (Epic, Oracle Health, Microsoft Azure) have each committed to FHIR as a core architectural pillar
- FHIR R4 is now the minimum expected version; FHIR R4B adoption is accelerating for newer use cases
- USCDI v7 released January 29, 2026 added 29 new data elements for adverse event reporting, nutrition exchanges, and quality improvement — each requiring FHIR support

The market inflection point: The industry has officially transitioned from the "innovation" phase to the "large-scale implementation" phase. Organizations that have built FHIR infrastructure are now operationalizing it. Those that have not are facing accelerating compliance costs.

### 1.2 Data Exchange Volumes

TEFCA volume statistics (source: HHS, February 2026):
- Records exchanged via TEFCA: ~500 million (cumulative to Feb 2026)
- Comparison: ~10 million records in January 2025
- Growth factor: ~50x in 13 months

HIE market data:
- Global HIE market: $1.7B (2024) → $2.49B (2026) → projected $5.5B+ (2034)
- US market dominates at roughly 40% of global share
- CAGR: 8.7-9.7% depending on data source (2026-2035)

Carequality legacy network: exchanges approximately 1 billion clinical documents annually but is actively transitioning toward the TEFCA framework. The network's future without Epic's footprint is structurally uncertain.

### 1.3 Regulatory Milestones Calendar

| Date | Milestone | Impact |
|------|-----------|--------|
| Jan 29, 2026 | USCDI v7 released (29 new elements) | EHR certification update requirements |
| Jan 1, 2026 | CMS-0057-F public reporting begins | Payer compliance clock started |
| Feb 11, 2026 | HHS announces TEFCA ~500M records | Market validation signal |
| Q1 2026 | CMS Interoperability Framework first milestone | Voluntary but competitive signal |
| Q2 2026 | CMS FHIR adoption deadline for app developers | Developer ecosystem requirements tighten |
| Sept 30, 2026 | Azure API for FHIR retirement (Microsoft) | Customer migration window for Oracle |
| Jan 1, 2027 | CMS-0057-F: All Prior Auth APIs must be live | Hard payer enforcement deadline |

---

## 2. Regulatory Landscape

### 2.1 21st Century Cures Act — Current State

The Cures Act's interoperability provisions are now fully in the enforcement phase. Key developments:

**Information Blocking Enforcement**: ASTP/ONC issued its first "notices of potential non-conformity" to health IT developers under 45 CFR 170.580. This marks a shift from passive compliance monitoring to active enforcement. Healthcare IT developers that restrict or delay access to electronic health information now face direct regulatory action, not just scrutiny.

**HTI-5 Proposed Rule (Deregulatory)**: Filed December 29, 2025 in the Federal Register. Proposes removing 34 and revising 7 of the current 60 certification criteria. Projected savings: $1.53 billion in developer compliance costs. Important implication: while the intent is deregulatory, it signals that ONC is streamlining — not weakening — the compliance framework. Vendors who built around outdated criteria face transition costs.

**USCDI Evolution**: Version 7 extends the minimum required data set. Each new version adds pressure on EHR vendors to certify support, creating ongoing upgrade cycles that favor vendors with built-in FHIR pipelines.

### 2.2 TEFCA — The National Interoperability Backbone

TEFCA is no longer theoretical. It is operating at scale and accelerating.

**Current QHINs** (as of Q1 2026): eHealth Exchange, Carequality (transitioning into TEFCA alignment), CommonWell (now under ELLKAY infrastructure), Kno2, MedAllies, Konza, and Oracle Health Information Network (designated November 2025).

**Epic's TEFCA mandate** is the most consequential force in the landscape: Epic called for all customers to commit to TEFCA participation by end of 2024 and complete the transition by end of 2025. Given Epic's 30-35% EHR market share, this mandate is effectively reshaping the entire clinical data exchange ecosystem. Organizations that are not TEFCA-connected are increasingly cut off from Epic's patient data.

**Carequality's pivot**: Carequality announced alignment with TEFCA SOPs, essentially transitioning from a parallel framework to a feeder into TEFCA. The relationship has inverted — TEFCA now influences Carequality rather than the reverse. This creates uncertainty for organizations that relied on Carequality as their primary exchange path.

**Individual Access Services (IAS)**: TEFCA now mandates IAS, enabling patients to directly access their own data — a use case that had minimal adoption under Carequality. This expands the patient portal battleground.

### 2.3 CMS-0057-F — The Payer Enforcement Timeline

The CMS Interoperability and Prior Authorization Final Rule is the most monetizable regulatory event for Oracle in 2026:

- **January 1, 2026**: Public reporting on Prior Authorization metrics began for impacted payers
- **January 1, 2027**: All Prior Authorization APIs must be live and operational
- **Required APIs**: Patient Access API, Provider Directory API, Prior Authorization API (new), and care coordination APIs — all FHIR R4 compliant
- **Payer scope**: Medicare Advantage, Medicaid, CHIP FFS, and QHP issuers on the Exchanges

This creates a direct sales motion: any Oracle customer in the payer space needs compliant APIs by January 2027. Oracle's QHIN designation and Seamless Exchange capability are the fastest path to compliance.

**Prior Authorization automation**: ONC's HTI-4 Final Rule (electronic Prior Auth standards) projected $19.2 billion in administrative cost savings over 10 years. This is a compelling ROI narrative for payer and provider sales.

---

## 3. Competitive Landscape

### 3.1 Competitive Matrix

| Vendor | Core Interop Capability | TEFCA Position | FHIR Maturity | Threat Level | Momentum |
|--------|------------------------|----------------|----------------|--------------|----------|
| **Epic** | 40,000+ site network, Carequality backbone, MyChart | QHIN-equivalent via direct participation | R4 full support | HIGH | Accelerating |
| **Microsoft Azure** | Azure Health Data Services FHIR Service, AI compliance layers | FHIR API service layer (not direct QHIN) | R4/R4B via Azure FHIR service | MEDIUM | Transitioning (legacy retirement Sept 2026) |
| **AWS HealthLake** | FHIR-native data lake, AI/ML analytics | Not a QHIN; infrastructure layer | R4 full support | MEDIUM | Steady |
| **Rhapsody (Lyniate)** | Best-in-KLAS integration engine, IDN-grade, multi-tenant locker architecture | Partner-dependent | Via channel transformations | MEDIUM | Stable |
| **Mirth Connect (NextGen)** | Most widely deployed HL7 engine (1/3 of US public HIEs) | Partner-dependent | R4 in Gold/Platinum tiers only | LOW-MEDIUM | Declining (commercialization shock) |
| **CommonWell/ELLKAY** | Legacy network, migrating to ELLKAY infrastructure | Designated QHIN | R4 | LOW | Uncertain transition |
| **Veradigm** | Ambulatory data, pharma analytics, practices | Limited | Moderate | LOW | Niche |

### 3.2 Epic — Primary Threat

Epic's interoperability strategy is sophisticated and aggressive. Their network advantage is compounding:

- Estimated 30-35% EHR market share in US hospitals
- Access to the largest single repository of longitudinal patient data in the US
- Forced TEFCA adoption by its customer base effectively sets the standard others must follow
- "Epic has more connections" is the most common objection Oracle faces — it is almost always true in raw count terms

Oracle's counter: Epic's network is very large, but it is also very Epic-centric. Data flowing through Epic's network is best served to Epic customers. Oracle's QHIN is designed for the multi-vendor, multi-network reality that most health systems actually live in. Oracle provides a neutral, federated exchange path that includes but does not depend on Epic connectivity.

### 3.3 Microsoft Azure — Infrastructure Competitor

Microsoft's play is not as a direct EHR competitor but as the cloud layer where interoperability happens. Key signal: **Azure API for FHIR is being retired September 30, 2026**, forcing existing customers to migrate to Azure Health Data Services. This is a 6-month disruption window for Oracle to position OCI + Seamless Exchange as an alternative to Azure Health Data Services for organizations evaluating their move.

Microsoft's strengths are identity management, M365 integration, SOC 2/ISO 27001/FedRAMP compliance layers, and AI workload compatibility. Their weakness is that they are infrastructure — they don't have patient context or clinical workflow integration the way Oracle does.

### 3.4 AWS HealthLake — Data Analytics Competitor

AWS HealthLake competes in the "FHIR data lake and analytics" layer. It is strong for organizations wanting to query population health data at scale. AWS is not a QHIN and has limited direct exchange capability. Their strength is elastic compute and ML tooling (SageMaker), making them appealing for research and population health use cases. They are weakest in real-time exchange and clinical workflow integration.

### 3.5 Rhapsody — Integration Engine Competitor

Rhapsody (Lyniate, formerly Orion Health) is the Best-in-KLAS integration engine for large IDNs. Its locker architecture provides full multi-tenant isolation across sites. Cost is high, and it is positioned as "enterprise overkill" for anything below 10-facility scale. Where Oracle Seamless Exchange is the right conversation at the EHR/network layer, Rhapsody is competing at the middleware layer. These two conversations sometimes overlap in large health system evaluations.

### 3.6 Mirth Connect — The Displacement Opportunity

On March 19, 2025, NextGen Healthcare ended open-source licensing for Mirth Connect at version 4.5.2.

- Mirth Connect currently powers approximately one-third of all public HIEs in the US
- The commercial pivot has created two OSS forks: BridgeLink (Innovar Healthcare, AWS-native) and OIE (community-governed)
- Neither fork provides TEFCA connectivity or integrated QHIN access
- Organizations evaluating away from Mirth are asking: "What do we replace it with, and how do we get TEFCA?"

This is Oracle's clearest displacement opportunity in 2026: offer Oracle Health Seamless Exchange + QHIN connectivity as the "Mirth replacement that also solves TEFCA" in a single motion.

Migration realities: 100-300 Mirth channels take 6-12 months to migrate. Organizations evaluating now will be in implementation in Q3-Q4 2026, timing perfectly with the January 2027 CMS deadline.

---

## 4. Oracle Health Interoperability Capabilities

### 4.1 TEFCA QHIN Designation

Oracle Health Information Network, Inc. received QHIN designation on November 20, 2025 — making Oracle one of the few EHR vendors with a direct QHIN designation. Key advantage: this is free for existing Oracle Health customers with no setup, no configuration, no consulting engagement required. Customers activate via the Oracle Health Connection Hub with an opt-in to the Terms of Participation.

This positions Oracle as a single point of connectivity: rather than hospitals managing separate CommonWell, Carequality, and eHealth Exchange connections, Oracle QHIN provides unified access to the TEFCA ecosystem from within the existing Oracle Health EHR workflow.

### 4.2 Oracle Health Seamless Exchange

The core exchange capability:
- Aggregates patient data from multiple source networks
- Cleanses and deduplicates incoming records
- Integrates directly into Oracle Health Foundation EHR and next-gen Oracle Health EHR
- Managed via Oracle Health Connection Hub (governance, auditing, access reporting)

Infrastructure: powered by Oracle Cloud Infrastructure (OCI), providing military-grade security and high availability. This is a meaningful differentiator against legacy on-prem exchange solutions.

### 4.3 Oracle Health Connection Hub

The management and governance layer for interoperability:
- Single pane for managing exchange services across networks
- Governance and access control
- Auditing and compliance reporting
- Entry point for QHIN participation

### 4.4 AI-Interoperability Integration

Oracle's differentiation is that interoperability is not a standalone product — it is the data foundation for the Clinical AI Agent and the broader Oracle Health intelligence stack:
- Clinical AI Agent: >40% reduction in documentation time for clinicians
- Nearly 10,000 clinicians currently using the Clinical AI Agent
- 100+ oncology sites collaborating on specialty workflows
- AI-native EHR certified by HHS ASTP/ONC (2025)
- Multimodal AI: considers real-time CMS rules, medical literature, and market data — not just historical EHR records
- Partnership with OpenAI for patient portal conversational AI

Oracle's interoperability story is: better data exchange → better AI → better clinical outcomes. This is a differentiated narrative that neither Rhapsody nor Microsoft can match end-to-end.

### 4.5 Oracle Health Network (Formerly CommonWell Health Alliance)

Note: CommonWell Health Alliance, which Oracle (then Cerner) co-founded, has been migrating its operational infrastructure to ELLKAY. Oracle has effectively separated its naming and network identity through the Oracle Health Information Network (QHIN) designation. This is a strategic repositioning that needs clear messaging in the field: Oracle's QHIN is the successor network identity, built on OCI, with TEFCA connectivity.

---

## 5. Strategic Opportunities

### Opportunity 1: The Mirth Connect Displacement Wave (6-Month Window)

Target: Any healthcare organization currently running Mirth Connect 4.5.x or earlier that now faces the NextGen commercial licensing decision.

Why now: March 2025 commercialization shock is still fresh. Organizations are mid-evaluation on integration engine strategy. The two OSS forks (BridgeLink, OIE) do not solve TEFCA. Oracle does.

Oracle's offer: Oracle Health Seamless Exchange + QHIN designation = one motion that replaces the integration engine AND delivers TEFCA compliance. No separate QHIN contracting needed.

Size of opportunity: Approximately one-third of US public HIEs run Mirth. Even 10% conversion represents significant ARR opportunity.

Action: Build an active pipeline campaign targeting known Mirth customers. Develop a Mirth-to-Oracle migration guide. Quantify ROI against NextGen commercial licensing costs.

### Opportunity 2: CMS-0057-F Payer Prior Authorization API Compliance (8-Month Runway)

Target: Medicare Advantage plans, Medicaid managed care organizations, CHIP plans, and QHP issuers who need Prior Authorization FHIR APIs live by January 1, 2027.

Why now: January 2027 is 9 months away. Implementation cycles for FHIR-compliant APIs typically run 6-12 months. Payers who have not started are already behind.

Oracle's offer: Oracle Health QHIN connectivity + FHIR API compliance consulting + Connection Hub governance as the fastest path to CMS-0057-F compliance.

Message: "The January 2027 deadline is 9 months away. Oracle can get you compliant faster than any alternative because our QHIN infrastructure is already live and your team activates via Connection Hub."

Action: Develop a "CMS-0057-F Compliance Package" with defined implementation milestones mapped to the regulatory calendar. Target payer-side sales motions immediately.

### Opportunity 3: Azure API for FHIR Migration Refugees (Sept 30, 2026 Deadline)

Target: Organizations currently on Microsoft's Azure API for FHIR that must migrate to Azure Health Data Services by September 30, 2026.

Why now: Microsoft announced this retirement, and the migration path to Azure Health Data Services requires technical rework. Some organizations will evaluate whether the migration effort warrants switching to a different infrastructure provider entirely.

Oracle's offer: OCI-based FHIR infrastructure + Oracle Health QHIN as the migration destination, with built-in EHR integration that Azure simply cannot provide.

Message: "You're already migrating your FHIR infrastructure. Don't migrate to more Azure — migrate to clinical infrastructure that actually knows your patients."

Action: Create a targeted campaign for Azure API for FHIR customers with a side-by-side comparison of Azure Health Data Services vs. OCI + Oracle Health Seamless Exchange.

---

## 6. Risks & Mitigation

### Risk 1: Epic's Network Gravity Becomes Decisive

**Risk**: Epic's TEFCA mandate and 30-35% market share means that Epic's TEFCA connections become the de facto standard. Organizations outside the Epic ecosystem find themselves looking at a diminished data set.

**Mitigation**: Oracle must differentiate on breadth and neutrality. Oracle's QHIN connects to ALL QHINs — eHealth Exchange, Carequality-aligned networks, CommonWell/ELLKAY — not just Epic-connected sites. Position Oracle as the "Switzerland of interoperability": neutral, federated, vendor-agnostic exchange.

### Risk 2: Regulatory Deregulation Reduces Compliance Urgency

**Risk**: HTI-5's removal of 34 certification criteria and the general HHS deregulatory posture under the current administration could slow compliance-driven purchase decisions.

**Mitigation**: Shift the sales narrative from compliance mandate to clinical outcomes and AI enablement. Interoperability investment's ROI story must be told through the Clinical AI Agent's 40%+ documentation reduction and the cost savings from eliminating duplicate testing — not just "you have to do this by the deadline."

### Risk 3: Cloud Commoditization of FHIR Erodes Differentiation

**Risk**: AWS HealthLake and Azure Health Data Services are making FHIR APIs cheap and broadly available. Organizations may view basic FHIR connectivity as a commodity and resist paying Oracle-level pricing for what seems like "just another API."

**Mitigation**: Oracle's differentiation is not the FHIR API — it is the integrated clinical context. Oracle QHIN is embedded in the EHR, not bolted on. Emphasize the zero-setup, zero-cost activation for existing customers and the seamless integration with Oracle Clinical AI as features that cloud-only FHIR services fundamentally cannot replicate.

### Risk 4: CommonWell → ELLKAY Transition Creates Customer Confusion

**Risk**: CommonWell migrating to ELLKAY infrastructure creates confusion among customers who understood their Oracle/Cerner relationship to include CommonWell benefits. If customers don't understand that Oracle Health Information Network (QHIN) is the successor, they may see Oracle as having "lost" CommonWell.

**Mitigation**: Immediate internal enablement update to field teams on the Oracle Health Network naming and positioning. Clear messaging: Oracle QHIN > CommonWell in scope, coverage, and capability. CommonWell was a milestone; QHIN is the destination.

---

## Appendix: Data Sources

1. Oracle Health News — TEFCA QHIN Designation announcement (Nov 20, 2025)
   https://www.oracle.com/news/announcement/oracle-health-secures-tefca-qhin-designation-2025-11-20/

2. HHS Press Room — TEFCA reaches ~500M health records exchanged (Feb 11, 2026)
   https://www.hhs.gov/press-room/tefca-americas-national-interoperability-network-reaches-nearly-500-million-health-records-exchanged.html

3. Forbes Technology Council — Digital Health Depends On Interoperability (March 13, 2026)
   https://www.forbes.com/councils/forbestechcouncil/2026/03/13/digital-health-depends-on-interoperability-where-we-stand-and-whats-next-in-2026/

4. Business 2.0 News — Epic, Oracle & Microsoft Advance Health Tech Interop in 2026 (Feb 10, 2026)
   https://business20channel.tv/epic-systems-oracle-microsoft-advance-health-tech-interop-in-2026-10-02-2026

5. AccWire/WRAL — HL7 FHIR Compliance Market to Reach USD 8.6B by 2036 (March 12, 2026)
   https://markets.financialcontent.com/wral/article/accwirecq-2026-3-12-hl7-fhir-compliance-market-to-reach-usd-86-billion-by-2036

6. Beckers Hospital Review — AI's Next Act: How Oracle Health Sees 2026 Taking Shape
   https://www.beckershospitalreview.com/healthcare-information-technology/ais-next-act-how-oracle-health-sees-2026-taking-shape/

7. ConsultZen — Carequality and Epic TEFCA Transition Analysis
   https://consultzen.com/carequality-and-epic-tefca-transition-announcements-how-does-this-impact-nationwide-data-exchange/

8. NerdBot — Mirth Connect vs Rhapsody vs Cloverleaf vs Iguana in 2026 (March 18, 2026)
   https://nerdbot.com/2026/03/18/mirth-connect-vs-rhapsody-vs-cloverleaf-vs-iguana-choosing-the-right-hl7-integration-engine-in-2026/

9. Firerly Blog — CMS-0057-F Decoded: Must-have APIs for 2026-2027
   https://fire.ly/blog/cms-0057-f-decoded-must-have-apis-vs-nice-to-have-igs-for-2026-2027/

10. CMS — Interoperability and Prior Authorization Final Rule (CMS-0057-F)
    https://www.cms.gov/priorities/burden-reduction/overview/interoperability/policies-regulations/cms-interoperability-prior-authorization-final-rule-cms-0057-f

11. Precedence Research — Health Information Exchange Market Size 2025-2034
    https://www.precedenceresearch.com/health-information-exchange-market

12. CommonWell Health Alliance News Center
    https://www.commonwellalliance.org/news-center/commonwell-news/

13. Federal Register — HTI-5 ASTP/ONC Deregulatory Actions (Dec 29, 2025)
    https://www.federalregister.gov/documents/2025/12/29/2025-23896/health-data-technology-and-interoperability-astponc-deregulatory-actions-to-unleash-prosperity

14. EHRSource — Epic vs Oracle Health Full Comparison 2026
    https://ehrsource.com/compare/epic-vs-oracle-health/

---
*Document generated: March 23, 2026 | Next refresh: March 30, 2026*
*Jake — Oracle Health M&CI Intelligence Pipeline v1.0*
