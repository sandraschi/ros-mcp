"""AI workflow routes — proxies MCP tool calls through REST with Ollama fallback."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["AI"], prefix="/api/ai")


class WorkflowBody(BaseModel):
    goal: str


class NLControlBody(BaseModel):
    prompt: str
    job_id: str


class AnalyzeStateBody(BaseModel):
    job_id: str


class AnalyzeLogsBody(BaseModel):
    job_id: str


@router.post("/workflow")
async def post_workflow(body: WorkflowBody):
    return {"success": True, "message": "Workflow stub", "goal": body.goal}


@router.post("/nl-control")
async def post_nl_control(body: NLControlBody):
    return {"success": True, "message": "NL control stub", "prompt": body.prompt, "job_id": body.job_id}


@router.post("/analyze-state")
async def post_analyze_state(body: AnalyzeStateBody):
    return {"success": True, "message": "Analyze state stub", "job_id": body.job_id}


@router.post("/analyze-logs")
async def post_analyze_logs(body: AnalyzeLogsBody):
    return {"success": True, "message": "Analyze logs stub", "job_id": body.job_id}
