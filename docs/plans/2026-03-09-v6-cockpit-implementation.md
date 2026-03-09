# Jake Console v6 — Cockpit Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform Jake Console v5 into a terminal-first cockpit with real xterm.js shell and 5-level capability maturity system with per-level checklists.

**Architecture:** Replace the fake React terminal with xterm.js connected to a Node.js WebSocket server that spawns a real PTY shell. Restructure the layout from dashboard-first to Cockpit Pattern (terminal 60-70% top, context panel 30-40% bottom). Add capability level checklists stored in YAML, exposed via new API endpoints, and rendered with segmented maturity bars.

**Tech Stack:** Next.js 16, React 19, xterm.js, node-pty, ws (WebSocket), Express, TypeScript, FastAPI (Python), YAML

**Design doc:** `docs/plans/2026-03-09-v6-cockpit-redesign.md`

---

## Round 1: WebSocket Terminal Server + xterm.js Client

### Task 1: Create the WebSocket terminal server

**Files:**
- Create: `apps/v5/server/terminal.ts`
- Create: `apps/v5/server/package.json`
- Create: `apps/v5/server/tsconfig.json`

**Step 1: Create server package.json**

```json
{
  "name": "jake-terminal-server",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "npx tsx server/terminal.ts",
    "build": "npx tsc -p server/tsconfig.json",
    "start": "node server/dist/terminal.js"
  },
  "dependencies": {
    "node-pty": "^1.0.0",
    "ws": "^8.18.0"
  },
  "devDependencies": {
    "tsx": "^4.19.0",
    "@types/ws": "^8.5.0",
    "typescript": "^5"
  }
}
```

Note: This goes inside `apps/v5/server/package.json`. The terminal server is a separate Node.js process from the Next.js dev server.

**Step 2: Create server/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "outDir": "dist",
    "rootDir": ".",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["terminal.ts"]
}
```

**Step 3: Write the terminal server**

```typescript
// apps/v5/server/terminal.ts
import { WebSocketServer, WebSocket } from "ws";
import * as pty from "node-pty";
import { platform } from "os";

const PORT = parseInt(process.env.TERMINAL_PORT || "8421", 10);
const SHELL = process.env.SHELL || (platform() === "win32" ? "powershell.exe" : "zsh");
const CWD = process.env.TERMINAL_CWD || "/Users/mikerodgers/Startup-Intelligence-OS";

const wss = new WebSocketServer({ port: PORT });
console.log(`Terminal server listening on ws://localhost:${PORT}`);

