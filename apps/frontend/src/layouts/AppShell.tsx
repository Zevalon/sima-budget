import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../features/auth/auth-context";

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

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

export function AppShell() {
  const auth = useAuth();
  const user = auth.user;

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
            <strong>{user?.organization_name ?? "Universitas / Organisasi"}</strong>
          </div>
          <div className="topbar-actions">
            <label>
              <span className="muted">Tahun Anggaran</span>
              <select defaultValue="2027" aria-label="Tahun Anggaran" disabled>
                <option value="2027">2027</option>
              </select>
            </label>
            <div className="profile-summary">
              <button className="avatar" type="button" aria-label="Profil pengguna">
                {initials(user?.full_name ?? "User") || "U"}
              </button>
              <div>
                <strong>{user?.full_name}</strong>
                <span className="muted">{user?.username}</span>
              </div>
            </div>
            <button className="secondary-button" type="button" onClick={() => void auth.logout()}>
              Keluar
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
