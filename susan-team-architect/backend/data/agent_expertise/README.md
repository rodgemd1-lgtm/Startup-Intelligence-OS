# Agent Expertise System

This directory turns Susan's agents from persona prompts into operating-grade specialists.

## Structure

- `manifest.yaml`: maps agents to doctrine, knowledge packs, collaboration triggers, and output contracts
- `shared/`: standards every agent should inherit
- `product/`, `engineering/`, `science/`, `psychology/`, `growth/`, `strategy/`: specialist packs
- `evals/`: quality rubric and scenario expectations

## Design Rules

Every agent should have:

1. Doctrine
2. Current-state expertise
3. Example library references
4. Decision rubrics
5. Failure modes
6. Explicit handoff rules
7. Output contract

## Usage

- Humans use this as the source of truth for upgrading agent specs.
- Scripts can audit whether agent files include the required sections.
- These packs can be ingested into RAG so agents retrieve domain doctrine, patterns, and examples instead of relying on vague prompting.

