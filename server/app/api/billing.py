from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.models.print_job import PrintJob
from app.models.payment import Payment


router = APIRouter(
    prefix="/billing",
    tags=["Billing"],
)


@router.post("/create/{job_id}")
def create_bill(
    job_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # 1. Find print job belonging to current user
    print_job = (
        db.query(PrintJob)
        .filter(
            PrintJob.job_id == job_id,
            PrintJob.user_id == user_id,
        )
        .first()
    )

    if not print_job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found",
        )

    # 2. Only pending jobs can be billed
    if print_job.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create bill for job with status {print_job.status}",
        )

    # 3. Check if payment already exists
    existing_payment = (
        db.query(Payment)
        .filter(Payment.print_job_id == print_job.id)
        .first()
    )

    if existing_payment:
        return {
            "message": "Bill already exists",
            "job_id": print_job.job_id,
            "payment_id": existing_payment.payment_id,
            "amount": existing_payment.amount,
            "status": existing_payment.status,
        }

    # 4. Server-authoritative amount
    amount = Decimal(str(print_job.amount))

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid bill amount",
        )

    # 5. Create internal payment record
    payment_id = f"PAY-{print_job.job_id}"

    payment = Payment(
        payment_id=payment_id,
        print_job_id=print_job.id,
        provider="razorpay",
        status="created",
        amount=float(amount),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Bill created successfully",
        "job_id": print_job.job_id,
        "payment_id": payment.payment_id,
        "amount": float(amount),
        "currency": "INR",
        "pages": print_job.pages,
        "status": print_job.status,
        "payment_status": payment.status,
    }