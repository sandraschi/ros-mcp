import { useState, useEffect, useCallback } from "react";

export default function Services() {
  const [services, setServices] = useState<string[]>([]);
  const [svcName, setSvcName] = useState("");
  const [svcType, setSvcType] = useState("");
  const [svcValue, setSvcValue] = useState("");
  const [svcResult, setSvcResult] = useState("");

  const fetchServices = useCallback(async () => {
    try {
      const r = await fetch("/api/services");
      if (r.ok) {
        const d = await r.json();
        if (d.services) setServices(d.services);
      }
    } catch {}
  }, []);

  useEffect(() => {
    fetchServices();
    const iv = setInterval(fetchServices, 5000);
    return () => clearInterval(iv);
  }, [fetchServices]);

  const handleCall = async () => {
    setSvcResult("Calling...");
    try {
      const r = await fetch("/api/services/call", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ service_name: svcName, service_type: svcType, values: svcValue }),
      });
      const d = await r.json();
      setSvcResult(d.response || d.error || "Done");
    } catch (e) {
      setSvcResult(String(e));
    }
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-6">Services</h1>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-xl border border-slate-700">
          <h2 className="text-lg font-semibold p-4 border-b border-slate-700">Service List</h2>
          <div className="divide-y divide-slate-700 max-h-96 overflow-auto">
            {services.length === 0 && (
              <div className="p-4 text-sm text-slate-500">No services found.</div>
            )}
            {services.map((s) => (
              <div
                key={s}
                className="p-3 text-sm hover:bg-slate-700/50 cursor-pointer"
                onClick={() => setSvcName(s)}
              >
                {s}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <h2 className="text-lg font-semibold mb-3">Call Service</h2>
          <div className="space-y-2">
            <input
              className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-sm"
              placeholder="Service name"
              value={svcName}
              onChange={(e) => setSvcName(e.target.value)}
            />
            <input
              className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-sm"
              placeholder="Type (optional)"
              value={svcType}
              onChange={(e) => setSvcType(e.target.value)}
            />
            <textarea
              className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-sm font-mono"
              rows={3}
              placeholder='Arguments JSON (optional)'
              value={svcValue}
              onChange={(e) => setSvcValue(e.target.value)}
            />
            <button
              onClick={handleCall}
              className="bg-cyan-700 hover:bg-cyan-600 text-white px-3 py-1.5 rounded text-sm"
            >
              Call
            </button>
            {svcResult && (
              <pre className="bg-slate-900 rounded p-2 text-xs text-slate-300 max-h-40 overflow-auto mt-2 whitespace-pre-wrap">
                {svcResult}
              </pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
