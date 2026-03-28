"""Vercel serverless function — proxy Supabase agent_runs queries.

Reads SUPABASE_URL and SUPABASE_SERVICE_KEY from Vercel env vars.
"""
import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            self._json({"error": "Supabase not configured"}, 500)
            return

        # Forward query params to Supabase REST API
        parsed = urllib.parse.urlparse(self.path)
        query = parsed.query

        url = f"{SUPABASE_URL}/rest/v1/agent_runs"
        if query:
            url += f"?{query}"

        req = urllib.request.Request(url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        })

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                self._json(data)
        except Exception as e:
            self._json({"error": str(e)}, 502)

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
