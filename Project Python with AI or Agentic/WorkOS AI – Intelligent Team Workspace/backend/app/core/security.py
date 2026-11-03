from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import hashlib
import hmac
import json
import base64
from app.core.config import settings

# Attempt passlib bcrypt, fallback to hashlib SHA-256 with salt if passlib is missing
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    HAS_PASSLIB = True
except Exception:
    HAS_PASSLIB = False
    pwd_context = None

# Attempt python-jose, fallback to manual HMAC-SHA256 JWT if missing
try:
    from jose import jwt
    HAS_JOSE = True
except Exception:
    HAS_JOSE = False
    jwt = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored hash."""
    if HAS_PASSLIB and pwd_context and hashed_password.startswith("$2"):
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass

    # Fallback salted sha256 verification
    if ":" in hashed_password:
        salt, stored_hash = hashed_password.split(":", 1)
        check = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
        return hmac.compare_digest(check, stored_hash)

    # Simple sha256 match
    check = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(check, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash from a plain password."""
    if HAS_PASSLIB and pwd_context:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass

    # Resilient salted sha256 fallback
    salt = "workos_salt_"
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{h}"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed JWT access token for authentication."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": int(expire.timestamp()),
        "sub": str(subject),
        "type": "access"
    }

    if HAS_JOSE and jwt:
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Standard fallback HMAC-SHA256 JWT
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = _b64url_encode(json.dumps(header).encode('utf-8'))
    p_b64 = _b64url_encode(json.dumps(to_encode).encode('utf-8'))
    signing_input = f"{h_b64}.{p_b64}".encode('utf-8')
    sig = hmac.new(settings.JWT_SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    s_b64 = _b64url_encode(sig)
    return f"{h_b64}.{p_b64}.{s_b64}"


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed JWT refresh token with longer expiration."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode = {
        "exp": int(expire.timestamp()),
        "sub": str(subject),
        "type": "refresh"
    }

    if HAS_JOSE and jwt:
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = _b64url_encode(json.dumps(header).encode('utf-8'))
    p_b64 = _b64url_encode(json.dumps(to_encode).encode('utf-8'))
    signing_input = f"{h_b64}.{p_b64}".encode('utf-8')
    sig = hmac.new(settings.JWT_SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    s_b64 = _b64url_encode(sig)
    return f"{h_b64}.{p_b64}.{s_b64}"


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token payload."""
    if HAS_JOSE and jwt:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    # Fallback HMAC-SHA256 decode
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("Invalid token structure")
    h_b64, p_b64, s_b64 = parts
    signing_input = f"{h_b64}.{p_b64}".encode('utf-8')
    sig = hmac.new(settings.JWT_SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url_encode(sig), s_b64):
        raise ValueError("Signature verification failed")
    payload = json.loads(_b64url_decode(p_b64).decode('utf-8'))
    exp = payload.get("exp")
    if exp and datetime.now(timezone.utc).timestamp() > exp:
        raise ValueError("Token has expired")
    return payload
