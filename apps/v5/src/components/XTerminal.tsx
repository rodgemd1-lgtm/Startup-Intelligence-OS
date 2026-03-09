"use client";
import { useEffect, useRef, useCallback } from "react";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebLinksAddon } from "@xterm/addon-web-links";
import "@xterm/xterm/css/xterm.css";

const WS_URL = process.env.NEXT_PUBLIC_TERMINAL_WS || "ws://localhost:8421";

export function XTerminal() {
  const containerRef = useRef<HTMLDivElement>(null);
  const termRef = useRef<Terminal | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);

  const connect = useCallback(() => {
    if (!termRef.current) return;
    const term = termRef.current;

    // Close previous connection if any
    wsRef.current?.close();

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      term.writeln("\x1b[32mConnected to shell.\x1b[0m");
      const fitAddon = fitAddonRef.current;
      if (fitAddon) {
        fitAddon.fit();
        ws.send(`\x1b[RESIZE:${term.cols}:${term.rows}`);
      }
    };

    ws.onmessage = (event) => {
      term.write(typeof event.data === "string" ? event.data : new Uint8Array(event.data));
    };

    ws.onclose = () => {
      term.writeln("\x1b[31mDisconnected. Press Enter to reconnect.\x1b[0m");
    };

    ws.onerror = () => {
      term.writeln("\x1b[31mConnection failed. Is the terminal server running on port 8421?\x1b[0m");
    };
  }, []);

  useEffect(() => {
    if (!containerRef.current || termRef.current) return;

    const term = new Terminal({
      theme: {
        background: "#060810",
        foreground: "#c8ccd4",
        cursor: "#5b8def",
        cursorAccent: "#060810",
        selectionBackground: "#2a3a5c",
        black: "#1a1e2e",
        red: "#e06565",
        green: "#5cd4a0",
        yellow: "#e8a84c",
        blue: "#5b8def",
        magenta: "#c4a1f7",
        cyan: "#5ec4c8",
        white: "#c8ccd4",
        brightBlack: "#8b92a8",
        brightRed: "#e06565",
        brightGreen: "#5cd4a0",
        brightYellow: "#e8a84c",
        brightBlue: "#5b8def",
        brightMagenta: "#c4a1f7",
        brightCyan: "#5ec4c8",
        brightWhite: "#f0f2f6",
      },
      fontFamily: "'SF Mono', 'Fira Code', 'Cascadia Code', Menlo, monospace",
      fontSize: 13,
      lineHeight: 1.3,
      cursorBlink: true,
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();
    term.loadAddon(fitAddon);
    term.loadAddon(webLinksAddon);

    termRef.current = term;
    fitAddonRef.current = fitAddon;

    term.open(containerRef.current);
    fitAddon.fit();

    // Register onData once — references wsRef.current for the active connection
    term.onData((data) => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      } else if (data === "\r") {
        connect();
      }
    });

    // Debounced resize observer
    let resizeTimeout: ReturnType<typeof setTimeout>;
    const resizeObserver = new ResizeObserver(() => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        fitAddon.fit();
        const ws = wsRef.current;
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(`\x1b[RESIZE:${term.cols}:${term.rows}`);
        }
      }, 100);
    });
    resizeObserver.observe(containerRef.current);

    connect();

    return () => {
      clearTimeout(resizeTimeout);
      resizeObserver.disconnect();
      wsRef.current?.close();
      term.dispose();
      termRef.current = null;
    };
  }, [connect]);

  return (
    <div
      ref={containerRef}
      className="xterminal"
      style={{ width: "100%", height: "100%", background: "#060810" }}
    />
  );
}
