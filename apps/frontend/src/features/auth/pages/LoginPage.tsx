import { type FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { ApiError } from "../../../lib/api/client";
import { useAuth } from "../auth-context";

type LoginLocationState = {
  from?: string;
};

export function LoginPage() {
  const auth = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (auth.status === "authenticated") {
    return <Navigate to="/app/dashboard" replace />;
  }

  async function submitLogin() {
    setErrorMessage(null);
    setSubmitting(true);

    try {
      await auth.login(username, password);
      const state = location.state as LoginLocationState | null;
      void navigate(state?.from ?? "/app/dashboard", { replace: true });
    } catch (error: unknown) {
      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("Terjadi kesalahan saat menghubungi server.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitLogin();
  }

  return (
    <main className="login-page">
      <section className="login-brand-panel">
        <div>
          <div className="brand-mark login-brand-mark">S</div>
          <p className="eyebrow login-eyebrow">SIMA</p>
          <h1>Sistem Informasi Monitoring Anggaran</h1>
          <p>
            Perencanaan, persetujuan, realisasi, dan monitoring anggaran organisasi dalam satu
            sistem.
          </p>
        </div>
      </section>

      <section className="login-form-panel">
        <form className="auth-card login-form" onSubmit={handleSubmit}>
          <div>
            <p className="eyebrow">Akses Internal</p>
            <h2>Masuk ke SIMA</h2>
            <p className="muted">Gunakan akun internal yang telah diberikan administrator.</p>
          </div>

          {errorMessage ? (
            <div className="form-alert" role="alert">
              {errorMessage}
            </div>
          ) : null}

          <label className="form-field">
            <span>Username atau email</span>
            <input
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>

          <label className="form-field">
            <span>Password</span>
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? "Memproses..." : "Masuk"}
          </button>
        </form>
      </section>
    </main>
  );
}
