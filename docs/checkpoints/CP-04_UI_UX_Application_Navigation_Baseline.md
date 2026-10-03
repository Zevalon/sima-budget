# CP-04 — UI/UX & Application Navigation Baseline

**Project:** SIMA — Sistem Informasi Monitoring Anggaran  
**Checkpoint:** CP-04  
**Status:** BASELINE  
**Scope:** UI/UX, navigation, page inventory, route structure, interaction patterns, dashboard roles, responsive behavior, and UX business safeguards.

---

## 1. Tujuan CP-04

Checkpoint ini mengunci rancangan pengalaman pengguna sebelum implementasi frontend dimulai.

Target utama:

1. Aplikasi mudah dipahami oleh user non-teknis.
2. Proses anggaran memiliki langkah yang jelas dan tidak membingungkan.
3. User hanya melihat menu dan data sesuai permission serta scope.
4. Informasi keuangan penting dapat dipahami tanpa harus membaca tabel besar.
5. Operasi sensitif selalu memiliki konfirmasi dan penjelasan dampak.
6. UI tidak mengandalkan istilah teknis database/API.
7. Aplikasi tetap usable pada laptop sebagai target utama, namun tetap responsive.
8. Desain tidak mengunci aplikasi hanya untuk universitas tertentu.

---

## 2. Prinsip UX

### UX-001 — Desktop-first, responsive
Target utama adalah desktop/laptop karena aktivitas seperti input budget, review tabel, approval, dan report lebih nyaman di layar besar.

Tetap mendukung tablet dan smartphone untuk:
- melihat dashboard,
- melihat notifikasi,
- melakukan approval sederhana,
- melihat detail plan,
- melihat report ringkas.

Input plan kompleks dan pengelolaan master data tetap dioptimalkan untuk desktop.

### UX-002 — Progressive disclosure
User hanya melihat detail yang dibutuhkan pada tahap saat ini.

Contoh:
- dashboard menampilkan KPI ringkas;
- detail item tampil ketika membuka plan;
- audit trail tidak memenuhi halaman utama;
- pengaturan teknis hanya muncul untuk admin.

### UX-003 — Permission-aware navigation
Menu tidak hanya disabled, tetapi disembunyikan jika user memang tidak memiliki permission.

Namun denial tetap divalidasi backend.

### UX-004 — Financial clarity
Semua nominal uang:
- right-aligned pada tabel;
- memakai format lokal;
- memiliki label jelas;
- tidak hanya dibedakan melalui warna;
- dapat menampilkan nilai penuh melalui tooltip/detail jika UI menggunakan bentuk singkat.

### UX-005 — Explicit status
Status workflow dan execution tidak dicampur.

Contoh:
- Workflow: APPROVED
- Pelaksanaan: PARTIALLY_REALIZED

### UX-006 — No silent destructive action
Operasi seperti cancel, reject, revision, reopen fiscal year, atau perubahan workflow harus memakai confirmation dialog dan alasan jika diperlukan.

### UX-007 — Preserve user context
Filter, sorting, pagination, dan selected fiscal year sebaiknya tidak hilang ketika user masuk detail lalu kembali ke daftar.

### UX-008 — Consistent interaction
Semua modul menggunakan pola yang konsisten:
- List
- Filter
- Detail
- Create/Edit
- Submit
- Review/Approval
- History

---

## 3. Application Shell

