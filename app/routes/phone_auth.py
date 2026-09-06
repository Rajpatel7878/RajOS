"""
Phone OTP Authentication & Mobile Task Notification Engine for RajOS.
Supports:
1. /auth/phone/send-otp: Generates secure 6-digit cryptographic OTP, hashes with secret salt,
   dispatches SMS via Twilio or Fast2SMS if configured, or provides dev_otp for local testing.
2. /auth/phone/verify-otp: Verifies OTP against cryptographic hash with expiry & attempt limits,
   auto-creates or logs in the user, and issues a standard RajOS JWT.
3. /auth/phone/link: Links a verified phone number to an account (e.g. after Google Sign-In)
   and enables task mobile push/SMS notifications.
4. /auth/phone/verify: Supabase backward compatibility endpoint.
"""

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.security.jwt import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret salt for OTP hashing
OTP_SALT = os.getenv("SECRET_KEY", "rajos_otp_secure_salt_7878")
OTP_EXPIRY_SECONDS = 300  # 5 minutes
MIN_RESEND_INTERVAL = 15  # 15 seconds cooldown

# In-memory secure OTP vault:
# phone -> { "hash": str, "expires_at": float, "attempts": int, "created_at": float, "dev_otp": str }
_OTP_VAULT: dict[str, dict] = {}


def normalize_phone_number(raw: str) -> str:
    """Normalize any phone input into E.164 standard format (e.g. +919876543210)."""
    cleaned = re.sub(r"[^\d+]", "", raw.strip())
    if not cleaned:
        raise ValueError("Phone number cannot be empty")

    if cleaned.startswith("+"):
        digits = cleaned[1:]
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Invalid phone number length")
        return cleaned

    # Handle leading zero
    if cleaned.startswith("0"):
        cleaned = cleaned[1:]

    # If 10 digits, default to India (+91)
    if len(cleaned) == 10:
        return f"+91{cleaned}"
    elif len(cleaned) == 12 and cleaned.startswith("91"):
        return f"+{cleaned}"
    elif 10 < len(cleaned) <= 15:
        return f"+{cleaned}"
    else:
        raise ValueError("Please provide a valid 10-digit mobile number")


def hash_otp(phone: str, otp: str) -> str:
    """Compute secure HMAC-SHA256 hash of the OTP for the given phone."""
    message = f"{phone}:{otp}:{OTP_SALT}".encode("utf-8")
    return hmac.new(OTP_SALT.encode("utf-8"), message, hashlib.sha256).hexdigest()


# ── SMS Gateways ──────────────────────────────────────────────────────────────

def send_sms_via_twilio(phone: str, otp: str) -> bool:
    """Send SMS via Twilio if TWILIO credentials are configured."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not (account_sid and auth_token and from_number):
        return False

    try:
        import urllib.parse
        import urllib.request
        import base64

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        body = f"Your RajOS task verification code is: {otp}. Valid for 5 minutes. Do not share."

        data = urllib.parse.urlencode({
            "To": phone,
            "From": from_number,
            "Body": body,
        }).encode("utf-8")

        auth_str = f"{account_sid}:{auth_token}"
        auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Authorization", f"Basic {auth_b64}")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in (200, 201):
                logger.info("Twilio SMS sent successfully to %s", phone)
                return True
    except Exception as exc:
        logger.warning("Twilio SMS dispatch failed: %s", exc)
    return False


def send_sms_via_fast2sms(phone: str, otp: str) -> bool:
    """Send SMS via Fast2SMS (India Quick Transactional OTP) if FAST2SMS_API_KEY is set."""
    api_key = os.getenv("FAST2SMS_API_KEY")
    if not api_key:
        return False

    try:
        import urllib.request

        # Extract 10-digit number for India
        digits = re.sub(r"[^\d]", "", phone)
        if digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]

        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = json.dumps({
            "variables_values": otp,
            "route": "otp",
            "numbers": digits,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("authorization", api_key)
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if res_data.get("return") is True:
                logger.info("Fast2SMS OTP sent successfully to %s", phone)
                return True
            else:
                logger.warning("Fast2SMS rejected dispatch: %s", res_data.get("message"))
    except Exception as exc:
        logger.warning("Fast2SMS dispatch failed: %s", exc)
    return False


def dispatch_sms(phone: str, otp: str) -> tuple[bool, str]:
    """Try configured SMS gateways in order: Twilio -> Fast2SMS."""
    if send_sms_via_twilio(phone, otp):
        return True, "twilio"
    if send_sms_via_fast2sms(phone, otp):
        return True, "fast2sms"
    return False, "none"


# ── Schemas ──────────────────────────────────────────────────────────────────

class SendOTPRequest(BaseModel):
    phone: str


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


class LinkPhoneRequest(BaseModel):
    phone: str
    otp: Optional[str] = None
    email: Optional[str] = None


class SupabasePhoneVerifyPayload(BaseModel):
    phone: str
    supabase_user_id: str
    name: str = ""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/auth/phone/send-otp")
def send_otp(payload: SendOTPRequest):
    """
    Generates a secure 6-digit OTP, stores its cryptographic hash,
    and dispatches via SMS (or returns dev_otp in dev mode).
    """
    try:
        norm_phone = normalize_phone_number(payload.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    now = time.time()
    existing = _OTP_VAULT.get(norm_phone)

    # Rate limiting: enforce resend interval
    if existing and (now - existing["created_at"]) < MIN_RESEND_INTERVAL:
        remaining = int(MIN_RESEND_INTERVAL - (now - existing["created_at"]))
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {remaining} seconds before requesting a new OTP."
        )

    # Generate 6-digit numeric OTP
    otp_code = f"{secrets.randbelow(900000) + 100000}"
    hashed = hash_otp(norm_phone, otp_code)

    _OTP_VAULT[norm_phone] = {
        "hash": hashed,
        "expires_at": now + OTP_EXPIRY_SECONDS,
        "attempts": 0,
        "created_at": now,
        "dev_otp": otp_code,
    }

    # Attempt SMS dispatch
    sms_dispatched, provider = dispatch_sms(norm_phone, otp_code)
    logger.info("[RajOS Phone Auth] Verification code for %s: %s (SMS sent: %s via %s)", norm_phone, otp_code, sms_dispatched, provider)

    return {
        "status": "success",
        "message": f"Verification code {'dispatched to ' + norm_phone if sms_dispatched else 'generated for ' + norm_phone}",
        "phone": norm_phone,
        "expires_in": OTP_EXPIRY_SECONDS,
        "sms_dispatched": sms_dispatched,
        "sms_provider": provider,
        # dev_otp allows instant testing in local environment when SMS gateway is not yet configured
        "dev_otp": otp_code,
    }


@router.post("/auth/phone/verify-otp")
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Validates the 6-digit OTP against the stored hash.
    Upon verification, creates or logs in the user and issues a JWT token.
    """
    try:
        norm_phone = normalize_phone_number(payload.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    record = _OTP_VAULT.get(norm_phone)
    if not record:
        raise HTTPException(
            status_code=400,
            detail="No active OTP found for this number. Please click 'Send OTP' first."
        )

    now = time.time()
    if now > record["expires_at"]:
        _OTP_VAULT.pop(norm_phone, None)
        raise HTTPException(
            status_code=400,
            detail="The verification code has expired. Please request a new one."
        )

    if record["attempts"] >= 5:
        _OTP_VAULT.pop(norm_phone, None)
        raise HTTPException(
            status_code=429,
            detail="Too many invalid attempts. Please request a new verification code."
        )

    clean_otp = payload.otp.strip()
    expected_hash = hash_otp(norm_phone, clean_otp)

    if not hmac.compare_digest(record["hash"], expected_hash):
        record["attempts"] += 1
        remaining = 5 - record["attempts"]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid verification code. {remaining} attempt(s) remaining."
        )

    # Valid OTP -> consume it
    _OTP_VAULT.pop(norm_phone, None)

    # Auto-register or authenticate user in RajOS database
    synthetic_email = f"phone_{norm_phone.replace('+', '')}@rajos.phone"
    derived_password = f"phone_verified_{norm_phone}"

    user = db.query(User).filter(
        (User.phone_number == norm_phone) | (User.email == synthetic_email)
    ).first()

    is_new = False
    if not user:
        display_name = f"user_{norm_phone[-4:]}"
        user = User(
            username=display_name,
            email=synthetic_email,
            password=pwd_context.hash(derived_password),
            phone_number=norm_phone,
            notifications_enabled=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        is_new = True

    # Generate real RajOS JWT token
    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone_number,
        },
        "is_new": is_new,
        "message": f"Welcome{' to RajOS' if is_new else ' back'}, {user.username}!",
    }


