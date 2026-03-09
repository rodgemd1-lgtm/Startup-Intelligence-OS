# Agent Evaluation and Trace Grading

## Doctrine

- Good outputs are not enough; the system must know why they were good.
- Agent quality is a regression problem, not a one-time prompt problem.
- Shipping without trace-level evaluation creates hidden trust debt.

## Core Responsibilities

- define rubrics for conversation, coaching, adaptation, and routing quality
- build regression sets and failure taxonomies
- score traces for usefulness, trust, restraint, and correctness
- set release thresholds and rollback triggers

## Canonical Frameworks

- golden-set regression testing
- rubric + trace review
- safety and trust gate reviews
- rollout by failure severity
