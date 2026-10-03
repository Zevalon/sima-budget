# CP-01 — Requirement & Business Rules Baseline

**Project:** SIMA (default branding) — Sistem Informasi Monitoring Anggaran  
**Checkpoint:** CP-01  
**Version:** 1.0  
**Status:** BASELINE FOR DATA MODEL DESIGN  
**Purpose:** Menyimpan keputusan requirement, scope, business rules, role, permission, serta asumsi desain sebelum masuk ke tahap Data Model & ERD.

---

## 1. Project Context

SIMA adalah aplikasi web untuk perencanaan, pengalokasian, persetujuan, realisasi, monitoring, dan pelaporan anggaran tahunan organisasi. Implementasi pertama ditujukan untuk sebuah universitas swasta, namun domain aplikasi dibuat generik agar dapat digunakan oleh universitas/organisasi lain tanpa perubahan besar pada source code.

Aplikasi dapat diakses melalui internet, tetapi pengguna merupakan user internal organisasi. Aplikasi bukan sistem accounting/ERP/procurement penuh dan tidak menggantikan SIAKAD, HRIS, atau sistem keuangan yang sudah ada. Integrasi dengan sistem lain dipersiapkan untuk masa depan.

---

## 2. Default Branding

- Nama default aplikasi: **SIMA**
- Nama panjang default: **Sistem Informasi Monitoring Anggaran**
- Nama aplikasi, nama organisasi, logo, favicon, warna, footer, zona waktu, format tanggal, dan identitas report harus dapat diubah melalui Application Settings.
- Nama repository teknis yang direkomendasikan: `sima-budget`.
- Branding tidak boleh di-hardcode sebagai bagian dari business logic.

---

## 3. Scope V1

Modul utama V1:

1. Authentication
2. User Management
3. Roles & Permissions
4. Organizational Units
5. Fiscal Year
6. Annual Budget
7. Budget Allocation
8. Budget Categories
9. Budget Plan
10. Budget Plan Items
11. Approval Workflow
12. Budget Realization
13. Budget Revision (configurable)
14. Dashboard
15. Reports
16. Notifications
17. Attachments
18. Audit Log
19. Application Settings

Out of scope V1:

- General Ledger / jurnal debit-kredit
- Accounting closing
- Payroll
- Procurement system penuh
- SIAKAD
- HRIS
- ERP penuh
- Banking/payment execution

---

## 4. Organization Model

Organisasi menggunakan konsep generik `OrganizationalUnit` dengan struktur hierarki parent-child.

Contoh struktur awal:

```text
Yayasan
└── Universitas
    ├── Rektorat
    ├── Fakultas
    │   └── Program Studi
    ├── Biro
    ├── Lembaga
    ├── UPT
    └── Unit Lainnya
```

Struktur di atas hanya contoh/default dan dapat disesuaikan oleh administrator.

Setiap unit minimal memiliki:

- kode
- nama
- tipe unit
- parent unit
- status aktif
- `can_receive_budget`
- `can_create_budget_plan`

Hierarki organisasi **tidak otomatis sama dengan hierarki budget**.

---

## 5. Default Roles

Role template V1:

1. System Administrator
2. Budget Administrator
3. Unit PIC
4. Unit Approver
5. Management Approver
6. Auditor
7. Viewer

Prinsip utama:

- User dapat memiliki lebih dari satu role.
- Role berbeda dengan jabatan/position.
- Permission tidak ditentukan berdasarkan nama jabatan.
- System Administrator tidak otomatis memiliki kewenangan finansial.
- User yang membutuhkan akses sistem + finansial dapat memperoleh beberapa role.

---

## 6. Permission Scope

Scope authorization awal:

- `OWN`
- `OWN_UNIT`
- `OWN_UNIT_AND_CHILDREN`
- `ALL`

Contoh:

- Kaprodi: `OWN_UNIT`
- Dekan: `OWN_UNIT_AND_CHILDREN`
- Budget Administrator: `ALL`

---

## 7. Fiscal Year Lifecycle

Status:

```text
DRAFT → PLANNING → ACTIVE → CLOSED → ARCHIVED
```

Aturan:

