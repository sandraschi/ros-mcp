# ros-mcp — System Prompt

## Purpose

ros-mcp provides programmatic access to ROS 2 through the Model Context Protocol (MCP).
It enables AI agents to load assets, manage simulation lifecycles, control robots, read state,
export data, and analyze results — all through standardized MCP tools.

The server manages ROS 2 simulations as isolated background subprocesses, providing
crash-safe lifecycle management. Each simulation runs independently with its own process,
job directory, and state files.

## Architecture

### Process Model

The server runs as a FastMCP Python process. Each simulation launch creates a managed child
subprocess running ROS 2. Communication between server and simulation uses multiple mechanisms:

- **Control**: Server writes control.json, runner reads on next step
- **State**: Runner writes state.json, server reads on demand
- **Signals**: Server touches stop.signal, runner detects and exits gracefully
- **Metadata**: Runner writes metadata.json on startup with actuator names and model info
- **Frames**: Runner saves PNG frames for export_frame (if render enabled)
- **Logs**: Runner writes runner.log, server reads for analysis and debugging

### Job Isolation

Each simulation runs in its own process space. A crash in the runner never affects the MCP
server or other concurrent simulations. Process output is written to log files (never piped)
to prevent pipe buffer deadlocks that freeze long-running simulations.

### Job Directory Structure

```
jobs/
  <job_id>/
    metadata.json     # Job metadata (model path, actuator names, start time)
    state.json        # Current simulation state (written periodically by runner)
    control.json      # Pending control values (written by server, read by runner)
    stop.signal       # Stop signal file (server touches, runner polls)
    runner.log        # Subprocess stdout/stderr (file, not pipe)
    frames/           # Render frames (only if render=True)
      frame_000000.png
      frame_000001.png
    error.txt         # Error information if runner crashed
    completed.txt     # Marker file for clean completion
```

## Complete Tool Reference (15 tools)

All tools return `{success: bool, ...}`. Always check success before proceeding.

### Simulation Tools

#### ros_status()

H**ealth check** for ROS 2 connectivity. Probes ros2 CLI and rclpy import. Returns active nodes, topics, services, and ROS domain ID. **Usage**: Always call first to verify ROS 2 is running and accessible. **Output**: {success, data: {ros_available, nodes, topics, services}}

#### topic_list()

L**ist ROS 2 topics** with their message types. Runs ros2 topic list -t. **Output**: {success, data: {topics: [{topic, type}], count}}. **Requires**: ROS 2 CLI on PATH.

#### topic_echo()

E**cho ROS 2 topic** messages. Runs ros2 topic echo with count and timeout limits. **Input**: topic (str), count (int, default 5), timeout (int, default 10s). **Output**: {success, data: {topic, messages, count}}. **Safety**: Bounded by count and timeout to prevent hanging.

#### topic_pub()

P**ublish a message** to a ROS 2 topic. Runs ros2 topic pub --once. **Input**: topic (str), type (str, e.g. std_msgs/msg/String), values (dict). **Output**: {success, data: {topic, type, values}}. **Timeout**: 10s publish window.

#### service_list()

L**ist ROS 2 services** with types. Runs ros2 service list -t. **Output**: {success, data: {services: [{service, type}], count}}.

#### service_call()

C**all a ROS 2 service**. Runs ros2 service call with type and args. **Input**: service (str), type (str), values (dict). **Output**: {success, data: {service, type, request, response}}. **Timeout**: 15s.

#### node_list()

L**ist ROS 2 nodes**. Runs ros2 node list. **Output**: {success, data: {nodes: [str], count}}.

#### param_get()

G**et a ROS 2 parameter** from a node. **Input**: node (str), param (str). **Output**: {success, data: {node, param, value}}.

#### param_set()

S**et a ROS 2 parameter** on a node. **Input**: node (str), param (str), value (any). **Output**: {success, data: {node, param, value}}.

#### launch()

L**aunch a ROS 2 launch file** as a background process. Returns job_id for lifecycle management. **Input**: package (str), launch_file (str, optional), args (str, optional). **Output**: {success, data: {job_id, pid, package, state}}. **Lifecycle**: Registered -> Running -> Stopped/Crashed.

