from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.security.dependencies import get_current_user
from app.models.user import User
from app.productivity.task_analyzer import task_analyzer
from app.productivity.workload_service import workload_service
from app.productivity.recommendation_engine import recommendation_engine
from app.productivity.planning_service import planning_service


router = APIRouter(
    prefix="/productivity",
    tags=["Productivity"]
)


class PlanRequest(BaseModel):
    available_minutes: Optional[int] = Field(None, description="Available minutes", ge=15, le=1440)
    constraints: Optional[str] = None


class BreakdownRequest(BaseModel):
    title: str = Field(..., description="Title of task to break down")
    description: Optional[str] = None


@router.get("/summary")
def get_productivity_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return task_analyzer.analyze_user_tasks(db, user.id)


@router.get("/daily")
def get_daily_brief(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return workload_service.get_daily_brief(db, user.id)


@router.get("/weekly")
def get_weekly_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return workload_service.get_weekly_summary(db, user.id)


@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    recs = recommendation_engine.generate_recommendations(db, user.id)
    return {"count": len(recs), "recommendations": recs}


@router.get("/workload")
def get_workload(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return workload_service.get_workload_analysis(db, user.id)


@router.get("/trends")
def get_trends(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return workload_service.get_productivity_trends(db, user.id)


@router.post("/plan")
def plan_daily_tasks(
    req: PlanRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return planning_service.plan_day(
        db=db,
        user_id=user.id,
        available_minutes=req.available_minutes,
        constraints=req.constraints
    )


@router.post("/breakdown")
def breakdown_task(
    req: BreakdownRequest,
    user: User = Depends(get_current_user)
):
    return planning_service.breakdown_task(title=req.title, description=req.description)
