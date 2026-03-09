# Workout Session Experience System 2026

This pack defines how the active workout experience should be designed in 2026.

## Core Principle

The workout screen must feel like a coached session, not a spreadsheet and not a pure chat transcript.

## Structural Model

- `session spine`: exercise, set target, prior performance, timer, primary controls
- `coach thread`: short guidance, rationale, reassurance, adaptation
- `state transitions`: set start, set complete, rest, adaptation, finish

## Design Laws

- Keep the session spine stable.
- Put dynamic coaching in a lightweight adjacent layer.
- Use motion for confirmation, orientation, and recovery-state pacing.
- Make numeric entry extremely fast and thumb-safe.
- Treat hard sets, adaptations, and finish moments as design-critical states.

## Best Practices

- high-contrast gym-safe surfaces
- large numeric entry targets
- one-thumb reach zones
- rest-state micro-motion, not cinematic motion
- previous-performance visibility
- clear explanation when the plan changes