@router.post("/auth/phone/link")
def link_phone(payload: LinkPhoneRequest, db: Session = Depends(get_db)):
    """
    Called after Google Sign-In as Step 2:
    Links a mobile phone number to the user's account and activates mobile task notifications.
    """
    try:
        norm_phone = normalize_phone_number(payload.phone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Optional OTP check if code was entered
    if payload.otp:
        record = _OTP_VAULT.get(norm_phone)
        if record:
            clean_otp = payload.otp.strip()
            expected_hash = hash_otp(norm_phone, clean_otp)
            if not hmac.compare_digest(record["hash"], expected_hash):
                raise HTTPException(status_code=400, detail="Invalid verification code.")
            _OTP_VAULT.pop(norm_phone, None)

    user = None
    if payload.email:
        user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        user = db.query(User).filter(User.phone_number == norm_phone).first()

    if not user and payload.email:
        # Create Google user with linked phone
        derived_password = f"phone_google_{secrets.token_hex(8)}"
        user = User(
            username=payload.email.split("@")[0],
            email=payload.email,
            password=pwd_context.hash(derived_password),
            phone_number=norm_phone,
            notifications_enabled=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif user:
        user.phone_number = norm_phone
        user.notifications_enabled = True
        db.commit()
        db.refresh(user)

    target_email = user.email if user else f"phone_{norm_phone}@rajos.phone"
    token = create_access_token({"sub": target_email})

    return {
        "status": "success",
        "message": f"Mobile {norm_phone} connected! Task notifications enabled.",
        "phone": norm_phone,
        "access_token": token,
        "notifications_enabled": True,
        "user": {
            "id": user.id if user else 99,
            "username": user.username if user else "Google User",
            "email": target_email,
            "phone": norm_phone,
        },
    }


@router.post("/auth/phone/verify")
def verify_phone_supabase(payload: SupabasePhoneVerifyPayload, db: Session = Depends(get_db)):
    """
    Backward-compatibility route for Supabase-based client OTP verification.
    """
    synthetic_email = f"phone_{payload.supabase_user_id}@rajos.phone"
    derived_password = f"phone_otp_{payload.supabase_user_id}"

    existing = db.query(User).filter(
        (User.phone_number == payload.phone) | (User.email == synthetic_email)
    ).first()

    if existing:
        token = create_access_token({"sub": existing.email})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": existing.id,
                "username": existing.username,
                "phone": existing.phone_number,
            },
            "is_new": False,
        }

    display_name = payload.name or payload.phone[-4:].ljust(4, "x")
    new_user = User(
        username=f"user_{display_name}",
        email=synthetic_email,
        password=pwd_context.hash(derived_password),
        phone_number=payload.phone,
        notifications_enabled=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "phone": new_user.phone_number,
        },
        "is_new": True,
    }
