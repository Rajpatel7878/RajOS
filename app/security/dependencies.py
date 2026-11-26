import base64
import json
import os
import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    email = None

    if credentials and credentials.credentials:
        token = credentials.credentials

        # Decode token with primary secret from environment
        try:
            secret_key = os.getenv("SECRET_KEY")
            if not secret_key:
                raise ValueError("SECRET_KEY not configured")
            payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
            if payload.get("type") == "refresh":
                raise HTTPException(
                    status_code=401,
                    detail="Refresh token cannot be used for authentication",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            email = payload.get("sub")
        except ExpiredSignatureError:
            logger.info("Rejected expired bearer token")
            raise HTTPException(
                status_code=401,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (JWTError, ValueError):
            # Handle base64 encoded token prefixes (rajos_jwt_, ragos_google_jwt_)
            try:
                raw = token
                for prefix in ["rajos_google_jwt_", "rajos_jwt_"]:
                    if raw.startswith(prefix):
                        raw = raw[len(prefix):]
                decoded = base64.b64decode(raw).decode("utf-8")
                data = json.loads(decoded)
                email = data.get("sub") or data.get("email")
            except Exception:
                email = None

            # A token was supplied but could not be honoured: tell the client to re-auth
            # instead of silently acting as the default user.
            if not email:
                logger.info("Rejected invalid bearer token")
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    if not email:
        email = "default_user@rajos.io"

    # Lookup or auto-create user in database
    user = db.query(User).filter(User.email == email).first()
    if not user:
        username = email.split("@")[0] if "@" in email else "rajos_user"
        user = User(
            username=username,
            email=email,
            password="rajos_managed_user",
            notifications_enabled=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
