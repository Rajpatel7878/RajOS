from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.automation.automation_schemas import (
    AutomationCreate,
    AutomationUpdate,
    AutomationEvent
)
from app.automation.automation_service import automation_service

from app.models.user import User
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/automation",
    tags=["Automation"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



@router.post("/")
def create_automation(
    data: AutomationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    return automation_service.create(
        db,
        user.id,
        data
    )



@router.get("/")
def list_automations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    return automation_service.get_all(
        db,
        user.id
    )



@router.get("/{automation_id}")
def get_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    automation = automation_service.get_one(
        db,
        user.id,
        automation_id
    )


    if not automation:
        raise HTTPException(
            status_code=404,
            detail="Automation not found"
        )


    return automation



@router.put("/{automation_id}")
def update_automation(
    automation_id: int,
    data: AutomationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    automation = automation_service.get_one(
        db,
        user.id,
        automation_id
    )


    if not automation:
        raise HTTPException(
            status_code=404,
            detail="Automation not found"
        )


    return automation_service.update(
        db,
        automation,
        data
    )



@router.delete("/{automation_id}")
def delete_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    automation = automation_service.get_one(
        db,
        user.id,
        automation_id
    )


    if not automation:
        raise HTTPException(
            status_code=404,
            detail="Automation not found"
        )


    return automation_service.delete(
        db,
        automation
    )


from app.automation.trigger_engine import trigger_engine


@router.post("/{automation_id}/execute")
def execute_automation(
    automation_id: int,
    event: AutomationEvent,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    automation = automation_service.get_one(
        db,
        user.id,
        automation_id
    )


    if not automation:
        raise HTTPException(
            status_code=404,
            detail="Automation not found"
        )


    result = trigger_engine.execute_trigger(
        automation,
        event.model_dump()
    )


    return {
        "automation_id": automation.id,
        "automation_name": automation.name,
        "result": result
    }
