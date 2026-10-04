import { useCallback, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { useFiscalYear } from "../../budget-foundation/fiscal-year-context";
import {
  approveBudgetPlan,
  listPendingBudgetPlanApprovals,
  rejectBudgetPlan,
} from "../api/budgetPlans";
import type { BudgetPlanPendingApproval } from "../types";

import "../../../styles/budget-plans.css";

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "") || "0";
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

export function BudgetPlanApprovalPage() {
  const fiscalYear = useFiscalYear();
  const selectedFiscalYear = fiscalYear.selectedFiscalYear;
  const [items, setItems] = useState<BudgetPlanPendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      setItems(await listPendingBudgetPlanApprovals(selectedFiscalYear?.id));
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal memuat inbox rencana anggaran.",
      );
    } finally {
      setLoading(false);
    }
  }, [selectedFiscalYear?.id]);

  useEffect(() => {
    void reload();
  }, [reload]);

  async function handleApprove(item: BudgetPlanPendingApproval) {
    const plan = item.budget_plan;
    if (!window.confirm(`Setujui ${plan.plan_number} versi ${item.approval.version_no}?`)) return;
    const note = window.prompt("Catatan persetujuan (opsional):", "");
    if (note === null) return;
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await approveBudgetPlan(plan.id, note.trim() || null);
      setSuccessMessage(`${plan.plan_number} berhasil disetujui.`);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal menyetujui rencana anggaran.",
      );
    }
  }

  async function handleReject(item: BudgetPlanPendingApproval) {
    const plan = item.budget_plan;
    const reason = window.prompt(`Alasan penolakan ${plan.plan_number}:`, "");
    if (reason === null) return;
    if (reason.trim().length < 3) {
      setErrorMessage("Alasan penolakan wajib diisi minimal 3 karakter.");
      return;
    }
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await rejectBudgetPlan(plan.id, reason.trim());
      setSuccessMessage(`${plan.plan_number} berhasil ditolak.`);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal menolak rencana anggaran.",
      );
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Approval</p>
          <h1>Persetujuan Rencana Anggaran</h1>
          <p className="lead">
            Meninjau versi rencana unit yang diajukan sesuai scope approval Anda.
          </p>
        </div>
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}
      {successMessage ? <div className="success-alert">{successMessage}</div> : null}

      <section className="panel">
        <div className="table-toolbar">
          <div>
            <h2>Menunggu Persetujuan</h2>
            <span className="muted">
              {selectedFiscalYear ? selectedFiscalYear.code : "Semua tahun dalam scope"}
            </span>
          </div>
          <span className="muted">{loading ? "Memuat..." : `${items.length} pengajuan`}</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Nomor</th>
                <th>Unit</th>
                <th>Versi</th>
                <th>Judul</th>
                <th>Total</th>
                <th>Diajukan</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {!loading && items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="empty-table-cell">
                    Tidak ada rencana anggaran yang menunggu persetujuan dalam scope Anda.
                  </td>
                </tr>
              ) : null}
              {items.map((item) => {
                const plan = item.budget_plan;
                return (
                  <tr key={item.approval.id}>
                    <td>
                      <strong>{plan.plan_number}</strong>
                    </td>
                    <td>
                      {plan.organization_unit_code} · {plan.organization_unit_name}
                    </td>
                    <td>{item.approval.version_no}</td>
                    <td>{plan.title}</td>
                    <td>{formatCurrency(plan.total_amount)}</td>
                    <td>{new Date(item.approval.requested_at).toLocaleString("id-ID")}</td>
                    <td>
                      <div className="approval-actions">
                        <button
                          className="secondary-button"
                          type="button"
                          onClick={() => void handleReject(item)}
                        >
                          Tolak
                        </button>
                        <button
                          className="primary-button"
                          type="button"
                          onClick={() => void handleApprove(item)}
                        >
                          Setujui
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
