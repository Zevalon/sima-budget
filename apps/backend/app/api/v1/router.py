from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.get("/meta", tags=["meta"])
async def meta() -> dict[str, str]:
    return {
        "api_version": "v1",
        "application": "SIMA",
        "implementation_phase": "0",
    }
