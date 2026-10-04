import { type FormEvent, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { getAuditLogs } from "../api/foundation";
import type { AuditLogPage } from "../types";

import "../../../styles/foundation.css";

export function AuditLogPage() {
  const [page, setPage] = useState<AuditLogPage | null>(null);
  const [action, setAction] = useState("");
  const [entityType, setEntityType] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function load(nextAction = action, nextEntityType = entityType) {
    setErrorMessage(null);
    try {
      setPage(
        await getAuditLogs({
          limit: 50,
          action: nextAction || undefined,
          entityType: nextEntityType || undefined,
        }),
      );
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat audit log.");
    }
  }

  useEffect(() => {
    let active = true;

    void getAuditLogs({ limit: 50 })
      .then((result) => {
        if (active) setPage(result);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat audit log.");
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleFilter(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const nextAction = getFormString(data, "action").trim();
    const nextEntityType = getFormString(data, "entity_type").trim();
    setAction(nextAction);
    setEntityType(nextEntityType);
    await load(nextAction, nextEntityType);
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Administration</p>
          <h1>Audit Log</h1>
          <p className="lead">Riwayat aksi keamanan dan perubahan data penting.</p>
        </div>
      </section>

      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}

      <form
        className="panel audit-filter"
        onSubmit={(event) => {
          void handleFilter(event);
        }}
      >
        <label className="form-field">
          <span>Action</span>
          <input name="action" defaultValue={action} placeholder="LOGIN, USER, SETTINGS..." />
        </label>
        <label className="form-field">
          <span>Entity type</span>
          <input name="entity_type" defaultValue={entityType} placeholder="user, role, auth..." />
        </label>
        <button className="secondary-button" type="submit">
          Terapkan Filter
        </button>
      </form>

      <section className="panel">
        <div className="table-toolbar">
          <h2>Aktivitas</h2>
          <span className="muted">{page ? `${page.total} event` : "Memuat..."}</span>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Waktu</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Entity</th>
                <th>ID</th>
              </tr>
            </thead>
            <tbody>
              {(page?.items ?? []).map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.created_at).toLocaleString("id-ID")}</td>
                  <td>{item.actor_full_name ?? item.actor_username ?? "System"}</td>
                  <td>
                    <strong>{item.action}</strong>
                  </td>
                  <td>{item.entity_type}</td>
                  <td className="audit-id">{item.entity_id ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
