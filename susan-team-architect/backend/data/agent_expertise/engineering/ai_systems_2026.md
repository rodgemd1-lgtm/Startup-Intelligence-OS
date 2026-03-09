# AI Systems 2026

## Doctrine

The default architecture is not "use more AI." The default is the smallest intelligence layer that produces a meaningful user advantage.

## Required Decision Order

1. User value
2. Data availability
3. Evaluation method
4. Fallback heuristic
5. Cost and latency envelope
6. Operational risk

## Current Patterns

- Hybrid retrieval with metadata filters first, semantic ranking second
- Inline contextual data injection when strict personalization is required
- LLM orchestration only after heuristics and retrieval boundaries are clear
- Evaluation-first development: golden sets, failure clustering, and rejection cases
- Human-readable justification paths for recommendations in regulated or trust-sensitive domains

## Output Expectations

- Minimum viable intelligence
- Data requirements
- Evaluation plan
- Model and tool routing
- Failure modes
- Cost model

## Failure Modes

- Building AI before defining deterministic baselines
- No offline eval harness
- Retrieval without provenance
- Personalization claims without real user data support
- Agent sprawl with no orchestration logic

