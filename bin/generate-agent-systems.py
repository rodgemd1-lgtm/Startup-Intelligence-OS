#!/usr/bin/env python3
"""Batch generate SYSTEM.md for all OpenClaw agents missing them.

Phase 5 of V15: Superagent Wave 3 — template-based SYSTEM.md creation.
Uses Susan agent definitions + IDENTITY.md for context.
"""

import os
import json
from pathlib import Path

OPENCLAW_AGENTS = Path.home() / ".openclaw" / "agents"
SUSAN_AGENTS = Path(__file__).resolve().parent.parent / "susan-team-architect" / "agents"
BUDGETS_FILE = Path.home() / ".openclaw" / "agent-budgets.json"

# Agents to skip (not real specialist agents)
SKIP_AGENTS = {"main", "jake"}

# Already have SYSTEM.md — will be verified, not overwritten
ALREADY_DONE = set()

# Department → heartbeat templates
HEARTBEAT_TEMPLATES = {
    "strategy": """## Heartbeat Behavior

When triggered by a strategy task (on-demand):

### Strategic Analysis
1. Analyze the current business context and competitive landscape
2. Review recent SCOUT signals and market intelligence
3. Evaluate strategic options with pros/cons and risk assessment
4. Cross-reference decisions against company goals and roadmap
5. Save strategic insights to SuperMemory `shared` container

### Decision Support
1. Frame decisions with clear options and trade-offs
2. Identify irreversible vs reversible choices
3. Quantify risk where possible (financial, timeline, competitive)
4. Recommend action with confidence level and evidence basis
5. Track decision outcomes for pattern learning""",

    "product": """## Heartbeat Behavior

When triggered by a product task (on-demand):

### Product Analysis
1. Review user needs, feedback, and behavioral data
2. Evaluate feature requests against product strategy and roadmap
3. Assess competitive product landscape for gaps and opportunities
4. Define acceptance criteria and success metrics for proposed features
5. Save product insights to SuperMemory `shared` container

### Design & Specification
1. Create user stories with clear acceptance criteria
2. Map user journeys and interaction flows
3. Identify dependencies and integration points
4. Prioritize using impact/effort framework
5. Track product decisions and their rationale""",

    "engineering": """## Heartbeat Behavior

When triggered by a build task (on-demand):

### Technical Review
1. Analyze proposed changes against system architecture
2. Check for technical debt, performance implications, and security concerns
3. Review code patterns for consistency with project conventions
4. Validate integration points and API contracts
5. Save technical decisions to SuperMemory `shared` container

### Implementation Support
1. Generate code following established patterns and conventions
2. Create test stubs and validation scripts
3. Wire new modules into existing dependency chains
4. Document technical decisions with rationale and rollback strategy""",

    "research": """## Heartbeat Behavior

When triggered by a research task (on-demand):

### Research Execution
1. Frame research questions with clear scope and success criteria
2. Identify authoritative sources (academic, industry, primary data)
3. Execute systematic search across available tools and databases
4. Grade evidence quality (A = peer-reviewed, B = industry, C = anecdotal)
5. Save findings to SuperMemory with source provenance

### Synthesis & Reporting
1. Synthesize findings into actionable insights
2. Identify contradictions and knowledge gaps
3. Recommend follow-up research where evidence is insufficient
4. Format output for the requesting agent or workflow""",

    "growth": """## Heartbeat Behavior

When triggered by a growth task (on-demand):

### Growth Analysis
1. Review current acquisition channels and conversion metrics
2. Analyze competitor growth strategies and market positioning
3. Identify high-leverage growth opportunities and quick wins
4. Evaluate content performance and engagement patterns
5. Save growth insights to SuperMemory `shared` container

### Content & Distribution
1. Create content aligned with brand voice and target audience
2. Optimize for platform-specific distribution (SEO, ASO, social)
3. Design engagement loops and retention triggers
4. Track performance metrics and iterate on strategies""",

    "health-science": """## Heartbeat Behavior

When triggered by a science task (on-demand):

### Evidence Review
1. Review current scientific literature and evidence base
2. Evaluate claims against peer-reviewed research
3. Identify evidence gaps and areas of scientific uncertainty
4. Cross-reference with regulatory guidelines and safety standards
5. Save evidence summaries to SuperMemory `shared` container

### Protocol Design
1. Design evidence-based protocols and recommendations
2. Include safety considerations and contraindications
3. Adapt recommendations for individual variation
4. Document evidence grade for each recommendation""",

    "performance-science": """## Heartbeat Behavior

When triggered by a behavioral/performance task (on-demand):

### Behavioral Analysis
1. Review behavioral science evidence relevant to the task
2. Map psychological mechanisms to product/user outcomes
3. Identify habit loops, motivation systems, and friction points
4. Evaluate ethical implications of behavioral interventions
5. Save behavioral insights to SuperMemory `shared` container

### Intervention Design
1. Design evidence-based behavioral interventions
2. Include ethical guardrails and user autonomy protections
3. Define measurable outcomes and evaluation criteria
4. Cross-reference with existing product patterns""",

    "behavioral-science": """## Heartbeat Behavior

When triggered by a behavioral task (on-demand):

### Behavioral Analysis
1. Review behavioral science evidence relevant to the task
2. Map psychological mechanisms to product/user outcomes
3. Design ethical engagement and retention systems
4. Evaluate long-term user impact and sustainability
5. Save behavioral insights to SuperMemory `shared` container""",

    "data-ai": """## Heartbeat Behavior

When triggered by an AI/data task (on-demand):

### Technical Evaluation
1. Assess AI/ML requirements and model selection criteria
2. Review data pipeline architecture and quality metrics
3. Evaluate model performance, cost, and latency trade-offs
4. Check for bias, fairness, and safety considerations
5. Save AI architecture decisions to SuperMemory `shared` container

### Implementation Guidance
1. Recommend model selection based on task requirements
2. Design evaluation frameworks and success metrics
3. Plan deployment, monitoring, and iteration cycles
4. Document AI decisions with evidence and rationale""",

    "quality-security": """## Heartbeat Behavior

When triggered by a quality/security task (on-demand):

### Security Review
1. Analyze code and architecture for security vulnerabilities
2. Review against OWASP Top 10 and security best practices
3. Evaluate authentication, authorization, and data protection
4. Check dependency vulnerabilities and supply chain risks
5. Save security findings to SuperMemory `shared` container

### Quality Assurance
1. Design test strategies covering unit, integration, and E2E
2. Review code quality, error handling, and edge cases
3. Validate compliance with project standards and conventions
4. Track quality metrics and regression patterns""",

    "oracle-health": """## Heartbeat Behavior

When triggered by an Oracle Health task (on-demand):

### Healthcare Context
1. Review Oracle Health product landscape and competitive positioning
2. Analyze healthcare AI trends and regulatory environment
3. Evaluate messaging for clinical accuracy and compliance
4. Cross-reference with existing Oracle Health knowledge base
5. Save healthcare insights to SuperMemory `shared` container

### Content & Strategy
1. Create healthcare-appropriate content and messaging
2. Ensure regulatory compliance (HIPAA, FDA guidance)
3. Design stakeholder-specific value propositions
4. Track market signals and competitive moves""",

    "film-production": """## Heartbeat Behavior

When triggered by a production task (on-demand):

### Production Review
1. Analyze production requirements and creative brief
2. Evaluate available tools and generation capabilities
3. Plan production pipeline with quality gates
4. Check legal clearance and rights requirements
5. Save production decisions to SuperMemory `shared` container

### Creative Execution
1. Execute assigned production phase with quality standards
2. Review output against creative direction and brand guidelines
3. Manage handoff to next production stage
4. Document creative decisions and alternatives considered""",

    "content-design": """## Heartbeat Behavior

When triggered by a content task (on-demand):

### Content Strategy
1. Analyze content requirements and audience targeting
2. Review brand voice guidelines and existing content patterns
3. Design content structure optimized for the target platform
4. Plan content pipeline with review and approval stages
5. Save content decisions to SuperMemory `shared` container

### Content Creation
1. Create content following brand voice and style guidelines
2. Optimize for platform-specific requirements and algorithms
3. Include visual and structural elements for engagement
4. Document content strategy and performance tracking plan""",

    "infrastructure": """## Heartbeat Behavior

When triggered by an infrastructure task (on-demand):

### Infrastructure Review
1. Analyze current infrastructure architecture and dependencies
2. Evaluate proposed changes for reliability and security impact
3. Review cloud resource configuration and cost implications
4. Check compliance with security policies and access controls
5. Save infrastructure decisions to SuperMemory `shared` container

### Implementation
1. Design infrastructure changes with rollback strategies
2. Create IaC configurations following established patterns
3. Validate deployment pipelines and monitoring coverage
4. Document architecture decisions with rationale""",

    "languages": """## Heartbeat Behavior

When triggered by a development task (on-demand):

### Code Review & Implementation
1. Analyze code for language-specific best practices and idioms
2. Review performance characteristics and optimization opportunities
3. Ensure type safety, memory safety, and error handling
4. Validate against project coding standards
5. Save implementation patterns to SuperMemory `shared` container""",

    "executive": """## Heartbeat Behavior

When triggered by a coordination task (on-demand):

### Orchestration
1. Decompose complex requests into specialist subtasks
2. Route to appropriate department heads and specialists
3. Synthesize results into coherent deliverables
4. Track cross-department dependencies and blockers
5. Save coordination decisions to SuperMemory `shared` container""",
}

