# Research Brief: AI Agents Controlling Entire Desktops (macOS Focus)

**Date**: 2026-03-19
**Researcher**: Jake (via Exa Deep Search, Brave Search)
**Status**: COMPLETE
**Confidence**: AUTO (primary sources verified)

---

## 1. Anthropic Computer Use

### What It Is
Claude's beta capability to control desktop environments via screenshot-action loops. Available since Oct 2024, updated through 2025.

### How It Works Architecturally
- **Loop**: Your code takes screenshot -> sends to Claude API -> Claude returns JSON action (click, type, scroll) -> your code executes action -> repeat
- **Vision-only**: Claude sees base64 screenshots (resized to ~1024x768), counts pixels to determine click coordinates. No DOM/accessibility tree access.
- **"Flipbook" perception**: Discrete screenshot-action cycles, not continuous screen streaming.

### API Details
- **Endpoint**: `POST https://api.anthropic.com/v1/messages` with beta header
- **Latest tool version**: `computer_20251124` (for Opus 4.6, Sonnet 4.6, Opus 4.5) — adds `zoom` action for region inspection
- **Previous version**: `computer_20250124` (Sonnet 4.5, Haiku 4.5, Opus 4.1, etc.)
- **Actions**: `screenshot`, `mouse_move`, `left_click`, `right_click`, `double_click`, `type`, `key`, `scroll`, `wait`, `hold_key`, `drag`, `zoom`
- **Combine with**: `bash` tool and `text_editor` tool for full automation

### Code Example
```python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[{
        "type": "computer_20251124",
        "name": "computer",
        "display_width_px": 1024,
        "display_height_px": 768,
        "display_number": 1,
        "enable_zoom": True
    }],
    betas=["computer-use-2025-11-24"],
    messages=[{"role": "user", "content": "Save a picture of a cat to my desktop."}]
)
```

### Production Readiness
- **BETA ONLY** — not ZDR-eligible
- ~2-5s per action (slow)
- Error-prone on pixel coordinates
- Recommended: run in Docker/VM containers only, NOT direct host access
- Prompt injection risk from screen content
- Reference implementation: `anthropic-quickstarts` repo (Docker + web UI + agent loop)

### Hermes Relevance
Claude Computer Use is the most direct path. Hermes could wrap the API in an agent loop, run against the local macOS screen (with appropriate safeguards), and use `zoom` for precision. The 2-5s/action latency is the main bottleneck.

### Sources
- https://docs.anthropic.com/en/docs/agents-and-tools/computer-use
- https://www.anthropic.com/news/developing-computer-use
- https://github.com/anthropics/anthropic-quickstarts

---

## 2. Apple Accessibility APIs (macOS)

### Three Layers of Control

#### AXUIElement (Low-level C API)
- **Framework**: ApplicationServices
- **What**: Query/manipulate any UI element in any app. Get windows, buttons, text fields. Read attributes (title, role, position, size, enabled state). Perform actions (press, show menu).
- **Key functions**:
  - `AXUIElementCreateApplication(pid)` — get app's root element
  - `AXUIElementCopyAttributeValue()` — read attributes
  - `AXUIElementPerformAction()` — click/press actions
  - `AXUIElementCopyElementAtPosition(x, y)` — find element at coordinates
  - `AXUIElementSetAttributeValue()` — move/resize windows
- **Best for**: Precise, fast, structured control. The "blueprint" approach vs screenshot "photo" approach.

#### AppleScript System Events (High-level scripting)
- **What**: `tell application "System Events" tell process "AppName"` — interact with any app's UI
- **Capabilities**: Click buttons, read menus, type keystrokes, query UI hierarchy
- **Inspect with**: Accessibility Inspector (Xcode developer tool)
- **Example**: `tell process "Safari" to name of every menu of menu bar 1`

#### CGEvent (Low-level input simulation)
- **What**: Create and post synthetic keyboard/mouse events globally
- **Key classes**: `CGEvent(keyboardEventSource:virtualKey:keyDown:)`, `CGEvent(mouseEventSource:mouseType:mouseCursorPosition:mouseButton:)`
- **Post with**: `CGEventPost(tap: .cgSessionEventTap)`
- **Best for**: Simulating raw input when accessibility actions don't work

