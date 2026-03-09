"use client";
import { useState } from "react";
import { useAppState, useAppRefresh } from "@/components/AppShell";
import { CapabilityDrilldown } from "@/components/CapabilityDrilldown";
import { MaturityBar } from "@/components/MaturityBar";
import { delay } from "@/lib/utils";

export default function CapabilitiesPage() {
  const state = useAppState();
  const { refreshCapabilities } = useAppRefresh();
  const [expandedDomain, setExpandedDomain] = useState<string | null>(null);

  // Use capability summary data when available, fall back to static capabilities
  const hasSummary = state.capabilitySummary && state.capabilitySummary.length > 0;
  const capabilities = hasSummary
    ? state.capabilitySummary!.map((s) => ({
        name: s.name,
        maturity: s.maturity_current,
        target: s.maturity_target,
        gaps: s.gaps,
        wave: s.wave,
        id: s.id,
        total_items: s.total_items,
        done_items: s.done_items,
        progress_percent: s.progress_percent,
        threshold: s.threshold,
        next_item: s.next_item,
        owner_agent: s.owner_agent,
      }))
    : state.capabilities.map((c) => ({
        name: c.name,
        maturity: c.maturity,
        target: c.target,
        gaps: c.gaps,
        wave: c.wave,
        id: c.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
        total_items: 0,
        done_items: 0,
        progress_percent: 0,
        threshold: false,
        next_item: null as string | null,
        owner_agent: "",
      }));

  const totalGaps = capabilities.reduce((s, c) => s + c.gaps.length, 0);
  const avgMaturity = capabilities.length > 0
    ? +(capabilities.reduce((s, c) => s + c.maturity, 0) / capabilities.length).toFixed(1)
    : 0;

  // Wave counts
  const waves = [0, 0, 0];
  capabilities.forEach((c) => {
    waves[c.wave - 1]++;
  });

  // Sort for critical gaps: wave ascending, then maturity ascending
  const sortedCaps = [...capabilities]
    .filter((c) => c.gaps.length > 0)
    .sort((a, b) => a.wave - b.wave || a.maturity - b.maturity);

  return (
    <>
      <h1
        className="reveal"
        {...delay(0)}
        style={{ marginBottom: 4, ...({ "--d": "0ms" } as React.CSSProperties) }}
      >
        Capability Map
      </h1>
      <p className="reveal" {...delay(0)}>
        {capabilities.length} domains scored from the 25X assessment.
        Current aggregate:{" "}
        <span className="warning">
          {avgMaturity} / 5.0
        </span>
        .
      </p>

      {/* Wave summary */}
      <div className="grid-3 reveal" {...delay(1)}>
        <div className="metric-card m-accent">
          <div className="metric-label">Wave 1 (Foundation)</div>
          <div className="metric-value accent">{waves[0]}</div>
        </div>
        <div className="metric-card m-warning">
          <div className="metric-label">Wave 2 (Scale)</div>
          <div className="metric-value warning">{waves[1]}</div>
        </div>
        <div className="metric-card m-success">
          <div className="metric-label">Wave 3 (Compound)</div>
          <div className="metric-value success">{waves[2]}</div>
        </div>
      </div>

      {/* Domain Maturity */}
      <div className="card reveal" {...delay(2)}>
        <div className="card-header">
          <h2>Domain Maturity</h2>
          <div className="label">current / target</div>
        </div>
        <div className="stack">
          {capabilities.map((c) => {
            const isExpanded = expandedDomain === c.name;
            return (
              <div key={c.name}>
                <div
                  className="maturity-row"
                  role="button"
                  tabIndex={0}
                  aria-expanded={isExpanded}
                  style={{ cursor: "pointer" }}
                  onClick={() =>
                    setExpandedDomain(isExpanded ? null : c.name)
                  }
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setExpandedDomain(isExpanded ? null : c.name);
                    }
                  }}
                >
                  <div className="domain-name">{c.name}</div>
                  <div className="bar-wrap">
                    <MaturityBar
                      maturity={c.maturity}
                      target={c.target}
                      threshold={c.threshold}
                      compact
                    />
                  </div>
                  <div className="score-label">
                    {c.maturity.toFixed(1)} &rarr; {c.target.toFixed(1)}
                  </div>
                  {hasSummary && c.total_items > 0 && (
                    <span
                      className="mono tertiary"
                      style={{ fontSize: "0.68rem", minWidth: 60, textAlign: "right" }}
                    >
                      {c.done_items}/{c.total_items} &mdash; {c.progress_percent}%
                    </span>
                  )}
                  <span
                    className={`tag tag-${
                      c.wave === 1
                        ? "active"
                        : c.wave === 2
                        ? "partial"
                        : "ok"
                    }`}
                  >
                    W{c.wave}
                  </span>
                </div>

                {/* Drilldown inline */}
                <CapabilityDrilldown
                  capability={{
                    name: c.name,
                    maturity: c.maturity,
                    target: c.target,
                    gaps: c.gaps,
                    wave: c.wave,
                  }}
                  capabilityId={c.id}
                  agents={state.agents}
                  expanded={isExpanded}
                  onDataChange={refreshCapabilities}
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* Critical Gaps */}
      <div className="card reveal" {...delay(3)}>
        <div className="card-header">
          <h2>Critical Gaps</h2>
          <span className="urgency-badge">Foundation at risk</span>
        </div>
        <div className="list-stack">
          {sortedCaps.map((c) => {
            const critClass =
              c.wave === 1 && c.maturity < 2 ? " critical-path" : "";
            return (
              <div className={`list-item${critClass}`} key={c.name}>
                <div className="row">
                  <strong>{c.name}</strong>
                  <div
                    style={{
                      display: "flex",
                      gap: 6,
                      alignItems: "center",
                    }}
                  >
                    <span className={`wave-label w${c.wave}`}>
                      W{c.wave}
                    </span>
                    <span className="tag tag-gap">
                      {c.gaps.length} gaps
                    </span>
                  </div>
                </div>
                <div className="item-meta">{c.gaps.join(" \u00B7 ")}</div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
