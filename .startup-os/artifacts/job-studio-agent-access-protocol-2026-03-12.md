# Job Studio Agent Access Protocol

**Date:** 2026-03-12  
**Department:** Job Studio

## Objective
Define how every persona and agent accesses the Job Studio corpus, training factory data, behavioral-science materials, and linked company evidence before making material decisions or producing training assets.

## Context Namespaces

| Namespace | Purpose | Typical sources |
|---|---|---|
| `studio_memory` | Mike-authored and work-history context | Job Studio email corpus, authored messages, work messages |
| `training_research` | AI foundations, instructional design, and training examples | Oracle corpus extracts, AI enablement repo, behavioral-science docs |
| `linked_company_context` | Company-specific operating context | Oracle Health corpus, linked company locators, workflow docs |
| `market_research` | Competitive, market, and messaging evidence | Oracle market intelligence documents, vendor intelligence repo |
| `operational_protocols` | Repeatable operating rules and quality gates | protocol docs, session maps, rubrics, decision records |
| `evaluation_corpus` | Transcript reviews, failure patterns, panel notes, scoring | training evaluations, critique artifacts, rubric outputs |

## Access Matrix

| Persona or agent | Required bundles | Primary use |
|---|---|---|
| Jake | `studio_memory`, `operational_protocols`, `training_research`, `linked_company_context` | orchestration, routing, decision framing |
| Susan | `operational_protocols`, `training_research`, `market_research`, `evaluation_corpus` | foundry design, maturity scoring, capability mapping |
| Ellen | `training_research`, `linked_company_context`, `market_research`, `operational_protocols` | learner-facing guidance, Gen Chat enablement, workflow execution |
| Knowledge Engineer | `training_research`, `linked_company_context`, `evaluation_corpus`, `operational_protocols` | corpus harvest, tagging, retrieval, locator maintenance |
| AI Evaluation Specialist | `evaluation_corpus`, `training_research`, `operational_protocols` | transcript scoring, quality review, confidence calibration |
| Marketing Studio Director | `market_research`, `training_research`, `operational_protocols` | decks, message maps, learner-facing assets |
| Research Director | `market_research`, `training_research`, `linked_company_context` | evidence packets, best-practice synthesis, example libraries |
| Consumer User Studio | `training_research`, `evaluation_corpus`, `linked_company_context` | learner behavior diagnosis and adoption friction analysis |
| Engineering & Agent Systems Studio | `operational_protocols`, `evaluation_corpus`, `linked_company_context` | pipeline, automation, and toolchain upgrades |

## Material-Ask Rule
For any ask that changes strategy, training content, evaluation criteria, or company-facing deliverables:
1. The action packet must name the context bundles attached.
2. The run must state the linked corpora or locators used.
3. Missing bundles must trigger a routing note or signal rather than silent work.

## Writeback Rule
Every Job Studio run should write back:
- new named examples
- revised prompts or scripts
- failure patterns
- rubric deltas
- corpus locator updates when new source roots are added
