from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import admin, analytics, health, losses, weather

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(losses.router, prefix="/api/v1")
api_router.include_router(weather.router, prefix="/api/v1")
api_router.include_router(analytics.router, prefix="/api/v1")
api_router.include_router(admin.router, prefix="/api/v1")
