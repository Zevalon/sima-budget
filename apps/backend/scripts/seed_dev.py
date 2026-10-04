import argparse
import asyncio
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete, select, text
from sqlalchemy.engine import make_url

from app.core.config import get_settings
from app.core.database import Base, get_engine, get_session_factory
from app.core.security import hash_password, hash_session_token
from app.modules.annual_budgets.models import AnnualBudget, AnnualBudgetApproval
from app.modules.audit.models import AuditLog
from app.modules.auth.models import UserSession
from app.modules.budget_foundation.models import BudgetCategory, FiscalYear, UnitOfMeasure
from app.modules.budget_plans.models import (
    BudgetPlan,
    BudgetPlanApproval,
    BudgetPlanItem,
    BudgetPlanVersion,
)
from app.modules.organizations.models import (
    Organization,
    OrganizationUnit,
    OrganizationUnitType,
    UserUnitMembership,
)
from app.modules.realizations.models import Realization
from app.modules.roles.models import Role, UserRoleAssignment
from app.modules.settings.models import ApplicationSetting
from app.modules.unit_allocations.models import UnitAllocation
from app.modules.users.models import User
from app.shared.db import model_registry
from scripts.bootstrap_foundation import ensure_organization

SEED_PROFILE = "sima-dev-baseline-v1"
SAFE_LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "postgres"}

USER_SPECS: tuple[tuple[str, str, str | None, str, str, str | None], ...] = (
    ("sysadmin", "System Administrator", "sysadmin@sima.local", "SYSTEM_ADMIN", "ALL", None),
    ("budgetadmin", "Budget Administrator", "budgetadmin@sima.local", "BUDGET_ADMIN", "ALL", None),
    (
        "management",
        "Management Approver",
        "management@sima.local",
        "MANAGEMENT_APPROVER",
        "ALL",
        None,
    ),
    ("auditor", "Internal Auditor", "auditor@sima.local", "AUDITOR", "ALL", None),
    ("viewer", "Read Only Viewer", "viewer@sima.local", "VIEWER", "ALL", None),
    ("itpic", "PIC Teknologi Informasi", "itpic@sima.local", "UNIT_PIC", "OWN_UNIT", "IT"),
    (
        "itapprover",
        "Approver Teknologi Informasi",
        "itapprover@sima.local",
        "UNIT_APPROVER",
        "OWN_UNIT",
        "IT",
    ),
    (
        "ftipic",
        "PIC Fakultas Teknik dan Informatika",
        "ftipic@sima.local",
        "UNIT_PIC",
        "OWN_UNIT_AND_CHILDREN",
        "FTI",
    ),
    (
        "ftiapprover",
        "Approver Fakultas Teknik dan Informatika",
        "ftiapprover@sima.local",
        "UNIT_APPROVER",
        "OWN_UNIT_AND_CHILDREN",
        "FTI",
    ),
)

UNIT_SPECS: tuple[tuple[str, str, str, str, bool, bool], ...] = (
    ("REKTORAT", "Rektorat", "RECTORATE", "ROOT", False, False),
    ("KEUANGAN", "Biro Keuangan", "BUREAU", "ROOT", True, True),
    ("SDM", "Biro Sumber Daya Manusia", "BUREAU", "ROOT", True, True),
    ("IT", "UPT Teknologi Informasi", "UPT", "ROOT", True, True),
    ("FTI", "Fakultas Teknik dan Informatika", "FACULTY", "ROOT", True, True),
    ("FEB", "Fakultas Ekonomi dan Bisnis", "FACULTY", "ROOT", True, True),
    ("IF", "Program Studi Informatika", "STUDY_PROGRAM", "FTI", True, True),
    ("LPPM", "Lembaga Penelitian dan Pengabdian", "INSTITUTE", "ROOT", True, True),
    ("LIBRARY", "UPT Perpustakaan", "UPT", "ROOT", True, True),
)

CATEGORY_SPECS: tuple[tuple[str, str, str], ...] = (
    ("OPEX", "Operasional", "Belanja operasional rutin organisasi."),
    ("CAPEX", "Belanja Modal", "Pengadaan aset dan investasi jangka panjang."),
    ("PERSONNEL", "Personalia", "Honorarium, tenaga kerja, dan kebutuhan personalia."),
    ("TRAVEL", "Perjalanan Dinas", "Perjalanan dinas dan kegiatan luar kota."),
    ("IT", "Teknologi Informasi", "Perangkat keras, perangkat lunak, dan layanan TI."),
    ("ACADEMIC", "Akademik", "Kegiatan pendidikan dan akademik."),
    ("RESEARCH", "Penelitian", "Penelitian dan pengabdian kepada masyarakat."),
    ("MAINTENANCE", "Pemeliharaan", "Pemeliharaan fasilitas dan aset."),
)

