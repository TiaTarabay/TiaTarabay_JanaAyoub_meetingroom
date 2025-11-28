from fastapi import HTTPException
import time

# Simple in-memory store (reset on restart)
rate_store = {}

def rate_limiter(max_requests: int, window_seconds: int, key: str):
    """
    Factory function that RETURNS a dependency function.
    """

    def dependency():
        now = time.time()
        
        if key not in rate_store:
            rate_store[key] = []

        # Keep only timestamps inside window
        rate_store[key] = [ts for ts in rate_store[key] if now - ts < window_seconds]

        # If too many requests
        if len(rate_store[key]) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Try again later."
            )

        # Otherwise add new timestamp
        rate_store[key].append(now)

    # RETURN the dependency function
    return dependency
