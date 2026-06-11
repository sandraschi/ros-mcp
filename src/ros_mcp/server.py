import json
import os
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastmcp import Context, FastMCP

from ros_mcp.state_machine import (
    RosJob,
    RosState,
    transition_crashed,
    transition_registered,
    transition_running,
    transition_stopped,
    transition_stopping,
)

mcp = FastMCP("ros-mcp")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
JOBS_DIR = REPO_ROOT / "jobs"

JOBS_DIR.mkdir(parents=True, exist_ok=True)

_jobs: dict[str, Any] = {}
_job_states: dict[str, RosJob] = {}


def _ros2_available() -> bool:
    return shutil.which("ros2") is not None


def _rclpy_available() -> bool:
    try:
        import rclpy  # noqa: F401
        return True
    except ImportError:
        return False


def _ros_domain_id() -> str:
    return os.environ.get("ROS_DOMAIN_ID", "default")


def _ros_version() -> str | None:
    try:
        result = subprocess.run(["ros2", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    try:
        import rclpy
        return getattr(rclpy, "__version__", None) or "unknown"
    except ImportError:
        pass
    return None


def _run_ros2(args: list[str], timeout: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ros2"] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _parse_topic_list(output: str) -> list[dict]:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    topics = []
    for line in lines:
        parts = line.split()
        if parts:
            topic = parts[0].rstrip(":")
            topic_type = parts[1] if len(parts) > 1 else None
            topics.append({"topic": topic, "type": topic_type})
    return topics


def _parse_service_list(output: str) -> list[dict]:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    services = []
    for line in lines:
        parts = line.split()
        if parts:
            svc = parts[0].rstrip(":")
            svc_type = parts[1] if len(parts) > 1 else None
            services.append({"service": svc, "type": svc_type})
    return services


def _parse_node_list(output: str) -> list[str]:
    return [n.strip("/") for n in output.splitlines() if n.strip() and n.strip().startswith("/")]


def _extract_json(text: str) -> dict | None:
    for m in re.finditer(r'\{[^{}]*\}', text):
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            continue
    return None


def _extract_json_array(text: str) -> list:
    for m in re.finditer(r'\[.*?\]', text, re.DOTALL):
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            continue
    return []


def _check_ros(error_prefix: str = "ROS 2") -> dict | None:
    if not _ros2_available() and not _rclpy_available():
        return {
            "success": False,
            "message": f"{error_prefix} is not available. Install ROS 2 (ros2 CLI) or the rclpy Python package.",
            "ros2_cli": _ros2_available(),
            "rclpy": _rclpy_available(),
        }
    return None


# ---------------------------------------------------------------------------
# Core ROS tools (9)
# ---------------------------------------------------------------------------


@mcp.tool()
def ros_status() -> dict:
    """Check ROS 2 availability and return system status.

    Probes for ros2 CLI and rclpy. If a ROS system is running, returns
    active nodes, topics, and services.

    ## Return Format
    {"success": bool, "message": str, "data": {"ros_available": bool, "ros_version": str, ...}}

    ## Examples
    ros_status()
    """
    check = _check_ros()
    if check:
        return check

    nodes = []
    topics = []
    services_list = []

    try:
        result = _run_ros2(["node", "list"], timeout=5)
        if result.returncode == 0:
            nodes = _parse_node_list(result.stdout)
    except Exception:
        pass

    try:
        result = _run_ros2(["topic", "list", "-t"], timeout=5)
        if result.returncode == 0:
            topics = _parse_topic_list(result.stdout)
    except Exception:
        pass

    try:
        result = _run_ros2(["service", "list", "-t"], timeout=5)
        if result.returncode == 0:
            services_list = _parse_service_list(result.stdout)
    except Exception:
        pass

    return {
        "success": True,
        "message": f"ROS 2 is available ({_ros_version() or 'unknown'}). {len(nodes)} nodes, {len(topics)} topics, {len(services_list)} services.",
        "data": {
            "ros_available": True,
            "ros2_cli": _ros2_available(),
            "rclpy": _rclpy_available(),
            "ros_version": _ros_version(),
            "ros_domain_id": _ros_domain_id(),
            "nodes": nodes,
            "node_count": len(nodes),
            "topics": topics,
            "topic_count": len(topics),
            "services": services_list,
            "service_count": len(services_list),
        },
    }


@mcp.tool()
def topic_list() -> dict:
    """List all active ROS 2 topics with their types.

    Runs ``ros2 topic list -t`` and parses the output.

    ## Return Format
    {"success": bool, "message": str, "data": {"topics": [{"topic": str, "type": str}]}}

    ## Examples
    topic_list()
    """
    check = _check_ros()
    if check:
        return check

    try:
        result = _run_ros2(["topic", "list", "-t"])
        if result.returncode != 0:
            return {"success": False, "message": f"ros2 topic list failed: {result.stderr.strip()}"}
        topics = _parse_topic_list(result.stdout)
        return {
            "success": True,
            "message": f"Found {len(topics)} topics.",
            "data": {"topics": topics, "count": len(topics)},
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "ros2 topic list timed out."}
    except Exception as e:
        return {"success": False, "message": f"Failed to list topics: {e}"}


@mcp.tool()
def topic_echo(topic: str, count: int = 5, timeout: int = 10) -> dict:
    """Echo messages from a ROS 2 topic.

    Runs ``ros2 topic echo`` with a limited count and timeout.

    ## Return Format
    {"success": bool, "message": str, "data": {"topic": str, "messages": list, "count": int}}

    ## Examples
    topic_echo(topic="/chatter")
    topic_echo(topic="/tf", count=1, timeout=5)
    """
    check = _check_ros()
    if check:
        return check

    try:
        result = _run_ros2(
            ["topic", "echo", topic, "--count", str(count), "--field", "data"],
            timeout=timeout,
        )
        if result.returncode != 0:
            return {"success": False, "message": f"ros2 topic echo failed: {result.stderr.strip()}"}
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return {
            "success": True,
            "message": f"Received {len(lines)} messages from {topic}.",
            "data": {"topic": topic, "messages": lines, "count": len(lines)},
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": f"topic_echo timed out after {timeout}s on {topic}."}
    except Exception as e:
        return {"success": False, "message": f"Failed to echo topic {topic}: {e}"}


@mcp.tool()
def topic_pub(topic: str, type: str, values: dict, rate: int = 1) -> dict:
    """Publish a message to a ROS 2 topic.

    Runs ``ros2 topic pub`` with the given message type and field values.
    Publishes a single message at the specified rate.

    ## Return Format
    {"success": bool, "message": str, "data": {"topic": str, "type": str, "values": dict}}

    ## Examples
    topic_pub(topic="/chatter", type="std_msgs/msg/String", values={"data": "hello"})
    topic_pub(topic="/cmd_vel", type="geometry_msgs/msg/Twist", values={"linear": {"x": 0.5}})
    """
    check = _check_ros()
    if check:
        return check

    values_json = json.dumps(values)
    try:
        proc = subprocess.Popen(
            [
                "ros2", "topic", "pub",
                "--once",
                topic, type,
                values_json,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            stdout, stderr = proc.communicate(timeout=10)
            if proc.returncode != 0:
                return {"success": False, "message": f"ros2 topic pub failed: {stderr.decode().strip()}"}
            return {
                "success": True,
                "message": f"Published to {topic} ({type}).",
                "data": {"topic": topic, "type": type, "values": values},
            }
        except subprocess.TimeoutExpired:
            proc.kill()
            return {"success": False, "message": f"topic_pub timed out on {topic}."}
    except Exception as e:
        return {"success": False, "message": f"Failed to publish to {topic}: {e}"}


@mcp.tool()
def service_list() -> dict:
    """List all active ROS 2 services with their types.

    Runs ``ros2 service list -t`` and parses the output.

    ## Return Format
    {"success": bool, "message": str, "data": {"services": [{"service": str, "type": str}]}}

    ## Examples
    service_list()
    """
    check = _check_ros()
    if check:
        return check

    try:
        result = _run_ros2(["service", "list", "-t"])
        if result.returncode != 0:
            return {"success": False, "message": f"ros2 service list failed: {result.stderr.strip()}"}
        services_list = _parse_service_list(result.stdout)
        return {
            "success": True,
            "message": f"Found {len(services_list)} services.",
            "data": {"services": services_list, "count": len(services_list)},
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "ros2 service list timed out."}
    except Exception as e:
        return {"success": False, "message": f"Failed to list services: {e}"}


@mcp.tool()
def service_call(service: str, type: str, values: dict) -> dict:
    """Call a ROS 2 service with the given values.

    Runs ``ros2 service call`` and returns the response.

    ## Return Format
    {"success": bool, "message": str, "data": {"service": str, "request": dict, "response": str}}

    ## Examples
    service_call(service="/spawn", type="turtlesim/srv/Spawn", values={"x": 1.0, "y": 1.0, "name": "turtle2"})
    service_call(service="/clear", type="std_srvs/srv/Empty", values={})
    """
    check = _check_ros()
    if check:
        return check

    values_json = json.dumps(values)
    try:
        result = _run_ros2(["service", "call", service, type, values_json], timeout=15)
        if result.returncode != 0:
            return {"success": False, "message": f"ros2 service call failed: {result.stderr.strip()}"}
        return {
            "success": True,
            "message": f"Called {service} ({type}).",
            "data": {
                "service": service,
                "type": type,
                "request": values,
                "response": result.stdout.strip(),
            },
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": f"service_call timed out on {service}."}
    except Exception as e:
        return {"success": False, "message": f"Failed to call service {service}: {e}"}


@mcp.tool()
def node_list() -> dict:
    """List all active ROS 2 nodes.

    Runs ``ros2 node list``.

    ## Return Format
    {"success": bool, "message": str, "data": {"nodes": [str], "count": int}}

    ## Examples
    node_list()
    """
    check = _check_ros()
    if check:
        return check

    try:
        result = _run_ros2(["node", "list"])
        if result.returncode != 0:
            return {"success": False, "message": f"ros2 node list failed: {result.stderr.strip()}"}
        nodes = _parse_node_list(result.stdout)
        return {
            "success": True,
            "message": f"Found {len(nodes)} nodes.",
            "data": {"nodes": nodes, "count": len(nodes)},
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "ros2 node list timed out."}
    except Exception as e:
        return {"success": False, "message": f"Failed to list nodes: {e}"}


@mcp.tool()
def param_get(node: str, param: str) -> dict:
    """Get a ROS 2 parameter value from a node.

    Runs ``ros2 param get``.

    ## Return Format
    {"success": bool, "message": str, "data": {"node": str, "param": str, "value": str}}

    ## Examples
    param_get(node="/turtlesim", param="background_b")
    """
    check = _check_ros()
    if check:
        return check

    try:
        result = _run_ros2(["param", "get", node, param])
        if result.returncode != 0:
            return {"success": False, "message": f"ros2 param get failed: {result.stderr.strip()}"}
        value = result.stdout.strip()
        return {
            "success": True,
            "message": f"Parameter {node}/{param} = {value}",
            "data": {"node": node, "param": param, "value": value},
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": f"param_get timed out on {node}/{param}."}
    except Exception as e:
        return {"success": False, "message": f"Failed to get param {node}/{param}: {e}"}


@mcp.tool()
def param_set(node: str, param: str, value: Any) -> dict:
    """Set a ROS 2 parameter value on a node.

    Runs ``ros2 param set``.

    ## Return Format
    {"success": bool, "message": str, "data": {"node": str, "param": str, "value": Any}}

    ## Examples
    param_set(node="/turtlesim", param="background_b", value=255)
    """
    check = _check_ros()
    if check:
        return check

    try:
        result = _run_ros2(["param", "set", node, param, str(value)])
        if result.returncode != 0:
            return {"success": False, "message": f"ros2 param set failed: {result.stderr.strip()}"}
        return {
            "success": True,
            "message": f"Set {node}/{param} = {value}",
            "data": {"node": node, "param": param, "value": value},
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": f"param_set timed out on {node}/{param}."}
    except Exception as e:
        return {"success": False, "message": f"Failed to set param {node}/{param}: {e}"}


# ---------------------------------------------------------------------------
# Launch tools (2)
# ---------------------------------------------------------------------------


@mcp.tool()
def launch(package: str, launch_file: str = "", args: str = "") -> dict:
    """Launch a ROS 2 launch file as a background process.

    Runs ``ros2 launch`` and returns a job_id for lifecycle management.
    Use stop_launch(job_id) to stop it.

    ## Return Format
    {"success": bool, "message": str, "data": {"job_id": str, "pid": int, "package": str, "launch_file": str}}

    ## Examples
    launch(package="turtlesim", launch_file="multisim.launch.py")
    launch(package="my_bot", launch_file="bringup.launch.py", args="use_sim_time:=True")
    """
    check = _check_ros()
    if check:
        return check

    cmd = ["ros2", "launch", package]
    if launch_file:
        cmd.append(launch_file)
    if args:
        cmd.extend(args.split())

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        job_id = uuid.uuid4().hex[:8]
        label = f"{package}/{launch_file or 'default'}"
        job = RosJob(job_id=job_id, label=label, job_type="launch")
        transition_registered(job, proc, label, "launch")
        _job_states[job_id] = job
        _jobs[job_id] = {
            "process": proc,
            "package": package,
            "launch_file": launch_file,
            "started_at": time.time(),
            "job_type": "launch",
        }

        for _ in range(50):
            if proc.poll() is not None:
                transition_crashed(job, f"Launch exited immediately (code {proc.returncode})", proc.returncode)
                break
            time.sleep(0.1)
        else:
            transition_running(job)

        return {
            "success": True,
            "message": f"Launch job {job_id} is {job.state.value}.",
            "data": {
                "job_id": job_id,
                "pid": proc.pid,
                "package": package,
                "launch_file": launch_file or "default",
                "state": job.state.value,
            },
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to launch {package}: {e}"}


@mcp.tool()
def stop_launch(job_id: str) -> dict:
    """Stop a launched ROS 2 process by job_id.

    Terminates the background process started by launch().

    ## Return Format
    {"success": bool, "message": str, "data": {"job_id": str, "state": str, "exit_code": int | None}}

    ## Examples
    stop_launch(job_id="abc12345")
    """
    job = _job_states.get(job_id)
    if not job:
        return {"success": False, "message": f"Job '{job_id}' not found."}

    proc_info = _jobs.get(job_id, {})
    proc = proc_info.get("process")

    if job.state == RosState.RUNNING:
        transition_stopping(job)

    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
            transition_stopped(job, proc.returncode)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
            transition_crashed(job, "Killed after stop timeout", proc.returncode)
    else:
        exit_code = proc.poll() if proc else None
        transition_stopped(job, exit_code)

    return {
        "success": True,
        "message": f"Job {job_id}: {job.state.value}.",
        "data": {
            "job_id": job_id,
            "state": job.state.value,
            "exit_code": job.exit_code,
            "error": job.error_message,
        },
    }


# ---------------------------------------------------------------------------
# Bag tools (2)
# ---------------------------------------------------------------------------


@mcp.tool()
def bag_record(topic: str, duration: int = 10, output: str = "") -> dict:
    """Record ROS 2 topics to a bag file.

    Runs ``ros2 bag record`` as a background process with a timeout.
    The bag is stored in the jobs directory.

    ## Return Format
    {"success": bool, "message": str, "data": {"job_id": str, "output": str, "duration": int}}

    ## Examples
    bag_record(topic="/chatter", duration=5)
    bag_record(topic="/tf /odom", duration=30, output="my_bag")
    """
    check = _check_ros()
    if check:
        return check

    output_name = output or f"rosbag_{uuid.uuid4().hex[:6]}"
    bag_dir = JOBS_DIR / output_name

    cmd = ["ros2", "bag", "record"]
    if topic:
        cmd.extend(topic.split())
    cmd.extend(["-o", str(bag_dir)])

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        job_id = uuid.uuid4().hex[:8]
        job = RosJob(job_id=job_id, label=output_name, job_type="bag_record")
        transition_registered(job, proc, output_name, "bag_record")
        _job_states[job_id] = job
        _jobs[job_id] = {
            "process": proc,
            "output": output_name,
            "started_at": time.time(),
            "duration": duration,
            "job_type": "bag_record",
        }

        for _ in range(50):
            if proc.poll() is not None:
                transition_crashed(job, f"Bag record exited immediately (code {proc.returncode})", proc.returncode)
                break
            time.sleep(0.1)
        else:
            transition_running(job)

        return {
            "success": True,
            "message": f"Bag record job {job_id} is {job.state.value}. Recording for {duration}s.",
            "data": {
                "job_id": job_id,
                "output": output_name,
                "duration": duration,
                "state": job.state.value,
            },
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to start bag record: {e}"}


@mcp.tool()
def bag_play(bag_file: str, rate: float = 1.0) -> dict:
    """Play back a ROS 2 bag file.

    Runs ``ros2 bag play`` as a background process.

    ## Return Format
    {"success": bool, "message": str, "data": {"job_id": str, "bag_file": str, "rate": float}}

    ## Examples
    bag_play(bag_file="/path/to/bag_dir")
    bag_play(bag_file="my_bag", rate=2.0)
    """
    check = _check_ros()
    if check:
        return check

    cmd = ["ros2", "bag", "play", bag_file]
    if rate != 1.0:
        cmd.extend(["--rate", str(rate)])

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        job_id = uuid.uuid4().hex[:8]
        label = Path(bag_file).name
        job = RosJob(job_id=job_id, label=label, job_type="bag_play")
        transition_registered(job, proc, label, "bag_play")
        _job_states[job_id] = job
        _jobs[job_id] = {
            "process": proc,
            "bag_file": bag_file,
            "rate": rate,
            "started_at": time.time(),
            "job_type": "bag_play",
        }

        for _ in range(50):
            if proc.poll() is not None:
                transition_crashed(job, f"Bag play exited immediately (code {proc.returncode})", proc.returncode)
                break
            time.sleep(0.1)
        else:
            transition_running(job)

        return {
            "success": True,
            "message": f"Bag play job {job_id} is {job.state.value}.",
            "data": {
                "job_id": job_id,
                "bag_file": bag_file,
                "rate": rate,
                "state": job.state.value,
            },
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to play bag: {e}"}


@mcp.tool()
def list_jobs() -> dict:
    """List all tracked ROS jobs (launch, bag_record, bag_play).

    ## Return Format
    {"success": bool, "data": {"active": list, "completed": list, "total": int}}

    ## Examples
    list_jobs()
    """
    active = []
    completed = []

    for jid, job in list(_job_states.items()):
        d = job.info()
        if job.state in (RosState.RUNNING, RosState.NODE_REGISTERED, RosState.STOPPING):
            active.append(d)
        else:
            completed.append(d)

    return {
        "success": True,
        "data": {
            "active": active,
            "completed": completed,
            "total": len(active) + len(completed),
        },
    }


# ---------------------------------------------------------------------------
# AI workflow tool (1)
# ---------------------------------------------------------------------------


@mcp.tool()
async def agentic_ros_workflow(goal: str, ctx: Context) -> dict:
    """Execute an autonomous multi-step ROS 2 workflow using the host LLM.

    The LLM plans a sequence of tool calls (topic_list, topic_pub, service_call,
    param_set, launch, etc.) to achieve the described goal. Falls back to
    Ollama when ctx.sample is unavailable.

    ## Return Format
    {"success": bool, "message": str, "plan_and_result": str, "sampling_used": bool}

    ## Examples
    agentic_ros_workflow(goal="List all topics, then echo /chatter")
    agentic_ros_workflow(goal="Start turtlesim, spawn a turtle, and set background to blue")
    """
    tools_desc = """
Available tools (invoke with JSON):
- ros_status() — health check, ROS version, active nodes/topics/services
- topic_list() — list all active topics with types
- topic_echo(topic, count, timeout) — echo messages from a topic
- topic_pub(topic, type, values, rate) — publish a message
- service_list() — list all active services
- service_call(service, type, values) — call a service
- node_list() — list all active nodes
- param_get(node, param) — get a parameter
- param_set(node, param, value) — set a parameter
- launch(package, launch_file, args) — launch a ROS 2 launch file
- stop_launch(job_id) — stop a launched process
- bag_record(topic, duration, output) — record topics to bag
- bag_play(bag_file, rate) — play back a bag file
- list_jobs() — list tracked background jobs
"""
    prompt = f"""You are a robotics engineer working with ROS 2. Your goal: {goal}

{tools_desc}

Plan and execute the steps. Show your reasoning before each tool call.
After completion, summarize what happened and any observations."""

    try:
        result = await ctx.sample(prompt)
        text = getattr(result, "text", None) or str(result)
        return {
            "success": True,
            "message": "Workflow completed.",
            "plan_and_result": text.strip(),
            "sampling_used": True,
        }
    except Exception as e:
        try:
            resp = httpx.post(
                "http://127.0.0.1:11434/api/generate",
                json={"model": "llama3.2:3b", "prompt": prompt, "stream": False},
                timeout=120,
            )
            return {
                "success": True,
                "message": "Workflow completed (Ollama).",
                "plan_and_result": resp.json().get("response", ""),
                "sampling_used": False,
                "model": "ollama",
            }
        except Exception as ollama_e:
            return {
                "success": False,
                "message": f"Both sampling and Ollama fallback failed: {e}; {ollama_e}",
            }


def main():
    mcp.run()
