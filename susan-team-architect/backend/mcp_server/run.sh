#!/bin/bash
# Launcher for Susan Intelligence MCP Server
# Used by Claude Desktop which doesn't support cwd in config
cd /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend
exec /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/.venv/bin/python3 -m mcp_server.server
