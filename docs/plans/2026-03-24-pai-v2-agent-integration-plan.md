# PAI V2: Agent Integration — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Wire Susan's 82 agents, 16 MCP servers, and Fabric's 233 patterns into the PAI architecture so every capability is callable from any channel. Implement Algorithm v1 (adapted from Miessler's 7-phase loop) as the core reasoning engine.

**Architecture:** Susan MCP server exposed as OpenClaw skill. mcporter bridges all 16 MCP servers. Fabric REST API as sidecar. Claude Code bridge (openclaw-claude-code-skill) routes complex reasoning to Opus. Per-pattern model routing via Inference config. Algorithm v1 governs all multi-step tasks.

**Depends On:** V0 (infrastructure) + V1 (memory) complete

**Process Rule:** Research → Plan → Execute → Lessons Learned → Documentation. Every time. No exceptions.

---

## Pre-Flight Checklist

- [ ] V1 exit criteria all passed (memory migration complete, retriever working)
- [ ] OpenClaw gateway running with LosslessClaw active
- [ ] Claude Code brain running in tmux (jake-brain session)
- [ ] Fabric REST API running on port 8080
- [ ] Susan backend venv activates and MCP server starts
- [ ] All 82 agent .md files present in `susan-team-architect/agents/`

---

## Phase 2A: Susan MCP Integration

*Bring Susan's 82 agents and RAG into OpenClaw as a callable skill.*

### Task 1: Create Susan OpenClaw Skill

**Files:**
- Create: `pai/skills/susan-mcp/skill.json`
- Create: `pai/skills/susan-mcp/handler.ts`
- Create: `pai/skills/susan-mcp/README.md`

**Step 1: Create skill manifest**

```json
{
  "name": "susan-mcp",
  "version": "1.0.0",
  "description": "Bridge to Susan MCP server — 82 agents, 10K+ RAG chunks, research pipeline",
  "author": "Jake PAI",
  "tools": [
    {
      "name": "susan_search",
      "description": "Search Susan's RAG knowledge base (Voyage AI embeddings, 10K+ chunks)",
      "parameters": {
        "query": { "type": "string", "description": "Search query" },
        "company": { "type": "string", "description": "Company context (optional)" },
        "limit": { "type": "number", "description": "Max results (default 5)" }
      }
    },
    {
      "name": "susan_agent",
      "description": "Invoke a Susan agent by name for specialized analysis",
      "parameters": {
        "agent": { "type": "string", "description": "Agent name (e.g., steve-strategy, atlas-engineering)" },
        "prompt": { "type": "string", "description": "Task for the agent" },
        "company": { "type": "string", "description": "Company context" }
      }
    },
    {
      "name": "susan_foundry",
      "description": "Run Susan's capability foundry for a company — capability mapping, team design, maturity scoring",
      "parameters": {
        "company": { "type": "string", "description": "Company name" },
        "mode": { "type": "string", "description": "Foundry mode: foundry, route, design, status" }
      }
    },
    {
      "name": "susan_research",
      "description": "Dispatch Susan's research pipeline — web, arxiv, reddit, appstore researchers",
      "parameters": {
        "topic": { "type": "string", "description": "Research topic" },
        "sources": { "type": "array", "description": "Sources to search: web, arxiv, reddit, appstore" }
      }
    }
  ]
}
```

**Step 2: Create handler that bridges to Susan MCP**

```typescript
// pai/skills/susan-mcp/handler.ts
// OpenClaw skill handler — proxies requests to Susan MCP server

import { execSync } from "child_process";

const SUSAN_BACKEND = "/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend";
const VENV_PYTHON = `${SUSAN_BACKEND}/.venv/bin/python`;

interface ToolCall {
  name: string;
  parameters: Record<string, any>;
}

export async function handle(tool: ToolCall): Promise<string> {
  const { name, parameters } = tool;

  switch (name) {
    case "susan_search": {
      const cmd = `${VENV_PYTHON} -c "
