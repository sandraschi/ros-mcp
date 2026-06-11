import { useState, useEffect, useCallback } from "react";

interface Topic {
  name: string;
  type: string;
}

export default function Topics() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [echoTopic, setEchoTopic] = useState("");
  const [echoResult, setEchoResult] = useState("");
  const [publishTopic, setPublishTopic] = useState("");
  const [publishType, setPublishType] = useState("");
  const [publishValue, setPublishValue] = useState("");

  const fetchTopics = useCallback(async () => {
    try {
      const r = await fetch("/api/topics");
      if (r.ok) {
        const d = await r.json();
        if (d.topics) setTopics(d.topics);
      }
    } catch {}
  }, []);

  useEffect(() => {
    fetchTopics();
    const iv = setInterval(fetchTopics, 5000);
    return () => clearInterval(iv);
  }, [fetchTopics]);

  const handleEcho = async (name: string) => {
    setEchoTopic(name);
    setEchoResult("Echoing...");
    try {
      const r = await fetch("/api/topics/echo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic_name: name, timeout: 3 }),
      });
      const d = await r.json();
      setEchoResult(d.messages?.join("\n") || d.error || "No messages");
    } catch (e) {
      setEchoResult(String(e));
    }
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-6">Topics</h1>

      <div className="grid grid-cols-2 gap-6">
        {/* Topic List */}
        <div className="bg-slate-800 rounded-xl border border-slate-700">
          <h2 className="text-lg font-semibold p-4 border-b border-slate-700">Topic Browser</h2>
          <div className="divide-y divide-slate-700 max-h-96 overflow-auto">
            {topics.length === 0 && (
              <div className="p-4 text-sm text-slate-500">No topics found.</div>
            )}
            {topics.map((t) => (
              <div key={t.name} className="p-3 flex items-center justify-between text-sm hover:bg-slate-700/50">
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{t.name}</div>
                  <div className="text-xs text-slate-400 truncate">{t.type || "unknown type"}</div>
                </div>
                <button
                  onClick={() => handleEcho(t.name)}
                  className="ml-2 text-xs bg-cyan-800 hover:bg-cyan-700 text-cyan-200 px-2 py-1 rounded"
                >
                  Echo
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Echo / Publish */}
        <div className="space-y-4">
          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h3 className="text-sm font-semibold mb-2">Echo: {echoTopic || "(select a topic)"}</h3>
            <pre className="bg-slate-900 rounded p-2 text-xs text-slate-300 max-h-48 overflow-auto whitespace-pre-wrap">
              {echoResult || "Click Echo on a topic to see messages."}
            </pre>
          </div>

          <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
            <h3 className="text-sm font-semibold mb-2">Publish</h3>
            <div className="space-y-2">
              <input
                className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-sm"
                placeholder="Topic name (e.g. /cmd_vel)"
                value={publishTopic}
                onChange={(e) => setPublishTopic(e.target.value)}
              />
              <input
                className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-sm"
                placeholder="Type (e.g. geometry_msgs/msg/Twist)"
                value={publishType}
                onChange={(e) => setPublishType(e.target.value)}
              />
              <textarea
                className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1.5 text-sm font-mono"
                rows={3}
                placeholder='{"linear": {"x": 0.1}}'
                value={publishValue}
                onChange={(e) => setPublishValue(e.target.value)}
              />
              <button className="bg-cyan-700 hover:bg-cyan-600 text-white px-3 py-1.5 rounded text-sm">
                Publish
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
