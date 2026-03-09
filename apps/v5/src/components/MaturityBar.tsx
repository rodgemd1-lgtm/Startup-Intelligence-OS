"use client";

const LEVEL_COLORS: Record<number, string> = {
  1: "#e06565",
  2: "#e8a84c",
  3: "#5b8def",
  4: "#5cd4a0",
  5: "#c4a1f7",
};

const LEVEL_LABELS = ["NAS", "EMR", "SCL", "OPT", "LDG"];

interface MaturityBarProps {
  maturity: number;
  target: number;
  threshold?: boolean;
  compact?: boolean;
}

export function MaturityBar({ maturity, target, threshold, compact }: MaturityBarProps) {
  return (
    <div
      className="maturity-bar-v6"
      role="meter"
      aria-valuenow={maturity}
      aria-valuemin={0}
      aria-valuemax={5}
      aria-label={`Maturity: ${maturity.toFixed(1)} of 5`}
    >
      {[1, 2, 3, 4, 5].map((level) => {
        const filled = level <= Math.floor(maturity) || (level === Math.ceil(maturity) && maturity >= level);
        const isPartial = !filled && level === Math.ceil(maturity) && maturity % 1 > 0;
        const isTargetZone = !filled && !isPartial && level <= Math.ceil(target) && level > Math.ceil(maturity);
        const isThreshold = threshold && level === Math.ceil(maturity) + 1 && level <= 5;

        const segStyle: React.CSSProperties = {};
        if (filled) {
          segStyle.background = LEVEL_COLORS[level];
        } else if (isPartial) {
          const pct = Math.round((maturity % 1) * 100);
          segStyle.background = `linear-gradient(90deg, ${LEVEL_COLORS[level]} ${pct}%, var(--surface-3) ${pct}%)`;
        }

        const classes = [
          "seg",
          filled ? "filled" : "",
          isTargetZone ? "target-zone" : "",
          isThreshold ? "threshold" : "",
        ]
          .filter(Boolean)
          .join(" ");

        return (
          <div key={level} style={{ flex: 1 }}>
            <div className={classes} style={segStyle} />
            {!compact && (
              <div className="seg-label">{LEVEL_LABELS[level - 1]}</div>
            )}
          </div>
        );
      })}
    </div>
  );
}
