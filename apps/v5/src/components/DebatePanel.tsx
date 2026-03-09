"use client";
import { useState, useCallback } from "react";
import { api } from "@/lib/api";

interface DebateResponse {
  mode: string;
  argument: string;
  confidence: number;
  counter: string;
}

const MODES = ["builder", "skeptic", "contrarian", "operator", "red_team"] as const;

const MODE_LABELS: Record<string, string> = {
  builder: "Builder",
  skeptic: "Skeptic",
  contrarian: "Contrarian",
  operator: "Operator",
  red_team: "Red Team",
};

const FALLBACK_RESPONSES: Record<string, DebateResponse> = {
  builder: {
    mode: "builder",
    argument:
      "This approach maximizes value delivery and aligns with strategic goals. The technical foundation supports execution.",
    confidence: 0.82,
    counter: "Speed may introduce technical debt.",
  },
  skeptic: {
    mode: "skeptic",
    argument:
      "Key assumptions remain untested. Projected outcomes lack evidence within the proposed timeline.",
    confidence: 0.65,
    counter: "Waiting has its own opportunity cost.",
  },
  contrarian: {
    mode: "contrarian",
    argument:
      "The opposite approach may yield better results. Conventional framing could anchor us suboptimally.",
    confidence: 0.58,
    counter:
      "Contrarian positions should pressure-test, not override evidence.",
  },
  operator: {
    mode: "operator",
    argument:
      "Resource allocation and dependencies need mapping before capacity commitment.",
    confidence: 0.75,
    counter: "Over-planning can be as costly as under-planning.",
  },
  red_team: {
    mode: "red_team",
    argument:
      "Failure modes need enumeration. Blast radius analysis and mitigation must be pre-positioned.",
    confidence: 0.7,
    counter: "Risk analysis should inform, not paralyze.",
  },
};

interface DebatePanelProps {
  decisionId: string;
}

export function DebatePanel({ decisionId }: DebatePanelProps) {
  const [activeMode, setActiveMode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<DebateResponse | null>(null);

  const handleTabClick = useCallback(
    async (mode: string) => {
      setActiveMode(mode);
      setLoading(true);
      setResponse(null);

      try {
        const data = await api.debate(decisionId, mode);
        if (data && data.argument) {
          setResponse(data as DebateResponse);
        } else {
          setResponse(FALLBACK_RESPONSES[mode]);
        }
      } catch {
        setResponse(FALLBACK_RESPONSES[mode]);
      } finally {
        setLoading(false);
      }
    },
    [decisionId]
  );

  return (
    <div>
      <div className="debate-tabs">
        {MODES.map((mode) => (
          <div
            key={mode}
            className={`debate-tab${activeMode === mode ? " active" : ""}`}
            onClick={() => handleTabClick(mode)}
          >
            {MODE_LABELS[mode]}
          </div>
        ))}
      </div>

      {loading && (
        <div
          style={{
            padding: "16px",
            color: "var(--text-secondary)",
            fontSize: "0.82rem",
          }}
        >
          Generating {activeMode ? MODE_LABELS[activeMode] : ""} perspective...
        </div>
      )}

      {response && !loading && (
        <div
          style={{
            padding: "14px",
            borderRadius: "var(--radius-sm)",
            background: "var(--surface-2)",
            border: "1px solid var(--border-subtle)",
          }}
        >
          <div
            className="label"
            style={{ marginBottom: 8, textTransform: "uppercase" }}
          >
            {MODE_LABELS[response.mode]} POV
          </div>
          <p style={{ fontSize: "0.82rem", marginBottom: 12 }}>
            {response.argument}
          </p>

          <div style={{ marginBottom: 8 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 4,
              }}
            >
              <span
                className="tertiary"
                style={{ fontSize: "0.72rem" }}
              >
                confidence
              </span>
              <span
                className="mono tertiary"
                style={{ fontSize: "0.7rem" }}
              >
                {Math.round(response.confidence * 100)}%
              </span>
            </div>
            <div className="score-bar-track">
              <div
                className="score-bar-fill"
                style={{ width: `${response.confidence * 100}%` }}
              />
            </div>
          </div>

          <div
            style={{
              fontSize: "0.78rem",
              color: "var(--text-tertiary)",
              fontStyle: "italic",
            }}
          >
            Counter: {response.counter}
          </div>
        </div>
      )}
    </div>
  );
}
