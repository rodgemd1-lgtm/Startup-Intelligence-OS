#!/usr/bin/env python3
"""
Wave 3 Batch Agent Registration for OpenClaw
Reads Susan agent definitions and registers them in OpenClaw.
"""

import os
import re
import subprocess
import json
import yaml

SUSAN_AGENTS_DIR = os.path.expanduser("~/Startup-Intelligence-OS/susan-team-architect/agents")
CLAUDE_AGENTS_DIR = os.path.expanduser("~/Startup-Intelligence-OS/.claude/agents")
OPENCLAW_AGENTS_DIR = os.path.expanduser("~/.openclaw/agents")
OPENCLAW_WORKSPACES = os.path.expanduser("~/.openclaw")

# Already registered — skip these
ALREADY_REGISTERED = {
    "jake-chat", "jake-triage", "jake-deep-work", "daily-ops",
    "kira", "aria", "scout", "steve", "compass",
    "atlas", "forge", "sentinel", "research-director", "oracle-brief", "ledger"
}

# Studios — register as a group under studio model, not individual agents
STUDIO_AGENTS = {
    "deck-studio", "design-studio-director", "landing-page-studio",
    "app-experience-studio", "marketing-studio-director", "article-studio",
    "memo-studio", "social-media-studio", "whitepaper-studio",
    "film-studio-director", "screenwriter-studio", "cinematography-studio",
    "color-grade-studio", "editing-studio", "music-score-studio",
    "sound-design-studio", "vfx-studio", "production-designer-studio",
    "production-manager-studio", "legal-rights-studio", "distribution-studio",
    "talent-cast-studio", "highlight-reel-studio", "photography-studio",
    "instagram-studio", "coach-outreach-studio", "recruiting-dashboard-studio",
    "recruiting-strategy-studio", "training-research-studio",
    "workout-program-studio", "workout-session-studio",
    "coaching-architecture-studio", "slideworks-builder",
    "slideworks-creative-director", "slideworks-strategist",
    "audio-gen-engine", "film-gen-engine", "image-gen-engine",
}

# Infrastructure/meta agents — skip (handled by system)
SKIP_AGENTS = {
    "susan",  # Susan is the orchestrator, not a chat agent
    "departments",  # Not an agent, it's a directory
    "knowledge",  # Not an agent, it's a directory
    "ux-design-process",  # This is a skill, not an agent
    "angular-architect",  # Too specific framework agent
    "cpp-pro",  # Too specific language agent
    "azure-infra-engineer",  # Too specific platform agent
}

# Model assignment based on role complexity
HAIKU_ROLES = {"specialist", "researcher", "studio"}
SONNET_ROLES = {"head", "lead", "director", "architect"}

def parse_susan_agent(filepath):
    """Parse a Susan agent markdown file with YAML frontmatter."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return None

    try:
        meta = yaml.safe_load(match.group(1))
    except:
        return None

    body = match.group(2).strip()

    # Extract first paragraph of identity section
    identity_match = re.search(r'(?:##?\s*Identity\s*\n+)(.*?)(?:\n##|\Z)', body, re.DOTALL)
    identity_text = identity_match.group(1).strip()[:500] if identity_match else body[:500]

    return {
        "name": meta.get("name", os.path.basename(filepath).replace(".md", "")),
        "description": meta.get("description", ""),
        "department": meta.get("department", "general"),
        "role": meta.get("role", "specialist"),
        "supervisor": meta.get("supervisor", "susan"),
        "identity_text": identity_text,
    }

def determine_model(agent):
    """Assign Haiku or Sonnet based on role."""
    role = agent.get("role", "specialist")
    if role in SONNET_ROLES or "lead" in agent["name"] or "director" in agent["name"]:
        return "anthropic/claude-sonnet-4-20250514"
    return "anthropic/claude-haiku-4-5-20251001"

def determine_privilege(agent):
    """Assign privilege level based on department."""
    dept = agent.get("department", "")
    if dept in ("engineering", "data-ai"):
        return "RESTRICTED WRITE", "Can create/modify code, plans, and technical docs"
    elif dept in ("strategy", "growth", "product"):
        return "READ-ONLY", "Can read and analyze but cannot modify code or send messages"
    elif dept in ("research", "science"):
        return "READ-ONLY + RESEARCH TOOLS", "Can search, read, and synthesize"
    else:
        return "READ-ONLY", "Can read and analyze"

def create_agent_files(agent):
    """Create IDENTITY.md, GUARDRAILS.md, SOUL.md for an agent."""
    agent_id = agent["name"]
    agent_dir = os.path.join(OPENCLAW_AGENTS_DIR, agent_id, "agent")
    workspace_dir = os.path.join(OPENCLAW_WORKSPACES, f"workspace-{agent_id}")

    os.makedirs(agent_dir, exist_ok=True)
    os.makedirs(workspace_dir, exist_ok=True)

    privilege, privilege_desc = determine_privilege(agent)
    container = agent_id

    # IDENTITY.md
    identity = f"""# {agent_id.replace('-', ' ').title()} — {agent['description'][:60]}