### Permissions Required (TCC)
- **ALL** require Accessibility permission in System Settings > Privacy & Security > Accessibility
- Check: `AXIsProcessTrusted()` or `AXIsProcessTrustedWithOptions()`
- Prompt user: `AXIsProcessTrustedWithOptions([kAXTrustedCheckOptionPrompt: true])`
- Info.plist needs: `NSAccessibilityUsageDescription`
- App must be code-signed for TCC recognition
- User manually grants per-app

### Hermes Relevance
This is the FAST path. AXUIElement gives structured data (<100ms vs 2-5s for vision). An agent could read the accessibility tree to understand what's on screen, then use AXUIElement actions or CGEvent for input. This is what Hammerspoon uses under the hood. Combine with Claude for reasoning about WHAT to do, use accessibility APIs for HOW to do it.

### Sources
- https://developer.apple.com/documentation/applicationservices/axuielement
- https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/AutomatetheUserInterface.html
- https://jano.dev/apple/macos/swift/2025/01/08/Accessibility-Permission.html

---

## 3. Hammerspoon + AI

### Current State
Hammerspoon is a macOS automation bridge (Lua scripting) that controls windows, hotkeys, system events, mouse/keyboard. Several AI integrations exist:

### Existing Projects

| Project | What It Does | URL |
|---------|-------------|-----|
| **cursor-auto-accept** | Hammerspoon script auto-accepts Cursor AI agent commands via Cmd+Return keystrokes | https://github.com/2mawi2/cursor-auto-accept |
| **DescribeImage.spoon** | Uses OpenAI Vision API (GPT-4) to describe images under VoiceOver cursor | https://github.com/mikolysz/DescribeImage.spoon |
| **ChatGPT Spoon** | Replaces clipboard contents with ChatGPT completions via hotkey | https://gist.github.com/jcconnell/1a7bf4354dd6535240da6989702b3a18 |
| **LobeHub Hammerspoon Skill** | Skill for Claude/Cursor to generate Hammerspoon configs | https://lobehub.com/skills/plinde-claude-plugins-hammerspoon |
| **SkillMD.ai Hammerspoon** | SKILL.md for AI agents to use Hammerspoon | http://skillmd.ai/how-to-build/hammerspoon-1/ |

### Architecture Pattern
- AI agents use `hs` CLI (via `hs.ipc`) to execute Lua code on the running Hammerspoon instance
- `require("hs.ipc")` enables IPC support
- CLI: `hs -c "hs.application.launchOrFocus('Safari')"` — any Lua code
- Hammerspoon provides: window management, app control, mouse/keyboard simulation, system events, notifications, audio, WiFi, battery, USB watchers

### Gap
No full AI-agent-to-Hammerspoon bridge exists yet. The pattern is always: AI generates Lua code, sends via `hs -c`. Nobody has built a persistent agent loop that uses Hammerspoon as its hands.

### Hermes Relevance
Hammerspoon is already in our stack. The `hs` CLI is the perfect execution layer. Hermes could: (1) read accessibility tree via hs.axuielement, (2) reason with Claude about what to do, (3) execute via `hs -c` commands. This is the hybrid architecture.

### Sources
- https://www.hammerspoon.org/docs/hs.ipc.html
- https://mcpmarket.com/tools/skills/macos-desktop-automation-hammerspoon

---

## 4. Open Interpreter

### Architecture
Open Interpreter is an open-source project (130 contributors, 48 releases) that lets LLMs run code locally. Its **OS Mode** is the desktop control feature.

### How It Works
1. **Computer API** — Python primitives the LLM generates code against:
   - `computer.display.view()` — takes screenshot, returns PIL image
   - `computer.mouse.click("On-screen text")` — OCR-locates text, clicks
   - `computer.mouse.click(icon="gear icon")` — icon recognition
   - `computer.keyboard.write("text")` — type text
   - `computer.keyboard.hotkey("command", "space")` — keyboard shortcuts
   - `computer.mouse.scroll(-10)` — scroll
   - `computer.clipboard.view()` — read clipboard

