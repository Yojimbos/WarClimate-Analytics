from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LossesDaily(Base):
    __tablename__ = "losses_daily"
    __table_args__ = (UniqueConstraint("date", name="uq_losses_daily_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    personnel_losses: Mapped[int] = mapped_column(Integer)
    source_name: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[str] = mapped_column(String(512))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    raw_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
