FOUNDATION_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("settings.view", "Lihat Pengaturan Aplikasi", "settings"),
    ("settings.update", "Ubah Pengaturan Aplikasi", "settings"),
    ("users.view", "Lihat Pengguna", "users"),
    ("users.create", "Buat Pengguna", "users"),
    ("users.update", "Ubah Pengguna", "users"),
    ("users.deactivate", "Nonaktifkan Pengguna", "users"),
    ("roles.view", "Lihat Role", "roles"),
    ("roles.create", "Buat Role", "roles"),
    ("roles.update", "Ubah Role", "roles"),
    ("roles.assign", "Tetapkan Role", "roles"),
    ("permissions.view", "Lihat Permission", "roles"),
    ("organization_units.view", "Lihat Unit Organisasi", "organizations"),
    ("organization_units.create", "Buat Unit Organisasi", "organizations"),
    ("organization_units.update", "Ubah Unit Organisasi", "organizations"),
    ("organization_units.deactivate", "Nonaktifkan Unit Organisasi", "organizations"),
    ("audit.view", "Lihat Audit Log", "audit"),
    ("sessions.revoke", "Cabut Session Pengguna", "auth"),
)

PHASE2A_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("fiscal_years.view", "Lihat Tahun Anggaran", "budget_foundation"),
    ("fiscal_years.create", "Buat Tahun Anggaran", "budget_foundation"),
    ("fiscal_years.update", "Ubah Tahun Anggaran", "budget_foundation"),
    ("fiscal_years.transition", "Ubah Status Tahun Anggaran", "budget_foundation"),
    ("fiscal_years.reopen", "Buka Kembali Tahun Anggaran", "budget_foundation"),
    ("budget_categories.view", "Lihat Kategori Anggaran", "budget_foundation"),
    ("budget_categories.manage", "Kelola Kategori Anggaran", "budget_foundation"),
    ("units_of_measure.view", "Lihat Satuan", "budget_foundation"),
    ("units_of_measure.manage", "Kelola Satuan", "budget_foundation"),
)


PHASE2B1_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("annual_budgets.view", "Lihat Anggaran Tahunan", "annual_budgets"),
    ("annual_budgets.create", "Buat Anggaran Tahunan", "annual_budgets"),
    ("annual_budgets.update", "Ubah Anggaran Tahunan", "annual_budgets"),
    ("annual_budgets.submit", "Ajukan Anggaran Tahunan", "annual_budgets"),
)

PHASE2B2_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("annual_budgets.approve", "Setujui atau Tolak Anggaran Tahunan", "annual_budgets"),
)

PHASE2C_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("unit_allocations.view", "Lihat Alokasi Unit", "unit_allocations"),
    ("unit_allocations.create", "Buat Alokasi Unit", "unit_allocations"),
    ("unit_allocations.update", "Ubah Alokasi Unit", "unit_allocations"),
)

PHASE3A_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("budget_plans.view", "Lihat Rencana Anggaran", "budget_plans"),
    ("budget_plans.create", "Buat Rencana Anggaran", "budget_plans"),
    ("budget_plans.update", "Ubah Draft Rencana Anggaran", "budget_plans"),
)

PHASE3B_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("budget_plans.submit", "Ajukan Rencana Anggaran", "budget_plans"),
    ("budget_plans.approve", "Setujui atau Tolak Rencana Anggaran", "budget_plans"),
    ("budget_plans.revise", "Revisi Rencana Anggaran Ditolak", "budget_plans"),
)

PHASE4A_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("realizations.view", "Lihat Realisasi Anggaran", "realizations"),
    ("realizations.create", "Buat Draft Realisasi", "realizations"),
    ("realizations.update", "Ubah Draft Realisasi", "realizations"),
    ("realizations.post", "Posting Realisasi Anggaran", "realizations"),
)

PHASE4B_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("realizations.cancel", "Batalkan Draft Realisasi", "realizations"),
    ("realizations.reverse", "Reversal Realisasi Posted", "realizations"),
)

PHASE5A_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("reports.view", "Lihat Laporan Anggaran", "reports"),
)

ALL_BOOTSTRAP_PERMISSIONS = (
    FOUNDATION_PERMISSIONS
    + PHASE2A_PERMISSIONS
    + PHASE2B1_PERMISSIONS
    + PHASE2B2_PERMISSIONS
    + PHASE2C_PERMISSIONS
    + PHASE3A_PERMISSIONS
    + PHASE3B_PERMISSIONS
    + PHASE4A_PERMISSIONS
    + PHASE4B_PERMISSIONS
    + PHASE5A_PERMISSIONS
)

PHASE2A_VIEW_PERMISSIONS = (
    "fiscal_years.view",
    "budget_categories.view",
    "units_of_measure.view",
)

PHASE2A_BUDGET_ADMIN_PERMISSIONS = tuple(code for code, _, _ in PHASE2A_PERMISSIONS)

