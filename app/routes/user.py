from fastapi import APIRouter, Depends

from app.security.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["User"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.user_update import UserUpdate

@router.put("/me")
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.username = data.username
    current_user.email = data.email

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email
        }
    }

from app.schemas.change_password import ChangePassword
from app.security.password import hash_password, verify_password

@router.put("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(
            status_code=400,
            detail="Old password is incorrect"
        )

    current_user.password = hash_password(data.new_password)

    db.commit()

    return {
        "message": "Password changed successfully"
    }
