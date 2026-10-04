from app.modules.annual_budgets.models import AnnualBudget, AnnualBudgetApproval
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear, UnitOfMeasure
from app.modules.organizations.models import (
    Organization,
    OrganizationUnit,
    OrganizationUnitType,
    UserUnitMembership,
)
from app.modules.roles.models import Permission, Role, RolePermission, UserRoleAssignment
from app.modules.settings.models import ApplicationSetting
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User

MODELS = (
    Organization,
    ApplicationSetting,
    OrganizationUnitType,
    OrganizationUnit,
    User,
    UserUnitMembership,
    Role,
    Permission,
    RolePermission,
    UserRoleAssignment,
    UserSession,
    AuditLog,
    FiscalYear,
    BudgetCategory,
    UnitOfMeasure,
    AnnualBudget,
    AnnualBudgetApproval,
    UnitAllocation,
)