- Tahun aktif dan tahun planning berikutnya dapat tersedia bersamaan.
- Hanya satu Fiscal Year yang menjadi tahun transaksi aktif pada satu waktu.
- Fiscal Year CLOSED tidak menerima plan, allocation, atau realization baru.
- Reopen hanya melalui permission khusus dan wajib diaudit.

---

## 8. Annual Budget

Satu Fiscal Year memiliki satu Annual Budget utama.

Workflow:

```text
DRAFT → SUBMITTED → APPROVED → LOCKED
```

- Budget Administrator dapat menginput anggaran.
- Pihak berwenang yang mempunyai permission dapat melakukan approval.
- Annual Budget yang sudah approved tidak dapat diedit langsung.
- Revision merupakan proses terkontrol dan dapat diaktifkan/dinonaktifkan.
- Default `Allow Annual Budget Revision = OFF`.
- Jika revision diaktifkan, nilai original harus tetap tersimpan.

---

## 9. Budget Allocation

Aturan utama:

```text
SUM(active unit allocations) <= current annual budget
```

- Budget tidak wajib seluruhnya dialokasikan.
- Unallocated budget adalah kondisi valid.
- Allocation hanya dapat diberikan kepada unit dengan `can_receive_budget = true`.
- Semua validasi kritis dilakukan di backend.

---

## 10. Budget Plan

Budget Plan dibuat untuk satu Fiscal Year dan satu Organizational Unit.

Struktur:

```text
Budget Plan (Header)
└── Budget Plan Items (Detail)
```

Plan dapat mewakili kegiatan, program, pengadaan, layanan, perjalanan, honor, lisensi, dan kebutuhan lain; tidak terbatas pada pembelian barang.

Item minimal mendukung:

- deskripsi
- quantity
- unit of measure
- unit price
- subtotal
- notes
- budget category

Formula:

```text
Item Subtotal = Quantity × Unit Price
Plan Total = SUM(Item Subtotal)
```

Nilai uang menggunakan fixed precision (`NUMERIC/Decimal`), bukan floating point.

---

## 11. Allocation, Commitment, Realization

Konsep anggaran dibedakan menjadi:

- Allocated
- Committed
- Realized
- Available

Plan DRAFT tidak mengurangi saldo resmi.

Ketika plan final approved, nilainya menjadi commitment.

Formula konseptual:

```text
Available = Allocated - Committed
```

Realized merupakan bagian dari commitment yang sudah digunakan.

Pada final approval, backend wajib melakukan pengecekan saldo kembali secara transaksional untuk mencegah dua plan disetujui bersamaan melebihi allocation.

---

## 12. Budget Plan Status

Approval/workflow status dipisahkan dari execution status.

### Workflow Status

- DRAFT
- SUBMITTED
- UNDER_REVIEW
- REVISION_REQUIRED
- APPROVED
- REJECTED
- CANCELLED

### Execution Status

- NOT_STARTED
- IN_PROGRESS
- PARTIALLY_REALIZED
- FULLY_REALIZED
- CLOSED

---

## 13. Approval Workflow

Approval dibuat configurable tetapi tidak berupa BPM engine kompleks pada V1.

Struktur dasar:

```text
Workflow
├── Step 1
├── Step 2
├── Step 3
└── ...
```

Setiap step dapat menentukan:

- required role/permission
- scope
- order
- optional amount threshold

Approval dilakukan berurutan.

Keputusan approver:

- APPROVE
- REJECT
- REQUEST_REVISION

REJECT dan REQUEST_REVISION wajib memiliki komentar.

Default:

```text
Allow Self Approval = OFF
```

User yang submit tidak dapat approve submission yang sama meskipun memiliki permission approve, kecuali policy organisasi secara eksplisit diubah.

---

## 14. Revision

Approved Plan bersifat immutable secara langsung.

Perubahan dilakukan sebagai version/revision baru.

Contoh:

```text
Plan Version 1 — Rp100 juta — APPROVED
Plan Version 2 — Rp120 juta — PENDING APPROVAL
```

Jika V2 approved:

- V1 tetap disimpan sebagai histori.
- V2 menjadi current approved version.

Prinsip: **Revision, bukan silent edit.**

---

## 15. Realization

