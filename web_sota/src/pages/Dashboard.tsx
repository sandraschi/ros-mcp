import { useState, useEffect, useCallback } from "react";

interface RosStatus {
  ros_available: boolean;
  topic_count: number;
  node_count: number;
  service_count: number;
  active_jobs: number;
  error?: string;
}

export default function Dashboard() {
  const [status, setStatus] = useState<RosStatus | null>(null);
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiResult, setAiResult] = useState("");

  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch("/api/health");
      if (r.ok) setStatus(await r.json());
    } catch {}
  }, []);

  useEffect(() => {
    fetchStatus();
    const iv = setInterval(fetchStatus, 5000);
    return () => clearInterval(iv);
  }, [fetchStatus]);

  const handleAiExecute = async () => {
    setAiResult("Thinking...");
    try {
      const r = await fetch("/api/llm/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "llama3.2:3b",
          prompt: `You are a ROS 2 robotics assistant. ${aiPrompt}`,
        }),
      });
      const data = await r.json();
      setAiResult(data.response || data.error || "No response");
    } catch (e) {
      setAiResult(String(e));
    }
  };

  const rosOk = status?.ros_available;

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: "ROS 2", value: rosOk ? "Available" : status ? "N/A" : "..." },
          { label: "Topics", value: status?.topic_count ?? "..." },
          { label: "Nodes", value: status?.node_count ?? "..." },
          { label: "Services", value: status?.service_count ?? "..." },
        ].map((c) => (
          <div key={c.label} className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <div className="text-xs text-slate-400 uppercase tracking-wider">{c.label}</div>
            <div className={`text-2xl font-bold mt-1 ${rosOk ? "text-cyan-300" : "text-red-400"}`}>{c.value}</div>
          </div>
        ))}
      </div>

      {status?.error && (
        <div className="bg-red-900/50 text-red-300 px-4 py-3 rounded-xl mb-6 text-sm border border-red-800">
          {status.error}
        </div>
      )}

      <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 mb-8">
        <h2 className="text-lg font-semibold mb-3">Quick AI Workflow</h2>
        <div className="flex gap-3">
          <input
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-cyan-500"
            placeholder="e.g. list all topics and echo /chatter"
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAiExecute()}
          />
          <button
            onClick={handleAiExecute}
            className="bg-cyan-700 hover:bg-cyan-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            Execute
          </button>
        </div>
        {aiResult && (
          <pre className="mt-3 bg-slate-900 rounded-lg p-3 text-xs text-slate-300 max-h-40 overflow-auto whitespace-pre-wrap">
            {aiResult}
          </pre>
        )}
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700">
        <h2 className="text-lg font-semibold p-4 border-b border-slate-700">Active Jobs</h2>
        <div className="p-4 text-sm text-slate-500">
          {status?.active_jobs ? `${status.active_jobs} running` : "No active jobs. Launch a node from the Nodes page."}
        </div>
      </div>
    </div>
  );
}
