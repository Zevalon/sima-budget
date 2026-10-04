import { useCallback, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import {
  approveAnnualBudget,
  listPendingAnnualBudgets,
  rejectAnnualBudget,
} from "../api/annualBudgets";
import type { AnnualBudget } from "../types";

import "../../../styles/annual-budgets.css";

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "");
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

export function AnnualBudgetApprovalPage() {
  const [items, setItems] = useState<AnnualBudget[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      setItems(await listPendingAnnualBudgets());
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal memuat inbox persetujuan.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  async function handleApprove(item: AnnualBudget) {
    if (!window.confirm(`Setujui anggaran ${item.fiscal_year_code}?`)) return;
    const note = window.prompt("Catatan persetujuan (opsional):", "");
    if (note === null) return;
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await approveAnnualBudget(item.id, note.trim() || null);
      setSuccessMessage(`Anggaran ${item.fiscal_year_code} berhasil disetujui.`);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal menyetujui anggaran tahunan.",
      );
    }
  }

  async function handleReject(item: AnnualBudget) {
    const reason = window.prompt(`Alasan penolakan anggaran ${item.fiscal_year_code}:`, "");
    if (reason === null) return;
    if (reason.trim().length < 3) {
      setErrorMessage("Alasan penolakan wajib diisi minimal 3 karakter.");
      return;
    }
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await rejectAnnualBudget(item.id, reason.trim());
      setSuccessMessage(`Anggaran ${item.fiscal_year_code} berhasil ditolak.`);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal menolak anggaran tahunan.",
      );
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Approval</p>
          <h1>Persetujuan Anggaran Tahunan</h1>
          <p className="lead">Meninjau pagu organisasi yang diajukan Budget Administrator.</p>
        </div>
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}
      {successMessage ? <div className="success-alert">{successMessage}</div> : null}

      <section className="panel">
        <div className="table-toolbar">
          <h2>Menunggu Persetujuan</h2>
          <span className="muted">{loading ? "Memuat..." : `${items.length} pengajuan`}</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Tahun Anggaran</th>
                <th>Versi</th>
                <th>Total Pagu</th>
                <th>Diajukan</th>
                <th>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {!loading && items.length === 0 ? (
                <tr>
                  <td colSpan={5} className="empty-table-cell">
                    Tidak ada anggaran tahunan yang menunggu persetujuan.
                  </td>
                </tr>
              ) : null}
              {items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <strong>{item.fiscal_year_code}</strong>
                  </td>
                  <td>{item.version}</td>
                  <td>{formatCurrency(item.amount)}</td>
                  <td>
                    {item.submitted_at ? new Date(item.submitted_at).toLocaleString("id-ID") : "—"}
                  </td>
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
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
