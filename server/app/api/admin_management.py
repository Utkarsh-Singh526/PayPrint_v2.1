
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.admin_access import require_super_admin
from app.core.security import hash_password

from app.db.database import get_db
from app.models.admin_kiosk_assignment import AdminKioskAssignment
from app.models.kiosk import Kiosk
from app.models.user import User


router = APIRouter(
    prefix="/admin/management",
    tags=["Super Admin Management"],
)


class AssignmentCreate(BaseModel):
    user_id: int
    kiosk_id: int

class AdminCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)

@router.post("/admins", status_code=status.HTTP_201_CREATED)
def create_regular_admin(
    data: AdminCreate,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    name = data.name.strip()
    email = data.email.strip().lower()

    if len(name) < 2:
        raise HTTPException(
            status_code=400,
            detail="Name must contain at least 2 characters",
        )

    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise HTTPException(
            status_code=400,
            detail="Invalid email address",
        )

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    new_admin = User(
        name=name,
        email=email,
        password_hash=hash_password(data.password),
        role="REGULAR_ADMIN",
        is_active=True,
    )

    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create admin",
        )

    return {
        "message": "Regular Admin created successfully",
        "admin": {
            "id": new_admin.id,
            "name": new_admin.name,
            "email": new_admin.email,
            "role": new_admin.role,
            "is_active": new_admin.is_active,
        },
    }

@router.get("/admins")
def list_regular_admins(
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    admins = (
        db.query(User)
        .filter(User.role.in_(["ADMIN", "REGULAR_ADMIN"]))
        .order_by(User.id.desc())
        .all()
    )

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        }
        for user in admins
    ]


@router.get("/kiosks")
def list_kiosks(
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    kiosks = db.query(Kiosk).order_by(Kiosk.id.desc()).all()

    return [
        {
            "id": kiosk.id,
            "kiosk_id": kiosk.kiosk_id,
            "name": kiosk.name,
            "location": kiosk.location,
            "is_active": kiosk.is_active,
            "last_seen": (
                kiosk.last_seen.isoformat()
                if kiosk.last_seen else None
            ),
        }
        for kiosk in kiosks
    ]


@router.get("/assignments")
def list_assignments(
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(AdminKioskAssignment, User, Kiosk)
        .join(User, User.id == AdminKioskAssignment.user_id)
        .join(Kiosk, Kiosk.id == AdminKioskAssignment.kiosk_id)
        .order_by(AdminKioskAssignment.id.desc())
        .all()
    )

    return [
        {
            "id": assignment.id,
            "user_id": user.id,
            "admin_name": user.name,
            "admin_email": user.email,
            "kiosk_id": kiosk.id,
            "kiosk_code": kiosk.kiosk_id,
            "kiosk_name": kiosk.name,
        }
        for assignment, user, kiosk in rows
    ]


@router.post(
    "/assignments",
    status_code=status.HTTP_201_CREATED,
)
def assign_kiosk(
    data: AssignmentCreate,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == data.user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Admin user not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot assign a kiosk to an inactive admin",
        )

    if user.role not in {"ADMIN", "REGULAR_ADMIN"}:
        raise HTTPException(
            status_code=400,
            detail="Kiosk can only be assigned to a regular admin",
        )

    kiosk = db.query(Kiosk).filter(Kiosk.id == data.kiosk_id).first()

    if kiosk is None:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found",
        )

    existing = (
        db.query(AdminKioskAssignment)
        .filter(
            AdminKioskAssignment.user_id == user.id,
            AdminKioskAssignment.kiosk_id == kiosk.id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="This kiosk is already assigned to this admin",
        )

    assignment = AdminKioskAssignment(
        user_id=user.id,
        kiosk_id=kiosk.id,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": "Kiosk assigned successfully",
        "assignment_id": assignment.id,
        "admin_id": user.id,
        "kiosk_id": kiosk.id,
        "kiosk_code": kiosk.kiosk_id,
    }


@router.delete("/assignments/{assignment_id}")
def remove_assignment(
    assignment_id: int,
    admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    assignment = (
        db.query(AdminKioskAssignment)
        .filter(AdminKioskAssignment.id == assignment_id)
        .first()
    )

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found",
        )

    db.delete(assignment)
    db.commit()

    return {"message": "Kiosk assignment removed successfully"}