- Realization hanya dapat dibuat terhadap Approved Plan.
- Satu Plan dapat memiliki banyak Realization.
- Input V1 bersifat manual karena sistem keuangan existing belum diketahui.
- Data model dipersiapkan untuk integrasi masa depan melalui `source`, `external_reference`, dan `external_system_id` atau konsep ekuivalen.

Default over-budget policy:

```text
STRICT
```

Aturan:

```text
SUM(realizations) <= approved plan amount
```

Future policy yang dapat dipertimbangkan:

- STRICT
- WARNING
- REQUIRE_APPROVAL

---

## 16. Delete & Correction Policy

- Draft yang belum diproses dapat dihapus jika tidak memiliki dependency.
- Submitted/Approved/Realized tidak boleh di-hard-delete.
- Koreksi menggunakan Cancel, Reject, Revision, Reversal, atau Archive sesuai kasus.
- Master data yang sudah digunakan menggunakan deactivate (`is_active = false`) daripada delete.

---

## 17. Budget Category & COA

Budget Category bersifat configurable.

Contoh seed awal:

- Pengadaan
- Operasional
- Pemeliharaan
- Pelatihan
- Perjalanan
- Kegiatan Akademik
- Kegiatan Kemahasiswaan
- Software
- Lainnya

COA/account code bukan master utama SIMA dan hanya diperlakukan sebagai optional reference/integration point sampai sistem keuangan existing dipahami.

---

## 18. Dashboard Baseline

Dashboard dibedakan berdasarkan role/scope.

Data utama:

- Total Annual Budget
- Allocated
- Unallocated
- Planned / Pipeline
- Committed
- Realized
- Available / Remaining
- Utilization percentage
- Pending approvals
- Unit utilization
- Monthly trend
- Budget vs realization
- Year comparison (jika data tersedia)

---

## 19. Reports Baseline

Laporan V1:

1. Annual Budget Summary
2. Allocation Report
3. Budget Plan Report
4. Plan Detail Report
5. Realization Report
6. Budget vs Realization
7. Remaining Budget
8. Unit Utilization
9. Category Report
10. Monthly Realization
11. Approval Report
12. Revision History

Filter utama:

- Fiscal Year
- Unit
- Category
- Status
- Date Range

Export bila relevan:

- PDF
- Excel
- CSV

---

## 20. Notifications & Intelligent Warnings

V1 menggunakan in-app notification.

Contoh event:

- plan submitted
- approval requested
- plan approved
- plan rejected
- revision requested
- realization added
- unit utilization threshold reached

Warning cerdas (rule-based, bukan AI wajib):

- serapan mencapai threshold tertentu
- approval terlalu lama pending
- kegiatan mendekati target date tetapi realisasi rendah
- Fiscal Year mendekati penutupan dengan sisa besar
- realisasi mendekati batas approved plan

---

## 21. Audit Log

Aktivitas penting wajib diaudit, minimal:

- LOGIN
- CREATE
- UPDATE
- SUBMIT
- APPROVE
- REJECT
- REQUEST_REVISION
- REVISION
- CANCEL
- REALIZATION
- ALLOCATE
- ROLE_CHANGE
- PERMISSION_CHANGE
- WORKFLOW_CHANGE
- SETTINGS_CHANGE
- EXPORT (untuk data sensitif/report tertentu)

Audit menyimpan jika relevan:

- user
- action
- entity
- entity ID
- timestamp
- before value
- after value
- metadata request/security bila diperlukan

Audit log tidak dapat diubah oleh user biasa.

---

## 22. Security Principles

- Authentication + authorization wajib pada seluruh area internal.
- Backend menjadi authority untuk semua business validation.
- Frontend validation hanya untuk UX, bukan security boundary.
- Least privilege.
- System administration dipisahkan dari financial authority.
- Approved financial data tidak boleh berubah tanpa histori.
- Permission-based authorization lebih penting daripada pengecekan nama role.

---

## 23. Default Permission Matrix

Legenda:

- `YES` = default diberikan
- `OPTIONAL` = dapat diberikan melalui konfigurasi
- `READ` = read-only
- `NO` = default tidak diberikan

