import secrets

from fastapi import APIRouter, Depends, HTTPException
from app.core.admin_access import require_super_admin
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_kiosk_access_token,
    get_current_kiosk,
)
from app.db.database import get_db
from app.models.kiosk import Kiosk

from datetime import datetime, timezone

router = APIRouter(
    prefix="/kiosk",
    tags=["Kiosk Authentication"],
)


@router.post("/register")
def register_kiosk(
    kiosk_id: str,
    name: str,
    location: str | None = None,
    db: Session = Depends(get_db),
    admin = Depends(require_super_admin),
):
    existing_kiosk = (
        db.query(Kiosk)
        .filter(Kiosk.kiosk_id == kiosk_id)
        .first()
    )

    if existing_kiosk:
        raise HTTPException(
            status_code=409,
            detail="Kiosk ID already exists",
        )

    kiosk_secret = secrets.token_urlsafe(32)

    kiosk = Kiosk(
        kiosk_id=kiosk_id,
        name=name,
        location=location,
        secret_hash=hash_password(kiosk_secret),
        is_active=True,
    )

    db.add(kiosk)
    db.commit()
    db.refresh(kiosk)

    return {
        "message": "Kiosk registered successfully",
        "kiosk_id": kiosk.kiosk_id,
        "name": kiosk.name,
        "location": kiosk.location,
        "kiosk_secret": kiosk_secret,
    }


@router.post("/login")
def kiosk_login(
    kiosk_id: str,
    kiosk_secret: str,
    db: Session = Depends(get_db),
):
    kiosk = (
        db.query(Kiosk)
        .filter(Kiosk.kiosk_id == kiosk_id)
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=401,
            detail="Invalid kiosk credentials",
        )

    if not kiosk.is_active:
        raise HTTPException(
            status_code=403,
            detail="Kiosk is inactive",
        )

    if not verify_password(
        kiosk_secret,
        kiosk.secret_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid kiosk credentials",
        )

    access_token = create_kiosk_access_token(
        kiosk.kiosk_id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "kiosk_id": kiosk.kiosk_id,
    }
@router.get("/me")
def kiosk_me(
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
    kiosk = (
        db.query(Kiosk)
        .filter(Kiosk.kiosk_id == kiosk_id)
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found",
        )

    if not kiosk.is_active:
        raise HTTPException(
            status_code=403,
            detail="Kiosk is inactive",
        )

    return {
        "kiosk_id": kiosk.kiosk_id,
        "name": kiosk.name,
        "location": kiosk.location,
        "is_active": kiosk.is_active,
    }

@router.post("/reset-secret")
def reset_kiosk_secret(
    kiosk_id: str,
    db: Session = Depends(get_db),
    admin = Depends(require_super_admin),
):
    kiosk = (
        db.query(Kiosk)
        .filter(Kiosk.kiosk_id == kiosk_id)
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found",
        )

    new_secret = secrets.token_urlsafe(32)

    kiosk.secret_hash = hash_password(new_secret)

    db.commit()


    return {
        "message": "Kiosk secret reset successfully",
        "kiosk_id": kiosk.kiosk_id,
        "new_kiosk_secret": new_secret,
    }

@router.post("/heartbeat")
def kiosk_heartbeat(
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
    kiosk = (
        db.query(Kiosk)
        .filter(Kiosk.kiosk_id == kiosk_id)
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found",
        )

    if not kiosk.is_active:
        raise HTTPException(
            status_code=403,
            detail="Kiosk is inactive",
        )

    kiosk.last_seen = datetime.now(timezone.utc)

    db.commit()
    db.refresh(kiosk)

    return {
        "message": "Heartbeat received",
        "kiosk_id": kiosk.kiosk_id,
        "status": "online",
        "last_seen": kiosk.last_seen,
    }
@router.get("/status")
def kiosk_status(
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
    kiosk = (
        db.query(Kiosk)
        .filter(Kiosk.kiosk_id == kiosk_id)
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found",
        )

    if not kiosk.is_active:
        return {
            "kiosk_id": kiosk.kiosk_id,
            "name": kiosk.name,
            "location": kiosk.location,
            "status": "inactive",
            "is_active": kiosk.is_active,
            "last_seen": kiosk.last_seen,
        }

    if kiosk.last_seen is None:
        status_value = "offline"

    else:
        now = datetime.utcnow()

        time_difference = now - kiosk.last_seen

        if time_difference.total_seconds() <= 120:
            status_value = "online"
        else:
            status_value = "offline"

    return {
        "kiosk_id": kiosk.kiosk_id,
        "name": kiosk.name,
        "location": kiosk.location,
        "status": status_value,
        "is_active": kiosk.is_active,
        "last_seen": kiosk.last_seen,
    }
