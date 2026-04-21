"""Rate limiting for authentication endpoints."""

import os
import sys
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, Concatenate, ParamSpec, TypeVar

from fastapi import HTTPException, Request, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Check if we're in a testing environment
TESTING = os.getenv("ENVIRONMENT") == "testing" or "pytest" in sys.modules

P = ParamSpec("P")
R = TypeVar("R")


def create_auth_rate_limiter(
    max_attempts: str = "5/minute",
) -> Callable[
    [Callable[Concatenate[Request, P], Awaitable[R]]],
    Callable[Concatenate[Request, P], Awaitable[R]],
]:
    """
    Create a rate limiter decorator for authentication endpoints.

    Args:
        max_attempts: Rate limit string (e.g., "5/minute", "10/hour")
    """

    def decorator(
        func: Callable[Concatenate[Request, P], Awaitable[R]],
    ) -> Callable[Concatenate[Request, P], Awaitable[R]]:
        # Skip rate limiting during testing
        if TESTING:
            return func

        @wraps(func)
        async def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs) -> R:
            try:
                # Apply the slowapi limiter
                limiter.limit(max_attempts)(lambda r: None)(request)
                return await func(request, *args, **kwargs)
            except RateLimitExceeded:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication attempts. Please try again later.",
                    headers={"Retry-After": "60"},
                )

        return wrapper  # type: ignore[return-value]

    return decorator


# Pre-configured rate limiters for different endpoints
strict_auth_limiter = create_auth_rate_limiter("3/minute")  # For login attempts
moderate_auth_limiter = create_auth_rate_limiter("10/minute")  # For registration
lenient_auth_limiter = create_auth_rate_limiter("20/minute")  # For general auth operations


def setup_rate_limiting(app: Any) -> None:
    """Set up rate limiting for the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
