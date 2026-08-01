from sqlalchemy.orm import Session

from app.automation.automation_models import Automation
from app.automation.automation_schemas import (
    AutomationCreate,
    AutomationUpdate
)


class AutomationService:


    def create(
        self,
        db: Session,
        user_id: int,
        data: AutomationCreate
    ):

        automation = Automation(
            user_id=user_id,
            name=data.name,
            trigger=data.trigger,
            action=data.action
        )

        db.add(automation)
        db.commit()
        db.refresh(automation)

        return automation



    def get_all(
        self,
        db: Session,
        user_id: int
    ):

        return db.query(Automation).filter(
            Automation.user_id == user_id
        ).all()



    def get_one(
        self,
        db: Session,
        user_id: int,
        automation_id: int
    ):

        return db.query(Automation).filter(
            Automation.id == automation_id,
            Automation.user_id == user_id
        ).first()



    def update(
        self,
        db: Session,
        automation: Automation,
        data: AutomationUpdate
    ):

        if data.name is not None:
            automation.name = data.name

        if data.trigger is not None:
            automation.trigger = data.trigger

        if data.action is not None:
            automation.action = data.action

        if data.enabled is not None:
            automation.enabled = data.enabled


        db.commit()
        db.refresh(automation)

        return automation



    def delete(
        self,
        db: Session,
        automation: Automation
    ):

        db.delete(automation)
        db.commit()

        return {
            "message": "Automation deleted successfully"
        }


automation_service = AutomationService()
