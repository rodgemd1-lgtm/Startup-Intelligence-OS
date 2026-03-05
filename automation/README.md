# Automation — AI Workflows, n8n, Zapier & Agent Pipelines

> Automating every repeatable process in your startup with AI agents and no-code tools.

---

## 1. Automation Strategy Framework

### What to Automate First (Impact × Frequency Matrix)

| Priority | Process | Tool |
|----------|---------|------|
| **P0** | CI/CD pipeline | GitHub Actions |
| **P0** | Error alerting | Sentry + Slack webhook |
| **P0** | Customer onboarding emails | Resend / ConvertKit |
| **P1** | Lead scoring & routing | n8n + CRM |
| **P1** | Social media scheduling | Buffer / Typefully |
| **P1** | Invoice generation | Stripe Billing |
| **P1** | Code review | Claude Code + GitHub Actions |
| **P2** | Content repurposing | n8n + Claude API |
| **P2** | Competitor monitoring | Apify + n8n |
| **P2** | Meeting notes → tasks | Otter.ai + Linear |
| **P3** | Customer feedback analysis | Claude API + Notion |
| **P3** | Report generation | n8n + Google Sheets |

### Rule of Thumb
> If you do it more than 3 times and it takes > 5 minutes, automate it.

---

## 2. n8n — The AI Automation Platform

### Why n8n
- **Open-source** (self-hostable) or cloud-hosted
- **400+ integrations** out of the box
- **AI-native**: Built-in LLM nodes (Claude, OpenAI, Ollama)
- **Code when needed**: JavaScript/Python function nodes
- **Webhook triggers**: React to any external event

### Key AI Workflow Templates

**Content Pipeline:**
```
Trigger (Schedule) → Exa Search → Claude (write article) →
Notion (save draft) → Slack (notify team)
```

**Lead Enrichment:**
```
Webhook (new signup) → Clearbit Enrichment →
Claude (score & summarize) → CRM (update record) →
Slack (notify sales if high-value)
```

**Customer Feedback Loop:**
```
Intercom (new message) → Claude (classify sentiment + intent) →
If negative: Slack (alert CS team)
If feature request: Canny (create request)
If bug: Linear (create issue)
```

**Competitor Intelligence:**
```
Schedule (weekly) → Apify (scrape competitor sites) →
Claude (analyze changes) → Notion (update competitor DB) →
Slack (weekly digest)
```

### n8n Setup
- **Self-hosted**: Docker container, ~$5/mo on Railway
- **Cloud**: n8n.cloud, free tier available
- **AI nodes**: Require API keys (Claude, OpenAI)

---

## 3. Zapier vs Make vs n8n Comparison

| Feature | n8n | Zapier | Make (Integromat) |
|---------|-----|--------|-------------------|
| **Pricing** | Free (self-hosted) / $20/mo cloud | $19.99/mo+ | $9/mo+ |
| **Complexity** | Medium-High | Low | Medium |
| **AI Integration** | Native LLM nodes | Limited | Good |
| **Self-hosting** | Yes | No | No |
| **Code nodes** | JS + Python | Limited | JS only |
| **Branching** | Full logic | Basic | Full logic |
| **Best for** | Developers, AI workflows | Non-technical, simple flows | Visual builders, complex flows |

### Recommendation
- **Non-technical founder**: Start with Zapier
- **Technical founder, simple needs**: Make
- **AI-heavy workflows**: n8n (self-hosted or cloud)

---

## 4. Claude API Automation Patterns

### Batch Processing
```python
import anthropic

client = anthropic.Anthropic()

def process_feedback(feedback_list):
    results = []
    for feedback in feedback_list:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Classify this customer feedback:

Feedback: {feedback}

Return JSON: {{"sentiment": "positive|neutral|negative",
"category": "bug|feature|praise|question",
"priority": "low|medium|high",
"summary": "one sentence"}}"""
            }]
        )
        results.append(response.content[0].text)
    return results
```

### Webhook-Triggered Analysis
```python
from fastapi import FastAPI
import anthropic

app = FastAPI()
client = anthropic.Anthropic()

@app.post("/analyze-support-ticket")
async def analyze_ticket(ticket: dict):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""Analyze this support ticket and return:
1. Urgency (1-5)
2. Category
3. Suggested response draft

Ticket: {ticket['message']}"""
        }]
    )
    return {"analysis": response.content[0].text}
```

---

## 5. GitHub Actions Automations

### Auto-Review PRs with Claude
```yaml
name: AI Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: AI Review
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Review this PR for security, performance, and code quality"
```

### Automated Dependency Updates
```yaml
name: Update Dependencies
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday 9am
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx npm-check-updates -u
      - run: npm install
      - run: npm test
      - uses: peter-evans/create-pull-request@v6
        with:
          title: 'chore: update dependencies'
```

---

## 6. Automation Tools Directory

| Tool | Category | Purpose |
|------|----------|---------|
| **n8n** | Workflow | AI-native workflow automation |
| **Zapier** | Workflow | No-code automation |
| **Make** | Workflow | Visual workflow builder |
| **Trigger.dev** | Background jobs | TypeScript background jobs |
| **Inngest** | Event-driven | Event-driven function orchestration |
| **Temporal** | Orchestration | Durable workflow engine |
| **Windmill** | Scripts | Open-source scripts-to-workflows |
| **Activepieces** | Workflow | Open-source Zapier alternative |

---

## Sources

| Source | URL |
|--------|-----|
| n8n — AI Automation Platform | [n8n.io/ai](https://n8n.io/ai) |
| Anthropic — Claude Code GitHub Action | [github.com/anthropics](https://github.com/anthropics/claude-code-action) |
| Trigger.dev — Background Jobs for Next.js | [trigger.dev](https://trigger.dev) |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
