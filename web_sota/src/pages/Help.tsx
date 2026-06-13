import { useState } from "react";

const TABS = ["Overview", "Tools", "Setup", "Troubleshooting"];

const TOOLS = [
  { name: "ros_status", desc: "Health check: ROS 2 availability, topic/node/service counts", group: "Status & Discovery" },
  { name: "topic_list", desc: "List ROS 2 topics with type information", group: "Status & Discovery" },
  { name: "topic_echo", desc: "Capture a single message from a topic (--once mode)", group: "Status & Discovery" },
  { name: "topic_info", desc: "Detailed topic metadata (type, count, publishers)", group: "Status & Discovery" },
  { name: "service_list", desc: "List all ROS 2 services", group: "Status & Discovery" },
  { name: "service_call", desc: "Call a ROS 2 service with type and arguments", group: "Status & Discovery" },
  { name: "service_type", desc: "Get the type definition of a ROS 2 service", group: "Status & Discovery" },
  { name: "node_list", desc: "List all ROS 2 nodes", group: "Status & Discovery" },
  { name: "node_info", desc: "Detailed node info (subscribers, publishers, services)", group: "Status & Discovery" },
  { name: "param_get", desc: "Read a parameter from a node", group: "Parameters" },
  { name: "param_set", desc: "Set a parameter on a node", group: "Parameters" },
  { name: "param_list", desc: "List all parameters on a node", group: "Parameters" },
  { name: "ros_launch", desc: "Launch a ROS 2 node via ros2 run (returns job_id)", group: "Lifecycle" },
  { name: "ros_stop", desc: "Stop a launched ROS process by job_id", group: "Lifecycle" },
  { name: "ros_log", desc: "Read stdout/stderr from a launched process", group: "Lifecycle" },
  { name: "list_jobs", desc: "List all tracked ROS processes with lifecycle state", group: "Lifecycle" },
];

const TROUBLES = [
  { symptom: "ros_status: ros2 CLI not found", cause: "ROS 2 not installed or not on PATH", fix: "Install ROS 2 (Humble/Jazzy) and source setup.bash. Ensure ros2 is on PATH." },
  { symptom: "topic_echo returns nothing", cause: "No messages being published on the topic", fix: "Verify a publisher is active with topic_list. Topics with 0 publishers cannot be echoed." },
  { symptom: "service_call fails: service not found", cause: "Service name does not exist in the ROS graph", fix: "Use service_list to verify the exact service name. Names are case-sensitive." },
  { symptom: "ros_launch: node not found", cause: "Package not installed in the ROS 2 workspace", fix: "Verify the package with ros2 pkg list. Source the correct workspace setup.bash." },
  { symptom: "Web dashboard not loading", cause: "Backend or Vite not running", fix: "Ensure backend (11050) and Vite (11051) are both running. Check browser console." },
  { symptom: "Port already in use", cause: "Previous instance still listening", fix: "Get-NetTCPConnection -LocalPort 11050,11051 | Stop-Process -Id {OwningProcess} -Force" },
  { symptom: "param_set: cannot set parameter", cause: "Parameter is read-only or node does not allow runtime changes", fix: "Check if the parameter is declared as read_only in the node. Some params require node restart." },
  { symptom: "Node launched via ros_launch crashes", cause: "Missing dependencies or incompatible ROS 2 version", fix: "Check ros_log(job_id) for stderr. Ensure the package is built for your ROS 2 distro." },
  { symptom: "Large ROS graph not fully visible", cause: "Topic truncation for performance", fix: "ros_status truncates at 50 topics. Use topic_list directly for the full list." },
];

