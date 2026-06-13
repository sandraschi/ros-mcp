# ros-mcp Tool Reference

15 tools: 9 core ROS introspection + 2 launch + 2 bag + 1 job list + 1 AI workflow.

**Note:** All tools require ROS 2 (`ros2` CLI or `rclpy` Python package). The server probes for `ros2` on PATH and `rclpy` importability.

---

## Core ROS Tools (1-9)

### ros_status

**Description:** Health check — probes ROS 2 CLI and rclpy availability. If a ROS system is running, returns active nodes, topics, and services.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| — | — | — | No parameters |

**Output:**
```json
{
  "success": true,
  "message": "ROS 2 is available. 3 nodes, 5 topics, 2 services.",
  "data": {
    "ros_available": true,
    "ros2_cli": true,
    "rclpy": true,
    "ros_version": "humble",
    "ros_domain_id": "default",
    "nodes": ["/turtlesim", "/teleop_turtle"],
    "topics": [{"topic": "/chatter", "type": "std_msgs/msg/String"}],
    "services": [{"service": "/spawn", "type": "turtlesim/srv/Spawn"}]
  }
}
```

**Examples:**
```python
await ros_status()
```

**State machine effect:** None — read-only.

---

### topic_list

**Description:** List all active ROS 2 topics with their types. Runs `ros2 topic list -t`.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| — | — | — | No parameters |

**Output:**
```json
{"success": true, "message": "Found 5 topics.", "data": {"topics": [{"topic": "/chatter", "type": "std_msgs/msg/String"}, ...], "count": 5}}
```

**Examples:**
```python
await topic_list()
```

---

### topic_echo

**Description:** Echo messages from a ROS 2 topic. Runs `ros2 topic echo` with a bounded count and timeout.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| topic | str | Yes | Topic name (e.g. "/chatter") |
| count | int | No | Number of messages to capture (default: 5) |
| timeout | int | No | Timeout in seconds (default: 10) |

**Output:**
```json
{"success": true, "message": "Received 3 messages from /chatter.", "data": {"topic": "/chatter", "messages": ["hello", "world", "..."], "count": 3}}
```

**Examples:**
```python
await topic_echo(topic="/chatter")
await topic_echo(topic="/tf", count=1, timeout=5)
```

---

### topic_pub

**Description:** Publish a single message to a ROS 2 topic. Runs `ros2 topic pub --once`.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| topic | str | Yes | Topic name |
| type | str | Yes | Message type (e.g. "std_msgs/msg/String") |
| values | dict | Yes | Message field values as a dict |
| rate | int | No | Publish rate in Hz (default: 1) |

**Output:**
```json
{"success": true, "message": "Published to /chatter (std_msgs/msg/String).", "data": {"topic": "/chatter", "type": "std_msgs/msg/String", "values": {"data": "hello"}}}
```

**Examples:**
```python
await topic_pub(topic="/chatter", type="std_msgs/msg/String", values={"data": "hello"})
await topic_pub(topic="/cmd_vel", type="geometry_msgs/msg/Twist", values={"linear": {"x": 0.5}})
```

---

### service_list

**Description:** List all active ROS 2 services with their types. Runs `ros2 service list -t`.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| — | — | — | No parameters |

**Output:**
```json
{"success": true, "message": "Found 2 services.", "data": {"services": [{"service": "/spawn", "type": "turtlesim/srv/Spawn"}], "count": 2}}
```

**Examples:**
```python
await service_list()
```

---

### service_call

**Description:** Call a ROS 2 service with the given values. Runs `ros2 service call`.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service | str | Yes | Service name (e.g. "/spawn") |
| type | str | Yes | Service type (e.g. "turtlesim/srv/Spawn") |
| values | dict | Yes | Service request field values |

**Output:**
```json
{"success": true, "message": "Called /spawn (turtlesim/srv/Spawn).", "data": {"service": "/spawn", "type": "turtlesim/srv/Spawn", "request": {"x": 1.0, "y": 1.0}, "response": "..."}}
```

**Examples:**
```python
await service_call(service="/spawn", type="turtlesim/srv/Spawn", values={"x": 1.0, "y": 1.0, "name": "turtle2"})
await service_call(service="/clear", type="std_srvs/srv/Empty", values={})
```

---

### node_list

**Description:** List all active ROS 2 nodes. Runs `ros2 node list`.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| — | — | — | No parameters |

**Output:**
```json
{"success": true, "message": "Found 3 nodes.", "data": {"nodes": ["/turtlesim", "/teleop_turtle"], "count": 3}}
```

**Examples:**
```python
await node_list()
```

---

### param_get

**Description:** Get a ROS 2 parameter value from a node. Runs `ros2 param get`.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| node | str | Yes | Node name (e.g. "/turtlesim") |
| param | str | Yes | Parameter name (e.g. "background_b") |

