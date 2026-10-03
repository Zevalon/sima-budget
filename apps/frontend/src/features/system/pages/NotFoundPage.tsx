import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="center-page">
      <div>
        <p className="eyebrow">404</p>
        <h1>Halaman tidak ditemukan</h1>
        <p>Alamat yang Anda buka belum tersedia atau tidak valid.</p>
        <Link className="button-link" to="/app/dashboard">
          Kembali ke Dashboard
        </Link>
      </div>
    </main>
  );
}