UOM_SPECS: tuple[tuple[str, str], ...] = (
    ("UNIT", "Unit"),
    ("PACKAGE", "Paket"),
    ("MONTH", "Bulan"),
    ("YEAR", "Tahun"),
    ("PERSON", "Orang"),
    ("DAY", "Hari"),
    ("TRIP", "Perjalanan"),
    ("LICENSE", "Lisensi"),
)

FISCAL_YEAR_SPECS: tuple[tuple[str, int, date, date, str], ...] = (
    ("FY2024", 2024, date(2024, 1, 1), date(2024, 12, 31), "CLOSED"),
    ("FY2025", 2025, date(2025, 1, 1), date(2025, 12, 31), "ACTIVE"),
    ("FY2026", 2026, date(2026, 1, 1), date(2026, 12, 31), "PLANNING"),
    ("FY2027", 2027, date(2027, 1, 1), date(2027, 12, 31), "DRAFT"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed deterministic SIMA development data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete all current application rows before applying the development seed.",
    )
    return parser.parse_args()


def assert_reset_is_safe() -> None:
    settings = get_settings()
    url = make_url(settings.database_url)
    host = (url.host or "").lower()

    if settings.app_env != "development":
        raise SystemExit("Reset seed hanya boleh dijalankan pada APP_ENV=development.")
    if host not in SAFE_LOCAL_HOSTS:
        raise SystemExit(
            f"Reset seed ditolak untuk host database non-lokal: {host or '<unknown>'}."
        )
    if url.database not in {"sima", "sima_dev", "sima_development"}:
        raise SystemExit(
            "Reset seed hanya diizinkan untuk database development SIMA "
            f"(database saat ini: {url.database!r})."
        )


def dev_password() -> str:
    password = get_settings().dev_seed_password
    if len(password) < 12:
        raise SystemExit("DEV_SEED_PASSWORD minimal 12 karakter.")
    return password


async def truncate_application_tables() -> None:
    assert_reset_is_safe()
    if not model_registry.MODELS:
        raise RuntimeError("Model registry kosong.")

    table_names = [table.name for table in Base.metadata.sorted_tables]
    if not table_names:
        raise RuntimeError("Tidak ada tabel aplikasi yang terdaftar untuk di-reset.")

    quoted = ", ".join(f'"{name}"' for name in table_names)
    async with get_engine().begin() as connection:
        await connection.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))


