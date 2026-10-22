import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.models.document import Document
from app.models.kiosk import Kiosk
from app.models.print_job import PrintJob
from app.models.paper_inventory import PaperInventory
from app.models.kiosk_pricing import KioskPricing


router = APIRouter(
    prefix="/print-jobs",
    tags=["Print Jobs"],
)


@router.post("/create")
def create_print_job(
    document_id: int,
    kiosk_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # 1. Verify that the document belongs to this user.
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == user_id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # 2. Verify that the kiosk is active.
    kiosk = (
        db.query(Kiosk)
        .filter(
            Kiosk.kiosk_id == kiosk_id,
            Kiosk.is_active.is_(True),
        )
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found or inactive",
        )

    # 3. Validate the document page count.
    pages = document.page_count

    if pages is None or pages <= 0:
        raise HTTPException(
            status_code=400,
            detail="Document page count is invalid",
        )

    # Current default print configuration: A4, black and white.
    paper_size = "A4"
    print_mode = "bw"

    # 4. Get the configured price for this kiosk.
    pricing = (
        db.query(KioskPricing)
        .filter(
            KioskPricing.kiosk_id == kiosk.id,
            KioskPricing.paper_size == paper_size,
            KioskPricing.print_mode == print_mode,
            KioskPricing.is_active.is_(True),
        )
        .first()
    )

    if not pricing:
        raise HTTPException(
            status_code=409,
            detail="Pricing is not configured for this kiosk",
        )

    price_per_page = float(pricing.price_per_page)
    amount = round(pages * price_per_page, 2)

    # 5. Reserve stock atomically.
    # Available stock = stock_sheets - reserved_sheets.
    # The conditional update prevents overselling stock.
    try:
        reserved = (
            db.query(PaperInventory)
            .filter(
                PaperInventory.kiosk_id == kiosk.id,
                (
                    PaperInventory.stock_sheets
                    - PaperInventory.reserved_sheets
                ) >= pages,
            )
            .update(
                {
                    PaperInventory.reserved_sheets:
                        PaperInventory.reserved_sheets + pages
                },
                synchronize_session=False,
            )
        )

        if reserved != 1:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail=(
                    "Insufficient paper stock or inventory "
                    "is not configured for this kiosk"
                ),
            )

        # 6. Create the print job after stock is reserved.
        job_id = f"JOB-{uuid.uuid4()}"

        print_job = PrintJob(
            job_id=job_id,
            user_id=user_id,
            kiosk_id=kiosk.id,
            document_id=document.id,
            pages=pages,
            amount=amount,
            status="PENDING",
        )

        db.add(print_job)
        db.commit()
        db.refresh(print_job)

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not reserve stock or create print job",
        )

    return {
        "message": "Print job created and paper stock reserved",
        "job_id": print_job.job_id,
        "document_id": document.id,
        "file_name": document.file_name,
        "pages": pages,
        "paper_size": paper_size,
        "print_mode": print_mode,
        "price_per_page": price_per_page,
        "amount": amount,
        "status": print_job.status,
        "kiosk_id": kiosk.kiosk_id,
        "reserved_sheets": pages,
    }