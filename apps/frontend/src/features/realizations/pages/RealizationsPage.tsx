import { type FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import { useFiscalYear } from "../../budget-foundation/fiscal-year-context";
import {
  createRealization,
  getRealizationContext,
  listRealizations,
  postRealization,
  updateRealization,
} from "../api/realizations";
import type { Realization, RealizationContext } from "../types";

import "../../../styles/realizations.css";

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "") || "0";
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

function messageFromError(error: unknown): string {
  return error instanceof ApiError ? error.message : "Permintaan tidak dapat diproses.";
}

export function RealizationsPage() {
  const auth = useAuth();
  const { selectedFiscalYear } = useFiscalYear();
  const permissions = useMemo(() => new Set(auth.user?.permissions ?? []), [auth.user]);
  const canCreate = permissions.has("realizations.create");
  const canUpdate = permissions.has("realizations.update");
  const canPost = permissions.has("realizations.post");

  const [context, setContext] = useState<RealizationContext | null>(null);
  const [items, setItems] = useState<Realization[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!selectedFiscalYear) {
      setContext(null);
      setItems([]);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const [nextContext, nextItems] = await Promise.all([
        getRealizationContext(selectedFiscalYear.id),
        listRealizations(selectedFiscalYear.id),
      ]);
      setContext(nextContext);
      setItems(nextItems);
    } catch (error) {
      setErrorMessage(messageFromError(error));
    } finally {
      setLoading(false);
    }
  }, [selectedFiscalYear]);

  useEffect(() => {
    void reload();
  }, [reload]);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setMessage(null);
    setErrorMessage(null);
    try {
      await createRealization({
        budget_plan_id: getFormString(data, "budget_plan_id"),
        realization_date: getFormString(data, "realization_date"),
        reference_number: getFormString(data, "reference_number"),
        description: getFormString(data, "description"),
        vendor_name: getFormString(data, "vendor_name").trim() || null,
        amount: getFormString(data, "amount"),
      });
      form.reset();
      setMessage("Draft realisasi berhasil dibuat.");
      await reload();
    } catch (error) {
      setErrorMessage(messageFromError(error));
    }
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>, item: Realization) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setMessage(null);
    setErrorMessage(null);
    try {
      await updateRealization(item.id, {
        expected_row_version: item.row_version,
        realization_date: getFormString(data, "realization_date"),
        reference_number: getFormString(data, "reference_number"),
        description: getFormString(data, "description"),
        vendor_name: getFormString(data, "vendor_name").trim() || null,
        amount: getFormString(data, "amount"),
      });
      setMessage("Draft realisasi berhasil diperbarui.");
      await reload();
    } catch (error) {
      setErrorMessage(messageFromError(error));
    }
  }

  async function handlePost(item: Realization) {
    if (
      !window.confirm(`Posting ${item.realization_number}? Setelah posting data akan terkunci.`)
    ) {
      return;
    }
    setMessage(null);
    setErrorMessage(null);
    try {
      await postRealization(item.id, item.row_version);
      setMessage("Realisasi berhasil diposting.");
      await reload();
    } catch (error) {
      setErrorMessage(messageFromError(error));
    }
  }

  const isActive = selectedFiscalYear?.status === "ACTIVE";

  return (
    <div className="realization-page">
      <header className="page-header">
        <div>
          <span className="eyebrow">BUDGET EXECUTION</span>
          <h1>Realisasi Anggaran</h1>
          <p className="muted">Mencatat pelaksanaan dari Rencana Anggaran yang telah disetujui.</p>
        </div>
      </header>

      {message ? <div className="success-banner">{message}</div> : null}
      {errorMessage ? <div className="error-banner">{errorMessage}</div> : null}

      {!selectedFiscalYear ? (
        <section className="panel">
          <p className="empty-state">Pilih Tahun Anggaran untuk melihat realisasi.</p>
        </section>
      ) : loading && !context ? (
        <p className="muted">Memuat realisasi...</p>
      ) : (
        <>
          <section className="realization-summary">
            <div>
              <span className="muted">Rencana Disetujui</span>
              <strong>{formatCurrency(context?.scope_approved_amount ?? "0")}</strong>
            </div>
            <div>
              <span className="muted">Sudah Direalisasi</span>
              <strong>{formatCurrency(context?.scope_realized_amount ?? "0")}</strong>
            </div>
            <div>
              <span className="muted">Draft Realisasi</span>
              <strong>{formatCurrency(context?.scope_draft_pipeline_amount ?? "0")}</strong>
            </div>
            <div>
              <span className="muted">Sisa Dapat Direalisasi</span>
              <strong>{formatCurrency(context?.scope_remaining_amount ?? "0")}</strong>
            </div>
          </section>

          {!isActive ? (
            <section className="panel realization-guidance">
              <h2>Realisasi Terkunci</h2>
              <p className="muted">
                Pencatatan realisasi hanya tersedia saat Tahun Anggaran berstatus ACTIVE.
              </p>
            </section>
          ) : null}

          {isActive && canCreate && context && context.plans.length > 0 ? (
            <form className="panel realization-form" onSubmit={(event) => void handleCreate(event)}>
              <h2>Draft Realisasi Baru</h2>
              <label className="form-field realization-span-2">
                <span>Rencana Anggaran APPROVED</span>
                <select name="budget_plan_id" required defaultValue="">
                  <option value="" disabled>
                    Pilih rencana anggaran
                  </option>
                  {context.plans.map((plan) => (
                    <option value={plan.budget_plan_id} key={plan.budget_plan_id}>
                      {plan.organization_unit_code} · {plan.plan_number} · sisa{" "}
                      {formatCurrency(plan.remaining_amount)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                <span>Tanggal realisasi</span>
                <input name="realization_date" type="date" required />
              </label>
              <label className="form-field">
                <span>Nomor dokumen / referensi</span>
                <input name="reference_number" maxLength={120} required />
              </label>
              <label className="form-field realization-span-2">
                <span>Deskripsi</span>
                <input name="description" maxLength={500} required />
              </label>
              <label className="form-field">
                <span>Vendor (opsional)</span>
                <input name="vendor_name" maxLength={250} />
              </label>
              <label className="form-field">
                <span>Jumlah realisasi</span>
                <input name="amount" inputMode="decimal" placeholder="1000000.00" required />
              </label>
              <div className="realization-actions realization-span-2">
                <button className="primary-button" type="submit">
                  Simpan Draft
                </button>
              </div>
            </form>
          ) : null}

          {isActive && canCreate && context && context.plans.length === 0 ? (
            <section className="panel realization-guidance">
              <h2>Belum Ada Rencana APPROVED</h2>
              <p className="muted">
                Realisasi baru dapat dibuat setelah ada Rencana Anggaran APPROVED dalam scope Anda.
              </p>
            </section>
          ) : null}

          <section className="panel">
            <div className="table-toolbar">
              <div>
                <h2>Daftar Realisasi</h2>
                <span className="muted">{items.length} record</span>
              </div>
              <span className="muted">Status tahun: {selectedFiscalYear.status}</span>
            </div>

            {items.length === 0 ? (
              <p className="empty-state">Belum ada realisasi untuk tahun anggaran ini.</p>
            ) : (
              <div className="realization-list">
                {items.map((item) => (
                  <article className="realization-card" key={item.id}>
                    <div className="realization-card-header">
                      <div>
                        <strong>{item.realization_number}</strong>
                        <span className="muted">
                          {item.organization_unit_code} · {item.plan_number}
                        </span>
                      </div>
                      <span className={`status-pill status-${item.status.toLowerCase()}`}>
                        {item.status}
                      </span>
                    </div>

                    <div className="realization-plan-metrics">
                      <span>Plan {formatCurrency(item.plan_approved_amount)}</span>
                      <span>Realized {formatCurrency(item.plan_realized_amount)}</span>
                      <span>Remaining {formatCurrency(item.plan_remaining_amount)}</span>
                    </div>

                    {item.status === "DRAFT" && canUpdate && isActive ? (
                      <form
                        className="realization-edit-form"
                        onSubmit={(event) => void handleUpdate(event, item)}
                      >
                        <label className="form-field">
                          <span>Tanggal</span>
                          <input
                            name="realization_date"
                            type="date"
                            defaultValue={item.realization_date}
                            required
                          />
                        </label>
                        <label className="form-field">
                          <span>Referensi</span>
                          <input
                            name="reference_number"
                            defaultValue={item.reference_number}
                            required
                          />
                        </label>
                        <label className="form-field realization-span-2">
                          <span>Deskripsi</span>
                          <input name="description" defaultValue={item.description} required />
                        </label>
                        <label className="form-field">
                          <span>Vendor</span>
                          <input name="vendor_name" defaultValue={item.vendor_name ?? ""} />
                        </label>
                        <label className="form-field">
                          <span>Jumlah</span>
                          <input
                            name="amount"
                            inputMode="decimal"
                            defaultValue={item.amount}
                            required
                          />
                        </label>
                        <div className="realization-actions realization-span-2">
                          <button className="secondary-button" type="submit">
                            Simpan Perubahan
                          </button>
                          {canPost ? (
                            <button
                              className="primary-button"
                              type="button"
                              onClick={() => void handlePost(item)}
                            >
                              Posting Realisasi
                            </button>
                          ) : null}
                        </div>
                      </form>
                    ) : (
                      <div className="realization-readonly">
                        <p>{item.description}</p>
                        <span className="muted">
                          {item.realization_date} · {item.reference_number}
                          {item.vendor_name ? ` · ${item.vendor_name}` : ""}
                        </span>
                        <strong>{formatCurrency(item.amount)}</strong>
                      </div>
                    )}
                    <span className="muted">Versi record {item.row_version}</span>
                  </article>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
