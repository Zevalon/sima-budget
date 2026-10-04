import { type FormEvent, useEffect, useMemo, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString, getFormStrings } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import { createRole, listPermissions, listRoles } from "../api/admin";
import type { AdminPermission, AdminRole } from "../types";

export function RolesPage() {
  const auth = useAuth();
  const canCreate = (auth.user?.permissions ?? []).includes("roles.create");
  const [roles, setRoles] = useState<AdminRole[]>([]);
  const [permissions, setPermissions] = useState<AdminPermission[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const permissionsByModule = useMemo(() => {
    return permissions.reduce<Record<string, AdminPermission[]>>((groups, permission) => {
      groups[permission.module] ??= [];
      groups[permission.module].push(permission);
      return groups;
    }, {});
  }, [permissions]);

  async function reload() {
    try {
      const [nextRoles, nextPermissions] = await Promise.all([listRoles(), listPermissions()]);
      setRoles(nextRoles);
      setPermissions(nextPermissions);
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal memuat role dan permission.",
      );
    }
  }

  useEffect(() => {
    let active = true;

    void Promise.all([listRoles(), listPermissions()])
      .then(([nextRoles, nextPermissions]) => {
        if (!active) return;
        setRoles(nextRoles);
        setPermissions(nextPermissions);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat role dan permission.",
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
      await createRole({
        code: getFormString(data, "code"),
        name: getFormString(data, "name"),
        description: getFormString(data, "description").trim() || null,
        permission_codes: getFormStrings(data, "permission_codes"),
      });

      form.reset();
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal membuat role.");
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Administration</p>
          <h1>Role & Permission</h1>
          <p className="lead">Role aplikasi berbeda dari jabatan organisasi.</p>
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
          <h2 className="admin-form-title">Buat Role</h2>
          <label className="form-field">
            <span>Kode</span>
            <input name="code" required />
          </label>
          <label className="form-field">
            <span>Nama</span>
            <input name="name" required />
          </label>
          <label className="form-field admin-span-2">
            <span>Deskripsi</span>
            <input name="description" />
          </label>
          <fieldset className="permission-fieldset admin-span-2">
            <legend>Permission</legend>
            {Object.entries(permissionsByModule).map(([module, items]) => (
              <div className="permission-group" key={module}>
                <strong>{module}</strong>
                {items.map((permission) => (
                  <label key={permission.id}>
                    <input type="checkbox" name="permission_codes" value={permission.code} />
                    <span>
                      {permission.name} <small>{permission.code}</small>
                    </span>
                  </label>
                ))}
              </div>
            ))}
          </fieldset>
          <div className="admin-form-actions admin-span-2">
            <button className="primary-button" type="submit">
              Simpan Role
            </button>
          </div>
        </form>
      ) : null}

      <section className="panel">
        <div className="table-toolbar">
          <h2>Daftar Role</h2>
          <span className="muted">{roles.length} role</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Role</th>
                <th>Kode</th>
                <th>Tipe</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {roles.map((role) => (
                <tr key={role.id}>
                  <td>
                    <strong>{role.name}</strong>
                    <span className="table-subtext">{role.description ?? ""}</span>
                  </td>
                  <td>{role.code}</td>
                  <td>{role.is_system_role ? "System" : "Custom"}</td>
                  <td>{role.is_active ? "Aktif" : "Nonaktif"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
