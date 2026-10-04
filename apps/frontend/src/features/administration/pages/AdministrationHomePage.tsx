import { Link } from "react-router-dom";

import "../../../styles/administration.css";

import { useAuth } from "../../auth/auth-context";

const sections = [
  {
    title: "Pengguna",
    description: "Kelola akun internal, unit utama, dan assignment role.",
    href: "/app/administration/users",
    permission: "users.view",
  },
  {
    title: "Role & Permission",
    description: "Kelola role aplikasi dan permission yang dimilikinya.",
    href: "/app/administration/roles",
    permission: "roles.view",
  },
  {
    title: "Unit Organisasi",
    description: "Kelola hierarchy organisasi yang digunakan oleh modul anggaran.",
    href: "/app/administration/organization-units",
    permission: "organization_units.view",
  },
] as const;

export function AdministrationHomePage() {
  const auth = useAuth();
  const permissions = new Set(auth.user?.permissions ?? []);

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Administration</p>
          <h1>Administrasi Sistem</h1>
          <p className="lead">Menu yang tampil mengikuti permission akun yang sedang digunakan.</p>
        </div>
      </section>

      <section className="admin-card-grid">
        {sections
          .filter((section) => permissions.has(section.permission))
          .map((section) => (
            <Link className="admin-card-link" to={section.href} key={section.href}>
              <article className="panel">
                <h2>{section.title}</h2>
                <p className="muted">{section.description}</p>
              </article>
            </Link>
          ))}
      </section>
    </div>
  );
}
