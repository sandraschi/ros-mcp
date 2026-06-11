# ros-mcp — Agent Instructions

## Overview
ros-mcp wraps ROS 2 CLI commands as MCP tools for agentic robotics workflows.
Supports topic/service/node introspection, parameter management, and node lifecycle.

## Available Tools (14 total)

### Status & Discovery
- ros_status — health check with active topic/node/service counts
- topic_list — list topics with types
- topic_echo — capture messages from a topic (--once mode)
- topic_info — detailed topic metadata
- service_list — list all services
- service_call — invoke a service with type and args
- service_type — get the type of a service
- node_list — list all nodes
- node_info — detailed node info (subs/pubs/services)

### Parameters
- param_get — read a parameter from a node
- param_set — write a parameter on a node
- param_list — enumerate all params on a node

### Lifecycle
- ros_launch — launch a ros2 run node (returns job_id)
- ros_stop — terminate a launched process by job_id
- ros_log — read stdout/stderr from a launched process
- list_jobs — list all tracked processes with state
