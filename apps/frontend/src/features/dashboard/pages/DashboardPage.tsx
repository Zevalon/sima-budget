import { useEffect, useMemo, useState } from "react";

import { getUnitAllocationOverview } from "../../unit-allocations/api/unitAllocations";
import type { UnitAllocationOverview } from "../../unit-allocations/types";
import { useAuth } from "../../auth/auth-context";
import { useFiscalYear } from "../../budget-foundation/fiscal-year-context";
import { ApiError } from "../../../lib/api/client";
import "../../../styles/dashboard.css";

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "") || "0";
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

function allocationPercent(overview: UnitAllocationOverview): string {
  const budget = Number(overview.annual_budget_amount);
  const allocated = Number(overview.allocated_amount);
  if (!Number.isFinite(budget) || budget <= 0 || !Number.isFinite(allocated)) return "0%";
  return `${Math.min((allocated / budget) * 100, 100).toFixed(1)}%`;
}

export function DashboardPage() {
  const auth = useAuth();
  const fiscalYear = useFiscalYear();
  const selectedFiscalYear = fiscalYear.selectedFiscalYear;
  const permissions = useMemo(() => new Set(auth.user?.permissions ?? []), [auth.user]);
  const canViewAllocations = permissions.has("unit_allocations.view");
  const [overview, setOverview] = useState<UnitAllocationOverview | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedFiscalYear || !canViewAllocations) {
      return;
    }

    let active = true;
    void getUnitAllocationOverview(selectedFiscalYear.id)
      .then((data) => {
        if (!active) return;
        setOverview(data);
        setErrorMessage(null);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat ringkasan anggaran.",
        );
      });

    return () => {
      active = false;
    };
  }, [canViewAllocations, selectedFiscalYear]);

  const activeOverview = overview?.fiscal_year_id === selectedFiscalYear?.id ? overview : null;

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Budget Foundation</p>
          <h1>Dashboard</h1>
          <p className="lead">
            Ringkasan pagu organisasi dan alokasi unit untuk Tahun Anggaran yang sedang dipilih.
          </p>
        </div>
        <span className="status-badge">
          {selectedFiscalYear ? selectedFiscalYear.status : "Pilih Tahun"}
        </span>
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}

      {!selectedFiscalYear ? (
        <section className="panel">
          <h2>Belum Ada Tahun Anggaran Terpilih</h2>
          <p className="muted">Pilih Tahun Anggaran pada bagian atas aplikasi.</p>
        </section>
      ) : null}

      {selectedFiscalYear && !canViewAllocations ? (
        <section className="panel">
          <h2>{selectedFiscalYear.code}</h2>
          <p className="muted">
            Anda dapat melihat konteks Tahun Anggaran, tetapi tidak memiliki akses ke ringkasan
            alokasi organisasi.
          </p>
        </section>
      ) : null}

      {selectedFiscalYear && canViewAllocations ? (
        <>
          <section className="dashboard-summary-grid">
            <article className="panel dashboard-metric">
              <span className="muted">Pagu Tahunan</span>
              <strong>{formatCurrency(activeOverview?.annual_budget_amount ?? "0.00")}</strong>
              <small>Status: {activeOverview?.annual_budget_status ?? "BELUM TERSEDIA"}</small>
            </article>
            <article className="panel dashboard-metric">
              <span className="muted">Sudah Dialokasikan</span>
              <strong>{formatCurrency(activeOverview?.allocated_amount ?? "0.00")}</strong>
              <small>{activeOverview ? allocationPercent(activeOverview) : "0%"} dari pagu</small>
            </article>
            <article className="panel dashboard-metric">
              <span className="muted">Sisa Belum Dialokasikan</span>
              <strong>{formatCurrency(activeOverview?.remaining_amount ?? "0.00")}</strong>
              <small>Masih tersedia untuk pembagian unit</small>
            </article>
            <article className="panel dashboard-metric">
              <span className="muted">Committed Plan</span>
              <strong>{formatCurrency(activeOverview?.committed_amount ?? "0.00")}</strong>
              <small>Rencana APPROVED yang mengikat alokasi unit</small>
            </article>
            <article className="panel dashboard-metric">
              <span className="muted">Available Unit Budget</span>
              <strong>{formatCurrency(activeOverview?.available_amount ?? "0.00")}</strong>
              <small>Alokasi dikurangi committed plan</small>
            </article>
            <article className="panel dashboard-metric">
              <span className="muted">Draft Pipeline</span>
              <strong>{formatCurrency(activeOverview?.draft_pipeline_amount ?? "0.00")}</strong>
              <small>DRAFT + PENDING_APPROVAL, belum committed</small>
            </article>
            <article className="panel dashboard-metric">
              <span className="muted">Unit Teralokasi</span>
              <strong>{activeOverview?.allocations.length ?? 0}</strong>
              <small>Unit dengan alokasi pada {selectedFiscalYear.code}</small>
            </article>
          </section>

          <section className="panel-grid">
            <article className="panel">
              <span className="muted">Kesiapan Tahun Anggaran</span>
              <h2>{selectedFiscalYear.code}</h2>
              <ul className="check-list">
                <li>Status tahun: {selectedFiscalYear.status}</li>
                <li>Status Annual Budget: {activeOverview?.annual_budget_status ?? "Belum ada"}</li>
                <li>Alokasi unit tercatat: {activeOverview?.allocations.length ?? 0}</li>
                <li>Committed: {formatCurrency(activeOverview?.committed_amount ?? "0.00")}</li>
                <li>Available: {formatCurrency(activeOverview?.available_amount ?? "0.00")}</li>
              </ul>
            </article>
            <article className="panel">
              <span className="muted">Tahap Berikutnya</span>
              <h2>Rencana Anggaran Unit</h2>
              <p>
                Rencana APPROVED sekarang menjadi commitment resmi terhadap alokasi unit. Draft dan
                pengajuan yang belum disetujui tetap dipantau sebagai pipeline terpisah.
              </p>
            </article>
          </section>
        </>
      ) : null}
    </div>
  );
}
