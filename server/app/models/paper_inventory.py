from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class PaperInventory(Base):
    __tablename__ = "paper_inventory"

    __table_args__ = (
        UniqueConstraint("kiosk_id", name="uq_paper_inventory_kiosk"),
        CheckConstraint("stock_sheets >= 0", name="ck_paper_stock_nonnegative"),
        CheckConstraint("reserved_sheets >= 0", name="ck_paper_reserved_nonnegative"),
        CheckConstraint(
            "reserved_sheets <= stock_sheets",
            name="ck_paper_reserved_lte_stock",
        ),
        CheckConstraint(
            "low_stock_threshold >= 0",
            name="ck_paper_low_threshold_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    kiosk_id: Mapped[int] = mapped_column(
        ForeignKey("kiosks.id"),
        index=True,
    )

    stock_sheets: Mapped[int] = mapped_column(Integer, default=0)
    reserved_sheets: Mapped[int] = mapped_column(Integer, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=50)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
