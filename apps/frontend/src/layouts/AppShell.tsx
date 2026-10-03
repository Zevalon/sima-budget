import { NavLink, Outlet } from "react-router-dom";

const navigation = [
  ["Dashboard", "/app/dashboard"],
  ["Anggaran", "#"],
  ["Rencana Anggaran", "#"],
  ["Realisasi", "#"],
  ["Approval", "#"],
  ["Laporan", "#"],
  ["Master Data", "#"],
  ["Administration", "#"],
] as const;

export function AppShell() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">S</div>
          <div>
            <strong>SIMA</strong>
            <span>Monitoring Anggaran</span>
          </div>
        </div>
        <nav aria-label="Navigasi utama">
          {navigation.map(([label, to]) =>
            to === "#" ? (
              <span className="nav-item nav-item-disabled" key={label} aria-disabled="true">
                {label}
                <small>segera</small>
              </span>
            ) : (
              <NavLink className="nav-item" to={to} key={label}>
                {label}
              </NavLink>
            ),
          )}
        </nav>
      </aside>

      <div className="content-column">
        <header className="topbar">
          <div>
            <span className="muted">Organisasi</span>
            <strong>Universitas / Organisasi</strong>
          </div>
          <div className="topbar-actions">
            <label>
              <span className="muted">Tahun Anggaran</span>
              <select defaultValue="2027" aria-label="Tahun Anggaran">
                <option value="2027">2027</option>
              </select>
            </label>
            <button className="avatar" type="button" aria-label="Profil pengguna">
              AD
            </button>
          </div>
        </header>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
