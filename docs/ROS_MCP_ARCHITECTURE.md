# ros-mcp Architecture

## Overview

ros-mcp wraps the ROS 2 CLI (ros2) as MCP tools. Instead of linking against rclpy or rclcpp, it shells out to `ros2 topic list`, `ros2 service call`, etc. This design provides zero-dependency introspection — no ROS 2 Python bindings needed in the MCP server process.

```
MCP client (Claude Desktop, Cursor, etc.)
    |
    | stdio / HTTP
    v
FastMCP server (src/ros_mcp/server.py)
    |
    | subprocess.run / subprocess.Popen
    v
ROS 2 CLI (ros2 topic list, ros2 service call, ...)
    |
    | DDS / RMW
    v
ROS 2 graph (running nodes, topics, services)
```

## Why CLI Wrapping Over rclpy

| Aspect | CLI wrapping | rclpy binding |
|--------|-------------|---------------|
| ROS 2 dependency | `ros2` CLI on PATH | Full ROS 2 Python env |
| Crash isolation | Subprocess isolation | In-process, can deadlock |
| Version compatibility | Works with any ROS 2 distro | Must match rclpy version |
| Parallel calls | Independent subprocesses | GIL-bound, event loop |
| Setup complexity | Minimal (just PATH) | Source setup.bash, env vars |

## Process Lifecycle

Nodes launched via `ros_launch` run as background subprocesses with a state machine:

```
IDLE -> NODE_REGISTERED -> RUNNING -> STOPPING -> STOPPED
                              |                    |
                              v                    v
                           CRASHED              CRASHED
```

The `RosJob` dataclass tracks each process with:
- `job_id` — unique 8-char hex ID
- `label` — human-readable `package/executable`
- `job_type` — "launch", "bag_record", "bag_play"
- `state` — current RosState
- `process` — Popen handle (for stdout/stderr reads)
- `pid` — OS process ID
- `uptime_s` — elapsed runtime

## Tool Categories

### Introspection (read-only, no ROS 2 runtime needed)
- `ros_status` — check if ros2 CLI is available, query live graph
- `topic_list` — list topics with types via `ros2 topic list -t`
- `service_list` — list services via `ros2 service list`
- `node_list` — list nodes via `ros2 node list`

### Data Access
- `topic_echo` — capture a single message from a topic (`--once` mode)
- `topic_info` — show topic metadata (type, count, publishers/subscribers)
- `node_info` — show a node's publishers, subscribers, and services

### Service Interaction
- `service_call` — invoke a service with type and JSON arguments
- `service_type` — get the service type definition

### Parameter Management
- `param_get`, `param_set`, `param_list` — CRUD for node parameters via `ros2 param`

### Node Lifecycle
- `ros_launch` — spawn a node via `ros2 run` as a managed subprocess
- `ros_stop` — terminate a launched process gracefully (SIGTERM -> SIGKILL)
- `ros_log` — read collected stdout/stderr from a launched process
- `list_jobs` — show all tracked processes with state machine info

## Webapp

The Vite + React dashboard at **11051** provides a visual interface for all tools:

- **Dashboard** — ROS availability KPIs, active topics/nodes/services, quick AI workflow
- **Topics** — topic browser with type info, echo viewer, publish form
- **Services** — service list with call form and value input
- **Nodes** — node list with parameter get/set
- **Logging** — ROS log viewer with filter/search
- **LLM** — chat with Ollama for natural-language ROS workflows
- **Settings** — ROS_DOMAIN_ID, DDS config, etc.

## Ports

| Service | Port |
|---------|------|
| Backend (FastAPI + MCP HTTP) | 11050 |
| Frontend (Vite dev) | 11051 |

## Gotchas

- `ros2` CLI must be on PATH for all tools to function
- `topic_echo` uses `--once` mode — captures a single message, then exits
- Launched processes retain stdout/stderr pipes; read with `ros_log`
- Large ROS graphs (>500 topics) will be truncated to 50 entries in `ros_status`
