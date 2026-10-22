
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.database import get_db
from app.models.user import User
from app.models.kiosk import Kiosk
from app.models.admin_kiosk_assignment import AdminKioskAssignment


bearer_scheme = HTTPBearer()

ADMIN_ROLES = {"ADMIN", "REGULAR_ADMIN", "SUPER_ADMIN"}


def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate token and current user status/role from the database."""

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
        user_id = int(payload.get("sub"))
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is missing or inactive",
        )

    if user.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user


def require_super_admin(
    current_admin: User = Depends(get_current_admin_user),
) -> User:
    """Allow only a currently active Super Admin."""

    if current_admin.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required",
        )

    return current_admin


def ensure_kiosk_access(
    db: Session,
    current_admin: User,
    kiosk: Kiosk,
) -> None:
    """Super Admin can access every kiosk; other admins need an assignment."""

    if current_admin.role == "SUPER_ADMIN":
        return

    assignment = (
        db.query(AdminKioskAssignment)
        .filter(
            AdminKioskAssignment.user_id == current_admin.id,
            AdminKioskAssignment.kiosk_id == kiosk.id,
        )
        .first()
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this kiosk",
        )