from rag_engine.retrieval import RAGRetriever
r = RAGRetriever()
results = r.search('${parameters.query.replace(/'/g, "\\'")}', top_k=${parameters.limit || 5})
for doc in results:
    print(f'---')
    print(doc.page_content[:300])
    print(f'Source: {doc.metadata.get(\"source\", \"unknown\")}')
"`;
      return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 30000 }).toString();
    }

    case "susan_agent": {
      const cmd = `${VENV_PYTHON} scripts/susan_cli.py route ${parameters.company || "startup-intelligence-os"} "${parameters.prompt.replace(/"/g, '\\"')}" --agent ${parameters.agent}`;
      return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 60000 }).toString();
    }

    case "susan_foundry": {
      const cmd = `${VENV_PYTHON} scripts/susan_cli.py ${parameters.mode || "foundry"} ${parameters.company}`;
      return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 60000 }).toString();
    }

    case "susan_research": {
      const sources = (parameters.sources || ["web"]).join(",");
      const cmd = `${VENV_PYTHON} -m research_daemon --command harvest --topic "${parameters.topic.replace(/"/g, '\\"')}" --sources ${sources}`;
      return execSync(cmd, { cwd: SUSAN_BACKEND, timeout: 120000 }).toString();
    }

    default:
      return `Unknown tool: ${name}`;
  }
}
```

**Step 3: Install skill in OpenClaw**

```bash
openclaw skills install ./pai/skills/susan-mcp
openclaw skills list
```

Expected: `susan-mcp` shows as installed with 4 tools.

**Step 4: Test from Telegram**

Send: "Jake, search Susan's knowledge base for Oracle Health competitive landscape"

Expected: Susan RAG results returned through OpenClaw → Claude Code → Telegram.

**Step 5: Commit**

```bash
git add pai/skills/susan-mcp/
git commit -m "feat(pai): Susan MCP as OpenClaw skill — 82 agents, RAG search, foundry, research pipeline"
```

---

### Task 2: Bridge All 16 MCP Servers via mcporter

**Files:**
- Create: `pai/config/mcporter.json`

**Step 1: Document current MCP server inventory**

From `.mcp.json` and `~/.claude/mcp.json`, catalog all MCP servers:

```bash
cat .mcp.json 2>/dev/null
cat ~/.claude/mcp.json 2>/dev/null
```

Expected servers (from design doc): Susan, filesystem, git, GitHub, Supabase, Brave Search, Notion, Google Calendar, Gmail, Slack, memory, sequential-thinking, context7, and others.

**Step 2: Create mcporter config**

```json
{
  "name": "jake-mcp-bridge",
  "description": "Bridges all MCP servers into OpenClaw as tools",
  "servers": {
    "susan": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend",
      "env": { "PYTHONPATH": "." }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-filesystem"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-brave-search"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-memory"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-sequential-thinking"]
    }
  },
  "openclaw": {
    "expose_as": "tools",
    "prefix": "mcp_",
    "gateway": "ws://127.0.0.1:18789"
  }
}
```

**Step 3: Install mcporter**

```bash
npm install -g mcporter@latest
mcporter start --config pai/config/mcporter.json
```

**Step 4: Verify MCP tools available in OpenClaw**

```bash
openclaw tools list | grep mcp_
```

Expected: All MCP server tools prefixed with `mcp_` available.

**Step 5: Commit**

```bash
git add pai/config/mcporter.json
git commit -m "feat(pai): mcporter bridge config — 16 MCP servers exposed as OpenClaw tools"
```

---

### Task 3: Configure Fabric Pattern Integration

**Files:**
- Create: `pai/skills/fabric/skill.json`
- Create: `pai/skills/fabric/handler.ts`
- Create: `pai/config/fabric-patterns-top50.json`

**Step 1: Curate top 50 Fabric patterns for PAI**

```json
{
  "patterns": {
    "analysis": [
      "analyze_claims", "analyze_risk", "analyze_sales_call",
      "analyze_threat_report", "analyze_personality"
    ],
    "extraction": [
      "extract_ideas", "extract_insights", "extract_wisdom",
      "extract_article_wisdom", "extract_book_ideas",
      "extract_controversial_ideas", "extract_main_idea",
      "extract_patterns", "extract_predictions", "extract_references"
    ],
    "summarization": [
      "summarize", "summarize_debate", "summarize_meeting",
      "summarize_newsletter", "summarize_paper", "summarize_rpg_session"
    ],
    "creation": [
      "create_keynote", "create_markmap_visualization",
      "create_mermaid_visualization", "create_micro_summary",
      "create_network_threat_landscape", "create_summary"
    ],
    "thinking": [
      "t_red_team_thinking", "t_find_blindspots",
      "t_steel_man", "t_devil_advocate",
      "t_first_principles", "t_second_order"
    ],
    "improvement": [
      "improve_prompt", "improve_writing",
      "improve_academic_writing", "improve_report_finding"
    ],
    "rating": [
      "rate_ai_result", "rate_ai_response",
      "rate_content", "rate_value"
    ],
    "utility": [
      "clean_text", "label_and_rate",
      "write_essay", "write_micro_essay",
      "get_wow_per_minute", "find_logical_fallacies"
    ]
  },
  "model_routing": {
    "cheap": ["summarize", "clean_text", "extract_ideas", "extract_main_idea", "create_micro_summary"],
    "mid": ["analyze_claims", "analyze_risk", "improve_writing", "rate_content", "summarize_meeting"],
    "expensive": ["extract_wisdom", "t_red_team_thinking", "t_find_blindspots", "analyze_personality", "t_first_principles"]
  }
}
```

**Step 2: Create Fabric OpenClaw skill**

```json
{
  "name": "fabric",
  "version": "1.0.0",
  "description": "Run Fabric prompt patterns — 233 patterns with per-pattern model routing",
  "tools": [
    {
      "name": "fabric_run",
      "description": "Execute a Fabric pattern on input text",
      "parameters": {
        "pattern": { "type": "string", "description": "Pattern name (e.g., summarize, extract_wisdom, t_red_team_thinking)" },
        "input": { "type": "string", "description": "Input text to process" },
        "model": { "type": "string", "description": "Override model (optional — defaults to per-pattern routing)" }
      }
    },
    {
      "name": "fabric_pipe",
      "description": "Chain multiple Fabric patterns in sequence (pipe output of one to input of next)",
      "parameters": {
        "patterns": { "type": "array", "description": "Pattern names in order" },
        "input": { "type": "string", "description": "Initial input text" }
      }
    },
    {
      "name": "fabric_list",
      "description": "List available Fabric patterns",
      "parameters": {
        "category": { "type": "string", "description": "Filter by category (optional)" }
      }
    }
  ]
}
```

**Step 3: Create handler**

```typescript
// pai/skills/fabric/handler.ts
import { execSync } from "child_process";
import { readFileSync } from "fs";

