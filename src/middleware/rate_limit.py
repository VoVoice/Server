# VoVoice Rate Limiting Middleware
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_limit: str = "60/minute"):
        super().__init__(app)
        self.default_limit = self._parse_limit(default_limit)
        self.requests = defaultdict(list)
        self.endpoint_limits = {
            "/account/register": self._parse_limit("5/hour"),
            "/account/login": self._parse_limit("10/hour"),
            "/auth/register": self._parse_limit("5/hour"),
            "/auth/login": self._parse_limit("10/hour"),
            "/stt": self._parse_limit("30/minute"),
            "/chat": self._parse_limit("60/minute"),
            "/tts": self._parse_limit("60/minute"),
            "/health": self._parse_limit("120/minute"),
        }

    def _parse_limit(self, limit_str: str) -> tuple:
        count, period = limit_str.split("/")
        multipliers = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}
        return int(count), multipliers.get(period, 60)

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        client_id = self._get_client_id(request)
        key = f"{client_id}:{path}"

        limit = self.endpoint_limits.get(path, self.default_limit)
        count, window = limit

        now = datetime.now()
        cutoff = now - timedelta(seconds=window)

        self.requests[key] = [t for t in self.requests[key] if t > cutoff]

        if len(self.requests[key]) >= count:
            retry_after = int((self.requests[key][0] - cutoff).total_seconds()) + 1
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)}
            )

        self.requests[key].append(now)

        response = await call_next(request)
        remaining = count - len(self.requests[key])
        response.headers["X-RateLimit-Limit"] = str(count)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(seconds=window)).timestamp()))

        return response


def setup_rate_limiting(app, default_limit: str = "60/minute"):
    app.add_middleware(RateLimitMiddleware, default_limit=default_limit)
