# Founder Evidence Graph Spec

## Purpose

The foundry should reason from a structured evidence graph, not just a pile of chunks. This graph is the layer between raw sources and company decisions.

## Core nodes

- source
- evidence item
- claim
- contradiction
- decision
- experiment
- metric
- company
- execution track

## Required evidence fields

- source url
- source type
- captured at
- effective date
- source tier
- confidence
- verification status
- owner
- freshness SLA

## Source tiers

- primary official
- primary research
- strong secondary
- weak secondary
- inferred internal

## Contradiction protocol

1. conflicting claims are stored separately
2. the contradiction is surfaced, not hidden
3. the owner or council responsible for arbitration is recorded
4. the claim remains unresolved until dated or adjudicated

## Freshness rules

- pricing and vendor claims: monthly
- launch-critical policies: monthly
- product and UX references: quarterly
- strategic analyses: quarterly
- academic and framework layers: semiannually unless rapidly moving

## Foundry behavior

Susan should:

- prefer primary and current sources
- surface contradictions explicitly
- cite what she is using
- say when a conclusion is an inference
- flag stale evidence before making strong recommendations