#### stop_launch()

S**top a launched ROS 2 process** by job_id. **Input**: job_id (str). **Output**: {success, data: {job_id, state, exit_code}}.

#### bag_record()

R**ecord ROS 2 topics** to a bag file as background process. **Input**: topic (str), duration (int, default 10s), output (str, optional). **Output**: {success, data: {job_id, output, duration}}.

#### bag_play()

P**lay back a ROS 2 bag** file as background process. **Input**: bag_file (str), rate (float, default 1.0). **Output**: {success, data: {job_id, bag_file, rate}}.

#### list_jobs()

L**ist active and completed** simulation jobs with state information. Active = RUNNING/STARTING/STOPPING. Completed = STOPPED/CRASHED/ERROR. **Output**: {success, active: [...], completed: [...], total}. Also scans job directories for orphaned metadata.

### AI Workflow Tools

#### agentic_ros_workflow()

A**utonomous ROS 2 workflow** via host LLM. Plans and executes ROS tool calls. **Input**: goal (str). **Output**: {success, plan_and_result, sampling_used}.

## Error Handling Strategy

### Subprocess Crashes
- Runner crashes are isolated — the MCP server never goes down with a sim
- Crashes are detected via process.poll() on next get_state or list_jobs call
- Error details are captured to error.txt and runner.log for post-mortem analysis
- Job transitions to CRASHED state with exit code recorded

### Process Termination
- stop.signal file is written for clean shutdown (runner polls this)
- SIGTERM sent first (5s grace period for state save)
- SIGKILL sent if process does not respond within timeout

### Pipe Buffer Deadlock Prevention
- NEVER use stdout/stderr=PIPE for long-running subprocesses
- Always redirect to a log file opened before Popen
- This is a critical rule for all fleet robotics MCP servers

### File System Race Conditions
- state.json written atomically (write to temp, rename)
- control.json reads are safe (missing file = no control applied)
- stop.signal existence check is atomic

### Network Failures
- load operations: httpx has 60-120s timeout depending on file size
- discover_model: 30s timeout per candidate URL
- All network calls wrapped in try/except with descriptive error messages

## AI Tool Fallback Chain

All AI workflow tools follow a two-stage fallback:

1. **ctx.sample()** — MCP sampling protocol (Claude Desktop, Cursor, etc.)
   - Preferred path, uses host LLM for reasoning
   - Returns sampling_used=True on success
2. **Ollama** — http://127.0.0.1:11434/api/generate
   - Fallback when ctx.sample is unavailable
   - Model: llama3.2:3b (or configured model)
   - Returns sampling_used=False, model='ollama' on success
3. **Error** — Both failed
   - Returns error message with hints (install Ollama, check connectivity)

## Configuration

### Ports
- Backend: 11050 (FastAPI + MCP HTTP `/mcp`)
- Frontend: 11051 (Vite React dashboard)

### Model Type: N/A (CLI wrappers)

### Environment Variables
See repo README for available environment variables.

## Limitations

1. **Subprocess isolation**: Each sim runs as a full subprocess (~50-500 MB for complex models).
   Multiple concurrent sims consume proportional memory and CPU.
2. **File-based IPC**: State is file-polled, not streamed. Minimum effective polling interval
   is ~33ms (30 FPS). State is typically 1-2 sim steps behind real time.
3. **No runtime physics changes**: Cannot adjust gravity, timestep, or solver parameters
   at runtime. Modify source files and reload.
4. **N/A (CLI wrappers) only**: Other model formats may require conversion.
5. **GPU requirements**: Offscreen rendering needs EGL/OSMesa (headless) or a display driver.
   First launch may be slow due to extension pull and cache warmup.
6. **Single-threaded physics**: Each sim runs in a single thread. No parallel stepping
   within one process.
7. **In-memory job state**: Active jobs are tracked in memory. Server restart loses job tracking
   (though log files persist on disk).


## Appendix: Detailed Error Recovery Procedures

### Immediate Crash Recovery
When a simulation crashes immediately after start_sim:
1. Check runner.log in the job directory for error details. Common causes include missing model
   dependencies, invalid XML/SDF syntax, or version incompatibility between the model format
   and the simulator version. For GPU-accelerated simulators, check for graphics driver issues.
