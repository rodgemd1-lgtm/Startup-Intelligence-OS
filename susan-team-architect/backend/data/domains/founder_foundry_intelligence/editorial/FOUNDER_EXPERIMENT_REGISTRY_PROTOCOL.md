# Founder Experiment Registry Protocol

## Purpose

The experiment registry is the canonical list of what the company is testing, why it matters, and what evidence changes the next decision.

## Required fields

- experiment id
- company id
- hypothesis
- user or workflow targeted
- metric moved
- leading signal
- disconfirming signal
- intervention
- owner
- start date
- stop date
- status
- result summary
- linked decisions

## Rules

1. no experiment without a falsifiable hypothesis
2. no experiment without a defined owner
3. no experiment without a next decision if it passes or fails
4. no experiment should survive beyond its stop date without an update

## Suggested statuses

- proposed
- approved
- running
- paused
- completed
- invalidated
- rolled into roadmap

## Foundry use

Susan should use the registry to avoid:

- duplicated tests
- cargo-cult iteration
- roadmap churn without evidence
