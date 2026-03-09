# TransformFit Personal Knowledge Map Spec

TransformFit needs a personal knowledge map so the coach can remember the right things with the right boundaries.

## Purpose

- reduce repeat explanation burden
- improve perceived responsiveness
- support better workout and recovery recommendations
- create relational continuity without surveillance

## Tier model

### Tier 1: Training context

- goals
- split preference
- equipment
- injury notes
- schedule windows

### Tier 2: Lifestyle context

- work rhythm
- sleep constraints
- family load
- travel
- stress patterns

### Tier 3: Life details

- kids' names
- pet names
- regular commitments
- celebrations

### Tier 4: Identity and values

- why they train
- what they fear losing
- what triggers shame or avoidance

### Tier 5: Preference fingerprint

- preferred tone
- humor tolerance
- when to push versus reassure
- tolerance for explanation depth

## Node schema

Each node should store:

- `node_id`
- `user_id`
- `category`
- `tier`
- `fact`
- `source_context`
- `user_supplied`
- `date_shared`
- `last_referenced_at`
- `reference_count`
- `freshness_window_days`
- `staleness_status`
- `natural_contexts`
- `prohibited_contexts`
- `proactive_safe`
- `requires_user_reactivation`
- `confidence`
- `notes`

## Reference policy

- Tier 1 can be used frequently
- Tier 2 should be used when it affects real planning
- Tier 3 should be used lightly and warmly
- Tier 4 should generally wait for user reactivation
- Tier 5 should influence tone implicitly, not through explicit statements

## Staleness decay

- training context: 180 days default
- lifestyle context: 90 days default
- life details: 60-90 days default
- identity material: dormant until reactivated
- sensitive material: never proactive

## Example summary object

```json
{
  "user_id": "user_123",
  "preferred_name": "Mike",
  "active_context_summary": [
    "two kids at home",
    "energy drops by 6pm",
    "four training days available"
  ],
  "warm_reference_budget": 1,
  "stale_nodes_hidden": true
}
```

## Usage rules

- never display the full memory inventory to the user
- do not use more than one non-operational personal detail per exchange
- if the product is uncertain, ask instead of pretending to know
- when in doubt, use the context to shape the plan rather than mentioning it directly
