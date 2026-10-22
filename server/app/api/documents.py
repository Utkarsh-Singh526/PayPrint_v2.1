import os
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.models.document import Document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


BASE_STORAGE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "storage",
        "documents",
    )
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):

    # 1. Check filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required",
        )

    # 2. Check extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    # 3. Read file
    file_content = await file.read()
    file_size = len(file_content)

    # 4. Check empty file
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    # 5. Check file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must not exceed 10 MB",
        )

    # 6. Validate PDF and count pages
    try:
        reader = PdfReader(BytesIO(file_content))

        page_count = len(reader.pages)

        if page_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF contains no pages",
            )

    except HTTPException:
        raise

    except Exception as e:
        print("PDF VALIDATION ERROR:", repr(e))

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted PDF file",
        )

    # 7. Create storage directory
    os.makedirs(BASE_STORAGE_PATH, exist_ok=True)

    # 8. Generate secure random filename
    storage_filename = f"{uuid.uuid4()}.pdf"

    storage_path = os.path.join(
        BASE_STORAGE_PATH,
        storage_filename,
    )

    # 9. Store PDF
    try:
        with open(storage_path, "wb") as destination:
            destination.write(file_content)

    except Exception as e:
        print("FILE STORAGE ERROR:", repr(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store document",
        )

    # 10. Create database record
    document = Document(
        user_id=user_id,
        file_name=file.filename,
        storage_key=storage_filename,
        page_count=page_count,
        file_size=file_size,
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)

    except Exception as e:
        db.rollback()

        if os.path.exists(storage_path):
            os.remove(storage_path)

        print("DATABASE ERROR:", repr(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create document record",
        )

    # 11. Response
    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "file_name": document.file_name,
        "pages": document.page_count,
        "file_size": document.file_size,
        "storage_key": document.storage_key,
    }