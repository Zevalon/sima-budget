import { type FormEvent, useEffect, useMemo, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import { useFiscalYear } from "../../budget-foundation/fiscal-year-context";
import {
  createAnnualBudget,
  listAnnualBudgetApprovals,
  listAnnualBudgets,
  submitAnnualBudget,
  updateAnnualBudget,
} from "../api/annualBudgets";
import type { AnnualBudget, AnnualBudgetApproval } from "../types";

import "../../../styles/annual-budgets.css";

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "");
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

export function AnnualBudgetsPage() {
  const auth = useAuth();
  const fiscalYearContext = useFiscalYear();
  const permissions = useMemo(() => new Set(auth.user?.permissions ?? []), [auth.user]);
  const canCreate = permissions.has("annual_budgets.create");
  const canUpdate = permissions.has("annual_budgets.update");
  const canSubmit = permissions.has("annual_budgets.submit");
  const selectedFiscalYear = fiscalYearContext.selectedFiscalYear;
  const [budget, setBudget] = useState<AnnualBudget | null>(null);
  const [approvals, setApprovals] = useState<AnnualBudgetApproval[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function reload() {
    if (!selectedFiscalYear) {
      setBudget(null);
      setApprovals([]);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const budgets = await listAnnualBudgets(selectedFiscalYear.id);
      const current = budgets[0] ?? null;
      setBudget(current);
      setApprovals(current ? await listAnnualBudgetApprovals(current.id) : []);
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat anggaran tahunan.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!selectedFiscalYear) return;

    let active = true;
    void listAnnualBudgets(selectedFiscalYear.id)
      .then(async (budgets) => {
        const current = budgets[0] ?? null;
        const history = current ? await listAnnualBudgetApprovals(current.id) : [];
        if (!active) return;
        setBudget(current);
        setApprovals(history);
        setLoading(false);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat anggaran tahunan.",
        );
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedFiscalYear]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFiscalYear) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await createAnnualBudget({
        fiscal_year_id: selectedFiscalYear.id,
        amount: getFormString(data, "amount"),
        notes: getFormString(data, "notes") || null,
      });
      form.reset();
      setSuccessMessage("Anggaran tahunan berhasil dibuat.");
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal membuat anggaran tahunan.",
      );
    }
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!budget) return;
    const data = new FormData(event.currentTarget);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await updateAnnualBudget(budget.id, {
        amount: getFormString(data, "amount"),
        notes: getFormString(data, "notes") || null,
      });
      setSuccessMessage("Anggaran tahunan berhasil diperbarui.");
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal memperbarui anggaran tahunan.",
      );
    }
  }

  async function handleSubmit() {
    if (!budget) return;
    if (!window.confirm("Ajukan anggaran tahunan ini untuk persetujuan?")) return;
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await submitAnnualBudget(budget.id);
      setSuccessMessage("Anggaran tahunan berhasil diajukan untuk persetujuan.");
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal mengajukan anggaran tahunan.",
      );
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Budget Foundation</p>
          <h1>Anggaran Tahunan</h1>
          <p className="lead">
            Menetapkan total pagu organisasi sebelum dialokasikan ke unit organisasi.
          </p>
        </div>
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}
      {successMessage ? <div className="success-alert">{successMessage}</div> : null}

      {!selectedFiscalYear ? (
        <section className="panel">
          <h2>Pilih Tahun Anggaran</h2>
          <p className="muted">
            Pilih Tahun Anggaran pada bagian atas aplikasi untuk melihat atau membuat anggaran
            tahunan.
          </p>
        </section>
      ) : (
        <>
          <section className="panel annual-budget-summary">
            <div>
              <span className="muted">Tahun Anggaran</span>
              <strong>{selectedFiscalYear.code}</strong>
            </div>
            <div>
              <span className="muted">Status Tahun</span>
              <strong>{selectedFiscalYear.status}</strong>
            </div>
            <div>
              <span className="muted">Status Anggaran</span>
              <strong>{budget?.status ?? "BELUM DIBUAT"}</strong>
            </div>
            <div>
              <span className="muted">Total Pagu</span>
              <strong>{budget ? formatCurrency(budget.amount) : "—"}</strong>
            </div>
          </section>

          {!budget && canCreate ? (
            <form
              className="panel annual-budget-form"
              onSubmit={(event) => void handleCreate(event)}
            >
              <h2>Buat Anggaran Tahunan</h2>
              <label className="form-field">
                <span>Jumlah anggaran</span>
                <input name="amount" inputMode="decimal" placeholder="500000000000.00" required />
              </label>
              <label className="form-field annual-budget-span-2">
                <span>Catatan</span>
                <textarea name="notes" rows={4} placeholder="Catatan anggaran tahunan" />
              </label>
              <div className="annual-budget-actions">
                <button className="primary-button" type="submit">
                  Simpan Draft
                </button>
              </div>
            </form>
          ) : null}

          {budget ? (
            <section className="panel">
              <div className="table-toolbar">
                <div>
                  <h2>Anggaran {budget.fiscal_year_code}</h2>
                  <span className="muted">Versi {budget.version}</span>
                </div>
                <span className={`status-pill status-${budget.status.toLowerCase()}`}>
                  {budget.status}
                </span>
              </div>

              {budget.status === "DRAFT" && canUpdate ? (
                <form className="annual-budget-form" onSubmit={(event) => void handleUpdate(event)}>
                  <label className="form-field">
                    <span>Jumlah anggaran</span>
                    <input
                      name="amount"
                      inputMode="decimal"
                      defaultValue={budget.amount}
                      required
                    />
                  </label>
                  <label className="form-field annual-budget-span-2">
                    <span>Catatan</span>
                    <textarea name="notes" rows={4} defaultValue={budget.notes ?? ""} />
                  </label>
                  <div className="annual-budget-actions">
                    <button className="secondary-button" type="submit">
                      Simpan Perubahan
                    </button>
                    {canSubmit ? (
                      <button
                        className="primary-button"
                        type="button"
                        onClick={() => void handleSubmit()}
                      >
                        Ajukan Persetujuan
                      </button>
                    ) : null}
                  </div>
                </form>
              ) : (
                <div className="annual-budget-readonly">
                  <div>
                    <span className="muted">Jumlah</span>
                    <strong>{formatCurrency(budget.amount)}</strong>
                  </div>
                  <div>
                    <span className="muted">Catatan</span>
                    <p>{budget.notes || "—"}</p>
                  </div>
                  {budget.submitted_at ? (
                    <div>
                      <span className="muted">Diajukan</span>
                      <p>{new Date(budget.submitted_at).toLocaleString("id-ID")}</p>
                    </div>
                  ) : null}
                </div>
              )}
            </section>
          ) : null}

          {budget ? (
            <section className="panel">
              <div className="table-toolbar">
                <h2>Riwayat Pengajuan</h2>
                <span className="muted">
                  {loading ? "Memuat..." : `${approvals.length} pengajuan`}
                </span>
              </div>
              <div className="table-scroll">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Pengajuan</th>
                      <th>Status</th>
                      <th>Waktu</th>
                      <th>Catatan Keputusan</th>
                    </tr>
                  </thead>
                  <tbody>
                    {approvals.length === 0 && !loading ? (
                      <tr>
                        <td colSpan={4} className="empty-table-cell">
                          Belum ada pengajuan persetujuan.
                        </td>
                      </tr>
                    ) : null}
                    {approvals.map((item) => (
                      <tr key={item.id}>
                        <td>#{item.submission_no}</td>
                        <td>{item.status}</td>
                        <td>{new Date(item.requested_at).toLocaleString("id-ID")}</td>
                        <td>{item.decision_note ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          ) : null}
        </>
      )}
    </div>
  );
}