# Department → monitoring targets
MONITORING_TARGETS = {
    "strategy": ["Company strategic metrics and KPIs", "Competitive landscape changes", "Revenue model performance"],
    "product": ["User feedback and feature requests", "Product metric trends", "UX pain points and opportunities"],
    "engineering": ["System architecture stability", "Code quality metrics", "Deployment pipeline health"],
    "research": ["Knowledge base freshness", "Source quality and coverage", "Research pipeline throughput"],
    "growth": ["Acquisition channel performance", "Content engagement metrics", "Conversion funnel health"],
    "health-science": ["Exercise science evidence updates", "Safety and regulatory changes", "Protocol effectiveness data"],
    "performance-science": ["Behavioral intervention outcomes", "User habit formation metrics", "Ethical impact assessment"],
    "behavioral-science": ["Engagement system health", "User autonomy metrics", "Ethical guardrail compliance"],
    "data-ai": ["Model performance metrics", "Data pipeline reliability", "AI cost and latency budgets"],
    "quality-security": ["Vulnerability scan results", "Test coverage trends", "Security incident patterns"],
    "oracle-health": ["Healthcare market signals", "Regulatory environment changes", "Stakeholder engagement metrics"],
    "film-production": ["Production pipeline status", "Asset quality gates", "Rights and clearance status"],
    "content-design": ["Content performance metrics", "Brand consistency scores", "Platform algorithm changes"],
    "infrastructure": ["Cloud resource utilization", "Security posture metrics", "Cost optimization opportunities"],
    "languages": ["Code quality metrics", "Performance benchmarks", "Dependency health"],
    "executive": ["Cross-department coordination", "System-wide health metrics", "Priority alignment"],
}


