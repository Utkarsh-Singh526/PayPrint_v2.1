from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class KioskPricing(Base):
    __tablename__ = "kiosk_pricing"

    __table_args__ = (
        UniqueConstraint(
            "kiosk_id",
            "paper_size",
            "print_mode",
            name="uq_kiosk_pricing_configuration",
        ),
        CheckConstraint("price_per_page >= 0", name="ck_price_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    kiosk_id: Mapped[int] = mapped_column(
        ForeignKey("kiosks.id"),
        index=True,
    )

    paper_size: Mapped[str] = mapped_column(String(20), default="A4")
    print_mode: Mapped[str] = mapped_column(String(20), default="bw")

    price_per_page: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("5.00"),
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
