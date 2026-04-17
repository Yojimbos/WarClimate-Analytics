from __future__ import annotations

from datetime import date, timedelta

from fastapi import Query

from app.core.validation import validate_date_range


def parse_date_range(
    from_date: date = Query(
        default_factory=lambda: date.today() - timedelta(days=29), alias="from"
    ),
    to_date: date = Query(default_factory=date.today, alias="to"),
) -> tuple[date, date]:
    validate_date_range(from_date, to_date)
    return from_date, to_date
