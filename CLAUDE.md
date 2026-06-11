# ros-mcp — Agent Context

## What this is
ROS 2 CLI wrapper via MCP. Introspect topics, services, nodes, parameters,
and manage node lifecycle — all through MCP tools. 14 tools total.

## Key paths
- `src/ros_mcp/server.py` — 14 MCP tools wrapping ros2 CLI
- `src/ros_mcp/state_machine.py` — process lifecycle state machine
- `web_sota/backend/server.py` — FastAPI backend (port 11050)
- `web_sota/src/` — React frontend (port 11051)

## Commands
- `uv run pytest tests/ -q` — unit tests
- `ruff check src/ web_sota/backend/` — lint
- `uv run python -m ros_mcp` — start MCP stdio
- `.\web_sota\start.ps1` — full web dashboard

## Gotchas
- Requires ROS 2 (ros2) on PATH for most tools
- Launched nodes run as subprocesses for crash isolation
- AI tools fall back to Ollama when ctx.sample is unavailable
- Ports: 11050 backend, 11051 frontend
