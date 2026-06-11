import { useState, useEffect, useRef, useCallback } from "react";

interface LogEntry {
  source: string;
  content: string;
}

export default function Logging() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [search, setSearch] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchLogs = useCallback(async () => {
    try {
      const r = await fetch("/api/jobs");
      if (r.ok) {
        const d = await r.json();
        if (d.jobs) {
          const entries: LogEntry[] = [];
          for (const job of d.jobs) {
            if (job.state === "running") {
              try {
                const lr = await fetch("/api/jobs/log", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ job_id: job.job_id, lines: 20 }),
                });
                const ld = await lr.json();
                if (ld.stderr) for (const line of ld.stderr) entries.push({ source: job.label, content: line });
                if (ld.stdout) for (const line of ld.stdout) entries.push({ source: job.label, content: line });
              } catch {}
            }
          }
          setLogs(entries.slice(-200));
        }
      }
    } catch {}
  }, []);

  useEffect(() => {
    fetchLogs();
    const iv = setInterval(fetchLogs, 3000);
    return () => clearInterval(iv);
  }, [fetchLogs]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const displayed = logs.filter((l) =>
    !search || l.content.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-6">Logging</h1>

      <div className="flex gap-3 mb-4">
        <input
          className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm flex-1 min-w-48 focus:outline-none focus:border-cyan-500"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="text-xs text-slate-400 self-center">{displayed.length} entries</div>
      </div>

      <div className="bg-black rounded-xl border border-slate-700 p-4 font-mono text-xs h-[600px] overflow-auto">
        {displayed.length === 0 && (
          <div className="text-slate-600">No log entries. Launch a node to see output here.</div>
        )}
        {displayed.map((l, i) => (
          <div key={i} className="mb-1">
            <span className="text-cyan-500">[{l.source}]</span>{" "}
            <span className="text-slate-400 whitespace-pre-wrap">{l.content}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
