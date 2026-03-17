"use client";

import type { ActionPacket, DepartmentPack, GraphSnapshot, SignalEvent } from "@/lib/api";
import type { Debrief, AppContext } from "@/lib/state";

interface RightRailProps {
  debrief: Debrief;
  context: AppContext;
  departments: DepartmentPack[];
  signals: SignalEvent[];
  actionPackets: ActionPacket[];
  graph: GraphSnapshot | null;
}

function severityTagClass(severity: SignalEvent["severity"]) {
  if (severity === "critical") return "tag-gap";
  if (severity === "warning") return "tag-partial";
  return "tag-ok";
}

export function RightRail({
  debrief,
  context,
  departments,
  signals,
  actionPackets,
  graph,
}: RightRailProps) {
  const fallbackActions = debrief.actions?.mike || [];
  const nextActions = actionPackets.length > 0
    ? actionPackets.slice(0, 4).map((packet) => packet.request_text)
    : fallbackActions;
  const topSignals = signals.slice(0, 4);
  const topDepartments = [...departments]
    .sort((left, right) => {
      const leftScore = Math.max(left.simulated_maturity ?? 0, left.current_maturity ?? 0);
      const rightScore = Math.max(right.simulated_maturity ?? 0, right.current_maturity ?? 0);
      return rightScore - leftScore;
    })
    .slice(0, 6);
  const simulatedCount = departments.filter((department) => typeof department.simulated_maturity === "number").length;

  return (
    <aside className="rightbar">
      <div>
        <div className="label" style={{ marginBottom: 10 }}>
          Next-Best Actions
        </div>
        <div className="list-stack">
          {nextActions.map((action, index) => (
            <div key={`${action}-${index}`} className="next-action-item">
              {action}
            </div>
          ))}
        </div>
      </div>
      <div>
        <div className="label" style={{ marginBottom: 10 }}>
          Active Signals
        </div>
        <div className="list-stack">
          {topSignals.length > 0 ? (
            topSignals.map((signal) => (
              <div key={signal.id} className="list-item">
                <div className="row">
                  <strong>{signal.title}</strong>
                  <span className={`tag ${severityTagClass(signal.severity)}`}>
                    {signal.severity}
                  </span>
                </div>
                <div className="item-meta">
                  {signal.next_action || signal.description}
                </div>
              </div>
            ))
          ) : (
            <div className="list-item">No active signals.</div>
          )}
        </div>
      </div>
      <div>
        <div className="label" style={{ marginBottom: 10 }}>
          Department Registry
        </div>
        <div className="mono tertiary" style={{ fontSize: "0.72rem", marginBottom: 10 }}>
          Simulated reviews live for {simulatedCount}/{departments.length || 0} departments.
        </div>
        <div className="list-stack">
          {topDepartments.length > 0 ? (
            topDepartments.map((department) => (
              <div key={department.id} className="list-item">
                <div className="row">
                  <strong>{department.name}</strong>
                  <span className="tag tag-active">{department.primary_mode}</span>
                </div>
                <div className="item-meta">Owner: {department.owner_agent}</div>
                <div className="item-meta">
                  Operational: {department.current_maturity?.toFixed(1) ?? "n/a"}
                  {typeof department.simulated_maturity === "number" && (
                    <>
                      {" · "}
                      Simulated: {department.simulated_maturity.toFixed(1)}
                    </>
                  )}
                </div>
                {department.simulated_review_path && (
                  <div className="mono tertiary" style={{ fontSize: "0.7rem", marginTop: 6 }}>
                    Review: {department.simulated_review_path}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="list-item">Department registry unavailable.</div>
          )}
        </div>
      </div>
      <div>
        <div className="label" style={{ marginBottom: 10 }}>
          Graph Context
        </div>
        <div className="list-stack">
          <div className="list-item">
            <strong>Nodes:</strong> {graph?.summary.node_count ?? 0}
          </div>
          <div className="list-item">
            <strong>Links:</strong> {graph?.summary.link_count ?? 0}
          </div>
          <div className="list-item">
            <strong>Company:</strong> {graph?.summary.active.company || context.active_company}
          </div>
          <div className="list-item">
            <strong>Project:</strong> {graph?.summary.active.project || context.active_project}
          </div>
          <div className="list-item">
            <strong>Decision:</strong> {graph?.summary.active.decision || context.active_decision}
          </div>
        </div>
      </div>
      <div>
        <div className="label" style={{ marginBottom: 10 }}>
          System
        </div>
        <div className="system-pulse">
          <span className="pulse-dot" />
          <span>{graph ? "Graph connected" : "Connecting..."}</span>
        </div>
      </div>
      <div className="design-rule">
        <strong>Design rule:</strong> Ask routing, simulated versus operational maturity, and active graph context should stay visible at all times.
      </div>
    </aside>
  );
}
