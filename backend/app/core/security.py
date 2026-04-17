from __future__ import annotations

from collections import defaultdict, deque
from time import time

from fastapi import Header, HTTPException, Request, status

from app.core.config import get_settings

settings = get_settings()
REQUESTS_PER_MINUTE = 120
_rate_limiter: dict[str, deque[float]] = defaultdict(deque)


def validate_admin_api_key(x_admin_api_key: str | None = Header(default=None)) -> None:
    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin API key."
        )


async def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    bucket = _rate_limiter[client_ip]
    now = time()
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded."
        )
    bucket.append(now)
