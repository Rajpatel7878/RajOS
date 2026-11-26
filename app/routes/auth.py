import os
import time
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database.connection import get_db
from app.models.user import User
from app.security.jwt import (
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
)
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.rate_limiter import check_auth_rate_limit

router = APIRouter()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@router.post("/register", response_model=UserResponse, dependencies=[Depends(check_auth_rate_limit)])
def register(user: UserCreate, db: Session = Depends(get_db), request: Request = ...):
    
    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=pwd_context.hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", dependencies=[Depends(check_auth_rate_limit)])
def login(user: UserLogin, db: Session = Depends(get_db), request: Request = ...):
    
    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not pwd_context.verify(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Wrong password"
        )

    return _token_response(db_user.email)


class RefreshRequest(BaseModel):
    """Body for POST /refresh."""

    refresh_token: str


def _token_response(email: str) -> dict:
    """Issue a fresh access token plus a rotating refresh token."""
    return {
        "access_token": create_access_token({"sub": email}),
        "refresh_token": create_refresh_token({"sub": email}),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_expires_in": REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    }


@router.post("/refresh")
def refresh(req: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token (without a password)."""
    try:
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise ValueError("SECRET_KEY not configured")
        payload = jwt.decode(req.refresh_token, secret_key, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return _token_response(user.email)
