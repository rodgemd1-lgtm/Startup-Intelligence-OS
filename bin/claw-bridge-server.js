#!/usr/bin/env node
/**
 * Claw Remote Bridge Server
 * Runs on Mike's Mac. Exposes local connectors (Apple Calendar, Apple Mail, etc.)
 * to the remote VM over Tailscale.
 *
 * Start: node bin/claw-bridge-server.js
 * Default port: 7842 (configurable via PORT env var)
 *
 * Endpoints:
 *   GET  /api/claw/status          — connector health check
 *   GET  /api/claw/remote-brief    — morning brief (calendar + mail summary)
 *   GET  /api/claw/calendar?date=YYYY-MM-DD  — calendar events for a date
 *   GET  /api/claw/mail?limit=20   — recent unread emails
 *   POST /api/claw/remote-command  — run a safe local command { command: "brief|status|sync|signals" }
 */

const http = require("http");
const { execSync, exec } = require("child_process");

const PORT = process.env.PORT || 7842;
const BIND = process.env.BIND || "100.103.237.24"; // Tailscale IP — only accessible on tailnet

// ── Apple Calendar via AppleScript ──────────────────────────────────────────

function getCalendarEvents(dateStr) {
  const date = dateStr || new Date().toISOString().split("T")[0];
  const [year, month, day] = date.split("-").map(Number);

  const script = `
    set targetDate to current date
    set year of targetDate to ${year}
    set month of targetDate to ${month}
    set day of targetDate to ${day}
    set hours of targetDate to 0
    set minutes of targetDate to 0
    set seconds of targetDate to 0

    set endDate to targetDate + (86400)

    set output to ""
    tell application "Calendar"
      set allCals to every calendar
      repeat with cal in allCals
        set calName to name of cal
        set evts to (every event of cal whose start date >= targetDate and start date < endDate)
        repeat with evt in evts
          set evtTitle to summary of evt
          set evtStart to start date of evt
          set evtEnd to end date of evt
          set output to output & calName & "|" & evtTitle & "|" & (evtStart as string) & "|" & (evtEnd as string) & "\\n"
        end repeat
      end repeat
    end tell
    return output
  `;

  try {
    const result = execSync(`osascript -e '${script.replace(/'/g, "'\\''")}'`, {
      timeout: 15000,
      encoding: "utf8",
    });
    const events = result
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((line) => {
        const [calendar, title, start, end] = line.split("|");
        return { calendar, title, start, end };
      })
      .sort((a, b) => new Date(a.start) - new Date(b.start));
    return { ok: true, date, source: "apple-work-calendar", events };
  } catch (err) {
    return { ok: false, source: "apple-work-calendar", error: err.message };
  }
}

// ── Apple Mail via AppleScript ───────────────────────────────────────────────

function getRecentMail(limit = 20) {
  const script = `
    set output to ""
    tell application "Mail"
      set unread to (every message of inbox whose read status is false)
      set msgLimit to ${limit}
      set count to 0
      repeat with msg in unread
        if count >= msgLimit then exit repeat
        set sender to sender of msg
        set subj to subject of msg
        set dt to date received of msg
        set output to output & sender & "|" & subj & "|" & (dt as string) & "\\n"
        set count to count + 1
      end repeat
    end tell
    return output
  `;

  try {
    const result = execSync(`osascript -e '${script.replace(/'/g, "'\\''")}'`, {
      timeout: 15000,
      encoding: "utf8",
    });
    const messages = result
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((line) => {
        const [from, subject, date] = line.split("|");
        return { from, subject, date };
      });
    return { ok: true, source: "apple-work-mail", messages };
  } catch (err) {
    return { ok: false, source: "apple-work-mail", error: err.message };
  }
}

// ── Remote Brief ─────────────────────────────────────────────────────────────

function getRemoteBrief() {
  const today = new Date().toISOString().split("T")[0];
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split("T")[0];

  const cal = getCalendarEvents(tomorrow);
  const mail = getRecentMail(10);

  return {
    ok: true,
    generated_at: new Date().toISOString(),
    tomorrow_date: tomorrow,
    calendar: cal,
    mail: mail,
  };
}

// ── Status ───────────────────────────────────────────────────────────────────

function getStatus() {
  const calTest = getCalendarEvents(new Date().toISOString().split("T")[0]);
  const mailTest = getRecentMail(1);
  return {
    ok: true,
    connectors: {
      "apple-work-calendar": calTest.ok ? "connected" : "error: " + calTest.error,
      "apple-work-mail": mailTest.ok ? "connected" : "error: " + mailTest.error,
    },
    tailscale_ip: BIND,
    port: PORT,
    version: "1.0.0",
  };
}

// ── HTTP Server ───────────────────────────────────────────────────────────────

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", "*");

  console.log(`[${new Date().toISOString()}] ${req.method} ${path}`);

  try {
    if (path === "/api/claw/status") {
      return res.end(JSON.stringify(getStatus(), null, 2));
    }

    if (path === "/api/claw/remote-brief") {
      return res.end(JSON.stringify(getRemoteBrief(), null, 2));
    }

    if (path === "/api/claw/calendar") {
      const date = url.searchParams.get("date");
      return res.end(JSON.stringify(getCalendarEvents(date), null, 2));
    }

    if (path === "/api/claw/mail") {
      const limit = parseInt(url.searchParams.get("limit") || "20", 10);
      return res.end(JSON.stringify(getRecentMail(limit), null, 2));
    }

    if (path === "/api/claw/remote-command" && req.method === "POST") {
      let body = "";
      req.on("data", (chunk) => (body += chunk));
      req.on("end", () => {
        try {
          const { command } = JSON.parse(body);
          const allowed = ["brief", "status", "sync", "signals", "context"];
          if (!allowed.includes(command)) {
            res.statusCode = 400;
            return res.end(JSON.stringify({ ok: false, error: "Command not allowed: " + command }));
          }
          if (command === "brief") return res.end(JSON.stringify(getRemoteBrief(), null, 2));
          if (command === "status") return res.end(JSON.stringify(getStatus(), null, 2));
          res.end(JSON.stringify({ ok: true, command, result: "not implemented yet" }));
        } catch (e) {
          res.statusCode = 400;
          res.end(JSON.stringify({ ok: false, error: "Bad request body" }));
        }
      });
      return;
    }

    res.statusCode = 404;
    res.end(JSON.stringify({ ok: false, error: "Not found" }));
  } catch (err) {
    res.statusCode = 500;
    res.end(JSON.stringify({ ok: false, error: err.message }));
  }
});

server.listen(PORT, BIND, () => {
  console.log(`\n🌉 Claw Bridge Server running`);
  console.log(`   Listening on http://${BIND}:${PORT}`);
  console.log(`   Accessible from VM at http://100.89.150.120 → http://${BIND}:${PORT}`);
  console.log(`\nEndpoints:`);
  console.log(`   GET  /api/claw/status`);
  console.log(`   GET  /api/claw/remote-brief`);
  console.log(`   GET  /api/claw/calendar?date=YYYY-MM-DD`);
  console.log(`   GET  /api/claw/mail?limit=20`);
  console.log(`   POST /api/claw/remote-command  { "command": "brief|status|sync|signals" }`);
  console.log(`\nPress Ctrl+C to stop.\n`);
});
