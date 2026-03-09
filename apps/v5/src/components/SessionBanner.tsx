"use client";

import type { SessionDiff } from "@/hooks/useSession";

interface SessionBannerProps {
  diff: SessionDiff | null;
}

export function SessionBanner({ diff }: SessionBannerProps) {
  if (!diff?.isReturning) return null;

  return (
    <div className="progress-since reveal" style={{ "--d": "60ms" } as React.CSSProperties}>
      <strong>Welcome back!</strong> It has been{" "}
      <strong>{diff.daysSince} day{diff.daysSince !== 1 ? "s" : ""}</strong> since your last session.
      {diff.decisionsDelta !== 0 && (
        <> Decisions: <strong>{diff.decisionsDelta > 0 ? "+" : ""}{diff.decisionsDelta}</strong>.</>
      )}
      {diff.maturityDelta !== 0 && (
        <> Maturity: <strong>{diff.maturityDelta > 0 ? "+" : ""}{diff.maturityDelta}</strong>.</>
      )}
      {diff.gapsDelta !== 0 && (
        <> Gaps: <strong>{diff.gapsDelta > 0 ? "+" : ""}{diff.gapsDelta}</strong>.</>
      )}
    </div>
  );
}
