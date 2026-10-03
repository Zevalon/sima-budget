from fastapi import APIRouter, HTTPException, status

from app.core.database import ping_database
from app.modules.health.schemas import HealthResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=HealthResponse)
async def live() -> HealthResponse:
    return HealthResponse()


@router.get("/ready", response_model=ReadinessResponse)
async def ready() -> ReadinessResponse:
    if not await ping_database():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Aplikasi belum siap menerima traffic.",
        )
    return ReadinessResponse()