2. If model file references external meshes, verify all paths are accessible. Relative paths in
   MJCF/URDF files resolve from the model file's directory. Absolute paths must match the
   filesystem on the simulator host.
3. For ROS 2-based simulators, verify the ROS_DOMAIN_ID matches across all nodes and
   that the ROS 2 daemon is running (ros2 daemon start).

### Resource Cleanup
To clean up after crashed or orphaned simulations:
1. Check list_jobs() for crashed jobs and call stop_sim() on each to ensure process cleanup.
2. Use the system monitor (Task Manager on Windows, ps on Linux) to find and kill orphaned
   simulator processes. Simulator process names vary by backend.
3. Job directories can be safely deleted once the associated process is confirmed dead.
   The server recreates directories as needed for new jobs.

### Network and Port Troubleshooting
If the server fails to bind its MCP or HTTP port:
1. Check for zombie processes: Get-NetTCPConnection -LocalPort <port> (Windows) or
   lsof -i :<port> (Linux). Kill occupying processes.
2. The start.ps1 script includes automatic port clearing. Run it from an elevated prompt.
3. Firewall rules may block MCP transport ports. Ensure inbound rules allow the port range.
4. For WSL-based setups (Gazebo on Windows), ensure WSL2 networking is properly configured.

### AI Tool Configuration
For the best experience with AI-powered tools:
1. Install Ollama (ollama.ai) and start the service: ollama serve
2. Pull a compatible model: ollama pull llama3.2:3b (3B parameters, fast) or
   ollama pull llama3.2:1b (lighter, faster).
3. The server connects to Ollama at http://127.0.0.1:11434 by default.
4. For MCP sampling (ctx.sample), use Claude Desktop or Cursor as the MCP client.
   These clients support the MCP sampling protocol that lets the server ask the host LLM
   for reasoning without additional setup.

### Depot Management
Model/scene/world depots persist across server restarts:
1. Depot files are stored in JSON format in the .depot/ subdirectory.
2. To clear the depot and start fresh, delete the registry.json file. Models will need
   to be reloaded before starting new simulations.
3. For repository-based models (Unitree, LimX), the discovery tools scan local git repos
   and do not require separate loading steps.
4. Depot entries can accumulate over time. Periodically review and remove unused entries
   by deleting the corresponding model files and registry entries.

### Concurrent Simulation Best Practices
When running multiple simulations simultaneously:
1. Each simulation runs as a separate OS process. Monitor total memory and CPU usage.
2. MuJoCo simulations use approximately 100-500 MB RAM and one CPU core each.
3. Isaac Sim simulations use approximately 2-8 GB RAM and 1-4 CPU cores each.
4. Assign unique job_id references to avoid cross-talk between concurrent experiments.
5. Use list_jobs() to monitor the fleet and stop_sim() to release resources when done.

### Log File Management
Log files accumulate in the jobs/ directory:
1. Each start_sim call creates a new job directory with log files.
2. Log files can grow large for long-running simulations (especially with verbose output).
3. Periodically archive or delete old job directories. The server only needs the
   directory structure for active jobs — completed/crashed job logs are optional.
4. Use analyze_sim_logs() for LLM-assisted log review before cleanup.

## Appendix: Detailed Error Recovery Procedures

### Immediate Crash Recovery
When a simulation crashes immediately after start_sim:
1. Check runner.log in the job directory for error details. Common causes include missing model
   dependencies, invalid XML/SDF syntax, or version incompatibility between the model format
   and the simulator version. For GPU-accelerated simulators, check for graphics driver issues.
2. If model file references external meshes, verify all paths are accessible. Relative paths in
   MJCF/URDF files resolve from the model file's directory. Absolute paths must match the
   filesystem on the simulator host.
3. For ROS 2-based simulators, verify the ROS_DOMAIN_ID matches across all nodes and
   that the ROS 2 daemon is running (ros2 daemon start).

### Resource Cleanup
To clean up after crashed or orphaned simulations:
1. Check list_jobs() for crashed jobs and call stop_sim() on each to ensure process cleanup.
2. Use the system monitor (Task Manager on Windows, ps on Linux) to find and kill orphaned
   simulator processes. Simulator process names vary by backend.
