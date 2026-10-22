from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.kiosk import Kiosk
from app.models.paper_inventory import PaperInventory
from app.models.kiosk_pricing import KioskPricing

router = APIRouter(
    prefix="/inventory-pricing",
    tags=["Inventory & Pricing"]
)


@router.get("/{kiosk_id}")
def get_inventory_pricing(
    kiosk_id: int,
    db: Session = Depends(get_db)
):
    kiosk = db.query(Kiosk).filter(Kiosk.id == kiosk_id).first()
    if not kiosk:
        raise HTTPException(status_code=404, detail="Kiosk not found")

    inventory = db.query(PaperInventory).filter(
        PaperInventory.kiosk_id == kiosk_id
    ).first()

    pricing = db.query(KioskPricing).filter(
        KioskPricing.kiosk_id == kiosk_id,
        KioskPricing.is_active.is_(True)
    ).all()

    return {
        "kiosk_id": kiosk_id,
        "inventory": {
            "stock_sheets": inventory.stock_sheets,
            "reserved_sheets": inventory.reserved_sheets,
            "available_sheets": (
                inventory.stock_sheets - inventory.reserved_sheets
            ),
            "low_stock_threshold": inventory.low_stock_threshold
        } if inventory else None,
        "pricing": [
            {
                "paper_size": p.paper_size,
                "print_mode": p.print_mode,
                "price_per_page": str(p.price_per_page)
            }
            for p in pricing
        ]
    }


@router.put("/{kiosk_id}/inventory")
def update_inventory(
    kiosk_id: int,
    stock_sheets: int,
    low_stock_threshold: int = 50,
    db: Session = Depends(get_db)
):
    if stock_sheets < 0 or low_stock_threshold < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock and threshold cannot be negative"
        )

    kiosk = db.query(Kiosk).filter(Kiosk.id == kiosk_id).first()
    if not kiosk:
        raise HTTPException(status_code=404, detail="Kiosk not found")

    inventory = db.query(PaperInventory).filter(
        PaperInventory.kiosk_id == kiosk_id
    ).first()

    if inventory is None:
        inventory = PaperInventory(
            kiosk_id=kiosk_id,
            stock_sheets=stock_sheets,
            reserved_sheets=0,
            low_stock_threshold=low_stock_threshold
        )
        db.add(inventory)
    else:
        if stock_sheets < inventory.reserved_sheets:
            raise HTTPException(
                status_code=400,
                detail="Stock cannot be below reserved sheets"
            )
        inventory.stock_sheets = stock_sheets
        inventory.low_stock_threshold = low_stock_threshold

    db.commit()
    db.refresh(inventory)

    available = inventory.stock_sheets - inventory.reserved_sheets

    return {
        "message": "Inventory updated",
        "kiosk_id": kiosk_id,
        "stock_sheets": inventory.stock_sheets,
        "reserved_sheets": inventory.reserved_sheets,
        "available_sheets": available,
        "low_stock": available <= inventory.low_stock_threshold
    }


@router.put("/{kiosk_id}/pricing")
def update_pricing(
    kiosk_id: int,
    paper_size: str,
    print_mode: str,
    price_per_page: Decimal,
    db: Session = Depends(get_db)
):
    paper_size = paper_size.strip().upper()
    print_mode = print_mode.strip().lower()

    if paper_size not in {"A4", "A3", "LETTER"}:
        raise HTTPException(status_code=400, detail="Invalid paper size")

    if print_mode not in {"bw", "color"}:
        raise HTTPException(status_code=400, detail="Invalid print mode")

    if not price_per_page.is_finite() or price_per_page < 0:
        raise HTTPException(status_code=400, detail="Invalid page price")

    kiosk = db.query(Kiosk).filter(Kiosk.id == kiosk_id).first()
    if not kiosk:
        raise HTTPException(status_code=404, detail="Kiosk not found")

    item = db.query(KioskPricing).filter(
        KioskPricing.kiosk_id == kiosk_id,
        KioskPricing.paper_size == paper_size,
        KioskPricing.print_mode == print_mode
    ).first()

    if item:
        item.price_per_page = price_per_page
        item.is_active = True
    else:
        item = KioskPricing(
            kiosk_id=kiosk_id,
            paper_size=paper_size,
            print_mode=print_mode,
            price_per_page=price_per_page,
            is_active=True
        )
        db.add(item)

    db.commit()
    db.refresh(item)

    return {
        "message": "Pricing updated",
        "kiosk_id": kiosk_id,
        "paper_size": item.paper_size,
        "print_mode": item.print_mode,
        "price_per_page": str(item.price_per_page)
    }