from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.losses_daily import LossesDaily
from app.models.weather_daily import WeatherDaily
from app.services.constants import get_location


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _load_dataframe(self, from_date: date, to_date: date, location: str) -> pd.DataFrame:
        location_name = get_location(location)["name"]
        losses = self.db.execute(
            select(LossesDaily)
            .where(LossesDaily.date >= from_date, LossesDaily.date <= to_date)
            .order_by(LossesDaily.date)
        ).scalars()
        weather = self.db.execute(
            select(WeatherDaily)
            .where(
                WeatherDaily.date >= from_date,
                WeatherDaily.date <= to_date,
                WeatherDaily.location_name == location_name,
            )
            .order_by(WeatherDaily.date)
        ).scalars()
        losses_rows = [
            {
                "date": row.date,
                "personnel_losses": row.personnel_losses,
                "losses_source_url": row.source_url,
            }
            for row in losses
        ]
        weather_rows = [
            {
                "date": row.date,
                "location_name": row.location_name,
                "avg_temperature_c": row.avg_temperature_c,
                "precipitation_mm": row.precipitation_mm,
                "weather_summary": row.weather_summary,
                "weather_source_url": row.source_url,
            }
            for row in weather
        ]
        losses_df = pd.DataFrame(losses_rows)
        weather_df = pd.DataFrame(weather_rows)
        if losses_df.empty or weather_df.empty:
            return pd.DataFrame()
        df = losses_df.merge(weather_df, on="date", how="inner").sort_values("date")
        df["rolling_losses_7d"] = df["personnel_losses"].rolling(window=7, min_periods=1).mean()
        df["rolling_temp_7d"] = df["avg_temperature_c"].rolling(window=7, min_periods=1).mean()
        return df

    def get_correlation_payload(self, from_date: date, to_date: date, location: str) -> dict:
        df = self._load_dataframe(from_date, to_date, location)
        if df.empty:
            return {
                "from_date": from_date,
                "to_date": to_date,
                "location": location,
                "pearson_temperature_vs_losses": None,
                "spearman_temperature_vs_losses": None,
                "pearson_precipitation_vs_losses": None,
                "spearman_precipitation_vs_losses": None,
                "records": [],
                "insights": [
                    "No overlapping losses and weather data is available for the selected range."
                ],
            }
        return {
            "from_date": from_date,
            "to_date": to_date,
            "location": location,
            "pearson_temperature_vs_losses": self._safe_corr(
                df, "avg_temperature_c", "personnel_losses", "pearson"
            ),
            "spearman_temperature_vs_losses": self._safe_corr(
                df, "avg_temperature_c", "personnel_losses", "spearman"
            ),
            "pearson_precipitation_vs_losses": self._safe_corr(
                df, "precipitation_mm", "personnel_losses", "pearson"
            ),
            "spearman_precipitation_vs_losses": self._safe_corr(
                df, "precipitation_mm", "personnel_losses", "spearman"
            ),
            "records": [
                {
                    "date": row["date"],
                    "personnel_losses": int(row["personnel_losses"]),
                    "avg_temperature_c": row["avg_temperature_c"],
                    "precipitation_mm": row["precipitation_mm"],
                    "weather_summary": row["weather_summary"],
                    "rolling_losses_7d": round(float(row["rolling_losses_7d"]), 2),
                    "rolling_temp_7d": round(float(row["rolling_temp_7d"]), 2),
                }
                for _, row in df.iterrows()
            ],
            "insights": self._build_insights(df),
        }

    def get_summary_payload(self, from_date: date, to_date: date, location: str) -> dict:
        df = self._load_dataframe(from_date, to_date, location)
        if df.empty:
            return {
                "from_date": from_date,
                "to_date": to_date,
                "location": location,
                "cards": [],
                "sources": [],
                "limitations": self._limitations(),
            }
        max_losses_row = df.loc[df["personnel_losses"].idxmax()]
        wettest_row = df.loc[df["precipitation_mm"].idxmax()]
        return {
            "from_date": from_date,
            "to_date": to_date,
            "location": location,
            "cards": [
                {
                    "label": "Average losses",
                    "value": f"{df['personnel_losses'].mean():.1f}",
                    "context": "daily personnel losses",
                },
                {
                    "label": "Max losses day",
                    "value": f"{int(max_losses_row['personnel_losses'])}",
                    "context": str(max_losses_row["date"]),
                },
                {
                    "label": "Average temperature",
                    "value": f"{df['avg_temperature_c'].mean():.1f} C",
                    "context": get_location(location)["name"],
                },
                {
                    "label": "Wettest day",
                    "value": f"{wettest_row['precipitation_mm']:.1f} mm",
                    "context": str(wettest_row["date"]),
                },
            ],
            "sources": [
                {
                    "name": "Ministry of Defence of Ukraine",
                    "url": df["losses_source_url"].dropna().iloc[0],
                },
                {
                    "name": "Open-Meteo Archive API",
                    "url": df["weather_source_url"].dropna().iloc[0],
                },
            ],
            "limitations": self._limitations(),
        }

    @staticmethod
    def _safe_corr(df: pd.DataFrame, left: str, right: str, method: str) -> float | None:
        subset = df[[left, right]].dropna()
        if len(subset) < 2:
            return None
        if method == "spearman":
            ranked = subset.rank(method="average")
            value = ranked[left].corr(ranked[right], method="pearson")
        else:
            value = subset[left].corr(subset[right], method=method)
        return None if pd.isna(value) else round(float(value), 4)

    @staticmethod
    def _build_insights(df: pd.DataFrame) -> list[str]:
        insights = [
            "The chart compares historical daily losses with a selected reference weather location.",
            "Correlation scores describe directional association within the selected range and should not be treated as causal evidence.",
        ]
        if not df.empty:
            insights.append(
                f"The selected range contains {len(df)} overlapping daily records suitable for comparison."
            )
        return insights

    @staticmethod
    def _limitations() -> list[str]:
        return [
            "Reference weather is location-based and does not represent exact battlefield conditions.",
            "Official source formatting may evolve, so parser coverage should be monitored.",
            "Correlation metrics are descriptive only and do not imply causation.",
        ]