const FABRIC_API = "http://localhost:8080";
const MODEL_CONFIG = JSON.parse(
  readFileSync("pai/config/fabric-patterns-top50.json", "utf-8")
);

function getModelForPattern(pattern: string): string {
  const routing = MODEL_CONFIG.model_routing;
  if (routing.cheap.includes(pattern)) return "openai/gpt-5.4-mini";
  if (routing.mid.includes(pattern)) return "Anthropic/claude-sonnet-4-6";
  if (routing.expensive.includes(pattern)) return "Anthropic/claude-opus-4-6";
  return "openai/gpt-5.4"; // Default
}

export async function handle(tool: any): Promise<string> {
  switch (tool.name) {
    case "fabric_run": {
      const model = tool.parameters.model || getModelForPattern(tool.parameters.pattern);
      const cmd = `echo '${tool.parameters.input.replace(/'/g, "\\'")}' | fabric --pattern ${tool.parameters.pattern} --model ${model}`;
      return execSync(cmd, { timeout: 60000 }).toString();
    }

    case "fabric_pipe": {
      let output = tool.parameters.input;
      for (const pattern of tool.parameters.patterns) {
        const model = getModelForPattern(pattern);
        const cmd = `echo '${output.replace(/'/g, "\\'")}' | fabric --pattern ${pattern} --model ${model}`;
        output = execSync(cmd, { timeout: 60000 }).toString();
      }
      return output;
    }

    case "fabric_list": {
      const cmd = "fabric --listpatterns";
      return execSync(cmd, { timeout: 10000 }).toString();
    }

    default:
      return `Unknown tool: ${tool.name}`;
  }
}
```

**Step 4: Install and test**

```bash
openclaw skills install ./pai/skills/fabric
```

Test: Send Telegram message: "Jake, run extract_wisdom on this: [paste article text]"

**Step 5: Commit**

```bash
git add pai/skills/fabric/ pai/config/fabric-patterns-top50.json
git commit -m "feat(pai): Fabric as OpenClaw skill — 50 curated patterns, per-pattern model routing, pipe chains"
```

---

## Phase 2B: Algorithm v1 (Core Reasoning Engine)

*Adapt Miessler's 7-phase Algorithm for Jake's PAI.*

### Task 4: Implement Algorithm v1

**Files:**
- Create: `pai/algorithm/v1.0.0.md`
- Create: `pai/algorithm/ISC.md`

**Step 1: Create Algorithm v1 specification**

```markdown
# The Algorithm v1.0.0 — Jake's Reasoning Engine

