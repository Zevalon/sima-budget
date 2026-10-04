export type RoleGrant = {
  role_code: string;
  role_name: string;
  scope_type: string;
  scope_unit_id: string | null;
};

export type UnitMembership = {
  unit_id: string;
  unit_code: string;
  unit_name: string;
  job_title: string | null;
  is_primary: boolean;
};

export type AuthUser = {
  id: string;
  username: string;
  email: string | null;
  full_name: string;
  organization_id: string;
  organization_name: string;
  application_name: string;
  application_short_name: string;
  organization_display_name: string;
  roles: RoleGrant[];
  permissions: string[];
  unit_memberships: UnitMembership[];
  session_expires_at: string;
  csrf_token: string;
};
