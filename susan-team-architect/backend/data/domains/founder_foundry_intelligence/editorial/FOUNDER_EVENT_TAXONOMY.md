# Founder Event Taxonomy

## Purpose

A production foundry needs a shared event language so every company can instrument behavior, measure progress, and compare outcomes consistently.

## Event families

- acquisition
- activation
- engagement
- conversion
- retention
- support
- trust
- experiment
- content
- studio production
- launch

## Required event fields

- event name
- company id
- user or account id when available
- session id when relevant
- timestamp
- source surface
- workflow id
- experiment ids
- trust flags when sensitive

## Naming rules

- use verb_noun pattern
- avoid UI-specific names if the event represents a business action
- separate user intent from system effect

## Required dictionaries

- metric dictionary
- event ownership map
- dashboard map
- alert threshold map

## Example events

- company_stage_gate_passed
- company_stage_gate_failed
- experiment_started
- experiment_completed
- studio_asset_published
- support_ticket_opened
- support_ticket_resolved
- trust_exception_logged
