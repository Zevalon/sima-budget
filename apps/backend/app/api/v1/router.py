from fastapi import APIRouter

from app.modules.administration.api import router as administration_router
from app.modules.audit.api import router as audit_router
from app.modules.auth.api import router as auth_router
from app.modules.settings.api import router as settings_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(administration_router)
router.include_router(settings_router)
router.include_router(audit_router)


@router.get("/meta", tags=["meta"])
async def meta() -> dict[str, str]:
    return {
        "api_version": "v1",
        "application": "SIMA",
        "implementation_phase": "1D1",
    }
