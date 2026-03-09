"use client";
import { useState, useEffect, useCallback } from "react";

interface SessionSnapshot {
  lastVisit: string;
  decisionCount: number;
  capabilityAvgMaturity: number;
  totalGaps: number;
  agentCount: number;
}

export interface SessionDiff {
  daysSince: number;
  decisionsDelta: number;
  maturityDelta: number;
  gapsDelta: number;
  agentsDelta: number;
  isReturning: boolean;
}

const STORAGE_KEY = "jake-console-session";

export function useSession(current: {
  decisionCount: number;
  avgMaturity: number;
  totalGaps: number;
  agentCount: number;
}) {
  const [diff] = useState<SessionDiff | null>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const prev: SessionSnapshot = JSON.parse(stored);
        const daysSince = Math.floor(
          (Date.now() - new Date(prev.lastVisit).getTime()) / 86400000
        );
        return {
          daysSince,
          decisionsDelta: current.decisionCount - prev.decisionCount,
          maturityDelta: +(current.avgMaturity - prev.capabilityAvgMaturity).toFixed(1),
          gapsDelta: current.totalGaps - prev.totalGaps,
          agentsDelta: current.agentCount - prev.agentCount,
          isReturning: daysSince > 0,
        };
      }
    } catch {}
    return null;
  });

  const saveSession = useCallback(() => {
    try {
      const snapshot: SessionSnapshot = {
        lastVisit: new Date().toISOString(),
        decisionCount: current.decisionCount,
        capabilityAvgMaturity: current.avgMaturity,
        totalGaps: current.totalGaps,
        agentCount: current.agentCount,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
    } catch {
      /* ignore */
    }
  }, [current]);

  useEffect(() => {
    const timer = setTimeout(saveSession, 5000);
    return () => clearTimeout(timer);
  }, [saveSession]);

  return { diff, saveSession };
}