3. Job directories can be safely deleted once the associated process is confirmed dead.
   The server recreates directories as needed for new jobs.

### Network and Port Troubleshooting
If the server fails to bind its MCP or HTTP port:
1. Check for zombie processes: Get-NetTCPConnection -LocalPort <port> (Windows) or
   lsof -i :<port> (Linux). Kill occupying processes.
2. The start.ps1 script includes automatic port clearing. Run it from an elevated prompt.
3. Firewall rules may block MCP transport ports. Ensure inbound rules allow the port range.
4. For WSL-based setups (Gazebo on Windows), ensure WSL2 networking is properly configured.

### AI Tool Configuration
For the best experience with AI-powered tools:
1. Install Ollama (ollama.ai) and start the service: ollama serve
2. Pull a compatible model: ollama pull llama3.2:3b (3B parameters, fast) or
   ollama pull llama3.2:1b (lighter, faster).
3. The server connects to Ollama at http://127.0.0.1:11434 by default.
4. For MCP sampling (ctx.sample), use Claude Desktop or Cursor as the MCP client.
   These clients support the MCP sampling protocol that lets the server ask the host LLM
   for reasoning without additional setup.

### Depot Management
Model/scene/world depots persist across server restarts:
1. Depot files are stored in JSON format in the .depot/ subdirectory.
2. To clear the depot and start fresh, delete the registry.json file. Models will need
   to be reloaded before starting new simulations.
3. For repository-based models (Unitree, LimX), the discovery tools scan local git repos
   and do not require separate loading steps.
4. Depot entries can accumulate over time. Periodically review and remove unused entries
   by deleting the corresponding model files and registry entries.

### Concurrent Simulation Best Practices
When running multiple simulations simultaneously:
1. Each simulation runs as a separate OS process. Monitor total memory and CPU usage.
2. MuJoCo simulations use approximately 100-500 MB RAM and one CPU core each.
3. Isaac Sim simulations use approximately 2-8 GB RAM and 1-4 CPU cores each.
4. Assign unique job_id references to avoid cross-talk between concurrent experiments.
5. Use list_jobs() to monitor the fleet and stop_sim() to release resources when done.

### Log File Management
Log files accumulate in the jobs/ directory:
1. Each start_sim call creates a new job directory with log files.
2. Log files can grow large for long-running simulations (especially with verbose output).
3. Periodically archive or delete old job directories. The server only needs the
   directory structure for active jobs — completed/crashed job logs are optional.
4. Use analyze_sim_logs() for LLM-assisted log review before cleanup.

## Appendix: Detailed Error Recovery Procedures

### Immediate Crash Recovery
When a simulation crashes immediately after start_sim:
1. Check runner.log in the job directory for error details. Common causes include missing model
   dependencies, invalid XML/SDF syntax, or version incompatibility between the model format
   and the simulator version. For GPU-accelerated simulators, check for graphics driver issues.
2. If model file references external meshes, verify all paths are accessible. Relative paths in
   MJCF/URDF files resolve from the model file's directory. Absolute paths must match the
   filesystem on the simulator host.
3. For ROS 2-based simulators, verify the ROS_DOMAIN_ID matches across all nodes and
   that the ROS 2 daemon is running (ros2 daemon start).

### Resource Cleanup
To clean up after crashed or orphaned simulations:
1. Check list_jobs() for crashed jobs and call stop_sim() on each to ensure process cleanup.
2. Use the system monitor (Task Manager on Windows, ps on Linux) to find and kill orphaned
   simulator processes. Simulator process names vary by backend.
3. Job directories can be safely deleted once the associated process is confirmed dead.
   The server recreates directories as needed for new jobs.

### Network and Port Troubleshooting
If the server fails to bind its MCP or HTTP port:
1. Check for zombie processes: Get-NetTCPConnection -LocalPort <port> (Windows) or
   lsof -i :<port> (Linux). Kill occupying processes.
2. The start.ps1 script includes automatic port clearing. Run it from an elevated prompt.
3. Firewall rules may block MCP transport ports. Ensure inbound rules allow the port range.
4. For WSL-based setups (Gazebo on Windows), ensure WSL2 networking is properly configured.

