import { type FormEvent, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { getAuditLogs } from "../api/foundation";
import type { AuditLogPage } from "../types";

import "../../../styles/foundation.css";

const PAGE_SIZE = 25;

export function AuditLogPage() {
  const [page, setPage] = useState<AuditLogPage | null>(null);
  const [action, setAction] = useState("");
  const [entityType, setEntityType] = useState("");
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function load(
    nextOffset: number,
    nextAction: string = action,
    nextEntityType: string = entityType,
  ) {
    setLoading(true);
    setErrorMessage(null);

    try {
      setPage(
        await getAuditLogs({
          limit: PAGE_SIZE,
          offset: nextOffset,
          action: nextAction || undefined,
          entityType: nextEntityType || undefined,
        }),
      );
      setOffset(nextOffset);
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat audit log.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;

    void getAuditLogs({ limit: PAGE_SIZE, offset: 0 })
      .then((result) => {
        if (!active) return;
        setPage(result);
        setLoading(false);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(error instanceof ApiError ? error.message : "Gagal memuat audit log.");
        setLoading(false);
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
    await load(0, nextAction, nextEntityType);
  }

  async function clearFilters() {
    setAction("");
    setEntityType("");
    await load(0, "", "");
  }

  const total = page?.total ?? 0;
  const hasPrevious = offset > 0;
  const hasNext = offset + PAGE_SIZE < total;
  const firstItem = total === 0 ? 0 : offset + 1;
  const lastItem = Math.min(offset + PAGE_SIZE, total);

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
          <input
            name="action"
            value={action}
            onChange={(event) => setAction(event.target.value)}
            placeholder="LOGIN, USER, SETTINGS..."
          />
        </label>
        <label className="form-field">
          <span>Entity type</span>
          <input
            name="entity_type"
            value={entityType}
            onChange={(event) => setEntityType(event.target.value)}
            placeholder="user, role, auth..."
          />
        </label>
        <div className="audit-filter-actions">
          <button className="secondary-button" type="submit" disabled={loading}>
            Terapkan Filter
          </button>
          <button
            className="secondary-button"
            type="button"
            disabled={loading || (!action && !entityType)}
            onClick={() => {
              void clearFilters();
            }}
          >
            Bersihkan
          </button>
        </div>
      </form>

      <section className="panel">
        <div className="table-toolbar">
          <h2>Aktivitas</h2>
          <span className="muted">
            {loading ? "Memuat..." : `${firstItem}-${lastItem} dari ${total} event`}
          </span>
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
              {(page?.items ?? []).length === 0 && !loading ? (
                <tr>
                  <td colSpan={5} className="empty-table-cell">
                    Tidak ada audit event yang sesuai dengan filter.
                  </td>
                </tr>
              ) : null}
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
        <div className="audit-pagination">
          <button
            className="secondary-button"
            type="button"
            disabled={!hasPrevious || loading}
            onClick={() => {
              void load(Math.max(0, offset - PAGE_SIZE));
            }}
          >
            Sebelumnya
          </button>
          <button
            className="secondary-button"
            type="button"
            disabled={!hasNext || loading}
            onClick={() => {
              void load(offset + PAGE_SIZE);
            }}
          >
            Berikutnya
          </button>
        </div>
      </section>
    </div>
  );
}
