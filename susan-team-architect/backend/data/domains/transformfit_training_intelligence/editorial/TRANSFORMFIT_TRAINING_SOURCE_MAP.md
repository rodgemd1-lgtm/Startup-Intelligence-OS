# TransformFit Training Source Map

This is the operating map for the TransformFit training-intelligence corpus.

## Structured datasets

### free-exercise-db

- raw GitHub JSON exercise library
- used for exercise selection, equipment-aware substitution, and movement examples
- fields include level, mechanic, equipment, primary muscles, secondary muscles, and instructions

### wger exercise API

- public exercise catalog with categories, muscles, equipment, and translated descriptions
- useful for alternate naming, broader movement coverage, and category-level exploration

## Open-access evidence

### programming and progression

- public-health activity guidance for baseline recommendations
- hypertrophy volume review
- autoregulation strength review
- AI-generated exercise-plan assessment papers

### recovery and nutrition

- sleep intervention review
- protein supplementation review

## User-research layer

- Reddit posts from fitness communities
- recent app-store reviews from competitor products such as Fitbod, Strava, Peloton, and Noom

## How this should be used

- `workout-program-studio`
  - exercise catalog first, training research second, user research third
- `training-research-studio`
  - evidence first, then user language, then program implications
- `coach`
  - use this corpus for progression logic, substitutions, and safety framing