{agent['identity_text']}

## Role in JakeStudio
- **Department**: {agent['department']}
- **Supervisor**: {agent['supervisor']}
- **Description**: {agent['description']}

## Your Owner
Mike Rodgers — runs 3 companies:
- **Startup Intelligence OS**: Susan-powered multi-agent platform
- **Oracle Health AI Enablement**: Enterprise healthcare AI strategy
- **Alex Recruiting**: Athletic recruiting platform

## SuperMemory Access

```bash
~/.openclaw/bin/supermemory search "<query>" {container}
~/.openclaw/bin/supermemory add "<content>" {container}
~/.openclaw/bin/supermemory search "<query>" shared
```

### Your Container: `{container}`
### Memory Rules
1. Search SuperMemory before answering complex questions
2. Save significant findings to your container
3. Always check `shared` for cross-domain context
"""

    # GUARDRAILS.md
    guardrails = f"""# {agent_id.replace('-', ' ').title()} — Guardrails

## Privilege Level: {privilege}
{privilege_desc}

## Allowed
- Read codebase and documentation
- Access Susan RAG knowledge base
- Generate reports and analysis
- Query SuperMemory
- Write to `{container}` SuperMemory container

## Denied
- Send emails or messages on behalf of Mike
- Make financial commitments
- Modify other agents' configurations
- Exceed 100 API calls/hr

## Budget: $5/month
## API Limit: 100 calls/hour
"""

    # SOUL.md
    soul = f"""# {agent_id.replace('-', ' ').title()}

{agent['description']}

You serve Mike Rodgers and his 3 companies:
- Startup Intelligence OS
- Oracle Health AI Enablement
- Alex Recruiting

Department: {agent['department']} | Supervisor: {agent['supervisor']}
"""

    with open(os.path.join(agent_dir, "IDENTITY.md"), 'w') as f:
        f.write(identity)
    with open(os.path.join(agent_dir, "GUARDRAILS.md"), 'w') as f:
        f.write(guardrails)
    with open(os.path.join(workspace_dir, "SOUL.md"), 'w') as f:
        f.write(soul)

    return agent_dir, workspace_dir

def register_agent(agent_id, agent_dir, workspace_dir, model):
    """Register agent in OpenClaw."""
    cmd = [
        "openclaw", "agents", "add", agent_id,
        "--agent-dir", agent_dir,
        "--model", model,
        "--workspace", workspace_dir,
        "--non-interactive", "--json"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0, result.stdout[:200]

def main():
    # Collect all Susan agents
    agents = []

    for filename in sorted(os.listdir(SUSAN_AGENTS_DIR)):
        if not filename.endswith(".md"):
            continue

        agent_id = filename.replace(".md", "")

        # Skip already registered, studios, and meta agents
        if agent_id in ALREADY_REGISTERED:
            continue
        if agent_id in STUDIO_AGENTS:
            continue
        if agent_id in SKIP_AGENTS:
            continue

        filepath = os.path.join(SUSAN_AGENTS_DIR, filename)
        agent = parse_susan_agent(filepath)
        if agent:
            agents.append(agent)

    # Also check .claude/agents for additional agents
    for filename in sorted(os.listdir(CLAUDE_AGENTS_DIR)):
        if not filename.endswith(".md"):
            continue
        agent_id = filename.replace(".md", "")
        if agent_id in ALREADY_REGISTERED or agent_id in STUDIO_AGENTS or agent_id in SKIP_AGENTS:
            continue
        # Check if already in the list
        if any(a["name"] == agent_id for a in agents):
            continue
        filepath = os.path.join(CLAUDE_AGENTS_DIR, filename)
        agent = parse_susan_agent(filepath)
        if agent:
            agents.append(agent)

    print(f"Found {len(agents)} agents to register\n")

    registered = 0
    failed = 0

    for agent in agents:
        agent_id = agent["name"]
        model = determine_model(agent)
        model_short = "Haiku" if "haiku" in model else "Sonnet"

        print(f"[{registered+failed+1}/{len(agents)}] {agent_id:40s} ({model_short:6s}) ... ", end="", flush=True)

        agent_dir, workspace_dir = create_agent_files(agent)
        ok, output = register_agent(agent_id, agent_dir, workspace_dir, model)

        if ok:
            print("OK")
            registered += 1
        else:
            print(f"FAIL: {output[:80]}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Registered: {registered}")
    print(f"Failed:     {failed}")
    print(f"Total:      {registered + failed}")
    print(f"Previously: 15")
    print(f"Grand total: {15 + registered}")

if __name__ == "__main__":
    main()
