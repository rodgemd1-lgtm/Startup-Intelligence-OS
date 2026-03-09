"use client";
import { useState } from "react";
import { useAppState } from "@/components/AppShell";
import { CapabilityDrilldown } from "@/components/CapabilityDrilldown";
import { delay } from "@/lib/utils";

export default function CapabilitiesPage() {
  const state = useAppState();
  const [expandedDomain, setExpandedDomain] = useState<string | null>(null);

  const totalGaps = state.capabilities.reduce((s, c) => s + c.gaps.length, 0);
  const avgMaturity = +(
    state.capabilities.reduce((s, c) => s + c.maturity, 0) /
    state.capabilities.length
  ).toFixed(1);

  // Wave counts
  const waves = [0, 0, 0];
  state.capabilities.forEach((c) => {
    waves[c.wave - 1]++;
  });

  // Sort for critical gaps: wave ascending, then maturity ascending
  const sortedCaps = [...state.capabilities]
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
        {state.capabilities.length} domains scored from the 25X assessment.
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
          {state.capabilities.map((c) => {
            const isExpanded = expandedDomain === c.name;
            return (
              <div key={c.name}>
                <div
                  className="maturity-row"
                  style={{ cursor: "pointer" }}
                  onClick={() =>
                    setExpandedDomain(isExpanded ? null : c.name)
                  }
                >
                  <div className="domain-name">{c.name}</div>
                  <div className="bar-wrap">
                    <div className="maturity-segments">
                      {[1, 2, 3, 4, 5].map((i) => {
                        const filled = i <= Math.round(c.maturity);
                        const isTarget =
                          i <= Math.round(c.target) && !filled;
                        const colorClass = filled
                          ? c.maturity < 1.5
                            ? " filled bad"
                            : c.maturity < 2.5
                            ? " filled warn"
                            : " filled"
                          : "";
                        return (
                          <div
                            key={i}
                            className={`maturity-seg${colorClass}${
                              isTarget ? " target" : ""
                            }`}
                          />
                        );
                      })}
                    </div>
                  </div>
                  <div className="score-label">
                    {c.maturity.toFixed(1)} &rarr; {c.target.toFixed(1)}
                  </div>
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
                  capability={c}
                  agents={state.agents}
                  expanded={isExpanded}
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
