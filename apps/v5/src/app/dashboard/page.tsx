"use client";
import { useAppState } from "@/components/AppShell";
import { MaturityBar } from "@/components/MaturityBar";
import { useBarAnimation } from "@/hooks/useBarAnimation";
import { delay } from "@/lib/utils";

const HEAT_COLORS: Record<number, string> = {
  1: "#e06565",
  2: "#e8a84c",
  3: "#5b8def",
  4: "#5cd4a0",
  5: "#c4a1f7",
};

function getHeatColor(maturity: number): string {
  const level = Math.max(1, Math.min(5, Math.round(maturity)));
  return HEAT_COLORS[level] || "#1a2030";
}

export default function DashboardPage() {
  const state = useAppState();

  // Use summary data when available
  const hasSummary = state.capabilitySummary && state.capabilitySummary.length > 0;
  const capabilities = hasSummary
    ? state.capabilitySummary!.map((s) => ({
        name: s.name,
        maturity: s.maturity_current,
        target: s.maturity_target,
        gaps: s.gaps,
        wave: s.wave,
        total_items: s.total_items,
        done_items: s.done_items,
        progress_percent: s.progress_percent,
        threshold: s.threshold,
      }))
    : state.capabilities.map((c) => ({
        name: c.name,
        maturity: c.maturity,
        target: c.target,
        gaps: c.gaps,
        wave: c.wave,
        total_items: 0,
        done_items: 0,
        progress_percent: 0,
        threshold: false,
      }));

  const total = capabilities.reduce((s, c) => s + c.maturity, 0);
  const avg = (total / capabilities.length).toFixed(1);
  const totalGaps = capabilities.reduce((s, c) => s + c.gaps.length, 0);
  const pctBaseline = Math.round((parseFloat(avg) / 5) * 100);

  // Aggregate progress from summary data
  const totalItems = capabilities.reduce((s, c) => s + c.total_items, 0);
  const doneItems = capabilities.reduce((s, c) => s + c.done_items, 0);
  const aggProgress = totalItems > 0 ? Math.round((doneItems / totalItems) * 100) : 0;

  useBarAnimation();

  return (
    <>
      <h1
        className="reveal"
        {...delay(0)}
        style={{ marginBottom: 4, ...({ "--d": "0ms" } as React.CSSProperties) }}
      >
        25X Dashboard
      </h1>
      <p className="reveal" {...delay(0)}>
        Tracking progress from current state to 25X target across all capability
        domains.
      </p>

      {/* Progress-since banner (endowed progress effect) */}
      <div className="progress-since reveal" {...delay(1)}>
        <strong>Assessment complete.</strong> {capabilities.length} domains
        scored. You are <strong>{avg}</strong> out of 5.0 &mdash; that&apos;s{" "}
        <strong>{pctBaseline}%</strong> of the way to baseline. Wave 1 addresses
        the <strong>7 most critical</strong> capabilities first.
        {hasSummary && totalItems > 0 && (
          <>
            {" "}Endowed progress: <strong>{doneItems}/{totalItems} steps complete ({aggProgress}%)</strong>.
          </>
        )}
      </div>

      {/* Aggregate metrics */}
      <div className="grid-3 reveal" {...delay(2)}>
        <div className="metric-card m-warning">
          <div className="metric-label">Aggregate Maturity</div>
          <div className="metric-value warning">{avg} / 5.0</div>
        </div>
        <div className="metric-card m-accent">
          <div className="metric-label">Domains Assessed</div>
          <div className="metric-value accent">
            {capabilities.length}
          </div>
        </div>
        <div className="metric-card m-danger">
          <div className="metric-label">Total Gaps</div>
          <div className="metric-value danger">{totalGaps}</div>
        </div>
      </div>

      {/* Domain Heat Map */}
      <div className="card reveal" {...delay(3)}>
        <div className="card-header">
          <h2>Domain Heat Map</h2>
          <div className="label">maturity by domain</div>
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: 6,
          }}
        >
          {capabilities.map((c) => (
            <div
              key={c.name}
              style={{
                padding: "10px 8px",
                borderRadius: "var(--radius-sm)",
                background: `${getHeatColor(c.maturity)}18`,
                border: `1px solid ${getHeatColor(c.maturity)}40`,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: "0.68rem",
                  fontWeight: 500,
                  color: "var(--text-secondary)",
                  marginBottom: 4,
                  lineHeight: 1.2,
                }}
              >
                {c.name}
              </div>
              <div
                style={{
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  color: getHeatColor(c.maturity),
                  fontFamily: "var(--mono)",
                }}
              >
                {c.maturity.toFixed(1)}
              </div>
              <div
                className={`wave-label w${c.wave}`}
                style={{ marginTop: 4, fontSize: "0.58rem" }}
              >
                W{c.wave}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Domain Progress */}
      <div className="card reveal" {...delay(4)}>
        <div className="card-header">
          <h2>Domain Progress to 25X</h2>
        </div>
        <div className="stack">
          {capabilities.map((c) => {
            const pct = Math.round((c.maturity / c.target) * 100);
            return (
              <div key={c.name}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 4,
                  }}
                >
                  <span
                    style={{ fontSize: "0.82rem", fontWeight: 500 }}
                  >
                    {c.name}
                  </span>
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
                    <span
                      className="mono tertiary"
                      style={{ fontSize: "0.72rem" }}
                    >
                      {pct}%
                    </span>
                  </div>
                </div>
                <MaturityBar
                  maturity={c.maturity}
                  target={c.target}
                  threshold={c.threshold}
                  compact
                />
                {hasSummary && c.total_items > 0 && (
                  <div className="mono tertiary" style={{ fontSize: "0.66rem", marginTop: 2 }}>
                    {c.done_items}/{c.total_items} steps &mdash; {c.progress_percent}%
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 25X Multiplier Targets */}
      <div className="card reveal" {...delay(5)}>
        <div className="card-header">
          <h2>25X Multiplier Targets</h2>
        </div>
        <div className="list-stack">
          <div className="list-item">
            <div className="row">
              <span>Decision cycle time</span>
              <span className="mono">1 week &rarr; &lt; 1 day</span>
            </div>
          </div>
          <div className="list-item">
            <div className="row">
              <span>Capability assessments</span>
              <span className="mono">manual &rarr; auto-generated</span>
            </div>
          </div>
          <div className="list-item">
            <div className="row">
              <span>Company onboarding</span>
              <span className="mono">2-3 days &rarr; &lt; 2 hours</span>
            </div>
          </div>
          <div className="list-item">
            <div className="row">
              <span>Agent team deployment</span>
              <span className="mono">per-company &rarr; shared foundry</span>
            </div>
          </div>
          <div className="list-item">
            <div className="row">
              <span>Research synthesis</span>
              <span className="mono">ad hoc &rarr; continuous</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
