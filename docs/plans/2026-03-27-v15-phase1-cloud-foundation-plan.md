# V15 Phase 1: Cloud Foundation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Jake lives on Cloudflare edge. SuperMemory.ai is his brain. OpenClaw v2026.3.24 is his runtime. Paperclip orchestrates. Any device can talk to Jake.

**Architecture:** Cloudflare Workers as always-on gateway, SuperMemory.ai as universal memory API, OpenClaw as agent runtime, Paperclip as multi-company orchestration. Local machines connect via Cloudflare Tunnel as "muscles" for heavy compute.

**Tech Stack:** Cloudflare (Workers, R2, KV, Zero Trust, Tunnel), OpenClaw v2026.3.24, SuperMemory.ai, Paperclip, QMD, Node.js 24, TypeScript

**Parent Design:** `docs/plans/2026-03-27-v15-personal-ai-infrastructure-design.md` (R3)

**Estimated Sessions:** 3-4

---

## Prerequisites

Before starting Phase 1, verify:
- [ ] Node.js 24 is installed (`node -v`)
- [ ] npm is current (`npm -v`)
- [ ] Cloudflare account exists (sign up at dash.cloudflare.com)
- [ ] SuperMemory.ai account exists (sign up at supermemory.ai)
- [ ] Obsidian is installed on desktop + laptop
- [ ] Git is configured on both machines

---

## Task 1: Install OpenClaw v2026.3.24

**Files:**
- Modify: `~/.openclaw/` (config directory, created by installer)
- Reference: `docs/plans/2026-03-27-v15-personal-ai-infrastructure-design.md`

**Step 1: Check Node.js version**

```bash
node -v
# Expected: v24.x.x (minimum 22.14)
# If not: brew install node@24
```

**Step 2: Install OpenClaw globally**

```bash
npm i -g openclaw
```

**Step 3: Verify installation**

```bash
openclaw --version
# Expected: v2026.3.24 or later
```

**Step 4: Run initial setup**

```bash
openclaw
# Follow interactive setup wizard
# Configure: model provider (Anthropic), API key, gateway settings
```

**Step 5: Verify gateway starts**

```bash
openclaw gateway
# Expected: Gateway running on http://localhost:18789
# Ctrl+C to stop (we'll move this to Cloudflare in Task 3)
```

**Step 6: Commit checkpoint**

```bash
# No code changes to commit — this is a system install
# Verify by running: openclaw status
```

---

## Task 2: Set Up Cloudflare Account + Services

**Files:**
- Create: `.cloudflare/` (local config reference, gitignored)
- Modify: `.gitignore` (add .cloudflare/)

**Step 1: Create Cloudflare account (if not exists)**

Go to `dash.cloudflare.com` and sign up. Free plan is sufficient to start.

**Step 2: Install Wrangler CLI**

```bash
npm i -g wrangler
wrangler login
# Browser opens for auth
```

**Step 3: Verify Wrangler auth**

```bash
wrangler whoami
# Expected: Shows account name and ID
```

**Step 4: Create R2 bucket for Jake's state**

```bash
wrangler r2 bucket create jake-state
# Expected: Bucket created successfully
```

**Step 5: Create KV namespace for hot cache**

```bash
wrangler kv namespace create JAKE_CACHE
# Expected: Returns namespace ID — save this
```

**Step 6: Set up Cloudflare Tunnel to desktop**

```bash
# Install cloudflared
brew install cloudflared
cloudflared tunnel login
# Browser opens for auth

# Create tunnel
cloudflared tunnel create jake-desktop
# Expected: Returns tunnel ID and credentials file path — save both

# Configure tunnel to route to local OpenClaw gateway
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: <TUNNEL_ID>
credentials-file: /Users/mikerodgers/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: jake.yourdomain.com
    service: http://localhost:18789
  - service: http_status:404
EOF
```

**Step 7: Add .cloudflare to gitignore**

```bash
echo ".cloudflare/" >> .gitignore
echo ".cloudflared/" >> .gitignore
```

