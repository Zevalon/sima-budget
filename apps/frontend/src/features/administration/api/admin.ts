import { apiRequest } from "../../../lib/api/client";
import type {
  AdminOrganizationUnit,
  AdminOrganizationUnitType,
  AdminPermission,
  AdminRole,
  AdminUser,
  RoleAssignmentInput,
} from "../types";

export function listUsers(): Promise<AdminUser[]> {
  return apiRequest<AdminUser[]>("/admin/users");
}

export function listRoles(): Promise<AdminRole[]> {
  return apiRequest<AdminRole[]>("/admin/roles");
}

export function listPermissions(): Promise<AdminPermission[]> {
  return apiRequest<AdminPermission[]>("/admin/permissions");
}

export function listOrganizationUnits(): Promise<AdminOrganizationUnit[]> {
  return apiRequest<AdminOrganizationUnit[]>("/admin/organization-units");
}

export function listOrganizationUnitTypes(): Promise<AdminOrganizationUnitType[]> {
  return apiRequest<AdminOrganizationUnitType[]>("/admin/organization-unit-types");
}

export function createUser(payload: {
  username: string;
  email: string | null;
  full_name: string;
  password: string;
  primary_unit_id: string;
  job_title: string | null;
  role_assignments: RoleAssignmentInput[];
}): Promise<unknown> {
  return apiRequest(
    "/admin/users",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    { csrf: true },
  );
}

export function deactivateUser(userId: string): Promise<void> {
  return apiRequest<void>(`/admin/users/${userId}/deactivate`, { method: "POST" }, { csrf: true });
}

export function revokeUserSessions(userId: string): Promise<void> {
  return apiRequest<void>(
    `/admin/users/${userId}/revoke-sessions`,
    { method: "POST" },
    { csrf: true },
  );
}

export function createRole(payload: {
  code: string;
  name: string;
  description: string | null;
  permission_codes: string[];
}): Promise<AdminRole> {
  return apiRequest<AdminRole>(
    "/admin/roles",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    { csrf: true },
  );
}

export function createOrganizationUnit(payload: {
  parent_id: string | null;
  unit_type_id: string;
  code: string;
  name: string;
  can_receive_budget: boolean;
  can_create_budget_plan: boolean;
}): Promise<AdminOrganizationUnit> {
  return apiRequest<AdminOrganizationUnit>(
    "/admin/organization-units",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    { csrf: true },
  );
}

export function deactivateOrganizationUnit(unitId: string): Promise<void> {
  return apiRequest<void>(
    `/admin/organization-units/${unitId}/deactivate`,
    { method: "POST" },
    { csrf: true },
  );
}
