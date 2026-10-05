import { useCallback, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { useFiscalYear } from "../../budget-foundation/fiscal-year-context";
import { getFinancialSummary } from "../api/reports";
import type { FinancialSummary } from "../types";
import "../../../styles/reports.css";

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "") || "0";
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

export function ReportsPage() {
  const fiscalYear = useFiscalYear();
  const selectedFiscalYear = fiscalYear.selectedFiscalYear;
  const [summary, setSummary] = useState<FinancialSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!selectedFiscalYear) {
      setSummary(null);
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    try {
      setSummary(await getFinancialSummary(selectedFiscalYear.id));
    } catch (error) {
      setSummary(null);
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat laporan anggaran.");
    } finally {
      setLoading(false);
    }
  }, [selectedFiscalYear]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const activeSummary = summary?.fiscal_year_id === selectedFiscalYear?.id ? summary : null;

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
          <section className="report-summary-grid">
            <article className="panel report-metric">
              <span className="muted">Pagu Scope</span>
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

          <section className="panel">
            <div className="report-section-heading">
              <div>
                <h2>Ringkasan Unit</h2>
                <span className="muted">{activeSummary.allocation_count} unit teralokasi</span>
              </div>
            </div>
            {activeSummary.unit_summaries.length === 0 ? (
              <p className="muted">Belum ada alokasi unit dalam scope ini.</p>
            ) : (
              <div className="table-scroll">
                <table className="report-table">
                  <thead>
                    <tr>
                      <th>Unit</th>
                      <th>Allocated</th>
                      <th>Committed</th>
                      <th>Realized</th>
                      <th>Available</th>
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
                        <td>{formatCurrency(item.realized_amount)}</td>
                        <td>{formatCurrency(item.available_amount)}</td>
                        <td>{item.utilization_percent}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="panel">
            <div className="report-section-heading">
              <div>
                <h2>Realisasi Bulanan</h2>
                <span className="muted">POSTED realization per bulan</span>
              </div>
            </div>
            <div className="monthly-grid">
              {activeSummary.monthly_realization.map((item) => (
                <article key={item.month}>
                  <span className="muted">{item.month_label}</span>
                  <strong>{formatCurrency(item.realized_amount)}</strong>
                </article>
              ))}
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