**Step 8: Document config (local reference)**

```bash
mkdir -p .cloudflare
cat > .cloudflare/README.md << 'EOF'
# Cloudflare Config Reference (DO NOT COMMIT SECRETS)
- R2 Bucket: jake-state
- KV Namespace: JAKE_CACHE (ID in Cloudflare dashboard)
- Tunnel: jake-desktop (ID in ~/.cloudflared/)
- Zero Trust: Configure at dash.teams.cloudflare.com
EOF
```

---

## Task 3: Deploy OpenClaw Gateway on Cloudflare Workers

**Files:**
- Create: `infrastructure/cloudflare-worker/` (worker project)
- Create: `infrastructure/cloudflare-worker/wrangler.toml`
- Create: `infrastructure/cloudflare-worker/src/index.ts`

**Step 1: Create worker project directory**

```bash
mkdir -p infrastructure/cloudflare-worker
cd infrastructure/cloudflare-worker
```

**Step 2: Initialize Wrangler project**

```bash
wrangler init jake-gateway --type javascript
# Or use the Moltworker pattern from ogwilliam's guide
```

**Step 3: Configure wrangler.toml**

```toml
name = "jake-gateway"
main = "src/index.ts"
compatibility_date = "2026-03-27"

[vars]
ENVIRONMENT = "production"

[[r2_buckets]]
binding = "JAKE_STATE"
bucket_name = "jake-state"

[[kv_namespaces]]
binding = "JAKE_CACHE"
id = "<KV_NAMESPACE_ID>"
```

**Step 4: Write gateway worker**

The gateway worker proxies requests to the OpenClaw gateway running on the desktop (via Cloudflare Tunnel) and adds Zero Trust auth.

```typescript
// src/index.ts
export default {
  async fetch(request: Request, env: any): Promise<Response> {
    // Cloudflare Zero Trust handles auth before request reaches here
    // Proxy to OpenClaw gateway on desktop via tunnel
    const url = new URL(request.url);
    url.hostname = 'jake.yourdomain.com'; // Tunnel hostname

    return fetch(new Request(url.toString(), request));
  }
};
```

> **Note**: The exact implementation depends on whether we run OpenClaw natively on Workers (stateless, edge-first) or proxy to the desktop gateway via Tunnel. Research the Moltworker pattern further during execution. The worker approach may evolve.

**Step 5: Deploy worker**

```bash
wrangler deploy
# Expected: Deployed to https://jake-gateway.<account>.workers.dev
```

**Step 6: Test from browser**

Open `https://jake-gateway.<account>.workers.dev` — should see OpenClaw dashboard or proxy response.

---

## Task 4: Configure Cloudflare Zero Trust

**Step 1: Go to Cloudflare Zero Trust dashboard**

Navigate to `dash.teams.cloudflare.com`

**Step 2: Create an Access Application**

- Name: "Jake PA"
- Type: Self-hosted
- Domain: `jake-gateway.<account>.workers.dev`
- Session duration: 24 hours

**Step 3: Add Access Policy**

- Policy name: "Mike Only"
- Include: Email = mike@mikerodgers.com (or whatever email)
- Authentication method: Google / GitHub / One-time PIN

**Step 4: Verify auth works**

Open the worker URL in an incognito browser. Should see Cloudflare login page. After auth, should see OpenClaw.

**Step 5: Test from phone**

Open the same URL on your phone browser. Should get auth prompt, then Jake.

---

## Task 5: Sign Up SuperMemory.ai + Configure

**Files:**
- Modify: `~/.openclaw/openclaw.json` (add SuperMemory MCP config)
- Reference: SuperMemory.ai dashboard

**Step 1: Sign up for SuperMemory Pro ($19/mo)**

Go to `supermemory.ai`, create account, subscribe to Pro plan.

**Step 2: Get API key**

From SuperMemory dashboard → Settings → API Keys → Create new key. Save it.

**Step 3: Install SuperMemory MCP server**

