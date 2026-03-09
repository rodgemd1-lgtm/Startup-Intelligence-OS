"use client";
import { useAppState } from "@/components/AppShell";
import { DebatePanel } from "@/components/DebatePanel";
import { useBarAnimation } from "@/hooks/useBarAnimation";
import { delay } from "@/lib/utils";

export default function DecisionsPage() {
  const state = useAppState();

  useBarAnimation();

  return (
    <>
      <h1 className="reveal" {...delay(0)} style={{ marginBottom: 4, ...({ "--d": "0ms" } as React.CSSProperties) }}>
        Decision Room
      </h1>
      <p className="reveal" {...delay(0)}>
        Strategic decisions with multi-perspective debate and weighted scoring.
      </p>

      {state.decisions.map((d, di) => {
        const maxTotal = Math.max(...d.options.map((o) => o.total));

        return (
          <div className="card reveal" key={d.id} {...delay(di + 1)}>
            <div className="card-header">
              <h2>{d.title}</h2>
              <span
                className={`tag tag-${
                  d.status === "proposed" ? "active" : "draft"
                }`}
              >
                {d.status}
              </span>
            </div>
            <p style={{ marginBottom: 14 }}>{d.context}</p>

            {/* Debate panel */}
            <DebatePanel decisionId={d.id} />

            {/* Options with scoring bars */}
            <div className="list-stack">
              {d.options.map((opt) => {
                const isBest = opt.total >= maxTotal;
                return (
                  <div className="list-item" key={opt.title}>
                    <div className="row">
                      <strong>{opt.title}</strong>
                      <span
                        className={`score-num${isBest ? " success" : ""}`}
                      >
                        {opt.total}
                      </span>
                    </div>
                    {/* Score breakdown bars */}
                    {Object.entries(opt.scores).map(([key, val]) => (
                      <div
                        key={key}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 8,
                          marginTop: 6,
                        }}
                      >
                        <span
                          className="tertiary"
                          style={{ width: 70, fontSize: "0.72rem" }}
                        >
                          {key}
                        </span>
                        <div className="score-bar-track">
                          <div
                            className={`score-bar-fill${
                              isBest ? " best" : ""
                            } bar-anim`}
                            data-width={val.toString()}
                          />
                        </div>
                        <span
                          className="mono tertiary"
                          style={{
                            width: 24,
                            textAlign: "right",
                            fontSize: "0.7rem",
                          }}
                        >
                          {val}
                        </span>
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>

            {/* Output contract */}
            <div
              style={{
                marginTop: 14,
                padding: 12,
                borderRadius: 10,
                background: "var(--surface-2)",
                border: "1px solid var(--border-subtle)",
              }}
            >
              <div className="label" style={{ marginBottom: 6 }}>
                Output Contract
              </div>
              <div
                style={{
                  fontSize: "0.78rem",
                  color: "var(--text-secondary)",
                }}
              >
                recommendation &middot; counter_recommendation &middot; why_now
                &middot; failure_modes &middot; next_experiment
              </div>
            </div>
          </div>
        );
      })}
    </>
  );
}
