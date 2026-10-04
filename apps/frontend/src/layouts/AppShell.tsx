import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../features/auth/auth-context";

type NavigationItem = {
  label: string;
  to: string;
  permissionAnyOf?: string[];
  disabled?: boolean;
};

const navigation: NavigationItem[] = [
  { label: "Dashboard", to: "/app/dashboard" },
  { label: "Anggaran", to: "#", disabled: true },
  { label: "Rencana Anggaran", to: "#", disabled: true },
  { label: "Realisasi", to: "#", disabled: true },
  { label: "Approval", to: "#", disabled: true },
  { label: "Laporan", to: "#", disabled: true },
  { label: "Master Data", to: "#", disabled: true },
  {
    label: "Administration",
    to: "/app/administration",
    permissionAnyOf: [
      "users.view",
      "roles.view",
      "permissions.view",
      "organization_units.view",
      "settings.view",
      "audit.view",
    ],
  },
];

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
  const permissions = new Set(user?.permissions ?? []);

  const visibleNavigation = navigation.filter((item) => {
    if (!item.permissionAnyOf) {
      return true;
    }
    return item.permissionAnyOf.some((permission) => permissions.has(permission));
  });

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">S</div>
          <div>
            <strong>{user?.application_short_name ?? "SIMA"}</strong>
            <span>{user?.application_name ?? "Sistem Informasi Monitoring Anggaran"}</span>
          </div>
        </div>
        <nav aria-label="Navigasi utama">
          {visibleNavigation.map((item) =>
            item.disabled ? (
              <span className="nav-item nav-item-disabled" key={item.label} aria-disabled="true">
                {item.label}
                <small>segera</small>
              </span>
            ) : (
              <NavLink className="nav-item" to={item.to} key={item.label}>
                {item.label}
              </NavLink>
            ),
          )}
        </nav>
      </aside>

      <div className="content-column">
        <header className="topbar">
          <div>
            <span className="muted">Organisasi</span>
            <strong>
              {user?.organization_display_name ??
                user?.organization_name ??
                "Universitas / Organisasi"}
            </strong>
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
