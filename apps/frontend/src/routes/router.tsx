import { createBrowserRouter, Navigate } from "react-router-dom";

import { DashboardPage } from "../features/dashboard/pages/DashboardPage";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { ProtectedRoute } from "../features/auth/ProtectedRoute";
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
        ],
      },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
