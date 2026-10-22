
import hashlib
from datetime import datetime

import razorpay
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.database import get_db
from app.models.customer_session import CustomerSession
from app.models.payment import Payment
from app.models.print_job import PrintJob

router = APIRouter(
    prefix="/customer-payments",
    tags=["Customer Payments"],
)


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


def get_customer_session(
    session_id: int,
    token: str,
    db: Session,
):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    session = db.query(CustomerSession).filter(
        CustomerSession.id == session_id,
        CustomerSession.token_hash == token_hash,
        CustomerSession.status == "ACTIVE",
        CustomerSession.expires_at > datetime.utcnow(),
    ).first()

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired customer session",
        )

    return session


def get_razorpay_client():
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(
            status_code=503,
            detail="Razorpay credentials are not configured",
        )

    return razorpay.Client(
        auth=(
            settings.razorpay_key_id,
            settings.razorpay_key_secret,
        )
    )


@router.post("/{session_id}/create-order/{job_id}")
def create_customer_order(
    session_id: int,
    job_id: str,
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
):
    session = get_customer_session(session_id, x_session_token, db)

    job = db.query(PrintJob).filter(
        PrintJob.job_id == job_id,
        PrintJob.customer_session_id == session.id,
        PrintJob.kiosk_id == session.kiosk_id,
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")

    if job.status != "PENDING":
        raise HTTPException(
            status_code=409,
            detail=f"Job cannot be paid in status {job.status}",
        )

    if float(job.amount) <= 0:
        raise HTTPException(status_code=400, detail="Invalid job amount")

    payment = db.query(Payment).filter(
        Payment.print_job_id == job.id
    ).first()

    if payment and payment.status == "paid":
        raise HTTPException(status_code=409, detail="Job is already paid")

    client = get_razorpay_client()

    # Reuse an existing order to avoid creating duplicates on retries.
    if payment and payment.provider_order_id:
        return {
            "payment_id": payment.payment_id,
            "razorpay_order_id": payment.provider_order_id,
            "amount": float(payment.amount),
            "currency": "INR",
            "key_id": settings.razorpay_key_id,
            "job_id": job.job_id,
        }

    if not payment:
        payment = Payment(
            payment_id=f"PAY-{job.job_id}",
            print_job_id=job.id,
            provider="razorpay",
            status="created",
            amount=float(job.amount),
        )
        db.add(payment)
        try:
            db.flush()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Could not create payment record; retry safely",
            )

    try:
        order = client.order.create({
            "amount": int(round(float(job.amount) * 100)),
            "currency": "INR",
            "receipt": payment.payment_id,
            "notes": {
                "job_id": job.job_id,
                "customer_session_id": str(session.id),
            },
        })

        payment.provider_order_id = order["id"]
        payment.status = "order_created"
        db.commit()
        db.refresh(payment)

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=502,
            detail="Could not create Razorpay order; check payment status before retrying",
        )

    return {
        "payment_id": payment.payment_id,
        "razorpay_order_id": payment.provider_order_id,
        "amount": float(payment.amount),
        "currency": "INR",
        "key_id": settings.razorpay_key_id,
        "job_id": job.job_id,
    }



@router.post("/{session_id}/verify")
def verify_customer_payment(
    session_id: int,
    data: VerifyPaymentRequest,
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
):
    session = get_customer_session(session_id, x_session_token, db)

    # 1. Find the Razorpay order and confirm it belongs to this session.
    payment = (
        db.query(Payment)
        .join(PrintJob, Payment.print_job_id == PrintJob.id)
        .filter(
            Payment.provider_order_id == data.razorpay_order_id.strip(),
            Payment.provider == "razorpay",
            PrintJob.customer_session_id == session.id,
            PrintJob.kiosk_id == session.kiosk_id,
        )
        .with_for_update()
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail=(
                "Payment order not found for this customer session. "
                "Use the exact razorpay_order_id returned by create-order."
            ),
        )

    job = (
        db.query(PrintJob)
        .filter(PrintJob.id == payment.print_job_id)
        .with_for_update()
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")

    # 2. Make verification retries safe.
    if payment.status == "paid" and job.status in {
        "QUEUED", "PRINTING", "COMPLETED"
    }:
        return {
            "message": "Payment already verified",
            "payment_status": payment.status,
            "job_id": job.job_id,
            "job_status": job.status,
        }

    if payment.status != "order_created":
        raise HTTPException(
            status_code=409,
            detail="Payment is not awaiting verification",
        )

    if job.status != "PENDING":
        raise HTTPException(
            status_code=409,
            detail=f"Job cannot be queued from status {job.status}",
        )

    client = get_razorpay_client()

    # 3. Verify the signature and fetch the payment from Razorpay.
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data.razorpay_order_id,
            "razorpay_payment_id": data.razorpay_payment_id,
            "razorpay_signature": data.razorpay_signature,
        })

        provider_payment = client.payment.fetch(
            data.razorpay_payment_id
        )

    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment signature",
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Could not verify payment with Razorpay; retry verification",
        )

    expected_paise = int(round(float(payment.amount) * 100))

    if (
        provider_payment.get("order_id") != data.razorpay_order_id
        or int(provider_payment.get("amount", -1)) != expected_paise
        or provider_payment.get("currency") != "INR"
    ):
        raise HTTPException(
            status_code=400,
            detail="Payment details do not match the order",
        )

    if provider_payment.get("status") != "captured":
        raise HTTPException(
            status_code=409,
            detail="Payment is not captured yet; check status and retry",
        )

    # 4. Mark payment as paid and release the job to the print queue.
    payment.provider_payment_id = data.razorpay_payment_id
    payment.status = "paid"
    job.status = "QUEUED"

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save verified payment; retry verification",
        )

    return {
        "message": "Payment verified; job added to print queue",
        "payment_status": payment.status,
        "job_id": job.job_id,
        "job_status": job.status,
    }
