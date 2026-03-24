# Challenges

Current blockers and challenges as of 2026-03-24.

## Critical
- **Hermes at 34/100**: The existing PAI scored 34/100 on capability audit. Three disconnected bots, 99K unstructured memories, no autonomous execution. Being replaced by PAI V0.
- **No always-on AI**: Jake only exists during active Claude Code sessions. No persistence between sessions. No way to reach Jake from Telegram when a session isn't running.
- **Context rot**: Sessions degrade as they get long. No automatic context health management. No HANDOFF discipline until recently.

## High Priority
- **Memory fragmentation**: 99K memories in Supabase with no structured retrieval. jake_brain_search has composite scoring but the data quality is low.
- **Susan RAG offline for most companies**: Only a few companies have active RAG chunks. The 6,693 chunk count is concentrated, not distributed.
- **No autonomous execution**: Jake can plan and advise but can't execute without a human starting a session and approving each step.

## Medium Priority
- **Scope creep tendency**: Mike's biggest operational weakness. New ideas interrupt current execution. The parking lot system helps but isn't enforced.
- **Mac Studio setup needed**: PAI V0 requires Mac Studio as always-on host. Setup, networking, and daemon management still to be done.
- **Cross-company intelligence gap**: Oracle Health, Alex Recruiting, and Startup Intelligence OS don't share learnings systematically.

## Low Priority
- **No visual dashboard**: All interaction is terminal-based. No at-a-glance status view.
- **No multi-channel support**: Only Telegram planned for V0. Slack, Discord, voice come later.