Layout utama:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Topbar: Logo | Organization | Fiscal Year | Search | Notifications | Profile │
├─────────────────┬────────────────────────────────────────────────────────────┤
│                 │                                                            │
│ Sidebar         │ Main Content                                               │
│                 │                                                            │
│ Dashboard       │ Breadcrumb                                                 │
│ Anggaran        │ Page Title + Actions                                       │
│ Rencana         │ Filters                                                    │
│ Realisasi       │ Content                                                    │
│ Approval        │                                                            │
│ Laporan         │                                                            │
│ Master Data     │                                                            │
│ Administration  │                                                            │
│                 │                                                            │
└─────────────────┴────────────────────────────────────────────────────────────┘
```

Sidebar dapat collapse.

Topbar memuat:
- logo aplikasi;
- nama organisasi;
- active fiscal year selector;
- global search jika nanti diaktifkan;
- notification center;
- profile menu.

---

## 4. Global Fiscal Year Context

Fiscal Year selector ditempatkan pada topbar.

Contoh:

```text
Tahun Anggaran: [ 2027 ▼ ]
```

Fungsi:
- mengubah konteks data mayoritas halaman;
- tidak mengubah data master umum;
- fiscal year yang ACTIVE diberi indikator;
- fiscal year CLOSED tetap dapat dipilih read-only;
- PLANNING dapat dipilih sesuai permission.

Jika user sedang mengisi form dan mencoba berpindah fiscal year, UI memperingatkan jika ada perubahan belum tersimpan.

---

## 5. Navigation Structure V1

### 5.1 Dashboard
- Dashboard Saya
- Dashboard Organisasi (permission)
- Dashboard Unit (scope)

### 5.2 Anggaran
- Tahun Anggaran
- Anggaran Tahunan
- Alokasi Unit
- Revisi Anggaran
- Transfer Anggaran (jika feature flag aktif)

### 5.3 Rencana Anggaran
- Semua Rencana
- Rencana Unit Saya
- Buat Rencana
- Revisi Rencana

### 5.4 Realisasi
- Semua Realisasi
- Realisasi Unit Saya
- Input Realisasi
- Verifikasi Realisasi

### 5.5 Approval
- Inbox Approval
- Pengajuan Saya
- Riwayat Approval

### 5.6 Laporan
- Ringkasan Anggaran
- Alokasi per Unit
- Rencana Anggaran
- Rincian Rencana
- Realisasi
- Budget vs Realization
- Sisa Anggaran
- Tingkat Serapan
- Kategori
- Bulanan
- Approval
- Revision History

### 5.7 Master Data
- Unit Organisasi
- Tipe Unit
- Kategori Anggaran
- Satuan
- Referensi Akun (optional)
- Template Nomor Dokumen

### 5.8 Administration
- Users
- Roles
- Permissions
- Approval Workflows
- Application Settings
- Audit Log
- System Information

Menu yang tidak memiliki permission tidak ditampilkan.

---

## 6. Dashboard V1

### 6.1 Budget Administrator Dashboard

KPI:
- Total Annual Budget
- Allocated
- Unallocated
- Committed
- Realized
- Available
- Utilization %

Visual:
- Budget vs Realization per Unit
- Monthly Realization
- Utilization per Unit
- Budget by Category
- Pending Approval Summary
- Low Absorption Units

Operational list:
- recent submissions;
- plans nearing target date;
- pending approvals aging;
- recent revisions.

### 6.2 Unit PIC Dashboard

KPI:
- Unit Allocation
- Committed
- Realized
- Available
- Draft Pipeline

Lists:
- My Draft Plans
- Submitted Plans
- Revision Required
- Upcoming Activities
- Recent Realizations

### 6.3 Unit Approver Dashboard

KPI:
- Pending Approval
- Waiting > SLA
- Approved This Month
- Returned for Revision

Primary component:
- Approval Inbox.

### 6.4 Management Dashboard

Executive-only presentation:
- Total Budget
- Realization
- Utilization %
- Unit Comparison
- Monthly Trend
- Low Absorption
- High Utilization
- Year-over-Year comparison when historical data exists.

Tidak menampilkan form operasional kecuali permission role lain juga dimiliki.

### 6.5 Auditor Dashboard

- Annual Budget Summary
- Recent Financial Changes
- Approval History
- Revision Activity
- Audit Events
- Filters by user/entity/date.

---

## 7. Budget Plan UX

### 7.1 Create Plan Flow

Gunakan stepper agar form panjang tidak terasa berat:

```text
1. Informasi Dasar
      ↓
2. Rincian Anggaran
      ↓
3. Dokumen Pendukung
      ↓
4. Review
      ↓
5. Simpan Draft / Submit
```

### Step 1 — Informasi Dasar
Fields:
- Fiscal Year (from context, read-only unless permitted)
- Unit
- Title
- Description
- PIC
- Target Date
- Notes

### Step 2 — Rincian Anggaran
Editable table:

| Item | Kategori | Qty | Satuan | Harga Satuan | Subtotal | Aksi |
|---|---|---:|---|---:|---:|---|

Features:
- Add row
- Duplicate row
- Delete row
- Reorder optional
- Inline validation
- Running total
- Remaining allocation indicator

Example summary:

```text
Alokasi Unit       Rp1.000.000.000
Committed            Rp500.000.000
Rencana Ini          Rp200.000.000
Sisa Setelah Approve Rp300.000.000
```

Draft plan tidak langsung mengurangi saldo resmi.

### Step 3 — Attachment
- Upload file
- Description
- File type
- Size
- Uploaded by
- Remove before submission

### Step 4 — Review
Tampilkan read-only summary sebelum submit.

Warning contoh:
- attachment missing jika workflow mensyaratkan;
- target date di luar fiscal year;
- duplicate item;
- total terlalu dekat dengan available budget.

### Step 5
Actions:
- Save Draft
- Submit for Approval
- Cancel editing

---

## 8. Plan Detail Page

Header:

```text
BP-2027-000123
Pengadaan Perangkat Laboratorium

