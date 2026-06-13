# ros-mcp

**ROS 2[^1] bridge via MCP. Topics, services, parameters, bags, launch files — control any ROS-compatible robot.**

[![CI](https://github.com/sandraschi/ros-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/ros-mcp/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.2+-blue)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

ros-mcp exposes the full ROS 2 middleware surface as MCP tools. List and echo topics, publish messages, call services, get and set parameters, launch and stop nodes, record and play bags — all through a unified MCP interface. The server connects to any running ROS 2 system (Humble, Iron, Rolling) via `rclpy` and supports both Python and native ROS 2 CLI fallbacks.

Built as the central nervous system of the fleet simulation pipeline: ros-mcp provides the communication layer that connects simulators (gazebo-mcp, mujoco-mcp, isaac-mcp) with robot control (unitree-mcp, limx-robotics-mcp), data logging, and agentic orchestration.

## Table of Contents

- [Quick Start](#quick-start)
- [Tools](#tools)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Ports](#ports)
- [Footnotes](#footnotes)

## Quick Start

```powershell
# 1. Clone and enter
git clone https://github.com/sandraschi/ros-mcp
cd ros-mcp

# 2. Run the MCP server
uv run python -m ros_mcp

# 3. Or launch the full web dashboard
.\start.ps1
```

## Tools

| # | Tool | Description |
|---|------|-------------|
| 1 | `ros_status` | Health check — ROS 2 distribution, active nodes, topic count |
| 2 | `topic_list` | List all active ROS 2 topics with types |
| 3 | `topic_echo` | Subscribe and echo messages from a topic (bounded count or duration) |
| 4 | `topic_pub` | Publish a message to a topic |
| 5 | `service_list` | List all available ROS 2 services |
| 6 | `service_call` | Call a ROS 2 service with arguments |
| 7 | `node_list` | List all active ROS 2 nodes |
| 8 | `param_get` | Get a parameter value from a node |
| 9 | `param_set` | Set a parameter value on a node |
| 10 | `launch` | Launch a ROS 2 launch file or standalone node |
| 11 | `stop_launch` | Stop a previously launched process |
| 12 | `bag_record` | Start recording a ROS 2 bag (topics filterable) |
| 13 | `bag_play` | Play back a ROS 2 bag |
| 14 | `agentic_ros_workflow` | Multi-step ROS 2 workflow via LLM sampling |

[Full tool reference →](docs/TOOLS.md)

## Architecture

ros-mcp wraps `rclpy` in a long-lived node that acts as the bridge between MCP and ROS 2. For each tool call, the server creates transient publishers/subscribers, calls services via `rclpy.wait_for_service`, and manages bag recording via `ros2 bag` CLI subprocesses. Launch processes are tracked in a process table keyed by launch ID.

```
MCP Client  ──►  ros-mcp (FastMCP 3.2)
                        │
              ┌─────────┴──────────────┐
              │  rclpy Bridge Node      │
              │  (transient pubs/subs)  │
              └─────────┬──────────────┘
                        │
                   ROS 2 Graph
              ┌────┬────┬────┬────┐
              │    │    │    │    │
           gazebo  sim  robot  bag
```

[Architecture deep-dive →](docs/ROS_MCP_ARCHITECTURE.md)

## Documentation

| Doc | Contents |
|-----|----------|
| `docs/TOOLS.md` | Full reference for all 14 tools with inputs, outputs, examples |
| `docs/SETUP.md` | Installation, ROS 2 distribution setup, workspace config, troubleshooting |
| `docs/ROS_MCP_ARCHITECTURE.md` | Bridge design, process lifecycle, topic QoS config |

## Ports

| Port | Service |
|------|---------|
| 11050 | FastAPI backend + MCP HTTP |
| 11051 | Vite React frontend |

## Footnotes

[^1]: **ROS 2** — Robot Operating System 2. Open-source middleware for robotics: pub/sub communication, services, parameters, and tooling. [ros.org](https://ros.org)
