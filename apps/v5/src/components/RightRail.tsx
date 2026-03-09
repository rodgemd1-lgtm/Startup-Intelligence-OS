"use client";
import type { Debrief, AppContext } from "@/lib/state";

interface RightRailProps {
  debrief: Debrief;
  context: AppContext;
}

export function RightRail({ debrief, context }: RightRailProps) {
  const actions = debrief.actions?.mike || [];

  return (
    <aside className="rightbar">
      <div>
        <div className="label" style={{ marginBottom: 10 }}>
          Next Actions
        </div>
        <div className="list-stack">
          {actions.map((a, i) => (
            <div key={i} className="next-action-item">
              {a}
            </div>
          ))}
        </div>
      </div>
      <div>
        <div className="label" style={{ marginBottom: 10 }}>
          Workspace
        </div>
        <div className="list-stack">
          <div className="list-item">
            <strong>Mode:</strong> {context.mode}
          </div>
          <div className="list-item">
            <strong>Front door:</strong> {context.front_door}
          </div>
          <div className="list-item">
            <strong>Foundry:</strong> {context.foundry}
          </div>
          <div className="list-item">
            <strong>Company:</strong> {context.active_company}
          </div>
        </div>
      </div>
      <div>
        <div className="label" style={{ marginBottom: 10 }}>
          System
        </div>
        <div className="system-pulse">
          <span className="pulse-dot" />
          <span>Connecting...</span>
        </div>
      </div>
      <div className="design-rule">
        <strong>Design rule:</strong> The operator should never wonder which
        workspace, company, branch, or decision is active.
      </div>
    </aside>
  );
}
