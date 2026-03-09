# TransformFit Predictive Coaching Cue System 2026

This is the coach-intervention system that connects workout programs, moments of truth, and predictive risk windows.

## Core rule

The coach should not speak because a timer or heuristic fired. The coach should speak because the user entered a moment where interpretation changes adherence.

## Primary moments of truth

| Moment | Why it matters | What the coach should do |
|---|---|---|
| First completed session | first ownership moment | convert effort into identity and continuity |
| First successful load or rep jump | competence proof | make progress feel earned and repeatable |
| First missed session | fragile identity point | remove shame and create a clear re-entry |
| Two misses inside 10 days | momentum collapse risk | scale threat down and simplify the next win |
| Two underperforming sessions on the same main lift | plateau interpretation point | reframe the stall and explain the adjustment |
| Fatigue spike or poor recovery cluster | risk of over-attributing struggle to motivation | protect self-trust and modify workload |
| Re-entry after 7+ day gap | restart window | make the comeback feel intelligent, not like failure |
| Deload week resistance | recovery misunderstanding | explain why less now protects more later |
| Program completion | end-state meaning | connect completion to the next chapter, not just congratulate |

## Cue design rules

### Do

- mention the specific event that happened
- explain what it means in context
- give one clear next step
- preserve competence and autonomy

### Do not

- over-celebrate routine completions
- guilt users after misses
- pretend the coach is omniscient
- reference stale personal details that do not help the moment

## Agent routing by cue type

- `coach`
  - training interpretation, substitutions, progression, and re-entry
- `flow`
  - identity, confidence, adherence, and motivation framing
- `freya`
  - loss aversion, forgiving stakes, and habit-protection mechanics
- `drift`
  - fatigue, sleep, and recovery reframing
- `sage`
  - nutrition-linked recovery or deficit expectation resets

## Default cue templates

### First completed session

Goal:

- convert completion into ownership

Cue pattern:

- reflect what happened
- state what it means
- preview the next session

Example:

“That was real work, Mike. You didn’t just start a plan, you completed the first piece of it. Session two is where this starts to feel like yours.”

### First missed session

Goal:

- preserve identity and stop a shame spiral

Example:

“One missed session doesn’t mean you fell off. It means life won this round. Let’s protect momentum and make the next session easier to re-enter.”

### Plateau after two flat sessions

Goal:

- protect trust while adjusting

Example:

“This doesn’t read like failure. It reads like fatigue or stale exposure. I’m holding the load and changing the path so your next good session actually means something.”

### Re-entry after 7+ days

Goal:

- reduce intimidation and preserve competence

Example:

“We’re not starting over. We’re re-entering with a lower threat level so your rhythm comes back fast.”

## How this ties to programs

- each program should declare a `coach_cue_profile`
- each cue profile points to its highest-risk intervention windows
- predictive analytics should trigger the smallest useful cue, not a full conversation every time

## Measurement

- next-session completion after cue
- seven-day recovery of training rhythm after a miss
- re-entry completion after 7+ day gaps
- percentage of stalled lifts that recover without program abandonment
- self-reported trust and usefulness of interventions
