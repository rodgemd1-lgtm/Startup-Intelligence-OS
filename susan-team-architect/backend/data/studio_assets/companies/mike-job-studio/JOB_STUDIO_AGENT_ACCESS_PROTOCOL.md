# Job Studio Agent Access Protocol

## Purpose

Make Job Studio data available to the right personas and agents by default so material decisions and training outputs are grounded in the attached corpora.

## Required context bundles

- `studio_memory`
- `training_research`
- `linked_company_context`
- `market_research`
- `operational_protocols`
- `evaluation_corpus`

## Default access by role

- Jake: `studio_memory`, `training_research`, `linked_company_context`, `operational_protocols`
- Susan: `training_research`, `market_research`, `operational_protocols`, `evaluation_corpus`
- Ellen: `training_research`, `linked_company_context`, `market_research`, `operational_protocols`
- Knowledge Engineer: `training_research`, `linked_company_context`, `evaluation_corpus`, `operational_protocols`
- AI Evaluation Specialist: `evaluation_corpus`, `training_research`, `operational_protocols`
- Marketing Studio Director: `market_research`, `training_research`, `operational_protocols`
- Research Director: `market_research`, `training_research`, `linked_company_context`

## Decision rule

For any material Job Studio ask, the action packet should name the context bundles attached before work begins.

## Writeback rule

Every training or strategy run should write back:
- improved examples
- failure patterns
- revised prompts
- revised facilitator notes
- rubric updates
- locator updates when new corpora are mounted
