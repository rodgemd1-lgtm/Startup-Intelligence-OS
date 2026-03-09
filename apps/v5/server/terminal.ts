// apps/v5/server/terminal.ts
import { WebSocketServer, WebSocket } from "ws";
import * as pty from "node-pty";
import { platform } from "os";

const PORT = parseInt(process.env.TERMINAL_PORT || "8421", 10);
const SHELL = process.env.SHELL || (platform() === "win32" ? "powershell.exe" : "zsh");
const CWD = process.env.TERMINAL_CWD || process.cwd();
const MAX_CONNECTIONS = 5;

let connectionCount = 0;

const wss = new WebSocketServer({ port: PORT, host: "127.0.0.1" });
console.log(`Terminal server listening on ws://127.0.0.1:${PORT}`);

wss.on("connection", (ws: WebSocket, req) => {
  // Origin validation
  const origin = req.headers.origin;
  if (origin && !origin.startsWith("http://localhost")) {
    ws.close(1008, "Origin not allowed");
    return;
  }

  // Connection limit
  if (connectionCount >= MAX_CONNECTIONS) {
    ws.close(1013, "Maximum connections reached");
    return;
  }
  connectionCount++;

  console.log(`Client connected (${connectionCount}/${MAX_CONNECTIONS}) — spawning PTY`);

  const ptyProcess = pty.spawn(SHELL, [], {
    name: "xterm-256color",
    cols: 120,
    rows: 30,
    cwd: CWD,
    env: { ...process.env } as Record<string, string>,
  });

  // PTY -> WebSocket
  ptyProcess.onData((data: string) => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    }
  });

  ptyProcess.onExit(({ exitCode }) => {
    console.log(`PTY exited with code ${exitCode}`);
    if (ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
  });

  // WebSocket -> PTY
  ws.on("message", (msg: Buffer | string) => {
    const data = typeof msg === "string" ? msg : msg.toString();
    // Handle resize messages
    if (data.startsWith("\x1b[RESIZE:")) {
      const match = data.match(/\x1b\[RESIZE:(\d+):(\d+)/);
      if (match) {
        ptyProcess.resize(parseInt(match[1], 10), parseInt(match[2], 10));
      }
      return;
    }
    ptyProcess.write(data);
  });

  ws.on("close", () => {
    connectionCount--;
    console.log(`Client disconnected (${connectionCount}/${MAX_CONNECTIONS}) — killing PTY`);
    ptyProcess.kill();
  });

  ws.on("error", (err) => {
    console.error("WebSocket error:", err.message);
    ptyProcess.kill();
  });
});
