import { Link } from "react-router-dom";

import { useAuth } from "../../auth/auth-context";

import "../../../styles/administration.css";

export function ApprovalHomePage() {
  const auth = useAuth();
  const permissions = new Set(auth.user?.permissions ?? []);
  const canAnnualBudget = permissions.has("annual_budgets.approve");
  const canBudgetPlan = permissions.has("budget_plans.approve");

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Approval</p>
          <h1>Persetujuan</h1>
          <p className="lead">Pilih inbox persetujuan sesuai kewenangan Anda.</p>
        </div>
      </section>

      <section className="panel">
        <div className="admin-card-grid">
          {canAnnualBudget ? (
            <Link className="admin-card" to="/app/approvals/annual-budgets">
              <strong>Anggaran Tahunan</strong>
              <span>Meninjau pagu organisasi yang menunggu persetujuan.</span>
            </Link>
          ) : null}
          {canBudgetPlan ? (
            <Link className="admin-card" to="/app/approvals/budget-plans">
              <strong>Rencana Anggaran</strong>
              <span>Meninjau rencana unit sesuai scope organisasi Anda.</span>
            </Link>
          ) : null}
          {!canAnnualBudget && !canBudgetPlan ? (
            <p className="empty-state">Tidak ada inbox approval yang tersedia.</p>
          ) : null}
        </div>
      </section>
    </div>
  );
}