wss.on("connection", (ws: WebSocket) => {
  console.log("Client connected — spawning PTY");

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
    console.log("Client disconnected — killing PTY");
    ptyProcess.kill();
  });

  ws.on("error", (err) => {
    console.error("WebSocket error:", err.message);
    ptyProcess.kill();
  });
});
```

**Step 4: Install dependencies and verify server starts**

```bash
cd apps/v5/server && npm install
npx tsx terminal.ts
# Expected: "Terminal server listening on ws://localhost:8421"
# Ctrl+C to stop
```

**Step 5: Add terminal server to launch.json**

Update `.claude/launch.json` to add the terminal server:

```json
{
  "name": "terminal-server",
  "runtimeExecutable": "npx",
  "runtimeArgs": ["tsx", "server/terminal.ts"],
  "port": 8421,
  "cwd": "apps/v5"
}
```

**Step 6: Commit**

```bash
git add apps/v5/server/ .claude/launch.json
git commit -m "feat: add WebSocket terminal server with node-pty"
```

---

### Task 2: Add xterm.js client component

**Files:**
- Modify: `apps/v5/package.json` (add xterm deps)
- Create: `apps/v5/src/components/XTerminal.tsx`

**Step 1: Install xterm.js packages**

```bash
cd apps/v5 && npm install @xterm/xterm @xterm/addon-fit @xterm/addon-web-links
```

**Step 2: Create XTerminal component**

```typescript
// apps/v5/src/components/XTerminal.tsx
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

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      term.writeln("\x1b[32mConnected to shell.\x1b[0m");
      // Send initial resize
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

    // Terminal input -> WebSocket
    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      } else if (data === "\r") {
        // Reconnect on Enter if disconnected
        connect();
      }
    });
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

    // Handle container resize
    const resizeObserver = new ResizeObserver(() => {
      fitAddon.fit();
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(`\x1b[RESIZE:${term.cols}:${term.rows}`);
      }
    });
    resizeObserver.observe(containerRef.current);

    connect();

    return () => {
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
```

**Step 3: Verify build**

```bash
cd apps/v5 && npm run build
# Expected: builds clean, XTerminal not yet used in any page
```

**Step 4: Commit**

```bash
git add apps/v5/package.json apps/v5/package-lock.json apps/v5/src/components/XTerminal.tsx
git commit -m "feat: add xterm.js client component with WebSocket connection"
```

---

### Task 3: Restructure AppShell to Cockpit layout

**Files:**
- Modify: `apps/v5/src/components/AppShell.tsx`
- Create: `apps/v5/src/components/DragHandle.tsx`
- Modify: `apps/v5/src/app/globals.css` (add cockpit layout styles)

**Step 1: Create the DragHandle component**

```typescript
// apps/v5/src/components/DragHandle.tsx
"use client";
import { useCallback, useRef } from "react";

interface DragHandleProps {
  onResize: (terminalPercent: number) => void;
}

export function DragHandle({ onResize }: DragHandleProps) {
  const dragging = useRef(false);

  const onMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      dragging.current = true;

      const mainEl = (e.target as HTMLElement).closest(".main");
      if (!mainEl) return;
      const rect = mainEl.getBoundingClientRect();
      // Subtract topbar height (~52px)
      const topbarHeight = 52;
      const availableHeight = rect.height - topbarHeight;

      const onMouseMove = (moveEvent: MouseEvent) => {
        if (!dragging.current) return;
        const relativeY = moveEvent.clientY - rect.top - topbarHeight;
        const percent = Math.min(90, Math.max(30, (relativeY / availableHeight) * 100));
        onResize(percent);
      };

      const onMouseUp = () => {
        dragging.current = false;
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
      };

      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
    },
    [onResize]
  );

  return <div className="drag-handle" onMouseDown={onMouseDown} />;
}
```

**Step 2: Update AppShell to cockpit layout**

Replace the contents of `apps/v5/src/components/AppShell.tsx` with the cockpit layout. Key changes:
- Terminal zone at top (XTerminal component)
- DragHandle between terminal and context panel
- Context panel below with children
- Remove old Terminal component import
- Store split percentage in localStorage

The new AppShell renders:
```tsx
<div className="main">
  <Topbar />
  <div className="terminal-zone" style={{ flex: `0 0 ${splitPercent}%` }}>
    <XTerminal />
  </div>
  <DragHandle onResize={setSplitPercent} />
  <div className="context-zone">
    {children}
  </div>
</div>
```

**Step 3: Add cockpit CSS to globals.css**

Add these styles to `apps/v5/src/app/globals.css`:

```css
/* Cockpit layout - terminal zone */
.terminal-zone {
  min-height: 200px;
  overflow: hidden;
  background: #060810;
}

.xterminal {
  width: 100%;
  height: 100%;
}

/* Drag handle */
.drag-handle {
  height: 4px;
  background: var(--border);
  cursor: row-resize;
  flex-shrink: 0;
  transition: background 0.15s;
}
.drag-handle:hover,
.drag-handle:active {
  background: var(--accent);
}

/* Context zone */
.context-zone {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  min-height: 150px;
}