def load_budgets():
    """Load agent budgets from JSON."""
    if BUDGETS_FILE.exists():
        with open(BUDGETS_FILE) as f:
            data = json.load(f)
        return data.get("agent_budgets", {})
    return {}


def load_susan_metadata():
    """Load agent metadata from Susan agent definitions."""
    metadata = {}
    if not SUSAN_AGENTS.exists():
        return metadata
    for f in SUSAN_AGENTS.glob("*.md"):
        name = None
        desc = None
        dept = None
        role = None
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                elif line.startswith("department:"):
                    dept = line.split(":", 1)[1].strip()
                elif line.startswith("role:"):
                    role = line.split(":", 1)[1].strip()
                elif line == "---" and name:
                    break
        if name:
            metadata[name] = {"description": desc, "department": dept, "role": role}
    return metadata


def generate_system_md(agent_name, susan_meta, budget_info):
    """Generate SYSTEM.md content for an agent."""
    desc = susan_meta.get("description", f"{agent_name} specialist agent")
    dept = susan_meta.get("department", "general")
    role = susan_meta.get("role", "specialist")

    # Get display name
    display_name = agent_name.replace("-", " ").title()

    # Get budget
    budget_key = agent_name.replace("-", "_")
    if budget_key in budget_info:
        b = budget_info[budget_key]
        budget_line = f"Your monthly budget is ${b['monthly_budget']:.0f}. Use {b['default_model'].title()} for primary tasks, Haiku for simple classification and routing."
    else:
        budget_line = "Your monthly budget is $2. Use Sonnet for analysis and generation, Haiku for classification and routing."

    # Get heartbeat template
    heartbeat = HEARTBEAT_TEMPLATES.get(dept, HEARTBEAT_TEMPLATES.get("engineering"))

    # Get monitoring targets
    targets = MONITORING_TARGETS.get(dept, MONITORING_TARGETS.get("engineering"))
    targets_text = "\n".join(f"- {t}" for t in targets)

    # Build the SYSTEM.md
    system_md = f"""# {display_name.upper()} — System Instructions

{heartbeat}

## Monitoring Targets

**Cross-Project Awareness:**
{targets_text}

**Startup Intelligence OS:**
- Susan runtime and RAG pipeline health
- Agent coordination and handoff quality

**Oracle Health:**
- Healthcare AI strategy alignment
- Stakeholder communication effectiveness

**Alex Recruiting:**
- Athletic recruiting pipeline metrics
- Coach engagement and outreach patterns

## Decision Records
When making decisions in your domain, always record:
| Field | Content |
|-------|---------|
| Decision | What was decided |
| Context | Why this decision was needed |
| Options | What alternatives were considered |
| Rationale | Why this option was chosen |
| Reversibility | Easy / Hard / Irreversible |
| Dependencies | What this affects downstream |

## Build Memory
Track across sessions:
- Domain decisions and their rationale
- Patterns that worked (and ones that didn't)
- Cross-project insights relevant to your specialty
- Performance baselines and quality trends

## Budget Awareness
{budget_line}
"""
    return system_md


