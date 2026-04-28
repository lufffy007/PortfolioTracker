from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing configuration.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 configuration for future auth flows.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a signed JWT access token for the given subject.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password.
    """
    return pwd_context.hash(password)


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.

    Returns the payload if valid, otherwise `None`.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

