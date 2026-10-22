from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.models.kiosk import Kiosk
from app.models.payment import Payment
from app.models.print_job import PrintJob

router = APIRouter(
    prefix="/kiosk-display",
    tags=["Public Kiosk Display"],
)

IST = timezone(timedelta(hours=5, minutes=30))


def get_active_kiosk(kiosk_id: str, db: Session) -> Kiosk:
    kiosk = (
        db.query(Kiosk)
        .filter(
            Kiosk.kiosk_id == kiosk_id.strip(),
            Kiosk.is_active.is_(True),
        )
        .first()
    )

    if not kiosk:
        raise HTTPException(status_code=404, detail="Kiosk not found or inactive")

    return kiosk


@router.get("/{kiosk_id}/summary")
def kiosk_display_summary(
    kiosk_id: str,
    db: Session = Depends(get_db),
):
    kiosk = get_active_kiosk(kiosk_id, db)

    # Database timestamps are stored as naive UTC datetimes.
    local_midnight = datetime.now(IST).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    utc_midnight = local_midnight.astimezone(timezone.utc).replace(tzinfo=None)

    paid_amount = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .join(PrintJob, Payment.print_job_id == PrintJob.id)
        .filter(
            PrintJob.kiosk_id == kiosk.id,
            func.lower(Payment.status) == "paid",
            Payment.created_at >= utc_midnight,
        )
        .scalar()
    )

    paid_pages = (
        db.query(func.coalesce(func.sum(PrintJob.pages), 0))
        .join(Payment, Payment.print_job_id == PrintJob.id)
        .filter(
            PrintJob.kiosk_id == kiosk.id,
            func.lower(Payment.status) == "paid",
            Payment.created_at >= utc_midnight,
        )
        .scalar()
    )

    return {
        "kiosk_id": kiosk.kiosk_id,
        "paid_today": round(float(paid_amount or 0), 2),
        "pages_today": int(paid_pages or 0),
    }


@router.get("/{kiosk_id}/queue")
def kiosk_display_queue(
    kiosk_id: str,
    db: Session = Depends(get_db),
):
    kiosk = get_active_kiosk(kiosk_id, db)

    # Show active paid/queued jobs first; never return storage keys or tokens.
    active_rows = (
        db.query(PrintJob, Document.file_name)
        .join(Document, PrintJob.document_id == Document.id)
        .filter(
            PrintJob.kiosk_id == kiosk.id,
            func.upper(PrintJob.status).in_(["QUEUED", "PRINTING"]),
        )
        .order_by(PrintJob.created_at.asc())
        .limit(12)
        .all()
    )

    rows = list(active_rows)

    # Fill remaining display slots with recently completed jobs.
    remaining = 12 - len(rows)
    if remaining > 0:
        completed_rows = (
            db.query(PrintJob, Document.file_name)
            .join(Document, PrintJob.document_id == Document.id)
            .filter(
                PrintJob.kiosk_id == kiosk.id,
                func.upper(PrintJob.status) == "COMPLETED",
            )
            .order_by(PrintJob.created_at.desc())
            .limit(remaining)
            .all()
        )
        rows.extend(completed_rows)

    jobs = [
        {
            "job_id": job.job_id,
            "file_name": file_name,
            "pages": job.pages,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
        for job, file_name in rows
    ]

    return {"kiosk_id": kiosk.kiosk_id, "jobs": jobs}