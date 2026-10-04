import { createBrowserRouter, Navigate } from "react-router-dom";

import { AdministrationHomePage } from "../features/administration/pages/AdministrationHomePage";
import { OrganizationUnitsPage } from "../features/administration/pages/OrganizationUnitsPage";
import { RolesPage } from "../features/administration/pages/RolesPage";
import { UsersPage } from "../features/administration/pages/UsersPage";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { AnnualBudgetsPage } from "../features/annual-budgets/pages/AnnualBudgetsPage";
import { PermissionRoute } from "../features/auth/PermissionRoute";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import { BudgetCategoriesPage } from "../features/budget-foundation/pages/BudgetCategoriesPage";
import { FiscalYearsPage } from "../features/budget-foundation/pages/FiscalYearsPage";
import { MasterDataHomePage } from "../features/budget-foundation/pages/MasterDataHomePage";
import { UnitsOfMeasurePage } from "../features/budget-foundation/pages/UnitsOfMeasurePage";
import { DashboardPage } from "../features/dashboard/pages/DashboardPage";
import { AuditLogPage } from "../features/foundation/pages/AuditLogPage";
import { SettingsPage } from "../features/foundation/pages/SettingsPage";
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