### AI Tool Configuration
For the best experience with AI-powered tools:
1. Install Ollama (ollama.ai) and start the service: ollama serve
2. Pull a compatible model: ollama pull llama3.2:3b (3B parameters, fast) or
   ollama pull llama3.2:1b (lighter, faster).
3. The server connects to Ollama at http://127.0.0.1:11434 by default.
4. For MCP sampling (ctx.sample), use Claude Desktop or Cursor as the MCP client.
   These clients support the MCP sampling protocol that lets the server ask the host LLM
   for reasoning without additional setup.

### Depot Management
Model/scene/world depots persist across server restarts:
1. Depot files are stored in JSON format in the .depot/ subdirectory.
2. To clear the depot and start fresh, delete the registry.json file. Models will need
   to be reloaded before starting new simulations.
3. For repository-based models (Unitree, LimX), the discovery tools scan local git repos
   and do not require separate loading steps.
4. Depot entries can accumulate over time. Periodically review and remove unused entries
   by deleting the corresponding model files and registry entries.

### Concurrent Simulation Best Practices
When running multiple simulations simultaneously:
1. Each simulation runs as a separate OS process. Monitor total memory and CPU usage.
2. MuJoCo simulations use approximately 100-500 MB RAM and one CPU core each.
3. Isaac Sim simulations use approximately 2-8 GB RAM and 1-4 CPU cores each.
4. Assign unique job_id references to avoid cross-talk between concurrent experiments.
5. Use list_jobs() to monitor the fleet and stop_sim() to release resources when done.

### Log File Management
Log files accumulate in the jobs/ directory:
1. Each start_sim call creates a new job directory with log files.
2. Log files can grow large for long-running simulations (especially with verbose output).
3. Periodically archive or delete old job directories. The server only needs the
   directory structure for active jobs — completed/crashed job logs are optional.
4. Use analyze_sim_logs() for LLM-assisted log review before cleanup.

## Appendix: Detailed Error Recovery Procedures

### Immediate Crash Recovery
When a simulation crashes immediately after start_sim:
1. Check runner.log in the job directory for error details. Common causes include missing model
   dependencies, invalid XML/SDF syntax, or version incompatibility between the model format
   and the simulator version. For GPU-accelerated simulators, check for graphics driver issues.
2. If model file references external meshes, verify all paths are accessible. Relative paths in
   MJCF/URDF files resolve from the model file's directory. Absolute paths must match the
   filesystem on the simulator host.
3. For ROS 2-based simulators, verify the ROS_DOMAIN_ID matches across all nodes and
   that the ROS 2 daemon is running (ros2 daemon start).

### Resource Cleanup
To clean up after crashed or orphaned simulations:
1. Check list_jobs() for crashed jobs and call stop_sim() on each to ensure process cleanup.
2. Use the system monitor (Task Manager on Windows, ps on Linux) to find and kill orphaned
   simulator processes. Simulator process names vary by backend.
3. Job directories can be safely deleted once the associated process is confirmed dead.
   The server recreates directories as needed for new jobs.

### Network and Port Troubleshooting
If the server fails to bind its MCP or HTTP port:
1. Check for zombie processes: Get-NetTCPConnection -LocalPort <port> (Windows) or
   lsof -i :<port> (Linux). Kill occupying processes.
2. The start.ps1 script includes automatic port clearing. Run it from an elevated prompt.
3. Firewall rules may block MCP transport ports. Ensure inbound rules allow the port range.
4. For WSL-based setups (Gazebo on Windows), ensure WSL2 networking is properly configured.

### AI Tool Configuration
For the best experience with AI-powered tools:
1. Install Ollama (ollama.ai) and start the service: ollama serve
2. Pull a compatible model: ollama pull llama3.2:3b (3B parameters, fast) or
   ollama pull llama3.2:1b (lighter, faster).
3. The server connects to Ollama at http://127.0.0.1:11434 by default.
4. For MCP sampling (ctx.sample), use Claude Desktop or Cursor as the MCP client.
   These clients support the MCP sampling protocol that lets the server ask the host LLM
   for reasoning without additional setup.

