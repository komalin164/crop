"""In-memory OTP store with expiry. For production, use Redis."""
import random
import string
from datetime import datetime, timedelta
from typing import Optional

_otp_store: dict[str, tuple[str, datetime]] = {}
OTP_EXPIRE_MINUTES = 5
OTP_LENGTH = 6


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=OTP_LENGTH))


def store_otp(email: str) -> str:
    email = email.strip().lower()
    otp = generate_otp()
    _otp_store[email] = (otp, datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES))
    return otp


def verify_otp(email: str, otp: str) -> bool:
    email = email.strip().lower()
    if email not in _otp_store:
        return False
    stored_otp, expiry = _otp_store[email]
    if datetime.utcnow() > expiry:
        del _otp_store[email]
        return False
    if stored_otp != otp.strip():
        return False
    del _otp_store[email]
    return True
