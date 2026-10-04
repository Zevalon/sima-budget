import { apiRequest } from "../../../lib/api/client";
import type { ApplicationSetting, AuditLogPage } from "../types";

export function getApplicationSettings(): Promise<ApplicationSetting> {
  return apiRequest<ApplicationSetting>("/settings");
}

export function updateApplicationSettings(
  payload: Partial<ApplicationSetting>,
): Promise<ApplicationSetting> {
  return apiRequest<ApplicationSetting>(
    "/settings",
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
    { csrf: true },
  );
}

export function getAuditLogs(
  params: {
    limit?: number;
    offset?: number;
    action?: string;
    entityType?: string;
  } = {},
): Promise<AuditLogPage> {
  const search = new URLSearchParams();
  search.set("limit", String(params.limit ?? 50));
  search.set("offset", String(params.offset ?? 0));

  if (params.action) {
    search.set("action", params.action);
  }
  if (params.entityType) {
    search.set("entity_type", params.entityType);
  }

  return apiRequest<AuditLogPage>(`/audit?${search.toString()}`);
}