Adapted from Daniel Miessler's Algorithm v3.7.0 for Jake PAI.

## Seven Phases (Mandatory, Sequential)

### Phase 1: OBSERVE
**Purpose:** Gather context, extract constraints, self-interrogate
**Actions:**
1. Read the user's request completely
2. Load relevant TELOS files (MISSION, GOALS, PROJECTS, CHALLENGES)
3. Search PAI memory (LosslessClaw + Supabase) for related context
4. Identify explicit and implicit constraints
5. Note what's NOT said (gaps, assumptions)
**Output:** Structured observation with constraints and gaps identified

### Phase 2: THINK
**Purpose:** Analyze, select capabilities, verification rehearsal
**Actions:**
1. Identify which Susan agents are relevant
2. Determine which Fabric patterns apply
3. Select model tier (cheap/mid/expensive) based on complexity
4. Run a mental verification rehearsal — "If I do X, will it achieve Y?"
5. Validate against AI Steering Rules
**Output:** Capability selection + verification plan

### Phase 3: PLAN
**Purpose:** Build Ideal State Criteria (ISC), persistent PRD
**Actions:**
1. Write 8-12 ISC criteria (see ISC.md)
2. Each criterion: exactly 8-12 words
3. Tag confidence: [E]xplicit, [I]nferred, [R]everse-engineered
4. Define anti-criteria (ISC-A-*) for prohibited states
5. Create PRD in MEMORY/WORK/ if task is multi-step
**Output:** ISC criteria document + PRD (if needed)

### Phase 4: BUILD
**Purpose:** Construct solution artifacts, prevent build drift
**Actions:**
1. Build artifacts one at a time
2. After each artifact, check against ISC criteria
3. If drifting from ISC, stop and re-plan
4. Use Fabric patterns where applicable
5. Use Susan agents for specialized subtasks
**Output:** Solution artifacts

