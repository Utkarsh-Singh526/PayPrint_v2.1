
import secrets
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.customer_session import CustomerSession
from app.models.document import Document
from app.models.kiosk import Kiosk
from app.models.print_job import PrintJob
from app.models.paper_inventory import PaperInventory
from app.models.kiosk_pricing import KioskPricing

import hashlib

router = APIRouter(
    prefix="/customer-print-jobs",
    tags=["Customer Print Jobs"]
)


class CustomerPrintJobRequest(BaseModel):
    document_id: int
    paper_size: str = "A4"
    print_mode: str = "bw"
    copies: int = Field(default=1, ge=1, le=10)


def validate_session(session_id: int, token: str, db: Session):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    session = db.query(CustomerSession).filter(
        CustomerSession.id == session_id,
        CustomerSession.token_hash == token_hash,
        CustomerSession.status == "ACTIVE",
        CustomerSession.expires_at > datetime.utcnow()
    ).first()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return session


@router.post("/{session_id}")
def create_customer_print_job(
    session_id: int,
    data: CustomerPrintJobRequest,
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db)
):
    session = validate_session(session_id, x_session_token, db)

    paper_size = data.paper_size.upper()
    print_mode = data.print_mode.lower()

    if paper_size not in {"A4", "A3", "LETTER"}:
        raise HTTPException(status_code=400, detail="Unsupported paper size")

    if print_mode not in {"bw", "color"}:
        raise HTTPException(status_code=400, detail="Unsupported print mode")

    document = db.query(Document).filter(
        Document.id == data.document_id,
        Document.customer_session_id == session.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found for this customer session"
        )

    kiosk = db.query(Kiosk).filter(
        Kiosk.id == session.kiosk_id,
        Kiosk.is_active.is_(True)
    ).first()

    if not kiosk:
        raise HTTPException(status_code=400, detail="Kiosk is inactive")

    pricing = db.query(KioskPricing).filter(
        KioskPricing.kiosk_id == kiosk.id,
        KioskPricing.paper_size == paper_size,
        KioskPricing.print_mode == print_mode,
        KioskPricing.is_active.is_(True)
    ).first()

    if not pricing:
        raise HTTPException(
            status_code=400,
            detail="Pricing is not configured for this option"
        )

    total_pages = document.page_count * data.copies
    total_amount = round(float(pricing.price_per_page) * total_pages, 2)

    # Reserve the required sheets atomically to prevent overselling stock.
    reserved = db.execute(
        update(PaperInventory)
        .where(
            PaperInventory.kiosk_id == kiosk.id,
            PaperInventory.stock_sheets - PaperInventory.reserved_sheets >= total_pages
        )
        .values(
            reserved_sheets=PaperInventory.reserved_sheets + total_pages
        )
    )

    if reserved.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Insufficient paper stock or inventory not configured"
        )

    job_id = f"JOB-{uuid.uuid4()}"
    tracking_code = secrets.token_hex(4).upper()

    job = PrintJob(
        job_id=job_id,
        user_id=None,
        kiosk_id=kiosk.id,
        document_id=document.id,
        customer_session_id=session.id,
        tracking_code=tracking_code,
        pages=total_pages,
        amount=total_amount,
        status="PENDING"
    )

    try:
        db.add(job)
        db.commit()
        db.refresh(job)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not create print job")

    return {
        "message": "Print job created; payment is required before printing",
        "job_id": job.job_id,
        "tracking_code": job.tracking_code,
        "document_id": document.id,
        "pages": total_pages,
        "paper_size": paper_size,
        "print_mode": print_mode,
        "copies": data.copies,
        "amount": total_amount,
        "currency": "INR",
        "status": job.status
    }

