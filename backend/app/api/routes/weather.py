from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import parse_date_range
from app.db.session import get_db
from app.models.weather_daily import WeatherDaily
from app.services.constants import get_location

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("")
def get_weather(
    date_range: tuple = Depends(parse_date_range),
    location: str = Query(default="kyiv"),
    db: Session = Depends(get_db),
) -> dict:
    from_date, to_date = date_range
    location_name = get_location(location)["name"]
    rows = db.execute(
        select(WeatherDaily)
        .where(
            WeatherDaily.date >= from_date,
            WeatherDaily.date <= to_date,
            WeatherDaily.location_name == location_name,
        )
        .order_by(WeatherDaily.date)
    ).scalars()
    items = [
        {
            "date": row.date,
            "location_name": row.location_name,
            "avg_temperature_c": row.avg_temperature_c,
            "min_temperature_c": row.min_temperature_c,
            "max_temperature_c": row.max_temperature_c,
            "precipitation_mm": row.precipitation_mm,
            "wind_speed_km_h": row.wind_speed_km_h,
            "humidity_percent": row.humidity_percent,
            "pressure_hpa": row.pressure_hpa,
            "weather_code": row.weather_code,
            "weather_summary": row.weather_summary,
            "source_name": row.source_name,
            "source_url": row.source_url,
            "fetched_at": row.fetched_at,
        }
        for row in rows
    ]
    return {"items": items, "total": len(items)}
