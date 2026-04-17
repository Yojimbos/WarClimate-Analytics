from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import validate_admin_api_key
from app.core.validation import range_from_days, validate_date_range
from app.db.session import get_db
from app.schemas.admin import ReimportRequest
from app.services.ingestion.service import IngestionService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(validate_admin_api_key)])


@router.post("/reimport")
async def reimport_data(payload: ReimportRequest, db: Session = Depends(get_db)) -> dict:
    from_date: date
    to_date: date
    if payload.from_date and payload.to_date:
        from_date, to_date = payload.from_date, payload.to_date
        validate_date_range(from_date, to_date)
    else:
        from_date, to_date = range_from_days(payload.days)
    service = IngestionService(db)
    losses_imported = await service.ingest_losses(from_date, to_date)
    weather_imported = await service.ingest_weather(from_date, to_date, payload.location)
    return {
        "status": "ok",
        "losses_imported": losses_imported,
        "weather_imported": weather_imported,
    }
