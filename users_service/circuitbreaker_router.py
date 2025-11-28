from fastapi import APIRouter, HTTPException
from common.utils.circuit_breaker import safe_request

circuit_router = APIRouter()

@circuit_router.get("/rooms-status")
def rooms_status():
    try:
        r = safe_request("GET", "http://127.0.0.1:8001/v1/rooms/")
        return r.json()
    except Exception:
        raise HTTPException(503, "Rooms service unavailable (circuit open)")