Workflow: APPROVED
Execution: PARTIALLY_REALIZED
```

Summary cards:
- Plan Total
- Realized
- Remaining Plan
- Unit Available

Tabs:

1. Overview
2. Budget Items
3. Realizations
4. Approval History
5. Revisions
6. Attachments
7. Audit/Activity (permission)

Actions hanya muncul jika valid terhadap status + permission:
- Edit Draft
- Submit
- Request Revision
- Cancel
- Add Realization
- Export

---

## 9. Approval Inbox UX

Approval tidak boleh mengharuskan approver membuka banyak halaman untuk memahami konteks.

List columns:
- Document No.
- Plan
- Unit
- Amount
- Submitted By
- Submitted At
- Current Step
- Waiting Time
- Action

Detail approval menggunakan split/summary layout:

```text
Plan Summary
Unit
Amount
Budget Position
Items
Attachments
Previous Approvals
Submitter Notes
```

Footer actions:
- Approve
- Request Revision
- Reject

Request Revision dan Reject wajib comment.

Approve meminta confirmation.

Self-approval:
- tombol Approve tidak muncul/disabled dengan explanation bila submitter = current user dan policy tidak mengizinkan.

---

## 10. Realization UX

Create realization:

Fields:
- Plan (read-only when entered from plan)
- Transaction Date
- Amount
- Description
- Reference Number
- Vendor/Counterparty text optional
- Attachment
- Notes

UI selalu menunjukkan:

```text
Approved Plan    Rp120.000.000
Realized Before   Rp80.000.000
This Realization  Rp20.000.000
Remaining         Rp20.000.000
```

Jika user memasukkan amount > remaining:
- frontend langsung warning/error;
- submit disabled;
- backend tetap menjadi final validator.

Lifecycle:

```text
DRAFT
↓
SUBMITTED
↓
VERIFIED
```

atau:

```text
SUBMITTED
↓
REJECTED
```

Verified realization tidak dapat dihapus langsung.

---

## 11. Annual Budget UX

Halaman menampilkan:

- Fiscal Year
- Original Budget
- Current Budget
- Allocated
- Unallocated
- Status
- Revision Allowed

Jika APPROVED/LOCKED:
- form nominal berubah menjadi read-only;
- action "Ajukan Revisi" hanya tampil jika feature aktif dan permission tersedia.

---

## 12. Allocation UX

Allocation page menggunakan grid/table:

| Unit | Current Allocation | Committed | Realized | Available | Action |
|---|---:|---:|---:|---:|---|

Atas halaman:

```text
Annual Budget   Rp50.000.000.000
Allocated       Rp45.000.000.000
Unallocated      Rp5.000.000.000
```

Create/edit allocation menampilkan dampak sebelum konfirmasi.

Pengurangan allocation ditolak jika akan membuat:
`new_allocation < committed`.

---

## 13. Organization Unit UX

Gunakan kombinasi tree + detail panel.

```text
Universitas
├── Rektorat
├── Fakultas Teknik
│   ├── Informatika
│   └── Sistem Informasi
├── Biro
└── UPT
```

Panel detail:
- Name
- Code
- Type
- Parent
- Active
- Can Receive Budget
- Can Create Plan

Drag-and-drop struktur organisasi tidak dijadikan V1 agar menghindari perubahan hierarki tanpa sengaja. Pemindahan parent dilakukan melalui form dengan confirmation.

---

## 14. User & RBAC UX

### User Detail
Tabs:
- Profile
- Unit Memberships
- Roles
- Effective Permissions
- Activity

Admin harus bisa melihat mengapa user memiliki suatu permission:

```text
plan.approve
Source: Unit Approver
Scope: OWN_UNIT
```

Ini penting untuk debugging authorization.

### Role Detail
- Role Name
- Description
- Permissions grouped by module
- Scope defaults
- Assigned users

Permission matrix menggunakan checkbox per capability tetapi disusun per module agar tidak menjadi ratusan checkbox tanpa struktur.

---

## 15. Reports UX

Pattern:

```text
Report Title
Filters
[Apply] [Reset]

