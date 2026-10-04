import { Link } from "react-router-dom";

export function AccessDeniedPage() {
  return (
    <div className="center-page">
      <section className="auth-card">
        <p className="eyebrow">Akses ditolak</p>
        <h1>Anda tidak memiliki permission untuk halaman ini.</h1>
        <p className="muted">
          Hak akses ditentukan oleh role dan scope akun yang sedang digunakan.
        </p>
        <Link className="primary-button access-denied-link" to="/app/dashboard">
          Kembali ke Dashboard
        </Link>
      </section>
    </div>
  );
}