PHASE2B1_VIEW_PERMISSIONS = ("annual_budgets.view",)
PHASE2B1_BUDGET_ADMIN_PERMISSIONS = tuple(code for code, _, _ in PHASE2B1_PERMISSIONS)
PHASE2B2_APPROVER_PERMISSIONS = tuple(code for code, _, _ in PHASE2B2_PERMISSIONS)
PHASE2C_VIEW_PERMISSIONS = ("unit_allocations.view",)
PHASE2C_BUDGET_ADMIN_PERMISSIONS = tuple(code for code, _, _ in PHASE2C_PERMISSIONS)
PHASE3A_VIEW_PERMISSIONS = ("budget_plans.view",)
PHASE3A_UNIT_PIC_PERMISSIONS = tuple(code for code, _, _ in PHASE3A_PERMISSIONS)
PHASE3B_UNIT_PIC_PERMISSIONS = ("budget_plans.submit", "budget_plans.revise")
PHASE3B_UNIT_APPROVER_PERMISSIONS = ("budget_plans.approve",)
PHASE4A_VIEW_PERMISSIONS = ("realizations.view",)
PHASE4A_UNIT_PIC_PERMISSIONS = tuple(code for code, _, _ in PHASE4A_PERMISSIONS)
PHASE4B_UNIT_PIC_PERMISSIONS = tuple(code for code, _, _ in PHASE4B_PERMISSIONS)
PHASE5A_VIEW_PERMISSIONS = tuple(code for code, _, _ in PHASE5A_PERMISSIONS)

DEFAULT_ROLE_TEMPLATES: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    (
        "SYSTEM_ADMIN",
        "System Administrator",
        "Mengelola konfigurasi sistem, pengguna, role, permission, dan struktur organisasi.",
        tuple(code for code, _, _ in FOUNDATION_PERMISSIONS)
        + PHASE2A_VIEW_PERMISSIONS
        + PHASE2B1_VIEW_PERMISSIONS
        + PHASE2C_VIEW_PERMISSIONS
        + PHASE3A_VIEW_PERMISSIONS
        + PHASE4A_VIEW_PERMISSIONS
        + PHASE5A_VIEW_PERMISSIONS,
    ),
    (
        "BUDGET_ADMIN",
        "Budget Administrator",
        "Mengelola fondasi dan administrasi domain anggaran.",
        (
            "settings.view",
            "organization_units.view",
            "users.view",
            "roles.view",
            "permissions.view",
        )
        + PHASE2A_BUDGET_ADMIN_PERMISSIONS
        + PHASE2B1_BUDGET_ADMIN_PERMISSIONS
        + PHASE2C_BUDGET_ADMIN_PERMISSIONS
        + PHASE3A_VIEW_PERMISSIONS
        + PHASE4A_VIEW_PERMISSIONS
        + PHASE5A_VIEW_PERMISSIONS,
    ),
    (
        "UNIT_PIC",
        "Unit PIC",
        "Template user operasional unit. Permission rencana anggaran ditambahkan pada Phase 3.",
        ("settings.view", "organization_units.view")
        + PHASE2A_VIEW_PERMISSIONS
        + PHASE3A_UNIT_PIC_PERMISSIONS
        + PHASE3B_UNIT_PIC_PERMISSIONS
        + PHASE4A_UNIT_PIC_PERMISSIONS
        + PHASE4B_UNIT_PIC_PERMISSIONS
        + PHASE5A_VIEW_PERMISSIONS,
    ),
    (
        "UNIT_APPROVER",
        "Unit Approver",
        "Template approver unit untuk review rencana anggaran dan akses baca realisasi.",
        ("settings.view", "organization_units.view")
        + PHASE2A_VIEW_PERMISSIONS
        + PHASE3A_VIEW_PERMISSIONS
        + PHASE3B_UNIT_APPROVER_PERMISSIONS
        + PHASE4A_VIEW_PERMISSIONS
        + PHASE5A_VIEW_PERMISSIONS,
    ),
    (
        "MANAGEMENT_APPROVER",
        "Management Approver",
        "Template pimpinan/approver tingkat manajemen.",
        ("settings.view", "organization_units.view")
        + PHASE2A_VIEW_PERMISSIONS
        + PHASE2B1_VIEW_PERMISSIONS
        + PHASE2B2_APPROVER_PERMISSIONS
        + PHASE2C_VIEW_PERMISSIONS
        + PHASE3A_VIEW_PERMISSIONS
        + PHASE4A_VIEW_PERMISSIONS
        + PHASE5A_VIEW_PERMISSIONS,
    ),
    (
        "AUDITOR",
        "Auditor",
        "Akses pemeriksaan read-only terhadap struktur, user, audit, dan fondasi anggaran.",
        (
            "settings.view",
            "users.view",
            "roles.view",
            "permissions.view",
            "organization_units.view",
            "audit.view",
        )
        + PHASE2A_VIEW_PERMISSIONS
        + PHASE2B1_VIEW_PERMISSIONS
        + PHASE2C_VIEW_PERMISSIONS
        + PHASE3A_VIEW_PERMISSIONS
        + PHASE4A_VIEW_PERMISSIONS
        + PHASE5A_VIEW_PERMISSIONS,
    ),
    (
        "VIEWER",
        "Viewer",
        "Akses baca terbatas.",
        ("settings.view", "organization_units.view")
        + PHASE2A_VIEW_PERMISSIONS
        + PHASE3A_VIEW_PERMISSIONS
        + PHASE4A_VIEW_PERMISSIONS
        + PHASE5A_VIEW_PERMISSIONS,
    ),
)
