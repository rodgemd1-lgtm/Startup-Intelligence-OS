#!/usr/bin/env python3
"""SuperMemory.ai MCP Server — thin wrapper over v4 API for Claude Code."""

from __future__ import annotations

import json
import os
import sys
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_BASE = "https://api.supermemory.ai"
API_KEY = os.environ.get("SUPERMEMORY_API_KEY", "")


def _api(method: str, path: str, body: dict | None = None) -> dict:
    req = Request(
        f"{API_BASE}{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )
    if body:
        req.data = json.dumps(body).encode()
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        return {"error": e.code, "message": e.read().decode()}


def handle_tool(name: str, arguments: dict) -> str:
    if name == "supermemory_search":
        result = _api("POST", "/v4/search", {
            "q": arguments["query"],
            "containerTag": arguments.get("container", "shared"),
            "limit": arguments.get("limit", 10),
        })
        return json.dumps(result, indent=2)

    elif name == "supermemory_add":
        result = _api("POST", "/v4/memories", {
            "memories": [{"content": arguments["content"]}],
            "containerTag": arguments.get("container", "shared"),
        })
        return json.dumps(result, indent=2)

    elif name == "supermemory_list":
        result = _api("POST", "/v4/memories/list", {
            "containerTags": [arguments.get("container", "shared")],
        })
        return json.dumps(result, indent=2)

    return json.dumps({"error": f"Unknown tool: {name}"})


TOOLS = [
    {
        "name": "supermemory_search",
        "description": "Search Jake's SuperMemory across agent containers. Returns ranked results by semantic similarity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "container": {
                    "type": "string",
                    "description": "Container tag: jake, kira, aria, scout, steve, compass, shared, jake-system",
                    "default": "shared",
                },
                "limit": {"type": "integer", "description": "Max results", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "supermemory_add",
        "description": "Add a memory to SuperMemory. Use for storing important context, decisions, and learnings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Memory content to store"},
                "container": {
                    "type": "string",
                    "description": "Container tag: jake, kira, aria, scout, steve, compass, shared",
                    "default": "shared",
                },
            },
            "required": ["content"],
        },
    },
    {
        "name": "supermemory_list",
        "description": "List recent memories in a SuperMemory container.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "container": {
                    "type": "string",
                    "description": "Container tag to list",
                    "default": "shared",
                },
            },
        },
    },
]


def main():
    """MCP stdio transport — read JSON-RPC from stdin, write to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = msg.get("method", "")
        msg_id = msg.get("id")

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": "supermemory",
                        "version": "1.0.0",
                    },
                },
            }
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOLS},
            }
        elif method == "tools/call":
            params = msg.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result_text = handle_tool(tool_name, arguments)
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": result_text}],
                },
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {},
            }

        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
