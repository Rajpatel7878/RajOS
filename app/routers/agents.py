from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.database.connection import SessionLocal
from app.models.user import User
from app.security.dependencies import get_current_user
from app.agents.agent_router import AgentRouter, get_agent_instance, get_all_agents


router = APIRouter(prefix="/agents", tags=["Agents"])

router_engine = AgentRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AgentRunRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None


@router.get("/")
def list_agents(
    user: User = Depends(get_current_user)
):
    """List all available agents with their metadata."""
    return get_all_agents()


@router.post("/{agent_id}/run")
def run_agent(
    agent_id: str,
    request: AgentRunRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Run a specific agent with a prompt."""
    valid_agents = ["atlas", "nova", "sage", "echo", "pulse"]

    if agent_id not in valid_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found. Available: {valid_agents}"
        )

    try:
        agent = get_agent_instance(agent_id)
        result = agent.run(
            message=request.prompt,
            context=request.context or {}
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/{agent_id}/status")
def get_agent_status(
    agent_id: str,
    user: User = Depends(get_current_user)
):
    """Get status of a specific agent."""
    valid_agents = ["atlas", "nova", "sage", "echo", "pulse"]

    if agent_id not in valid_agents:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found."
        )

    return {
        "agent_id": agent_id,
        "status": "Active",
        "last_active": "Now",
        "tasks_completed": 0,
        "success_rate": 98.5,
    }


@router.post("/route")
def route_message(
    request: AgentRunRequest,
    user: User = Depends(get_current_user)
):
    """Auto-route a message to the best agent and run it."""
    agent_id = router_engine.route(request.prompt)

    agent = get_agent_instance(agent_id)
    result = agent.run(
        message=request.prompt,
        context=request.context or {}
    )
    return result