2. **Screen Reading**: Screenshots + pytesseract OCR (offline) or hosted API. No accessibility tree.

3. **LLM Integration**: Via LiteLLM — supports GPT-4V, Claude, local models (Ollama, LM Studio)

4. **Agent Loop**: LLM receives screenshot, generates Python code using Computer API, code executes, new screenshot taken, loop continues.

5. **Mac-specific modules**: Mail, Contacts, Calendar, SMS (via AppleScript bridges)

### Desktop App (2025)
Open Interpreter pivoted to a desktop app focused on document editing (Excel, PDF, Word, Markdown) rather than full OS control. The CLI OS Mode remains experimental.

### Production Readiness
- **Experimental** — error-prone, slow
- Each action requires LLM inference (~2-7s)
- Relies on PyAutoGUI for mouse/keyboard (fragile on macOS)
- Screen recording permissions required
- No multi-display support
- Offline mode uses OpenCV (lower quality than hosted vision)

### Hermes Relevance
The Computer API pattern is worth studying. The `click("text")` approach using OCR is clever but slower than accessibility tree. The architecture of LLM -> Python code -> Computer API is a good reference for Hermes's agent loop.

### Sources
- https://github.com/openinterpreter/open-interpreter
- https://docs.openinterpreter.com/guides/os-mode
- https://docs.openinterpreter.com/code-execution/computer-api

---

## 5. Browser Automation Comparison

### The Three Contenders

| Tool | Type | Approach | Stars | Best For | Cost |
|------|------|----------|-------|----------|------|
| **Browser Use** | Full AI agent framework (Python) | DOM + LLM agent loop | 81k+ | Autonomous multi-step browsing | Free OSS + LLM costs |
| **Browserbase + Stagehand** | Cloud infra + hybrid AI SDK | Playwright + targeted AI | 21.6k | Production scraping/automation | ~$20+/mo |
| **Playwright MCP** | MCP server | Accessibility tree snapshots | 29.2k | Dev/testing, AI-assisted | Free |

### Browser Use (Best for Always-On Agent)
- 89.1% on WebVoyager benchmark (highest published)
- Full agent loop with memory, planning, multi-tab support
- Vision mode (screenshots) + DOM extraction mode
- Composable with LangChain, CrewAI
- Anti-detect browsers, CAPTCHA solving (cloud tier)
- **GitHub**: https://github.com/browser-use/browser-use

### Browserbase
- Cloud-managed headless browsers via Chrome DevTools Protocol
- Stagehand SDK: `act()`, `extract()`, `observe()` — hybrid deterministic + AI
- Scalable (1000s of browsers), stealth, session persistence
- $40M Series B (June 2025)
- **URL**: https://www.browserbase.com

### Playwright MCP
- Microsoft's official MCP server for browser automation
- Uses accessibility tree snapshots (NOT screenshots) — 93% more token-efficient than raw DOM
- 13+ tools: navigate, click, type, screenshot, evaluate, etc.
- Ships with GitHub Copilot Agent
- Sub-100ms actions (no LLM inference per action)
- **URL**: https://playwright.dev/agents

### Recommendation for Hermes
**Browser Use** for autonomous browsing tasks (it has the highest benchmark scores and full agent capabilities). Pair with **Browserbase** cloud for production scaling/stealth. Use **Playwright MCP** for structured, fast browser control when you don't need AI reasoning per step.

### Sources
- https://www.nxcode.io/resources/news/stagehand-vs-browser-use-vs-playwright-ai-browser-automation-2026
- https://awesomeagents.ai/tools/best-ai-browser-automation-tools-2026/

---

## 6. Screen Reading: How Agents "See"

### Three Approaches Compared

| Method | Speed | Cost | Accuracy | Works On |
|--------|-------|------|----------|----------|
| **Accessibility Tree** | <100ms/action | Free (local) | High (structured data) | Apps with accessibility support |
| **Screenshots + Vision LLM** | 2-7s/action | $$$ (image tokens) | Medium (hallucinations) | Any visual UI |
| **OCR (pytesseract/hosted)** | ~500ms | Low | Low-Medium | Text-heavy UIs |

