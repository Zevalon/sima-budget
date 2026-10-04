import { type FormEvent, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import {
  createUnitOfMeasure,
  deactivateUnitOfMeasure,
  listUnitsOfMeasure,
} from "../api/budgetFoundation";
import type { UnitOfMeasure } from "../types";

import "../../../styles/budget-foundation.css";

export function UnitsOfMeasurePage() {
  const auth = useAuth();
  const canManage = (auth.user?.permissions ?? []).includes("units_of_measure.manage");
  const [items, setItems] = useState<UnitOfMeasure[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function reload() {
    try {
      setItems(await listUnitsOfMeasure());
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat satuan.");
    }
  }

  useEffect(() => {
    let active = true;
    void listUnitsOfMeasure()
      .then((data) => {
        if (active) setItems(data);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat satuan.");
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
      await createUnitOfMeasure({
        code: getFormString(data, "code"),
        name: getFormString(data, "name"),
      });
      form.reset();
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal membuat satuan.");
    }
  }

  async function handleDeactivate(item: UnitOfMeasure) {
    if (!window.confirm(`Nonaktifkan satuan ${item.code}?`)) return;
    try {
      await deactivateUnitOfMeasure(item.id);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal menonaktifkan satuan.");
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Budget Foundation</p>
          <h1>Satuan</h1>
          <p className="lead">Satuan quantity untuk item rencana anggaran.</p>
        </div>
      </section>
      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}
      {canManage ? (
        <form
          className="panel budget-foundation-form"
          onSubmit={(event) => void handleCreate(event)}
        >
          <h2>Buat Satuan</h2>
          <label className="form-field">
            <span>Kode</span>
            <input name="code" placeholder="UNIT" required />
          </label>
          <label className="form-field">
            <span>Nama</span>
            <input name="name" placeholder="Unit" required />
          </label>
          <div className="budget-foundation-actions budget-span-2">
            <button className="primary-button" type="submit">
              Simpan Satuan
            </button>
          </div>
        </form>
      ) : null}
      <section className="panel">
        <div className="table-toolbar">
          <h2>Daftar Satuan</h2>
          <span className="muted">{items.length} satuan</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Kode</th>
                <th>Nama</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={4} className="empty-table-cell">
                    Belum ada satuan.
                  </td>
                </tr>
              ) : null}
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{item.code}</td>
                  <td>{item.name}</td>
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