KPI / Summary
Chart (jika relevan)
Data Table

[Export PDF] [Export Excel] [Export CSV]
```

Filter standar:
- Fiscal Year
- Unit
- Category
- Workflow Status
- Execution Status
- Date Range

Export mengikuti filter aktif.

Report besar diexport server-side apabila volume data tinggi di masa depan.

---

## 16. Notification Center

Topbar bell.

Notification types:
- INFO
- SUCCESS
- WARNING
- ACTION_REQUIRED

Item:
- title;
- description;
- timestamp;
- related entity;
- read/unread;
- deep link.

Contoh:
`Rencana BP-2027-00123 menunggu persetujuan Anda.`

---

## 17. Search

Global search belum menjadi dependency V1.

Jika diaktifkan, target awal:
- document number;
- plan title;
- organizational unit;
- realization reference.

Search tidak boleh membocorkan data di luar permission scope.

---

## 18. Tables

Standard behavior:
- server-side pagination;
- sorting;
- filter;
- empty state;
- loading skeleton;
- error retry;
- sticky action column jika diperlukan;
- right alignment untuk nominal;
- configurable page size.

Default page size: 20.

Tidak memuat ribuan record di browser.

---

## 19. Forms

Semua form:
- inline validation;
- error summary untuk submit failure;
- required marker;
- unsaved changes warning;
- keyboard-accessible;
- server errors dipetakan kembali ke field bila memungkinkan.

Untuk nominal:
- user mengetik angka normal;
- UI dapat memformat secara lokal;
- backend menerima representasi numerik yang valid;
- tidak menggunakan float untuk business calculation.

---

## 20. Confirmation Levels

### Low risk
Contoh:
- mark notification read.

Tidak memerlukan modal.

### Medium risk
Contoh:
- delete Draft.

Modal confirmation.

### High risk
Contoh:
- approve budget;
- reject plan;
- reopen fiscal year;
- cancel approved document;
- change approval workflow.

Modal + explanation + reason jika dibutuhkan.

---

## 21. Empty States

Jangan hanya menampilkan tabel kosong.

Contoh:

```text
Belum ada rencana anggaran untuk tahun 2027.

Jika unit Anda telah memperoleh alokasi, Anda dapat mulai membuat rencana.
[+ Buat Rencana]
```

CTA hanya muncul jika user memiliki permission.

---

## 22. Error States

Error dibagi:

- validation error;
- permission denied;
- conflict;
- insufficient budget;
- stale data/version conflict;
- network/server error.

Contoh conflict:

```text
Data ini telah berubah sejak terakhir Anda buka.
Muat ulang data terbaru sebelum melanjutkan.
```

UI tidak boleh otomatis overwrite perubahan user lain.

---

## 23. Responsive Strategy

### >= 1280px
Full sidebar + wide table + charts.

### 768–1279px
Collapsible sidebar; tables dapat horizontal scroll.

### < 768px
Drawer navigation.
Dashboard cards stack.
Complex tables berubah menjadi card/list bila perlu.
Form item budget dapat menggunakan row cards.

Approval sederhana harus tetap nyaman dilakukan.

---

## 24. Accessibility Baseline

- keyboard navigation;
- semantic HTML;
- visible focus;
- label untuk input;
- status tidak hanya menggunakan warna;
- contrast yang layak;
- aria attributes pada komponen interaktif;
- chart memiliki textual summary/alternative.

Target desain mengikuti prinsip WCAG 2.1 AA sebisa mungkin.

---

## 25. Visual Design Direction

Default SIMA:

- Corporate/academic professional
- Minimal
- Dense enough for financial work
- Tidak terlalu dekoratif
- Banyak whitespace namun tabel tetap efisien
- Clear typography hierarchy

Branding configurable:
- Application Name
- Short Name
- Organization Name
- Logo
- Favicon
- Primary Color
- Secondary Color
- Footer Text

Jangan membuat warna organisasi menjadi dependency logic.

---

## 26. Recommended Frontend UI Building Blocks

Tidak dikunci ke library tertentu pada CP-04, tetapi frontend perlu komponen reusable:

- AppShell
- Sidebar
- Topbar
- Breadcrumb
- PageHeader
- StatCard
- DataTable
- FilterBar
- Money
- StatusBadge
- EmptyState
- ErrorState
- LoadingSkeleton
- ConfirmationDialog
- ReasonDialog
- FileUploader
- Stepper
- ApprovalTimeline
- ActivityTimeline
- FiscalYearSelector
- PermissionGuard

---

## 27. Page Route Baseline

Detail lengkap ada pada `CP-04_Page_Route_Map.md`.

Prefix aplikasi internal:
`/app`

Examples:

```text
/login
/app/dashboard

