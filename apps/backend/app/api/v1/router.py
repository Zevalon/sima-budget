from fastapi import APIRouter

from app.modules.administration.api import router as administration_router
from app.modules.annual_budgets.api import router as annual_budgets_router
from app.modules.audit.api import router as audit_router
from app.modules.auth.api import router as auth_router
from app.modules.budget_foundation.api import router as budget_foundation_router
from app.modules.budget_plans.api import router as budget_plans_router
from app.modules.realizations.api import router as realizations_router
from app.modules.reports.api import router as reports_router
from app.modules.settings.api import router as settings_router
from app.modules.unit_allocations.api import router as unit_allocations_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(administration_router)
router.include_router(settings_router)
router.include_router(audit_router)
router.include_router(budget_foundation_router)
router.include_router(annual_budgets_router)
router.include_router(unit_allocations_router)
router.include_router(budget_plans_router)
router.include_router(realizations_router)
router.include_router(reports_router)


@router.get("/meta", tags=["meta"])
async def meta() -> dict[str, str]:
    return {
        "api_version": "v1",
        "application": "SIMA",
        "implementation_phase": "5A",
    }
