from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.database import get_db
from app.models.kiosk import Kiosk
from app.models.payment import Payment
from app.models.print_job import PrintJob
from app.models.user import User


router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Super Admin Dashboard"],
)

bearer_scheme = HTTPBearer()


def require_super_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> int:
    """Verify the JWT and the user's current database role."""

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
        user_id = int(payload.get("sub"))
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User is missing or inactive",
        )

    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Super Admin access required",
        )

    return user.id


@router.get("/overview")
def get_dashboard_overview(
    admin_id: int = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    """Return dashboard metrics from the existing database."""

    now = datetime.utcnow()
    today_start = now.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    online_cutoff = now - timedelta(minutes=5)

    total_jobs = db.query(func.count(PrintJob.id)).scalar() or 0

    jobs_today = (
        db.query(func.count(PrintJob.id))
        .filter(PrintJob.created_at >= today_start)
        .scalar()
        or 0
    )

    total_revenue = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status == "paid")
        .scalar()
        or 0
    )

    revenue_today = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(
            Payment.status == "paid",
            Payment.created_at >= today_start,
        )
        .scalar()
        or 0
    )

    paid_payments = (
        db.query(func.count(Payment.id))
        .filter(Payment.status == "paid")
        .scalar()
        or 0
    )

    pending_jobs = (
        db.query(func.count(PrintJob.id))
        .filter(PrintJob.status == "PENDING")
        .scalar()
        or 0
    )

    queued_jobs = (
        db.query(func.count(PrintJob.id))
        .filter(PrintJob.status == "QUEUED")
        .scalar()
        or 0
    )

    printing_jobs = (
        db.query(func.count(PrintJob.id))
        .filter(PrintJob.status == "PRINTING")
        .scalar()
        or 0
    )

    completed_jobs = (
        db.query(func.count(PrintJob.id))
        .filter(PrintJob.status == "COMPLETED")
        .scalar()
        or 0
    )

    failed_jobs = (
        db.query(func.count(PrintJob.id))
        .filter(
            PrintJob.status.in_(
                ["FAILED", "PRINT_FAILED", "ERROR"]
            )
        )
        .scalar()
        or 0
    )

    total_kiosks = db.query(func.count(Kiosk.id)).scalar() or 0

    active_kiosks = (
        db.query(func.count(Kiosk.id))
        .filter(Kiosk.is_active.is_(True))
        .scalar()
        or 0
    )

    online_kiosks = (
        db.query(func.count(Kiosk.id))
        .filter(
            Kiosk.is_active.is_(True),
            Kiosk.last_seen >= online_cutoff,
        )
        .scalar()
        or 0
    )

    total_users = db.query(func.count(User.id)).scalar() or 0

    # Recent jobs include kiosk and payment information, not document contents.
    recent_rows = (
        db.query(PrintJob, Kiosk.name, Payment.status)
        .outerjoin(Kiosk, PrintJob.kiosk_id == Kiosk.id)
        .outerjoin(Payment, Payment.print_job_id == PrintJob.id)
        .order_by(PrintJob.created_at.desc())
        .limit(10)
        .all()
    )

    recent_jobs = []

    for job, kiosk_name, payment_status in recent_rows:
        recent_jobs.append({
            "job_id": job.job_id,
            "status": job.status,
            "pages": job.pages,
            "amount": float(job.amount or 0),
            "created_at": (
                job.created_at.isoformat()
                if job.created_at else None
            ),
            "kiosk_name": kiosk_name,
            "payment_status": payment_status,
        })

    status_rows = (
        db.query(PrintJob.status, func.count(PrintJob.id))
        .group_by(PrintJob.status)
        .all()
    )

    return {
        "generated_at": now.isoformat() + "Z",
        "metrics": {
            "total_jobs": total_jobs,
            "jobs_today": jobs_today,
            "total_revenue_inr": round(float(total_revenue), 2),
            "revenue_today_inr": round(float(revenue_today), 2),
            "paid_payments": paid_payments,
            "pending_jobs": pending_jobs,
            "queued_jobs": queued_jobs,
            "printing_jobs": printing_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "total_kiosks": total_kiosks,
            "active_kiosks": active_kiosks,
            "online_kiosks": online_kiosks,
            "total_users": total_users,
        },
        "job_status_breakdown": [
            {"status": status, "count": count}
            for status, count in status_rows
        ],
        "recent_jobs": recent_jobs,
    }
