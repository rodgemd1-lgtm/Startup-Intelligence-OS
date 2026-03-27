#!/usr/bin/env python3
"""Paperclip — local cost dashboard server.

Serves the cost dashboard HTML and proxies Supabase queries so no keys
are exposed in the browser. Reads credentials from ~/.jake-vault/secrets.env.

Usage:
    python3 paperclip-server.py          # starts on port 4174
    python3 paperclip-server.py 8080     # custom port
"""
import http.server
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4174
DASHBOARD_DIR = Path(__file__).parent

# Load vault secrets
VAULT = Path.home() / ".jake-vault" / "secrets.env"
_env = {}
if VAULT.exists():
    for line in VAULT.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            _env[k.strip()] = v.strip()

SUPABASE_URL = _env.get("SUPABASE_URL", "")
SUPABASE_KEY = _env.get("SUPABASE_SERVICE_KEY", "")


class PaperclipHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Serve dashboard at root
        if parsed.path == "/":
            self.path = "/cost-dashboard.html"
            return super().do_GET()

        # API proxy: /api/agent_runs?select=*&order=created_at.desc&limit=100
        if parsed.path.startswith("/api/"):
            table = parsed.path.split("/api/", 1)[1]
            params = parsed.query
            self._proxy_supabase(table, params)
            return

        # Static files
        return super().do_GET()

    def _proxy_supabase(self, table, query_string):
        if not SUPABASE_URL or not SUPABASE_KEY:
            self._json_response({"error": "Supabase not configured in vault"}, 500)
            return

        url = f"{SUPABASE_URL}/rest/v1/{table}"
        if query_string:
            url += f"?{query_string}"

        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        })

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                self._json_response(data)
        except Exception as e:
            self._json_response({"error": str(e)}, 502)

    def _json_response(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Quieter logging
        if "/api/" in (args[0] if args else ""):
            return
        super().log_message(fmt, *args)


if __name__ == "__main__":
    print(f"📎 Paperclip running at http://localhost:{PORT}")
    print(f"   Supabase: {'connected' if SUPABASE_KEY else 'NOT CONFIGURED'}")
    print(f"   Vault: {VAULT}")
    server = http.server.HTTPServer(("127.0.0.1", PORT), PaperclipHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n📎 Paperclip stopped.")