**Output:**
```json
{"success": true, "message": "Parameter /turtlesim/background_b = 255", "data": {"node": "/turtlesim", "param": "background_b", "value": "255"}}
```

**Examples:**
```python
await param_get(node="/turtlesim", param="background_b")
```

---

### param_set

**Description:** Set a ROS 2 parameter value on a node. Runs `ros2 param set`.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| node | str | Yes | Node name |
| param | str | Yes | Parameter name |
| value | Any | Yes | Parameter value |

**Output:**
```json
{"success": true, "message": "Set /turtlesim/background_b = 255", "data": {"node": "/turtlesim", "param": "background_b", "value": 255}}
```

**Examples:**
```python
await param_set(node="/turtlesim", param="background_b", value=255)
```

---

## Launch Tools (10-11)

### launch

**Description:** Launch a ROS 2 launch file as a background process. Returns a job_id for lifecycle management.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| package | str | Yes | ROS 2 package name |
| launch_file | str | No | Launch file name (e.g. "bringup.launch.py") |
| args | str | No | Additional launch arguments |

**Output:**
```json
{"success": true, "message": "Launch job a1b2c3d4 is running.", "data": {"job_id": "a1b2c3d4", "pid": 12345, "package": "turtlesim", "launch_file": "multisim.launch.py", "state": "running"}}
```

**Examples:**
```python
await launch(package="turtlesim", launch_file="multisim.launch.py")
await launch(package="my_bot", launch_file="bringup.launch.py", args="use_sim_time:=True")
```

**State machine effect:** IDLE → NODE_REGISTERED → RUNNING (or CRASHED)

---

### stop_launch

**Description:** Stop a launched ROS 2 process by job_id.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| job_id | str | Yes | Job ID from launch() |

**Output:**
```json
{"success": true, "message": "Job a1b2c3d4: stopped.", "data": {"job_id": "a1b2c3d4", "state": "stopped", "exit_code": 0, "error": null}}
```

**Examples:**
```python
await stop_launch(job_id="a1b2c3d4")
```

**State machine effect:** RUNNING → STOPPING → STOPPED

---

## Bag Tools (12-13)

### bag_record

**Description:** Record ROS 2 topics to a bag file as a background process with a timeout.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| topic | str | Yes | Topic(s) to record (space-separated for multiple) |
| duration | int | No | Recording duration in seconds (default: 10) |
| output | str | No | Output bag name (auto-generated if empty) |

**Output:**
```json
{"success": true, "message": "Bag record job a1b2c3d4 is running. Recording for 10s.", "data": {"job_id": "a1b2c3d4", "output": "rosbag_abc123", "duration": 10, "state": "running"}}
```

**Examples:**
```python
await bag_record(topic="/chatter", duration=5)
await bag_record(topic="/tf /odom", duration=30, output="my_bag")
```

**State machine effect:** IDLE → NODE_REGISTERED → RUNNING

---

### bag_play

**Description:** Play back a ROS 2 bag file as a background process.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| bag_file | str | Yes | Path to the bag directory |
| rate | float | No | Playback rate multiplier (default: 1.0) |

**Output:**
```json
{"success": true, "message": "Bag play job a1b2c3d4 is running.", "data": {"job_id": "a1b2c3d4", "bag_file": "/path/to/bag", "rate": 1.0, "state": "running"}}
```

**Examples:**
```python
await bag_play(bag_file="/path/to/bag_dir")
await bag_play(bag_file="my_bag", rate=2.0)
```

**State machine effect:** IDLE → NODE_REGISTERED → RUNNING

---

## Job Management (14)

### list_jobs

**Description:** List all tracked ROS jobs (launch, bag_record, bag_play) with state machine info.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| — | — | — | No parameters |

**Output:**
```json
{"success": true, "data": {"active": [{"job_id": "a1b2c3d4", "label": "turtlesim/multisim.launch.py", "state": "running"}], "completed": [...], "total": 3}}
```

**Examples:**
```python
await list_jobs()
```

**State machine effect:** None — read-only.

---

## AI Workflow Tool (15)

### agentic_ros_workflow

**Description:** Uses the host LLM to plan and execute a multi-step ROS 2 workflow. Falls back to Ollama.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| goal | str | Yes | Natural language goal |
| ctx | Context | Yes | FastMCP context (injected automatically) |

**Output:**
```json
{"success": true, "message": "Workflow completed.", "plan_and_result": "1. List topics... 2. Echo /chatter...", "sampling_used": true}
```

**Examples:**
```python
await agentic_ros_workflow(goal="List all topics, then echo /chatter")
await agentic_ros_workflow(goal="Start turtlesim, spawn a turtle, and set background to blue")
```

**State machine effect:** Depends on the tools the LLM calls.