### Depot Management
Model/scene/world depots persist across server restarts:
1. Depot files are stored in JSON format in the .depot/ subdirectory.
2. To clear the depot and start fresh, delete the registry.json file. Models will need
   to be reloaded before starting new simulations.
3. For repository-based models (Unitree, LimX), the discovery tools scan local git repos
   and do not require separate loading steps.
4. Depot entries can accumulate over time. Periodically review and remove unused entries
   by deleting the corresponding model files and registry entries.

### Concurrent Simulation Best Practices
When running multiple simulations simultaneously:
1. Each simulation runs as a separate OS process. Monitor total memory and CPU usage.
2. MuJoCo simulations use approximately 100-500 MB RAM and one CPU core each.
3. Isaac Sim simulations use approximately 2-8 GB RAM and 1-4 CPU cores each.
4. Assign unique job_id references to avoid cross-talk between concurrent experiments.
5. Use list_jobs() to monitor the fleet and stop_sim() to release resources when done.

### Log File Management
Log files accumulate in the jobs/ directory:
1. Each start_sim call creates a new job directory with log files.
2. Log files can grow large for long-running simulations (especially with verbose output).
3. Periodically archive or delete old job directories. The server only needs the
   directory structure for active jobs — completed/crashed job logs are optional.
4. Use analyze_sim_logs() for LLM-assisted log review before cleanup.

## Appendix: Detailed Error Recovery Procedures

### Immediate Crash Recovery
When a simulation crashes immediately after start_sim:
1. Check runner.log in the job directory for error details. Common causes include missing model
   dependencies, invalid XML/SDF syntax, or version incompatibility between the model format
   and the simulator version. For GPU-accelerated simulators, check for graphics driver issues.
2. If model file references external meshes, verify all paths are accessible. Relative paths in
   MJCF/URDF files resolve from the model file's directory. Absolute paths must match the
   filesystem on the simulator host.
3. For ROS 2-based simulators, verify the ROS_DOMAIN_ID matches across all nodes and
   that the ROS 2 daemon is running (ros2 daemon start).

### Resource Cleanup
To clean up after crashed or orphaned simulations:
1. Check list_jobs() for crashed jobs and call stop_sim() on each to ensure process cleanup.
2. Use the system monitor (Task Manager on Windows, ps on Linux) to find and kill orphaned
   simulator processes. Simulator process names vary by backend.
3. Job directories can be safely deleted once the associated process is confirmed dead.
   The server recreates directories as needed for new jobs.

### Network and Port Troubleshooting
If the server fails to bind its MCP or HTTP port:
1. Check for zombie processes: Get-NetTCPConnection -LocalPort <port> (Windows) or
   lsof -i :<port> (Linux). Kill occupying processes.
2. The start.ps1 script includes automatic port clearing. Run it from an elevated prompt.
3. Firewall rules may block MCP transport ports. Ensure inbound rules allow the port range.
4. For WSL-based setups (Gazebo on Windows), ensure WSL2 networking is properly configured.

### AI Tool Configuration
For the best experience with AI-powered tools:
1. Install Ollama (ollama.ai) and start the service: ollama serve
2. Pull a compatible model: ollama pull llama3.2:3b (3B parameters, fast) or
   ollama pull llama3.2:1b (lighter, faster).
3. The server connects to Ollama at http://127.0.0.1:11434 by default.
4. For MCP sampling (ctx.sample), use Claude Desktop or Cursor as the MCP client.
   These clients support the MCP sampling protocol that lets the server ask the host LLM
   for reasoning without additional setup.

### Depot Management
Model/scene/world depots persist across server restarts:
1. Depot files are stored in JSON format in the .depot/ subdirectory.
2. To clear the depot and start fresh, delete the registry.json file. Models will need
   to be reloaded before starting new simulations.
3. For repository-based models (Unitree, LimX), the discovery tools scan local git repos
   and do not require separate loading steps.
4. Depot entries can accumulate over time. Periodically review and remove unused entries
   by deleting the corresponding model files and registry entries.

