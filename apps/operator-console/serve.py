#!/usr/bin/env python3
"""Simple HTTP server that reads PORT from environment."""
import http.server
import os

port = int(os.environ.get("PORT", "4173"))
handler = http.server.SimpleHTTPRequestHandler
with http.server.HTTPServer(("", port), handler) as httpd:
    print(f"Serving on port {port}")
    httpd.serve_forever()
