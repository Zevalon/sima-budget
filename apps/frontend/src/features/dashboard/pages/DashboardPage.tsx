const cards = [
  ["Total Anggaran", "Rp50,0 M", "Baseline contoh"],
  ["Teralokasi", "Rp45,0 M", "90% dari total"],
  ["Committed", "Rp32,5 M", "Rencana disetujui"],
  ["Realisasi", "Rp21,4 M", "42,8% dari total"],
] as const;

export function DashboardPage() {
  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Implementation Phase 0</p>
          <h1>Dashboard</h1>
          <p className="lead">
            Fondasi UI SIMA sudah aktif. Data pada halaman ini masih contoh visual dan belum
            terhubung ke modul anggaran.
          </p>
        </div>
        <span className="status-badge">Scaffold Ready</span>
      </section>

      <section className="stat-grid" aria-label="Ringkasan anggaran contoh">
        {cards.map(([label, value, detail]) => (
          <article className="stat-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{detail}</small>
          </article>
        ))}
      </section>

      <section className="panel-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="muted">Project readiness</span>
              <h2>Fondasi yang sudah tersedia</h2>
            </div>
          </div>
          <ul className="check-list">
            <li>React + TypeScript application shell</li>
            <li>FastAPI API skeleton + health endpoints</li>
            <li>PostgreSQL Docker development service</li>
            <li>CI, migration, testing, docs, dan checkpoint structure</li>
          </ul>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <span className="muted">Next milestone</span>
              <h2>Phase 1 — Foundation</h2>
            </div>
          </div>
          <p>
            Authentication, user management, RBAC + scope, organizational units, application
            settings, dan audit infrastructure.
          </p>
          <div className="progress-track" aria-label="Progress desain project">
            <div className="progress-value" />
          </div>
          <small>CP-01 sampai CP-05 selesai — implementasi dimulai.</small>
        </article>
      </section>
    </div>
  );
}
