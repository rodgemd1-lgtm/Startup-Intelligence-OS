# OpenClaw API List — Focus & Criteria
**Source**: https://github.com/Kevjade/openclaw-api-list/blob/main/OPENCLAW_FOCUS.md
**Ingested**: 2026-03-22
**Purpose**: PAI (Personal AI Infrastructure) — understanding inclusion criteria and category relevance

---

## What is OpenClaw?
- **Multi-channel**: WhatsApp, Telegram, Slack, Discord, Signal, iMessage, Google Chat, Matrix, Teams, WebChat
- **Agentic**: shell commands, browser, file management, cron jobs, webhooks, skills/tools
- **Skills**: `~/.openclaw/workspace/skills/<name>/SKILL.md` — teaches agent when/how to call tools. API keys via `skills.entries.<name>.apiKey` or env vars in `openclaw.json`
- **MCP**: First-class integration. Add server URL to OpenClaw config, no skill folder needed
- **ClawHub**: Public skill registry. `clawhub install` / `clawhub sync`

## Inclusion Criteria (must meet 1+)
1. Callable by a skill (REST/HTTP or Apify-style run with API key)
2. MCP-compatible (OpenClaw connects directly via config)
3. Webhook-friendly (trigger or be triggered by OpenClaw's webhook/cron)
4. Integration-ready (Calendar, email, messaging, storage, search, productivity)

## Category Relevance for OpenClaw

| Category | Relevance | How it ties in |
|----------|-----------|----------------|
| **MCP Servers** | Direct | First-class. Plug in via config, no skill needed |
| **Automation** | High | Workflows, triggers, webhooks. Agent starts/reacts via cron and webhook handlers |
| **Integrations** | High | Calendar, email, messaging, storage. Natural "do this for me" skills |
| **AI** | High | Models and agents the assistant can call |
| **Agents** | Medium-High | Agent-to-agent APIs. Wrap as skills for research, content, jobs |
| **Travel** | Medium | Book, search, compare. "Plan my trip" skills |
| **Jobs** | Medium | Job search, salary data, applications. "Find jobs" monitoring skills |
| **News** | Medium | Headlines, summaries, feeds. Daily briefing and digest skills |
| **Ecommerce** | Medium | Price monitoring, product search, reviews. Shopping assistant skills |
| **Lead Generation** | Medium | Contact finding, enrichment. Use responsibly (GDPR, CAN-SPAM) |
| **Social Media** | Medium | Post scheduling, analytics, trend monitoring |
| **Real Estate** | Medium | Property listings, market data |
| **SEO Tools** | Medium | Keyword research, ranking tracking |
| **Videos** | Medium | Transcripts, metadata. "Summarize this video" skills |
| **Developer Tools** | Low-Medium | Scriptable/HTTP-callable tools only |
| **Open Source** | Low-Medium | Same as Developer Tools |

## How to Use with OpenClaw
1. Start with curated list (92 APIs) — pick 2-3, wire up, then expand
2. Or pick from category when you know what you want
3. Create a skill in `~/.openclaw/workspace/skills/` with a `SKILL.md`
4. Configure key in `~/.openclaw/openclaw.json` under `skills.entries.<skillName>`
5. Optional: publish to ClawHub

## Resources
- OpenClaw: https://openclaw.ai
- Docs: https://docs.openclaw.ai
- Skills: https://docs.openclaw.ai/tools/skills
- ClawHub: https://clawhub.com
- The Operator Vault (200+ operators community): https://theoperatorvault.io