```bash
# Check if SuperMemory has a Claude Code plugin
# If yes:
claude plugin add supermemoryai/claude-supermemory

# If MCP config needed, add to .mcp.json:
```

**Step 4: Configure SuperMemory connectors**

In SuperMemory dashboard:
- Connect Gmail (OAuth)
- Connect Notion (API key)
- Connect GitHub (OAuth)
- Connect Google Drive (OAuth)

**Step 5: Create container tags for agent isolation**

Via SuperMemory API or dashboard:
- `jake` — Jake's personal memories
- `shared` — Cross-agent shared knowledge
- `oracle-health` — Oracle Health company memories
- `alex-recruiting` — Alex Recruiting company memories
- `startup-os` — Startup Intelligence OS memories

**Step 6: Test memory write + read**

```bash
# Via SuperMemory API or MCP:
# Write a test memory
# Read it back
# Verify it appears in dashboard
```

**Step 7: Verify auto-sync**

Wait 5-10 minutes after connecting Gmail. Check SuperMemory dashboard for ingested email content.

---

## Task 6: Install Paperclip

**Files:**
- Create: `~/.paperclip/` (Paperclip config directory)

**Step 1: Install Paperclip**

```bash
npx paperclipai onboard
# Follow interactive setup wizard
```

**Step 2: Configure 3 companies**

In Paperclip dashboard:
1. Create company: "Startup Intelligence OS"
2. Create company: "Oracle Health AI Enablement"
3. Create company: "Alex Recruiting"

**Step 3: Add Jake as first agent**

In Paperclip, register Jake:
- Name: Jake
- Role: Chief of Staff / Lead PA
- Company: All 3 (cross-company)
- Adapter: openclaw-gateway
- Budget: $50/mo (initial, adjustable)
- Heartbeat: every 15 minutes (while active), every 1 hour (background)

**Step 4: Verify Paperclip dashboard**

Open Paperclip UI — should show 3 companies, Jake as the first agent.

**Step 5: Test heartbeat**

Wait for Jake's heartbeat to fire. Check Paperclip logs for heartbeat activity.

---

## Task 7: Install QMD

**Files:**
- Modify: `.mcp.json` (add QMD MCP config if needed)

**Step 1: Install QMD as Claude Code plugin**

```bash
claude plugin add tobi/qmd
```

**Step 2: Configure QMD to index Obsidian vault**

```bash
# Point QMD at your Obsidian vault directory
qmd index ~/Documents/Obsidian/  # or wherever your vault is
```

**Step 3: Verify search works**

```bash
qmd query "Jake architecture"
# Expected: Returns relevant results from Obsidian vault
```

**Step 4: Test MCP integration**

From Claude Code, use QMD's MCP tools to search. Should return results.

---

## Task 8: Set Up Obsidian Vault Structure

**Files:**
- Create: Obsidian vault directory with standard structure

**Step 1: Create vault (if not exists)**

```bash
mkdir -p ~/Documents/Obsidian/Jake-Brain
cd ~/Documents/Obsidian/Jake-Brain
git init
```

**Step 2: Create vault structure**

```bash
mkdir -p People Projects Companies Decisions "Daily Notes" Reference Agents
```

**Step 3: Create initial notes from existing memory**

Migrate key knowledge from `~/.claude/projects/-Users-mikerodgers-Startup-Intelligence-OS/memory/` to Obsidian:

- `user_mike_profile.md` → `People/Mike Rodgers.md`
- `jake_personality.md` → `Agents/Jake.md`
- `user_multi_company.md` → `Reference/Multi-Company Structure.md`
- `project_portfolio_full.md` → `Projects/Portfolio Overview.md`

**Step 4: Initialize Git for sync**

```bash
cd ~/Documents/Obsidian/Jake-Brain
git add .
git commit -m "feat(obsidian): initialize Jake Brain vault with migrated knowledge"
```

**Step 5: Set up Git remote for cross-device sync**

```bash
# Create private GitHub repo
gh repo create jake-brain --private
git remote add origin git@github.com:mikerodgers/jake-brain.git
git push -u origin main
```

