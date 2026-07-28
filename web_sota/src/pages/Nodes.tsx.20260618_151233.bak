import { useState, useEffect, useCallback } from "react";

export default function Nodes() {
  const [nodes, setNodes] = useState<string[]>([]);
  const [selectedNode, setSelectedNode] = useState("");
  const [params, setParams] = useState<string[]>([]);
  const [paramName, setParamName] = useState("");
  const [paramValue, setParamValue] = useState("");
  const [paramResult, setParamResult] = useState("");

  const fetchNodes = useCallback(async () => {
    try {
      const r = await fetch("/api/nodes");
      if (r.ok) {
        const d = await r.json();
        if (d.nodes) setNodes(d.nodes);
      }
    } catch {}
  }, []);

  useEffect(() => {
    fetchNodes();
    const iv = setInterval(fetchNodes, 5000);
    return () => clearInterval(iv);
  }, [fetchNodes]);

  const handleGetParam = async () => {
    if (!selectedNode || !paramName) return;
    setParamResult("Loading...");
    try {
      const r = await fetch("/api/nodes/param_get", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_name: selectedNode, param_name: paramName }),
      });
      const d = await r.json();
      setParamResult(JSON.stringify(d.value ?? d.error, null, 2));
    } catch (e) {
      setParamResult(String(e));
    }
  };

  const handleSetParam = async () => {
    if (!selectedNode || !paramName) return;
    setParamResult("Setting...");
    try {
      const r = await fetch("/api/nodes/param_set", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ node_name: selectedNode, param_name: paramName, value: paramValue }),
      });
      const d = await r.json();
      setParamResult(d.message || d.error || "Done");
    } catch (e) {
      setParamResult(String(e));
    }
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-6">Nodes</h1>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-xl border border-slate-700">
          <h2 className="text-lg font-semibold p-4 border-b border-slate-700">Node List</h2>
          <div className="divide-y divide-slate-700 max-h-96 overflow-auto">
            {nodes.length === 0 && (
              <div className="p-4 text-sm text-slate-500">No nodes found.</div>
            )}
            {nodes.map((n) => (
              <div
                key={n}
                className={`p-3 text-sm hover:bg-slate-700/50 cursor-pointer ${selectedNode === n ? "bg-cyan-900/30" : ""}`}
                onClick={() => setSelectedNode(n)}
              >
                {n}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h2 className="text-lg font-semibold mb-3">Parameters: {selectedNode || "(select a node)"}</h2>
          <div className="space-y-2">
            <input
              className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-sm"
              placeholder="Parameter name"
              value={paramName}
              onChange={(e) => setParamName(e.target.value)}
            />
            <div className="flex gap-2">
              <button onClick={handleGetParam} className="bg-cyan-700 hover:bg-cyan-600 text-white px-3 py-1.5 rounded text-sm">
                Get
              </button>
              <input
                className="flex-1 bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-sm"
                placeholder="Value (for set)"
                value={paramValue}
                onChange={(e) => setParamValue(e.target.value)}
              />
              <button onClick={handleSetParam} className="bg-green-700 hover:bg-green-600 text-white px-3 py-1.5 rounded text-sm">
                Set
              </button>
            </div>
            {paramResult && (
              <pre className="bg-slate-900 rounded p-2 text-xs text-slate-300 max-h-40 overflow-auto mt-2 whitespace-pre-wrap">
                {paramResult}
              </pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
