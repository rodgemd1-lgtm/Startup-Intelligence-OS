"use client";

const LEVEL_COLORS: Record<number, string> = {
  1: "#e06565",
  2: "#e8a84c",
  3: "#5b8def",
  4: "#5cd4a0",
};

const LEVEL_NAMES: Record<number, string> = {
  1: "Nascent",
  2: "Emerging",
  3: "Scaling",
  4: "Optimizing",
};

interface LevelChecklistProps {
  capabilityId: string;
  levels: Record<number, { name: string; items: { text: string; done: boolean }[] }>;
  currentMaturity: number;
  onToggle: (level: number, index: number) => void;
}

export function LevelChecklist({ capabilityId, levels, currentMaturity, onToggle }: LevelChecklistProps) {
  // Determine which level is the current working level (first with incomplete items)
  let workingLevel: number | null = null;
  for (let l = 1; l <= 4; l++) {
    const level = levels[l];
    if (level && level.items.some((item) => !item.done)) {
      workingLevel = l;
      break;
    }
  }

  return (
    <div
      className="level-stack"
      data-capability-id={capabilityId}
      data-current-maturity={currentMaturity}
    >
      {[1, 2, 3, 4].map((levelNum) => {
        const level = levels[levelNum];
        if (!level) return null;

        const doneCount = level.items.filter((i) => i.done).length;
        const totalCount = level.items.length;
        const allDone = doneCount === totalCount && totalCount > 0;
        const isWorking = levelNum === workingLevel;
        const isFuture = workingLevel !== null && levelNum > workingLevel;
        const color = LEVEL_COLORS[levelNum] || "#8ba4cc";
        const levelName = level.name || LEVEL_NAMES[levelNum] || `Level ${levelNum}`;

        const sectionClass = [
          "level-section",
          allDone ? "complete" : "",
          isFuture ? "dimmed" : "",
        ]
          .filter(Boolean)
          .join(" ");

        return (
          <div key={levelNum} className={sectionClass}>
            <div className="level-header">
              <div className="level-dot" style={{ background: color }} />
              <span>{levelName}</span>
              {allDone && (
                <span style={{ color: "var(--success)", fontSize: "0.82rem" }}>
                  &#10003;
                </span>
              )}
              <span className="level-count">
                {doneCount}/{totalCount}
              </span>
            </div>

            {/* Only show items if working level or completed */}
            {(isWorking || allDone) && (
              <div className="level-items">
                {level.items.map((item, idx) => (
                  <div
                    key={idx}
                    role="checkbox"
                    aria-checked={item.done}
                    aria-label={item.text}
                    tabIndex={isFuture ? -1 : 0}
                    className={`level-item${item.done ? " done" : ""}`}
                    onClick={() => {
                      if (!isFuture) onToggle(levelNum, idx);
                    }}
                    onKeyDown={(e) => {
                      if (!isFuture && (e.key === "Enter" || e.key === " ")) {
                        e.preventDefault();
                        onToggle(levelNum, idx);
                      }
                    }}
                  >
                    <div className={`checkbox${item.done ? " checked" : ""}`} aria-hidden="true">
                      {item.done && (
                        <svg
                          width="10"
                          height="10"
                          viewBox="0 0 10 10"
                          fill="none"
                          stroke="#fff"
                          strokeWidth="1.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <polyline points="2,5 4.5,7.5 8,3" />
                        </svg>
                      )}
                    </div>
                    <span>{item.text}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
