from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.data_refresh import ensure_data_available
from app.api.deps import parse_date_range
from app.db.session import get_db
from app.services.analytics.service import AnalyticsService

router = APIRouter(tags=["analytics"])


@router.get("/correlation")
async def get_correlation(
    date_range: tuple = Depends(parse_date_range),
    location: str = Query(default="kharkiv"),
    db: Session = Depends(get_db),
) -> dict:
    from_date, to_date = date_range
    await ensure_data_available(db, from_date, to_date, location)
    return AnalyticsService(db).get_correlation_payload(from_date, to_date, location)


@router.get("/summary")
async def get_summary(
    date_range: tuple = Depends(parse_date_range),
    location: str = Query(default="kharkiv"),
    db: Session = Depends(get_db),
) -> dict:
    from_date, to_date = date_range
    await ensure_data_available(db, from_date, to_date, location)
    return AnalyticsService(db).get_summary_payload(from_date, to_date, location)
