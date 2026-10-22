import jwt

from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.settings import settings


# Password hashing
password_hasher = PasswordHasher()

# Bearer token authentication
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        password_hasher.verify(password_hash, password)
        return True
    except Exception:
        return False


# ---------------------------------------------------------
# USER JWT
# ---------------------------------------------------------

def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_roles(*allowed_roles: str):

    def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    ) -> int:

        token = credentials.credentials

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=["HS256"],
            )

            user_id = payload.get("sub")
            role = payload.get("role")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                )

            if role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            return int(user_id)

        except (jwt.InvalidTokenError, ValueError):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

    return role_checker


# ---------------------------------------------------------
# KIOSK JWT
# ---------------------------------------------------------

def create_kiosk_access_token(kiosk_id: str) -> str:

    expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "type": "kiosk",
        "kiosk_id": kiosk_id,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )


def get_current_kiosk(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )

        token_type = payload.get("type")
        kiosk_id = payload.get("kiosk_id")

        if token_type != "kiosk" or kiosk_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid kiosk token",
            )

        return kiosk_id

    except (jwt.InvalidTokenError, ValueError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired kiosk token",
        )