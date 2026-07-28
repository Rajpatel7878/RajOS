from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import ProfileUpdate, ChangePassword
from app.security.password import verify_password, hash_password
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get("")
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }


@router.put("/update")
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.username = data.username
    current_user.email = data.email

    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated"}


@router.post("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not verify_password(
        data.old_password,
        current_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Old password incorrect"
        )

    current_user.password = hash_password(
        data.new_password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }
