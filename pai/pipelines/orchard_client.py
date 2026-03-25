#!/usr/bin/env python3
"""Orchard MCP Client

Lightweight client for Orchard's Streamable HTTP MCP server.
Provides direct access to 48 Apple ecosystem tools.

Usage:
    from orchard_client import OrchardClient
    client = OrchardClient()
    events = client.call("calendar_info", {"type": "events", "range": "today"})
"""

import json
import urllib.request
from typing import Any, Dict, List, Optional

ORCHARD_URL = "http://localhost:8086/mcp"


class OrchardClient:
    """MCP client for Orchard (Apple ecosystem bridge)."""

    def __init__(self, url: str = ORCHARD_URL):
        self.url = url
        self.session_id = None  # type: Optional[str]
        self._request_id = 0
        self._initialize()

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _post(self, payload: dict, headers: Optional[dict] = None) -> dict:
        """Send a JSON-RPC request to Orchard."""
        hdrs = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            hdrs["Mcp-Session-Id"] = self.session_id
        if headers:
            hdrs.update(headers)

        req = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers=hdrs,
        )
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            # Capture session ID from response headers
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid
            body = resp.read().decode()
            if body:
                return json.loads(body)
            return {}
        except Exception as e:
            return {"error": str(e)}

    def _initialize(self):
        """Initialize MCP session with Orchard."""
        result = self._post({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "pai-pipeline", "version": "3.0"},
            },
            "id": self._next_id(),
        })
        if "error" not in result:
            # Send initialized notification
            self._post({
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            })

    def call(self, tool: str, arguments: Optional[dict] = None) -> Any:
        """Call an Orchard MCP tool and return the result content."""
        result = self._post({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": arguments or {},
            },
            "id": self._next_id(),
        })

        if "error" in result and isinstance(result["error"], str):
            return {"error": result["error"]}

        if "error" in result and isinstance(result["error"], dict):
            return {"error": result["error"].get("message", str(result["error"]))}

        # Extract content from MCP response
        content = result.get("result", {}).get("content", [])
        if content and isinstance(content, list):
            # Return text content joined
            texts = [c.get("text", "") for c in content if c.get("type") == "text"]
            if len(texts) == 1:
                # Try to parse as JSON
                try:
                    return json.loads(texts[0])
                except (json.JSONDecodeError, TypeError):
                    return texts[0]
            return "\n".join(texts) if texts else content

        return result.get("result", result)

    def calendar_today(self) -> list[dict]:
        """Get today's calendar events."""
        result = self.call("calendar_info", {
            "type": "events",
            "range": "today",
        })
        if isinstance(result, dict) and "error" in result:
            return []
        if isinstance(result, list):
            return result
        if isinstance(result, str):
            # Parse text output into structured data
            events = []
            for line in result.strip().split("\n"):
                if line.strip():
                    events.append({"raw": line.strip()})
            return events
        return []

    def calendar_upcoming(self, hours: int = 4) -> list[dict]:
        """Get upcoming events in the next N hours."""
        from datetime import datetime, timedelta
        now = datetime.now()
        end = now + timedelta(hours=hours)
        result = self.call("calendar_info", {
            "type": "events",
            "start_date": now.strftime("%Y-%m-%d %H:%M"),
            "end_date": end.strftime("%Y-%m-%d %H:%M"),
        })
        if isinstance(result, list):
            return result
        return []

    def mail_unread(self, account: Optional[str] = None) -> list:
        """Get unread emails."""
        params = {"operation": "search", "keyword": "", "unread_only": True}
        if account:
            params["account"] = account
        result = self.call("mail_read", params)
        if isinstance(result, list):
            return result
        return []

    def mail_accounts(self) -> list[dict]:
        """Get configured mail accounts."""
        return self.call("mail_accounts", {})

    def weather(self, location: str = "current") -> dict:
        """Get current weather."""
        return self.call("weather_get", {"location": location})

    def is_available(self) -> bool:
        """Check if Orchard is running and responsive."""
        try:
            result = self._post({
                "jsonrpc": "2.0",
                "method": "ping",
                "id": self._next_id(),
            })
            return "error" not in result or "Method not found" in str(result.get("error", ""))
        except Exception:
            return False


if __name__ == "__main__":
    import sys
    client = OrchardClient()

    if len(sys.argv) < 2:
        print("Usage: python orchard_client.py <tool> [json_args]")
        print("Example: python orchard_client.py calendar_info '{\"type\": \"events\", \"range\": \"today\"}'")
        sys.exit(0)

    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    result = client.call(tool, args)
    print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
