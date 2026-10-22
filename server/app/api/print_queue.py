from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import (
    get_current_kiosk,
    require_roles,
)
from app.db.database import get_db
from app.models.kiosk import Kiosk
from app.models.print_job import PrintJob
from app.models.document import Document
from app.models.paper_inventory import PaperInventory

from pathlib import Path
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/print-queue",
    tags=["Print Queue"],
)


# ---------------------------------------------------------
# 1. ENQUEUE PRINT JOB
# ---------------------------------------------------------

@router.post("/enqueue/{job_id}")
def enqueue_print_job(
    job_id: str,
    user_id: int = Depends(
        require_roles("ADMIN", "SUPER_ADMIN")
    ),
    db: Session = Depends(get_db),
):
    """
    Move a PAID print job into the printing queue.
    Only ADMIN / SUPER_ADMIN can enqueue jobs manually.
    """

    print_job = (
        db.query(PrintJob)
        .filter(PrintJob.job_id == job_id)
        .first()
    )

    if not print_job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found",
        )

    if print_job.status != "PAID":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only PAID jobs can be queued. "
                f"Current status: {print_job.status}"
            ),
        )

    print_job.status = "QUEUED"

    db.commit()
    db.refresh(print_job)

    return {
        "message": "Print job added to queue",
        "job_id": print_job.job_id,
        "status": print_job.status,
        "kiosk_id": print_job.kiosk_id,
    }


# ---------------------------------------------------------
# 2. GET NEXT JOB FOR KIOSK
# ---------------------------------------------------------

@router.get("/next")
def get_next_print_job(
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
    """
    Returns the oldest queued job assigned to this kiosk.
    """

    kiosk = (
        db.query(Kiosk)
        .filter(
            Kiosk.kiosk_id == kiosk_id,
            Kiosk.is_active == True,
        )
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found or inactive",
        )

    print_job = (
        db.query(PrintJob)
        .filter(
            PrintJob.kiosk_id == kiosk.id,
            PrintJob.status == "QUEUED",
        )
        .order_by(PrintJob.created_at.asc())
        .first()
    )

    if not print_job:
        return {
            "message": "No print job available",
            "job": None,
        }

    document = (
        db.query(Document)
        .filter(Document.id == print_job.document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found for print job",
        )

    return {
        "message": "Print job available",
        "job": {
            "job_id": print_job.job_id,
            "document_id": print_job.document_id,
            "file_name": document.file_name,
            "storage_key": document.storage_key,
            "pages": print_job.pages,
            "amount": print_job.amount,
            "status": print_job.status,
            "created_at": print_job.created_at,
        },
    }


# ---------------------------------------------------------
# 3. CLAIM JOB
# ---------------------------------------------------------

@router.post("/{job_id}/claim")
def claim_print_job(
    job_id: str,
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
    """
    Kiosk claims a queued job before printing.
    """

    kiosk = (
        db.query(Kiosk)
        .filter(
            Kiosk.kiosk_id == kiosk_id,
            Kiosk.is_active == True,
        )
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found or inactive",
        )

    print_job = (
        db.query(PrintJob)
        .filter(
            PrintJob.job_id == job_id,
            PrintJob.kiosk_id == kiosk.id,
        )
        .first()
    )

    if not print_job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found for this kiosk",
        )

    if print_job.status != "QUEUED":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Job cannot be claimed. "
                f"Current status: {print_job.status}"
            ),
        )

    print_job.status = "PRINTING"

    db.commit()
    db.refresh(print_job)

    return {
        "message": "Print job claimed",
        "job_id": print_job.job_id,
        "status": print_job.status,
        "kiosk_id": kiosk.kiosk_id,
    }


# ---------------------------------------------------------
# 4. PRINT COMPLETED
# ---------------------------------------------------------

