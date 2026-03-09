# Engineering Execution Doctrine

## Core Rule

Architecture exists to preserve velocity under growth and uncertainty.

## What Senior Engineering Answers Must Include

- service or module boundaries
- state ownership
- idempotency and retry behavior
- failure handling
- observability
- rollout and migration path
- what should stay simple for now

## Technical Review Heuristics

- Prefer boring technology unless the new choice clearly reduces strategic risk
- Make background workflows explicit
- Assume retries, duplicates, and partial failure
- Design operational visibility alongside the feature

## Common Failure Modes

- hidden coupling
- no migration story
- no monitoring plan
- overfitting to edge-case scale
- API designs that ignore versioning and partial adoption