### Accessibility Tree (Best for Speed/Accuracy)
- macOS: AXUIElement API provides element roles, names, states, positions, hierarchy
- Web: Browser's built-in accessibility tree (what screen readers use)
- **93% more token-efficient** than raw DOM for web
- Used by: Playwright MCP, Fazm, ChatGPT Atlas
- **Limitation**: Only works on apps that properly implement accessibility

### Screenshots + Vision Models (Best for Universality)
- Capture full screen, send to GPT-4V/Claude Vision/Qwen-2.5-VL
- Model identifies UI elements, determines coordinates for actions
- Used by: Anthropic Computer Use, Google Project Mariner, OpenAI Operator
- **Enhancement**: Microsoft OmniParser V2 — pre-processes screenshots to identify interactable elements, boosting vision model accuracy

### OCR
- Extract text from screenshots via pytesseract (offline) or hosted API
- **WARNING**: "OCR is a narrator, UI state is the truth" — OCR misreads labels, ignores enabled/disabled states, misses z-index layering
- Use OCR for CONTENT reading, never for CONTROL decisions
- Always prefer: UI automation state > visual detection > OCR

### Hybrid Approach (Best Overall)
The winning architecture: Use accessibility tree for speed/efficiency, fall back to screenshots + vision for apps without accessibility support. Google Mariner and Browser Use both do this.

### Microsoft OmniParser (Key Tool)
- **Paper**: arXiv:2408.00203 (Oct 2024)
- **What**: Screen parsing module that converts UI screenshots into structured elements
- Fine-tuned detection model identifies interactable icons + captioning model describes functionality
- Makes any vision LLM better at GUI grounding
- **V2** (Feb 2025): State-of-the-art on ScreenSpot benchmark
- **GitHub**: https://github.com/microsoft/OmniParser

### Sources
- https://fazm.ai/blog/how-ai-agents-see-your-screen-dom-vs-screenshots
- https://medium.com/data-science-at-microsoft/where-ai-meets-gui-an-overview-of-computer-using-agents-3085d3bbe332
- https://www.microsoft.com/en-us/research/articles/omniparser-for-pure-vision-based-gui-agent/

---

## 7. Claude Code Monitoring

### Can an Agent Detect What Claude Code Is Doing?

**Yes, multiple approaches exist:**

| Tool | What It Does | URL |
|------|-------------|-----|
| **claude-esp** (phiat) | Go-based TUI that streams Claude Code's hidden output (thinking, tool calls, subagents) to a separate terminal | https://github.com/hesreallyhim/awesome-claude-code |
| **Claude Code Usage Monitor** | Real-time usage monitor with predictions, warnings, plan recognition. Auto-detects terminal theme, timezone. Tracks 5-hour rolling session windows. | https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor |
| **Datadog AI Agents Console** | Aggregates Claude Code metrics: latency percentiles, error rates, failed bash commands, success rates by repository | https://www.datadoghq.com/blog/claude-code-monitoring/ |
| **Session search MCP** | Local tool that indexes past Claude Code sessions (tool calls, errors, results). Works as MCP server for cross-session search. | Reddit: r/ClaudeAI |
| **AI Coding Agent Dashboard** (Marc Nuri) | Real-time dashboard to monitor and orchestrate multiple AI coding agents across projects/devices | https://blog.marcnuri.com/ai-coding-agent-dashboard |

### How Claude Code Exposes Data
- Claude Code's IDE plugins see: open files, current selection, integrated terminal output
- The `~/.claude/` directory contains session data, settings, memory
- Hooks system (pre/post tool use, session start/stop) can capture events
- OpenTelemetry integration possible for structured telemetry

### Hermes Relevance
Hermes could monitor Claude Code via: (1) `claude-esp` for real-time output streaming, (2) hooks for event capture, (3) session file monitoring in `~/.claude/`, (4) terminal output parsing.

---

## 8. Academic Papers (2024-2025)

### Key Papers

