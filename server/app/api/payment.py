import razorpay

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.core.settings import settings
from app.db.database import get_db
from app.models.payment import Payment
from app.models.print_job import PrintJob
from app.models.print_job import PrintJob


router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)


class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order/{payment_id}")
def create_razorpay_order(
    payment_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    payment = (
        db.query(Payment)
        .filter(Payment.payment_id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    print_job = (
        db.query(PrintJob)
        .filter(
            PrintJob.id == payment.print_job_id,
            PrintJob.user_id == user_id,
        )
        .first()
    )

    if not print_job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found",
        )

    if payment.provider_payment_id:
        raise HTTPException(
            status_code=400,
            detail="Payment order already created",
        )

    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(
            status_code=500,
            detail="Razorpay credentials are not configured",
        )

    client = razorpay.Client(
        auth=(
            settings.razorpay_key_id,
            settings.razorpay_key_secret,
        )
    )

    amount_paise = int(round(payment.amount * 100))

    try:
        order = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": payment.payment_id,
            }
        )

    except Exception as e:
        print("RAZORPAY ORDER ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Failed to create Razorpay order",
        )

    payment.provider_payment_id = order["id"]
    payment.status = "order_created"

    db.commit()
    db.refresh(payment)

    return {
        "message": "Razorpay order created successfully",
        "payment_id": payment.payment_id,
        "razorpay_order_id": order["id"],
        "amount": payment.amount,
        "amount_paise": amount_paise,
        "currency": "INR",
        "key_id": settings.razorpay_key_id,
        "job_id": print_job.job_id,
    }


@router.post("/verify")
def verify_razorpay_payment(
    data: PaymentVerificationRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    payment = (
        db.query(Payment)
        .join(PrintJob, Payment.print_job_id == PrintJob.id)
        .filter(
            Payment.provider_payment_id == data.razorpay_order_id,
            PrintJob.user_id == user_id,
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment order not found",
        )

    print_job = (
        db.query(PrintJob)
        .filter(
            PrintJob.id == payment.print_job_id,
            PrintJob.user_id == user_id,
        )
        .first()
    )

    if not print_job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found",
        )

    # Idempotency:
    # If this payment was already verified, don't process it again.
    if payment.status == "paid":
        return {
            "message": "Payment already verified",
            "payment_id": payment.payment_id,
            "razorpay_order_id": data.razorpay_order_id,
            "razorpay_payment_id": data.razorpay_payment_id,
            "status": payment.status,
            "job_id": print_job.job_id,
            "job_status": print_job.status,
        }

    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        raise HTTPException(
            status_code=500,
            detail="Razorpay credentials are not configured",
        )

    client = razorpay.Client(
        auth=(
            settings.razorpay_key_id,
            settings.razorpay_key_secret,
        )
    )

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": data.razorpay_order_id,
                "razorpay_payment_id": data.razorpay_payment_id,
                "razorpay_signature": data.razorpay_signature,
            }
        )

    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid Razorpay payment signature",
        )

    except Exception as e:
        print("RAZORPAY VERIFICATION ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Payment verification failed",
        )

    # Signature is valid.
    payment.provider_payment_id = data.razorpay_payment_id
    payment.status = "paid"

    # Automatically queue the job after verified payment.
    print_job.status = "QUEUED"

    db.commit()
    db.refresh(payment)
    db.refresh(print_job)

    return {
        "message": "Payment verified successfully",
        "payment_id": payment.payment_id,
        "razorpay_order_id": data.razorpay_order_id,
        "razorpay_payment_id": data.razorpay_payment_id,
        "status": payment.status,
        "job_id": print_job.job_id,
        "job_status": print_job.status,
    }