/* Main column now uses flexbox column */
.main {
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}
```

Also remove the old `.terminal`, `.terminal-header`, `.terminal-output`, `.terminal-input-wrap`, `.terminal-input`, `.terminal-prompt` CSS classes since the fake terminal is being replaced.

**Step 4: Verify build compiles**

```bash
cd apps/v5 && npm run build
```

**Step 5: Commit**

```bash
git add apps/v5/src/components/AppShell.tsx apps/v5/src/components/DragHandle.tsx apps/v5/src/app/globals.css
git commit -m "feat: restructure AppShell to cockpit layout with xterm.js terminal"
```

---

### Task 4: Remove old Terminal component and clean up

**Files:**
- Delete: `apps/v5/src/components/Terminal.tsx`
- Modify: `apps/v5/src/hooks/useKeyboard.ts` (update shortcut — `t` now focuses terminal container instead of toggling)

**Step 1: Delete old Terminal.tsx**

Remove `apps/v5/src/components/Terminal.tsx` — no longer needed.

**Step 2: Simplify useKeyboard.ts**

Remove the terminal toggle functionality. Keep only the view-switching shortcuts (1-6 keys).

**Step 3: Update AppShell to remove TerminalContext**

Remove `TerminalContext`, `useTerminal`, `terminalVisible`, `toggleTerminal` from AppShell since the terminal is now always visible.

**Step 4: Update Topbar to remove terminal toggle button**

Remove the "Terminal" button from Topbar since the terminal is always visible.

**Step 5: Verify build**

```bash
cd apps/v5 && npm run build
```

**Step 6: Commit**

```bash
git add -u apps/v5/src/
git commit -m "refactor: remove old fake terminal, simplify keyboard shortcuts"
```

---

### Task 5: Verify terminal works end-to-end

**Step 1: Start all 3 servers**

Start the terminal server (port 8421), the FastAPI backend (port 8420), and the Next.js console (port 3000).

**Step 2: Open browser and verify**

- Terminal zone should show at top 65% of center column
- Should see "Connected to shell." in green
- Type `ls` — should see repo files
- Type `bin/jake` — should run the jake preflight
- Type `git status` — should show git state
- Drag the handle to resize — should persist
- Context panel below should show the active view page content

**Step 3: Screenshot proof**

Take a screenshot showing the working terminal with real shell output.

---

## Round 2: Capability Level System (Backend)

### Task 6: Extend Capability model with levels

**Files:**
- Modify: `apps/decision_os/models.py`
- Modify: `apps/v5/src/lib/state.ts`

**Step 1: Add LevelItem and CapabilityLevels to models.py**

Add after the existing `Capability` model:

```python
class LevelItem(BaseModel):
    text: str
    done: bool = False

class CapabilityLevel(BaseModel):
    name: str  # Nascent, Emerging, Scaling, Optimizing, Leading
    items: list[LevelItem] = Field(default_factory=list)

class CapabilityWithLevels(Capability):
    """Extended capability with per-level checklists."""
    wave: int = 1
    maturity_target: float = 4.0
    levels: dict[int, CapabilityLevel] = Field(default_factory=dict)
```

**Step 2: Update frontend Capability interface in state.ts**

```typescript
export interface LevelItem {
  text: string;
  done: boolean;
}

export interface CapabilityLevel {
  name: string;
  items: LevelItem[];
}

export interface Capability {
  name: string;
  maturity: number;
  target: number;
  gaps: string[];
  wave: number;
  levels?: Record<number, CapabilityLevel>;
}
```

**Step 3: Commit**

```bash
git add apps/decision_os/models.py apps/v5/src/lib/state.ts
git commit -m "feat: add capability level checklists to data model"
```

---

### Task 7: Seed 12 capability YAML files with level checklists

**Files:**
- Create: `.startup-os/capabilities/data-analytics.yaml`
- Create: `.startup-os/capabilities/platform-infrastructure.yaml`
- Create: `.startup-os/capabilities/operator-experience.yaml`
- Create: `.startup-os/capabilities/innovation-strategy.yaml`
- Create: `.startup-os/capabilities/studio-operations.yaml`
- Create: `.startup-os/capabilities/portfolio-management.yaml`
- Create: `.startup-os/capabilities/content-marketing.yaml`
- Create: `.startup-os/capabilities/agent-orchestration.yaml`
- Create: `.startup-os/capabilities/decision-kernel.yaml`
- Create: `.startup-os/capabilities/capability-management.yaml`
- Create: `.startup-os/capabilities/ux-design.yaml`
- Create: `.startup-os/capabilities/intelligence-research.yaml`

Each YAML file follows the schema from the design doc with 3-5 items per level for levels 1-4. Level 1 items should mostly be marked `done: true` (capabilities are identified, scoped, owners assigned). Level 2 items should be partially done based on actual state. Levels 3-4 should be `done: false`.

**Step 1: Create all 12 YAML files**

Use the existing `.startup-os/capabilities/` directory. Each file has:
```yaml
id: <kebab-case-id>
name: <Display Name>
maturity_current: <current numeric>
maturity_target: 4
wave: <1|2|3>
owner_human: Mike Rodgers
owner_agent: <primary agent>
gaps:
  - <gap 1>
  - <gap 2>
