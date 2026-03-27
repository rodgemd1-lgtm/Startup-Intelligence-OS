# V15 Phase 7: Full Infrastructure Inventory

**Date**: 2026-03-27
**Author**: Jake
**Purpose**: Complete audit of all services, API keys, scheduled tasks, and tools

---

## 1. API Keys (28 keys in ~/.hermes/.env)

| Key | Service | Purpose | Still Needed? |
|-----|---------|---------|---------------|
| ANTHROPIC_API_KEY | Anthropic | Claude API (all agents) | ✅ Yes |
| APIFY_API_KEY | Apify | Web scraping MCP | ✅ Yes |
| BRAVE_SEARCH_API_KEY | Brave | Web search MCP | ✅ Yes |
| EXA_API_KEY | Exa | Advanced web search MCP | ✅ Yes |
| FIRECRAWL_API_KEY | Firecrawl | Web crawling MCP | ✅ Yes |
| FIREHOSE_API_KEY | Firehose | ? | ❓ Check |
| GITHUB_PERSONAL_ACCESS_TOKEN | GitHub | Repo access, MCP | ✅ Yes |
| GOOGLE_CALENDAR_ID | Google | Calendar access | ✅ Yes |
| GOOGLE_CLIENT_ID | Google | OAuth (Calendar, Drive) | ✅ Yes |
| GOOGLE_CLIENT_SECRET | Google | OAuth | ✅ Yes |
| GOOGLE_REFRESH_TOKEN | Google | OAuth token refresh | ✅ Yes |
| GROQ_API_KEY | Groq | Fast inference (Llama) | ✅ Yes (cost reduction) |
| HF_API_KEY | Hugging Face | Model inference | ❓ Check usage |
| HF_SECRET | Hugging Face | Webhook secret | ❓ Check usage |
| HIGGSFIELD_API_KEY_ID | Higgsfield | Video generation MCP | ❓ Low priority |
| HIGGSFIELD_API_KEY_SECRET | Higgsfield | Video generation MCP | ❓ Low priority |
| JINA_API_KEY | Jina | Web reading MCP | ✅ Yes |
| NOTION_API_TOKEN | Notion | Notion MCP | ✅ Yes |
| OPENROUTER_API_KEY | OpenRouter | Multi-model routing | ✅ Yes (cost reduction) |
| RESEND_API_KEY | Resend | Email delivery | ✅ Yes |
| RESEND_TO | Resend | Mike's email | ✅ Yes |
| SUPABASE_SERVICE_KEY | Supabase | Susan RAG, Brain | ✅ Yes |
| SUPABASE_URL | Supabase | Database URL | ✅ Yes |
| SUPERMEMORY_API_KEY | SuperMemory | Memory MCP | ✅ Yes |
| TELEGRAM_BOT_TOKEN | Telegram | Jake → Mike messaging | ✅ Yes |
| TELEGRAM_CHAT_ID | Telegram | Mike's chat ID | ✅ Yes |
| VOYAGE_API_KEY | Voyage AI | Embeddings (1024d) | ✅ Yes |
| GATEWAY_ALLOW_ALL_USERS | OpenClaw | Gateway auth | ✅ Yes |

### Keys to Investigate
- FIREHOSE_API_KEY — what is this for?
- HF_API_KEY / HF_SECRET — are we using Hugging Face?
- HIGGSFIELD — do we need video generation?

---

## 2. Active Services & Infrastructure

### Always-On
| Service | What | Cost | Location |
|---------|------|------|----------|
| Paperclip | Agent control plane | Free (local) | 127.0.0.1:3101 |
| Cloudflare Workers | Jake gateway | Free tier | jake-gateway.rodgemd1.workers.dev |
| Cloudflare R2 | State storage | Free tier | jake-state bucket |
| Cloudflare KV | Hot cache | Free tier | JAKE_CACHE namespace |
| Cloudflare Tunnel | Desktop → edge | Free | ai.jakestudio.tunnel |
| Supabase | Database + RAG | Free tier | zqsdadnnpgqhehqxplio.supabase.co |
| Vercel | OpenClaw Studio | Free tier | openclaw-studio-psi.vercel.app |

### Subscription Services
| Service | Cost/Month | Purpose |
|---------|-----------|---------|
| SuperMemory.ai Pro | $19 | Memory infrastructure |
| Anthropic API | ~$150 budget | Claude (all agents) |
| Voyage AI | Pay-per-use | Embeddings |
| Resend | Free tier? | Email delivery |

