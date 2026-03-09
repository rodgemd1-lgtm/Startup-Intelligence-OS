"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import type { AppState } from "@/lib/state";

interface TerminalProps {
  visible: boolean;
  onToggle: () => void;
  state: AppState;
}

export function Terminal({ visible, onToggle, state }: TerminalProps) {
  const [history, setHistory] = useState<string[]>(() => [
    "jake v5 -- Startup Intelligence OS",
    "Session: " + new Date().toLocaleString(),
    'Type "help" for available commands.\n',
  ]);
  const inputRef = useRef<HTMLInputElement>(null);
  const outputRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on history change
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [history]);

  // Focus input when visible
  useEffect(() => {
    if (visible && inputRef.current) {
      inputRef.current.focus();
    }
  }, [visible]);

  const handleCommand = useCallback(
    (cmd: string) => {
      if (cmd === "clear") {
        setHistory([]);
        return;
      }

      const staticCommands: Record<string, string> = {
        help:
          "Available commands:\n" +
          "  help        Show this message\n" +
          "  status      System status\n" +
          "  decisions   Open decisions\n" +
          "  capabilities  Capability gaps\n" +
          "  context     Active workspace context\n" +
          "  clear       Clear terminal\n\n" +
          "Keyboard shortcuts:\n" +
          "  1-6   Switch views \u00B7 t  Toggle terminal",
      };

      const dynamicCommands: Record<string, () => string> = {
        status: () =>
          "jake: Decision OS status\n" +
          "  decisions: " + state.status.decisions + "\n" +
          "  capabilities: " + state.status.capabilities + "\n" +
          "  runs: " + state.status.runs + "\n" +
          "  agents: " + state.agents.length,
        context: () =>
          "Startup Intelligence OS Context\n" +
          "  Company: " + state.context.active_company + "\n" +
          "  Project: " + state.context.active_project + "\n" +
          "  Decision: " + state.context.active_decision + "\n" +
          "  Branch: " + state.context.active_branch,
        decisions: () => {
          const lines = ["Open decisions (" + state.decisions.length + "):"];
          state.decisions.forEach((d, i) => {
            const best = d.options.reduce((a, b) =>
              a.total > b.total ? a : b
            );
            lines.push(
              "  " +
                (i + 1) +
                ". " +
                d.title +
                " [" +
                d.status +
                "] \u2014 best: " +
                best.title +
                " (" +
                best.total +
                ")"
            );
          });
          return lines.join("\n");
        },
        capabilities: () => {
          const lines = [
            "Capability domains (" + state.capabilities.length + "):",
          ];
          state.capabilities.forEach((c) => {
            let bar = "";
            for (let i = 0; i < 5; i++)
              bar += i < Math.round(c.maturity) ? "\u2588" : "\u2591";
            lines.push(
              "  " +
                bar +
                "  " +
                c.maturity.toFixed(1) +
                "/" +
                c.target.toFixed(1) +
                "  " +
                c.name +
                " [W" +
                c.wave +
                "]"
            );
          });
          return lines.join("\n");
        },
      };

      // Build response
      let response: string | null = null;
      if (staticCommands[cmd]) {
        response = staticCommands[cmd];
      } else if (dynamicCommands[cmd]) {
        response = dynamicCommands[cmd]();
      }

      if (response !== null) {
        setHistory((prev) => [...prev, "$ " + cmd, response!]);
        return;
      }

      // API forwarding
      setHistory((prev) => [...prev, "$ " + cmd]);
      fetch("/api/" + cmd)
        .then((r) => r.json())
        .then((data) => {
          setHistory((prev) => [...prev, JSON.stringify(data, null, 2)]);
        })
        .catch(() => {
          setHistory((prev) => [
            ...prev,
            'Unknown command: ' + cmd + '\nType "help" for available commands.',
          ]);
        });
    },
    [state]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key !== "Enter") return;
      const cmd = (e.target as HTMLInputElement).value.trim();
      if (!cmd) return;
      (e.target as HTMLInputElement).value = "";
      handleCommand(cmd);
    },
    [handleCommand]
  );

  if (!visible) return null;

  return (
    <div className="terminal">
      <div className="terminal-header">
        <div className="terminal-dot" style={{ background: "#e06565" }} />
        <div className="terminal-dot" style={{ background: "#e8a84c" }} />
        <div className="terminal-dot" style={{ background: "#5cd4a0" }} />
        <span style={{ marginLeft: 8, cursor: "pointer" }} onClick={onToggle}>
          jake terminal
        </span>
      </div>
      <div className="terminal-output" ref={outputRef}>
        {history.join("\n")}
      </div>
      <div className="terminal-input-wrap">
        <span className="terminal-prompt">$</span>
        <input
          className="terminal-input"
          ref={inputRef}
          placeholder="Type a command..."
          autoComplete="off"
          onKeyDown={handleKeyDown}
        />
      </div>
    </div>
  );
}
