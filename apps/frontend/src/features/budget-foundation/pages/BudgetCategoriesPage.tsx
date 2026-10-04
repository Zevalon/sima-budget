import { type FormEvent, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import {
  createBudgetCategory,
  deactivateBudgetCategory,
  listBudgetCategories,
} from "../api/budgetFoundation";
import type { BudgetCategory } from "../types";

import "../../../styles/budget-foundation.css";

export function BudgetCategoriesPage() {
  const auth = useAuth();
  const canManage = (auth.user?.permissions ?? []).includes("budget_categories.manage");
  const [items, setItems] = useState<BudgetCategory[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function reload() {
    try {
      setItems(await listBudgetCategories());
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal memuat kategori anggaran.",
      );
    }
  }

  useEffect(() => {
    let active = true;
    void listBudgetCategories()
      .then((data) => {
        if (active) setItems(data);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat kategori anggaran.",
        );
      });
    return () => {
      active = false;
    };
  }, []);

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    try {
      await createBudgetCategory({
        code: getFormString(data, "code"),
        name: getFormString(data, "name"),
        description: getFormString(data, "description").trim() || null,
      });
      form.reset();
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal membuat kategori.");
    }
  }

  async function handleDeactivate(item: BudgetCategory) {
    if (!window.confirm(`Nonaktifkan kategori ${item.code}?`)) return;
    try {
      await deactivateBudgetCategory(item.id);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal menonaktifkan kategori.");
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Budget Foundation</p>
          <h1>Kategori Anggaran</h1>
          <p className="lead">Kategori digunakan pada item rencana anggaran.</p>
        </div>
      </section>
      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}
      {canManage ? (
        <form
          className="panel budget-foundation-form"
          onSubmit={(event) => void handleCreate(event)}
        >
          <h2>Buat Kategori</h2>
          <label className="form-field">
            <span>Kode</span>
            <input name="code" required />
          </label>
          <label className="form-field">
            <span>Nama</span>
            <input name="name" required />
          </label>
          <label className="form-field budget-span-2">
            <span>Deskripsi</span>
            <input name="description" />
          </label>
          <div className="budget-foundation-actions budget-span-2">
            <button className="primary-button" type="submit">
              Simpan Kategori
            </button>
          </div>
        </form>
      ) : null}
      <section className="panel">
        <div className="table-toolbar">
          <h2>Daftar Kategori</h2>
          <span className="muted">{items.length} kategori</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Kode</th>
                <th>Nama</th>
                <th>Deskripsi</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={5} className="empty-table-cell">
                    Belum ada kategori anggaran.
                  </td>
                </tr>
              ) : null}
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.code}</td>
                  <td>{item.name}</td>
                  <td>{item.description ?? "—"}</td>
                  <td>{item.is_active ? "Aktif" : "Nonaktif"}</td>
                  <td className="table-actions">
                    {canManage && item.is_active ? (
                      <button
                        className="danger-button"
                        type="button"
                        onClick={() => void handleDeactivate(item)}
                      >
                        Nonaktifkan
                      </button>
                    ) : null}
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
