# ros-mcp Setup

## Prerequisites

- Python 3.11+
- `uv` package manager
- ROS 2 (Humble / Iron / Rolling) installed on the system

## Installation

```powershell
git clone https://github.com/sandraschi/ros-mcp.git
cd ros-mcp
uv sync
```

## Simulator Setup

No simulator is required. ros-mcp is a **pure middleware** bridge — it connects to any ROS 2 system via the `ros2` CLI and `rclpy` Python package.

### Install ROS 2

See the [ROS 2 installation guide](https://docs.ros.org/en/humble/Installation.html) for your platform:

```bash
# Ubuntu / Debian (Humble)
sudo apt install ros-humble-ros-base
source /opt/ros/humble/setup.bash
```

```powershell
# Windows (experimental)
# Follow the official ROS 2 Windows install guide
```

### Verify Installation

```bash
ros2 --version
python -c "import rclpy; print('ok')"
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ROS_DOMAIN_ID` | `default` | ROS 2 domain ID for network isolation |
| `ROS_MASTER_URI` | — | Required only for ROS 1 compatibility |

All standard ROS 2 environment variables apply:
- `ROS_DOMAIN_ID` — DDS domain (must match other nodes)
- `ROS_LOCALHOST_ONLY` — set to 1 for single-machine setups
- `CYCLONEDDS_URI` / `FASTRTPS_DEFAULT_PROFILES_FILE` — DDS config

### Ports

| Service | Port |
|---------|------|
| Backend (REST + MCP HTTP) | 11050 |
| Frontend (Vite dev) | 11051 |

Note: ROS 2 DDS discovery uses its own UDP port range (typically 7400-7500, configured via DDS profile).

## Running

### MCP stdio

```powershell
uv run python -m ros_mcp
```

### Web Dashboard

```powershell
.\web_sota\start.ps1
```

Before running, source your ROS 2 environment:

```powershell
# PowerShell (Windows)
C:\opt\ros\humble\x64\setup.ps1

# bash (Linux/WSL2)
source /opt/ros/humble/setup.bash
```

## Testing

```powershell
uv run pytest tests/ -q
ruff check src/ web_sota/backend/
```

## Troubleshooting

### "ROS 2 is not available"

**Cause:** `ros2` CLI not found or `rclpy` not importable.  
**Fix:** Install ROS 2 (see Simulator Setup). Verify: `ros2 --version` and `python -c "import rclpy; print('ok')"`

### No topics/nodes found with ros_status

**Cause:** No ROS 2 system is running, or `ROS_DOMAIN_ID` mismatch.  
**Fix:** Start a ROS 2 node (e.g. `ros2 run turtlesim turtlesim_node` in another terminal). Check `ROS_DOMAIN_ID` matches.

### "ros2 topic list timed out"

**Cause:** DDS discovery is slow or no ROS daemon is running.  
**Fix:** Start a ROS 2 node first. The `ros2` CLI waits for DDS discovery which can take several seconds on an empty system.

### topic_pub / service_call fails

**Cause:** Wrong message type, topic name, or field values.  
**Fix:** Use `topic_list` to verify the topic and type. Check the ROS 2 message definition for field names.

### Launch exits immediately

**Cause:** Package or launch file not found, or ROS 2 environment not sourced.  
**Fix:** Source the ROS 2 setup script first. Verify: `ros2 launch <package> <launch_file>` works manually.

### Bag record fails

**Cause:** ROS 2 bag package not installed.  
**Fix:** Install the rosbag2 package: `sudo apt install ros-humble-ros2bag ros-humble-rosbag2`

### Port 11050/11051 already in use

**Cause:** Another process is bound.  
**Fix:**
```powershell
Get-NetTCPConnection -LocalPort 11050 | ForEach { Stop-Process $_.OwningProcess -Force }
```

### DDS discovery across machines fails

**Cause:** Firewall blocking UDP multicast or mismatched `ROS_DOMAIN_ID`.  
**Fix:** Ensure all machines have the same `ROS_DOMAIN_ID`. Open UDP ports 7400-7500 (or configure DDS for unicast).

### Windows: setup.ps1 not found

**Cause:** ROS 2 installed to a non-standard path on Windows.  
**Fix:** Locate the `setup.ps1` file and source it: `. C:\path\to\ros2\setup.ps1`. Set `ROS_DOMAIN_ID` manually.