export default function Help() {
  const [tab, setTab] = useState(0);
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Help</h1>
      <div className="flex gap-2 mb-6 flex-wrap">
        {TABS.map((t, i) => (
          <button
            key={t}
            onClick={() => setTab(i)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${tab === i ? "bg-blue-600 text-white" : "border border-slate-300 text-slate-600 hover:bg-slate-100"}`}
          >
            {t}
          </button>
        ))}
      </div>
      {tab === 0 && <Overview />}
      {tab === 1 && <Tools />}
      {tab === 2 && <Setup />}
      {tab === 3 && <Troubleshooting />}
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-5 mb-4">
      <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-4">{title}</h2>
      {children}
    </div>
  );
}

function Overview() {
  return (
    <div className="space-y-4">
      <Card title="What It Is">
        <p className="text-sm text-slate-600 mb-2">
          <strong>ros-mcp</strong> wraps the ROS 2 CLI (<code className="text-xs bg-slate-100 px-1 rounded">ros2</code>) as MCP tools.
          Introspect topics, services, nodes, parameters, and manage node lifecycle — all from any MCP client.
        </p>
        <p className="text-sm text-slate-600 mb-2">
          <strong>ros-mcp does not run ROS.</strong> It connects to an existing ROS 2 system on the network.
          The ROS 2 graph (nodes, topics, services) must already be running — ros-mcp shells out to the
          <code className="text-xs bg-slate-100 px-1 rounded"> ros2</code> CLI for all operations.
        </p>
      </Card>

      <Card title="Where ROS 2 Runs">
        <p className="text-sm text-slate-600 mb-3">ros-mcp works with any ROS 2 setup reachable via DDS. Common configurations:</p>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-slate-500">
              <th className="pb-2 pr-4 font-medium">Setup</th>
              <th className="pb-2 pr-4 font-medium">Where ROS runs</th>
              <th className="pb-2 font-medium">Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-slate-100">
              <td className="py-2 pr-4 text-xs font-mono">Real robot</td>
              <td className="py-2 pr-4 text-xs text-slate-600">On-board computer</td>
              <td className="py-2 text-xs text-slate-500">DDS discovery over LAN. Set ROS_DOMAIN_ID to match the robot.</td>
            </tr>
            <tr className="border-b border-slate-100">
              <td className="py-2 pr-4 text-xs font-mono">Docker</td>
              <td className="py-2 pr-4 text-xs text-slate-600">Container(s) on same host</td>
              <td className="py-2 text-xs text-slate-500">Use host networking (--network=host) or DDS multicast config.</td>
            </tr>
            <tr className="border-b border-slate-100">
              <td className="py-2 pr-4 text-xs font-mono">WSL2</td>
              <td className="py-2 pr-4 text-xs text-slate-600">WSL2 Ubuntu distro</td>
              <td className="py-2 text-xs text-slate-500">Install ROS 2 in WSL2. DDS discovery works via WSL2 virtual NIC.</td>
            </tr>
            <tr className="border-b border-slate-100">
              <td className="py-2 pr-4 text-xs font-mono">Native Linux</td>
              <td className="py-2 pr-4 text-xs text-slate-600">Same machine</td>
              <td className="py-2 text-xs text-slate-500">Simplest setup. Source setup.bash, run ros2 nodes, start ros-mcp.</td>
            </tr>
            <tr>
              <td className="py-2 pr-4 text-xs font-mono">Simulation</td>
              <td className="py-2 pr-4 text-xs text-slate-600">Gazebo + ROS 2 bridge</td>
              <td className="py-2 text-xs text-slate-500">Used with gazebo-mcp or unitree_ros2 for simulated robots.</td>
            </tr>
          </tbody>
        </table>
      </Card>

      <Card title="Architecture">
        <pre className="bg-slate-900 text-green-300 text-xs p-4 rounded font-mono leading-relaxed whitespace-pre-wrap overflow-x-auto mb-3">
{`MCP Client (Claude Desktop, Cursor)
    │  stdio / HTTP
    ▼
FastMCP server (port 11050)
    │  subprocess.run / subprocess.Popen
    ▼
ROS 2 CLI (ros2 topic list, service call, ...)
    │
    │  DDS / RMW
    ▼
ROS 2 Graph (running nodes, topics, services)
  ┌────┴────┐
  │  Real   │  Docker  │  WSL2   │  Sim
  │  Robot  │          │         │  (Gazebo)
  └─────────┘          └─────────┘`}
        </pre>
        <p className="text-sm text-slate-600">Uses CLI wrapping over rclpy for zero-dependency introspection and version compatibility with any ROS 2 distro.</p>
      </Card>

      <Card title="Ports">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-slate-500">
              <th className="pb-2 pr-4 font-medium">Port</th>
              <th className="pb-2 font-medium">Service</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-slate-100">
              <td className="py-2 pr-4 text-xs font-mono">11050</td>
              <td className="py-2 text-xs text-slate-600">FastAPI backend + MCP HTTP</td>
            </tr>
            <tr>
              <td className="py-2 pr-4 text-xs font-mono">11051</td>
              <td className="py-2 text-xs text-slate-600">Vite React frontend (dev)</td>
            </tr>
          </tbody>
        </table>
      </Card>

      <Card title="Badges">
        <div className="flex gap-2 flex-wrap">
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">Python 3.11+</span>
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">ROS 2 CLI</span>
          <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full font-medium">16 tools</span>
          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full font-medium">Zero rclpy dep</span>
        </div>
      </Card>
    </div>
  );
}

function Tools() {
  const discovery = TOOLS.filter((t) => t.group === "Status & Discovery");
  const params = TOOLS.filter((t) => t.group === "Parameters");
  const lifecycle = TOOLS.filter((t) => t.group === "Lifecycle");
  return (
    <div className="space-y-4">
      <Card title="Status & Discovery (9)">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-2 pr-4 font-medium">Tool</th>
                <th className="pb-2 font-medium">Description</th>
              </tr>
            </thead>
            <tbody>
              {discovery.map((t) => (
                <tr key={t.name} className="border-b border-slate-100">
                  <td className="py-2 pr-4 text-xs font-mono text-blue-700 whitespace-nowrap">{t.name}</td>
                  <td className="py-2 text-xs text-slate-600">{t.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Parameters (3)">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-2 pr-4 font-medium">Tool</th>
                <th className="pb-2 font-medium">Description</th>
              </tr>
            </thead>
            <tbody>
              {params.map((t) => (
                <tr key={t.name} className="border-b border-slate-100">
                  <td className="py-2 pr-4 text-xs font-mono text-blue-700 whitespace-nowrap">{t.name}</td>
                  <td className="py-2 text-xs text-slate-600">{t.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Node Lifecycle (4)">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-2 pr-4 font-medium">Tool</th>
                <th className="pb-2 font-medium">Description</th>
              </tr>
            </thead>
            <tbody>
              {lifecycle.map((t) => (
                <tr key={t.name} className="border-b border-slate-100">
                  <td className="py-2 pr-4 text-xs font-mono text-blue-700 whitespace-nowrap">{t.name}</td>
                  <td className="py-2 text-xs text-slate-600">{t.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-500 mt-3">Full reference: <code className="text-xs bg-slate-100 px-1 rounded">docs/ROS_MCP_ARCHITECTURE.md</code> in the repo.</p>
      </Card>
    </div>
  );
}

function Setup() {
  return (
    <div className="space-y-4">
      <Card title="Prerequisites">
        <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
          <li><strong>Python 3.11+</strong> — tested with 3.12, 3.13</li>
          <li><strong>ROS 2</strong> — <code className="text-xs bg-slate-100 px-1 rounded">ros2</code> CLI on PATH (Humble, Jazzy, or newer)</li>
          <li><strong>Git</strong> — for cloning the repo</li>
          <li><strong>uv</strong> (recommended) — <code className="text-xs bg-slate-100 px-1 rounded">pip install uv</code></li>
          <li><strong>Node.js 20+</strong> — for the web dashboard</li>
          <li><strong>Ollama</strong> (optional) — for AI workflow features</li>
        </ul>
      </Card>

      <Card title="Quick Install">
        <pre className="bg-slate-900 text-green-300 text-xs p-3 rounded font-mono whitespace-pre-wrap">
{`git clone https://github.com/sandraschi/ros-mcp
cd ros-mcp
uv sync
uv run python -m ros_mcp

# Start web dashboard
.\web_sota\start.ps1`}
        </pre>
        <p className="text-xs text-slate-500 mt-2">Ensure <code className="text-xs bg-slate-100 px-1 rounded">ros2</code> is on PATH and a ROS 2 graph is active before using the tools.</p>
      </Card>

      <Card title="ROS 2 Setup">
        <pre className="bg-slate-900 text-green-300 text-xs p-3 rounded font-mono whitespace-pre-wrap">
{`# Windows (WSL2) — install ROS 2 Humble in WSL2 Ubuntu
# Then ensure ros2 is accessible:
wsl -e bash -lc "source /opt/ros/humble/setup.bash && ros2 topic list"

# Linux — source your workspace:
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_cpp talker &
uv run python -m ros_mcp`}
        </pre>
      </Card>

      <Card title="Configuration">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500">
                <th className="pb-2 pr-4 font-medium">Variable</th>
                <th className="pb-2 pr-4 font-medium">Default</th>
                <th className="pb-2 font-medium">Description</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-100">
                <td className="py-2 pr-4 text-xs font-mono">ROS_DOMAIN_ID</td>
                <td className="py-2 pr-4 text-xs text-slate-500">default</td>
                <td className="py-2 text-xs text-slate-600">DDS domain ID for multi-robot isolation</td>
              </tr>
              <tr className="border-b border-slate-100">
                <td className="py-2 pr-4 text-xs font-mono">ROS_MCP_PORT</td>
                <td className="py-2 pr-4 text-xs text-slate-500">11050</td>
                <td className="py-2 text-xs text-slate-600">MCP server HTTP port</td>
              </tr>
              <tr>
                <td className="py-2 pr-4 text-xs font-mono">OLLAMA_URL</td>
                <td className="py-2 pr-4 text-xs text-slate-500">http://localhost:11434</td>
                <td className="py-2 text-xs text-slate-600">Ollama for AI tool fallback</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Development Commands">
        <pre className="bg-slate-900 text-green-300 text-xs p-3 rounded font-mono whitespace-pre-wrap">
{`just lint     # ruff check
just test     # pytest
just dev      # backend + frontend with hot reload
just e2e      # Playwright e2e tests`}
        </pre>
      </Card>
    </div>
  );
}

function Troubleshooting() {
  return (
    <Card title="Common Issues">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-slate-500">
              <th className="pb-2 pr-4 font-medium">Symptom</th>
              <th className="pb-2 pr-4 font-medium">Cause</th>
              <th className="pb-2 font-medium">Fix</th>
            </tr>
          </thead>
          <tbody>
            {TROUBLES.map((t, i) => (
              <tr key={i} className="border-b border-slate-100">
                <td className="py-2 pr-4 text-xs text-red-700 font-medium align-top">{t.symptom}</td>
                <td className="py-2 pr-4 text-xs text-slate-600 align-top">{t.cause}</td>
                <td className="py-2 text-xs text-slate-800 font-mono align-top whitespace-pre-wrap">{t.fix}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 p-3 bg-slate-50 rounded text-xs text-slate-600">
        <p className="mb-1"><strong>Log files:</strong> Per-node logs in <code className="text-xs bg-slate-100 px-1 rounded">jobs/&lt;job_id&gt;/</code> for launched processes</p>
        <p className="mb-1"><strong>Reset:</strong> Delete <code className="text-xs bg-slate-100 px-1 rounded">jobs/</code> directory to clear all tracked processes</p>
      </div>
    </Card>
  );
}
