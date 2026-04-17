"""initial schema

Revision ID: 20260417_0001
Revises:
Create Date: 2026-04-17 12:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260417_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("base_url", sa.String(length=512), nullable=False),
        sa.Column("is_official", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_name", sa.String(length=80), nullable=False),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "losses_daily",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("personnel_losses", sa.Integer(), nullable=False),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("source_url", sa.String(length=512), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", name="uq_losses_daily_date"),
    )

    op.create_table(
        "weather_daily",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("location_name", sa.String(length=80), nullable=False),
        sa.Column("avg_temperature_c", sa.Float(), nullable=True),
        sa.Column("min_temperature_c", sa.Float(), nullable=True),
        sa.Column("max_temperature_c", sa.Float(), nullable=True),
        sa.Column("precipitation_mm", sa.Float(), nullable=True),
        sa.Column("wind_speed_km_h", sa.Float(), nullable=True),
        sa.Column("humidity_percent", sa.Float(), nullable=True),
        sa.Column("pressure_hpa", sa.Float(), nullable=True),
        sa.Column("weather_code", sa.String(length=32), nullable=True),
        sa.Column("weather_summary", sa.String(length=120), nullable=True),
        sa.Column("source_name", sa.String(length=120), nullable=False),
        sa.Column("source_url", sa.String(length=512), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", "location_name", name="uq_weather_daily_date_location"),
    )

    op.create_table(
        "analytics_cache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cache_key", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cache_key"),
    )


def downgrade() -> None:
    op.drop_table("analytics_cache")
    op.drop_table("weather_daily")
    op.drop_table("losses_daily")
    op.drop_table("ingestion_runs")
    op.drop_table("data_sources")