levels:
  1:
    name: Nascent
    items:
      - text: "Capability identified and scoped"
        done: true
      # ... 2-4 more items
  2:
    name: Emerging
    items:
      # ... 3-5 items, some done based on actual state
  3:
    name: Scaling
    items:
      # ... 3-5 items, all done: false
  4:
    name: Optimizing
    items:
      # ... 3-5 items, all done: false
```

The items should be specific and verifiable based on the actual system state — not generic. Reference real files, endpoints, and capabilities that exist or need to exist.

**Step 2: Commit**

```bash
git add .startup-os/capabilities/
git commit -m "feat: seed 12 capability domains with level checklists"
```

---

### Task 8: Add API endpoints for capability levels

**Files:**
- Modify: `apps/decision_os/api.py`
- Modify: `apps/decision_os/store.py` (add level read/write)

**Step 1: Add capability level reader to Store**

Add a method to `Store` that reads a capability YAML file from `.startup-os/capabilities/` and returns the levels structure. Also add a method to toggle a checklist item and write it back.

```python
# In store.py
def get_capability_levels(self, capability_id: str) -> dict | None:
    """Read capability YAML and return levels structure."""
    path = self._root / ".startup-os" / "capabilities" / f"{capability_id}.yaml"
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text())
    return data

def toggle_capability_item(self, capability_id: str, level: int, index: int) -> dict | None:
    """Toggle a checklist item in a capability level."""
    path = self._root / ".startup-os" / "capabilities" / f"{capability_id}.yaml"
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text())
    levels = data.get("levels", {})
    level_data = levels.get(level)
    if not level_data or index >= len(level_data.get("items", [])):
        return None
    level_data["items"][index]["done"] = not level_data["items"][index]["done"]
    # Auto-compute maturity: highest level where all items are done
    computed_maturity = 0
    for lvl in sorted(levels.keys()):
        items = levels[lvl].get("items", [])
        if items and all(item.get("done") for item in items):
            computed_maturity = lvl
        else:
            break
    data["maturity_current"] = computed_maturity
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    return data
```

**Step 2: Add API endpoints**

```python
# In api.py
@app.get("/api/capabilities/{capability_id}/levels")
def get_capability_levels(capability_id: str) -> dict:
    data = store.get_capability_levels(capability_id)
    if data is None:
        raise HTTPException(404, f"Capability {capability_id} not found")
    return data

@app.put("/api/capabilities/{capability_id}/levels/{level}/items/{index}")
def toggle_capability_item(capability_id: str, level: int, index: int) -> dict:
    data = store.toggle_capability_item(capability_id, level, index)
    if data is None:
        raise HTTPException(404, f"Capability {capability_id} not found or invalid level/index")
    return data

