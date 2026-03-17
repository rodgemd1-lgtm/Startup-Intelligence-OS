"use client";
import { createContext, useCallback, useContext, useState } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { RightRail } from "./RightRail";
import { BottomNav } from "./BottomNav";
import { XTerminal } from "./XTerminal";
import { DragHandle } from "./DragHandle";
import { useApi } from "@/hooks/useApi";
import { useKeyboard } from "@/hooks/useKeyboard";

type AppStateType = ReturnType<typeof useApi>;
const AppStateContext = createContext<AppStateType | null>(null);

export function useAppState() {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error("useAppState must be used within AppShell");
  return ctx;
}

export function useAppRefresh() {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error("useAppRefresh must be used within AppShell");
  return {
    refreshCapabilities: ctx.refreshCapabilities,
    refreshOperator: ctx.refreshOperator,
  };
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const state = useApi();
  const pathname = usePathname();
  const [splitPercent, setSplitPercent] = useState(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("cockpit-split");
      return stored ? parseFloat(stored) : 65;
    }
    return 65;
  });

  const handleResize = useCallback((pct: number) => {
    setSplitPercent(pct);
    localStorage.setItem("cockpit-split", String(pct));
  }, []);

  useKeyboard();

  return (
    <AppStateContext.Provider value={state}>
      <div className="app">
        <Sidebar
          currentPath={pathname}
          apiLive={state.apiLive}
          agentCount={state.agents.length}
          decisionCount={state.status.decisions ?? state.decisions.length}
          totalGaps={
            state.capabilitySummary?.length
              ? state.capabilitySummary.reduce((sum, capability) => sum + capability.gaps.length, 0)
              : state.capabilities.reduce((sum, capability) => sum + capability.gaps.length, 0)
          }
        />
        <div className="main">
          <Topbar context={state.context} />
          <div className="terminal-zone" style={{ flex: `0 0 ${splitPercent}%` }}>
            <XTerminal />
          </div>
          <DragHandle onResize={handleResize} />
          <div className="context-zone">
            {children}
          </div>
        </div>
        <RightRail
          debrief={state.debrief}
          context={state.context}
          departments={state.departments}
          signals={state.signals}
          actionPackets={state.actionPackets}
          graph={state.graph}
        />
        <BottomNav currentPath={pathname} />
      </div>
    </AppStateContext.Provider>
  );
}
