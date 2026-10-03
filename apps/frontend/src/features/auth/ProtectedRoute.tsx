import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "./auth-context";

export function ProtectedRoute() {
  const auth = useAuth();
  const location = useLocation();

  if (auth.status === "loading") {
    return (
      <main className="center-page">
        <div className="auth-card">
          <p className="eyebrow">SIMA</p>
          <h1>Memeriksa session...</h1>
          <p className="muted">Mohon tunggu sebentar.</p>
        </div>
      </main>
    );
  }

  if (auth.status === "anonymous") {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
