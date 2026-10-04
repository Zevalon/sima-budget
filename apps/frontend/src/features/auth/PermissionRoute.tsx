import { Outlet } from "react-router-dom";

import { AccessDeniedPage } from "../system/pages/AccessDeniedPage";
import { useAuth } from "./auth-context";

type PermissionRouteProps = {
  anyOf: string[];
};

export function PermissionRoute({ anyOf }: PermissionRouteProps) {
  const auth = useAuth();
  const permissions = new Set(auth.user?.permissions ?? []);
  const allowed = anyOf.some((permission) => permissions.has(permission));

  if (!allowed) {
    return <AccessDeniedPage />;
  }

  return <Outlet />;
}
