from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from app.core.config import get_settings
from app.services.adapters.base import LossesAdapter, LossesRecordPayload
from app.services.constants import LOSSES_SOURCE_NAME


class SampleLossesAdapter(LossesAdapter):
    name = "sample_losses"

    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_range(self, from_date: date, to_date: date) -> list[LossesRecordPayload]:
        path = Path(self.settings.data_dir) / "losses_sample.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        return [
            LossesRecordPayload(
                date=date.fromisoformat(item["date"]),
                personnel_losses=item["personnel_losses"],
                source_name=LOSSES_SOURCE_NAME,
                source_url=item["source_url"],
                raw_payload=item,
                raw_text=item.get("raw_text"),
            )
            for item in records
            if from_date <= date.fromisoformat(item["date"]) <= to_date
        ]
