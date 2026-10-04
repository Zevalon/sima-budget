export type ApplicationSetting = {
  application_name: string;
  application_short_name: string;
  organization_display_name: string;
  primary_color: string | null;
  secondary_color: string | null;
  currency_code: string;
  timezone: string;
  date_format: string;
  allow_annual_budget_revision: boolean;
  allow_budget_transfer: boolean;
  allow_self_approval: boolean;
};

export type AuditLogItem = {
  id: string;
  actor_user_id: string | null;
  actor_username: string | null;
  actor_full_name: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  before_data: Record<string, unknown> | null;
  after_data: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type AuditLogPage = {
  items: AuditLogItem[];
  total: number;
  limit: number;
  offset: number;
};
