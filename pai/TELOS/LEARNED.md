# Learned

Lessons learned the hard way. Seeded from jake_procedural memory (2K+ rules in Supabase).

## Architecture Lessons
- Never assert without verification. Evidence required, always.
- Surgical fixes only — never remove components as a "fix."
- First principles over bolt-ons. If the foundation is wrong, adding layers makes it worse.
- One change when debugging — isolate variables or you'll chase ghosts.
- Read before modifying ANY file. Assumptions kill codebases.
- If touching >8 files in one change, check if scope is right.

## Process Lessons
- Research completes before design starts. No exceptions.
- Plans mean stop. No execution without explicit approval.
- Context health is a leading indicator. When it degrades, everything degrades.
- Write HANDOFF.md when context hits ORANGE. By RED it's too late for clean handoff.
- Capture ideas to parking lot, don't build them mid-session. Scope creep is the enemy.
- Run tests after each logical unit, not at the end. Late testing is debugging, not testing.

## Product Lessons
- More features != more value. Often the opposite.
- "Just code it up" is the most expensive decision in a startup.
- Demo-ware and production-ware are separated by 10x effort. Plan for it.
- Users don't care about your architecture. They care if it works.
- Dogfooding catches 80% of UX problems before users see them.

## Team Lessons
- Agent teams need the same clarity as human teams: purpose, inputs, outputs, success criteria.
- Orchestration without clear routing is just chaos with extra steps.
- 73 agents means nothing if they can't coordinate. Coordination is the product.

## Personal Lessons
- Best work happens before 8 PM. Don't schedule deep work after.
- Scope creep is my biggest weakness. The circuit breaker exists for a reason.
- Saying "not now" is harder than saying "yes" but almost always the right call.