@app.get("/api/capabilities/summary")
def get_capabilities_summary() -> list[dict]:
    """Return all capabilities with computed maturity from level checklists."""
    caps_dir = store._root / ".startup-os" / "capabilities"
    results = []
    for path in sorted(caps_dir.glob("*.yaml")):
        if path.stem in ("README", "agent-readiness-index"):
            continue
        data = yaml.safe_load(path.read_text())
        if "levels" not in data:
            continue
        # Compute progress
        levels = data.get("levels", {})
        total_items = sum(len(l.get("items", [])) for l in levels.values())
        done_items = sum(
            sum(1 for item in l.get("items", []) if item.get("done"))
            for l in levels.values()
        )
        # Find next incomplete level
        next_level = None
        next_item = None
        for lvl in sorted(levels.keys()):
            items = levels[lvl].get("items", [])
            for item in items:
                if not item.get("done"):
                    next_level = lvl
                    next_item = item.get("text")
                    break
            if next_level:
                break
        # Check threshold (1 item from leveling up)
        threshold = False
        for lvl in sorted(levels.keys()):
            items = levels[lvl].get("items", [])
            undone = [i for i in items if not i.get("done")]
            if len(undone) == 1:
                threshold = True
                break

        results.append({
            "id": data.get("id", path.stem),
            "name": data.get("name", path.stem),
            "maturity_current": data.get("maturity_current", 0),
            "maturity_target": data.get("maturity_target", 4),
            "wave": data.get("wave", 1),
            "gaps": data.get("gaps", []),
            "total_items": total_items,
            "done_items": done_items,
            "progress_percent": round(done_items / total_items * 100) if total_items else 0,
            "next_level": next_level,
            "next_item": next_item,
            "threshold": threshold,
            "owner_agent": data.get("owner_agent", ""),
        })
    results.sort(key=lambda r: (r["wave"], r["maturity_current"]))
    return results
```

**Step 3: Add `import yaml` to api.py if not present**

**Step 4: Test the endpoints**

```bash
curl http://localhost:8420/api/capabilities/summary | python3 -m json.tool
curl http://localhost:8420/api/capabilities/decision-kernel/levels | python3 -m json.tool
```

**Step 5: Commit**

```bash
git add apps/decision_os/api.py apps/decision_os/store.py
git commit -m "feat: add capability level API endpoints with auto-maturity"
```

---

## Round 3: Frontend Capability Visualization

### Task 9: Add capability level API to frontend

**Files:**
- Modify: `apps/v5/src/lib/api.ts`
- Modify: `apps/v5/src/hooks/useApi.ts`

**Step 1: Add level endpoints to api.ts**

```typescript
// Add to api.ts
capabilitySummary: () => fetchJson<CapabilitySummary[]>("/capabilities/summary"),
capabilityLevels: (id: string) => fetchJson<CapabilityWithLevels>(`/capabilities/${id}/levels`),
toggleItem: (id: string, level: number, index: number) =>
  fetch(`${API_BASE}/capabilities/${id}/levels/${level}/items/${index}`, { method: "PUT" })
    .then((r) => { if (!r.ok) throw new Error(`API error: ${r.status}`); return r.json(); }),
```

**Step 2: Add SWR hook for capability summary**

In `useApi.ts`, add a `capabilitySummary` SWR call and include it in the return value.

**Step 3: Commit**

```bash
git add apps/v5/src/lib/api.ts apps/v5/src/hooks/useApi.ts
git commit -m "feat: add capability level API hooks to frontend"
```

---

### Task 10: Create MaturityBar component with level segments

**Files:**
- Create: `apps/v5/src/components/MaturityBar.tsx`

**Step 1: Create the component**

The MaturityBar shows 5 segments labeled NAS/EMR/SCL/OPT/LDG, filled based on maturity, with gradient fill for partial levels, dashed outline for target, and a threshold marker when 1 item from leveling up.

Colors per level from design doc:
- Level 1 (Nascent): `#e06565`
- Level 2 (Emerging): `#e8a84c`
- Level 3 (Scaling): `#5b8def`
- Level 4 (Optimizing): `#5cd4a0`
- Level 5 (Leading): `#c4a1f7`

Props:
```typescript
interface MaturityBarProps {
  maturity: number;       // 0-5
  target: number;         // 0-5
  threshold?: boolean;    // show threshold marker
  compact?: boolean;      // omit labels for list views
}
```

**Step 2: Add CSS for MaturityBar to globals.css**

**Step 3: Commit**

```bash
git add apps/v5/src/components/MaturityBar.tsx apps/v5/src/app/globals.css
git commit -m "feat: add MaturityBar component with 5-level segments"
```

---

### Task 11: Create LevelChecklist component

**Files:**
- Create: `apps/v5/src/components/LevelChecklist.tsx`

**Step 1: Create the component**

