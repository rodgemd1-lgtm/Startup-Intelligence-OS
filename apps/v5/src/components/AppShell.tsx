"use client";
import { createContext, useCallback, useContext, useState } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { RightRail } from "./RightRail";
import { BottomNav } from "./BottomNav";
import { Terminal } from "./Terminal";
import { useApi } from "@/hooks/useApi";
import { useKeyboard } from "@/hooks/useKeyboard";
import type { AppState } from "@/lib/state";

type AppStateType = ReturnType<typeof useApi>;
const AppStateContext = createContext<AppStateType | null>(null);

export function useAppState() {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error("useAppState must be used within AppShell");
  return ctx;
}

const TerminalContext = createContext<{ visible: boolean; toggle: () => void }>({
  visible: false,
  toggle: () => {},
});

export function useTerminal() {
  return useContext(TerminalContext);
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const state = useApi();
  const pathname = usePathname();
  const [terminalVisible, setTerminalVisible] = useState(false);
  const toggleTerminal = useCallback(() => setTerminalVisible((v) => !v), []);

  useKeyboard(toggleTerminal);

  const terminalState: AppState = {
    context: state.context,
    status: state.status,
    debrief: state.debrief,
    decisions: state.decisions,
    capabilities: state.capabilities,
    agents: state.agents,
    vision: state.vision,
  };

  return (
    <AppStateContext.Provider value={state}>
      <TerminalContext.Provider value={{ visible: terminalVisible, toggle: toggleTerminal }}>
        <div className="app">
          <Sidebar
            currentPath={pathname}
            apiLive={state.apiLive}
            agentCount={state.agents.length}
            decisionCount={state.status.decisions ?? state.decisions.length}
            totalGaps={state.capabilities.reduce((s, c) => s + c.gaps.length, 0)}
          />
          <div className="main">
            <Topbar context={state.context} onToggleTerminal={toggleTerminal} />
            <div className="pane">
              <div className="pane-inner">
                {children}
                <Terminal
                  visible={terminalVisible}
                  onToggle={toggleTerminal}
                  state={terminalState}
                />
              </div>
            </div>
          </div>
          <RightRail debrief={state.debrief} context={state.context} />
          <BottomNav currentPath={pathname} />
        </div>
      </TerminalContext.Provider>
    </AppStateContext.Provider>
  );
}
