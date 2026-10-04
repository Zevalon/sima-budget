import { type FormEvent, useEffect, useState } from "react";

import { ApiError } from "../../../lib/api/client";
import { getFormString } from "../../../lib/forms/formData";
import { useAuth } from "../../auth/auth-context";
import { getApplicationSettings, updateApplicationSettings } from "../api/foundation";
import type { ApplicationSetting } from "../types";

import "../../../styles/foundation.css";

export function SettingsPage() {
  const auth = useAuth();
  const canUpdate = (auth.user?.permissions ?? []).includes("settings.update");

  const [setting, setSetting] = useState<ApplicationSetting | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    void getApplicationSettings()
      .then((data) => {
        if (active) setSetting(data);
      })
      .catch((error: unknown) => {
        if (!active) return;
        setErrorMessage(
          error instanceof ApiError ? error.message : "Gagal memuat pengaturan aplikasi.",
        );
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);

    setMessage(null);
    setErrorMessage(null);

    try {
      const updated = await updateApplicationSettings({
        application_name: getFormString(data, "application_name"),
        application_short_name: getFormString(data, "application_short_name"),
        organization_display_name: getFormString(data, "organization_display_name"),
        currency_code: getFormString(data, "currency_code"),
        timezone: getFormString(data, "timezone"),
        date_format: getFormString(data, "date_format"),
        primary_color: getFormString(data, "primary_color").trim() || null,
        secondary_color: getFormString(data, "secondary_color").trim() || null,
        allow_annual_budget_revision: data.get("allow_annual_budget_revision") === "on",
        allow_budget_transfer: data.get("allow_budget_transfer") === "on",
        allow_self_approval: data.get("allow_self_approval") === "on",
      });
      setSetting(updated);
      setMessage("Pengaturan berhasil disimpan.");
    } catch (error: unknown) {
      setErrorMessage(error instanceof ApiError ? error.message : "Gagal menyimpan pengaturan.");
    }
  }

  if (!setting) {
    return (
      <div className="page-stack">
        <section className="page-header">
          <div>
            <p className="eyebrow">Administration</p>
            <h1>Pengaturan Aplikasi</h1>
          </div>
        </section>
        {errorMessage ? <div className="form-alert">{errorMessage}</div> : <p>Memuat...</p>}
      </div>
    );
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Administration</p>
          <h1>Pengaturan Aplikasi</h1>
          <p className="lead">Branding dan kebijakan dasar deployment SIMA.</p>
        </div>
      </section>

      {message ? <div className="success-alert">{message}</div> : null}
      {errorMessage ? <div className="form-alert">{errorMessage}</div> : null}

      <form
        className="panel foundation-form-grid"
        onSubmit={(event) => {
          void handleSubmit(event);
        }}
      >
        <label className="form-field">
          <span>Nama aplikasi</span>
          <input
            name="application_name"
            defaultValue={setting.application_name}
            disabled={!canUpdate}
            required
          />
        </label>
        <label className="form-field">
          <span>Nama singkat</span>
          <input
            name="application_short_name"
            defaultValue={setting.application_short_name}
            disabled={!canUpdate}
            required
          />
        </label>
        <label className="form-field foundation-span-2">
          <span>Nama organisasi</span>
          <input
            name="organization_display_name"
            defaultValue={setting.organization_display_name}
            disabled={!canUpdate}
            required
          />
        </label>
        <label className="form-field">
          <span>Mata uang</span>
          <input
            name="currency_code"
            defaultValue={setting.currency_code}
            maxLength={3}
            disabled={!canUpdate}
            required
          />
        </label>
        <label className="form-field">
          <span>Timezone</span>
          <input name="timezone" defaultValue={setting.timezone} disabled={!canUpdate} required />
        </label>
        <label className="form-field">
          <span>Format tanggal</span>
          <input
            name="date_format"
            defaultValue={setting.date_format}
            disabled={!canUpdate}
            required
          />
        </label>
        <label className="form-field">
          <span>Primary color</span>
          <input
            name="primary_color"
            defaultValue={setting.primary_color ?? ""}
            placeholder="#0F172A"
            disabled={!canUpdate}
          />
        </label>
        <label className="form-field">
          <span>Secondary color</span>
          <input
            name="secondary_color"
            defaultValue={setting.secondary_color ?? ""}
            placeholder="#FFFFFF"
            disabled={!canUpdate}
          />
        </label>

        <div className="foundation-policy-list foundation-span-2">
          <label className="checkbox-field">
            <input
              type="checkbox"
              name="allow_annual_budget_revision"
              defaultChecked={setting.allow_annual_budget_revision}
              disabled={!canUpdate}
            />
            <span>Izinkan revisi anggaran tahunan</span>
          </label>
          <label className="checkbox-field">
            <input
              type="checkbox"
              name="allow_budget_transfer"
              defaultChecked={setting.allow_budget_transfer}
              disabled={!canUpdate}
            />
            <span>Izinkan transfer anggaran antar unit</span>
          </label>
          <label className="checkbox-field">
            <input
              type="checkbox"
              name="allow_self_approval"
              defaultChecked={setting.allow_self_approval}
              disabled={!canUpdate}
            />
            <span>Izinkan self-approval</span>
          </label>
        </div>

        {canUpdate ? (
          <div className="foundation-span-2">
            <button className="primary-button" type="submit">
              Simpan Pengaturan
            </button>
          </div>
        ) : null}
      </form>
    </div>
  );
}
