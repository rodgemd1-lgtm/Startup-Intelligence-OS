# V20 Quick Reference

## Cloud Endpoints
- Susan: https://susan-cloud-brain.fly.dev
- Jake Gateway: https://jake-gateway.rodgemd1.workers.dev
- Dashboard: https://dashboard.jakestudio.ai

## Launch Sessions
- `bin/launch-sessions` — shows all session options
- Oracle Health: `cd ~/Desktop/Oracle-Health-Intelligence && claude`
- Founder OS: `cd ~/Desktop/Startup-Intelligence-OS && claude`
- Alex Recruiting: `cd ~/Desktop/Alex-Recruiting && aider`
- Fitness App: `cd ~/Desktop/Fitness-App && aider`

## Model Costs (per 1M tokens)
- Workers AI (Llama 3.1): $0
- Ollama local: $0
- DeepSeek V3: $0.14 input / $0.28 output
- DeepSeek R1: $0.55 input / $2.19 output
- Claude Haiku: $0.25 / $1.25
- Claude Sonnet: $3 / $15
- Claude Opus: $15 / $75

## Daily Triggers (after setup)
- 06:00 CT: Morning brief
- 12:00 CT: Midday update
- 20:00 CT: Evening summary
- 01:00 CT: Overnight worker
- 03:00 CT: Research harvest

## Key Commands
- `ollama pull qwen2.5-coder:32b` — local coding model
- `ollama pull deepseek-r1:14b` — local reasoning model
- `fly deploy` — deploy Susan updates
- `wrangler deploy` — deploy Jake gateway updates
