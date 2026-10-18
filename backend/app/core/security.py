import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str | uuid.UUID) -> str:
    sub = str(subject)
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_ttl_minutes)
    return jwt.encode(
        {"sub": sub, "exp": exp, "type": "access"},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str | uuid.UUID) -> str:
    sub = str(subject)
    exp = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_ttl_days)
    return jwt.encode(
        {"sub": sub, "exp": exp, "type": "refresh"},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
