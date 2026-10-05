import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { useFiscalYear } from "../../budget-foundation/fiscal-year-context";
import { getFinancialSummary } from "../api/reports";
import type { FinancialSummary, ReportMonthlyRealization } from "../types";
import "../../../styles/reports.css";

type ReportFilters = {
  fiscalYearId: string;
  organizationUnitId: string;
  month: string;
  categoryId: string;
};

const EMPTY_FILTERS: ReportFilters = {
  fiscalYearId: "",
  organizationUnitId: "",
  month: "",
  categoryId: "",
};

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "") || "0";
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

function barWidth(item: ReportMonthlyRealization, maximum: number): string {
  if (maximum <= 0) {
    return "0%";
  }
  return `${Math.max((Number(item.realized_amount) / maximum) * 100, 2)}%`;
}

export function ReportsPage() {
  const fiscalYear = useFiscalYear();
  const selectedFiscalYear = fiscalYear.selectedFiscalYear;
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [filters, setFilters] = useState<ReportFilters>(EMPTY_FILTERS);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const requestSequence = useRef(0);

  const currentFilters =
    selectedFiscalYear && filters.fiscalYearId === selectedFiscalYear.id
      ? filters
      : {
          ...EMPTY_FILTERS,
          fiscalYearId: selectedFiscalYear?.id ?? "",
        };

  const reload = useCallback(async () => {
    if (!selectedFiscalYear) {
      setSummary(null);
      return;
    }

    const requestId = requestSequence.current + 1;
    requestSequence.current = requestId;
    setLoading(true);
    setErrorMessage(null);

    try {
      const result = await getFinancialSummary(
        selectedFiscalYear.id,
        currentFilters.organizationUnitId || undefined,
      );
      if (requestSequence.current === requestId) {
        setSummary(result);
      }
    } catch (error) {
      if (requestSequence.current === requestId) {
        setSummary(null);
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat laporan anggaran.",
        );
      }
    } finally {
      if (requestSequence.current === requestId) {
        setLoading(false);
      }
    }
  }, [currentFilters.organizationUnitId, selectedFiscalYear]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const activeSummary =
    summary !== null &&
    summary.fiscal_year_id === selectedFiscalYear?.id &&
    (summary.organization_unit_filter_id ?? "") === currentFilters.organizationUnitId
      ? summary
      : null;

  const selectedCategoryId = activeSummary?.category_plan_summaries.some(
    (item) => item.budget_category_id === currentFilters.categoryId,
  )
    ? currentFilters.categoryId
    : "";

  const visibleCategories = useMemo(() => {
    if (!activeSummary) {
      return [];
    }
    if (!selectedCategoryId) {
      return activeSummary.category_plan_summaries;
    }
    return activeSummary.category_plan_summaries.filter(
      (item) => item.budget_category_id === selectedCategoryId,
    );
  }, [activeSummary, selectedCategoryId]);

  const visibleMonths = useMemo(() => {
    if (!activeSummary) {
      return [];
    }
    if (!currentFilters.month) {
      return activeSummary.monthly_realization;
    }
    return activeSummary.monthly_realization.filter(
      (item) => String(item.month) === currentFilters.month,
    );
  }, [activeSummary, currentFilters.month]);

  const maximumMonthlyAmount = useMemo(
    () =>
      Math.max(
        0,
        ...(activeSummary?.monthly_realization.map((item) => Number(item.realized_amount)) ?? []),
      ),
    [activeSummary],
  );

  const selectedUnitName =
    activeSummary?.unit_filter_options.find(
      (item) => item.organization_unit_id === currentFilters.organizationUnitId,
    )?.organization_unit_name ?? null;

  function updateFilters(next: Partial<ReportFilters>) {
    setFilters((previous) => ({
      ...previous,
      ...next,
      fiscalYearId: selectedFiscalYear?.id ?? "",
    }));
  }

  function resetFilters() {
    setFilters({
      ...EMPTY_FILTERS,
      fiscalYearId: selectedFiscalYear?.id ?? "",
    });
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Monitoring & Reporting</p>
          <h1>Laporan Anggaran</h1>
          <p className="lead">
            Ringkasan finansial terkanonisasi berdasarkan scope organisasi yang diberikan kepada
            pengguna.
          </p>
        </div>
        <span className="status-badge">
          {selectedFiscalYear ? selectedFiscalYear.status : "Pilih Tahun"}
        </span>
      </section>

      <nav className="report-section-nav" aria-label="Bagian laporan">
        <a href="#ringkasan">Ringkasan</a>
        <a href="#unit">Unit</a>
        <a href="#bulanan">Bulanan</a>
        <a href="#kategori">Kategori</a>
      </nav>

      <section className="panel report-filter-panel" aria-label="Filter laporan">
        <div className="report-filter-heading">
          <div>
            <h2>Filter Laporan</h2>
            <p className="muted">
              Filter unit dihitung ulang oleh server sesuai scope. Filter bulan dan kategori
              membatasi breakdown yang ditampilkan.
            </p>
          </div>
          <button className="secondary-button" type="button" onClick={resetFilters}>
            Reset Filter
          </button>
        </div>

        <div className="report-filter-grid">
          <label>
            <span>Unit organisasi</span>
            <select
              aria-label="Unit organisasi"
              value={currentFilters.organizationUnitId}
              disabled={!activeSummary || loading}
              onChange={(event) =>
                updateFilters({
                  organizationUnitId: event.target.value,
                  categoryId: "",
                })
              }
            >
              <option value="">Semua unit dalam scope</option>
              {activeSummary?.unit_filter_options.map((item) => (
                <option key={item.organization_unit_id} value={item.organization_unit_id}>
                  {item.organization_unit_code} · {item.organization_unit_name}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Bulan realisasi</span>
            <select
              aria-label="Bulan realisasi"
              value={currentFilters.month}
              disabled={!activeSummary}
              onChange={(event) => updateFilters({ month: event.target.value })}
            >
              <option value="">Semua bulan</option>
              {activeSummary?.monthly_realization.map((item) => (
                <option key={item.month} value={String(item.month)}>
                  {item.month_label}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Kategori anggaran</span>
            <select
              aria-label="Kategori anggaran"
              value={selectedCategoryId}
              disabled={!activeSummary || activeSummary.category_plan_summaries.length === 0}
              onChange={(event) => updateFilters({ categoryId: event.target.value })}
            >
              <option value="">Semua kategori</option>
              {activeSummary?.category_plan_summaries.map((item) => (
                <option key={item.budget_category_id} value={item.budget_category_id}>
                  {item.budget_category_code} · {item.budget_category_name}
                </option>
              ))}
            </select>
          </label>
        </div>

        {selectedUnitName ? (
          <p className="filter-active-note">Filter unit aktif: {selectedUnitName}</p>
        ) : null}
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}
      {loading ? <section className="panel">Memuat laporan...</section> : null}

      {!selectedFiscalYear ? (
        <section className="panel">
          <h2>Belum Ada Tahun Anggaran Terpilih</h2>
          <p className="muted">Pilih Tahun Anggaran pada bagian atas aplikasi.</p>
        </section>
      ) : null}

      {selectedFiscalYear && !loading && activeSummary ? (
        <>
          <section className="report-summary-grid" id="ringkasan">
            <article className="panel report-metric">
              <span className="muted">
                {currentFilters.organizationUnitId ? "Pagu Unit" : "Pagu Scope"}
              </span>
              <strong>{formatCurrency(activeSummary.scope_budget_amount)}</strong>
            </article>
            <article className="panel report-metric">
              <span className="muted">Allocated</span>
              <strong>{formatCurrency(activeSummary.allocated_amount)}</strong>
            </article>
            <article className="panel report-metric">
              <span className="muted">Committed</span>
              <strong>{formatCurrency(activeSummary.committed_amount)}</strong>
            </article>
            <article className="panel report-metric">
              <span className="muted">Realized</span>
              <strong>{formatCurrency(activeSummary.realized_amount)}</strong>
            </article>
            <article className="panel report-metric">
              <span className="muted">Available</span>
              <strong>{formatCurrency(activeSummary.available_amount)}</strong>
            </article>
            <article className="panel report-metric">
              <span className="muted">Sisa Direalisasi</span>
              <strong>{formatCurrency(activeSummary.remaining_to_realize_amount)}</strong>
            </article>
            <article className="panel report-metric">
              <span className="muted">Draft Plan Pipeline</span>
              <strong>{formatCurrency(activeSummary.draft_pipeline_amount)}</strong>
            </article>
            <article className="panel report-metric">
              <span className="muted">Draft Realization Pipeline</span>
              <strong>{formatCurrency(activeSummary.realization_draft_pipeline_amount)}</strong>
            </article>
            <article className="panel report-metric">
              <span className="muted">Utilization</span>
              <strong>{activeSummary.utilization_percent}%</strong>
            </article>
          </section>

          <section className="panel" id="unit">
            <div className="report-section-heading">
              <div>
                <h2>Ringkasan Unit</h2>
                <span className="muted">
                  {activeSummary.allocation_count} unit teralokasi dalam hasil saat ini
                </span>
              </div>
            </div>
            {activeSummary.unit_summaries.length === 0 ? (
              <p className="muted">Belum ada alokasi unit untuk filter ini.</p>
            ) : (
              <div className="table-scroll">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>Unit</th>
                      <th>Allocated</th>
                      <th>Committed</th>
                      <th>Plan Pipeline</th>
                      <th>Realized</th>
                      <th>Realization Pipeline</th>
                      <th>Available</th>
                      <th>Sisa Direalisasi</th>
                      <th>Utilization</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeSummary.unit_summaries.map((item) => (
                      <tr key={item.organization_unit_id}>
                        <td>
                          <strong>{item.organization_unit_code}</strong>
                          <span className="muted report-unit-name">
                            {item.organization_unit_name}
                          </span>
                        </td>
                        <td>{formatCurrency(item.allocated_amount)}</td>
                        <td>{formatCurrency(item.committed_amount)}</td>
                        <td>{formatCurrency(item.draft_pipeline_amount)}</td>
                        <td>{formatCurrency(item.realized_amount)}</td>
                        <td>{formatCurrency(item.realization_draft_pipeline_amount)}</td>
                        <td>{formatCurrency(item.available_amount)}</td>
                        <td>{formatCurrency(item.remaining_to_realize_amount)}</td>
                        <td>{item.utilization_percent}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="panel" id="bulanan">
            <div className="report-section-heading">
              <div>
                <h2>Realisasi Bulanan</h2>
                <span className="muted">
                  POSTED realization per bulan
                  {currentFilters.month ? " · filter bulan aktif" : ""}
                </span>
              </div>
            </div>
            <div className="monthly-chart">
              {visibleMonths.map((item) => (
                <article key={item.month} aria-label={`Realisasi ${item.month_label}`}>
                  <div className="monthly-chart-label">
                    <span>{item.month_label}</span>
                    <strong>{formatCurrency(item.realized_amount)}</strong>
                  </div>
                  <div className="monthly-chart-track" aria-hidden="true">
                    <span
                      className="monthly-chart-bar"
                      style={{ width: barWidth(item, maximumMonthlyAmount) }}
                    />
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="panel" id="kategori">
            <div className="report-section-heading">
              <div>
                <h2>Ringkasan Kategori</h2>
                <span className="muted">
                  Commitment dan draft plan pipeline dari item rencana anggaran.
                </span>
              </div>
            </div>
            <div className="report-info-note">
              Realized per kategori belum dihitung karena realisasi saat ini dicatat pada level
              Budget Plan, bukan pada item/kategori. SIMA tidak mengalokasikan nilai realisasi ke
              kategori secara asumsi.
            </div>
            {visibleCategories.length === 0 ? (
              <p className="muted">Belum ada data kategori untuk filter ini.</p>
            ) : (
              <div className="table-scroll">
                <table className="report-table report-category-table">
                  <thead>
                    <tr>
                      <th>Kategori</th>
                      <th>Committed</th>
                      <th>Draft Plan Pipeline</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleCategories.map((item) => (
                      <tr key={item.budget_category_id}>
                        <td>
                          <strong>{item.budget_category_code}</strong>
                          <span className="muted report-unit-name">
                            {item.budget_category_name}
                          </span>
                        </td>
                        <td>{formatCurrency(item.committed_amount)}</td>
                        <td>{formatCurrency(item.draft_pipeline_amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      ) : null}
    </div>
  );
}
