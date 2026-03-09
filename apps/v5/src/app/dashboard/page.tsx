"use client";
import { useAppState } from "@/components/AppShell";
import { useBarAnimation } from "@/hooks/useBarAnimation";
import { maturityColor, delay } from "@/lib/utils";

export default function DashboardPage() {
  const state = useAppState();

  const total = state.capabilities.reduce((s, c) => s + c.maturity, 0);
  const avg = (total / state.capabilities.length).toFixed(1);
  const totalGaps = state.capabilities.reduce((s, c) => s + c.gaps.length, 0);
  const pctBaseline = Math.round((parseFloat(avg) / 5) * 100);

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
        <strong>Assessment complete.</strong> {state.capabilities.length} domains
        scored. You are <strong>{avg}</strong> out of 5.0 &mdash; that&apos;s{" "}
        <strong>{pctBaseline}%</strong> of the way to baseline. Wave 1 addresses
        the <strong>7 most critical</strong> capabilities first.
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
            {state.capabilities.length}
          </div>
        </div>
        <div className="metric-card m-danger">
          <div className="metric-label">Total Gaps</div>
          <div className="metric-value danger">{totalGaps}</div>
        </div>
      </div>

      {/* Domain Progress */}
      <div className="card reveal" {...delay(3)}>
        <div className="card-header">
          <h2>Domain Progress to 25X</h2>
        </div>
        <div className="stack">
          {state.capabilities.map((c) => {
            const pct = Math.round((c.maturity / c.target) * 100);
            const barColor = maturityColor(c.maturity);
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
                <div className="progress-track">
                  <div
                    className={`progress-fill ${barColor} bar-anim`}
                    data-width={pct.toString()}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 25X Multiplier Targets */}
      <div className="card reveal" {...delay(4)}>
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
