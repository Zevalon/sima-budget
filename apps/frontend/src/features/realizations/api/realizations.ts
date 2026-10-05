import { apiRequest } from "../../../lib/api/client";
import type { Realization, RealizationContext, RealizationStatus } from "../types";

export function getRealizationContext(fiscalYearId: string): Promise<RealizationContext> {
  return apiRequest<RealizationContext>(
    `/realizations/context?fiscal_year_id=${encodeURIComponent(fiscalYearId)}`,
  );
}

export function listRealizations(fiscalYearId: string): Promise<Realization[]> {
  return apiRequest<Realization[]>(
    `/realizations?fiscal_year_id=${encodeURIComponent(fiscalYearId)}`,
  );
}

export function createRealization(payload: {
  budget_plan_id: string;
  realization_date: string;
  reference_number: string;
  description: string;
  vendor_name: string | null;
  amount: string;
}): Promise<Realization> {
  return apiRequest<Realization>(
    "/realizations",
    { method: "POST", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function updateRealization(
  realizationId: string,
  payload: {
    expected_row_version: number;
    expected_status: RealizationStatus;
    expected_plan_version_id: string;
    realization_date: string;
    reference_number: string;
    description: string;
    vendor_name: string | null;
    amount: string;
  },
): Promise<Realization> {
  return apiRequest<Realization>(
    `/realizations/${realizationId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
    { csrf: true },
  );
}

export function postRealization(
  realizationId: string,
  expectedRowVersion: number,
  expectedStatus: RealizationStatus,
  expectedPlanVersionId: string,
): Promise<Realization> {
  return apiRequest<Realization>(
    `/realizations/${realizationId}/post`,
    {
      method: "POST",
      body: JSON.stringify({
        expected_row_version: expectedRowVersion,
        expected_status: expectedStatus,
        expected_plan_version_id: expectedPlanVersionId,
      }),
    },
    { csrf: true },
  );
}

export function cancelRealization(
  realizationId: string,
  expectedRowVersion: number,
  expectedStatus: RealizationStatus,
  expectedPlanVersionId: string,
  reason: string,
): Promise<Realization> {
  return apiRequest<Realization>(
    `/realizations/${realizationId}/cancel`,
    {
      method: "POST",
      body: JSON.stringify({
        expected_row_version: expectedRowVersion,
        expected_status: expectedStatus,
        expected_plan_version_id: expectedPlanVersionId,
        reason,
      }),
    },
    { csrf: true },
  );
}

export function reverseRealization(
  realizationId: string,
  expectedRowVersion: number,
  expectedStatus: RealizationStatus,
  expectedPlanVersionId: string,
  reason: string,
): Promise<Realization> {
  return apiRequest<Realization>(
    `/realizations/${realizationId}/reverse`,
    {
      method: "POST",
      body: JSON.stringify({
        expected_row_version: expectedRowVersion,
        expected_status: expectedStatus,
        expected_plan_version_id: expectedPlanVersionId,
        reason,
      }),
    },
    { csrf: true },
  );
}

export function createCorrectionDraft(
  realizationId: string,
  expectedRowVersion: number,
  expectedStatus: RealizationStatus,
  expectedPlanVersionId: string,
): Promise<Realization> {
  return apiRequest<Realization>(
    `/realizations/${realizationId}/correction`,
    {
      method: "POST",
      body: JSON.stringify({
        expected_row_version: expectedRowVersion,
        expected_status: expectedStatus,
        expected_plan_version_id: expectedPlanVersionId,
      }),
    },
    { csrf: true },
  );
}
