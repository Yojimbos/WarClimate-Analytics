from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import parse_date_range
from app.db.session import get_db
from app.services.analytics.service import AnalyticsService

router = APIRouter(tags=["analytics"])


@router.get("/correlation")
def get_correlation(
    date_range: tuple = Depends(parse_date_range),
    location: str = Query(default="kyiv"),
    db: Session = Depends(get_db),
) -> dict:
    from_date, to_date = date_range
    return AnalyticsService(db).get_correlation_payload(from_date, to_date, location)


@router.get("/summary")
def get_summary(
    date_range: tuple = Depends(parse_date_range),
    location: str = Query(default="kyiv"),
    db: Session = Depends(get_db),
) -> dict:
    from_date, to_date = date_range
    return AnalyticsService(db).get_summary_payload(from_date, to_date, location)
