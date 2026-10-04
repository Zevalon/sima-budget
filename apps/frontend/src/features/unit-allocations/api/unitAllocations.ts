import { apiRequest } from "../../../lib/api/client";
import type { UnitAllocation, UnitAllocationOverview } from "../types";

export function getUnitAllocationOverview(fiscalYearId: string): Promise<UnitAllocationOverview> {
  return apiRequest<UnitAllocationOverview>(
    `/unit-allocations/overview?fiscal_year_id=${encodeURIComponent(fiscalYearId)}`,
  );
}

export function createUnitAllocation(payload: {
  fiscal_year_id: string;
  organization_unit_id: string;
  amount: string;
  notes: string | null;
}): Promise<UnitAllocation> {
  return apiRequest<UnitAllocation>(
    "/unit-allocations",
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function updateUnitAllocation(
  allocationId: string,
  payload: { amount?: string; notes?: string | null },
): Promise<UnitAllocation> {
  return apiRequest<UnitAllocation>(
    `/unit-allocations/${allocationId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
    { csrf: true },
  );
}
