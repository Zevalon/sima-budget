export function DashboardPage() {
  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Implementation Phase 1B</p>
          <h1>Dashboard</h1>
          <p className="lead">
            Authentication dan session foundation sudah aktif. Nilai anggaran nyata belum
            ditampilkan karena modul Fiscal Year dan Annual Budget baru dibangun pada Phase 2.
          </p>
        </div>
        <span className="status-badge">Foundation Active</span>
      </section>

      <section className="panel-grid">
        <article className="panel">
          <span className="muted">Foundation</span>
          <h2>Identity & Authentication</h2>
          <ul className="check-list">
            <li>Organization dan Organizational Unit foundation</li>
            <li>Users, Roles, Permissions, dan Data Scope foundation</li>
            <li>Opaque server-side session dengan HttpOnly cookie</li>
            <li>CSRF protection untuk mutation request</li>
          </ul>
        </article>

        <article className="panel">
          <span className="muted">Tahap berikutnya</span>
          <h2>Phase 1C — Administration</h2>
          <p>
            User management, role/permission management, scope evaluation, organizational units, dan
            administration API.
          </p>
        </article>
      </section>
    </div>
  );
}
