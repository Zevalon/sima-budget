import { createBrowserRouter, Navigate } from "react-router-dom";

import { AdministrationHomePage } from "../features/administration/pages/AdministrationHomePage";
import { OrganizationUnitsPage } from "../features/administration/pages/OrganizationUnitsPage";
import { RolesPage } from "../features/administration/pages/RolesPage";
import { UsersPage } from "../features/administration/pages/UsersPage";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { PermissionRoute } from "../features/auth/PermissionRoute";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
import { DashboardPage } from "../features/dashboard/pages/DashboardPage";
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
            element: (
              <PermissionRoute
                anyOf={["users.view", "roles.view", "permissions.view", "organization_units.view"]}
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
        ],
      },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
