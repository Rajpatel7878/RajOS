from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.agent import AgentRunModel
from app.security.dependencies import get_current_user
from app.schemas.agent_schema import (
    AgentResponse,
    AgentCreate,
    AgentUpdate,
    AgentRunRequest,
    AgentRunResponse,
    AgentRunDetail
)
from app.agents.agent_registry import agent_registry
from app.agents.agent_service import agent_service

router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


@router.get("", response_model=List[AgentResponse])
def list_agents(
    include_disabled: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all built-in and user-custom agents available to the authenticated user."""
    return agent_registry.list_agents(db, user_id=user.id, include_disabled=include_disabled)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent_detail(
    agent_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get single agent definition details."""
    agent = agent_registry.get_agent(db, agent_id, user_id=user.id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' was not found.")
    return agent


@router.post("", response_model=AgentResponse)
def create_custom_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new custom user agent definition with backend validation."""
    try:
        return agent_registry.register_custom_agent(db, user.id, payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: str,
    payload: AgentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update custom agent configuration."""
    try:
        agent = agent_registry.update_agent(db, agent_id, user.id, payload)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' was not found.")
        return agent
    except ValueError as ve:
        raise HTTPException(status_code=403, detail=str(ve))


@router.delete("/{agent_id}")
def delete_custom_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete custom user agent definition."""
    success = agent_registry.delete_custom_agent(db, agent_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Custom agent '{agent_id}' not found or cannot be deleted.")
    return {"status": "deleted", "agent_id": agent_id}


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
def run_agent(
    agent_id: str,
    request: AgentRunRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Execute an agent run with prompt context, capabilities, and tool step limits."""
    try:
        res = agent_service.run_agent(
            db=db,
            agent_id=agent_id,
            user_id=user.id,
            prompt=request.prompt,
            conversation_id=request.conversation_id,
            confirmation=request.confirmation
        )
        return res
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Agent run execution failed: {str(ex)}")


@router.get("/runs/{run_id}", response_model=AgentRunDetail)
def get_run_detail(
    run_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Fetch details and step history of an agent run verifying user ownership."""
    run_record = db.query(AgentRunModel).filter(
        AgentRunModel.id == run_id,
        AgentRunModel.user_id == user.id
    ).first()
    if not run_record:
        raise HTTPException(status_code=404, detail="Agent run was not found.")
    return run_record


@router.post("/runs/{run_id}/cancel")
def cancel_run(
    run_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Cancel an active agent run."""
    run_record = db.query(AgentRunModel).filter(
        AgentRunModel.id == run_id,
        AgentRunModel.user_id == user.id
    ).first()
    if not run_record:
        raise HTTPException(status_code=404, detail="Agent run was not found.")

    run_record.status = "cancelled"
    db.commit()
    return {"status": "cancelled", "run_id": run_id}