### Mike's Other Services (Cross-Project)
| Service | Used By | Purpose |
|---------|---------|---------|
| ClickSend | Alex Recruiting? | SMS/voice outreach |
| Cloudflare domain | Alex Recruiting | Email via Jacob's domain |
| Fly.io | James's OS | App hosting |
| Voyeur.ai | James's OS | ? |

---

## 3. Scheduled Tasks (Active)

### launchd (Local Mac)
| Job | Schedule | Script | Status |
|-----|----------|--------|--------|
| com.jake.proactive-morning-pipeline | 6:00 AM daily | bin/jake-morning-pipeline.sh | ✅ New |
| com.jake.proactive-overnight-intel | 5:00 AM daily | bin/jake-overnight-intel.sh | ✅ New |
| com.jake.proactive-meeting-scanner | Every 15 min | bin/jake-meeting-scanner.sh | ✅ New |
| com.jake.claude-remote | Always on | Claude remote | ✅ Active |
| ai.jakestudio.paperclip | Always on | Paperclip server | ✅ Fixed |
| ai.jakestudio.tunnel | Always on | Cloudflare Tunnel | ✅ Active |

### Disabled (Hermes-Era) — 22 plists
All renamed to .plist.disabled. Can be permanently deleted after Phase 7 validation.

---

## 4. MCP Servers (Connected to Claude Code)

| Server | Tools | Purpose |
|--------|-------|---------|
| susan-intelligence | 35 tools | Susan backend (RAG, agents, productions) |
| supermemory | 3 tools | Memory search/add/list |
| qmd | 4 tools | Local markdown search (726 docs) |
| higgsfield | ? | Video generation |

### MCP Servers Available But Not in .mcp.json
- brave-search, exa, firecrawl, jina — available via API keys
- github — available via PAT
- notion-custom — available via token
- trendradar — available via separate config
- context7 — library docs
- playwright — browser automation
- gemini — Google AI

---

## 5. Agent Platforms

| Platform | Count | Status |
|----------|-------|--------|
| OpenClaw agents (SYSTEM.md) | 65 | ✅ All upgraded |
| Susan agent definitions | 73+ | ✅ Active |
| Paperclip registered agents | 21 | ✅ Active |
| Claude Code subagent types | ~112 | ✅ Available (wshobson plugins) |
| VoltAgent community skills | 734 repos | 🆕 Cloned, needs import |
| VoltAgent framework packages | 30+ | 🆕 Cloned, needs evaluation |

---

## 6. VoltAgent Import Status

### Repos Cloned
- `archive/voltagent/awesome-agent-skills/` — 734 skill repo links, 1,173 line README
- `archive/voltagent/voltagent/` — Full TypeScript agent framework (30+ packages)

### Key VoltAgent Packages to Evaluate
| Package | What It Does | Relevant? |
|---------|-------------|-----------|
| core | Agent runtime | Study patterns |
| anthropic-ai | Claude integration | Study patterns |
| rag | RAG implementation | Compare with Susan |
| mcp-server | MCP server builder | Study patterns |
| voltagent-memory | Memory system | Compare with Brain |
| supabase | Supabase integration | Compare with ours |
| voice | Voice capabilities | Future feature |
| evals | Agent evaluation | Adopt patterns |
| scorers | Quality scoring | Adopt patterns |

### Skill Categories Most Relevant to Us
1. **Official Claude Skills** — already have most
2. **Skills by Supabase** — database patterns
3. **Skills by Cloudflare** — infrastructure patterns
4. **Skills by Firecrawl** — scraping (already have)
5. **Community Skills** — largest category, needs curation
6. **Marketing Skills** — useful for growth agents
7. **Product Manager Skills** — useful for Compass
8. **MiniMax Skills** — cost reduction opportunity

---

## 7. Cost Reduction Opportunities

| Opportunity | Current Cost | Target | How |
|------------|-------------|--------|-----|
| Haiku-tier tasks → open-source | ~$30/mo | $0 | Route via Groq (Llama) or OpenRouter |
| Embedding model | Voyage AI (pay/use) | Lower | Evaluate open-source embeddings |
| Model routing | Manual | Automatic | Paperclip budget enforcement |
| Unused API keys | $0 (but complexity) | $0 | Remove unused keys |
| Duplicate services | Complexity cost | Simplified | Consolidate venues |

### Models to Evaluate
| Model | Provider | Cost | Good For |
|-------|----------|------|----------|
| GLM-5-Turbo | Zhipu AI | Very low | Classification, routing |
| MiniMax v2.7 | MiniMax | Low | General tasks |
| Llama 3.3 70B | Groq | Free tier | Fast inference |
| Qwen 2.5 | Alibaba | Low | Coding tasks |
| DeepSeek V3 | DeepSeek | Very low | Reasoning |
