from fastapi import APIRouter
from app.agent_loop import run_agent
from pydantic import BaseModel


router = APIRouter()


class AgentRequest(BaseModel):
    query: str
    content_id: str | None = None
    top_k: int = 3
    mode: str | None = None


@router.post("/agent")
def agent_run(request: AgentRequest):
    return run_agent(request.query)
