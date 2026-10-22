
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class PrintJob(Base):
    __tablename__ = "print_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    job_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    # Registered users are optional for customer kiosk printing
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    kiosk_id: Mapped[int] = mapped_column(
        ForeignKey("kiosks.id")
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id")
    )

    # Link print job to a temporary customer session
    customer_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("customer_sessions.id"),
        nullable=True,
        index=True
    )

    tracking_code: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True
    )

    pages: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column()

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
