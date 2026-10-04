import { createBrowserRouter, Navigate } from "react-router-dom";

import { AdministrationHomePage } from "../features/administration/pages/AdministrationHomePage";
import { OrganizationUnitsPage } from "../features/administration/pages/OrganizationUnitsPage";
import { RolesPage } from "../features/administration/pages/RolesPage";
import { UsersPage } from "../features/administration/pages/UsersPage";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { AnnualBudgetApprovalPage } from "../features/annual-budgets/pages/AnnualBudgetApprovalPage";
import { ApprovalHomePage } from "../features/approvals/pages/ApprovalHomePage";
import { AnnualBudgetsPage } from "../features/annual-budgets/pages/AnnualBudgetsPage";
import { PermissionRoute } from "../features/auth/PermissionRoute";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import { BudgetCategoriesPage } from "../features/budget-foundation/pages/BudgetCategoriesPage";
import { FiscalYearsPage } from "../features/budget-foundation/pages/FiscalYearsPage";
import { MasterDataHomePage } from "../features/budget-foundation/pages/MasterDataHomePage";
import { UnitsOfMeasurePage } from "../features/budget-foundation/pages/UnitsOfMeasurePage";
import { DashboardPage } from "../features/dashboard/pages/DashboardPage";
import { BudgetPlanApprovalPage } from "../features/budget-plans/pages/BudgetPlanApprovalPage";
import { BudgetPlansPage } from "../features/budget-plans/pages/BudgetPlansPage";
import { AuditLogPage } from "../features/foundation/pages/AuditLogPage";
import { SettingsPage } from "../features/foundation/pages/SettingsPage";
import { RealizationsPage } from "../features/realizations/pages/RealizationsPage";
import { UnitAllocationsPage } from "../features/unit-allocations/pages/UnitAllocationsPage";
import { NotFoundPage } from "../features/system/pages/NotFoundPage";
import { AppShell } from "../layouts/AppShell";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: "/",
        element: <Navigate to="/app/dashboard" replace />,
      },
      {
        path: "/app",
        element: <AppShell />,
        children: [
          {
            path: "dashboard",
            element: <DashboardPage />,
          },
          {
            element: <PermissionRoute anyOf={["annual_budgets.view"]} />,
            children: [
              {
                path: "annual-budgets",
                element: <AnnualBudgetsPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["unit_allocations.view"]} />,
            children: [
              {
                path: "unit-allocations",
                element: <UnitAllocationsPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["budget_plans.view"]} />,
            children: [
              {
                path: "budget-plans",
                element: <BudgetPlansPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["realizations.view"]} />,
            children: [
              {
                path: "realizations",
                element: <RealizationsPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["annual_budgets.approve", "budget_plans.approve"]} />,
            children: [
              {
                path: "approvals",
                element: <ApprovalHomePage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["annual_budgets.approve"]} />,
            children: [
              {
                path: "approvals/annual-budgets",
                element: <AnnualBudgetApprovalPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["budget_plans.approve"]} />,
            children: [
              {
                path: "approvals/budget-plans",
                element: <BudgetPlanApprovalPage />,
              },
            ],
          },
          {
            element: (
              <PermissionRoute
                anyOf={["fiscal_years.view", "budget_categories.view", "units_of_measure.view"]}
              />
            ),
            children: [
              {
                path: "master-data",
                element: <MasterDataHomePage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["fiscal_years.view"]} />,
            children: [
              {
                path: "master-data/fiscal-years",
                element: <FiscalYearsPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["budget_categories.view"]} />,
            children: [
              {
                path: "master-data/budget-categories",
                element: <BudgetCategoriesPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["units_of_measure.view"]} />,
            children: [
              {
                path: "master-data/units-of-measure",
                element: <UnitsOfMeasurePage />,
              },
            ],
          },
          {
            element: (
              <PermissionRoute
                anyOf={[
                  "users.view",
                  "roles.view",
                  "permissions.view",
                  "organization_units.view",
                  "settings.view",
                  "audit.view",
                ]}
              />
            ),
            children: [
              {
                path: "administration",
                element: <AdministrationHomePage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["users.view"]} />,
            children: [
              {
                path: "administration/users",
                element: <UsersPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["roles.view", "permissions.view"]} />,
            children: [
              {
                path: "administration/roles",
                element: <RolesPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["organization_units.view"]} />,
            children: [
              {
                path: "administration/organization-units",
                element: <OrganizationUnitsPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["settings.view"]} />,
            children: [
              {
                path: "administration/settings",
                element: <SettingsPage />,
              },
            ],
          },
          {
            element: <PermissionRoute anyOf={["audit.view"]} />,
            children: [
              {
                path: "administration/audit",
                element: <AuditLogPage />,
              },
            ],
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
