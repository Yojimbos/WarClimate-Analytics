from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WeatherDaily(Base):
    __tablename__ = "weather_daily"
    __table_args__ = (
        UniqueConstraint("date", "location_name", name="uq_weather_daily_date_location"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    location_name: Mapped[str] = mapped_column(String(80), index=True)
    avg_temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_speed_km_h: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure_hpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    weather_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    weather_summary: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_name: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[str] = mapped_column(String(512))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
