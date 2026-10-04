import { type FormEvent, useEffect, useMemo, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import {
  createOrganizationUnit,
  deactivateOrganizationUnit,
  listOrganizationUnitTypes,
  listOrganizationUnits,
} from "../api/admin";
import type { AdminOrganizationUnit, AdminOrganizationUnitType } from "../types";

export function OrganizationUnitsPage() {
  const auth = useAuth();
  const permissions = new Set(auth.user?.permissions ?? []);
  const canCreate = permissions.has("organization_units.create");
  const canDeactivate = permissions.has("organization_units.deactivate");

  const [units, setUnits] = useState<AdminOrganizationUnit[]>([]);
  const [unitTypes, setUnitTypes] = useState<AdminOrganizationUnitType[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const activeUnits = useMemo(() => units.filter((unit) => unit.is_active), [units]);
  const activeTypes = useMemo(
    () => unitTypes.filter((unitType) => unitType.is_active),
    [unitTypes],
  );

  async function reload() {
    try {
      const [nextUnits, nextTypes] = await Promise.all([
        listOrganizationUnits(),
        listOrganizationUnitTypes(),
      ]);
      setUnits(nextUnits);
      setUnitTypes(nextTypes);
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat unit organisasi.");
    }
  }

  useEffect(() => {
    let active = true;

    void Promise.all([listOrganizationUnits(), listOrganizationUnitTypes()])
      .then(([nextUnits, nextTypes]) => {
        if (!active) return;
        setUnits(nextUnits);
        setUnitTypes(nextTypes);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat unit organisasi.",
        );
      });

    return () => {
      active = false;
    };
  }, []);

  async function submitCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const form = event.currentTarget;
    const data = new FormData(form);

    setErrorMessage(null);

    try {
      await createOrganizationUnit({
        parent_id: getFormString(data, "parent_id") || null,
        unit_type_id: getFormString(data, "unit_type_id"),
        code: getFormString(data, "code"),
        name: getFormString(data, "name"),
        can_receive_budget: data.get("can_receive_budget") === "on",
        can_create_budget_plan: data.get("can_create_budget_plan") === "on",
      });

      form.reset();
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal membuat unit organisasi.");
    }
  }

  async function handleDeactivate(unitId: string) {
    if (!window.confirm("Nonaktifkan unit organisasi ini?")) {
      return;
    }

    try {
      await deactivateOrganizationUnit(unitId);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal menonaktifkan unit.");
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Administration</p>
          <h1>Unit Organisasi</h1>
          <p className="lead">
            Hierarchy unit bersifat generik dan tidak dikunci hanya untuk struktur universitas.
          </p>
        </div>
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}

      {canCreate ? (
        <form
          className="panel admin-form-grid"
          onSubmit={(event) => {
            void submitCreate(event);
          }}
        >
          <h2 className="admin-form-title">Buat Unit</h2>
          <label className="form-field">
            <span>Kode</span>
            <input name="code" required />
          </label>
          <label className="form-field">
            <span>Nama unit</span>
            <input name="name" required />
          </label>
          <label className="form-field">
            <span>Tipe unit</span>
            <select name="unit_type_id" required>
              <option value="">Pilih tipe</option>
              {activeTypes.map((unitType) => (
                <option value={unitType.id} key={unitType.id}>
                  {unitType.name}
                </option>
              ))}
            </select>
          </label>
          <label className="form-field">
            <span>Parent</span>
            <select name="parent_id">
              <option value="">Tanpa parent</option>
              {activeUnits.map((unit) => (
                <option value={unit.id} key={unit.id}>
                  {unit.name}
                </option>
              ))}
            </select>
          </label>
          <label className="checkbox-field">
            <input type="checkbox" name="can_receive_budget" />
            <span>Dapat menerima alokasi anggaran</span>
          </label>
          <label className="checkbox-field">
            <input type="checkbox" name="can_create_budget_plan" />
            <span>Dapat membuat rencana anggaran</span>
          </label>
          <div className="admin-form-actions admin-span-2">
            <button className="primary-button" type="submit">
              Simpan Unit
            </button>
          </div>
        </form>
      ) : null}

      <section className="panel">
        <div className="table-toolbar">
          <h2>Struktur Unit</h2>
          <span className="muted">{units.length} unit</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Unit</th>
                <th>Kode</th>
                <th>Tipe</th>
                <th>Budget</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {units.map((unit) => (
                <tr key={unit.id}>
                  <td>{unit.name}</td>
                  <td>{unit.code}</td>
                  <td>{unit.unit_type_name}</td>
                  <td>
                    {unit.can_receive_budget ? "Alokasi" : "—"}
                    {unit.can_create_budget_plan ? " / Rencana" : ""}
                  </td>
                  <td>{unit.is_active ? "Aktif" : "Nonaktif"}</td>
                  <td className="table-actions">
                    {canDeactivate && unit.is_active && unit.code !== "ROOT" ? (
                      <button
                        className="danger-button"
                        type="button"
                        onClick={() => {
                          void handleDeactivate(unit.id);
                        }}
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