/app/budgets/fiscal-years
/app/budgets/annual
/app/budgets/allocations

/app/plans
/app/plans/new
/app/plans/:planId

/app/realizations
/app/approvals/inbox

/app/reports

/app/admin/users
/app/admin/roles
/app/admin/organization-units
/app/admin/workflows
/app/admin/settings
/app/admin/audit
```

Route access selalu dikombinasikan dengan authorization backend.

---

## 28. Key User Journeys

### Journey A — Budget Administrator
```text
Login
→ Create Fiscal Year
→ Create Annual Budget
→ Submit
→ Approval
→ Allocate to Units
→ Monitor
```

### Journey B — Unit PIC
```text
Login
→ Dashboard
→ Create Plan
→ Add Items
→ Review
→ Submit
→ Track Approval
→ Add Realization after approval
```

### Journey C — Approver
```text
Login
→ Approval Inbox
→ Open Submission
→ Review Budget Position
→ Review Items/Attachments
→ Approve / Revision / Reject
```

### Journey D — Auditor
```text
Login
→ Reports/Audit
→ Filter Fiscal Year/Unit
→ Inspect Document
→ Trace Approval
→ Trace Revision
→ Export
```

---

## 29. UX Business Safeguards

1. Tidak ada tombol edit langsung untuk approved plan.
2. Tidak ada hard delete untuk processed financial documents.
3. Current budget position selalu terlihat saat approval.
4. Nominal plan selalu dihitung dari item.
5. Total realization selalu ditampilkan terhadap approved amount.
6. User diberi warning untuk unsaved changes.
7. Rejection/revision meminta reason.
8. High-risk state changes meminta confirmation.
9. Status workflow/execution selalu ditampilkan terpisah.
10. UI tidak menjadikan hidden button sebagai satu-satunya security control.

---

## 30. Feature Flags / Configurable UX

UI harus dapat menyesuaikan konfigurasi:

- Allow Annual Budget Revision
- Enable Budget Transfer
- Enable Account Reference
- Enable Email Notifications
- Allow Self Approval
- Enable Global Search
- Enable Dark Mode
- Require Attachments for selected workflows

Fitur disabled tidak ditampilkan sebagai menu kosong.

---

## 31. Out of Scope CP-04 / V1

Belum menjadi fokus:
- native mobile app;
- real-time collaborative editing;
- drag-and-drop workflow designer kompleks;
- custom dashboard builder;
- AI chatbot;
- accounting journal UI;
- procurement lifecycle;
- vendor master penuh.

Arsitektur tidak boleh menghalangi pengembangan fitur tersebut jika kelak dibutuhkan.

---

## 32. Diagram Set CP-04

Folder diagram memuat source Mermaid:

1. `01-application-navigation.mmd`
2. `02-budget-plan-wireflow.mmd`
3. `03-approval-wireflow.mmd`
4. `04-realization-wireflow.mmd`
5. `05-role-dashboard-navigation.mmd`
6. `06-page-state-model.mmd`

---

## 33. Keputusan yang Dikunci

- Desktop-first responsive.
- Sidebar + topbar application shell.
- Global fiscal-year context.
- Role/permission-aware navigation.
- Dashboard berbeda menurut role/scope.
- Budget Plan memakai multi-step flow.
- Approval Inbox menjadi area kerja khusus.
- Workflow status dan execution status dipisah di UI.
- Tree UI untuk organizational units.
- Tables memakai server-side pagination.
- Reports mengikuti pola filter → summary → chart/table → export.
- Destructive/high-risk operations memiliki confirmation.
- Branding configurable.
- UI mengikuti business rules backend, bukan menggantikan backend validation.

---

## 34. Status

**CP-04 = BASELINE**

Perubahan besar berikutnya harus dicatat sebagai revision checkpoint.

Next checkpoint:
**CP-05 — Development Readiness Baseline**

CP-05 akan mengunci:
- repository structure final;
- coding standards;
- dependency strategy;
- environment files;
- Docker Compose;
- migrations;
- seed strategy;
- testing matrix;
- CI;
- logging;
- security checklist;
- documentation structure;
- implementation roadmap;
- definition of done;
- initial release plan.
