import { type FormEvent, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import { useFiscalYear } from "../fiscal-year-context";
import {
  createFiscalYear,
  listFiscalYears,
  reopenFiscalYear,
  transitionFiscalYear,
} from "../api/budgetFoundation";
import type { FiscalYear, FiscalYearStatus } from "../types";

import "../../../styles/budget-foundation.css";

const transitionLabels: Partial<
  Record<FiscalYearStatus, { target: FiscalYearStatus; label: string }>
> = {
  DRAFT: { target: "PLANNING", label: "Mulai Planning" },
  PLANNING: { target: "ACTIVE", label: "Aktifkan" },
  ACTIVE: { target: "CLOSED", label: "Tutup" },
  CLOSED: { target: "ARCHIVED", label: "Arsipkan" },
};

export function FiscalYearsPage() {
  const auth = useAuth();
  const fiscalYearContext = useFiscalYear();
  const permissions = new Set(auth.user?.permissions ?? []);
  const canCreate = permissions.has("fiscal_years.create");
  const canTransition = permissions.has("fiscal_years.transition");
  const canReopen = permissions.has("fiscal_years.reopen");
  const [items, setItems] = useState<FiscalYear[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function reload() {
    setErrorMessage(null);
    try {
      setItems(await listFiscalYears());
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat tahun anggaran.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    void listFiscalYears()
      .then((data) => {
        if (!active) return;
        setItems(data);
        setLoading(false);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat tahun anggaran.");
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const yearText = getFormString(data, "year");
    setErrorMessage(null);

    try {
      await createFiscalYear({
        code: getFormString(data, "code"),
        year: yearText ? Number(yearText) : null,
        start_date: getFormString(data, "start_date"),
        end_date: getFormString(data, "end_date"),
      });
      form.reset();
      await reload();
      await fiscalYearContext.refreshFiscalYears();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal membuat tahun anggaran.");
    }
  }

  async function handleTransition(item: FiscalYear, target: FiscalYearStatus) {
    if (!window.confirm(`Ubah ${item.code} dari ${item.status} menjadi ${target}?`)) return;
    try {
      await transitionFiscalYear(item.id, target);
      await reload();
      await fiscalYearContext.refreshFiscalYears();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal mengubah status tahun anggaran.",
      );
    }
  }

  async function handleReopen(item: FiscalYear) {
    const reason = window.prompt("Alasan membuka kembali tahun anggaran:");
    if (!reason) return;
    try {
      await reopenFiscalYear(item.id, reason);
      await reload();
      await fiscalYearContext.refreshFiscalYears();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal membuka kembali tahun anggaran.",
      );
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Budget Foundation</p>
          <h1>Tahun Anggaran</h1>
          <p className="lead">Lifecycle: DRAFT → PLANNING → ACTIVE → CLOSED → ARCHIVED.</p>
        </div>
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}

      {canCreate ? (
        <form
          className="panel budget-foundation-form"
          onSubmit={(event) => void handleCreate(event)}
        >
          <h2>Buat Tahun Anggaran</h2>
          <label className="form-field">
            <span>Kode</span>
            <input name="code" placeholder="FY2027" required />
          </label>
          <label className="form-field">
            <span>Tahun</span>
            <input name="year" type="number" min="1900" max="2200" placeholder="2027" />
          </label>
          <label className="form-field">
            <span>Tanggal mulai</span>
            <input name="start_date" type="date" required />
          </label>
          <label className="form-field">
            <span>Tanggal selesai</span>
            <input name="end_date" type="date" required />
          </label>
          <div className="budget-foundation-actions">
            <button className="primary-button" type="submit">
              Simpan Tahun Anggaran
            </button>
          </div>
        </form>
      ) : null}

      <section className="panel">
        <div className="table-toolbar">
          <h2>Daftar Tahun Anggaran</h2>
          <span className="muted">{loading ? "Memuat..." : `${items.length} tahun`}</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Kode</th>
                <th>Periode</th>
                <th>Status</th>
                <th>Reopen</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.length === 0 && !loading ? (
                <tr>
                  <td colSpan={5} className="empty-table-cell">
                    Belum ada tahun anggaran.
                  </td>
                </tr>
              ) : null}
              {items.map((item) => {
                const transition = transitionLabels[item.status];
                return (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.code}</strong>
                      {item.year ? <span className="table-subtext">{item.year}</span> : null}
                    </td>
                    <td>
                      {item.start_date} — {item.end_date}
                    </td>
                    <td>
                      <span className={`status-pill status-${item.status.toLowerCase()}`}>
                        {item.status}
                      </span>
                    </td>
                    <td>
                      {item.reopened_at ? (item.reopen_reason ?? "Pernah dibuka kembali") : "—"}
                    </td>
                    <td className="table-actions">
                      <div className="table-action-group">
                        {canTransition && transition ? (
                          <button
                            className="secondary-button compact-button"
                            type="button"
                            onClick={() => void handleTransition(item, transition.target)}
                          >
                            {transition.label}
                          </button>
                        ) : null}
                        {canReopen && item.status === "CLOSED" ? (
                          <button
                            className="secondary-button compact-button"
                            type="button"
                            onClick={() => void handleReopen(item)}
                          >
                            Buka Kembali
                          </button>
                        ) : null}
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
