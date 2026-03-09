"use client";
import { useAppState } from "@/components/AppShell";

function delay(i: number) {
  return { style: { "--d": `${i * 60}ms` } as React.CSSProperties };
}

export default function InnovationPage() {
  const state = useAppState();

  return (
    <>
      <h1
        className="reveal"
        {...delay(0)}
        style={{ marginBottom: 4, ...({ "--d": "0ms" } as React.CSSProperties) }}
      >
        Innovation Studio
      </h1>
      <p className="reveal" {...delay(0)}>
        Strategos future-back vision. 5-year strategic plan working backward
        from the north star.
      </p>

      {/* Strategic bets */}
      <div className="grid-3 reveal" {...delay(1)}>
        <div className="card">
          <h3 className="accent">Bet 1</h3>
          <p style={{ marginTop: 6, fontSize: "0.82rem" }}>
            Intelligence Compounding
          </p>
          <p style={{ marginTop: 4, fontSize: "0.75rem" }}>
            Knowledge from Company N makes Company N+1 faster. The moat.
          </p>
        </div>
        <div className="card">
          <h3 className="success">Bet 2</h3>
          <p style={{ marginTop: 6, fontSize: "0.82rem" }}>
            Agent Factory as Platform
          </p>
          <p style={{ marginTop: 4, fontSize: "0.75rem" }}>
            Other founders configure their own agent teams and domain packs.
          </p>
        </div>
        <div className="card">
          <h3 className="warning">Bet 3</h3>
          <p style={{ marginTop: 6, fontSize: "0.82rem" }}>
            TransformFit as Proof
          </p>
          <p style={{ marginTop: 4, fontSize: "0.75rem" }}>
            A company built by 60 agents + 1 human with real users and revenue.
          </p>
        </div>
      </div>

      {/* Timeline */}
      <div className="card reveal" {...delay(2)}>
        <div className="card-header">
          <h2>5-Year Timeline</h2>
        </div>
        <div className="timeline">
          {state.vision.map((v) => (
            <div
              key={v.year}
              className={`timeline-item${v.current ? " current" : ""}`}
            >
              <div className="timeline-year">
                {v.year} &mdash; {v.label}
              </div>
              <div className="timeline-title">{v.title}</div>
              <div className="timeline-desc">{v.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Highest-Risk Assumptions */}
      <div className="card reveal" {...delay(3)}>
        <div className="card-header">
          <h2>Highest-Risk Assumptions</h2>
        </div>
        <div className="list-stack">
          <div className="list-item">
            <div className="row">
              <strong>Solo Operator Ceiling</strong>
              <span className="tag tag-gap">high risk</span>
            </div>
            <div className="item-meta">
              Can one person manage 5+ companies through AI? Cognitive load does
              not scale linearly.
            </div>
          </div>
          <div className="list-item">
            <div className="row">
              <strong>LLM Provider Dependency</strong>
              <span className="tag tag-partial">medium risk</span>
            </div>
            <div className="item-meta">
              Entire system tuned for Claude. Price increase or capability
              regression would be disruptive.
            </div>
          </div>
          <div className="list-item">
            <div className="row">
              <strong>Knowledge Quality at Scale</strong>
              <span className="tag tag-partial">medium risk</span>
            </div>
            <div className="item-meta">
              500K+ chunk RAG might degrade into noise. More data is not always
              better.
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