| Paper | arXiv | Date | Key Contribution |
|-------|-------|------|-----------------|
| **OSWorld** | 2404.07972 | Apr 2024 | First real computer environment benchmark for multimodal agents. 369 tasks across Ubuntu/Windows/macOS. Best model: 12.24% vs human 72.36%. |
| **ScreenAgent** | 2402.07945 | Feb 2024 | VLM-driven agent for computer control via screenshots + mouse/keyboard. Comparable to GPT-4V with better UI positioning. Published at IJCAI 2024. |
| **CogAgent** | 2312.08914 | Dec 2023 (updated Dec 2024) | 18B parameter VLM for GUI agents. Dual encoder (low+high res, 1120x1120 input). SOTA on Mind2Web and AITW using only screenshots. |
| **UFO2: The Desktop AgentOS** | 2504.14603 | Apr 2025 | Microsoft's multiagent system for Windows. HostAgent + AppAgents with native APIs. Hybrid control: Windows UI Automation + vision-based parsing. Shadow desktop for non-disruptive execution. |
| **OSWorld-Human** | 2506.16042 | Jun 2025 | Efficiency benchmark. Even best agents take 1.4-2.7x more steps than humans. LLM planning/reflection = 75-94% of total latency. |
| **LLM-Brained GUI Agents Survey** | 2411.18279 | Nov 2024 (updated May 2025) | Comprehensive survey — 12 revisions. Covers frameworks, training data, action models, evaluation. Best single reference. |
| **OS Agents Survey** | 2508.04482 | 2025 | Survey covering mobile, desktop, web agents. Accepted at ACL 2025. Covers environment types, benchmarks, architectures. |
| **OmniParser** | 2408.00203 | Aug 2024 | Screen parsing for vision-based agents. Detection + captioning models. #1 trending on HuggingFace. V2 (Feb 2025) is SOTA on ScreenSpot. |
| **CUA-Skill** | 2601.21123 | Jan 2026 | Skill-based approach for Computer Use Agents. 57.5% on WindowsAgentArena (1.7-3.6x improvement over prior SOTA). |
| **UI-TARS** | 2501.12326 | Jan 2025 | ByteDance. Pioneering automated GUI interaction with native agents. |

### Key Findings Across Papers
1. **The gap is enormous**: Best AI agents achieve ~12-57% on benchmarks vs 72%+ for humans
2. **LLM inference is the bottleneck**: 75-94% of agent latency is planning/reflection, not execution
3. **Hybrid wins**: Vision-only is fragile; combining accessibility APIs + vision outperforms either alone
4. **Deep OS integration matters**: UFO2's approach (native APIs, domain knowledge per app) dramatically outperforms shallow screenshot-based agents
5. **Efficiency is unsolved**: Agents take 1.4-2.7x more steps than necessary even when they succeed

---

## Architecture Recommendation for Hermes

### The Optimal Stack (macOS)

```
Layer 4: Claude API (reasoning)
  - Receives structured state (accessibility tree + optional screenshot)
  - Decides WHAT to do next
  - Returns action in structured format

Layer 3: Hermes Agent Loop (orchestration)
  - Manages state, memory, task decomposition
  - Routes between browser and desktop control
  - Monitors progress, handles errors

Layer 2: Execution Layer (control)
  - Desktop: Hammerspoon (hs CLI) + AXUIElement for structured control
  - Browser: Browser Use (autonomous) or Playwright MCP (fast/structured)
  - Fallback: Claude Computer Use API for apps without accessibility

Layer 1: Perception Layer (seeing)
  - Primary: Accessibility tree via hs.axuielement (fast, structured, free)
  - Secondary: Screenshots + Claude Vision (for non-accessible apps)
  - Enhancement: OmniParser for better screenshot understanding
```

### Why This Beats Pure Computer Use
- **10-50x faster** per action (accessibility tree vs screenshot+vision)
- **10x cheaper** (no image tokens for most actions)
- **More reliable** (structured data vs pixel guessing)
- **Privacy-preserving** (no screenshots sent to cloud for most actions)
- **Hybrid fallback** covers the 20% of apps that need vision

### Implementation Priority
1. **Hammerspoon as execution layer** (already in stack, hs CLI ready)
2. **AXUIElement wrapper** for reading macOS UI state
3. **Claude API integration** for reasoning about what to do
4. **Browser Use** for web tasks
5. **Claude Computer Use** as fallback for non-accessible apps
6. **OmniParser** for enhanced screenshot understanding when vision needed
