import { Link } from "react-router-dom";

import { useAuth } from "../../auth/auth-context";

import "../../../styles/budget-foundation.css";

const sections = [
  {
    title: "Tahun Anggaran",
    description: "Kelola lifecycle tahun anggaran dari draft sampai arsip.",
    href: "/app/master-data/fiscal-years",
    permission: "fiscal_years.view",
  },
  {
    title: "Kategori Anggaran",
    description: "Master kategori yang digunakan pada detail rencana anggaran.",
    href: "/app/master-data/budget-categories",
    permission: "budget_categories.view",
  },
  {
    title: "Satuan",
    description: "Master satuan untuk quantity item rencana anggaran.",
    href: "/app/master-data/units-of-measure",
    permission: "units_of_measure.view",
  },
] as const;

export function MasterDataHomePage() {
  const auth = useAuth();
  const permissions = new Set(auth.user?.permissions ?? []);

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Budget Foundation</p>
          <h1>Master Data</h1>
          <p className="lead">Fondasi referensi untuk proses anggaran SIMA.</p>
        </div>
      </section>

      <section className="budget-master-grid">
        {sections
          .filter((section) => permissions.has(section.permission))
          .map((section) => (
            <Link className="budget-master-card" to={section.href} key={section.href}>
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