### Concurrent Simulation Best Practices
When running multiple simulations simultaneously:
1. Each simulation runs as a separate OS process. Monitor total memory and CPU usage.
2. MuJoCo simulations use approximately 100-500 MB RAM and one CPU core each.
3. Isaac Sim simulations use approximately 2-8 GB RAM and 1-4 CPU cores each.
4. Assign unique job_id references to avoid cross-talk between concurrent experiments.
5. Use list_jobs() to monitor the fleet and stop_sim() to release resources when done.

### Log File Management
Log files accumulate in the jobs/ directory:
1. Each start_sim call creates a new job directory with log files.
2. Log files can grow large for long-running simulations (especially with verbose output).
3. Periodically archive or delete old job directories. The server only needs the
   directory structure for active jobs — completed/crashed job logs are optional.
4. Use analyze_sim_logs() for LLM-assisted log review before cleanup.

## Appendix: Detailed Error Recovery Procedures

### Immediate Crash Recovery
When a simulation crashes immediately after start_sim:
1. Check runner.log in the job directory for error details. Common causes include missing model
   dependencies, invalid XML/SDF syntax, or version incompatibility between the model format
   and the simulator version. For GPU-accelerated simulators, check for graphics driver issues.
2. If model file references external meshes, verify all paths are accessible. Relative paths in
   MJCF/URDF files resolve from the model file's directory. Absolute paths must match the
   filesystem on the simulator host.
3. For ROS 2-based simulators, verify the ROS_DOMAIN_ID matches across all nodes and
   that the ROS 2 daemon is running (ros2 daemon start).

### Resource Cleanup
To clean up after crashed or orphaned simulations:
1. Check list_jobs() for crashed jobs and call stop_sim() on each to ensure process cleanup.
2. Use the system monitor (Task Manager on Windows, ps on Linux) to find and kill orphaned
   simulator processes. Simulator process names vary by backend.
3. Job directories can be safely deleted once the associated process is confirmed dead.
   The server recreates directories as needed for new jobs.

### Network and Port Troubleshooting
If the server fails to bind its MCP or HTTP port:
1. Check for zombie processes: Get-NetTCPConnection -LocalPort <port> (Windows) or
   lsof -i :<port> (Linux). Kill occupying processes.
2. The start.ps1 script includes automatic port clearing. Run it from an elevated prompt.
3. Firewall rules may block MCP transport ports. Ensure inbound rules allow the port range.
4. For WSL-based setups (Gazebo on Windows), ensure WSL2 networking is properly configured.

### AI Tool Configuration
For the best experience with AI-powered tools:
1. Install Ollama (ollama.ai) and start the service: ollama serve
2. Pull a compatible model: ollama pull llama3.2:3b (3B parameters, fast) or
   ollama pull llama3.2:1b (lighter, faster).
3. The server connects to Ollama at http://127.0.0.1:11434 by default.
4. For MCP sampling (ctx.sample), use Claude Desktop or Cursor as the MCP client.
   These clients support the MCP sampling protocol that lets the server ask the host LLM
   for reasoning without additional setup.

### Depot Management
Model/scene/world depots persist across server restarts:
1. Depot files are stored in JSON format in the .depot/ subdirectory.
2. To clear the depot and start fresh, delete the registry.json file. Models will need
   to be reloaded before starting new simulations.
3. For repository-based models (Unitree, LimX), the discovery tools scan local git repos
   and do not require separate loading steps.
4. Depot entries can accumulate over time. Periodically review and remove unused entries
   by deleting the corresponding model files and registry entries.

### Concurrent Simulation Best Practices
When running multiple simulations simultaneously:
1. Each simulation runs as a separate OS process. Monitor total memory and CPU usage.
2. MuJoCo simulations use approximately 100-500 MB RAM and one CPU core each.
3. Isaac Sim simulations use approximately 2-8 GB RAM and 1-4 CPU cores each.
4. Assign unique job_id references to avoid cross-talk between concurrent experiments.
5. Use list_jobs() to monitor the fleet and stop_sim() to release resources when done.

### Log File Management
Log files accumulate in the jobs/ directory:
1. Each start_sim call creates a new job directory with log files.
2. Log files can grow large for long-running simulations (especially with verbose output).
3. Periodically archive or delete old job directories. The server only needs the
   directory structure for active jobs — completed/crashed job logs are optional.
4. Use analyze_sim_logs() for LLM-assisted log review before cleanup.