| Capability | System Admin | Budget Admin | Unit PIC | Unit Approver | Management Approver | Auditor | Viewer |
|---|---|---|---|---|---|---|---|
| Manage Application Settings | YES | NO | NO | NO | NO | READ | NO |
| Manage Users | YES | NO | NO | NO | NO | READ | NO |
| Manage Roles/Permissions | YES | NO | NO | NO | NO | READ | NO |
| Manage Organizational Units | YES | OPTIONAL | NO | NO | NO | READ | READ |
| Manage Fiscal Year | NO | YES | NO | NO | NO | READ | READ |
| Create/Submit Annual Budget | NO | YES | NO | NO | NO | READ | READ |
| Approve Annual Budget | NO | OPTIONAL | NO | NO | YES | READ | READ |
| Manage Allocation | NO | YES | NO | NO | NO | READ | READ |
| View All Unit Budgets | OPTIONAL | YES | NO | OPTIONAL | YES | YES | OPTIONAL |
| View Own Unit Budget | OPTIONAL | YES | YES | YES | YES | YES | OPTIONAL |
| Create/Edit/Submit Budget Plan | NO | OPTIONAL | YES | YES | OPTIONAL | NO | NO |
| Review/Approve Plan | NO | OPTIONAL | NO | YES | YES | READ | NO |
| Reject/Request Revision | NO | OPTIONAL | NO | YES | YES | READ | NO |
| Create Realization | NO | OPTIONAL | YES | YES | NO | NO | NO |
| Verify Realization | NO | YES | NO | OPTIONAL | OPTIONAL | READ | NO |
| View Reports | OPTIONAL | YES | YES | YES | YES | YES | YES |
| Export Reports | OPTIONAL | YES | OPTIONAL | OPTIONAL | YES | YES | OPTIONAL |
| View Audit Log | YES | OPTIONAL | NO | NO | OPTIONAL | YES | NO |
| Manage Approval Workflow | YES | YES | NO | NO | NO | READ | NO |

Semua role di atas adalah template; implementasi authorization harus berdasarkan permission dan scope, bukan hardcoded role name.

---

## 24. Architecture Principles

1. Configuration over hardcoding
2. History over destructive update
3. Permission over role-name checking
4. Organizational Unit over faculty-specific tables
5. Revision over silent edits
6. Audit over untracked actions
7. API-ready over tightly coupled integration
8. Modular architecture over giant modules
9. Simple UI over unnecessary complexity
10. Database integrity and backend validation over UI-only rules

---

## 25. Decisions Classification

### CONFIRMED

- Web application, internet accessible, internal users.
- PostgreSQL + FastAPI + React/TypeScript stack.
- Annual budget dibagi ke unit.
- Unit membuat rencana yang tidak boleh melewati pagu.
- Satu rencana dapat mempunyai banyak detail item.
- Realization dapat berbeda dari planned amount, tetapi default tidak boleh melampaui approved plan.
- Dashboard/report digunakan untuk monitoring.
- Branding dapat diubah melalui settings.

### PROPOSED BASELINE

- Single organization per deployment.
- Generic Organizational Unit hierarchy.
- RBAC + scoped access.
- System Admin dipisahkan dari Budget Admin.
- Self approval OFF.
- Approved data immutable; correction melalui revision/reversal.
- Budget commitment terjadi pada final approval.
- Realization manual pada V1.
- Over-budget policy STRICT.

### CONFIGURABLE

- Organization structure.
- Unit types.
- Budget holder flags.
- Roles and permissions.
- Approval workflow.
- Categories.
- Branding.
- Revision policy.
- Notification thresholds.

### OPEN / FUTURE DISCOVERY

- Nama resmi unit keuangan di universitas.
- Approval chain resmi universitas.
- Struktur/fitur sistem keuangan existing.
- COA/account reference integration.
- Sumber resmi realization dari sistem keuangan.
- Kebijakan resmi budget transfer/carry-over.
- Report khusus yang diwajibkan pimpinan.

---

## 26. Next Milestone

**CP-02 — Data Model & ERD Baseline**

Output yang diharapkan:

- daftar entity/table
- relationship/cardinality
- primary/foreign keys konseptual
- status/version model
- authorization data model
- approval workflow model
- budget/commitment/realization model
- audit/file/notification model
- ERD modular
- business flow diagram
- budget lifecycle diagram
- approval flow diagram
- data dictionary awal

CP-02 hanya dibuat setelah rancangan data model telah direview dan dianggap baseline.
