import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppShell } from "../layouts/AppShell";
import { DashboardPage } from "../features/dashboard/pages/DashboardPage";
import { NotFoundPage } from "../features/system/pages/NotFoundPage";

export const router = createBrowserRouter([
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
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