@router.post("/{job_id}/complete")
def complete_print_job(
    job_id: str,
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
    """
    Kiosk reports successful printing.
    """

    kiosk = (
        db.query(Kiosk)
        .filter(
            Kiosk.kiosk_id == kiosk_id,
            Kiosk.is_active == True,
        )
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found or inactive",
        )

    print_job = (
        db.query(PrintJob)
        .filter(
            PrintJob.job_id == job_id,
            PrintJob.kiosk_id == kiosk.id,
        )
        .first()
    )

    if not print_job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found",
        )

    if print_job.status != "PRINTING":
        raise HTTPException(
            status_code=400,
            detail=f"Job cannot be completed. Current status: {print_job.status}",
        )   

    inventory = (
        db.query(PaperInventory)
        .filter(PaperInventory.kiosk_id == kiosk.id)
        .with_for_update()
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=409,
            detail="Paper inventory not found",
        )

    if (
        inventory.reserved_sheets < print_job.pages
        or inventory.stock_sheets < print_job.pages
    ):
        raise HTTPException(
            status_code=409,
            detail="Reserved paper stock is inconsistent; check inventory",
        )

    # Deduct consumed paper and release its reservation.
    inventory.stock_sheets -= print_job.pages
    inventory.reserved_sheets -= print_job.pages

    print_job.status = "COMPLETED"

    try:
        db.commit()
        db.refresh(print_job)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not finalize print job inventory",
        )

    return {
        "message": "Print job completed and stock updated",
        "job_id": print_job.job_id,
        "status": print_job.status,
        "sheets_consumed": print_job.pages,
        "completed_at": datetime.utcnow(),
    }


# ---------------------------------------------------------
# 5. PRINT FAILED
# ---------------------------------------------------------

@router.post("/{job_id}/failed")
def fail_print_job(
    job_id: str,
    reason: str = "Printer error",
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
    """
    Kiosk reports a printing failure.
    """

    kiosk = (
        db.query(Kiosk)
        .filter(
            Kiosk.kiosk_id == kiosk_id,
            Kiosk.is_active == True,
        )
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found or inactive",
        )

    print_job = (
        db.query(PrintJob)
        .filter(
            PrintJob.job_id == job_id,
            PrintJob.kiosk_id == kiosk.id,
        )
        .first()
    )

    if not print_job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found",
        )

    if print_job.status != "PRINTING":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Job cannot be marked failed. "
                f"Current status: {print_job.status}"
            ),
        )

        # Release the reservation because printing failed.
    inventory = (
        db.query(PaperInventory)
        .filter(PaperInventory.kiosk_id == kiosk.id)
        .with_for_update()
        .first()
    )

    if inventory and inventory.reserved_sheets >= print_job.pages:
        inventory.reserved_sheets -= print_job.pages

    print_job.status = "FAILED"

    try:
        db.commit()
        db.refresh(print_job)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not release reserved paper stock",
        )

    return {
        "message": "Print job failed; reservation released when available",
        "job_id": print_job.job_id,
        "status": print_job.status,
        "reason": reason,
    }
   
    


# ---------------------------------------------------------
# 6. JOB STATUS
# ---------------------------------------------------------

@router.get("/{job_id}/status")
def get_queue_job_status(
    job_id: str,
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
    """
    Kiosk checks current status of its print job.
    """

    kiosk = (
        db.query(Kiosk)
        .filter(
            Kiosk.kiosk_id == kiosk_id,
            Kiosk.is_active == True,
        )
        .first()
    )

    if not kiosk:
        raise HTTPException(
            status_code=404,
            detail="Kiosk not found or inactive",
        )

    print_job = (
        db.query(PrintJob)
        .filter(
            PrintJob.job_id == job_id,
            PrintJob.kiosk_id == kiosk.id,
        )
        .first()
    )

    if not print_job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found",
        )

    return {
        "job_id": print_job.job_id,
        "status": print_job.status,
        "pages": print_job.pages,
        "amount": print_job.amount,
        "kiosk_id": kiosk.kiosk_id,
        "created_at": print_job.created_at,
    }

# Secure PDF download for the authenticated kiosk worker.
@router.get("/{job_id}/document")
def download_print_document(
    job_id: str,
    kiosk_id: str = Depends(get_current_kiosk),
    db: Session = Depends(get_db),
):
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

    job = (
        db.query(PrintJob)
        .filter(
            PrintJob.job_id == job_id,
            PrintJob.kiosk_id == kiosk.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Print job not found for this kiosk",
        )

    if job.status != "PRINTING":
        raise HTTPException(
            status_code=409,
            detail="Job must be claimed before downloading",
        )

    document = (
        db.query(Document)
        .filter(Document.id == job.document_id)
        .first()
    )

    if not document or not document.storage_key:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # Only allow a plain filename, never a path from a request.
    storage_key = Path(document.storage_key).name
    if storage_key != document.storage_key:
        raise HTTPException(
            status_code=400,
            detail="Invalid document storage key",
        )

    storage_dir = (
        Path(__file__).resolve().parents[1]
        / "storage"
        / "documents"
    )
    pdf_path = (storage_dir / storage_key).resolve()

    if pdf_path.parent != storage_dir.resolve() or not pdf_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stored PDF is unavailable",
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=Path(document.file_name).name,
    )

