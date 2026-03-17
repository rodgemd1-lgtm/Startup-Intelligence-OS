# Stronger Dataset and Benchmark Enrichment

**Research question:** Which stronger datasets should Startup Intelligence OS and Job Studio ingest next to improve benchmark coverage, eval quality, and synthetic-run review depth?

## Definitions
- **Benchmark library:** curated operating cases, reports, handbooks, and benchmark references used to compare quality, coverage, and maturity.
- **Eval dataset:** source material that supports quality tests, synthetic-run review, rubric design, or output scoring.
- **Synthetic-run review:** structured assessment of modeled or automated runs using explicit scenarios, rubrics, and failure analysis.

## Methods
- review Susan's existing dataset inventory and foundry gap assessments
- identify stronger public benchmark and eval sources
- package those sources into repeatable scrape manifests
- store the resulting summaries so Susan's research agent can refresh them later

## Source stack

### Benchmark and operating-case sources
- GitLab handbook and operating guidance
- SaaS Capital private SaaS benchmark survey
- Salesforce State of Sales
- HubSpot State of Marketing
- Bessemer and Paddle revenue or pricing benchmark material

### Evaluation and synthetic-run sources
- OpenAI eval guidance
- OpenAI `openai/evals`
- OpenAI `simple-evals`
- Confident AI `deepeval`
- Arize `phoenix`
- NIST AI Risk Management Framework

### Learning-science and training sources
- CMU teaching and assessment guides
- Vanderbilt CFT learning design guidance
- Learning Scientists retrieval-practice and learning-science references
- existing Job Studio and Oracle training packets

## Benchmark targets
- stronger benchmark library coverage for founder, revenue, finance, talent, and operator systems
- richer eval-test sources for synthetic-run review
- stronger adult-learning and transfer-design evidence for Job Studio training

## Synthesis
The current OS has enough structure to use stronger datasets immediately. The next high-leverage move is not more generic web volume. It is better benchmark cases, stronger evaluation sources, and richer learning-science material that can be reused by Susan's research, scoring, and training systems.

## Execution update
- stronger benchmark case library: `319` chunks
- eval and synthetic review foundations: `382` chunks
- Job Studio training learning science stronger: `120` chunks
- total landed in this wave: `821` chunks
- total errors: `0`

## Unknowns
- which benchmark providers produce the cleanest chunks under the current scrape stack
- how much of the synthetic-run review layer should live as `studio_evals` versus `operational_protocols`
- whether some benchmark sources need a dedicated single-page ingest path instead of crawl mode

## Next research steps
1. Execute the stronger dataset wave.
2. Review chunk quality and source yield.
3. Promote the best sources into the maintained benchmark library and synthetic-run review framework.
