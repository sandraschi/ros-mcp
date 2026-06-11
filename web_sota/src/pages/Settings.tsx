import { useState, useEffect } from "react";

export default function Settings() {
  const [rosDomainId, setRosDomainId] = useState("");
  const [rmwImpl, setRmwImpl] = useState("");
  const [toast, setToast] = useState("");

  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then((d) => {
        if (d.settings) {
          setRosDomainId(d.settings.ROS_DOMAIN_ID || "");
          setRmwImpl(d.settings.RMW_IMPLEMENTATION || "");
        }
      })
      .catch(() => {});
  }, []);

  const handleSave = async () => {
    try {
      const r = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ROS_DOMAIN_ID: rosDomainId, RMW_IMPLEMENTATION: rmwImpl }),
      });
      if (r.ok) {
        setToast("Settings saved (session only).");
        setTimeout(() => setToast(""), 3000);
      } else {
        setToast("Failed to save settings.");
      }
    } catch (e) {
      setToast(String(e));
    }
  };

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      {toast && (
        <div className="bg-green-900 text-green-300 px-4 py-2 rounded-lg mb-4 text-sm">{toast}</div>
      )}

      <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 space-y-4">
        <div>
          <label className="block text-xs text-slate-400 mb-1">ROS_DOMAIN_ID</label>
          <input
            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-cyan-500"
            value={rosDomainId}
            onChange={(e) => setRosDomainId(e.target.value)}
            placeholder="e.g. 42"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">RMW_IMPLEMENTATION</label>
          <select
            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-cyan-500"
            value={rmwImpl}
            onChange={(e) => setRmwImpl(e.target.value)}
          >
            <option value="">Default</option>
            <option value="rmw_fastrtps_cpp">rmw_fastrtps_cpp</option>
            <option value="rmw_cyclonedds_cpp">rmw_cyclonedds_cpp</option>
            <option value="rmw_gurumdds_cpp">rmw_gurumdds_cpp</option>
          </select>
        </div>
        <div className="text-xs text-slate-500">Changes persist for the current session only.</div>
        <button
          onClick={handleSave}
          className="bg-cyan-700 hover:bg-cyan-600 text-white px-5 py-2 rounded-lg text-sm font-medium"
        >
          Save
        </button>
      </div>
    </div>
  );
}