Shows a vertical stack of levels 1-5, each with a name, color indicator, and checklist items. Completed levels are fully filled. The current level shows its checklist with toggleable items (clickable checkboxes). Future levels are grayed out.

Props:
```typescript
interface LevelChecklistProps {
  capabilityId: string;
  levels: Record<number, CapabilityLevel>;
  currentMaturity: number;
  onToggle: (level: number, index: number) => void;
}
```

Calls `PUT /api/capabilities/{id}/levels/{level}/items/{index}` on checkbox click via the `onToggle` callback.

**Step 2: Add CSS**

**Step 3: Commit**

```bash
git add apps/v5/src/components/LevelChecklist.tsx apps/v5/src/app/globals.css
git commit -m "feat: add LevelChecklist component with toggleable items"
```

---

### Task 12: Update CapabilitiesPage and CapabilityDrilldown

**Files:**
- Modify: `apps/v5/src/app/capabilities/page.tsx`
- Modify: `apps/v5/src/components/CapabilityDrilldown.tsx`

**Step 1: Update CapabilitiesPage**

Replace the old maturity segments with the new `MaturityBar` component. Use the `/api/capabilities/summary` data when available (with fallback to static data). Show threshold markers and progress percentages.

**Step 2: Update CapabilityDrilldown**

When expanded, fetch the capability's full level data via `/api/capabilities/{id}/levels` and render a `LevelChecklist`. Show the "next item" prominently. Include the progress fraction (e.g., "7/13 steps — 54%").

**Step 3: Verify build**

```bash
cd apps/v5 && npm run build
```

**Step 4: Commit**

```bash
git add apps/v5/src/app/capabilities/page.tsx apps/v5/src/components/CapabilityDrilldown.tsx
git commit -m "feat: wire capability maturity bars and level checklists to views"
```

---

### Task 13: Update Home page and 25X Dashboard

**Files:**
- Modify: `apps/v5/src/app/page.tsx`
- Modify: `apps/v5/src/app/dashboard/page.tsx`

**Step 1: Update Home page**

Add focus capability section — show the single lowest-maturity Wave 1 domain with its next action. Show "X capabilities waiting behind this one." Show endowed progress: "Y/Z steps complete (N%)."

**Step 2: Update 25X Dashboard**

Replace the simple progress bars with the new `MaturityBar` components. Add a domain heat map grid color-coded by maturity level. Show aggregate progress.

**Step 3: Commit**

```bash
git add apps/v5/src/app/page.tsx apps/v5/src/app/dashboard/page.tsx
git commit -m "feat: add focus capability to home, maturity bars to dashboard"
```

---

## Round 4: Polish + Verify

### Task 14: Full end-to-end verification

**Step 1: Start all servers**

- Terminal server on :8421
- FastAPI on :8420
- Next.js on :3000

**Step 2: Verify terminal**

- Real shell works (ls, git, claude, bin/jake)
- Resize drag handle works
- Terminal reconnects on disconnect

**Step 3: Verify capability system**

- `/capabilities` page shows MaturityBars with correct levels
- Drill-down shows LevelChecklist with real items from YAML
- Toggling a checklist item updates YAML and refreshes UI
- Auto-maturity advancement works when all items in a level complete
- Threshold markers appear when 1 item from leveling up

**Step 4: Verify all views**

Cycle through all 6 views — zero console errors, zero server errors.

**Step 5: Screenshot proof**

Take screenshots of:
1. Cockpit layout with terminal and context panel
2. Capability maturity bars
3. Level checklist drill-down

**Step 6: Final commit**

```bash
git add -A
git commit -m "feat: complete v6 cockpit redesign with terminal and maturity system"
```

---

## Summary

| Round | Tasks | Description |
|-------|-------|-------------|
| 1 | 1-5 | WebSocket terminal server, xterm.js client, cockpit layout, cleanup, e2e verify |
| 2 | 6-8 | Capability model with levels, 12 YAML seeds, API endpoints |
| 3 | 9-13 | Frontend hooks, MaturityBar, LevelChecklist, page updates |
| 4 | 14 | Full verification and final commit |

**Total:** 14 tasks across 4 rounds.
