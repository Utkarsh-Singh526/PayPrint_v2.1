
import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.customer_session import CustomerSession
from app.models.kiosk import Kiosk

router = APIRouter(
    prefix="/customer-sessions",
    tags=["Customer Sessions"],
)


class CustomerSessionRequest(BaseModel):
    kiosk_id: str = Field(min_length=1, max_length=100)
    customer_name: str = Field(min_length=1, max_length=100)


@router.post("/start")
def start_customer_session(
    data: CustomerSessionRequest,
    db: Session = Depends(get_db),
):
    name = data.customer_name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Customer name is required",
        )

    kiosk = (
        db.query(Kiosk)
        .filter(
            Kiosk.kiosk_id == data.kiosk_id,
            Kiosk.is_active.is_(True),
        )
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found or inactive",
        )

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    session = CustomerSession(
        kiosk_id=kiosk.id,
        customer_name=name,
        token_hash=token_hash,
        status="ACTIVE",
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    try:
        db.add(session)
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not create customer session",
        )

    return {
        "message": "Customer session created",
        "session_id": session.id,
        "customer_name": session.customer_name,
        "kiosk_id": kiosk.kiosk_id,
        "session_token": token,
        "expires_at": session.expires_at,
    }
