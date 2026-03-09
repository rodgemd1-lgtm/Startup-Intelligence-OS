"use client";
import { useAppState } from "@/components/AppShell";
import { MetricCard } from "@/components/MetricCard";
import { SessionBanner } from "@/components/SessionBanner";
import { useSession } from "@/hooks/useSession";
import { useBarAnimation } from "@/hooks/useBarAnimation";
import { maturityLabel, maturityColor, delay } from "@/lib/utils";

export default function HomePage() {
  const state = useAppState();

  const totalGaps = state.capabilities.reduce((s, c) => s + c.gaps.length, 0);
  const avgMaturity = +(
    state.capabilities.reduce((s, c) => s + c.maturity, 0) /
    state.capabilities.length
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
  const w1Count = state.capabilities.filter((c) => c.wave === 1).length;

  // Sort capabilities: wave ascending, then maturity ascending
  const w1First = [...state.capabilities].sort(
    (a, b) => a.wave - b.wave || a.maturity - b.maturity
  );

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
          {state.capabilities.length} domains.
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
                  <div className="progress-track" style={{ marginTop: 8 }}>
                    <div
                      className={`progress-fill ${maturityColor(
                        c.maturity
                      )} bar-anim`}
                      data-width={((c.maturity / 5) * 100).toString()}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}
