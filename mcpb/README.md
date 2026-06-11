# ros-mcp

**ROS 2 CLI wrapper via MCP** — introspect topics, services, nodes, parameters, and manage node lifecycle from any MCP client (Claude Desktop, Cursor).

**Ports:** Backend 11050 / Frontend 11051

---

## Quick Start

```powershell
git clone https://github.com/sandraschi/ros-mcp
cd ros-mcp
uv sync
uv run python -m ros_mcp
```

Or use the start script:

```powershell
.\web_sota\start.ps1          # backend + webapp
```

---

## Tools

| Tool | Description |
|------|-------------|
| `ros_status` | Health check: ROS 2 availability, topic/node/service counts |
| `topic_list` | List ROS 2 topics with type information |
| `topic_echo` | Capture messages from a topic (--once mode) |
| `topic_info` | Detailed topic metadata (type, count, publishers) |
| `service_list` | List all ROS 2 services |
| `service_call` | Call a ROS 2 service with type and arguments |
| `service_type` | Get the type of a ROS 2 service |
| `node_list` | List all ROS 2 nodes |
| `node_info` | Detailed node info (subscribers, publishers, services) |
| `param_get` | Read a parameter from a node |
| `param_set` | Set a parameter on a node |
| `param_list` | List all parameters on a node |
| `ros_launch` | Launch a ROS 2 node via ros2 run (returns job_id) |
| `ros_stop` | Stop a launched ROS process by job_id |
| `ros_log` | Read stdout/stderr from a launched process |
| `list_jobs` | List all tracked ROS processes with lifecycle state |

---

## Architecture

```
MCP client -> FastMCP (11050) -> ros2 CLI subprocesses
                                  -> topic/service/node introspection
                                  -> parameter CRUD
                                  -> node lifecycle management
```

Each `ros2` invocation runs as an isolated subprocess. See `docs/ROS_MCP_ARCHITECTURE.md`.

---

## Webapp

Vite + React dashboard at **11051** with 7 pages: Dashboard, Topics, Services, Nodes, Logging, LLM, Settings.

---

## docs

- `docs/ROS_MCP_ARCHITECTURE.md` — CLI wrapper design, subprocess model, lifecycle management

---

## Requirements

- Python 3.11+
- ROS 2 (ros2 CLI on PATH) for full functionality
- Ollama (optional) for AI workflow features
