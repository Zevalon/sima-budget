import { type FormEvent, useEffect, useMemo, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import { useFiscalYear } from "../../budget-foundation/fiscal-year-context";
import {
  createBudgetPlan,
  getBudgetPlanContext,
  listBudgetPlanApprovals,
  listBudgetPlans,
  reviseBudgetPlan,
  submitBudgetPlan,
  updateBudgetPlan,
} from "../api/budgetPlans";
import type {
  BudgetPlan,
  BudgetPlanApproval,
  BudgetPlanContext,
  BudgetPlanItemInput,
} from "../types";

import "../../../styles/budget-plans.css";

function formatCurrency(value: string): string {
  const [wholePart, fractionPart = "00"] = value.split(".");
  const normalizedWhole = wholePart.replace(/^0+(?=\d)/, "") || "0";
  const grouped = normalizedWhole.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const fraction = fractionPart.padEnd(2, "0").slice(0, 2);
  return `Rp ${grouped},${fraction}`;
}

type EditableItem = BudgetPlanItemInput & { key: number };

let nextItemKey = 1;

function newItem(context: BudgetPlanContext): EditableItem {
  return {
    key: nextItemKey++,
    budget_category_id: context.budget_categories[0]?.id ?? "",
    unit_of_measure_id: context.units_of_measure[0]?.id ?? "",
    description: "",
    quantity: "1",
    unit_price: "0.00",
    notes: null,
  };
}

function inputItems(items: EditableItem[]): BudgetPlanItemInput[] {
  return items.map((item) => ({
    budget_category_id: item.budget_category_id,
    unit_of_measure_id: item.unit_of_measure_id,
    description: item.description,
    quantity: item.quantity,
    unit_price: item.unit_price,
    notes: item.notes,
  }));
}

export function BudgetPlansPage() {
  const auth = useAuth();
  const fiscalYearContext = useFiscalYear();
  const selectedFiscalYear = fiscalYearContext.selectedFiscalYear;
  const permissions = useMemo(() => new Set(auth.user?.permissions ?? []), [auth.user]);
  const canCreate = permissions.has("budget_plans.create");
  const canUpdate = permissions.has("budget_plans.update");
  const canSubmit = permissions.has("budget_plans.submit");
  const canRevise = permissions.has("budget_plans.revise");
  const [context, setContext] = useState<BudgetPlanContext | null>(null);
  const [plans, setPlans] = useState<BudgetPlan[]>([]);
  const [createItems, setCreateItems] = useState<EditableItem[]>([]);
  const [editingPlanId, setEditingPlanId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editItems, setEditItems] = useState<EditableItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [approvalHistory, setApprovalHistory] = useState<Record<string, BudgetPlanApproval[]>>({});

  async function reload() {
    if (!selectedFiscalYear) {
      setContext(null);
      setPlans([]);
      return;
    }
    setLoading(true);
    setErrorMessage(null);
    try {
      const [contextData, planData] = await Promise.all([
        getBudgetPlanContext(selectedFiscalYear.id),
        listBudgetPlans(selectedFiscalYear.id),
      ]);
      setContext(contextData);
      setPlans(planData);
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat rencana anggaran.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!selectedFiscalYear) return;

    let active = true;
    void Promise.all([
      getBudgetPlanContext(selectedFiscalYear.id),
      listBudgetPlans(selectedFiscalYear.id),
    ])
      .then(([contextData, planData]) => {
        if (!active) return;
        setContext(contextData);
        setPlans(planData);
        setLoading(false);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat rencana anggaran.",
        );
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedFiscalYear]);

  const activeContext = context?.fiscal_year_id === selectedFiscalYear?.id ? context : null;
  const canMutate = activeContext?.fiscal_year_status === "PLANNING";
  const hasLookups =
    (activeContext?.budget_categories.length ?? 0) > 0 &&
    (activeContext?.units_of_measure.length ?? 0) > 0;

  function updateCreateItem(key: number, patch: Partial<EditableItem>) {
    setCreateItems((items) =>
      items.map((item) => (item.key === key ? { ...item, ...patch } : item)),
    );
  }

  function updateEditItem(key: number, patch: Partial<EditableItem>) {
    setEditItems((items) => items.map((item) => (item.key === key ? { ...item, ...patch } : item)));
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!activeContext || createItems.length === 0) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await createBudgetPlan({
        unit_allocation_id: getFormString(data, "unit_allocation_id"),
        title: getFormString(data, "title"),
        description: getFormString(data, "description") || null,
        items: inputItems(createItems),
      });
      form.reset();
      setCreateItems([]);
      setSuccessMessage("Draft rencana anggaran berhasil dibuat.");
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal membuat rencana anggaran.",
      );
    }
  }

  function beginEdit(plan: BudgetPlan) {
    setEditingPlanId(plan.id);
    setEditTitle(plan.title);
    setEditDescription(plan.description ?? "");
    setEditItems(
      plan.items.map((item) => ({
        key: nextItemKey++,
        budget_category_id: item.budget_category_id,
        unit_of_measure_id: item.unit_of_measure_id,
        description: item.description,
        quantity: item.quantity,
        unit_price: item.unit_price,
        notes: item.notes,
      })),
    );
  }

  async function handleUpdate(event: FormEvent<HTMLFormElement>, plan: BudgetPlan) {
    event.preventDefault();
    if (editItems.length === 0) return;
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const payload = {
        expected_row_version: plan.row_version,
        title: editTitle,
        description: editDescription || null,
        items: inputItems(editItems),
      };
      if (plan.status === "REJECTED") {
        await reviseBudgetPlan(plan.id, payload);
        setSuccessMessage("Revisi baru berhasil dibuat sebagai draft.");
      } else {
        await updateBudgetPlan(plan.id, payload);
        setSuccessMessage("Draft rencana anggaran berhasil diperbarui.");
      }
      setEditingPlanId(null);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal menyimpan rencana anggaran.",
      );
    }
  }

  async function loadApprovalHistory(plan: BudgetPlan) {
    setErrorMessage(null);
    try {
      const history = await listBudgetPlanApprovals(plan.id);
      setApprovalHistory((current) => ({ ...current, [plan.id]: history }));
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat riwayat approval.");
    }
  }

  async function handleSubmit(plan: BudgetPlan) {
    if (!window.confirm(`Ajukan ${plan.plan_number} versi ${plan.current_version_no}?`)) return;
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await submitBudgetPlan(plan.id);
      setSuccessMessage(`${plan.plan_number} berhasil diajukan untuk persetujuan.`);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal mengajukan rencana anggaran.",
      );
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Budget Planning</p>
          <h1>Rencana Anggaran</h1>
          <p className="lead">
            Menyusun draft rencana belanja unit berdasarkan alokasi yang tersedia.
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
          <section className="panel plan-summary">
            <div>
              <span className="muted">Tahun Anggaran</span>
              <strong>{selectedFiscalYear.code}</strong>
            </div>
            <div>
              <span className="muted">Status</span>
              <strong>{selectedFiscalYear.status}</strong>
            </div>
            <div>
              <span className="muted">Alokasi dalam Scope</span>
              <strong>{activeContext?.allocations.length ?? 0} unit</strong>
            </div>
            <div>
              <span className="muted">Draft Terlihat</span>
              <strong>{plans.length} rencana</strong>
            </div>
          </section>

          {loading ? <p className="muted">Memuat rencana anggaran...</p> : null}

          {activeContext &&
          canCreate &&
          canMutate &&
          hasLookups &&
          activeContext.allocations.length > 0 ? (
            <form className="panel plan-form" onSubmit={(event) => void handleCreate(event)}>
              <div className="table-toolbar plan-span-full">
                <div>
                  <h2>Buat Draft Rencana Anggaran</h2>
                  <span className="muted">
                    Draft belum mengurangi saldo committed. Commitment diterapkan pada fase
                    approval.
                  </span>
                </div>
              </div>
              <label className="form-field">
                <span>Unit / sumber alokasi</span>
                <select name="unit_allocation_id" required defaultValue="">
                  <option value="" disabled>
                    Pilih unit
                  </option>
                  {activeContext.allocations.map((item) => (
                    <option value={item.unit_allocation_id} key={item.unit_allocation_id}>
                      {item.organization_unit_code} · {item.organization_unit_name} ·{" "}
                      {formatCurrency(item.allocation_amount)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="form-field">
                <span>Judul rencana</span>
                <input name="title" required maxLength={250} />
              </label>
              <label className="form-field plan-span-full">
                <span>Deskripsi</span>
                <textarea name="description" rows={3} />
              </label>

              <div className="plan-items plan-span-full">
                <div className="table-toolbar">
                  <h3>Item Rencana</h3>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => setCreateItems((items) => [...items, newItem(activeContext)])}
                  >
                    Tambah Item
                  </button>
                </div>
                {createItems.length === 0 ? (
                  <p className="empty-state">Tambahkan minimal satu item rencana.</p>
                ) : null}
                {createItems.map((item) => (
                  <div className="plan-item-editor" key={item.key}>
                    <label className="form-field plan-item-description">
                      <span>Uraian</span>
                      <input
                        value={item.description}
                        required
                        onChange={(event) =>
                          updateCreateItem(item.key, { description: event.target.value })
                        }
                      />
                    </label>
                    <label className="form-field">
                      <span>Kategori</span>
                      <select
                        value={item.budget_category_id}
                        onChange={(event) =>
                          updateCreateItem(item.key, { budget_category_id: event.target.value })
                        }
                      >
                        {activeContext.budget_categories.map((option) => (
                          <option value={option.id} key={option.id}>
                            {option.code} · {option.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="form-field">
                      <span>Satuan</span>
                      <select
                        value={item.unit_of_measure_id}
                        onChange={(event) =>
                          updateCreateItem(item.key, { unit_of_measure_id: event.target.value })
                        }
                      >
                        {activeContext.units_of_measure.map((option) => (
                          <option value={option.id} key={option.id}>
                            {option.code} · {option.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="form-field">
                      <span>Qty</span>
                      <input
                        inputMode="decimal"
                        value={item.quantity}
                        required
                        onChange={(event) =>
                          updateCreateItem(item.key, { quantity: event.target.value })
                        }
                      />
                    </label>
                    <label className="form-field">
                      <span>Harga satuan</span>
                      <input
                        inputMode="decimal"
                        value={item.unit_price}
                        required
                        onChange={(event) =>
                          updateCreateItem(item.key, { unit_price: event.target.value })
                        }
                      />
                    </label>
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={() =>
                        setCreateItems((items) => items.filter((entry) => entry.key !== item.key))
                      }
                    >
                      Hapus
                    </button>
                  </div>
                ))}
              </div>
              <div className="plan-actions plan-span-full">
                <button
                  className="primary-button"
                  type="submit"
                  disabled={createItems.length === 0}
                >
                  Simpan Draft
                </button>
              </div>
            </form>
          ) : null}

          {activeContext && canCreate && canMutate && activeContext.allocations.length === 0 ? (
            <section className="panel">
              <h2>Belum Ada Alokasi yang Dapat Digunakan</h2>
              <p className="muted">
                User ini belum memiliki alokasi unit dalam scope untuk Tahun Anggaran tersebut.
              </p>
            </section>
          ) : null}

          {activeContext && selectedFiscalYear.status !== "PLANNING" ? (
            <section className="panel">
              <h2>Perencanaan Terkunci</h2>
              <p className="muted">
                Draft Rencana Anggaran hanya dapat dibuat atau diubah saat Tahun Anggaran PLANNING.
              </p>
            </section>
          ) : null}

          <section className="panel">
            <div className="table-toolbar">
              <div>
                <h2>Daftar Rencana Anggaran</h2>
                <span className="muted">{plans.length} rencana dalam scope Anda</span>
              </div>
            </div>
            {plans.length === 0 && !loading ? (
              <p className="empty-state">Belum ada rencana anggaran untuk Tahun Anggaran ini.</p>
            ) : null}
            <div className="plan-list">
              {plans.map((plan) => (
                <article className="plan-card" key={plan.id}>
                  <div className="plan-card-header">
                    <div>
                      <span className="muted">{plan.plan_number}</span>
                      <h3>{plan.title}</h3>
                      <span className="muted">
                        {plan.organization_unit_code} · {plan.organization_unit_name}
                      </span>
                    </div>
                    <div className="plan-card-total">
                      <span className={`status-pill status-${plan.status.toLowerCase()}`}>
                        {plan.status}
                      </span>
                      <strong>{formatCurrency(plan.total_amount)}</strong>
                      <span className="muted">
                        Alokasi {formatCurrency(plan.allocation_amount)}
                      </span>
                    </div>
                  </div>

                  {editingPlanId === plan.id ? (
                    <form
                      className="plan-edit"
                      onSubmit={(event) => void handleUpdate(event, plan)}
                    >
                      <label className="form-field">
                        <span>Judul</span>
                        <input
                          value={editTitle}
                          required
                          onChange={(event) => setEditTitle(event.target.value)}
                        />
                      </label>
                      <label className="form-field">
                        <span>Deskripsi</span>
                        <textarea
                          value={editDescription}
                          rows={3}
                          onChange={(event) => setEditDescription(event.target.value)}
                        />
                      </label>
                      <div className="plan-items">
                        <div className="table-toolbar">
                          <h4>Item Versi {plan.current_version_no}</h4>
                          {activeContext && hasLookups ? (
                            <button
                              className="secondary-button"
                              type="button"
                              onClick={() =>
                                setEditItems((items) => [...items, newItem(activeContext)])
                              }
                            >
                              Tambah Item
                            </button>
                          ) : null}
                        </div>
                        {editItems.map((item) => (
                          <div className="plan-item-editor" key={item.key}>
                            <label className="form-field plan-item-description">
                              <span>Uraian</span>
                              <input
                                value={item.description}
                                required
                                onChange={(event) =>
                                  updateEditItem(item.key, { description: event.target.value })
                                }
                              />
                            </label>
                            <label className="form-field">
                              <span>Kategori</span>
                              <select
                                value={item.budget_category_id}
                                onChange={(event) =>
                                  updateEditItem(item.key, {
                                    budget_category_id: event.target.value,
                                  })
                                }
                              >
                                {activeContext?.budget_categories.map((option) => (
                                  <option value={option.id} key={option.id}>
                                    {option.code} · {option.name}
                                  </option>
                                ))}
                              </select>
                            </label>
                            <label className="form-field">
                              <span>Satuan</span>
                              <select
                                value={item.unit_of_measure_id}
                                onChange={(event) =>
                                  updateEditItem(item.key, {
                                    unit_of_measure_id: event.target.value,
                                  })
                                }
                              >
                                {activeContext?.units_of_measure.map((option) => (
                                  <option value={option.id} key={option.id}>
                                    {option.code} · {option.name}
                                  </option>
                                ))}
                              </select>
                            </label>
                            <label className="form-field">
                              <span>Qty</span>
                              <input
                                inputMode="decimal"
                                value={item.quantity}
                                required
                                onChange={(event) =>
                                  updateEditItem(item.key, { quantity: event.target.value })
                                }
                              />
                            </label>
                            <label className="form-field">
                              <span>Harga satuan</span>
                              <input
                                inputMode="decimal"
                                value={item.unit_price}
                                required
                                onChange={(event) =>
                                  updateEditItem(item.key, { unit_price: event.target.value })
                                }
                              />
                            </label>
                            <button
                              className="secondary-button"
                              type="button"
                              onClick={() =>
                                setEditItems((items) =>
                                  items.filter((entry) => entry.key !== item.key),
                                )
                              }
                            >
                              Hapus
                            </button>
                          </div>
                        ))}
                      </div>
                      <div className="plan-actions">
                        <button
                          className="secondary-button"
                          type="button"
                          onClick={() => setEditingPlanId(null)}
                        >
                          Batal
                        </button>
                        <button
                          className="primary-button"
                          type="submit"
                          disabled={editItems.length === 0}
                        >
                          {plan.status === "REJECTED" ? "Simpan Revisi" : "Simpan Perubahan"}
                        </button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <p>{plan.description || "Tidak ada deskripsi."}</p>
                      {plan.rejection_reason ? (
                        <div className="form-alert">
                          <strong>Alasan penolakan:</strong> {plan.rejection_reason}
                        </div>
                      ) : null}
                      {plan.submitted_at && plan.status === "PENDING_APPROVAL" ? (
                        <p className="muted">
                          Diajukan {new Date(plan.submitted_at).toLocaleString("id-ID")}
                        </p>
                      ) : null}
                      {plan.approved_at && plan.status === "APPROVED" ? (
                        <p className="muted">
                          Disetujui {new Date(plan.approved_at).toLocaleString("id-ID")}
                        </p>
                      ) : null}
                      <div className="table-scroll">
                        <table className="data-table">
                          <thead>
                            <tr>
                              <th>#</th>
                              <th>Uraian</th>
                              <th>Kategori</th>
                              <th>Qty</th>
                              <th>Satuan</th>
                              <th>Harga</th>
                              <th>Jumlah</th>
                            </tr>
                          </thead>
                          <tbody>
                            {plan.items.map((item) => (
                              <tr key={item.id}>
                                <td>{item.line_no}</td>
                                <td>{item.description}</td>
                                <td>{item.budget_category_code}</td>
                                <td>{item.quantity}</td>
                                <td>{item.unit_of_measure_code}</td>
                                <td>{formatCurrency(item.unit_price)}</td>
                                <td>{formatCurrency(item.amount)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {approvalHistory[plan.id] ? (
                        <div className="approval-history">
                          <h4>Riwayat Approval</h4>
                          {approvalHistory[plan.id].length === 0 ? (
                            <p className="muted">Belum ada riwayat pengajuan.</p>
                          ) : (
                            <ul>
                              {approvalHistory[plan.id].map((approval) => (
                                <li key={approval.id}>
                                  Submission {approval.submission_no} · Versi {approval.version_no}{" "}
                                  · {approval.status}
                                  {approval.decision_note ? ` · ${approval.decision_note}` : ""}
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ) : null}
                      <div className="plan-card-footer">
                        <span className="muted">
                          Versi {plan.current_version_no} · Row {plan.row_version}
                        </span>
                        <div className="approval-actions">
                          {plan.status !== "DRAFT" ? (
                            <button
                              className="secondary-button"
                              type="button"
                              onClick={() => void loadApprovalHistory(plan)}
                            >
                              Riwayat Approval
                            </button>
                          ) : null}
                          {canUpdate && canMutate && plan.status === "DRAFT" ? (
                            <button
                              className="secondary-button"
                              type="button"
                              onClick={() => beginEdit(plan)}
                            >
                              Edit Draft
                            </button>
                          ) : null}
                          {canRevise && canMutate && plan.status === "REJECTED" ? (
                            <button
                              className="secondary-button"
                              type="button"
                              onClick={() => beginEdit(plan)}
                            >
                              Buat Revisi
                            </button>
                          ) : null}
                          {canSubmit && canMutate && plan.status === "DRAFT" ? (
                            <button
                              className="primary-button"
                              type="button"
                              onClick={() => void handleSubmit(plan)}
                            >
                              Ajukan
                            </button>
                          ) : null}
                        </div>
                      </div>
                    </>
                  )}
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
