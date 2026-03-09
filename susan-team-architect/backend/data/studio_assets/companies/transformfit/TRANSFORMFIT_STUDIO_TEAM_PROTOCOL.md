# TransformFit Studio Team Protocol

> Purpose: define exactly who Susan should pull in for TransformFit UI/UX and experience work so the app does not rely on ad hoc agent selection.

## Default rule

For meaningful TransformFit UI/UX work, Susan should usually pull both the general design studio and the TransformFit-specific studios.

Minimum default team:
- `susan`
- `design-studio-director`
- `app-experience-studio`
- `workout-session-studio`
- `coaching-architecture-studio`
- `marcus`
- `mira`
- `lens`
- `echo`

Add these by default when the task touches core product logic:
- `conversation-designer`
- `ai-product-manager`

## Task-to-team map

### 1. Landing pages, acquisition pages, or launch surfaces

Pull:
- `design-studio-director`
- `landing-page-studio`
- `marcus`
- `mira`
- `prism`
- `echo`
- `lens`
- `marketing-studio-director`

Use when:
- redesigning the homepage
- building launch pages
- improving signup conversion
- defining visual direction or narrative motion

### 2. Active workout session, logging, and in-gym UX

Pull:
- `design-studio-director`
- `app-experience-studio`
- `workout-session-studio`
- `coaching-architecture-studio`
- `marcus`
- `mira`
- `lens`
- `echo`
- `conversation-designer`
- `coach`
- `flow`
- `freya`
- `ai-product-manager`

Add when adaptation is involved:
- `algorithm-lab`
- `knowledge-engineer`

Use when:
- changing workout logging
- redesigning set entry
- changing coaching cues
- building session flow
- revising rest timers, PR moments, or mid-session adjustments

### 3. Onboarding, first-week experience, and habit formation

Pull:
- `design-studio-director`
- `app-experience-studio`
- `coaching-architecture-studio`
- `marcus`
- `mira`
- `echo`
- `freya`
- `flow`
- `conversation-designer`
- `ai-product-manager`

Use when:
- changing onboarding
- designing first-session and first-week flows
- building emotional arcs
- reducing early churn

### 4. Workout programs and coaching overlays

Pull:
- `workout-program-studio`
- `training-research-studio`
- `coach`
- `sage`
- `drift`
- `flow`
- `freya`
- `coaching-architecture-studio`
- `conversation-designer`

Add when product implications are involved:
- `workout-session-studio`
- `algorithm-lab`

Use when:
- creating or modifying programs
- changing progression
- defining coaching cues
- building adherence or re-entry rules

### 5. Visual proof, screenshots, and reference gathering

Pull:
- `design-studio-director`
- `social-media-studio`
- `marcus`
- `prism`
- `research-director`
- `research-ops`

Use when:
- building annotated precedent sets
- collecting competitor references
- creating screenshot-led proof
- building storyboards or reels

## Escalation rules

- If the work affects the active workout screen, always involve `workout-session-studio`.
- If the work affects coach language, always involve `coaching-architecture-studio` and `conversation-designer`.
- If the work changes user effort, friction, or motivation, always involve `freya` and `flow`.
- If the work changes how the system adapts, always involve `algorithm-lab`.
- If the work changes accessibility or readability in the gym environment, always involve `lens`.

## What Susan should avoid

Do not route TransformFit UI/UX work to only:
- `marcus`
- `echo`

That combination is useful, but incomplete. It misses:
- session-state expertise
- coaching architecture
- accessibility
- motivation science
- adaptation logic

## Trigger prompt to use in practice

If the user asks vaguely for TransformFit design help, Susan should interpret that as:

`Pull the full TransformFit experience team: Design Studio Director, App Experience Studio, Workout Session Studio, Coaching Architecture Studio, Marcus, Mira, Lens, Echo, Conversation Designer, AI Product Manager, and any science/algorithm specialists required by the task.`
