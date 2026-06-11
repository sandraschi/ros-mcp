"""FastAPI backend for the ros-mcp web dashboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ros_mcp.server import ros_status, topic_list, service_list, node_list, list_jobs
from web_sota.backend.routes.ai import router as ai_router

app = FastAPI(title="ros-mcp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)


@app.get("/health")
@app.get("/api/health")
async def health():
    return ros_status()


@app.get("/api/topics")
async def api_topics():
    return topic_list()


@app.get("/api/services")
async def api_services():
    return service_list()


@app.get("/api/nodes")
async def api_nodes():
    return node_list()


@app.get("/api/jobs")
async def api_jobs():
    return list_jobs()


@app.get("/api/llm/providers")
async def llm_providers():
    import httpx
    try:
        r = httpx.get("http://127.0.0.1:11434/api/tags", timeout=3)
        return {"ollama": r.json().get("models", [{"name": "llama3.2:3b"}])}
    except Exception:
        return {"ollama": [{"name": "llama3.2:3b"}]}


@app.post("/api/llm/chat")
async def llm_chat(body: dict):
    import httpx
    try:
        resp = httpx.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": body.get("model", "llama3.2:3b"), "prompt": body.get("prompt", ""), "stream": False},
            timeout=60,
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/settings")
async def get_settings():
    import os
    return {"settings": {"ROS_DOMAIN_ID": os.environ.get("ROS_DOMAIN_ID", ""), "RMW_IMPLEMENTATION": os.environ.get("RMW_IMPLEMENTATION", "")}}


@app.post("/api/settings")
async def set_settings(body: dict):
    import os
    if "ROS_DOMAIN_ID" in body:
        os.environ["ROS_DOMAIN_ID"] = str(body["ROS_DOMAIN_ID"])
    if "RMW_IMPLEMENTATION" in body:
        os.environ["RMW_IMPLEMENTATION"] = str(body["RMW_IMPLEMENTATION"])
    return {"success": True, "message": "Settings updated (session only)."}


# Mount MCP HTTP
mcp_mod = __import__("ros_mcp.server", fromlist=["mcp"])
app.mount("/mcp", mcp_mod.mcp.http_app())

# Serve frontend static files (if dist exists)
dist = Path(__file__).resolve().parent.parent / "dist"
if dist.is_dir():
    app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")


def run_dev() -> None:
    import uvicorn
    uvicorn.run("web_sota.backend.server:app", host="127.0.0.1", port=11050, log_level="info", reload=True)


if __name__ == "__main__":
    run_dev()
