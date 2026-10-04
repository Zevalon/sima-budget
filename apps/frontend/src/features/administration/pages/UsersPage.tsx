import { type FormEvent, useEffect, useMemo, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import {
  createUser,
  deactivateUser,
  listOrganizationUnits,
  listRoles,
  listUsers,
  revokeUserSessions,
} from "../api/admin";
import type { AdminOrganizationUnit, AdminRole, AdminUser } from "../types";

export function UsersPage() {
  const auth = useAuth();
  const permissions = new Set(auth.user?.permissions ?? []);
  const canCreate = permissions.has("users.create");
  const canDeactivate = permissions.has("users.deactivate");
  const canRevokeSessions = permissions.has("sessions.revoke");

  const [users, setUsers] = useState<AdminUser[]>([]);
  const [roles, setRoles] = useState<AdminRole[]>([]);
  const [units, setUnits] = useState<AdminOrganizationUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const activeRoles = useMemo(() => roles.filter((role) => role.is_active), [roles]);
  const activeUnits = useMemo(() => units.filter((unit) => unit.is_active), [units]);

  async function reload() {
    setLoading(true);
    setErrorMessage(null);

    try {
      const [nextUsers, nextRoles, nextUnits] = await Promise.all([
        listUsers(),
        listRoles(),
        listOrganizationUnits(),
      ]);
      setUsers(nextUsers);
      setRoles(nextRoles);
      setUnits(nextUnits);
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal memuat data administrasi.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;

    void Promise.all([listUsers(), listRoles(), listOrganizationUnits()])
      .then(([nextUsers, nextRoles, nextUnits]) => {
        if (!active) return;
        setUsers(nextUsers);
        setRoles(nextRoles);
        setUnits(nextUnits);
        setLoading(false);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat data administrasi.",
        );
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  async function submitCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const form = event.currentTarget;
    const data = new FormData(form);
    const roleId = getFormString(data, "role_id");
    const unitId = getFormString(data, "primary_unit_id");

    setErrorMessage(null);

    try {
      await createUser({
        username: getFormString(data, "username"),
        email: getFormString(data, "email").trim() || null,
        full_name: getFormString(data, "full_name"),
        password: getFormString(data, "password"),
        primary_unit_id: unitId,
        job_title: getFormString(data, "job_title").trim() || null,
        role_assignments: roleId
          ? [
              {
                role_id: roleId,
                scope_type: "ALL",
                scope_unit_id: null,
              },
            ]
          : [],
      });

      form.reset();
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal membuat user.");
    }
  }

  async function handleRevokeSessions(userId: string) {
    if (!window.confirm("Cabut semua session aktif untuk pengguna ini?")) {
      return;
    }

    setErrorMessage(null);
    try {
      await revokeUserSessions(userId);
    } catch (error: unknown) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Gagal mencabut session pengguna.",
      );
    }
  }

  async function handleDeactivate(userId: string) {
    if (!window.confirm("Nonaktifkan user ini? Session aktif user juga akan dicabut.")) {
      return;
    }

    try {
      await deactivateUser(userId);
      await reload();
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal menonaktifkan user.");
    }
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Administration</p>
          <h1>Pengguna</h1>
          <p className="lead">Kelola akun internal SIMA.</p>
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
          <h2 className="admin-form-title">Buat Pengguna</h2>
          <label className="form-field">
            <span>Username</span>
            <input name="username" required minLength={3} />
          </label>
          <label className="form-field">
            <span>Nama lengkap</span>
            <input name="full_name" required />
          </label>
          <label className="form-field">
            <span>Email</span>
            <input name="email" type="email" />
          </label>
          <label className="form-field">
            <span>Password awal</span>
            <input name="password" type="password" required minLength={12} />
          </label>
          <label className="form-field">
            <span>Unit utama</span>
            <select name="primary_unit_id" required>
              <option value="">Pilih unit</option>
              {activeUnits.map((unit) => (
                <option value={unit.id} key={unit.id}>
                  {unit.name}
                </option>
              ))}
            </select>
          </label>
          <label className="form-field">
            <span>Jabatan</span>
            <input name="job_title" />
          </label>
          <label className="form-field">
            <span>Role awal</span>
            <select name="role_id">
              <option value="">Tanpa role</option>
              {activeRoles.map((role) => (
                <option value={role.id} key={role.id}>
                  {role.name}
                </option>
              ))}
            </select>
          </label>
          <div className="admin-form-actions">
            <button className="primary-button" type="submit">
              Simpan Pengguna
            </button>
          </div>
        </form>
      ) : null}

      <section className="panel">
        <div className="table-toolbar">
          <h2>Daftar Pengguna</h2>
          <span className="muted">{loading ? "Memuat..." : `${users.length} pengguna`}</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Nama</th>
                <th>Username</th>
                <th>Email</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {users.length === 0 && !loading ? (
                <tr>
                  <td colSpan={5} className="empty-table-cell">
                    Belum ada pengguna untuk ditampilkan.
                  </td>
                </tr>
              ) : null}
              {users.map((user) => (
                <tr key={user.id}>
                  <td>{user.full_name}</td>
                  <td>{user.username}</td>
                  <td>{user.email ?? "—"}</td>
                  <td>{user.is_active ? "Aktif" : "Nonaktif"}</td>
                  <td className="table-actions">
                    <div className="table-action-group">
                      {canRevokeSessions && user.id !== auth.user?.id && user.is_active ? (
                        <button
                          className="secondary-button compact-button"
                          type="button"
                          onClick={() => {
                            void handleRevokeSessions(user.id);
                          }}
                        >
                          Cabut Session
                        </button>
                      ) : null}
                      {canDeactivate && user.is_active ? (
                        <button
                          className="danger-button"
                          type="button"
                          onClick={() => {
                            void handleDeactivate(user.id);
                          }}
                        >
                          Nonaktifkan
                        </button>
                      ) : null}
                    </div>
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
