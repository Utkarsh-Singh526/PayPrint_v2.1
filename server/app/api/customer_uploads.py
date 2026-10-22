
import hashlib
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.customer_session import CustomerSession
from app.models.document import Document

router = APIRouter(
    prefix="/customer-uploads",
    tags=["Customer Uploads"]
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
STORAGE_DIR = Path(__file__).resolve().parents[1] / "storage" / "documents"


def get_valid_session(
    session_id: int,
    session_token: str,
    db: Session
) -> CustomerSession:
    token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    customer_session = (
        db.query(CustomerSession)
        .filter(
            CustomerSession.id == session_id,
            CustomerSession.token_hash == token_hash,
            CustomerSession.status == "ACTIVE",
            CustomerSession.expires_at > datetime.utcnow()
        )
        .first()
    )

    if not customer_session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired customer session"
        )

    return customer_session


@router.post("/{session_id}/pdf")
async def upload_customer_pdf(
    session_id: int,
    file: UploadFile = File(...),
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db)
):
    customer_session = get_valid_session(
        session_id, x_session_token, db
    )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF must be 10 MB or smaller"
        )

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    storage_name = f"{uuid.uuid4().hex}.pdf"
    storage_path = STORAGE_DIR / storage_name

    try:
        # Validate PDF and count pages before storing it.
        import io
        reader = PdfReader(io.BytesIO(content), strict=True)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="Password-protected PDFs are not supported"
            )

        page_count = len(reader.pages)

        if page_count < 1:
            raise HTTPException(
                status_code=400,
                detail="PDF contains no pages"
            )

        storage_path.write_bytes(content)

        document = Document(
            user_id=None,
            customer_session_id=customer_session.id,
            file_name=Path(file.filename).name[:255],
            storage_key=storage_name,
            page_count=page_count,
            file_size=len(content)
        )

        db.add(document)
        db.commit()
        db.refresh(document)

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        if storage_path.exists():
            storage_path.unlink()
        raise HTTPException(
            status_code=400,
            detail="Could not process this PDF"
        )
    finally:
        await file.close()

    return {
        "message": "PDF uploaded successfully",
        "document_id": document.id,
        "file_name": document.file_name,
        "page_count": document.page_count,
        "file_size": document.file_size,
        "session_id": customer_session.id,
        "status": "uploaded"
    }
