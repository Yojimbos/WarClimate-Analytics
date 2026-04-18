from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.data_refresh import ensure_data_available
from app.api.deps import parse_date_range
from app.db.session import get_db
from app.models.losses_daily import LossesDaily

router = APIRouter(prefix="/losses", tags=["losses"])


@router.get("")
async def get_losses(
    date_range: tuple = Depends(parse_date_range), db: Session = Depends(get_db)
) -> dict:
    from_date, to_date = date_range
    await ensure_data_available(
        db,
        from_date,
        to_date,
        "kharkiv",
        include_losses=True,
        include_weather=False,
    )
    rows = db.execute(
        select(LossesDaily)
        .where(LossesDaily.date >= from_date, LossesDaily.date <= to_date)
        .order_by(LossesDaily.date)
    ).scalars()
    items = [
        {
            "date": row.date,
            "personnel_losses": row.personnel_losses,
            "source_name": row.source_name,
            "source_url": row.source_url,
            "fetched_at": row.fetched_at,
        }
        for row in rows
    ]
    return {"items": items, "total": len(items)}
