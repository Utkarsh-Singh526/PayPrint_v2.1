from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Printer(Base):
    __tablename__ = "printers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    kiosk_id: Mapped[int] = mapped_column(
        ForeignKey("kiosks.id"),
        unique=True,
        index=True
    )

    manufacturer: Mapped[str] = mapped_column(
        String(100)
    )

    model: Mapped[str] = mapped_column(
        String(150)
    )

    connection_type: Mapped[str] = mapped_column(
        String(50),
        default="USB"
    )

    connection_address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class PrinterCapability(Base):
    __tablename__ = "printer_capabilities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    printer_id: Mapped[int] = mapped_column(
        ForeignKey("printers.id"),
        unique=True,
        index=True
    )

    supports_bw: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    supports_color: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    supports_simplex: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    supports_duplex: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    supports_a4: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    supports_a3: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    supports_letter: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    max_copies: Mapped[int] = mapped_column(
        Integer,
        default=99
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