**Step 6: Clone on laptop**

On laptop:
```bash
cd ~/Documents/Obsidian/
git clone git@github.com:mikerodgers/jake-brain.git Jake-Brain
# Open in Obsidian
```

---

## Task 9: Migrate Jake Config from Hermes to OpenClaw

**Files:**
- Modify: `~/.openclaw/` (agent config, skills, memory)
- Reference: `~/.hermes/` (existing Jake config)

**Step 1: Export Jake's personality from Hermes**

```bash
cat ~/.hermes/SOUL.md
# Copy personality definition
```

**Step 2: Create OpenClaw agent config**

Write Jake's identity into OpenClaw's config format, adapting from SOUL.md + our jake.md rules.

**Step 3: Migrate skills**

Identify which Hermes skills map to OpenClaw skills. Install equivalents from ClawHub or create custom.

Priority skills to migrate:
- `/jake-brief` → OpenClaw daily brief skill
- `/oracle-health-intel` → OpenClaw Oracle Health skill
- `/email-triage` → OpenClaw email skill
- `/jake-recall` → Replace with SuperMemory MCP

**Step 4: Configure SuperMemory as Jake's memory**

Replace Hermes memory config with SuperMemory API integration.

**Step 5: Test Jake responds**

Send a message via Telegram → Jake on OpenClaw (Cloudflare) → responds with personality intact.

**Step 6: Keep Hermes running in parallel**

Do NOT shut down Hermes yet. Run both in parallel until OpenClaw proves stable.

---

## Task 10: Multi-Device Verification

**Step 1: Test from Mac Desktop**

- Open Cloudflare URL in browser → Jake responds
- Send Telegram message → Jake responds
- Use Claude Code → Jake's memory accessible via SuperMemory MCP

**Step 2: Test from Laptop**

- Open same Cloudflare URL → Jake responds (same context)
- Send Telegram message → Jake responds
- Obsidian vault synced via Git

**Step 3: Test from Phone**

- Open Cloudflare URL in mobile browser → Jake responds
- Send Telegram message → Jake responds

**Step 4: Test continuity**

- Start a conversation on desktop
- Continue it on laptop
- Verify Jake remembers the desktop conversation (via SuperMemory)

**Step 5: Test with desktop OFF**

- Close laptop, shut down desktop
- Send Telegram message from phone
- Jake should STILL respond (Cloudflare gateway is always-on)

---

## Phase 1 Exit Criteria

All of these must pass before moving to Phase 2:

- [ ] OpenClaw v2026.3.24 installed and running
- [ ] Cloudflare Workers deployed with Jake gateway
- [ ] Cloudflare Zero Trust auth working (only Mike can access)
- [ ] Cloudflare Tunnel connecting to desktop for local compute
- [ ] SuperMemory.ai Pro active with Gmail, Notion, GitHub, Drive connected
- [ ] SuperMemory container tags created for agent isolation
- [ ] Paperclip running with 3 companies configured
- [ ] Jake registered as first agent in Paperclip
- [ ] QMD installed and indexing Obsidian vault
- [ ] Obsidian vault created with migrated knowledge
- [ ] Obsidian Git-synced between desktop and laptop
- [ ] Jake responds from desktop, laptop, and phone
- [ ] Jake responds when desktop is OFF (cloud-only test)
- [ ] Jake's personality intact after migration from Hermes
- [ ] Hermes running in parallel as fallback

---

## Phase 1 → Phase 2 Handoff

When Phase 1 is complete, the next session starts Phase 2: Superagent Wave 1 + Memory.

Phase 2 focus:
- Wire SuperMemory MCP to all agents
- Upgrade Jake, KIRA, ARIA, SCOUT, Steve, Compass to full superagents
- Install lossless-claw for infinite context
- Configure heartbeat scheduling via Paperclip
- Test full memory lifecycle (ingest → search → decay → contradiction → cross-agent recall)

**Phase 2 plan will be written at the start of the Phase 2 session** with the same bite-sized task format.
