from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.losses_daily import LossesDaily
from app.models.weather_daily import WeatherDaily
from app.services.constants import get_location
from app.services.ingestion.service import IngestionService


async def ensure_data_available(
    db: Session,
    from_date: date,
    to_date: date,
    location: str,
    *,
    include_losses: bool = True,
    include_weather: bool = True,
) -> None:
    if db.bind is not None and db.bind.dialect.name == "sqlite":
        return

    expected_days = (to_date - from_date).days + 1
    losses_count = expected_days if not include_losses else db.execute(
        select(func.count(LossesDaily.date)).where(
            LossesDaily.date >= from_date,
            LossesDaily.date <= to_date,
        )
    ).scalar_one()

    weather_count = expected_days
    if include_weather:
        location_name = get_location(location)["name"]
        weather_count = db.execute(
            select(func.count(WeatherDaily.date)).where(
                WeatherDaily.date >= from_date,
                WeatherDaily.date <= to_date,
                WeatherDaily.location_name == location_name,
            )
        ).scalar_one()

    service = IngestionService(db)

    if include_losses and losses_count < expected_days:
        await service.ingest_losses(from_date, to_date)

    if include_weather and weather_count < expected_days:
        await service.ingest_weather(from_date, to_date, location)
