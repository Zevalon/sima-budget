from fastapi import APIRouter

from app.modules.auth.api import router as auth_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)


@router.get("/meta", tags=["meta"])
async def meta() -> dict[str, str]:
    return {
        "api_version": "v1",
        "application": "SIMA",
        "implementation_phase": "1B",
    }