async def apply_seed() -> None:
    password = dev_password()
    session_factory = get_session_factory()
    now = datetime.now(UTC)

    async with session_factory() as session:
        organization = await session.scalar(
            select(Organization).where(Organization.code == "DEFAULT")
        )
        if organization is None:
            raise RuntimeError("Foundation organization belum tersedia.")

        setting = await session.scalar(
            select(ApplicationSetting).where(ApplicationSetting.organization_id == organization.id)
        )
        root = await session.scalar(
            select(OrganizationUnit).where(
                OrganizationUnit.organization_id == organization.id,
                OrganizationUnit.code == "ROOT",
            )
        )
        unit_types = {
            item.code: item
            for item in (
                await session.scalars(
                    select(OrganizationUnitType).where(
                        OrganizationUnitType.organization_id == organization.id
                    )
                )
            ).all()
        }
        roles = {
            item.code: item
            for item in (
                await session.scalars(select(Role).where(Role.organization_id == organization.id))
            ).all()
        }
        if setting is None or root is None:
            raise RuntimeError("Foundation bootstrap tidak lengkap.")

        setting.application_name = "SIMA Development"
        setting.application_short_name = "SIMA DEV"
        setting.organization_display_name = "Universitas / Organisasi Demo"
        setting.currency_code = "IDR"
        setting.timezone = "Asia/Jakarta"
        setting.date_format = "DD/MM/YYYY"
        setting.allow_annual_budget_revision = False
        setting.allow_budget_transfer = False
        setting.allow_self_approval = False

        units: dict[str, OrganizationUnit] = {"ROOT": root}
        pending_units = list(UNIT_SPECS)
        while pending_units:
            progressed = False
            for spec in pending_units[:]:
                code, name, type_code, parent_code, can_receive, can_plan = spec
                parent = units.get(parent_code)
                unit_type = unit_types.get(type_code)
                if parent is None or unit_type is None:
                    continue

                unit = await session.scalar(
                    select(OrganizationUnit).where(
                        OrganizationUnit.organization_id == organization.id,
                        OrganizationUnit.code == code,
                    )
                )
                if unit is None:
                    unit = OrganizationUnit(
                        organization_id=organization.id,
                        unit_type_id=unit_type.id,
                        parent_id=parent.id,
                        code=code,
                        name=name,
                        can_receive_budget=can_receive,
                        can_create_budget_plan=can_plan,
                        is_active=True,
                    )
                    session.add(unit)
                    await session.flush()
                else:
                    unit.unit_type_id = unit_type.id
                    unit.parent_id = parent.id
                    unit.name = name
                    unit.can_receive_budget = can_receive
                    unit.can_create_budget_plan = can_plan
                    unit.is_active = True
                units[code] = unit
                pending_units.remove(spec)
                progressed = True
            if not progressed:
                raise RuntimeError("Seed unit organisasi memiliki parent/type yang tidak valid.")

        users: dict[str, User] = {}
        for username, full_name, email, _, _, _ in USER_SPECS:
            user = await session.scalar(select(User).where(User.username == username))
            if user is None:
                user = User(
                    username=username,
                    email=email,
                    full_name=full_name,
                    password_hash=hash_password(password),
                    is_active=True,
                    is_locked=False,
                    failed_login_attempts=0,
                )
                session.add(user)
                await session.flush()
            else:
                user.email = email
                user.full_name = full_name
                user.password_hash = hash_password(password)
                user.is_active = True
                user.is_locked = False
                user.failed_login_attempts = 0
                user.locked_until = None
            users[username] = user

        seeded_user_ids = [user.id for user in users.values()]
        await session.execute(
            delete(UserRoleAssignment).where(UserRoleAssignment.user_id.in_(seeded_user_ids))
        )
        await session.execute(
            delete(UserUnitMembership).where(UserUnitMembership.user_id.in_(seeded_user_ids))
        )
        await session.execute(delete(UserSession).where(UserSession.user_id.in_(seeded_user_ids)))

        global_members = {"sysadmin", "budgetadmin", "management", "auditor", "viewer"}
        for username, _, _, role_code, scope_type, scope_unit_code in USER_SPECS:
            user = users[username]
            role = roles.get(role_code)
            if role is None:
                raise RuntimeError(f"Role seed tidak ditemukan: {role_code}")
            scope_unit = units.get(scope_unit_code) if scope_unit_code else None
            if scope_unit_code and scope_unit is None:
                raise RuntimeError(f"Scope unit seed tidak ditemukan: {scope_unit_code}")

            membership_unit = root if username in global_members else scope_unit
            if membership_unit is None:
                raise RuntimeError(f"Membership unit belum tersedia untuk {username}.")

            session.add(
                UserUnitMembership(
                    user_id=user.id,
                    organization_unit_id=membership_unit.id,
                    job_title=(
                        "Development Account"
                        if username in global_members
                        else full_name_for(username)
                    ),
                    is_primary=True,
                    start_at=date(2024, 1, 1),
                )
            )
            session.add(
                UserRoleAssignment(
                    user_id=user.id,
                    role_id=role.id,
                    scope_type=scope_type,
                    scope_unit_id=scope_unit.id if scope_unit is not None else None,
                )
            )

        for code, name, description in CATEGORY_SPECS:
            item = await session.scalar(
                select(BudgetCategory).where(
                    BudgetCategory.organization_id == organization.id,
                    BudgetCategory.code == code,
                )
            )
            if item is None:
                item = BudgetCategory(
                    organization_id=organization.id,
                    code=code,
                    name=name,
                    description=description,
                    is_active=True,
                )
                session.add(item)
            else:
                item.name = name
                item.description = description
                item.is_active = True

        for code, name in UOM_SPECS:
            item = await session.scalar(
                select(UnitOfMeasure).where(
                    UnitOfMeasure.organization_id == organization.id,
                    UnitOfMeasure.code == code,
                )
            )
            if item is None:
                session.add(
                    UnitOfMeasure(
                        organization_id=organization.id,
                        code=code,
                        name=name,
                        is_active=True,
                    )
                )
            else:
                item.name = name
                item.is_active = True

        fiscal_years: dict[str, FiscalYear] = {}
        for code, year, start_date, end_date, status in FISCAL_YEAR_SPECS:
            item = await session.scalar(
                select(FiscalYear).where(
                    FiscalYear.organization_id == organization.id,
                    FiscalYear.code == code,
                )
            )
            if item is None:
                item = FiscalYear(
                    organization_id=organization.id,
                    code=code,
                    year=year,
                    start_date=start_date,
                    end_date=end_date,
                    status=status,
                )
                session.add(item)
                await session.flush()
            else:
                item.year = year
                item.start_date = start_date
                item.end_date = end_date
                item.status = status
                item.reopened_at = None
                item.reopened_by = None
                item.reopen_reason = None
            fiscal_years[code] = item

        budget_admin = users["budgetadmin"]
        management = users["management"]
        budget_specs = (
            ("FY2024", Decimal("400000000000.00"), 1, "Approved historical budget 2024"),
            ("FY2025", Decimal("500000000000.25"), 2, "Approved active budget 2025"),
            ("FY2026", Decimal("600000000000.00"), 1, "Approved planning budget 2026"),
        )
        budgets: dict[str, AnnualBudget] = {}
        for index, (fy_code, amount, version, notes) in enumerate(budget_specs, start=1):
            fiscal_year = fiscal_years[fy_code]
            submitted_at = now - timedelta(days=90 - index * 10)
            approved_at = submitted_at + timedelta(days=2)
            item = await session.scalar(
                select(AnnualBudget).where(
                    AnnualBudget.organization_id == organization.id,
                    AnnualBudget.fiscal_year_id == fiscal_year.id,
                )
            )
            if item is None:
                item = AnnualBudget(
                    organization_id=organization.id,
                    fiscal_year_id=fiscal_year.id,
                    amount=amount,
                    notes=notes,
                    status="APPROVED",
                    version=version,
                    submitted_by=budget_admin.id,
                    submitted_at=submitted_at,
                    approved_by=management.id,
                    approved_at=approved_at,
                    rejection_reason=None,
                )
                session.add(item)
                await session.flush()
            else:
                item.amount = amount
                item.notes = notes
                item.status = "APPROVED"
                item.version = version
                item.submitted_by = budget_admin.id
                item.submitted_at = submitted_at
                item.approved_by = management.id
                item.approved_at = approved_at
                item.rejection_reason = None
            budgets[fy_code] = item

        budget_ids = [item.id for item in budgets.values()]
        await session.execute(
            delete(AnnualBudgetApproval).where(
                AnnualBudgetApproval.annual_budget_id.in_(budget_ids)
            )
        )
        plan_ids = (
            await session.scalars(
                select(BudgetPlan.id).where(BudgetPlan.organization_id == organization.id)
            )
        ).all()
        if plan_ids:
            await session.execute(
                delete(Realization).where(
                    Realization.budget_plan_id.in_(plan_ids),
                    Realization.correction_of_id.is_not(None),
                )
            )
            await session.execute(
                delete(Realization).where(Realization.budget_plan_id.in_(plan_ids))
            )
            await session.execute(
                delete(BudgetPlanApproval).where(BudgetPlanApproval.budget_plan_id.in_(plan_ids))
            )
        await session.execute(
            delete(BudgetPlan).where(BudgetPlan.organization_id == organization.id)
        )
        await session.execute(
            delete(UnitAllocation).where(UnitAllocation.annual_budget_id.in_(budget_ids))
        )

        approval_rows = [
            AnnualBudgetApproval(
                annual_budget_id=budgets["FY2024"].id,
                submission_no=1,
                status="APPROVED",
                requested_by=budget_admin.id,
                requested_at=now - timedelta(days=300),
                decided_by=management.id,
                decided_at=now - timedelta(days=298),
                decision_note="Disetujui untuk baseline development.",
            ),
            AnnualBudgetApproval(
                annual_budget_id=budgets["FY2025"].id,
                submission_no=1,
                status="REJECTED",
                requested_by=budget_admin.id,
                requested_at=now - timedelta(days=180),
                decided_by=management.id,
                decided_at=now - timedelta(days=178),
                decision_note="Perbaiki rincian dan total pagu.",
            ),
            AnnualBudgetApproval(
                annual_budget_id=budgets["FY2025"].id,
                submission_no=2,
                status="APPROVED",
                requested_by=budget_admin.id,
                requested_at=now - timedelta(days=170),
                decided_by=management.id,
                decided_at=now - timedelta(days=168),
                decision_note="Revisi telah sesuai.",
            ),
            AnnualBudgetApproval(
                annual_budget_id=budgets["FY2026"].id,
                submission_no=1,
                status="APPROVED",
                requested_by=budget_admin.id,
                requested_at=now - timedelta(days=30),
                decided_by=management.id,
                decided_at=now - timedelta(days=28),
                decision_note="Disetujui untuk perencanaan FY2026.",
            ),
        ]
        session.add_all(approval_rows)

        allocation_specs = (
            ("FY2025", "IT", Decimal("100000000000.00"), "Operasional dan pengembangan TI"),
            ("FY2025", "FTI", Decimal("150000000000.00"), "Program fakultas"),
            ("FY2025", "FEB", Decimal("100000000000.00"), "Program fakultas"),
            ("FY2025", "LPPM", Decimal("50000000000.00"), "Penelitian dan pengabdian"),
            ("FY2026", "IT", Decimal("120000000000.00"), "Baseline alokasi TI"),
            ("FY2026", "FTI", Decimal("100000000000.00"), "Baseline alokasi FTI"),
            ("FY2026", "FEB", Decimal("80000000000.00"), "Baseline alokasi FEB"),
        )
        allocations: list[UnitAllocation] = []
        for fy_code, unit_code, amount, notes in allocation_specs:
            item = UnitAllocation(
                organization_id=organization.id,
                fiscal_year_id=fiscal_years[fy_code].id,
                annual_budget_id=budgets[fy_code].id,
                organization_unit_id=units[unit_code].id,
                amount=amount,
                notes=notes,
                version=1,
            )
            allocations.append(item)
        session.add_all(allocations)
        await session.flush()

        allocations_by_key = {
            (fy_code, unit_code): allocation
            for (fy_code, unit_code, _, _), allocation in zip(
                allocation_specs, allocations, strict=True
            )
        }
        categories_by_code = {
            item.code: item
            for item in (
                await session.scalars(
                    select(BudgetCategory).where(BudgetCategory.organization_id == organization.id)
                )
            ).all()
        }
        uoms_by_code = {
            item.code: item
            for item in (
                await session.scalars(
                    select(UnitOfMeasure).where(UnitOfMeasure.organization_id == organization.id)
                )
            ).all()
        }

        plan_specs = (
            (
                "DEV-FY2026-IT-001",
                "IT",
                "itpic",
                "PENDING_APPROVAL",
                "Modernisasi Infrastruktur TI",
                "Pengajuan baseline untuk pengujian approval rencana anggaran unit TI.",
                (
                    (
                        "IT",
                        "LICENSE",
                        "Lisensi perangkat lunak institusi",
                        Decimal("100"),
                        Decimal("100000000.00"),
                    ),
                    (
                        "IT",
                        "UNIT",
                        "Perangkat jaringan dan server",
                        Decimal("20"),
                        Decimal("250000000.00"),
                    ),
                ),
                "itapprover",
                None,
            ),
            (
                "DEV-FY2026-IT-APPROVED-001",
                "IT",
                "itpic",
                "APPROVED",
                "Operasional Platform Digital",
                "Baseline commitment APPROVED untuk pengujian saldo tersedia Phase 3C.",
                (
                    (
                        "IT",
                        "MONTH",
                        "Operasional layanan cloud",
                        Decimal("12"),
                        Decimal("1500000000.00"),
                    ),
                    (
                        "OPEX",
                        "UNIT",
                        "Perpanjangan dukungan perangkat inti",
                        Decimal("12"),
                        Decimal("1000000000.00"),
                    ),
                ),
                "itapprover",
                "Disetujui sebagai commitment baseline FY2026.",
            ),
            (
                "DEV-FY2026-FTI-001",
                "FTI",
                "ftipic",
                "REJECTED",
                "Penguatan Laboratorium Informatika",
                "Baseline fakultas yang ditolak untuk pengujian revisi Phase 3B.",
                (
                    (
                        "CAPEX",
                        "UNIT",
                        "Perangkat workstation laboratorium",
                        Decimal("20"),
                        Decimal("500000000.00"),
                    ),
                    (
                        "OPEX",
                        "MONTH",
                        "Layanan pendukung laboratorium",
                        Decimal("12"),
                        Decimal("100000000.00"),
                    ),
                ),
                "ftiapprover",
                "Perjelas prioritas dan justifikasi item sebelum diajukan ulang.",
            ),
        )
        for (
            plan_number,
            unit_code,
            username,
            plan_status,
            title,
            description,
            item_specs,
            approver_username,
            rejection_reason,
        ) in plan_specs:
            allocation = allocations_by_key[("FY2026", unit_code)]
            submitted_at = now - timedelta(days=5 if unit_code == "IT" else 8)
            decided_at = (
                None if plan_status == "PENDING_APPROVAL" else submitted_at + timedelta(days=1)
            )
            approved = plan_status == "APPROVED"
            rejected = plan_status == "REJECTED"
            plan = BudgetPlan(
                organization_id=organization.id,
                fiscal_year_id=fiscal_years["FY2026"].id,
                unit_allocation_id=allocation.id,
                organization_unit_id=units[unit_code].id,
                plan_number=plan_number,
                status=plan_status,
                current_version_no=1,
                row_version=2 if plan_status == "PENDING_APPROVAL" else 3,
                created_by=users[username].id,
                submitted_by=users[username].id,
                submitted_at=submitted_at,
                approved_by=users[approver_username].id if approved else None,
                approved_at=decided_at if approved else None,
                rejection_reason=rejection_reason if rejected else None,
            )
            session.add(plan)
            await session.flush()

            item_amounts = [quantity * unit_price for _, _, _, quantity, unit_price in item_specs]
            version = BudgetPlanVersion(
                organization_id=organization.id,
                budget_plan_id=plan.id,
                version_no=1,
                title=title,
                description=description,
                total_amount=sum(item_amounts, Decimal("0.00")),
                created_by=users[username].id,
            )
            session.add(version)
            await session.flush()

            for line_no, (
                category_code,
                uom_code,
                item_description,
                quantity,
                unit_price,
            ) in enumerate(item_specs, start=1):
                session.add(
                    BudgetPlanItem(
                        organization_id=organization.id,
                        plan_version_id=version.id,
                        line_no=line_no,
                        budget_category_id=categories_by_code[category_code].id,
                        unit_of_measure_id=uoms_by_code[uom_code].id,
                        description=item_description,
                        quantity=quantity,
                        unit_price=unit_price,
                        amount=quantity * unit_price,
                        notes=None,
                    )
                )

            approval_status = {
                "PENDING_APPROVAL": "PENDING",
                "REJECTED": "REJECTED",
                "APPROVED": "APPROVED",
            }[plan_status]
            session.add(
                BudgetPlanApproval(
                    organization_id=organization.id,
                    budget_plan_id=plan.id,
                    plan_version_id=version.id,
                    submission_no=1,
                    status=approval_status,
                    requested_by=users[username].id,
                    requested_at=submitted_at,
                    decided_by=(
                        users[approver_username].id
                        if approval_status in {"APPROVED", "REJECTED"}
                        else None
                    ),
                    decided_at=decided_at,
                    decision_note=rejection_reason,
                )
            )

        fy2025_allocation = allocations_by_key[("FY2025", "IT")]
        fy2025_plan = BudgetPlan(
            organization_id=organization.id,
            fiscal_year_id=fiscal_years["FY2025"].id,
            unit_allocation_id=fy2025_allocation.id,
            organization_unit_id=units["IT"].id,
            plan_number="DEV-FY2025-IT-REALIZATION-001",
            status="APPROVED",
            current_version_no=1,
            row_version=3,
            created_by=users["itpic"].id,
            submitted_by=users["itpic"].id,
            submitted_at=now - timedelta(days=220),
            approved_by=users["itapprover"].id,
            approved_at=now - timedelta(days=218),
            rejection_reason=None,
        )
        session.add(fy2025_plan)
        await session.flush()
        fy2025_version = BudgetPlanVersion(
            organization_id=organization.id,
            budget_plan_id=fy2025_plan.id,
            version_no=1,
            title="Operasional Infrastruktur TI FY2025",
            description="Baseline APPROVED untuk smoke test realisasi Phase 4.",
            total_amount=Decimal("20000000000.00"),
            created_by=users["itpic"].id,
        )
        session.add(fy2025_version)
        await session.flush()
        session.add_all(
            [
                BudgetPlanItem(
                    organization_id=organization.id,
                    plan_version_id=fy2025_version.id,
                    line_no=1,
                    budget_category_id=categories_by_code["IT"].id,
                    unit_of_measure_id=uoms_by_code["MONTH"].id,
                    description="Layanan infrastruktur dan cloud",
                    quantity=Decimal("12"),
                    unit_price=Decimal("1000000000.00"),
                    amount=Decimal("12000000000.00"),
                    notes=None,
                ),
                BudgetPlanItem(
                    organization_id=organization.id,
                    plan_version_id=fy2025_version.id,
                    line_no=2,
                    budget_category_id=categories_by_code["IT"].id,
                    unit_of_measure_id=uoms_by_code["UNIT"].id,
                    description="Perangkat pendukung infrastruktur",
                    quantity=Decimal("8"),
                    unit_price=Decimal("1000000000.00"),
                    amount=Decimal("8000000000.00"),
                    notes=None,
                ),
            ]
        )
        session.add(
            BudgetPlanApproval(
                organization_id=organization.id,
                budget_plan_id=fy2025_plan.id,
                plan_version_id=fy2025_version.id,
                submission_no=1,
                status="APPROVED",
                requested_by=users["itpic"].id,
                requested_at=now - timedelta(days=220),
                decided_by=users["itapprover"].id,
                decided_at=now - timedelta(days=218),
                decision_note="Approved realization baseline.",
            )
        )
        posted_realization = Realization(
            organization_id=organization.id,
            fiscal_year_id=fiscal_years["FY2025"].id,
            budget_plan_id=fy2025_plan.id,
            plan_version_id=fy2025_version.id,
            organization_unit_id=units["IT"].id,
            realization_number="DEV-RLZ-FY2025-IT-001",
            status="POSTED",
            realization_date=date(2025, 3, 15),
            reference_number="INV-DEV-2025-001",
            description="Pembayaran layanan infrastruktur triwulan pertama",
            vendor_name="Vendor Infrastruktur Demo",
            amount=Decimal("5000000000.00"),
            row_version=2,
            created_by=users["itpic"].id,
            posted_by=users["itpic"].id,
            posted_at=now - timedelta(days=200),
        )
        draft_realization = Realization(
            organization_id=organization.id,
            fiscal_year_id=fiscal_years["FY2025"].id,
            budget_plan_id=fy2025_plan.id,
            plan_version_id=fy2025_version.id,
            organization_unit_id=units["IT"].id,
            realization_number="DEV-RLZ-FY2025-IT-002",
            status="DRAFT",
            realization_date=date(2025, 4, 1),
            reference_number="DRAFT-DEV-2025-002",
            description="Draft pembelian perangkat pendukung",
            vendor_name=None,
            amount=Decimal("2000000000.00"),
            row_version=1,
            created_by=users["itpic"].id,
        )
        cancelled_realization = Realization(
            organization_id=organization.id,
            fiscal_year_id=fiscal_years["FY2025"].id,
            budget_plan_id=fy2025_plan.id,
            plan_version_id=fy2025_version.id,
            organization_unit_id=units["IT"].id,
            realization_number="DEV-RLZ-FY2025-IT-003",
            status="CANCELLED",
            realization_date=date(2025, 4, 10),
            reference_number="CANCEL-DEV-2025-003",
            description="Contoh draft realisasi yang dibatalkan",
            vendor_name=None,
            amount=Decimal("1000000000.00"),
            row_version=2,
            created_by=users["itpic"].id,
            cancelled_by=users["itpic"].id,
            cancelled_at=now - timedelta(days=180),
            cancellation_reason="Dokumen pengadaan dibatalkan pada baseline development.",
        )
        reversed_realization = Realization(
            organization_id=organization.id,
            fiscal_year_id=fiscal_years["FY2025"].id,
            budget_plan_id=fy2025_plan.id,
            plan_version_id=fy2025_version.id,
            organization_unit_id=units["IT"].id,
            realization_number="DEV-RLZ-FY2025-IT-004",
            status="REVERSED",
            realization_date=date(2025, 5, 10),
            reference_number="REV-DEV-2025-004",
            description="Contoh realisasi yang telah direversal",
            vendor_name="Vendor Koreksi Demo",
            amount=Decimal("1500000000.00"),
            row_version=3,
            created_by=users["itpic"].id,
            posted_by=users["itpic"].id,
            posted_at=now - timedelta(days=170),
            reversed_by=users["itpic"].id,
            reversed_at=now - timedelta(days=160),
            reversal_reason="Nominal pada dokumen sumber perlu dikoreksi.",
        )
        session.add_all(
            [
                posted_realization,
                draft_realization,
                cancelled_realization,
                reversed_realization,
            ]
        )
        await session.flush()
        correction_realization = Realization(
            organization_id=organization.id,
            fiscal_year_id=fiscal_years["FY2025"].id,
            budget_plan_id=fy2025_plan.id,
            plan_version_id=fy2025_version.id,
            organization_unit_id=units["IT"].id,
            realization_number="DEV-RLZ-FY2025-IT-005",
            status="DRAFT",
            realization_date=date(2025, 5, 10),
            reference_number="CORR-REV-DEV-2025-004",
            description="Draft koreksi dari realisasi yang direversal",
            vendor_name="Vendor Koreksi Demo",
            amount=Decimal("1400000000.00"),
            row_version=1,
            created_by=users["itpic"].id,
            correction_of_id=reversed_realization.id,
        )
        session.add(correction_realization)

        viewer = users["viewer"]
        expired_at = now - timedelta(days=1)
        session.add(
            UserSession(
                user_id=viewer.id,
                token_hash=hash_session_token(
                    "sima-dev-seed-revoked-session",
                    get_settings().session_secret,
                ),
                expires_at=expired_at,
                revoked_at=expired_at - timedelta(hours=1),
                last_seen_at=expired_at - timedelta(hours=2),
                ip_address="127.0.0.1",
                user_agent="SIMA development seed",
                created_at=expired_at - timedelta(days=1),
            )
        )

        await session.execute(
            delete(AuditLog).where(AuditLog.metadata_json.contains({"seed_profile": SEED_PROFILE}))
        )
        session.add_all(
            [
                AuditLog(
                    organization_id=organization.id,
                    actor_user_id=budget_admin.id,
                    action="ANNUAL_BUDGET_APPROVED",
                    entity_type="annual_budget",
                    entity_id=budgets["FY2026"].id,
                    before_data={"status": "PENDING_APPROVAL"},
                    after_data={"status": "APPROVED", "amount": str(budgets["FY2026"].amount)},
                    metadata_json={"seed_profile": SEED_PROFILE},
                ),
                AuditLog(
                    organization_id=organization.id,
                    actor_user_id=budget_admin.id,
                    action="UNIT_ALLOCATION_CREATED",
                    entity_type="unit_allocation",
                    entity_id=allocations[-1].id,
                    after_data={"amount": str(allocations[-1].amount)},
                    metadata_json={"seed_profile": SEED_PROFILE},
                ),
                AuditLog(
                    organization_id=organization.id,
                    actor_user_id=users["itpic"].id,
                    action="REALIZATION_POSTED",
                    entity_type="realization",
                    entity_id=posted_realization.id,
                    after_data={
                        "status": "POSTED",
                        "amount": str(posted_realization.amount),
                    },
                    metadata_json={"seed_profile": SEED_PROFILE},
                ),
                AuditLog(
                    organization_id=organization.id,
                    actor_user_id=users["itpic"].id,
                    action="REALIZATION_CANCELLED",
                    entity_type="realization",
                    entity_id=cancelled_realization.id,
                    after_data={"status": "CANCELLED"},
                    metadata_json={"seed_profile": SEED_PROFILE},
                ),
                AuditLog(
                    organization_id=organization.id,
                    actor_user_id=users["itpic"].id,
                    action="REALIZATION_REVERSED",
                    entity_type="realization",
                    entity_id=reversed_realization.id,
                    after_data={"status": "REVERSED"},
                    metadata_json={"seed_profile": SEED_PROFILE},
                ),
                AuditLog(
                    organization_id=organization.id,
                    actor_user_id=users["itpic"].id,
                    action="REALIZATION_CORRECTION_DRAFT_CREATED",
                    entity_type="realization",
                    entity_id=correction_realization.id,
                    after_data={
                        "status": "DRAFT",
                        "correction_of_id": str(reversed_realization.id),
                    },
                    metadata_json={"seed_profile": SEED_PROFILE},
                ),
                AuditLog(
                    organization_id=organization.id,
                    actor_user_id=users["sysadmin"].id,
                    action="DEV_SEED_APPLIED",
                    entity_type="development_seed",
                    entity_id=None,
                    metadata_json={"seed_profile": SEED_PROFILE},
                ),
            ]
        )

        await session.commit()


def full_name_for(username: str) -> str:
    for item_username, full_name, *_ in USER_SPECS:
        if item_username == username:
            return full_name
    return username


async def main() -> None:
    args = parse_args()
    if args.reset:
        print("[dev-seed] Menghapus seluruh data aplikasi development...")
        await truncate_application_tables()

    print("[dev-seed] Memastikan foundation bootstrap...")
    await ensure_organization()
    print("[dev-seed] Menerapkan baseline development seed...")
    await apply_seed()

    password = dev_password()
    print("Development seed applied successfully.")
    print(f"Profile: {SEED_PROFILE}")
    print("Login password seluruh akun seed:", password)
    print("Akun utama: sysadmin, budgetadmin, management, auditor, viewer")
    print("Akun unit: itpic, itapprover, ftipic, ftiapprover")
    print(
        "FY2025 = ACTIVE + approved plan + posted/draft/cancelled/reversed/correction realization; "
        "FY2026 = PLANNING + planning/approval/commitment scenarios."
    )


if __name__ == "__main__":
    asyncio.run(main())
