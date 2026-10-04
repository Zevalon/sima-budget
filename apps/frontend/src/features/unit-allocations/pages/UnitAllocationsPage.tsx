import { type FormEvent, useEffect, useMemo, useState } from "react";

import { listOrganizationUnits } from "../../administration/api/admin";
import type { AdminOrganizationUnit } from "../../administration/types";
import { useAuth } from "../../auth/auth-context";
import { useFiscalYear } from "../../budget-foundation/fiscal-year-context";
import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import {
  createUnitAllocation,
  getUnitAllocationOverview,
  updateUnitAllocation,
} from "../api/unitAllocations";
import type { UnitAllocationOverview } from "../types";

import "../../../styles/unit-allocations.css";

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "") || "0";
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

export function UnitAllocationsPage() {
  const auth = useAuth();
  const fiscalYearContext = useFiscalYear();
  const selectedFiscalYear = fiscalYearContext.selectedFiscalYear;
  const permissions = useMemo(() => new Set(auth.user?.permissions ?? []), [auth.user]);
  const canCreate = permissions.has("unit_allocations.create");
  const canUpdate = permissions.has("unit_allocations.update");
  const [overview, setOverview] = useState<UnitAllocationOverview | null>(null);
  const [units, setUnits] = useState<AdminOrganizationUnit[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function reload() {
    if (!selectedFiscalYear) {
      setOverview(null);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const [overviewData, organizationUnits] = await Promise.all([
        getUnitAllocationOverview(selectedFiscalYear.id),
        listOrganizationUnits(),
      ]);
      setOverview(overviewData);
      setUnits(organizationUnits);
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat alokasi unit.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!selectedFiscalYear) return;

    let active = true;
    void Promise.all([getUnitAllocationOverview(selectedFiscalYear.id), listOrganizationUnits()])
      .then(([overviewData, organizationUnits]) => {
        if (!active) return;
        setOverview(overviewData);
        setUnits(organizationUnits);
        setLoading(false);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat alokasi unit.");
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedFiscalYear]);

  const activeOverview = overview?.fiscal_year_id === selectedFiscalYear?.id ? overview : null;
  const allocatedUnitIds = useMemo(
    () => new Set(activeOverview?.allocations.map((item) => item.organization_unit_id) ?? []),
    [activeOverview],
  );
  const receivableUnits = units.filter((unit) => unit.is_active && unit.can_receive_budget);
  const eligibleUnits = receivableUnits.filter((unit) => !allocatedUnitIds.has(unit.id));
  const canMutate =
    selectedFiscalYear?.status === "PLANNING" &&
    activeOverview?.annual_budget_status === "APPROVED";

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFiscalYear) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await createUnitAllocation({
        fiscal_year_id: selectedFiscalYear.id,
        organization_unit_id: getFormString(data, "organization_unit_id"),
        amount: getFormString(data, "amount"),
        notes: getFormString(data, "notes") || null,
      });
      form.reset();
      setSuccessMessage("Alokasi unit berhasil dibuat.");
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal membuat alokasi unit.");
    }
  }

  async function handleUpdate(
    event: FormEvent<HTMLFormElement>,
    allocationId: string,
    expectedVersion: number,
  ) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await updateUnitAllocation(allocationId, {
        expected_version: expectedVersion,
        amount: getFormString(data, "amount"),
        notes: getFormString(data, "notes") || null,
      });
      setSuccessMessage("Alokasi unit berhasil diperbarui.");
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal memperbarui alokasi unit.",
      );
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Budget Foundation</p>
          <h1>Alokasi Unit</h1>
          <p className="lead">
            Membagi anggaran tahunan yang telah disetujui ke unit organisasi penerima anggaran.
          </p>
        </div>
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}
      {successMessage ? <div className="success-alert">{successMessage}</div> : null}

      {!selectedFiscalYear ? (
        <section className="panel">
          <h2>Pilih Tahun Anggaran</h2>
          <p className="muted">Pilih Tahun Anggaran pada bagian atas aplikasi.</p>
        </section>
      ) : (
        <>
          <section className="panel allocation-summary">
            <div>
              <span className="muted">Tahun Anggaran</span>
              <strong>{selectedFiscalYear.code}</strong>
            </div>
            <div>
              <span className="muted">Pagu Disetujui</span>
              <strong>{formatCurrency(activeOverview?.annual_budget_amount ?? "0.00")}</strong>
            </div>
            <div>
              <span className="muted">Sudah Dialokasikan</span>
              <strong>{formatCurrency(activeOverview?.allocated_amount ?? "0.00")}</strong>
            </div>
            <div>
              <span className="muted">Sisa Belum Dialokasikan</span>
              <strong>{formatCurrency(activeOverview?.remaining_amount ?? "0.00")}</strong>
            </div>
            <div>
              <span className="muted">Committed Plan</span>
              <strong>{formatCurrency(activeOverview?.committed_amount ?? "0.00")}</strong>
            </div>
            <div>
              <span className="muted">Draft Pipeline</span>
              <strong>{formatCurrency(activeOverview?.draft_pipeline_amount ?? "0.00")}</strong>
            </div>
            <div>
              <span className="muted">Available untuk Plan</span>
              <strong>{formatCurrency(activeOverview?.available_amount ?? "0.00")}</strong>
            </div>
            <div>
              <span className="muted">Realized</span>
              <strong>{formatCurrency(activeOverview?.realized_amount ?? "0.00")}</strong>
            </div>
            <div>
              <span className="muted">Draft Realisasi</span>
              <strong>
                {formatCurrency(activeOverview?.realization_draft_pipeline_amount ?? "0.00")}
              </strong>
            </div>
            <div>
              <span className="muted">Sisa Direalisasi</span>
              <strong>
                {formatCurrency(activeOverview?.remaining_to_realize_amount ?? "0.00")}
              </strong>
            </div>
          </section>

          {loading ? <p className="muted">Memuat alokasi...</p> : null}

          {activeOverview && activeOverview.annual_budget_status !== "APPROVED" ? (
            <section className="panel">
              <h2>Anggaran Tahunan Belum Siap Dialokasikan</h2>
              <p className="muted">
                Annual Budget untuk {activeOverview.fiscal_year_code} harus berstatus APPROVED
                sebelum alokasi unit dapat dibuat.
              </p>
            </section>
          ) : null}

          {activeOverview && canCreate && canMutate && eligibleUnits.length > 0 ? (
            <form className="panel allocation-form" onSubmit={(event) => void handleCreate(event)}>
              <h2>Alokasi Unit Baru</h2>
              <label className="form-field">
                <span>Unit penerima</span>
                <select name="organization_unit_id" required defaultValue="">
                  <option value="" disabled>
                    Pilih unit
                  </option>
                  {eligibleUnits.map((unit) => (
                    <option value={unit.id} key={unit.id}>
                      {unit.code} · {unit.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                <span>Jumlah alokasi</span>
                <input name="amount" inputMode="decimal" placeholder="25000000000.00" required />
              </label>
              <label className="form-field allocation-span-2">
                <span>Catatan</span>
                <textarea name="notes" rows={3} placeholder="Catatan alokasi" />
              </label>
              <div className="allocation-actions">
                <button className="primary-button" type="submit">
                  Simpan Alokasi
                </button>
              </div>
            </form>
          ) : null}

          {activeOverview && canCreate && canMutate && eligibleUnits.length === 0 ? (
            <section className="panel allocation-guidance">
              {receivableUnits.length === 0 ? (
                <>
                  <h2>Belum Ada Unit Penerima Anggaran</h2>
                  <p className="muted">
                    Aktifkan opsi penerima anggaran pada Administration → Unit Organisasi agar unit
                    dapat dipilih untuk alokasi.
                  </p>
                </>
              ) : (
                <>
                  <h2>Semua Unit Sudah Memiliki Alokasi</h2>
                  <p className="muted">
                    Tidak ada unit penerima yang belum dialokasikan untuk tahun anggaran ini.
                    Gunakan formulir pada masing-masing unit untuk melakukan penyesuaian.
                  </p>
                </>
              )}
            </section>
          ) : null}

          {activeOverview && selectedFiscalYear.status !== "PLANNING" ? (
            <section className="panel allocation-guidance">
              <h2>Alokasi Terkunci</h2>
              <p className="muted">
                Alokasi hanya dapat dibuat atau diubah saat Tahun Anggaran berstatus PLANNING.
              </p>
            </section>
          ) : null}

          {activeOverview ? (
            <section className="panel">
              <div className="table-toolbar">
                <div>
                  <h2>Daftar Alokasi Unit</h2>
                  <span className="muted">{activeOverview.allocations.length} unit</span>
                </div>
                <span className="muted">Status tahun: {activeOverview.fiscal_year_status}</span>
              </div>
              {activeOverview.allocations.length === 0 ? (
                <p className="empty-state">Belum ada alokasi unit untuk tahun anggaran ini.</p>
              ) : (
                <div className="allocation-list">
                  {activeOverview.allocations.map((item) => (
                    <article className="allocation-card" key={item.id}>
                      <div className="allocation-card-header">
                        <div>
                          <strong>{item.organization_unit_name}</strong>
                          <span className="muted">{item.organization_unit_code}</span>
                        </div>
                        <div className="allocation-card-metrics">
                          <strong>{formatCurrency(item.amount)}</strong>
                          <span className="muted">
                            Committed {formatCurrency(item.committed_amount)}
                          </span>
                          <span className="muted">
                            Available {formatCurrency(item.available_amount)}
                          </span>
                          <span className="muted">
                            Pipeline {formatCurrency(item.draft_pipeline_amount)}
                          </span>
                          <span className="muted">
                            Realized {formatCurrency(item.realized_amount)}
                          </span>
                          <span className="muted">
                            Draft Realisasi {formatCurrency(item.realization_draft_pipeline_amount)}
                          </span>
                          <span className="muted">
                            Sisa Direalisasi {formatCurrency(item.remaining_to_realize_amount)}
                          </span>
                        </div>
                      </div>
                      {canUpdate && canMutate ? (
                        <form
                          className="allocation-edit-form"
                          onSubmit={(event) => void handleUpdate(event, item.id, item.version)}
                        >
                          <label className="form-field">
                            <span>Jumlah</span>
                            <input
                              name="amount"
                              inputMode="decimal"
                              defaultValue={item.amount}
                              required
                            />
                          </label>
                          <label className="form-field">
                            <span>Catatan</span>
                            <input name="notes" defaultValue={item.notes ?? ""} />
                          </label>
                          <button className="secondary-button" type="submit">
                            Simpan Perubahan
                          </button>
                        </form>
                      ) : (
                        <p className="muted">{item.notes || "Tidak ada catatan."}</p>
                      )}
                      <span className="muted">Versi {item.version}</span>
                    </article>
                  ))}
                </div>
              )}
            </section>
          ) : null}
        </>
      )}
    </div>
  );
}
