export type AdminUser = {
  id: string;
  username: string;
  email: string | null;
  full_name: string;
  is_active: boolean;
  is_locked: boolean;
  last_login_at: string | null;
};

export type AdminRole = {
  id: string;
  code: string;
  name: string;
  description: string | null;
  is_system_role: boolean;
  is_active: boolean;
};

export type AdminPermission = {
  id: string;
  code: string;
  name: string;
  module: string;
  description: string | null;
};

export type AdminOrganizationUnit = {
  id: string;
  parent_id: string | null;
  code: string;
  name: string;
  unit_type_id: string;
  unit_type_code: string;
  unit_type_name: string;
  can_receive_budget: boolean;
  can_create_budget_plan: boolean;
  is_active: boolean;
};

export type AdminOrganizationUnitType = {
  id: string;
  code: string;
  name: string;
  sort_order: number;
  is_active: boolean;
};

export type RoleAssignmentInput = {
  role_id: string;
  scope_type: "OWN" | "OWN_UNIT" | "OWN_UNIT_AND_CHILDREN" | "ALL";
  scope_unit_id: string | null;
};
