# Startup Intelligence OS Department Gap Closure Wave

**Date:** 2026-03-12  
**Scope:** All core departments plus Job Studio training evaluation  
**Owner:** Jake

## Objective
Close the highest-leverage maturity gaps by attaching targeted public evidence to the weakest departments and training systems instead of collecting more undifferentiated data.

## Framing
The base corpus is no longer the primary blocker. We now have a completed local extraction pass, a large Oracle-derived training corpus, and a running Job Studio training factory. The remaining gap is uneven department coverage: several departments have structure but still lack dense, current, official reference layers.

## Current Gap Priorities

| Capability area | Current state | Target state | Maturity delta | Gap | Owner | Sequence | Success criteria |
|---|---|---|---:|---|---|---:|---|
| Talent & Org Design Studio | Wrapper exists, but role scorecards, hiring loops, and onboarding references are thin. | Reusable org blueprint, role scorecards, hiring loops, and onboarding packets grounded in official handbook sources. | 5.2 | More evidence than process today. | Susan | 1 | Official hiring/onboarding corpus ingested and usable in routed work. |
| Finance & Operating Cadence Studio | Cadence wrapper exists, but KPI, variance, and finance operating references are sparse. | Finance review packets and KPI-tree patterns backed by strong finance handbooks and startup-finance references. | 5.0 | Thin evidence and few reusable cadence packets. | Ledger | 2 | Finance source bundle exists with cadence-ready outputs. |
| Revenue & Growth Studio | Studio is defined, but offer/channel/proof references are not yet dense enough. | Growth system can pull offer, pipeline, pricing, and GTM references into one measurable plan. | 4.8 | Need direct growth and pricing evidence. | Steve | 3 | GTM, pricing, and funnel references ingested and cited by routed asks. |
| Job Studio Training Evaluation | Training factory exists, but evaluation corpus and session-scoring references are still narrow. | Eight-session training system with a strong evaluation and critique backbone. | 5.8 | Low evaluation density. | Jake | 4 | Evaluation and instructional-design sources are ingested and visible in training outputs. |
| Trust & Governance Studio | Department exists, but release gates need stronger official standards backing. | Security, privacy, accessibility, and AI claims guidance become inherited defaults. | 4.8 | Need official source depth and remediation patterns. | Shield | 5 | Trust source bundle spans OWASP, NIST, W3C, and FTC layers. |
| Data & Decision Science Studio | Wrapper exists, but forecast, instrumentation, and experimentation references are still shallow. | Measured scorecards, forecasts, and instrumentation patterns grounded in analytics and experimentation docs. | 4.6 | Need analytics and eval systems evidence. | Pulse | 6 | Instrumentation and eval corpus is ingested and queryable. |

## Recommendation
Start the gap closure wave now. Use direct-URL manifests only for this pass, keep Job Studio-specific training harvests in `mike-job-studio`, and write shared department intelligence into `founder-intelligence-os`.

## Source Stack
- Official docs and public handbooks
- Standards bodies and policy sources
- Stable public GitHub documentation pages
- Existing Job Studio training manifests for AI foundations, Ellen enablement, MCP stack, and behavioral science

## New Manifest Set
- `startup_os_talent_org_design_officials.yaml`
- `startup_os_finance_operating_cadence_officials.yaml`
- `startup_os_revenue_growth_officials.yaml`
- `startup_os_trust_governance_officials.yaml`
- `startup_os_data_decision_science_officials.yaml`
- `startup_os_training_evaluation_officials.yaml`

## Existing Job Studio Manifest Set
- `job_studio_training_ai_foundations.yaml`
- `job_studio_training_behavioral_science.yaml`
- `job_studio_training_ellen_enablement.yaml`
- `job_studio_training_github_harvest.yaml`
- `job_studio_training_mcp_stack.yaml`

## Assumptions
- Official docs and handbooks are strong enough to materially improve department maturity without a search phase.
- The next maturity lift comes from targeted evidence density plus reusable templates, not from additional department wrappers.
- Some maturity gaps are process-only and will not be solved by more data. Those still need protocol and UI work after the crawl wave lands.

## Risks
- Crawl depth can create noisy chunks if source sites are too broad.
- Shared department data and Job Studio data need to stay separated by company context.
- Evidence growth alone does not raise maturity unless we also write role packets, scorecards, and templates from it.

## Next Actions
1. Execute the gap closure wave runner with resume enabled.
2. Review run summaries and failed sources.
3. Update maturity scores only where new evidence materially changes output quality.
4. Convert the strongest new source bundles into finance packets, talent packets, trust gates, growth templates, and training rubrics.

## Execution Update

This wave is now active and partially verified beyond the initial run:

- `startup_os_product_experience_studio_officials.yaml`
  - prior state: `592` chunks, `1` error on `m3.material.io`
  - current targeted rerun: `781` chunks, `0` errors
- `startup_os_revenue_growth_officials.yaml`
  - prior state: `34` chunks
  - current targeted rerun: `382` chunks, `0` errors
- `job_studio_training_ai_foundations.yaml`
  - prior state: `0` chunks on the last resumable wave
  - current targeted rerun: `219` chunks, `0` errors

## What changed in this pass

- Patched Exa ingestion to match the current SDK contract and removed the invalid `use_autoprompt` call.
- Reduced the Product & Experience Material crawl to a smaller, safer scope and added a Jina overview source.
- Expanded Revenue & Growth with stronger pricing and revenue-operations sources plus Exa-backed discovery.
- Expanded Track C AI foundations with additional official docs and Exa-backed AI foundations discovery.
- Added reusable operating packs for Founder Decision Room, Marketing & Narrative Studio, and Data & Decision Science Studio so the maturity lift comes from operating loops as well as new data.

## Current note

The full `run_department_gap_closure_wave.py --resume` batch is still running after these fixes. The targeted reruns above are already verified and were used to refresh the maturity dashboard in the meantime.