### Phase 5: EXECUTE
**Purpose:** Take action, track against criteria
**Actions:**
1. Execute the plan step by step
2. Track which ISC criteria are satisfied
3. If unexpected result, pause and re-assess (don't brute force)
4. Commit at logical checkpoints
**Output:** Executed actions with ISC tracking

### Phase 6: VERIFY
**Purpose:** Confirm each ISC criterion with evidence
**Actions:**
1. Go through each ISC criterion
2. Provide concrete evidence of satisfaction
3. Mark as PASS/FAIL/PARTIAL
4. If any FAIL, return to BUILD or PLAN
5. Run tests if code was written
**Output:** Verification matrix with evidence

### Phase 7: LEARN
**Purpose:** Capture insights, write structured reflection
**Actions:**
1. What went well?
2. What was unexpected?
3. What would we do differently?
4. Update TELOS files if warranted (LEARNED.md, WRONG.md)
5. Write learning extract to MEMORY/LEARNING/
6. Capture rating (1-5)
**Output:** Learning file in MEMORY/LEARNING/

## When to Use the Full Algorithm
- Multi-step tasks (3+ steps)
- Tasks touching >3 files
- Architectural decisions
- Anything Mike says "plan this"

## When to Skip (Quick Response Mode)
- Simple questions ("What time is it?")
- Single-file edits with clear instructions
- Status checks
- Casual conversation
```

**Step 2: Create ISC methodology doc**

```markdown
# ISC — Ideal State Criteria

## Format
Each criterion follows this exact format:
```
ISC-C{N} [{Confidence}] {Description in 8-12 words} | Verify: {Method}
```

## Confidence Tags
- **[E]** — Explicit: User stated this directly
- **[I]** — Inferred: Logically follows from what user said
- **[R]** — Reverse-engineered: Deduced from context/domain knowledge

## Anti-Criteria
Prohibited states that MUST NOT be true:
```
ISC-A-{N} {Description} | Verify: {Method}
```

## Example
Task: "Add dark mode to the dashboard"

```
ISC-C1 [E] Dashboard supports both light and dark color themes | Verify: Toggle switch works
ISC-C2 [I] User preference persists across browser sessions | Verify: Reload retains theme
ISC-C3 [I] All text maintains WCAG AA contrast in both modes | Verify: Lighthouse audit
ISC-C4 [R] No flash of wrong theme on page load | Verify: Fresh load in each mode
ISC-C5 [I] System theme preference detected on first visit | Verify: prefers-color-scheme
ISC-A-1 No hardcoded color values in component files | Verify: grep for hex codes
ISC-A-2 No broken layouts when switching themes | Verify: Visual regression test
```

## Rules
1. Exactly 8-12 words per criterion description
2. Binary testable — every criterion has a clear PASS/FAIL
3. Evidence required — VERIFY field must name concrete method
4. Define BEFORE building — criteria are set in PLAN phase
5. Anti-criteria catch edge cases — what MUST NOT happen
```

**Step 3: Commit**

```bash
git add pai/algorithm/
git commit -m "feat(pai): Algorithm v1.0.0 — 7-phase reasoning engine + ISC methodology, adapted from Miessler v3.7.0"
```

---

### Task 5: Create Inference Config (Model Routing)

**Files:**
- Create: `pai/config/inference.json`

**Step 1: Define model routing hierarchy**

```json
{
  "version": "1.0.0",
  "description": "PAI model routing — adapted from Miessler's Inference.ts",
  "routing_hierarchy": [
    "CODE",
    "CLI_TOOL",
    "PROMPT",
    "SKILL",
    "AGENT"
  ],
  "models": {
    "nano": {
      "id": "openai/gpt-5.4-nano",
      "cost_per_msg": 0.001,
      "use_for": ["classification", "intent_routing", "urgency_scoring", "tagging"]
    },
    "cheap": {
      "id": "openai/gpt-5.4-mini",
      "cost_per_msg": 0.005,
      "use_for": ["summarization", "extraction", "text_cleanup", "simple_patterns"]
    },
    "mid": {
      "id": "claude-sonnet-4-6",
      "cost_per_msg": 0.03,
      "use_for": ["analysis", "agent_tasks", "research", "writing", "code_review"]
    },
    "expensive": {
      "id": "claude-opus-4-6",
      "cost_per_msg": 0.15,
      "use_for": ["strategic_reasoning", "architecture", "complex_planning", "multi_step_tasks"]
    }
  },
  "rules": [
    {
      "condition": "message_length < 50 AND no_tool_use",
      "model": "nano",
      "reason": "Quick classification or ack"
    },
    {
      "condition": "fabric_pattern IN cheap_patterns",
      "model": "cheap",
      "reason": "Cheap Fabric patterns"
    },
    {
      "condition": "susan_agent_invoked",
      "model": "mid",
      "reason": "Susan agent tasks need mid-tier"
    },
    {
      "condition": "algorithm_triggered OR multi_step OR architecture",
      "model": "expensive",
      "reason": "Full Algorithm needs Opus"
    },
    {
      "condition": "mike_direct_message",
      "model": "expensive",
      "reason": "Full Jake for Mike — always Opus (Mike's mandate)"
    }
  ],
  "override": {
    "always_opus_for": ["mike_telegram", "mike_claude_code"],
    "reason": "Mike's mandate: Full Jake all the time"
  }
}
```

**Step 2: Commit**

```bash
git add pai/config/inference.json
git commit -m "feat(pai): inference config — 4-tier model routing with Mike's Full Jake override"
```

---

### Task 6: Create Agent Registry (Callable from OpenClaw)

**Files:**
- Create: `pai/agents/registry.json`
- Create: `pai/agents/README.md`

**Step 1: Build agent registry from Susan's 82 agents**

```bash
# Generate registry from agent files
cd susan-team-architect/agents
ls *.md | sed 's/.md$//' | while read agent; do
    echo "  \"$agent\": {"
    head -5 "$agent.md" | grep -i "role\|purpose\|description" | head -1 | sed 's/^/    "description": "/' | sed 's/$/"/'
    echo "  },"
done
```

Create `pai/agents/registry.json`:

```json
{
  "version": "1.0.0",
  "total_agents": 82,
  "groups": {
    "orchestration": ["susan"],
    "strategy": ["steve-strategy", "shield-legal-compliance", "bridge-partnerships", "ledger-finance", "vault-fundraising", "recruiting-strategy-studio"],
    "product": ["marcus-ux", "mira-emotional-experience", "compass-product", "ai-product-manager", "conversation-designer", "echo-neuro-design", "lens-accessibility", "prism-brand"],
    "engineering": ["atlas-engineering", "nova-ai", "pulse-data-science", "sentinel-security", "forge-qa", "knowledge-engineer", "ai-evaluation-specialist", "algorithm-lab"],
    "science": ["coach-exercise-science", "sage-nutrition", "drift-sleep-recovery", "workout-program-studio", "coaching-architecture-studio"],
    "psychology": ["freya-behavioral-economics", "flow-sports-psychology", "quest-gamification"],
    "growth": ["aria-growth", "haven-community", "guide-customer-success", "herald-pr", "beacon-aso", "coach-outreach-studio", "x-growth-studio"],
    "research": ["research-director", "research-ops", "training-research-studio", "researcher-web", "researcher-arxiv", "researcher-reddit", "researcher-appstore"],
    "studio": ["deck-studio", "design-studio-director", "landing-page-studio", "app-experience-studio", "marketing-studio-director", "article-studio", "memo-studio", "social-media-studio", "whitepaper-studio", "instagram-studio", "recruiting-dashboard-studio", "photography-studio"],
    "film_studio": ["film-studio-director", "screenwriter-studio", "cinematography-studio", "editing-studio", "color-grade-studio", "vfx-studio", "sound-design-studio", "music-score-studio", "production-designer-studio", "production-manager-studio", "talent-cast-studio", "distribution-studio", "legal-rights-studio", "highlight-reel-studio", "audio-gen-engine", "film-gen-engine", "image-gen-engine"]
  },
  "routing": {
    "strategy_question": ["steve-strategy", "shield-legal-compliance"],
    "product_question": ["compass-product", "marcus-ux"],
    "technical_question": ["atlas-engineering", "nova-ai"],
    "research_request": ["research-director", "researcher-web"],
    "competitive_intel": ["herald-pr", "aria-growth"],
    "content_creation": ["article-studio", "deck-studio", "social-media-studio"],
    "financial_question": ["ledger-finance", "vault-fundraising"],
    "security_concern": ["sentinel-security", "shield-legal-compliance"],
    "fitness_question": ["coach-exercise-science", "workout-program-studio"]
  }
}
```

**Step 2: Commit**

```bash
git add pai/agents/
git commit -m "feat(pai): agent registry — 82 agents mapped across 9 groups with intent routing"
```

---

## Phase 2C: Claude Code Bridge Optimization

### Task 7: Optimize openclaw-claude-code-skill Configuration

**Step 1: Verify bridge is working (from V0)**

```bash
openclaw skills info openclaw-claude-code-skill
```

**Step 2: Configure session persistence**

Ensure the bridge:
- Reuses the same tmux session (jake-brain)
- Passes TELOS context on session start
- Passes PAI retriever results for memory queries
- Returns structured responses (not raw Claude Code output)

**Step 3: Configure response formatting**

Create `pai/config/response-format.json`:

```json
{
  "telegram": {
    "max_length": 4096,
    "format": "markdown",
    "truncation": "smart",
    "footer": false
  },
  "slack": {
    "max_length": 3000,
    "format": "mrkdwn",
    "truncation": "smart",
    "footer": true
  },
  "discord": {
    "max_length": 2000,
    "format": "markdown",
    "truncation": "hard",
    "footer": false
  }
}
```

**Step 4: Commit**

```bash
git add pai/config/response-format.json
git commit -m "feat(pai): channel response formatting config — per-channel length and format rules"
```

---

## Phase 2D: Verification

### Task 8: End-to-End Agent Integration Verification

**Files:**
- Create: `pai/verification/v2-test-results.md`

**Step 1: Test Susan agent invocation from Telegram**

Send: "Jake, have Steve do a strategy review of our Oracle Health positioning"

Expected: Message routes through OpenClaw → Claude Code → Susan MCP → steve-strategy agent → structured strategy output → Telegram response.

**Step 2: Test Fabric pattern execution from Telegram**

Send: "Jake, run t_red_team_thinking on this plan: [paste plan text]"

Expected: Fabric pattern executes with claude-opus-4-6 model, returns red team analysis.

**Step 3: Test Fabric pipe chain**

Send: "Jake, pipe this article through summarize then extract_wisdom: [paste article]"

Expected: Two patterns execute in sequence, second receives output of first.

**Step 4: Test Algorithm v1 on a multi-step task**

Send: "Jake, plan a competitive analysis of our Alex Recruiting platform"

Expected: Jake uses Algorithm phases (OBSERVE, THINK, PLAN), references ISC criteria, invokes relevant agents (research-director, herald-pr, steve-strategy).

**Step 5: Test model routing**

- Send simple: "Hey Jake" → Should route to cheap model (quick ack)
- Send complex: "Jake, what's the optimal go-to-market strategy for PAI as a product?" → Should route to Opus

**Step 6: Document results**

```bash
git add pai/verification/v2-test-results.md
git commit -m "feat(pai): V2 agent integration verification complete"
```

---

## V2 Exit Criteria (All Must Pass)

- [ ] Susan MCP callable as OpenClaw skill (search, agent, foundry, research)
- [ ] mcporter bridges all MCP servers into OpenClaw
- [ ] Fabric top 50 patterns callable with per-pattern model routing
- [ ] Fabric pipe chains work (output of one → input of next)
- [ ] Algorithm v1 spec written and referenced in session context
- [ ] ISC methodology documented and usable
- [ ] Inference config defines 4-tier model routing
- [ ] Agent registry maps all 82 agents across 9 groups
- [ ] Intent routing maps user intents to agent groups
- [ ] Claude Code bridge optimized (session reuse, TELOS context, structured responses)
- [ ] Channel response formatting configured (Telegram, Slack, Discord)
- [ ] End-to-end: Telegram → OpenClaw → Susan agent → Fabric pattern → response
- [ ] All 82 agents callable from any channel
- [ ] All 16 MCP servers connected via mcporter

**Score target: 50 → 60** (full agent roster online, patterns callable, reasoning engine active)
