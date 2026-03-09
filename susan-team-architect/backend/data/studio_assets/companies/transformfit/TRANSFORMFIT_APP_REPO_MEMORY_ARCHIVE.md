# TransformFit App Repo Memory Archive

> Purpose: preserve the most important design, UX, coaching, and operating learnings from the live TransformFit app repo so Susan's team can retrieve them even if the app repo changes later.
> Primary source repo: `/Users/mikerodgers/adapt-evolve-progress`

## Core experience laws

- TransformFit should feel like a coach, not a fitness app.
- The gym is not the place for complex UI. If it takes more than 8 seconds to log a set, the product has failed.
- The user experiences one coherent coach, even if multiple systems or agents power the logic behind the scenes.
- Intelligence must be visible. The app should explain why it changed something, not just change it.
- The product should feel proactive, not reactive. It notices, adapts, and guides at the right moments.
- Every screen should carry a story forward. No dead-end screens.
- Progress worth celebrating is broader than PRs: consistency, re-entry, showing up on a hard day, good decisions, and smart restraint all count.
- Known-ness should feel attentive and coach-like, never invasive or uncanny.

## Active session expectations

The current app-repo learnings are explicit that the active workout experience is the make-or-break moment.

The preserved expectations are:
- one unified workout logging system instead of parallel patterns
- tap-to-type weight and rep entry, not tedious stepper-first logging
- previous-performance ghost references inline during the session
- always-visible RPE with clear meaning, not buried controls
- a floating or persistent coach presence during the workout
- contextual coaching cues when effort spikes, a PR is near, fatigue accumulates, or a user misses targets
- visible mid-session adaptation logic rather than a silent background change
- post-session narrative that explains what happened and why it matters

## Coaching-system rules

From the app repo's architecture and crew prompt docs, these rules should survive:
- exercise order must respect training logic
- deloads, readiness adjustments, and substitutions must be explainable
- the coach should modulate intensity based on recovery, pain flags, and recent performance
- tone should adapt to the user's preferred coaching style
- the system should preserve trust by distinguishing useful adaptation from random-seeming change

## User-model truths

The user personas in the app repo imply three durable product truths:
- serious intermediates want visible reasoning and progression confidence
- busy professionals need lower-friction session flow and re-entry intelligence
- returning athletes need safety, reassurance, and constraint-aware programming

Those user truths should drive:
- session UX
- program assignment
- re-entry logic
- coaching copy
- adaptation policies

## TransformFit-specific design expectations

The app repo established several non-generic expectations that should remain part of the studio:
- dark, premium, coach-led visual language
- motion that serves meaning, not decoration
- one emotional job per section or screen state
- proof at the point of doubt
- calm, specific, regulated coaching tone
- first-session and first-week coherence matter more than feature breadth

## Product standards Susan should retain

- coach before product
- diagnose before decorate
- show reasoning
- preserve exercise intent before novelty
- use reduced motion and accessibility as first-order design constraints
- treat active workout screens as high-friction, high-fatigue environments
- design for one-thumb logging, glare, noise, and time pressure

## Source documents folded into this memory

- `docs/design/TRANSFORMFIT_DESIGN_PRINCIPLES_2026.md`
- `docs/design/TRANSFORMFIT_LANDING_PAGE_STUDIO_GUIDE.md`
- `docs/design/TRANSFORMFIT_DESIGN_SPEC.md`
- `docs/design/UX-JOURNEY-MAP.md`
- `docs/WORKOUT_LOGGING_UX_PLAN.md`
- `docs/USER-FLOW.md`
- `docs/TRANSFORMFIT_ORG.md`
- `docs/company/CREWAI_AGENT_PROMPTS.md`
- `docs/company/USER_PERSONAS.md`

## Reuse rule

If there is any conflict between a generic studio suggestion and these TransformFit-specific constraints, default to the TransformFit-specific constraints unless new evidence clearly invalidates them.
