"""Auth: email OTP only. No mobile, no password login."""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
import aiosqlite

from config import SECRET_KEY, DB_PATH
from email_service import send_otp_email
from otp_store import store_otp, verify_otp

ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
OTP_USER_PASSWORD = "otp_user_no_password"  # Placeholder for OTP-only users


def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def _hash_password(s: str) -> str:
    import bcrypt
    b = s.encode("utf-8")[:72]
    return bcrypt.hashpw(b, bcrypt.gensalt()).decode("utf-8")


async def send_otp(email: str, name: str = "") -> dict:
    """Send OTP to email. Returns {sent: bool, message: str}."""
    email = (email or "").strip().lower()
    if not email or "@" not in email:
        return {"sent": False, "message": "Invalid email"}
    otp = store_otp(email)
    ok = send_otp_email(email, otp, name=(name or "").strip())
    if ok:
        return {"sent": True, "message": "OTP sent to your email"}
    return {"sent": False, "message": "Failed to send email. Check mail configuration."}


async def verify_otp_and_register(
    email: str, otp: str, name: str = "", mobile: str = ""
) -> Optional[dict]:
    """Verify OTP and create/return user. Returns user dict or None."""
    email = (email or "").strip().lower()
    if not email or not otp:
        return None
    if not verify_otp(email, otp):
        return None
    name = (name or "").strip() or None
    mobile = (mobile or "").strip() or None
    conn = await aiosqlite.connect(DB_PATH)
    try:
        cur = await conn.execute(
            "SELECT id, email, name, mobile FROM users WHERE email = ?", (email,)
        )
        row = await cur.fetchone()
        if row:
            return {"id": row[0], "email": row[1], "name": row[2], "mobile": row[3]}
        await conn.execute(
            "INSERT INTO users (email, mobile, name, password_hash) VALUES (?, ?, ?, ?)",
            (email, mobile, name, _hash_password(OTP_USER_PASSWORD)),
        )
        await conn.commit()
        cur = await conn.execute(
            "SELECT id, email, name, mobile FROM users WHERE id = last_insert_rowid()"
        )
        row = await cur.fetchone()
        return {"id": row[0], "email": row[1], "name": row[2], "mobile": row[3]}
    finally:
        await conn.close()
