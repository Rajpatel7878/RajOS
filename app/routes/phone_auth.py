"""Phone OTP Authentication & Mobile Task Notification Engine for RajOS.

Supports:
1. /auth/phone/send-otp: Generates secure 6-digit cryptographic OTP, hashes with secret salt,
   dispatches SMS via Twilio or Fast2SMS if configured, or provides dev_otp for local testing.
2. /auth/phone/verify-otp: Verifies OTP against cryptographic hash with expiry & attempt limits,
   auto-creates or logs in the user, and issues a standard RajOS JWT.
3. /auth/phone/link: Links a verified phone number to an account (e.g. after Google Sign-In)
   and enables task mobile push/SMS notifications.
4. /auth/phone/verify: Supabase backward compatibility endpoint.
5. /webhooks/twilio/voice: Outbound call TwiML instructions (POST).
6. /webhooks/twilio/status: Call status update receiver (POST).
"""

import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Form, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.base.exceptions import TwilioRestException

from app.database.connection import get_db
from app.models.user import User
from app.models.phone_call import PhoneCall
from app.security.jwt import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()

# ── OTP Constants ──────────────────────────────────────────────────────────────

OTP_SALT = os.getenv("SECRET_KEY", "rajos_otp_secure_salt_7878")
OTP_EXPIRY_SECONDS = 300
MIN_RESEND_INTERVAL = 15

# ── OTP Vault ─────────────────────────────────────────────────────────────────

_OTP_VAULT: dict[str, dict] = {}


def normalize_phone_number(raw: str) -> str:
    cleaned = re.sub(r"[^\d+]", "", raw.strip())
    if not cleaned:
        raise ValueError("Phone number cannot be empty")
    if cleaned.startswith("+"):
        digits = cleaned[1:]
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError("Invalid phone number length")
        return cleaned
    if cleaned.startswith("0"):
        cleaned = cleaned[1:]
    if len(cleaned) == 10:
        return f"+91{cleaned}"
    elif len(cleaned) == 12 and cleaned.startswith("91"):
        return f"+{cleaned}"
    elif 10 < len(cleaned) <= 15:
        return f"+{cleaned}"
    else:
        raise ValueError("Please provide a valid 10-digit mobile number")


def hash_otp(phone: str, otp: str) -> str:
    message = f"{phone}:{otp}:{OTP_SALT}".encode("utf-8")
    return hmac.new(OTP_SALT.encode("utf-8"), message, hashlib.sha256).hexdigest()


# ── SMS Gateways ──────────────────────────────────────────────────────────────

def send_sms_via_twilio(phone: str, otp: str) -> bool:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    if not (account_sid and auth_token and from_number):
        return False
    try:
        client = TwilioClient(account_sid, auth_token)
        message = client.messages.create(
            body=f"Your RajOS verification code is: {otp}. Valid for 5 minutes.",
            from_=from_number,
            to=phone,
        )
        logger.info("Twilio SMS sent to %s, sid=%s", phone, message.sid)
        return True
    except Exception as exc:
        logger.warning("Twilio SMS failed: %s", exc)
    return False


def send_sms_via_fast2sms(phone: str, otp: str) -> bool:
    api_key = os.getenv("FAST2SMS_API_KEY")
    if not api_key:
        return False
    try:
        import urllib.request
        digits = re.sub(r"[^\d]", "", phone)
        if digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = json.dumps({"variables_values": otp, "route": "otp", "numbers": digits}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("authorization", api_key)
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if res_data.get("return") is True:
                logger.info("Fast2SMS OTP sent to %s", phone)
                return True
    except Exception as exc:
        logger.warning("Fast2SMS failed: %s", exc)
    return False


def dispatch_sms(phone: str, otp: str) -> tuple[bool, str]:
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


# ── Twilio Configuration Helpers ─────────────────────────────────────────────

def _get_twilio_creds():
    return os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"), os.getenv("TWILIO_PHONE_NUMBER")

def _is_india_number(phone: str) -> bool:
    return re.match(r"^\+91\d{10}$", phone) is not None

def _normalize_for_twilio(phone: str) -> str:
    if not phone.startswith("+"):
        return f"+{phone}"
    return phone


# ── Twilio Signature Validation ───────────────────────────────────────────────

def _validate_twilio_signature(request: Request, url: str, signature: str) -> bool:
    account_sid, _, _ = _get_twilio_creds()
    if not account_sid:
        logger.error("Twilio credentials not configured; cannot validate signature")
        return False
    try:
        validator = TwilioRequest(account_sid, os.getenv("TWILIO_AUTH_TOKEN", ""))
        is_valid = validator.validate(request.body(), url, signature)
        if not is_valid:
            logger.warning("Twilio signature validation failed for %s", request.url)
        return is_valid
    except TwilioRestException:
        logger.warning("Twilio signature validation exception for %s", request.url)
        return False
    except Exception as exc:
        logger.error("Unexpected error during Twilio signature validation: %s", exc)
        return False


# ── Idempotency Helper ───────────────────────────────────────────────────────

_call_records: dict[str, datetime] = {}

def _is_duplicate_call_sid(call_sid: str, min_interval_seconds: int = 30) -> bool:
    last = _call_records.get(call_sid)
    if last is None:
        return False
    elapsed = (datetime.utcnow() - last).total_seconds()
    return elapsed < min_interval_seconds

def _touch_call_sid(call_sid: str) -> None:
    _call_records[call_sid] = datetime.utcnow()


# ── India Calling Restrictions Helper ─────────────────────────────────────────

_india_restriction_reported: bool = False

def _check_india_restrictions(recipient_phone: str) -> tuple[bool, str]:
    global _india_restriction_reported
    account_sid, auth_token, from_number = _get_twilio_creds()
    if not from_number:
        return True, ""
    is_india = _is_india_number(recipient_phone)
    if not is_india:
        return True, ""
    from_is_india = _is_india_number(from_number)
    from_is_us_or_international = not from_is_india
    if from_is_india and from_is_india:
        return True, ""
    if from_is_india and not is_india:
        return True, ""
    if not from_is_india and is_india:
        if not auth_token:
            return False, "Twilio auth token not configured"
        if not _india_restriction_reported:
            logger.warning(
                "India calling: non-India caller ID (%s) to India number (%s)" % (from_number, recipient_phone),
            )
