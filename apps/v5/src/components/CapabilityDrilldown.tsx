"use client";
import type { Capability, Agent } from "@/lib/state";
import { groupColors } from "@/lib/utils";

const DOMAIN_AGENT_GROUPS: Record<string, string[]> = {
  "Decision Kernel": ["orchestration", "strategy"],
  "Capability Management": ["orchestration", "strategy"],
  "Innovation & Strategy": ["strategy", "studio"],
  "UX & Design": ["product", "studio"],
  "Agent Orchestration": ["engineering", "orchestration"],
  "Studio Operations": ["studio", "product"],
  "Intelligence & Research": ["research"],
  "Portfolio Management": ["strategy", "orchestration"],
  "Operator Experience": ["product", "engineering"],
  "Platform Infrastructure": ["engineering"],
  "Content & Marketing": ["growth", "studio"],
  "Data & Analytics": ["engineering", "science"],
};

const GAP_ACTIONS: Record<string, string> = {
  "LLM debate": "Wire DecisionEngine to Claude API for multi-POV debate",
  "evidence scoring":
    "Implement confidence scoring on evidence records",
  "outcome tracking":
    "Add outcome fields to decision records with feedback loops",
  "automated discovery":
    "Build capability scanner from codebase and docs",
  "design system":
    "Create Figma token pipeline with Tailwind integration",
  "semantic routing":
    "Implement intent-based agent routing with embeddings",
  "agent memory":
    "Add conversation persistence with pgvector storage",
  auth: "Set up NextAuth with GitHub OAuth provider",
  "CI/CD": "Configure GitHub Actions for test + deploy pipeline",
  monitoring: "Add Sentry error tracking and Vercel Analytics",
  WebSockets: "Implement real-time updates with SSE",
};

function getAction(gap: string): string {
  return GAP_ACTIONS[gap] || `Address ${gap} gap to reach target maturity`;
}

interface CapabilityDrilldownProps {
  capability: Capability;
  agents: Agent[];
  expanded: boolean;
}

export function CapabilityDrilldown({
  capability,
  agents,
  expanded,
}: CapabilityDrilldownProps) {
  if (!expanded) return null;

  const groups = DOMAIN_AGENT_GROUPS[capability.name] || [];
  const matchedAgents = agents.filter((a) => groups.includes(a.group));

  return (
    <div
      style={{
        padding: "14px 16px",
        background: "var(--surface-2)",
        borderRadius: "var(--radius-sm)",
        border: "1px solid var(--border-subtle)",
        marginTop: 4,
        marginBottom: 8,
      }}
    >
      {/* Gap list with recommended actions */}
      {capability.gaps.length > 0 && (
        <div style={{ marginBottom: 14 }}>
          <div className="label" style={{ marginBottom: 8 }}>
            Gaps & Recommended Actions
          </div>
          <div className="list-stack">
            {capability.gaps.map((gap) => (
              <div key={gap} className="list-item" style={{ padding: "8px 10px" }}>
                <div className="row">
                  <strong style={{ fontSize: "0.82rem" }}>{gap}</strong>
                  <span className="tag tag-gap">gap</span>
                </div>
                <div
                  className="item-meta"
                  style={{ marginTop: 4, fontSize: "0.75rem" }}
                >
                  {getAction(gap)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assigned agents */}
      {matchedAgents.length > 0 && (
        <div>
          <div className="label" style={{ marginBottom: 8 }}>
            Assigned Agents
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {matchedAgents.map((a) => {
              const gc = groupColors[a.group] || "#8ba4cc";
              return (
                <div
                  key={a.name}
                  className="agent-group-badge"
                  style={{
                    background: `${gc}20`,
                    color: gc,
                  }}
                >
                  {a.name} ({a.role})
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
