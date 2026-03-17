"use client";

import { useMemo, useState, useTransition } from "react";

import { api } from "@/lib/api";
import type { ActionPacket, DepartmentPack, RouteResponse } from "@/lib/api";
import { useAppRefresh } from "./AppShell";

interface AskRouterPanelProps {
  departments: DepartmentPack[];
  latestActionPacket: ActionPacket | null;
}

export function AskRouterPanel({ departments, latestActionPacket }: AskRouterPanelProps) {
  const [requestText, setRequestText] = useState("");
  const [routeResult, setRouteResult] = useState<RouteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const { refreshOperator } = useAppRefresh();

  const departmentMap = useMemo(
    () => new Map(departments.map((department) => [department.id, department])),
    [departments]
  );

  const activePacket = routeResult?.action_packet ?? latestActionPacket;

  function resolveDepartmentName(departmentId: string) {
    return departmentMap.get(departmentId)?.name ?? departmentId;
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = requestText.trim();
    if (!trimmed) return;

    setError(null);
    startTransition(() => {
      void api
        .routeRequest(trimmed)
        .then((result) => {
          setRouteResult(result);
          setRequestText("");
          refreshOperator();
        })
        .catch(() => {
          setError("Routing failed. Check the operator API and try again.");
        });
    });
  }

  return (
    <div className="card reveal" style={{ marginBottom: 16 }}>
      <div className="card-header">
        <h2>Operator Ask Router</h2>
        <span className="tag tag-active">{departments.length || 6} departments live</span>
      </div>
      <p style={{ marginBottom: 12 }}>
        Route a freeform ask through the department registry and generate a file-backed action packet.
      </p>
      <form onSubmit={handleSubmit}>
        <textarea
          value={requestText}
          onChange={(event) => setRequestText(event.target.value)}
          placeholder="Describe what you want the OS to decide, research, design, launch, or build."
          style={{
            width: "100%",
            minHeight: 94,
            resize: "vertical",
            borderRadius: 12,
            border: "1px solid var(--border)",
            background: "var(--surface-2)",
            color: "var(--text)",
            padding: "12px 14px",
            fontFamily: "var(--font)",
            fontSize: "0.85rem",
            marginBottom: 10,
          }}
        />
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
          <div className="mono tertiary" style={{ fontSize: "0.72rem" }}>
            Ask-driven routing writes an action packet to `.startup-os/action-packets`.
          </div>
          <button className="btn btn-primary" type="submit" disabled={isPending}>
            {isPending ? "Routing..." : "Route Ask"}
          </button>
        </div>
      </form>
      {error && (
        <div className="design-rule" style={{ marginTop: 12 }}>
          <strong>Routing error:</strong> {error}
        </div>
      )}
      {activePacket && (
        <div style={{ marginTop: 14 }}>
          <div className="label" style={{ marginBottom: 10 }}>
            Routed Department Stack
          </div>
          <div className="list-stack">
            {activePacket.department_sequence.map((step) => (
              <div key={`${activePacket.id}-${step.department_id}`} className="list-item">
                <div className="row">
                  <strong>{step.department_name || resolveDepartmentName(step.department_id)}</strong>
                  <span className={`tag ${step.role === "primary" ? "tag-active" : "tag-draft"}`}>
                    {step.role}
                  </span>
                </div>
                <div className="item-meta">
                  Outputs: {step.expected_outputs.join(", ") || "none specified"}
                </div>
                {step.depends_on.length > 0 && (
                  <div className="mono tertiary" style={{ fontSize: "0.7rem", marginTop: 6 }}>
                    Depends on: {step.depends_on.map(resolveDepartmentName).join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="mono tertiary" style={{ fontSize: "0.72rem", marginTop: 10 }}>
            Susan mode: {activePacket.recommended_susan_mode}
            {" · "}
            Decision: {activePacket.decision_requirement}
            {activePacket.company_context_name && (
              <>
                {" · "}
                Context: {activePacket.company_context_name}
              </>
            )}
            {activePacket.execution_track_id && (
              <>
                {" · "}
                Track: {activePacket.execution_track_id}
              </>
            )}
          </div>
          {activePacket.context_sources.length > 0 && (
            <div className="mono tertiary" style={{ fontSize: "0.7rem", marginTop: 6 }}>
              Sources: {activePacket.context_sources.slice(0, 2).join(" · ")}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