def main():
    budgets = load_budgets()
    susan_meta = load_susan_metadata()

    created = 0
    skipped = 0
    errors = 0

    for agent_dir in sorted(OPENCLAW_AGENTS.iterdir()):
        if not agent_dir.is_dir():
            continue

        agent_name = agent_dir.name

        if agent_name in SKIP_AGENTS:
            print(f"SKIP: {agent_name} (excluded)")
            skipped += 1
            continue

        agent_subdir = agent_dir / "agent"
        system_md_path = agent_subdir / "SYSTEM.md"

        if system_md_path.exists():
            print(f"EXISTS: {agent_name}")
            skipped += 1
            continue

        # Ensure agent/ directory exists
        agent_subdir.mkdir(parents=True, exist_ok=True)

        # Get Susan metadata
        meta = susan_meta.get(agent_name, {})
        if not meta:
            # Try Claude Code agent definitions
            claude_agent = Path(__file__).resolve().parent.parent / ".claude" / "agents" / f"{agent_name}.md"
            if claude_agent.exists():
                with open(claude_agent) as f:
                    content = f.read()
                # Extract description from first few lines
                for line in content.split("\n"):
                    if line.startswith("description:"):
                        meta["description"] = line.split(":", 1)[1].strip()
                    elif line.startswith("department:"):
                        meta["department"] = line.split(":", 1)[1].strip()
                    elif line.startswith("role:"):
                        meta["role"] = line.split(":", 1)[1].strip()

        if not meta:
            meta = {"description": f"{agent_name} agent", "department": "general", "role": "specialist"}
            print(f"WARN: {agent_name} — no Susan definition found, using defaults")

        # Generate and write
        content = generate_system_md(agent_name, meta, budgets)
        with open(system_md_path, "w") as f:
            f.write(content)
        print(f"CREATED: {agent_name} ({meta.get('department', 'general')}/{meta.get('role', 'specialist')})")
        created += 1

    print(f"\n--- Summary ---")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Errors:  {errors}")
    print(f"Total agents: {created + skipped + errors}")


if __name__ == "__main__":
    main()
