"""
Google OAuth endpoint — receives Supabase user info and returns a RajOS JWT.
Called by the /auth/callback frontend page after Google sign-in.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext

from app.database.connection import get_db
from app.models.user import User
from app.security.jwt import create_access_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class GoogleUserPayload(BaseModel):
    email: str
    name: str
    google_id: str  # Supabase user.id


@router.post("/auth/google")
def google_auth(payload: GoogleUserPayload, db: Session = Depends(get_db)):
    """
    Creates or retrieves a RajOS user from Google OAuth data and
    returns a RajOS JWT access token.
    """
    # Derive a stable password from the google_id so the account
    # can also be accessed via the normal /login endpoint if needed.
    derived_password = f"google_oauth_{payload.google_id}"

    existing = db.query(User).filter(User.email == payload.email).first()

    if existing:
        # User already exists — return a fresh token
        token = create_access_token({"sub": existing.email})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": existing.id, "username": existing.username, "email": existing.email},
            "is_new": False,
        }

    # New user — register them
    new_user = User(
        username=payload.name or payload.email.split("@")[0],
        email=payload.email,
        password=pwd_context.hash(derived_password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email},
        "is_new": True,
    }
