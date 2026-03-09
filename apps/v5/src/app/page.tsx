"use client";
import { useAppState } from "@/components/AppShell";
import { MetricCard } from "@/components/MetricCard";
import { SessionBanner } from "@/components/SessionBanner";
import { MaturityBar } from "@/components/MaturityBar";
import { useSession } from "@/hooks/useSession";
import { useBarAnimation } from "@/hooks/useBarAnimation";
import { maturityLabel, delay } from "@/lib/utils";

export default function HomePage() {
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
        next_item: s.next_item,
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
        next_item: null as string | null,
      }));

  const totalGaps = capabilities.reduce((s, c) => s + c.gaps.length, 0);
  const avgMaturity = +(
    capabilities.reduce((s, c) => s + c.maturity, 0) /
    capabilities.length
  ).toFixed(1);
  const { diff } = useSession({
    decisionCount: state.decisions.length,
    avgMaturity,
    totalGaps,
    agentCount: state.agents.length,
  });

  const sessionDay = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    month: "short",
    day: "numeric",
  });

  // Wave 1 count for urgency
  const w1Count = capabilities.filter((c) => c.wave === 1).length;

  // Sort capabilities: wave ascending, then maturity ascending
  const w1First = [...capabilities].sort(
    (a, b) => a.wave - b.wave || a.maturity - b.maturity
  );

  // Focus capability: lowest-maturity Wave 1 domain
  const focusCap = w1First.find((c) => c.wave === 1) || w1First[0];
  const capsWaiting = capabilities.filter(
    (c) => c.name !== focusCap?.name && c.wave >= (focusCap?.wave || 1)
  ).length;

  // Aggregate progress from summary data
  const totalItems = capabilities.reduce((s, c) => s + c.total_items, 0);
  const doneItems = capabilities.reduce((s, c) => s + c.done_items, 0);
  const aggProgress = totalItems > 0 ? Math.round((doneItems / totalItems) * 100) : 0;

  useBarAnimation();

  return (
    <>
      {/* Metrics row */}
      <div className="metrics-row">
        <MetricCard
          label="Open decisions"
          value={state.status.decisions}
          color="accent"
          delay={0}
        />
        <MetricCard
          label="Capability gaps"
          value={totalGaps}
          color="danger"
          delay={60}
        />
        <MetricCard
          label="Active runs"
          value={state.status.runs}
          color="success"
          delay={120}
        />
        <MetricCard
          label="Agents"
          value={state.agents.length}
          color="warning"
          delay={180}
        />
      </div>

      {/* Session context + streak */}
      <div
        className="reveal"
        {...delay(4)}
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          ...({ "--d": `${4 * 60}ms` } as React.CSSProperties),
        }}
      >
        <div className="streak-badge">Session active &middot; {sessionDay}</div>
        <div className="urgency-badge">
          Wave 1: {w1Count} capabilities unresolved
        </div>
      </div>

      {/* Session banner for returning users */}
      <SessionBanner diff={diff} />

      {/* Jake brief */}
      <div className="card card-glow reveal" {...delay(5)}>
        <div className="jake-msg">
          <div className="jake-label">JAKE &mdash; ACTIVE</div>
          {state.debrief.greeting} &mdash; we&apos;re in{" "}
          <span className="accent">{state.context.active_company}</span>.
          Active decision:{" "}
          <span className="accent">{state.context.active_decision}</span>.
          <br />
          <br />
          System maturity:{" "}
          <span className="warning">
            {avgMaturity} / 5.0 (Emerging)
          </span>
          . The 25X assessment identified{" "}
          <span className="danger">{totalGaps} capability gaps</span> across{" "}
          {capabilities.length} domains.
          {hasSummary && totalItems > 0 && (
            <>
              <br />
              Endowed progress:{" "}
              <span className="success">
                {doneItems}/{totalItems} steps complete ({aggProgress}%)
              </span>
            </>
          )}
          <br />
          <br />
          <strong style={{ color: "var(--text)" }}>Best next moves:</strong>
          <br />
          1. Review the 5-year strategic vision (Innovation Studio)
          <br />
          2. Address Wave 1 gaps &mdash; platform infrastructure, closed-loop
          learning, agent collaboration
          <br />
          3. Wire the decision engine to Claude for real AI-powered debate
        </div>
      </div>

      {/* Grid: Decision Room + Capability Foundry */}
      <div className="grid-2">
        {/* Decision Room preview */}
        <div className="card reveal" {...delay(6)}>
          <div className="card-header">
            <h2>Decision Room</h2>
            <span className="tag tag-active">
              {state.decisions.length} active
            </span>
          </div>
          <div className="list-stack">
            {state.decisions.map((d) => {
              const best = d.options.reduce((a, b) =>
                a.total > b.total ? a : b
              );
              return (
                <div className="list-item" key={d.id}>
                  <div className="row">
                    <strong>{d.title}</strong>
                    <span
                      className={`tag tag-${
                        d.status === "proposed" ? "active" : "draft"
                      }`}
                    >
                      {d.status}
                    </span>
                  </div>
                  <div className="item-meta">
                    Best option: {best.title} (score {best.total})
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Capability Foundry preview */}
        <div className="card reveal" {...delay(7)}>
          <div className="card-header">
            <h2>Capability Foundry</h2>
            <span className="tag tag-gap">{totalGaps} gaps</span>
          </div>

          {/* Focus capability */}
          {focusCap && (
            <div
              style={{
                padding: "10px 14px",
                borderRadius: "var(--radius-sm)",
                background: "linear-gradient(135deg, rgba(91,141,239,0.08), rgba(92,212,160,0.06))",
                border: "1px solid var(--accent-border)",
                marginBottom: 12,
                fontSize: "0.82rem",
              }}
            >
              <div className="label" style={{ marginBottom: 4, color: "var(--accent)" }}>
                Focus Capability
              </div>
              <div style={{ fontWeight: 500, color: "var(--text)" }}>
                {focusCap.name}
              </div>
              {focusCap.next_item && (
                <div className="muted" style={{ fontSize: "0.78rem", marginTop: 4 }}>
                  Next: {focusCap.next_item}
                </div>
              )}
              <div className="mono tertiary" style={{ fontSize: "0.68rem", marginTop: 4 }}>
                {capsWaiting} capabilities waiting behind this one
              </div>
            </div>
          )}

          <div className="list-stack">
            {w1First.slice(0, 4).map((c) => {
              const tagClass =
                c.maturity < 1.5
                  ? "tag-gap"
                  : c.maturity < 2.5
                  ? "tag-partial"
                  : "tag-ok";
              const critClass =
                c.wave === 1 && c.maturity < 2 ? " critical-path" : "";
              return (
                <div className={`list-item${critClass}`} key={c.name}>
                  <div className="row">
                    <span>{c.name}</span>
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
                      <span className={`tag ${tagClass}`}>
                        {maturityLabel(c.maturity)}
                      </span>
                    </div>
                  </div>
                  <div style={{ marginTop: 8 }}>
                    <MaturityBar
                      maturity={c.maturity}
                      target={c.target}
                      threshold={c.threshold}
                      compact
                    />
                  </div>
                  {hasSummary && c.total_items > 0 && (
                    <div className="mono tertiary" style={{ fontSize: "0.68rem", marginTop: 4 }}>
                      {c.done_items}/{c.total_items} steps &mdash; {c.progress_percent}%
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}
