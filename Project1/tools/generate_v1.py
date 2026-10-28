import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import date, datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
sys.dont_write_bytecode = True

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

import completion_specs as completion
from workflows_v13 import (
    NORTHSTAR_DISRUPTION_WINDOWS,
    ORG_NSC_MANAGERS,
    PROJECT_TEAM_LEADERS,
    _dual_review_meta,
    build_workflows,
    project_code,
    reconcile_document_snapshots,
    stable_id,
    validate_workflows,
)

# -------------------------------------------------------------
# Configuration & Constants (Phase 1: Deterministic & Reproducible)
# Vietnam Timezone (UTC+07:00), Working Calendar, Holidays & Overtime (17:00-22:00)
# -------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent  # Points to Project1

TODAY = date(2026, 10, 12)  # As-of date (Monday)
START = date(2026, 4, 16)   # Start date (Thursday)
SPRINT_BASE = date(2026, 4, 14)  # Thirteen inclusive 14-day sprints end on TODAY
DAYS_TOTAL = (TODAY - START).days + 1  # 180 calendar days
VN_TZ = "+07:00"

# Vietnam public holidays inside the 2026-04-16 .. 2026-10-12 window:
# - 2026-04-27 (Mon): Hung Kings' Commemoration Day compensatory holiday (10/3 Lunar fell on Sun 2026-04-26)
# - 2026-04-30 (Thu): Reunification Day
# - 2026-05-01 (Fri): International Labor Day
# - 2026-09-01 (Tue) & 2026-09-02 (Wed): National Day holiday window
VN_HOLIDAYS = {
    date(2026, 4, 27),
    date(2026, 4, 30),
    date(2026, 5, 1),
    date(2026, 9, 1),
    date(2026, 9, 2),
}

# Designated Saturday incident / canary release war-room dates (only P0/Highest incident/release OT allowed)
WEEKEND_INCIDENT_DATES = {
    date(2026, 8, 29),   # Checkout idempotency race war-room (DOC-CHKO-RCA-008)
    date(2026, 9, 26),   # Payment duplicate webhook containment war-room (DOC-PAY-RCA-006)
    date(2026, 10, 10),  # Pre-release staging dress rehearsal & migration war-room
}

# Automated 24/7 system bots (run nights, weekends, and holidays)
SYSTEM_BOTS = [
    {"bot_id": "BOT-SFTP-SYNC", "display_name": "Meridian SFTP Catalog Sync Worker", "schedule": "02:00:00+07:00"},
    {"bot_id": "BOT-INV-EXPIRY", "display_name": "Inventory Lease Expiry Sweeper", "schedule": "03:30:00+07:00"},
    {"bot_id": "BOT-CI-RUNNER", "display_name": "Northstar GitLab CI/CD Runner", "schedule": "continuous_24x7"},
    {"bot_id": "BOT-ALERT-MANAGER", "display_name": "Prometheus SLO Alertmanager", "schedule": "continuous_24x7"},
]

# Weekdays (128 Mon-Fri days) and actual human working days (123 working days excluding 5 VN holidays)
ALL_DAYS = [START + timedelta(days=i) for i in range(DAYS_TOTAL)]
WEEKDAYS = [d for d in ALL_DAYS if d.weekday() < 5]
TOTAL_WEEKDAYS = len(WEEKDAYS)
assert TOTAL_WEEKDAYS == 128, f"Expected 128 weekdays, got {TOTAL_WEEKDAYS}"

WORKING_DAYS = [d for d in WEEKDAYS if d not in VN_HOLIDAYS]
TOTAL_WORKING_DAYS = len(WORKING_DAYS)
assert TOTAL_WORKING_DAYS == 123, f"Expected 123 working days after 5 VN holidays, got {TOTAL_WORKING_DAYS}"
WORKING_DAYS_SET = set(WORKING_DAYS)

# Distribute 1,373 bundled daily engineering docs strictly across the 123 actual WORKING_DAYS:
# 20 working days with 12 docs + 103 working days with 11 docs = 240 + 1,133 = 1,373 docs (0 on weekends/holidays!)
DAILY_DOC_TARGETS = []
acc = 0
for i in range(TOTAL_WORKING_DAYS):
    acc += 20
    if acc >= TOTAL_WORKING_DAYS:
        acc -= TOTAL_WORKING_DAYS
        DAILY_DOC_TARGETS.append(12)
    else:
        DAILY_DOC_TARGETS.append(11)

assert len(DAILY_DOC_TARGETS) == 123
assert sum(1 for x in DAILY_DOC_TARGETS if x == 12) == 20
assert sum(1 for x in DAILY_DOC_TARGETS if x == 11) == 103
assert sum(DAILY_DOC_TARGETS) == 1373

def snap_to_working_day(d, prefer_forward=True):
    """Snap any calendar date to an active human working day (Mon-Fri, not in VN_HOLIDAYS) within [START, TODAY]."""
    if d < START:
        d = START
    if d > TODAY:
        d = TODAY
    if d in WORKING_DAYS_SET:
        return d
    step = 1 if prefer_forward else -1
    curr = d
    for _ in range(10):
        curr = curr + timedelta(days=step)
        if START <= curr <= TODAY and curr in WORKING_DAYS_SET:
            return curr
    curr = d
    for _ in range(10):
        curr = curr - timedelta(days=step)
        if START <= curr <= TODAY and curr in WORKING_DAYS_SET:
            return curr
    return TODAY

def snap_future_working_day(d):
    """Snap a due_date (which may be after TODAY) to a Monday-Friday non-holiday working day."""
    curr = d
    while curr.weekday() >= 5 or curr in VN_HOLIDAYS:
        curr += timedelta(days=1)
    return curr

def add_working_days(d, num_days, cap_at_today=True):
    """Advance `num_days` working days from `d`."""
    curr = snap_to_working_day(d, prefer_forward=True)
    remaining = max(0, num_days)
    while remaining > 0:
        nxt = curr + timedelta(days=1)
        if cap_at_today and nxt > TODAY:
            return TODAY
        if nxt.weekday() < 5 and nxt not in VN_HOLIDAYS:
            curr = nxt
            remaining -= 1
        else:
            curr = nxt
            if cap_at_today and curr > TODAY:
                return TODAY
    return snap_to_working_day(curr, prefer_forward=False) if cap_at_today else snap_future_working_day(curr)

# Regular working hours: 08:00-11:55 and 13:00-16:55 (Lunch 12:00-12:59 has ZERO human activity)
REGULAR_HOURS_MORNING = [8, 9, 10, 11]
REGULAR_HOURS_AFTERNOON = [13, 14, 15, 16]
REGULAR_HOURS_ALL = REGULAR_HOURS_MORNING + REGULAR_HOURS_AFTERNOON
# Overtime hours: 17:00-21:55 (5 PM to 10 PM Vietnam time)
OVERTIME_HOURS = [17, 18, 19, 20, 21]

def make_human_timestamp(d, seed_val, is_ot=False, slot_index=0):
    """Create a deterministic ISO-8601 timestamp with +07:00 offset respecting lunch break and OT rules."""
    if is_ot:
        hr = OVERTIME_HOURS[(seed_val + slot_index) % len(OVERTIME_HOURS)]
        mn = (seed_val * 7 + slot_index * 13 + 5) % 56
        sc = (seed_val * 11 + slot_index * 17 + 3) % 60
    else:
        hr = REGULAR_HOURS_ALL[(seed_val + slot_index * 2) % len(REGULAR_HOURS_ALL)]
        mn = (seed_val * 5 + slot_index * 11 + 4) % 56
        sc = (seed_val * 9 + slot_index * 19 + 7) % 60
    return f"{d.isoformat()}T{hr:02d}:{mn:02d}:{sc:02d}{VN_TZ}"

def calc_business_hours_between(start_ts, end_ts, ot_hours=0.0):
    """Calculate exact elapsed business hours by intersecting [start_ts, end_ts] with (08:00-12:00, 13:00-17:00) on working days + logged overtime_hours."""
    start_dt = datetime.fromisoformat(start_ts)
    end_dt = datetime.fromisoformat(end_ts)
    if end_dt <= start_dt:
        return round(ot_hours, 1)
    tz = start_dt.tzinfo
    total_reg_seconds = 0.0
    cur_d = start_dt.date()
    end_d = end_dt.date()
    while cur_d <= end_d:
        if cur_d in WORKING_DAYS_SET:
            for sh_start_hr, sh_end_hr in ((8, 12), (13, 17)):
                sh_start = datetime(cur_d.year, cur_d.month, cur_d.day, sh_start_hr, 0, 0, tzinfo=tz)
                sh_end = datetime(cur_d.year, cur_d.month, cur_d.day, sh_end_hr, 0, 0, tzinfo=tz)
                ov_start = max(start_dt, sh_start)
                ov_end = min(end_dt, sh_end)
                if ov_end > ov_start:
                    total_reg_seconds += (ov_end - ov_start).total_seconds()
        cur_d += timedelta(days=1)
    return round((total_reg_seconds / 3600.0) + ot_hours, 1)

DIRECTORIES = [
    ROOT / "documents" / "markdown" / "bundles",
    ROOT / "documents" / "markdown" / "formal",
    ROOT / "documents" / "docx",
    ROOT / "structured",
    ROOT / "evaluation",
    ROOT / "fixtures" / "attachments",
]
for d in DIRECTORIES:
    d.mkdir(parents=True, exist_ok=True)

import zipfile
import io
import re

def canonicalize_zip_file(path):
    """Normalize zip entry timestamps and core.xml dates to ensure byte-identical reproducibility."""
    raw_bytes = Path(path).read_bytes()
    in_buf = io.BytesIO(raw_bytes)
    out_buf = io.BytesIO()
    with zipfile.ZipFile(in_buf, 'r') as zf_in, zipfile.ZipFile(out_buf, 'w', compression=zipfile.ZIP_DEFLATED) as zf_out:
        for name in sorted(zf_in.namelist()):
            data = zf_in.read(name)
            if name.endswith('core.xml'):
                data = re.sub(rb'(<dcterms:created[^>]*>).*?(</dcterms:created>)', rb'\g<1>2026-10-12T00:00:00Z\g<2>', data)
                data = re.sub(rb'(<dcterms:modified[^>]*>).*?(</dcterms:modified>)', rb'\g<1>2026-10-12T00:00:00Z\g<2>', data)
            zinfo = zipfile.ZipInfo(name, date_time=(2026, 10, 12, 0, 0, 0))
            zf_out.writestr(zinfo, data)
    Path(path).write_bytes(out_buf.getvalue())

def write_jsonl(rel_path, rows):
    target = ROOT / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def is_package_file(path):
    return (
        path.is_file()
        and "__pycache__" not in path.parts
        and not path.name.endswith((".pyc", ".pyo"))
    )

def compute_section_sha256(text):
    """Canonical section SHA-256: normalized \\n line endings, trimmed trailing whitespace."""
    canonical = text.strip().replace("\r\n", "\n")
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

# -------------------------------------------------------------
# 1. Organizations (3)
# -------------------------------------------------------------
orgs = [
    {"org_id": "ORG-NSC", "continuum_org_id": stable_id("org", "ORG-NSC"), "continuum_import_scope": "primary_tenant", "name": "Northstar Commerce Systems", "org_type": "software_company", "domain": "northstar.invalid", "synthetic": True},
    {"org_id": "ORG-MERIDIAN", "continuum_org_id": stable_id("org", "ORG-MERIDIAN"), "continuum_import_scope": "external_counterparty_excluded", "name": "Meridian Outfitters", "org_type": "customer_merchant", "domain": "meridianoutfitters.invalid", "synthetic": True},
    {"org_id": "ORG-PULSEPAY", "continuum_org_id": stable_id("org", "ORG-PULSEPAY"), "continuum_import_scope": "external_counterparty_excluded", "name": "PulsePay Network", "org_type": "integration_partner", "domain": "pulsepay.invalid", "synthetic": True}
]

# -------------------------------------------------------------
# 2. Departments (10)
# -------------------------------------------------------------
dept_data = [
    ("DEPT-EXEC", "ORG-NSC", "Executive & Operations"),
    ("DEPT-PROD", "ORG-NSC", "Product & Experience"),
    ("DEPT-COMMERCE", "ORG-NSC", "Commerce Engineering"),
    ("DEPT-PLATFORM", "ORG-NSC", "Platform & SRE"),
    ("DEPT-QA", "ORG-NSC", "Quality Engineering"),
    ("DEPT-DATA", "ORG-NSC", "Data & Analytics"),
    ("DEPT-SEC", "ORG-NSC", "Information Security"),
    ("DEPT-SUPPORT", "ORG-NSC", "Customer Success & Merchant Support"),
    ("DEPT-MERCH", "ORG-MERIDIAN", "Digital Merchandising & Retail Ops"),
    ("DEPT-PAYOPS", "ORG-PULSEPAY", "API Operations & Partner Settlements")
]
departments = [{"department_id": d[0], "org_id": d[1], "name": d[2], "synthetic": True} for d in dept_data]

# -------------------------------------------------------------
# 3. Members (74: 60 Northstar, 8 Meridian, 6 PulsePay)
# -------------------------------------------------------------
seed_person_data = [
    ("M-001", "Avery Chen", "ORG-NSC", "DEPT-EXEC", "Executive Sponsor"),
    ("M-002", "Jordan Lee", "ORG-NSC", "DEPT-PROD", "Product Manager"),
    ("M-003", "Maya Patel", "ORG-NSC", "DEPT-COMMERCE", "Catalog Principal Engineer"),
    ("M-004", "Ethan Brooks", "ORG-NSC", "DEPT-COMMERCE", "Search Principal Engineer"),
    ("M-005", "Sofia Nguyen", "ORG-NSC", "DEPT-COMMERCE", "Checkout Lead Engineer"),
    ("M-006", "Noah Kim", "ORG-NSC", "DEPT-COMMERCE", "Payment Orchestration Engineer"),
    ("M-007", "Priya Shah", "ORG-NSC", "DEPT-COMMERCE", "Inventory & Stock Engineer"),
    ("M-008", "Lucas Martin", "ORG-NSC", "DEPT-COMMERCE", "Orders & Fulfillment Engineer"),
    ("M-009", "Grace Wilson", "ORG-NSC", "DEPT-PLATFORM", "Staff Platform Engineer"),
    ("M-010", "Owen Garcia", "ORG-NSC", "DEPT-QA", "QA Lead"),
    ("M-011", "Zoe Park", "ORG-NSC", "DEPT-DATA", "Analytics Lead Engineer"),
    ("M-012", "Daniel Foster", "ORG-NSC", "DEPT-SEC", "Principal Security Engineer"),
    ("M-013", "Amara Okafor", "ORG-NSC", "DEPT-PLATFORM", "Site Reliability Engineer"),
    ("M-014", "Isla Thompson", "ORG-NSC", "DEPT-PROD", "Product Designer"),
    ("M-015", "Ravi Desai", "ORG-NSC", "DEPT-SUPPORT", "Merchant Success Lead"),
    ("M-016", "Morgan Ellis", "ORG-MERIDIAN", "DEPT-MERCH", "Merchant Product Owner"),
    ("M-017", "Taylor Reed", "ORG-PULSEPAY", "DEPT-PAYOPS", "Partner Integration Engineer"),
    ("M-018", "Casey Rivera", "ORG-NSC", "DEPT-COMMERCE", "Former Catalog Engineer")  # Inactive since 2026-09-15
]

nsc_additional_names = [
    ("M-019", "Liam Vance", "DEPT-COMMERCE", "Catalog Backend Engineer"),
    ("M-020", "Emma Watson", "DEPT-COMMERCE", "Catalog Frontend Engineer"),
    ("M-021", "Oliver Brown", "DEPT-COMMERCE", "Search Relevance Engineer"),
    ("M-022", "Ava Davis", "DEPT-COMMERCE", "Search Indexing Specialist"),
    ("M-023", "William Miller", "DEPT-COMMERCE", "Cart & Promotions Engineer"),
    ("M-024", "Sophia Wilson", "DEPT-COMMERCE", "Cart Logic Developer"),
    ("M-025", "James Moore", "DEPT-COMMERCE", "Checkout Flow Engineer"),
    ("M-026", "Isabella Taylor", "DEPT-COMMERCE", "Checkout Security Specialist"),
    ("M-027", "Benjamin Anderson", "DEPT-COMMERCE", "Payment Integration Engineer"),
    ("M-028", "Mia Thomas", "DEPT-COMMERCE", "Payment Reconciliation Developer"),
    ("M-029", "Lucas Jackson", "DEPT-COMMERCE", "Inventory Reservation Engineer"),
    ("M-030", "Charlotte White", "DEPT-COMMERCE", "Warehouse Sync Engineer"),
    ("M-031", "Henry Harris", "DEPT-COMMERCE", "Order State Machine Engineer"),
    ("M-032", "Amelia Martin", "DEPT-COMMERCE", "Returns & Refund Engineer"),
    ("M-033", "Alexander Thompson", "DEPT-PLATFORM", "Cloud Infrastructure Architect"),
    ("M-034", "Harper Garcia", "DEPT-PLATFORM", "Kubernetes SRE"),
    ("M-035", "Sebastian Martinez", "DEPT-PLATFORM", "Database Administrator (PostgreSQL)"),
    ("M-036", "Evelyn Robinson", "DEPT-PLATFORM", "Observability & Telemetry Engineer"),
    ("M-037", "Jack Clark", "DEPT-QA", "Automation QA Engineer"),
    ("M-038", "Abigail Rodriguez", "DEPT-QA", "Performance & Load Test Engineer"),
    ("M-039", "Daniel Lewis", "DEPT-QA", "End-to-End Test Engineer"),
    ("M-040", "Emily Lee", "DEPT-QA", "API Contract Test Specialist"),
    ("M-041", "Matthew Walker", "DEPT-DATA", "Data Pipeline Engineer"),
    ("M-042", "Elizabeth Hall", "DEPT-DATA", "Senior Analytics Developer"),
    ("M-043", "Anthony Allen", "DEPT-DATA", "BI & Reporting Specialist"),
    ("M-044", "Sofia Young", "DEPT-DATA", "Event Streaming Specialist"),
    ("M-045", "Devon Vance", "DEPT-COMMERCE", "Former Search Engineer"),  # Inactive since 2026-08-01
    ("M-046", "David Hernandez", "DEPT-SEC", "AppSec Reviewer"),
    ("M-047", "Victoria King", "DEPT-SEC", "Identity & Access Governance Lead"),
    ("M-048", "Joseph Wright", "DEPT-SEC", "Compliance & Audit Specialist"),
    ("M-049", "Chloe Lopez", "DEPT-PROD", "Technical Product Manager"),
    ("M-050", "Samuel Hill", "DEPT-PROD", "Associate Product Manager"),
    ("M-051", "Penelope Scott", "DEPT-PROD", "UX Researcher"),
    ("M-052", "Andrew Green", "DEPT-PROD", "UI/UX Designer"),
    ("M-053", "Ella Adams", "DEPT-SUPPORT", "Technical Support Engineer"),
    ("M-054", "Joshua Baker", "DEPT-SUPPORT", "Merchant Onboarding Specialist"),
    ("M-055", "Grace Gonzalez", "DEPT-SUPPORT", "Merchant Escalations Lead"),
    ("M-056", "Christopher Nelson", "DEPT-SUPPORT", "Merchant Solutions Architect"),
    ("M-057", "Hannah Carter", "DEPT-COMMERCE", "Catalog API Engineer"),
    ("M-058", "Andrew Mitchell", "DEPT-COMMERCE", "Search Ranking Engineer"),
    ("M-059", "Lily Perez", "DEPT-COMMERCE", "Promotion Rules Engineer"),
    ("M-060", "Ryan Roberts", "DEPT-PLATFORM", "Network & Security SRE"),
    ("M-061", "Zoe Turner", "DEPT-COMMERCE", "Orders API Developer"),
    ("M-062", "Nathan Phillips", "DEPT-COMMERCE", "Inventory API Developer")
]

meridian_additional_names = [
    ("M-063", "Claire Bennett", "DEPT-MERCH", "Meridian E-Commerce Director"),
    ("M-064", "Marcus Hayes", "DEPT-MERCH", "Senior Catalog Merchandiser"),
    ("M-065", "Leah Sullivan", "DEPT-MERCH", "Inventory Operations Manager"),
    ("M-066", "Eli Reynolds", "DEPT-MERCH", "Customer Experience Lead"),
    ("M-067", "Nora Ortiz", "DEPT-MERCH", "Fulfillment & Logistics Specialist"),
    ("M-068", "Julian Cooper", "DEPT-MERCH", "Meridian Digital Analyst"),
    ("M-069", "Stella Ward", "DEPT-MERCH", "Meridian Compliance Specialist")
]

pulsepay_additional_names = [
    ("M-070", "Logan Brooks", "DEPT-PAYOPS", "Former PulsePay Integration Specialist"),  # Inactive since 2026-07-15
    ("M-071", "Samira Khan", "DEPT-PAYOPS", "Lead Settlement Engineer"),
    ("M-072", "Chris Vance", "DEPT-PAYOPS", "Fraud & Risk Operations Analyst"),
    ("M-073", "Elena Rostova", "DEPT-PAYOPS", "Webhook Reliability Engineer"),
    ("M-074", "Marcus Sterling", "DEPT-PAYOPS", "PulsePay Technical Account Director")
]

members = []
for mid, name, org, dept, title in seed_person_data:
    status = "inactive" if mid == "M-018" else "active"
    left_at = "2026-09-15" if mid == "M-018" else None
    members.append({
        "member_id": mid,
        "display_name": name,
        "email": f"{mid.lower()}@example.invalid",
        "org_id": org,
        "department_id": dept,
        "job_title": title,
        "account_status": status,
        "joined_at": "2025-11-03",
        "left_at": left_at,
        "synthetic": True
    })

for mid, name, dept, title in nsc_additional_names:
    status = "inactive" if mid == "M-045" else "active"
    left_at = "2026-08-01" if mid == "M-045" else None
    members.append({
        "member_id": mid,
        "display_name": name,
        "email": f"{mid.lower()}@example.invalid",
        "org_id": "ORG-NSC",
        "department_id": dept,
        "job_title": title,
        "account_status": status,
        "joined_at": "2025-12-01",
        "left_at": left_at,
        "synthetic": True
    })

for mid, name, dept, title in meridian_additional_names:
    members.append({
        "member_id": mid,
        "display_name": name,
        "email": f"{mid.lower()}@example.invalid",
        "org_id": "ORG-MERIDIAN",
        "department_id": dept,
        "job_title": title,
        "account_status": "active",
        "joined_at": "2026-01-15",
        "left_at": None,
        "synthetic": True
    })

for mid, name, dept, title in pulsepay_additional_names:
    status = "inactive" if mid == "M-070" else "active"
    left_at = "2026-07-15" if mid == "M-070" else None
    members.append({
        "member_id": mid,
        "display_name": name,
        "email": f"{mid.lower()}@example.invalid",
        "org_id": "ORG-PULSEPAY",
        "department_id": dept,
        "job_title": title,
        "account_status": status,
        "joined_at": "2026-02-01",
        "left_at": left_at,
        "synthetic": True
    })

assert len(members) == 74
member_leave_windows = {}
for _dis_pid, _dis in NORTHSTAR_DISRUPTION_WINDOWS.items():
    member_leave_windows.setdefault(_dis["affected_member_id"], []).append({
        "disruption_id": _dis["disruption_id"],
        "project_id": _dis_pid,
        "kind": _dis["kind"],
        "start": _dis["unavailable_from"],
        "end": _dis["unavailable_to"],
        "backup_member_id": _dis["backup_member_id"],
        "reason": _dis["summary_vi_en"],
    })
for _m in members:
    _mid = _m["member_id"]
    _org = _m["org_id"]
    _inactive = _m["account_status"] == "inactive"
    _m["continuum_user_id"] = stable_id("user", _mid)
    _m["continuum_org_id"] = stable_id("org", _org)
    _m["continuum_org_membership_id"] = stable_id("org-member", f"{_org}:{_mid}")
    _m["continuum_org_role"] = "ADMIN" if (_org == "ORG-NSC" and _mid in ORG_NSC_MANAGERS) else "MEMBER"
    _m["continuum_membership_status"] = "REMOVED" if _inactive else "ACTIVE"
    _m["continuum_import_eligible"] = (_org == "ORG-NSC")
    _m["leave_windows"] = member_leave_windows.get(_mid, [])

# -------------------------------------------------------------
# 4. Access Groups (15) & Memberships
# -------------------------------------------------------------
groups = [
    {"group_id": "GRP-ALL-STAFF", "name": "Northstar Employees", "org_id": "ORG-NSC"},
    {"group_id": "GRP-LEADERS", "name": "Northstar Leadership", "org_id": "ORG-NSC"},
    {"group_id": "GRP-CATALOG", "name": "Catalog Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-SEARCH", "name": "Search & Discovery Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-CART", "name": "Cart & Promotions Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-CHECKOUT", "name": "Checkout Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-PAYMENT", "name": "Payment Integration Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-INVENTORY", "name": "Inventory & Fulfillment Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-ORDERS", "name": "Orders & Returns Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-SECURITY", "name": "Security Reviewers", "org_id": "ORG-NSC"},
    {"group_id": "GRP-SUPPORT", "name": "Merchant Support", "org_id": "ORG-NSC"},
    {"group_id": "GRP-PLATFORM", "name": "Platform & SRE Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-DATA", "name": "Data & Analytics Squad", "org_id": "ORG-NSC"},
    {"group_id": "GRP-MERIDIAN", "name": "Meridian Pilot Team", "org_id": "ORG-MERIDIAN"},
    {"group_id": "GRP-PULSEPAY", "name": "PulsePay Integration Team", "org_id": "ORG-PULSEPAY"}
]

member_groups_map = {}
for m in members:
    mid = m["member_id"]
    org = m["org_id"]
    dept = m["department_id"]
    grps = []
    if org == "ORG-NSC":
        grps.append("GRP-ALL-STAFF")
        if dept in ["DEPT-EXEC", "DEPT-PROD"] and mid in ["M-001", "M-002", "M-049"]:
            grps.append("GRP-LEADERS")
        if dept == "DEPT-COMMERCE":
            if mid in ["M-003", "M-018", "M-019", "M-020", "M-057"]:
                grps.append("GRP-CATALOG")
            if mid in ["M-004", "M-021", "M-022", "M-045", "M-058"]:
                grps.append("GRP-SEARCH")
            if mid in ["M-005", "M-023", "M-024", "M-059"]:
                grps.append("GRP-CART")
            if mid in ["M-005", "M-006", "M-025", "M-026", "M-027", "M-028"]:
                grps.append("GRP-CHECKOUT")
            if mid in ["M-006", "M-027", "M-028"]:
                grps.append("GRP-PAYMENT")
            if mid in ["M-007", "M-029", "M-030", "M-062"]:
                grps.append("GRP-INVENTORY")
            if mid in ["M-008", "M-031", "M-032", "M-061"]:
                grps.append("GRP-ORDERS")
        if dept == "DEPT-PLATFORM":
            grps.append("GRP-PLATFORM")
        if dept == "DEPT-DATA":
            grps.append("GRP-DATA")
        if dept == "DEPT-SEC":
            grps.append("GRP-SECURITY")
        if dept == "DEPT-SUPPORT":
            grps.append("GRP-SUPPORT")
        if dept == "DEPT-QA":
            grps.append("GRP-CHECKOUT")
    elif org == "ORG-MERIDIAN":
        grps.append("GRP-MERIDIAN")
    elif org == "ORG-PULSEPAY":
        grps.append("GRP-PULSEPAY")
    member_groups_map[mid] = grps

memberships = []
for m in members:
    mid = m["member_id"]
    is_inactive = (m["account_status"] == "inactive")
    for gid in member_groups_map.get(mid, []):
        memberships.append({
            "membership_id": f"MEMB-{mid}-{gid}",
            "member_id": mid,
            "group_id": gid,
            "status": "revoked" if is_inactive else "active",
            "valid_from": m["joined_at"],
            "valid_to": m["left_at"] if is_inactive else None,
            "synthetic": True
        })

# -------------------------------------------------------------
# 5. Projects (8) & Sprints Model (Phase 5)
# -------------------------------------------------------------
project_raw = [
    ("NSC-CAT", "Product Catalog & Merchandising", "In Progress", "M-002", "GRP-CATALOG", "Commerce Core", "2026-11-06"),
    ("NSC-SRCH", "Search & Discovery", "In Progress", "M-002", "GRP-SEARCH", "Commerce Core", "2026-11-20"),
    ("NSC-CART", "Cart & Promotions", "In Progress", "M-005", "GRP-CART", "Commerce Core", "2026-10-30"),
    ("NSC-CHKO", "Checkout Experience", "At Risk", "M-005", "GRP-CHECKOUT", "Revenue & Retention", "2026-10-23"),
    ("NSC-PAY", "Payment Orchestration", "At Risk", "M-006", "GRP-PAYMENT", "Revenue & Retention", "2026-10-23"),
    ("NSC-INV", "Inventory & Fulfillment", "In Progress", "M-007", "GRP-INVENTORY", "Commerce Core", "2026-11-13"),
    ("NSC-ORD", "Orders, Returns & Refunds", "In Progress", "M-008", "GRP-ORDERS", "Revenue & Retention", "2026-11-06"),
    ("NSC-PLAT", "Platform Reliability & Governance", "In Progress", "M-009", "GRP-PLATFORM", "Foundation", "2026-12-04")
]

PID_LIST = [p[0] for p in project_raw]
PID_INDEX = {pid: i for i, pid in enumerate(PID_LIST)}

# Generate 13 consecutive 14-day sprints per project (April 14 - Oct 12, 2026)
sprints = []
for pid, p_name, _, _, _, _, _ in project_raw:
    prefix = pid.replace("NSC-", "")
    for s_idx in range(1, 14):
        s_id = f"SPRINT-{prefix}-{s_idx:02d}"
        s_start = SPRINT_BASE + timedelta(days=(s_idx - 1) * 14)
        s_end = s_start + timedelta(days=13)
        s_status = "active" if s_idx == 13 else "closed"

        sp_rec = {
            "sprint_id": s_id,
            "continuum_sprint_id": stable_id("sprint", s_id),
            "continuum_project_id": stable_id("project", pid),
            "continuum_org_id": stable_id("org", "ORG-NSC"),
            "continuum_status": "ACTIVE" if s_status == "active" else "COMPLETED",
            "project_id": pid,
            "sprint_number": s_idx,
            "name": f"{p_name} Sprint {s_idx}",
            "status": s_status,
            "start_date": s_start.isoformat(),
            "end_date": s_end.isoformat(),
            "goal": f"Deliver milestone capabilities for {p_name} in iteration {s_idx}.",
            "synthetic": True
        }
        sprints.append(sp_rec)

projects = [{
    "project_id": p[0],
    "continuum_project_id": stable_id("project", p[0]),
    "continuum_org_id": stable_id("org", "ORG-NSC"),
    "continuum_code": project_code(p[0]),
    "continuum_status": "ACTIVE",
    "methodology": "AGILE_SPRINT",
    "created_by": p[3],
    "continuum_created_by_user_id": stable_id("user", p[3]),
    "team_leader_id": PROJECT_TEAM_LEADERS[p[0]],
    "name": p[1],
    "status": p[2],
    "owner_id": p[3],
    "team_group": p[4],
    "portfolio": p[5],
    "start_date": "2026-03-02",
    "target_date": p[6],
    "current_sprint_id": f"SPRINT-{p[0].replace('NSC-','')}-13",
    "source_system": "Jira",
    "synthetic": True
} for p in project_raw]

# Internal Northstar project squads: all 58 active Northstar staff are assigned across the 8 projects.
# External merchant (ORG-MERIDIAN) and partner (ORG-PULSEPAY) contacts are tracked separately in
# project_external_collaborators so they NEVER inherit internal Northstar GRP-* access groups!
project_devs = {
    "NSC-CAT": ["M-003", "M-019", "M-020", "M-057", "M-002", "M-014", "M-037", "M-041", "M-050", "M-054"],
    "NSC-SRCH": ["M-004", "M-021", "M-022", "M-058", "M-002", "M-011", "M-038", "M-042", "M-051"],
    "NSC-CART": ["M-005", "M-023", "M-024", "M-059", "M-049", "M-039", "M-052", "M-053"],
    "NSC-CHKO": ["M-005", "M-025", "M-026", "M-010", "M-014", "M-037", "M-039", "M-046", "M-049"],
    "NSC-PAY": ["M-006", "M-027", "M-028", "M-012", "M-013", "M-040", "M-044", "M-047", "M-055"],
    "NSC-INV": ["M-007", "M-029", "M-030", "M-062", "M-015", "M-038", "M-043", "M-056"],
    "NSC-ORD": ["M-008", "M-031", "M-032", "M-061", "M-015", "M-040", "M-053", "M-055"],
    "NSC-PLAT": ["M-009", "M-001", "M-012", "M-013", "M-033", "M-034", "M-035", "M-036", "M-048", "M-060"]
}

# Named external tenant/partner collaborators per workstream (13 active external members across Meridian & PulsePay)
project_external_collaborators = {
    "NSC-CAT": ["M-016", "M-063", "M-064"],
    "NSC-SRCH": ["M-068"],
    "NSC-CART": ["M-063"],
    "NSC-CHKO": ["M-016", "M-069"],
    "NSC-PAY": ["M-017", "M-071", "M-072", "M-073", "M-074"],
    "NSC-INV": ["M-065"],
    "NSC-ORD": ["M-066", "M-067"],
    "NSC-PLAT": ["M-069", "M-074"]
}

# Former members who were historically attached to a project before offboarding
project_former_members = {
    "NSC-CAT": ["M-018"],   # Left 2026-09-15
    "NSC-SRCH": ["M-045"],  # Left 2026-08-01
    "NSC-PAY": ["M-070"],   # Left 2026-07-15 (external partner)
}

# Project assignments grant explicit membership in the matching project group ONLY to internal Northstar staff.
member_by_id = {member["member_id"]: member for member in members}
existing_group_pairs = {(item["member_id"], item["group_id"]) for item in memberships}
for project in projects:
    project_id = project["project_id"]
    group_id = project["team_group"]
    for member_id in dict.fromkeys([project["owner_id"]] + project_devs[project_id]):
        if (member_id, group_id) in existing_group_pairs:
            continue
        member = member_by_id[member_id]
        if member["org_id"] != "ORG-NSC":
            continue
        is_inactive = member["account_status"] == "inactive"
        memberships.append({
            "membership_id": f"MEMB-{member_id}-{group_id}",
            "member_id": member_id,
            "group_id": group_id,
            "status": "revoked" if is_inactive else "active",
            "valid_from": member["joined_at"],
            "valid_to": member["left_at"] if is_inactive else None,
            "membership_source": "project_assignment",
            "project_id": project_id,
            "synthetic": True
        })
        existing_group_pairs.add((member_id, group_id))

project_memberships = []
for p in projects:
    pid = p["project_id"]
    owner = p["owner_id"]
    team = project_devs[pid]
    for mid in dict.fromkeys([owner] + team):
        role = "owner" if mid == owner else ("tech_lead" if mid in ["M-003", "M-004", "M-005", "M-006", "M-007", "M-008", "M-009"] else "contributor")
        project_memberships.append({
            "membership_id": f"PM-{pid}-{mid}",
            "project_id": pid,
            "member_id": mid,
            "role": role,
            "status": "active",
            "synthetic": True
        })
    for ext_mid in project_external_collaborators.get(pid, []):
        project_memberships.append({
            "membership_id": f"PM-{pid}-{ext_mid}",
            "project_id": pid,
            "member_id": ext_mid,
            "role": "external_collaborator",
            "status": "active",
            "synthetic": True
        })
    for former_mid in project_former_members.get(pid, []):
        project_memberships.append({
            "membership_id": f"PM-{pid}-{former_mid}",
            "project_id": pid,
            "member_id": former_mid,
            "role": "former_contributor",
            "status": "revoked",
            "synthetic": True
        })

for _pm in project_memberships:
    _pid = _pm["project_id"]
    _mid = _pm["member_id"]
    _mem = member_by_id[_mid]
    _is_nsc = (_mem["org_id"] == "ORG-NSC")
    _pm["continuum_project_member_id"] = stable_id("project-member", f"{_pid}:{_mid}")
    _pm["continuum_project_id"] = stable_id("project", _pid)
    _pm["continuum_user_id"] = stable_id("user", _mid)
    _pm["is_org_manager"] = (_is_nsc and _mid in ORG_NSC_MANAGERS)
    if not _is_nsc:
        _pm["continuum_role_code"] = None
        _pm["continuum_membership_status"] = "EXCLUDED_EXTERNAL"
        _pm["continuum_import_eligible"] = False
        _pm["continuum_exclusion_reason"] = "external_counterparty_tenant"
    else:
        _pm["continuum_role_code"] = "TEAM_LEADER" if PROJECT_TEAM_LEADERS[_pid] == _mid else "MEMBER"
        _pm["continuum_membership_status"] = "REMOVED" if _pm["status"] == "revoked" else "ACTIVE"
        _pm["continuum_import_eligible"] = True
        _pm["continuum_exclusion_reason"] = None

# -------------------------------------------------------------
# 6. Jira-like Issues (2,500) (Phase 2 & Phase 4: Lifecycle, Ownership, Quality)
# -------------------------------------------------------------
issue_counts_per_project = {
    "NSC-CAT": 313,
    "NSC-SRCH": 313,
    "NSC-CART": 312,
    "NSC-CHKO": 313,
    "NSC-PAY": 313,
    "NSC-INV": 312,
    "NSC-ORD": 312,
    "NSC-PLAT": 312
}
assert sum(issue_counts_per_project.values()) == 2500

issue_raw_topics = {
    "NSC-CAT": [
        "Unique SKU enforcement per merchant in catalog database",
        "Bulk CSV catalog imports with row-level validation reporting",
        "Image URL security validator and HTTPS CDN whitelisting",
        "Category and price faceted navigation filters",
        "Scheduled price books with timezone-aware effective windows",
        "Merchant variant matrix limit specifications",
        "Product attribute group hierarchy for apparel merchandising",
        "Localized product description support for regional storefronts",
        "Catalog import worker batch memory allocation optimization",
        "Configurable product option matrix validation",
        "Soft-delete lifecycle for discontinued merchant SKUs",
        "Merchant-scoped custom attribute indexing pipelines"
    ],
    "NSC-SRCH": [
        "Relevance ranking model for exact merchant SKU queries",
        "Merchant-scoped synonym dictionary management API",
        "Facet aggregation counts after multi-select filtering",
        "P95 search latency telemetry and load optimization",
        "Zero-result fallback recommendations for misspelled queries",
        "Locale-aware tokenization and character folding rules",
        "Tenant-isolated Elasticsearch index aliases configuration",
        "Phrase matching boosts for high-converting product categories",
        "Telemetry for zero-click and low-confidence search queries",
        "Synonym deletion and rebuild cache invalidation workflow",
        "Product search indexing throughput during bulk imports",
        "Query syntax sanitization to prevent index injection"
    ],
    "NSC-CART": [
        "Guest cart merging into customer account upon login",
        "Promotion stacking hierarchy and discount evaluation engine",
        "Abandoned cart expiration workflow with automated stock release",
        "Order line total recalculation after real-time inventory adjustments",
        "Idempotent cart item updates during concurrent requests",
        "Immutable cart audit transition event logging",
        "Fixed-amount and percentage tier coupon discounts",
        "Merchant cart item maximum quantity limit constraints",
        "Cart currency conversion with cached FX exchange rates",
        "Cart coupon eligibility against customer group rules",
        "Cart session TTL extension on user checkout interaction",
        "Bundle product component price breakdown in cart session"
    ],
    "NSC-CHKO": [
        "Customer shipping address validation before tax quotation",
        "Idempotent checkout session endpoint with durable replay keys",
        "External tax service timeout handling with graceful fallback mode",
        "Fallback shipping rate computation during carrier API outages",
        "Prevention of duplicate order submission on multi-click submission",
        "Keyboard accessibility and screen reader flow in checkout UI",
        "Split-step checkout state machine with transactional checkpoints",
        "Merchant checkout configuration overrides on tenant boot",
        "Telemetry for checkout step drop-off rates across platforms",
        "Fifteen-minute checkout reservation timeout on inventory holds",
        "Merchant custom checkout field sanitization and persistence",
        "Tax exemption certificate verification for commercial accounts"
    ],
    "NSC-PAY": [
        "3D-Secure 2.0 challenge completion and return redirect handshake",
        "Payment webhook event deduplication using durable idempotency inbox",
        "Payment provider retry policy with exponential backoff and jitter",
        "Partial authorization and partial refund transaction lifecycle",
        "Payment provider failover mechanism for elevated error rates",
        "Structured dispute and chargeback evidence metadata capture",
        "PCI-DSS token storage boundaries and zero PAN persistence",
        "PulsePay settlement reconciliation reports against captured charges",
        "Circuit breaker implementation for payment gateway timeouts",
        "Webhook signature authorization header verification against tenant secrets",
        "Payment intent authorization cancellation upon checkout abandon",
        "Multi-currency payment capture with exchange settlement audit"
    ],
    "NSC-INV": [
        "Stock reservation with durable 15-minute TTL during active checkout",
        "Inventory oversell prevention during concurrent flash-sale checkouts",
        "Multi-warehouse stock transfer events with audit trails",
        "Daily merchant stock snapshot file reconciliation against live balances",
        "Automated low-stock webhook notifications to merchant ERP",
        "Backorder eligibility rules and fulfillment lead time tracking",
        "Safety stock buffers for high-velocity seasonal merchandise",
        "Atomic inventory decrement using database row locking",
        "Stock audit history for manual merchant inventory adjustments",
        "Warehouse bin location updates with pick-pack workflows",
        "Reservation release handling when checkout order is aborted",
        "Multi-location inventory allocation rules per customer zone"
    ],
    "NSC-ORD": [
        "Customer refund state machine with merchant approval gates",
        "Strict order cancellation cutoff before warehouse pack stage",
        "Logistics carrier shipment status tracking webhook events",
        "Partial fulfillment shipments across distributed warehouses",
        "Automated customer return shipping label request workflow",
        "Merchant invoice PDF generation and export retry mechanism",
        "Thirty-day return policy inspection window for Meridian pilot orders",
        "Order status change notification emails with localized templates",
        "Credit memo calculation engine for returned damaged items",
        "Order cancellation audit reasons and merchant override authorizations",
        "Merchant order re-routing to alternate fulfillment centers",
        "End-to-end fulfillment cycle time metrics for merchant SLA reporting"
    ],
    "NSC-PLAT": [
        "Tenant-scoped API authentication permissions across gateway routes",
        "Immutable administrative audit trail events in append-only log",
        "Document and resource group ACL filtering prior to vector retrieval",
        "Outbox event publishing with transactional exactly-once guarantees",
        "Checkout and payment service SLO dashboard with automated alerting",
        "Privacy-safe merchant data export complying with GDPR/CCPA",
        "Tenant database connection pool isolation and query rate limits",
        "Distributed tracing correlation IDs across all microservice requests",
        "Automated database index maintenance and vacuuming schedule",
        "Cross-tenant data leak prevention test suite on staging deployment",
        "Canary deployment rollout configuration with health error gates",
        "Secret rotation policies for third-party payment partner API keys"
    ]
}

SUMMARY_ASPECTS = [
    "API contract & schema validation",
    "PostgreSQL indexing & tenant query guard",
    "Redis distributed lock & concurrency handling",
    "Idempotent retry & dead-letter telemetry",
    "Integration test suite & staging replay",
    "Merchant admin UI state & error boundary",
    "Rate limiting & audit trail emission",
    "Backfill worker & batch memory tuning",
    "Webhook signature & payload verification",
    "Timeout fallback & circuit breaker logic",
    "Multi-tenant isolation & negative permission checks",
    "Observability spans & SLO alert thresholds",
    "Database expand-contract migration script",
    "Cache invalidation & version lineage check",
    "Load test benchmark & p95 latency profiling",
    "Edge-case race condition remediation",
    "Partner sandbox contract reconciliation",
    "Role-based access control policy enforcement",
    "Automated recovery & rollback verification",
    "Boundary value & currency minor-unit validation",
    "Event outbox deduplication & ordering",
    "Quarantine workflow for malformed inputs",
    "Storefront response serialization & pagination",
    "Zero-downtime deployment readiness gate",
    "Security header & token scope hardening",
    "Operational runbook & support diagnostics",
    "Data retention & privacy masking compliance",
    "Cross-service correlation ID propagation",
]

# Differentiated project status distributions (20-slot cycles) reflecting healthy vs At-Risk projects
PROJECT_STATUS_POOLS = {
    "NSC-CAT":  ["Done"] * 15 + ["In Progress"] * 2 + ["In Review"] * 1 + ["To Do"] * 1 + ["Blocked"] * 1,
    "NSC-CART": ["Done"] * 14 + ["In Progress"] * 2 + ["In Review"] * 2 + ["To Do"] * 1 + ["Blocked"] * 1,
    "NSC-SRCH": ["Done"] * 13 + ["In Progress"] * 3 + ["In Review"] * 2 + ["To Do"] * 1 + ["Blocked"] * 1,
    "NSC-INV":  ["Done"] * 12 + ["In Progress"] * 3 + ["In Review"] * 2 + ["To Do"] * 2 + ["Blocked"] * 1,
    "NSC-ORD":  ["Done"] * 12 + ["In Progress"] * 3 + ["In Review"] * 2 + ["To Do"] * 1 + ["Blocked"] * 2,
    "NSC-PLAT": ["Done"] * 11 + ["In Progress"] * 4 + ["In Review"] * 2 + ["To Do"] * 2 + ["Blocked"] * 1,
    "NSC-CHKO": ["Done"] * 8  + ["In Progress"] * 5 + ["In Review"] * 2 + ["To Do"] * 2 + ["Blocked"] * 3,
    "NSC-PAY":  ["Done"] * 7  + ["In Progress"] * 5 + ["In Review"] * 2 + ["To Do"] * 2 + ["Blocked"] * 4,
}

# Project overtime intensity (out of 20 issues): At-Risk projects have ~30% OT; stable projects ~7-12%
PROJECT_OT_SLOTS = {
    "NSC-CAT":  {6, 19},
    "NSC-CART": {5, 18},
    "NSC-SRCH": {4, 15},
    "NSC-INV":  {3, 14},
    "NSC-ORD":  {4, 11, 18},
    "NSC-PLAT": {2, 9, 17},
    "NSC-CHKO": {1, 4, 7, 11, 14, 18},
    "NSC-PAY":  {1, 3, 6, 9, 13, 16, 19},
}

def generate_issue_description(itype, summary, pid, assignee_name):
    """Generate grammatical, non-repetitive descriptions based on issue type and domain."""
    summary_clean = summary.strip().rstrip(".")
    if itype == "Bug":
        return f"Defect investigation: Discrepancy observed regarding {summary_clean.lower()}. Under high-concurrency staging conditions, edge-case race conditions were recorded. Acceptance Criteria: 1. Reproduce with automated test fixture. 2. Verify state machine preserves transactional boundaries. 3. Zero regressions in tenant isolation."
    elif itype == "Story":
        return f"User requirement: As a merchant administrator in {pid}, enable {summary_clean.lower()} to ensure predictable operations and tenant data safety. Acceptance Criteria: 1. API contract conforms to schema specification. 2. Staging integration suite passes. 3. Audit trail log entry is emitted upon completion."
    elif itype == "Task":
        return f"Operational task: Execute engineering milestones for {summary_clean.lower()} in compliance with Northstar platform governance. Acceptance Criteria: 1. Implementation adheres to architecture patterns. 2. Code review approved by tech lead. 3. Telemetry metrics verified on dashboard."
    else:  # Epic
        return f"Strategic initiative: Deliver core capabilities for {summary_clean.lower()} across multi-tenant milestones. Acceptance Criteria: 1. Squad deliverables approved. 2. Cross-service contracts validated. 3. Merchant pilot integration verified."

def generate_issue_comment(status, issue_key, summary, author_m, is_blocked, is_ot=False, work_mode="regular_hours"):
    """Generate deterministic, issue-specific Jira comments with varied evidence and overtime context."""
    prefix, num = issue_key.split("-", 1)
    variant = (int(num) + sum(ord(char) for char in prefix + author_m)) % 5
    subject = summary.rstrip(".")
    ot_prefix = ""
    if work_mode == "weekend_incident_ot":
        ot_prefix = "[Weekend Incident War-Room OT 17:00-22:00+07:00] "
    elif is_ot:
        ot_prefix = "[Evening Sprint Crunch OT 17:00-22:00+07:00] "
    pools = {
        "Done": [
            "Completed {subject}. The focused regression suite and tenant-scoped staging replay passed; the audit event retained merchant context.",
            "QA verified {subject} across the normal and retry paths. No duplicate side effects appeared, and the release note is attached to the change.",
            "The implementation for {subject} is merged. Contract tests, permission checks, and the pilot fixture set all passed.",
            "Acceptance is complete for {subject}; reviewers checked the failure-mode evidence and confirmed the rollback step before closing.",
            "Resolved {subject} and checked the resulting staging metrics. The expected state transition and audit trail were observed.",
        ],
        "In Progress": [
            "Working on {subject}; the main path is implemented, and I am adding coverage for retries and tenant boundaries before the staging run.",
            "The {subject} change is underway. I have a first pass in the feature branch and am tracing the remaining telemetry and error handling.",
            "Progress update for {subject}: the contract is agreed, the implementation is in review locally, and integration coverage is the next step.",
            "I am validating {subject} against the merchant pilot flow. The happy path passes; timeout and duplicate-request cases remain open.",
            "Implementation continues for {subject}. I am checking the data migration and adding a focused regression case before requesting review.",
        ],
        "In Review": [
            "Review requested for {subject}. Please focus on schema compatibility, failure-path behavior, and tenant context in the audit event.",
            "The change for {subject} is ready for squad review; the PR includes contract tests and a staging trace for the edge case.",
            "Please review {subject} for backward compatibility and retry safety. I attached the benchmark and the relevant fixture output.",
            "Submitted {subject} for review. The main tests pass, and I would like a second look at the permission boundary before merge.",
            "Review is open for {subject}; acceptance evidence covers the API response, audit record, and the failure recovery path.",
        ],
        "Blocked": [
            "Blocked on a reproducible provider response for {subject}. The sandbox trace is attached; I will rerun the idempotency check when access is restored.",
            "Work on {subject} is waiting for the upstream contract owner to confirm the retry semantics. The current behavior and impact are documented.",
            "This is blocked pending a stable integration fixture for {subject}. I have isolated the failing path and escalated the dependency to the squad lead.",
            "Cannot complete {subject} until the partner sandbox is available. No production data is involved; the next step is a replay with the provider trace.",
            "The {subject} path remains blocked by an unresolved migration dependency. I recorded the rollback condition and requested an owner and ETA.",
        ],
        "To Do": [
            "Backlog refinement for {subject}: split acceptance into the primary, retry, and tenant-isolation paths; confirm the dependency before scheduling.",
            "Before starting {subject}, we need a sample payload and a decision on the error contract. The estimate assumes both arrive this sprint.",
            "Refined {subject} with product and QA. The acceptance notes now cover expected behavior, audit evidence, and a negative permission case.",
            "Queued {subject} after confirming the owning service. Please attach the pilot fixture and final acceptance wording before development begins.",
            "{subject} is ready for planning once the open API dependency is confirmed; the proposed test cases are listed in the ticket description.",
        ],
    }
    if is_blocked or status == "Blocked":
        status = "Blocked"
    return ot_prefix + pools.get(status, pools["To Do"])[variant].format(subject=subject)

issues = []
comments = []
changelog = []

priorities_cycle = ["High", "Medium", "High", "Medium", "Highest", "Low", "Medium", "High"]
issue_types_cycle = ["Story", "Story", "Bug", "Story", "Task", "Bug", "Story", "Task"]

# Weekend incident war-room tickets (explicitly worked on Saturday evenings 17:00-22:00+07:00)
WEEKEND_INCIDENT_TICKETS = {
    "CHKO-012": date(2026, 8, 29),
    "CHKO-015": date(2026, 8, 29),
    "PAY-002":  date(2026, 9, 26),
    "PAY-003":  date(2026, 9, 26),
    "CHKO-005": date(2026, 10, 10),
    "PLAT-005": date(2026, 10, 10),
}

# Build issues deterministically across the 8 projects
for pid, total_count in issue_counts_per_project.items():
    pid_idx = PID_INDEX[pid]
    prefix = pid.replace("NSC-", "")
    topics = issue_raw_topics[pid]
    team = project_devs[pid]
    ext_collabs = project_external_collaborators.get(pid, [])
    owner = next(p["owner_id"] for p in projects if p["project_id"] == pid)
    sec_group = next(p["team_group"] for p in projects if p["project_id"] == pid)
    status_pool = PROJECT_STATUS_POOLS[pid]
    ot_slots = PROJECT_OT_SLOTS[pid]

    # Define 4 canonical Epics per project (keys 001, 011, 021, 031 except when overridden)
    epic_indices = {11, 21, 31, 41}
    epic_keys = [f"{prefix}-{idx:03d}" for idx in sorted(epic_indices)]

    for i in range(1, total_count + 1):
        key = f"{prefix}-{i:03d}"
        topic_idx = (i - 1) % len(topics)
        base_topic = topics[topic_idx]
        batch_num = ((i - 1) // len(topics)) + 1
        if batch_num == 1:
            summary = base_topic
        else:
            aspect = SUMMARY_ASPECTS[(batch_num - 2 + topic_idx * 3 + pid_idx * 5) % len(SUMMARY_ASPECTS)]
            summary = f"{base_topic} — {aspect}"

        # Specific overrides for canonical seed & test compatibility
        if key == "CAT-001":
            status = "Done"; priority = "High"; itype = "Story"; summary = "Enforce unique SKU per merchant in catalog schema"
        elif key == "CAT-002":
            status = "Done"; priority = "Medium"; itype = "Story"; summary = "Validate bulk catalog imports with error reporting"
        elif key == "CAT-003":
            status = "Done"; priority = "High"; itype = "Bug"; summary = "Reject unsafe image URLs and enforce HTTPS CDN whitelist"
        elif key == "CHKO-005":
            # Must be an active open/blocked Highest Bug so failed test FT-CHKO-007 links to an unresolved release blocker!
            status = "Blocked"; priority = "Highest"; itype = "Bug"; summary = "Prevent duplicate order creation under concurrent checkout submissions"
        elif key == "PAY-002":
            status = "Blocked"; priority = "Highest"; itype = "Bug"; summary = "Deduplicate payment webhooks using durable idempotency inbox"
        elif key in ["CHKO-045", "INV-088", "ORD-112", "PLAT-034", "PAY-015", "SRCH-042", "CART-055"]:
            status = "Blocked"; priority = "Highest"; itype = "Bug"
        elif i in epic_indices:
            itype = "Epic"
            status = "Done" if i in (11, 21) else "In Progress"
            priority = "High"
        else:
            status = status_pool[(i * 7 + pid_idx * 3) % len(status_pool)]
            priority = priorities_cycle[(i * 5 + pid_idx * 11) % len(priorities_cycle)]
            itype = issue_types_cycle[(i * 3 + pid_idx * 7) % len(issue_types_cycle)]

        # Map creation date strictly onto WORKING_DAYS (123 working days between 2026-04-16 and 2026-10-12).
        # Foundational issues 1..15 stay in April kickoff (working days 0..5: Apr 16 to Apr 23) for formal-document references.
        if i <= 15:
            w_idx = min(5, (i - 1) // 3)
        else:
            w_idx = min(TOTAL_WORKING_DAYS - 2, 6 + ((i - 16) * (TOTAL_WORKING_DAYS - 8)) // (total_count - 15))
        created_date = WORKING_DAYS[w_idx]

        # Initial sprint based on creation date
        initial_sprint_num = min(13, max(1, ((created_date - SPRINT_BASE).days // 14) + 1))
        initial_sprint_id = f"SPRINT-{prefix}-{initial_sprint_num:02d}"

        # Parent Epic linkage for Stories/Tasks/Bugs
        if itype == "Epic":
            parent_key = None
            story_pts = [13, 20, 21][(i + pid_idx) % 3]
        else:
            parent_key = epic_keys[(i + pid_idx) % len(epic_keys)]
            story_pts = [1, 2, 3, 5, 8][(i + pid_idx) % 5]

        # Assignee, Offboarding & PTO Handover Rules:
        # - M-018 (ORG-NSC, NSC-CAT) left 2026-09-15
        # - M-045 (ORG-NSC, NSC-SRCH) left 2026-08-01
        # - M-070 (ORG-PULSEPAY, NSC-PAY) left 2026-07-15
        was_reassigned = False
        former_or_prev_id = None
        reassign_reason = None
        reassign_date = None

        if key == "CAT-003":
            assignee = "M-018"
            updated_date = date(2026, 9, 10)  # Thursday working day before M-018 left on 2026-09-15
            due_date = date(2026, 9, 15)
        elif status == "Done" and (i % 19 == 0) and pid == "NSC-CAT" and created_date <= date(2026, 8, 25):
            assignee = "M-018"
            updated_date = add_working_days(created_date, 5, cap_at_today=True)
            if updated_date >= date(2026, 9, 14):
                updated_date = date(2026, 9, 11)
            due_date = add_working_days(created_date, 9, cap_at_today=False)
        elif status == "Done" and (i % 19 == 0) and pid == "NSC-SRCH" and created_date <= date(2026, 7, 15):
            assignee = "M-045"
            updated_date = add_working_days(created_date, 5, cap_at_today=True)
            if updated_date >= date(2026, 7, 31):
                updated_date = date(2026, 7, 30)
            due_date = add_working_days(created_date, 10, cap_at_today=False)
        else:
            assignee = team[(i - 1) % len(team)]
            # Offboarding or PTO reassignment on selected issues
            if pid == "NSC-CAT" and (i % 28 == 0) and created_date < date(2026, 9, 10):
                was_reassigned = True
                former_or_prev_id = "M-018"
                reassign_reason = "offboarding"
                reassign_date = max(add_working_days(created_date, 2, cap_at_today=True), date(2026, 9, 14))
            elif pid == "NSC-SRCH" and (i % 28 == 0) and created_date < date(2026, 7, 24):
                was_reassigned = True
                former_or_prev_id = "M-045"
                reassign_reason = "offboarding"
                reassign_date = max(add_working_days(created_date, 2, cap_at_today=True), date(2026, 7, 31))
            elif pid == "NSC-PAY" and (i % 35 == 0) and created_date < date(2026, 7, 10):
                was_reassigned = True
                former_or_prev_id = "M-070"
                reassign_reason = "partner_offboarding"
                reassign_date = max(add_working_days(created_date, 2, cap_at_today=True), date(2026, 7, 14))
            elif (i % 32 == 0) and status != "To Do":
                # Authentic PTO / annual leave handover between active squad members
                prev_candidate = team[(i + 2) % len(team)]
                if prev_candidate != assignee:
                    was_reassigned = True
                    former_or_prev_id = prev_candidate
                    reassign_reason = "pto_handover"
                    reassign_date = add_working_days(created_date, 2, cap_at_today=True)

            # Compute updated_date and due_date strictly on WORKING_DAYS (or weekend incident date)
            if status == "Done":
                updated_date = add_working_days(created_date, (i % 8) + 3, cap_at_today=True)
                if was_reassigned and reassign_date and updated_date <= reassign_date:
                    updated_date = add_working_days(reassign_date, 2, cap_at_today=True)
                due_date = add_working_days(created_date, (i % 10) + 6, cap_at_today=False)
            elif status == "Blocked":
                if i % 2 == 0:
                    due_date = snap_to_working_day(TODAY - timedelta(days=(i % 8) + 1), prefer_forward=False)
                else:
                    due_date = snap_future_working_day(TODAY + timedelta(days=(i % 12) + 2))
                updated_date = snap_to_working_day(max(add_working_days(created_date, 3), TODAY - timedelta(days=(i % 4))), prefer_forward=True)
            else:  # In Progress, In Review, To Do
                if i % 6 == 0 and pid in ("NSC-CHKO", "NSC-PAY"):
                    due_date = snap_to_working_day(TODAY - timedelta(days=(i % 6) + 1), prefer_forward=False)
                elif i % 11 == 0:
                    due_date = snap_to_working_day(TODAY - timedelta(days=(i % 5) + 1), prefer_forward=False)
                else:
                    due_date = snap_future_working_day(TODAY + timedelta(days=(i % 16) + 3))
                updated_date = snap_to_working_day(max(add_working_days(created_date, 2), date(2026, 9, 29) + timedelta(days=(i % 12))), prefer_forward=True)
                if updated_date < created_date:
                    updated_date = created_date

        # Check if this issue is one of the 6 Saturday incident war-room tickets
        is_weekend_incident = key in WEEKEND_INCIDENT_TICKETS
        if is_weekend_incident:
            inc_sat = WEEKEND_INCIDENT_TICKETS[key]
            if inc_sat >= created_date:
                updated_date = inc_sat
            is_overtime = True
            work_mode = "weekend_incident_ot"
            overtime_hours = round(3.5 + (i % 3) * 1.0, 1)
        else:
            # Contextual weekday overtime (17:00-22:00+07:00):
            # Triggered by project OT slot, or sprint-end crunch with High/Highest priority
            days_into_sprint = (updated_date - SPRINT_BASE).days % 14
            is_sprint_end = days_into_sprint >= 10
            if (i % 20) in ot_slots or (is_sprint_end and priority in ("Highest", "High") and (i % 4 == 0)):
                is_overtime = True
                work_mode = "evening_overtime"
                overtime_hours = round(1.5 + ((i + pid_idx) % 4) * 1.0, 1)
            else:
                is_overtime = False
                work_mode = "regular_hours"
                overtime_hours = 0.0

        # Realistic Scrum Sprint Lifecycle (computed AFTER updated_date is finalized!):
        # - Closed sprints (1..12) cannot hold unresolved open issues: any status != "Done" is in active Sprint 13.
        # - Done issues belong strictly to the sprint covering their actual completion date (updated_date).
        if status != "Done":
            sprint_num = 13
            sprint_id = f"SPRINT-{prefix}-13"
            spillover_count = max(0, 13 - initial_sprint_num)
        else:
            sprint_num = min(13, max(1, ((updated_date - SPRINT_BASE).days // 14) + 1))
            sprint_id = f"SPRINT-{prefix}-{sprint_num:02d}"
            spillover_count = max(0, sprint_num - initial_sprint_num)

        if was_reassigned and reassign_date and reassign_date > updated_date:
            reassign_date = snap_to_working_day(created_date + timedelta(days=1), prefer_forward=True)
            if reassign_date > updated_date:
                reassign_date = created_date

        assert created_date <= updated_date <= TODAY, f"Timeline inverted for {key}: {created_date} vs {updated_date}"

        # Build +07:00 timestamps ensuring created_ts < all intermediate transitions < updated_ts
        c_mn = 5 + ((i * 11 + pid_idx * 7) % 48)
        c_sc = 5 + ((i * 17 + pid_idx * 3) % 50)
        created_ts = f"{created_date.isoformat()}T08:{c_mn:02d}:{c_sc:02d}{VN_TZ}"
        updated_ts = make_human_timestamp(updated_date, i * 3 + pid_idx, is_ot=is_overtime, slot_index=5)
        if updated_date == created_date:
            updated_ts = f"{updated_date.isoformat()}T{20 if is_overtime else 16}:45:{c_sc:02d}{VN_TZ}"

        biz_hours = calc_business_hours_between(created_ts, updated_ts, overtime_hours)

        reporter = owner if (i % 2 == 0) else team[(i + 3) % len(team)]
        labels = ["synthetic", "commerce", f"sprint-{sprint_num}"]
        if status == "Blocked":
            labels.append("blocked")
        if due_date < TODAY and status != "Done":
            labels.append("overdue")
        if is_overtime:
            labels.append("overtime")
        if spillover_count > 0:
            labels.append("spillover")

        desc = generate_issue_description(itype, summary, pid, assignee)

        issue_rec = {
            "issue_id": f"ISSUE-{key}",
            "issue_key": key,
            "project_id": pid,
            "sprint_id": sprint_id,
            "initial_sprint_id": initial_sprint_id,
            "spillover_count": spillover_count,
            "parent_key": parent_key,
            "issue_type": itype,
            "summary": summary,
            "description": desc,
            "status": status,
            "priority": priority,
            "assignee_id": assignee,
            "reporter_id": reporter,
            "created_at": created_ts,
            "updated_at": updated_ts,
            "due_date": due_date.isoformat(),
            "story_points": story_pts,
            "is_overtime": is_overtime,
            "overtime_hours": overtime_hours,
            "work_mode": work_mode,
            "business_hours_elapsed": biz_hours,
            "labels": labels,
            "source_system": "Jira",
            "source_url": f"https://jira.northstar.invalid/browse/{key}",
            "security_group": sec_group,
            "synthetic": True
        }
        issues.append(issue_rec)

        # Build coherent, strictly chronological changelog events (status, assignee handovers, sprint spillover, review/QA loops)
        raw_events = []

        def Intermediate_ts(step_num, total_steps, use_ot=False):
            """Generate a strictly increasing timestamp between created_ts and updated_ts."""
            step_hours_reg = [9, 11, 13, 15, 16]
            step_hours_ot = [17, 18, 19, 20, 20]
            hr = (step_hours_ot if use_ot else step_hours_reg)[min(max(0, step_num - 1), 4)]
            mn = 10 + ((i * 3 + step_num * 11) % 45)
            sc = 5 + ((i * 7 + step_num * 13) % 50)
            if updated_date == created_date:
                return f"{created_date.isoformat()}T{hr:02d}:{mn:02d}:{sc:02d}{VN_TZ}"
            span_days = max(1, (updated_date - created_date).days)
            d_Cand = created_date + timedelta(days=max(1, (span_days * step_num) // (total_steps + 1)))
            d_work = snap_to_working_day(d_Cand, prefer_forward=True)
            max_inter_date = max(created_date, snap_to_working_day(updated_date - timedelta(days=1), prefer_forward=False))
            if d_work < created_date:
                d_work = created_date
            if d_work > max_inter_date:
                d_work = max_inter_date
            return f"{d_work.isoformat()}T{hr:02d}:{mn:02d}:{sc:02d}{VN_TZ}"

        if was_reassigned and former_or_prev_id:
            r_ts = make_human_timestamp(reassign_date, i + 19, is_ot=False, slot_index=2)
            if r_ts < created_ts:
                r_ts = created_ts
            if r_ts > updated_ts:
                r_ts = updated_ts
            raw_events.append((r_ts, "assignee", former_or_prev_id, assignee, owner))

        if spillover_count > 0:
            # Record Sprint carry-over into target sprint at target sprint kickoff morning
            target_sp_start = SPRINT_BASE + timedelta(days=(sprint_num - 1) * 14)
            sp_date = snap_to_working_day(max(created_date, target_sp_start), prefer_forward=True)
            if sp_date > updated_date:
                sp_date = updated_date
            if sp_date.weekday() >= 5:
                sp_ts = f"{sp_date.isoformat()}T17:05:{(i % 50):02d}{VN_TZ}"
            else:
                sp_ts = f"{sp_date.isoformat()}T08:00:{(i % 50):02d}{VN_TZ}"
            if sp_ts < created_ts:
                sp_ts = created_ts
            if sp_ts > updated_ts:
                sp_ts = updated_ts
            raw_events.append((sp_ts, "sprint", initial_sprint_id, sprint_id, owner))

        qa_reviewer = next((m for m in team if m in ("M-010", "M-037", "M-038", "M-039", "M-040")), "M-010")

        if status == "In Progress":
            if (i % 6 == 0) and (updated_date - created_date).days >= 3:
                # Code review bounce-back loop: To Do -> In Progress -> In Review -> In Progress
                raw_events.append((Intermediate_ts(1, 3), "status", "To Do", "In Progress", assignee))
                raw_events.append((Intermediate_ts(2, 3), "status", "In Progress", "In Review", assignee))
                raw_events.append((updated_ts, "status", "In Review", "In Progress", qa_reviewer))
            else:
                raw_events.append((updated_ts, "status", "To Do", "In Progress", assignee))
        elif status == "In Review":
            raw_events.append((Intermediate_ts(1, 2), "status", "To Do", "In Progress", assignee))
            raw_events.append((updated_ts, "status", "In Progress", "In Review", assignee))
        elif status == "Done":
            if (i % 7 == 0) and (updated_date - created_date).days >= 5:
                # Code review rejection & fix loop before Done
                raw_events.append((Intermediate_ts(1, 5), "status", "To Do", "In Progress", assignee))
                raw_events.append((Intermediate_ts(2, 5), "status", "In Progress", "In Review", assignee))
                raw_events.append((Intermediate_ts(3, 5), "status", "In Review", "In Progress", owner))
                raw_events.append((Intermediate_ts(4, 5, use_ot=is_overtime), "status", "In Progress", "In Review", assignee))
                raw_events.append((updated_ts, "status", "In Review", "Done", qa_reviewer))
            elif (i % 11 == 0) and (updated_date - created_date).days >= 5:
                # Unblocked lifecycle: To Do -> In Progress -> Blocked -> In Progress -> In Review -> Done
                raw_events.append((Intermediate_ts(1, 5), "status", "To Do", "In Progress", assignee))
                raw_events.append((Intermediate_ts(2, 5), "status", "In Progress", "Blocked", assignee))
                raw_events.append((Intermediate_ts(3, 5), "status", "Blocked", "In Progress", owner))
                raw_events.append((Intermediate_ts(4, 5, use_ot=is_overtime), "status", "In Progress", "In Review", assignee))
                raw_events.append((updated_ts, "status", "In Review", "Done", qa_reviewer))
            else:
                raw_events.append((Intermediate_ts(1, 3), "status", "To Do", "In Progress", assignee))
                raw_events.append((Intermediate_ts(2, 3, use_ot=is_overtime), "status", "In Progress", "In Review", assignee))
                raw_events.append((updated_ts, "status", "In Review", "Done", qa_reviewer if i % 2 == 0 else assignee))
        elif status == "Blocked":
            raw_events.append((Intermediate_ts(1, 2), "status", "To Do", "In Progress", assignee))
            raw_events.append((updated_ts, "status", "In Progress", "Blocked", assignee))

        # Sort non-status events alongside status events while preserving status transition sequence
        status_events = [ev for ev in raw_events if ev[1] == "status"]
        other_events = sorted([ev for ev in raw_events if ev[1] != "status"], key=lambda x: x[0])

        # Ensure status_events timestamps are strictly non-decreasing
        fixed_status_events = []
        last_ts = created_ts
        for idx_ev, (ev_ts, fld, f_v, t_v, act) in enumerate(status_events):
            if ev_ts < last_ts:
                ev_ts = last_ts
            if ev_ts > updated_ts:
                ev_ts = updated_ts
            fixed_status_events.append((ev_ts, idx_ev + 10, fld, f_v, t_v, act))
            last_ts = ev_ts

        fixed_other_events = []
        for idx_ev, (ev_ts, fld, f_v, t_v, act) in enumerate(other_events):
            if ev_ts < created_ts:
                ev_ts = created_ts
            if ev_ts > updated_ts:
                ev_ts = updated_ts
            fixed_other_events.append((ev_ts, idx_ev, fld, f_v, t_v, act))

        combined_events = sorted(fixed_other_events + fixed_status_events, key=lambda x: (x[0], x[1]))
        for seq_num, (ev_ts, _, fld, f_v, t_v, act) in enumerate(combined_events, 1):
            ev_hr = int(ev_ts[11:13])
            ev_is_ot = ev_hr >= 17
            changelog.append({
                "history_id": f"HIST-{key}-{seq_num:02d}",
                "issue_key": key,
                "field": fld,
                "from_value": f_v,
                "to_value": t_v,
                "changed_by": act,
                "changed_at": ev_ts,
                "is_overtime": ev_is_ot,
                "work_mode": work_mode if ev_is_ot else "regular_hours"
            })

        # Primary human comment on every issue
        comment_body = generate_issue_comment(
            status, key, summary, assignee, status == "Blocked",
            is_ot=is_overtime, work_mode=work_mode
        )
        comments.append({
            "comment_id": f"COMMENT-{key}-01",
            "issue_key": key,
            "author_id": assignee if status == "Done" else reporter,
            "actor_type": "human",
            "bot_id": None,
            "created_at": updated_ts,
            "is_overtime": is_overtime,
            "work_mode": work_mode,
            "body": comment_body,
            "visibility_group": sec_group
        })

        # Multi-turn follow-up comments:
        # 1) Offboarding / PTO handover note
        if was_reassigned and former_or_prev_id:
            if reassign_reason in ("offboarding", "partner_offboarding"):
                handover_text = f"Handover note for {key} ({summary}): Reassigned from {former_or_prev_id} to {assignee} prior to offboarding cutoff. Active credentials and group memberships for {former_or_prev_id} are scheduled for revocation; in-flight branch and staging fixtures transferred."
            else:
                handover_text = f"PTO handover note for {key} ({summary}): {former_or_prev_id} is on approved 3-day annual leave (PTO); {assignee} is taking over active sprint delivery and PR review follow-up."
            comments.append({
                "comment_id": f"COMMENT-{key}-02",
                "issue_key": key,
                "author_id": owner,
                "actor_type": "human",
                "bot_id": None,
                "created_at": r_ts,
                "is_overtime": False,
                "work_mode": "regular_hours",
                "body": handover_text,
                "visibility_group": sec_group
            })
        # 2) External collaborator UAT / Partner integration comment (gives all 13 active external members authentic activity!)
        elif ext_collabs and (i % 14 == 0):
            ext_author = ext_collabs[(i // 14) % len(ext_collabs)]
            ext_org = member_by_id[ext_author]["org_id"]
            vis_grp = "GRP-MERIDIAN" if ext_org == "ORG-MERIDIAN" else "GRP-PULSEPAY"
            ext_ts = Intermediate_ts(1, 2, use_ot=False)
            ext_body = (
                f"Partner/Tenant verification on {key} ({summary}): Validated tenant-scoped contract behavior in sandbox with {ext_author} ({ext_org}). Confirmed zero cross-tenant data exposure and expected error code alignment."
            )
            comments.append({
                "comment_id": f"COMMENT-{key}-02",
                "issue_key": key,
                "author_id": ext_author,
                "actor_type": "human",
                "bot_id": None,
                "created_at": ext_ts,
                "is_overtime": False,
                "work_mode": "regular_hours",
                "body": ext_body,
                "visibility_group": vis_grp
            })
        # 3) Automated 24/7 Bot telemetry comment (runs at 02:00 / 03:30 / weekends / holidays)
        elif i % 16 == 0:
            if pid == "NSC-CAT":
                bot = SYSTEM_BOTS[0]  # BOT-SFTP-SYNC at 02:00:00+07:00
                bot_ts = f"{updated_date.isoformat()}T02:00:{(i % 50) + 5:02d}{VN_TZ}"
                bot_body = f"[Automated Nightly Batch — {bot['bot_id']}] Executed 02:00+07:00 SFTP catalog delta check for {key} ({summary}). Processed 2,000 synthetic rows; schema checksum verified."
            elif pid == "NSC-INV":
                bot = SYSTEM_BOTS[1]  # BOT-INV-EXPIRY at 03:30:00+07:00
                bot_ts = f"{updated_date.isoformat()}T03:30:{(i % 50) + 5:02d}{VN_TZ}"
                bot_body = f"[Automated Lease Sweeper — {bot['bot_id']}] Executed 03:30+07:00 TTL reservation sweep for {key} ({summary}). Released expired holds idempotently with zero negative ATP."
            elif status == "Blocked" or priority == "Highest":
                bot = SYSTEM_BOTS[3]  # BOT-ALERT-MANAGER
                bot_ts = f"{updated_date.isoformat()}T23:15:{(i % 50) + 5:02d}{VN_TZ}"
                bot_body = f"[Automated SLO Alert — {bot['bot_id']}] Threshold check triggered for {key} ({summary}) in staging-sim. Paged on-call owner {assignee} with correlation trace."
            else:
                bot = SYSTEM_BOTS[2]  # BOT-CI-RUNNER
                bot_ts = f"{updated_date.isoformat()}T01:15:{(i % 50) + 5:02d}{VN_TZ}"
                bot_body = f"[Automated CI Pipeline — {bot['bot_id']}] Nightly regression and tenant-isolation matrix completed for {key} ({summary}) on build commerce-demo-1.0.0-rc3."
            comments.append({
                "comment_id": f"COMMENT-{key}-02",
                "issue_key": key,
                "author_id": owner,
                "actor_type": "system_bot",
                "bot_id": bot["bot_id"],
                "created_at": bot_ts,
                "is_overtime": False,
                "work_mode": "automated_bot",
                "body": bot_body,
                "visibility_group": sec_group
            })

assert len(issues) == 2500
print(f"Generated {len(issues)} issues, {len(changelog)} changelog transitions, and {len(comments)} comments with Vietnam (+07:00) working hours & OT.")

# -------------------------------------------------------------
# 7. Formal Standalone Documents (10 DOCX + 12 Markdown) & Fixtures
# -------------------------------------------------------------
docx_specs = [
    {
        "id": "DOC-ARCH-PLAT-001", "file": "Platform_Architecture_Overview.docx",
        "title": "Commerce Platform Architecture Overview", "project": "NSC-PLAT",
        "owner": "M-009", "date": "2026-08-28", "version": "2.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["PLAT-001", "PLAT-004"],
        "summary": "Service boundaries, multi-tenant database isolation, and asynchronous event bus architecture for the fictional commerce platform.",
        "sections": [
            ("System Context", [
                "Storefront and merchant administration surfaces access the Commerce API Gateway, which resolves tenant context before delegating to downstream services.",
                "The fictional stack utilizes modular Laravel domain packages, Vue.js single-page administration interfaces, Redis queue workers, and PostgreSQL schemas."
            ]),
            ("Service Boundaries", [
                "Catalog Service owns product variants, merchandising taxonomies, and price books scoped strictly by merchant ID.",
                "Search & Discovery executes tenant-isolated queries against Elasticsearch clusters, applying merchant access filters prior to text ranking.",
                "Checkout Service coordinates cart conversions, tax computation, stock reservations, and payment sessions with idempotent guarantees.",
                "Orders Service encapsulates state machines for authorizations, captures, shipments, cancellations, and return merchandise authorizations."
            ]),
            ("Core Architecture Invariants", [
                "All mutating external HTTP requests must include a durable Idempotency-Key retained for at least 72 hours.",
                "Event consumers must deduplicate messages using durable provider event inbox tables with unique constraints.",
                "Direct cross-tenant database joins or queries without an explicit tenant_id filter are strictly forbidden by gateway middleware."
            ])
        ],
        "table": [
            ["Service Domain", "Primary Entity", "Isolation Mechanism", "Audit Requirement"],
            ["Catalog", "Products & Variants", "Tenant-scoped SKU & Attribute Groups", "Full change history"],
            ["Checkout", "Checkout Sessions", "Durable idempotency key (72h TTL)", "Session state transitions"],
            ["Payments", "Payment Intents & Webhooks", "Durable inbox deduplication", "Raw payload & response hash"],
            ["Orders", "Orders & Returns", "Cryptographic state transition chain", "Financial audit ledger"],
            ["Platform", "Tenants & Access Groups", "Row-level tenant isolation middleware", "Security access log"]
        ]
    },
    {
        "id": "DOC-CHKO-API-002", "file": "Checkout_API_Contract.docx",
        "title": "Checkout API Contract", "project": "NSC-CHKO",
        "owner": "M-005", "date": "2026-09-11", "version": "2.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-CHECKOUT", "GRP-MERIDIAN"], "issues": ["CHKO-002", "CHKO-003", "CHKO-005"],
        "summary": "Contract specification for checkout sessions, tax quotation, and idempotent order placement.",
        "sections": [
            ("Request Conventions", [
                "All endpoints require merchant context headers ('X-Merchant-ID') and standard correlation identifiers ('X-Correlation-ID').",
                "Monetary amounts are represented as integer minor currency units (e.g., cents) alongside ISO 4217 currency strings.",
                "Unrecognized merchant context returns HTTP 403 Forbidden; malformed payload schemas return HTTP 422 Unprocessable Entity."
            ]),
            ("Checkout Session Lifecycle", [
                "POST /api/v1/checkout/sessions creates or retrieves a checkout session given an active cart ID and customer shipping address.",
                "Clients must supply an 'Idempotency-Key' header. Submitting the identical key and payload returns the original session.",
                "Submitting the identical key with a mutated payload returns HTTP 409 IDEMPOTENCY_CONFLICT with structured error details."
            ]),
            ("Order Submission & Provider Handshake", [
                "POST /api/v1/checkout/sessions/{id}/orders commits stock reservation, authorizes payment with PulsePay, and spawns the order record.",
                "In case of upstream payment provider timeout, the endpoint returns HTTP 202 Accepted with a pending reconciliation reference.",
                "Clients must NOT spawn a new checkout session upon timeout, but poll the reconciliation endpoint using exponential backoff."
            ])
        ],
        "table": [
            ["Endpoint Method", "URI Pattern", "Success Code", "Key Error Conditions"],
            ["POST", "/api/v1/checkout/sessions", "201 Created", "409 Conflict, 422 Validation Error"],
            ["GET", "/api/v1/checkout/sessions/{id}", "200 OK", "404 Not Found, 410 Expired"],
            ["POST", "/api/v1/checkout/sessions/{id}/orders", "201 / 202 Pending", "409 Double Submission, 503 Gateway Timeout"],
            ["GET", "/api/v1/orders/{id}", "200 OK", "403 Unauthorized Tenant, 404 Missing"]
        ]
    },
    {
        "id": "DOC-QA-CHECKOUT-017", "file": "Checkout_Order_Regression_Test_Plan.docx",
        "title": "Checkout and Order Regression Test Plan", "project": "NSC-CHKO",
        "owner": "M-010", "date": "2026-10-01", "version": "1.4", "status": "In Review",
        "class": "Internal", "groups": ["GRP-CHECKOUT"], "issues": ["CHKO-002", "PAY-002", "ORD-001"],
        "summary": "Formal test suites and quality gates governing checkout session orchestration, payment callbacks, and order states.",
        "sections": [
            ("Scope & Coverage", [
                "Covers automated end-to-end regression suites across checkout sessions, PulsePay webhooks, inventory holds, and order returns.",
                "Tests execute against simulated multi-tenant fixtures representing Meridian Outfitters and synthetic benchmark test stores."
            ]),
            ("Critical Acceptance Scenarios", [
                "Duplicate Request Replay: Submit identical checkout creation requests within 72 hours; assert exactly one order entity is created.",
                "Webhook Crash Replay: Simulate server crash immediately after payment webhook ingestion; assert no duplicate capture or fulfillment event.",
                "Cross-Tenant Boundary: Attempt to access Meridian order records using another merchant credential; assert strict HTTP 403 response.",
                "Partial Refund Boundary: Issue consecutive line-item refunds; assert total refunded minor units never exceed initial authorization capture."
            ]),
            ("Exit Criteria for Release", [
                "Zero open P0 or P1 severity defects in payment orchestration or order lifecycle state machines.",
                "100% pass rate on multi-tenant access control and cross-tenant data isolation security matrices."
            ])
        ],
        "table": [
            ["Test Case ID", "Scenario Description", "Expected Invariant", "Severity"],
            ["TC-CHKO-001", "Concurrent checkout button clicks", "Single order, idempotent response", "P0"],
            ["TC-PAY-004", "Duplicate webhook delivery from PulsePay", "Deduplicated in inbox, zero re-capture", "P0"],
            ["TC-SEC-012", "Cross-tenant order retrieval attempt", "Strict HTTP 403 Forbidden", "P0"],
            ["TC-ORD-008", "Partial refund amount exceeding total", "HTTP 422 rejected, zero state mutation", "P1"]
        ]
    },
    {
        "id": "DOC-SEC-CLASS-002", "file": "Security_Data_Classification_and_Access.docx",
        "title": "Security Data Classification and Access Standard", "project": "NSC-PLAT",
        "owner": "M-012", "date": "2026-09-04", "version": "2.1", "status": "Approved",
        "class": "Restricted", "groups": ["GRP-SECURITY", "GRP-LEADERS"], "issues": ["PLAT-001", "PLAT-003"],
        "summary": "Enterprise data classification tiers, role-based access rules, and search index filtering standards.",
        "sections": [
            ("Data Classification Levels", [
                "Level 1 - Public: Approved public marketing documentation, catalog specs, and public API reference.",
                "Level 2 - Internal: Standard operational documentation, sprint plans, and internal engineering designs (accessible to GRP-ALL-STAFF).",
                "Level 3 - Restricted: Security assessments, incident root-cause analyses, payment architecture, and vulnerability reports.",
                "Level 4 - Customer Restricted: Merchant export datasets and tenant configuration accessible strictly to authorized merchant personnel."
            ]),
            ("Search & Vector Retrieval ACL Invariants", [
                "Access control lists (ACL) must be evaluated as a pre-filter before vector distance calculation and snippet extraction.",
                "Under no circumstances may a search response expose document titles, summaries, or metadata for records the principal cannot access.",
                "Documents with missing or unparseable ACL metadata must be quarantined immediately and excluded from query indexes."
            ]),
            ("Offboarding & Revocation Lifecycle", [
                "When a team member transitions to inactive status, all group memberships and active authentication tokens are revoked instantly.",
                "Historical contributions (authorship, Jira changelogs) remain preserved for audit integrity, but current data access is denied."
            ])
        ],
        "table": [
            ["Data Category", "Classification Tier", "Authorized Access Groups", "Quarantine on Missing ACL"],
            ["Product Requirements", "Internal", "GRP-ALL-STAFF, Project Squad", "Yes"],
            ["Security Audits & RCAs", "Restricted", "GRP-SECURITY, GRP-LEADERS", "Yes"],
            ["Payment Gateway Credentials", "Restricted", "GRP-CHECKOUT, GRP-SECURITY", "Yes"],
            ["Merchant Private Exports", "Customer Restricted", "GRP-MERIDIAN, GRP-SUPPORT", "Yes"]
        ]
    },
    {
        "id": "DOC-PAY-RCA-006", "file": "Payment_Webhook_Duplicate_Incident_RCA.docx",
        "title": "Incident RCA: Duplicate Payment Webhook Processing", "project": "NSC-PAY",
        "owner": "M-013", "date": "2026-09-24", "version": "1.0", "status": "Approved",
        "class": "Restricted", "groups": ["GRP-CHECKOUT", "GRP-SECURITY"], "issues": ["PAY-002", "PAY-003"],
        "summary": "Root cause analysis of the staging duplicate payment webhook processing incident on 22 September 2026.",
        "sections": [
            ("Incident Summary & Blast Radius", [
                "On 22 September 2026 at 09:14 UTC, a network blip caused PulsePay to retransmit event 'EVT-SYN-1001' (payment.succeeded).",
                "A worker restart occurred between order state transition and event inbox acknowledgement, causing a duplicate fulfillment dispatch in staging.",
                "Zero customer financial impact; containment was achieved in staging before production rollout."
            ]),
            ("Root Cause Investigation", [
                "The payment consumer executed business side effects (order paid event emission) before committing the durable provider event ID.",
                "The consumer lacked a transactional outbox and unique database constraint across (merchant_id, provider_event_id)."
            ]),
            ("Remediation Actions", [
                "Implemented database unique constraint on payment_event_inbox(merchant_id, provider_event_id).",
                "Refactored consumer to commit inbox insertion and state change in a single atomic database transaction.",
                "Added crash simulation tests to the continuous integration pipeline to prevent regressions."
            ])
        ],
        "table": [
            ["Action Item", "Owner", "Target Date", "Verification Proof"],
            ["Inbox Unique Constraint", "Noah Kim (M-006)", "2026-10-14", "Migration migration_pay_inbox_idx validated"],
            ["Crash Replay Test Suite", "Owen Garcia (M-010)", "2026-10-15", "Automated CI test run attached to PAY-002"],
            ["Reconciliation Dashboard", "Amara Okafor (M-013)", "2026-10-30", "Grafana duplicate rejection metric active"]
        ]
    },
    {
        "id": "DOC-REL-RUN-009", "file": "Commerce_Release_and_Rollback_Runbook.docx",
        "title": "Commerce Release and Rollback Runbook", "project": "NSC-PLAT",
        "owner": "M-013", "date": "2026-10-02", "version": "1.2", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["PLAT-005", "CHKO-005", "PAY-002"],
        "summary": "Standard operating procedure for staged rollout, canary verification, and emergency rollback of commerce services.",
        "sections": [
            ("Pre-Deployment Verification Checklist", [
                "Verify all P0/P1 issues for the release milestone are resolved or hold an approved executive exception.",
                "Verify automated smoke tests across checkout, payment idempotency, and tenant access control on staging.",
                "Ensure designated on-call SRE and squad leads are present in release bridge."
            ]),
            ("Canary Rollout Progression", [
                "Stage 1: Internal synthetic test merchants (0% live customer traffic) for 30 minutes observation.",
                "Stage 2: Meridian Outfitters pilot tenant at 5% traffic allocation, expanding to 25%, 50%, and 100% over 2 hours.",
                "Continuously monitor p95 latency, 5xx error rate, and payment pending queue age."
            ]),
            ("Rollback Triggers & Execution", [
                "Trigger 1: Checkout 5xx rate exceeds 1.5% over a 5-minute rolling window.",
                "Trigger 2: Any duplicate payment capture or order creation anomaly detected.",
                "Trigger 3: Confirmed cross-tenant data disclosure or tenant isolation breach.",
                "Execution: Toggle feature flag 'ff_checkout_v2' to false immediately, then revert deployment container tag."
            ])
        ],
        "table": [
            ["Metric Name", "Warning Threshold", "Critical Rollback Threshold", "Action"],
            ["Checkout HTTP 5xx Rate", "> 0.5%", "> 1.5% for 5 min", "Disable feature flag, page SRE"],
            ["Payment Pending Age", "> 5 minutes", "> 15 minutes", "Halt canary, trigger reconciliation"],
            ["Database Deadlock Rate", "> 2 / min", "> 10 / min", "Roll back migration transaction"],
            ["Tenant Isolation Violation", "0 detected", ">= 1 confirmed event", "Immediate emergency rollback"]
        ]
    },
    {
        "id": "DOC-INV-STD-003", "file": "Inventory_Reservation_and_Safety_Stock_Standard.docx",
        "title": "Inventory Reservation and Safety Stock Standard", "project": "NSC-INV",
        "owner": "M-007", "date": "2026-07-14", "version": "1.1", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["INV-001", "INV-002"],
        "summary": "Operational standard for real-time inventory reservations, concurrency locks, and safety stock thresholds.",
        "sections": [
            ("Stock Hold Mechanics", [
                "Inventory reservation is initiated at the checkout payment step with a strict 15-minute time-to-live (TTL).",
                "If the checkout session expires or payment fails, an automated queue worker releases the reservation back to available stock.",
                "Reservations utilize Redis atomic locks combined with PostgreSQL SELECT ... FOR UPDATE to prevent race conditions."
            ]),
            ("Safety Stock Rules", [
                "Merchants can configure minimum safety buffers per SKU category to protect against warehouse inventory discrepancies.",
                "Available to promise (ATP) is calculated as: ATP = Physical On-Hand - Allocated Reserves - Safety Buffer."
            ])
        ],
        "table": [
            ["Category", "Default Safety Stock", "Reservation TTL", "Oversell Action"],
            ["High Velocity Apparel", "5 units", "15 minutes", "Hard reject at checkout"],
            ["Standard Catalog Items", "2 units", "15 minutes", "Hard reject at checkout"],
            ["Backorder Eligible", "0 units", "30 minutes", "Accept with delayed shipping notice"]
        ]
    },
    {
        "id": "DOC-ORD-SOP-004", "file": "Customer_Order_Lifecycle_and_Fulfillment_SOP.docx",
        "title": "Customer Order Lifecycle and Fulfillment SOP", "project": "NSC-ORD",
        "owner": "M-008", "date": "2026-08-11", "version": "2.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF", "GRP-MERIDIAN"], "issues": ["ORD-001", "ORD-002"],
        "summary": "Standard operating procedure for order state transitions, split shipments, and carrier tracking integration.",
        "sections": [
            ("Order Lifecycle States", [
                "State progression: PENDING -> AUTHORIZED -> PROCESSING -> PACKED -> SHIPPED -> DELIVERED.",
                "Cancellation is permitted only while the order remains in PENDING, AUTHORIZED, or PROCESSING state.",
                "Once an order transitions to PACKED, cancellation is locked and the customer must utilize the standard return RMA flow."
            ]),
            ("Carrier Integration & Tracking", [
                "Tracking numbers are ingested via webhook and published to merchant admin and customer email notifications within 5 minutes.",
                "Partial shipments generate distinct fulfillment sub-records with item-level tracking references."
            ])
        ],
        "table": [
            ["State", "Allowed Next States", "Customer Cancellation Permitted", "Inventory Impact"],
            ["AUTHORIZED", "PROCESSING, CANCELLED", "Yes (full automated refund)", "Reserved"],
            ["PROCESSING", "PACKED, CANCELLED", "Yes (manual review required)", "Reserved"],
            ["PACKED", "SHIPPED", "No (return request required)", "Deducted"],
            ["SHIPPED", "DELIVERED, RETURNED", "No", "Deducted"]
        ]
    },
    {
        "id": "DOC-CART-SPEC-005", "file": "Cart_Promotion_Rules_and_Coupon_Engine_Spec.docx",
        "title": "Cart Promotion Rules and Coupon Engine Spec", "project": "NSC-CART",
        "owner": "M-005", "date": "2026-06-25", "version": "1.3", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["CART-001", "CART-002"],
        "summary": "Specification for cart pricing calculations, promotion hierarchy, and coupon code stacking limitations.",
        "sections": [
            ("Promotion Evaluation Priority", [
                "Promotions evaluate in strict order: Catalog Price Rules -> Item Tier Discounts -> Cart Order Coupons -> Free Shipping.",
                "By default, coupon codes do not stack unless explicitly configured with the 'allow_stacking' flag by the merchant."
            ]),
            ("Cart Expiration & Cleanup", [
                "Anonymous carts expire after 7 days of inactivity; authenticated user carts persist for 30 days.",
                "Expired carts automatically surrender any temporary promotional vouchers and reserved coupon redemption counts."
            ])
        ],
        "table": [
            ["Promotion Type", "Evaluation Order", "Stackable by Default", "Calculation Target"],
            ["Catalog Rule", "1", "Yes", "Line item base price"],
            ["Item Quantity Tier", "2", "No", "Eligible item subtotal"],
            ["Cart Coupon Code", "3", "No (exclusive)", "Order aggregate subtotal"],
            ["Shipping Discount", "4", "Yes", "Shipping fee quote"]
        ]
    },
    {
        "id": "DOC-DATA-DICT-008", "file": "Data_Pipeline_and_Analytics_Data_Dictionary.docx",
        "title": "Data Pipeline and Analytics Data Dictionary", "project": "NSC-PLAT",
        "owner": "M-011", "date": "2026-07-29", "version": "1.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-DATA", "GRP-ALL-STAFF"], "issues": ["PLAT-006", "PLAT-008"],
        "summary": "Comprehensive schema definitions and metrics formulas for the merchant business intelligence and analytics pipelines.",
        "sections": [
            ("Core Metrics Formulas", [
                "Gross Merchandise Value (GMV): Sum of all captured order totals excluding refunded or voided transactions.",
                "Checkout Conversion Rate: Total Completed Orders divided by Total Checkout Sessions Created in the observation window.",
                "Average Order Value (AOV): Total GMV divided by Total Completed Order Count."
            ]),
            ("Data Privacy & Anonymization", [
                "All customer personal data (names, physical addresses, emails) are masked using cryptographic salt hashes in analytics views.",
                "Merchant queries are strictly scoped by tenant identifier in analytics views."
            ])
        ],
        "table": [
            ["Table Name", "Grain", "Key Fields", "Retention Period"],
            ["fact_orders", "One row per order", "order_id, merchant_id, gmv_cents, status", "7 years (regulatory)"],
            ["fact_checkout_funnel", "One row per session step", "session_id, merchant_id, step_name, drop_off", "90 days"],
            ["dim_merchants", "One row per merchant", "merchant_id, name, tier, onboarded_date", "Indefinite"],
            ["fact_payment_events", "One row per gateway event", "event_id, provider_ref, amount, success", "3 years"]
        ]
    }
]

# Phase 3: Explicit Organization-level Modeling (project_id: null, organization_id: "ORG-NSC", scope: "organization")
# Resolving INT-001 by mapping directly to canonical issue CAT-008!
md_specs = [
    {
        "id": "DOC-ORG-CHARTER-001", "file": "Northstar_Company_and_Product_Charter.md",
        "title": "Northstar Company and Product Charter", "project_id": None, "org_id": "ORG-NSC", "scope": "organization",
        "owner": "M-001", "date": "2026-04-16", "version": "1.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["CAT-001", "CHKO-002"],
        "summary": "Company context, product mission, pilot customer scope, and architectural principles.",
        "sections": [
            ("Mission & Strategic Vision", "Northstar Commerce Systems builds a high-reliability multi-tenant commerce engine tailored for mid-market merchants. Meridian Outfitters is our inaugural pilot merchant; PulsePay Network is our payment integration partner. Domain inspiration is derived from open-source ecommerce concepts (Bagisto Laravel/Vue architecture), but our codebase is fully proprietary and synthetic."),
            ("Scope of Initial Milestone", "The first operational release encompasses product catalog and merchandising, multi-locale faceted search, cart calculations, checkout orchestration, payment webhook reconciliation, inventory reservation holds, order lifecycle workflows, and merchant support operations."),
            ("Success Measures & SLAs", "Targeting 99.9% checkout uptime, search p95 latency under 300ms, zero duplicate captures during network failures, and validated ingestion of 5,000 SKUs."),
            ("Operating Principles", "Zero secrets in repositories, auditable state machine transitions, idempotent writes for all external APIs, least-privilege access control, and strictly synthetic demo data.")
        ]
    },
    {
        "id": "DOC-CAT-PRD-004", "file": "Catalog_Merchandising_PRD_v4.md",
        "title": "Catalog and Merchandising Requirements", "project_id": "NSC-CAT", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-002", "date": "2026-09-22", "version": "4.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-CATALOG"], "issues": ["CAT-001", "CAT-002", "CAT-004"],
        "summary": "Product requirements for products, variants, bulk catalog imports, price books, and facet taxonomies.",
        "sections": [
            ("Problem Statement", "Meridian currently manages complex apparel data in external spreadsheets. The pilot requires predictable CSV imports with row-level validation errors prior to records becoming searchable."),
            ("Product Data Model", "A parent product contains sellable variants. SKU is strictly unique per merchant. Archived SKUs remain reserved indefinitely for financial and audit traceability."),
            ("Import Pipeline Behavior", "CSV uploads require pre-import validation. Mandatory fields: merchant_sku, product_name, currency, category, and price. Invalid rows generate error codes without rejecting valid rows."),
            ("Acceptance Criteria", "Enforce unique merchant SKU; validate HTTPS image URLs; store timestamps in UTC; provide downloadable error reports."),
            ("Unresolved & Out of Scope", "Automated multi-lingual machine translation of catalog copy is NOT approved for v1. Search synonym dictionaries must not alter catalog source text.")
        ]
    },
    {
        "id": "DOC-SRCH-STRATEGY-003", "file": "Search_Relevance_Strategy_v3.md",
        "title": "Search Relevance and Discovery Strategy", "project_id": "NSC-SRCH", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-004", "date": "2026-09-18", "version": "3.0", "status": "In Review",
        "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["SRCH-001", "SRCH-002"],
        "summary": "Search ranking models, merchant-scoped synonym expansion, relevance benchmarks, and latency targets.",
        "sections": [
            ("Ranking Model Hierarchy", "Exact SKU matches and exact product title matches receive highest ranking boost, followed by fuzzy title and category matching. Inventory availability acts as a hard filter."),
            ("Synonym Dictionary Management", "Each merchant maintains a versioned synonym dictionary. Synonym expansions operate within tenant boundaries and must never bleed across merchants."),
            ("Offline Benchmark Evaluation", "Offline test harness runs 120 synthetic queries measuring nDCG@10, zero-result rate, and p95 query latency across product categories."),
            ("Performance Target", "P95 search response latency must remain strictly below 300ms under 100 queries per second for an index of 50,000 SKUs."),
            ("Privacy & Personalization Boundary", "User profiling or tracking across search queries is not authorized for the pilot release; model versioning is recorded per request.")
        ]
    },
    {
        "id": "DOC-PAY-ADR-001", "file": "Payment_Orchestration_ADR_v1_SUPERSEDED.md",
        "title": "ADR-001: Initial Payment Orchestration (SUPERSEDED)", "project_id": "NSC-PAY", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-018", "date": "2026-06-02", "version": "1.0", "status": "Superseded",
        "class": "Restricted", "groups": ["GRP-PAYMENT"], "issues": ["PAY-001", "PAY-002"],
        "summary": "Historic architectural decision for payment orchestration. Retained to evaluate stale-version search suppression and conflict tests.",
        "sections": [
            ("Decision (Superseded)", "Retain idempotency keys for 12 hours. Retry payment provider timeouts up to 3 times without jitter. Accept refund requests within 14 calendar days of shipment."),
            ("Historical Context", "The early prototype used short-lived Redis keys and did not implement durable inbox deduplication or delayed webhook replay handling."),
            ("Superseded Notice", "SUPERSEDED by DOC-PAY-ADR-003 on 2026-08-19. Do not treat this document as active architectural guidance.")
        ]
    },
    {
        "id": "DOC-PAY-ADR-003", "file": "Payment_Orchestration_ADR_v3.md",
        "title": "ADR-003: Payment Orchestration and Idempotency", "project_id": "NSC-PAY", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-006", "date": "2026-08-19", "version": "3.0", "status": "Approved",
        "class": "Restricted", "groups": ["GRP-PAYMENT", "GRP-PULSEPAY"], "issues": ["PAY-001", "PAY-002", "PAY-003"],
        "summary": "Active architectural decision governing payment idempotency, provider retries, webhook inbox deduplication, and PCI boundaries.",
        "sections": [
            ("Architectural Decision", "Persist merchant-scoped idempotency keys in PostgreSQL for at least 72 hours. An identical key with an identical payload hash returns the original cached response. A matching key with a differing payload returns HTTP 409 Conflict."),
            ("Provider Retry Policy", "Retry transient network connectivity errors and HTTP 5xx responses using exponential backoff with full jitter. Maximum 5 retry attempts spanning 20 minutes. Hard payment declines (HTTP 4xx) must never be retried."),
            ("Webhook Deduplication Protocol", "Upon receipt of a PulsePay webhook, verify HMAC-SHA256 signature, insert (merchant_id, provider_event_id) into a unique inbox table within a database transaction, then apply state transitions. Replays are acknowledged with HTTP 200 without executing side effects."),
            ("Security & PCI Invariants", "Only provider payment tokens, authorization codes, and minimal transaction metadata are persisted. Storing credit card PAN or CVV is strictly prohibited. Refund policies adhere to DOC-ORD-POL-005.")
        ]
    },
    {
        "id": "DOC-ORD-POL-005", "file": "Refund_and_Cancellation_Policy_v5.md",
        "title": "Refund and Cancellation Policy", "project_id": "NSC-ORD", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-008", "date": "2026-09-03", "version": "5.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF", "GRP-MERIDIAN"], "issues": ["ORD-001", "ORD-002", "PAY-004"],
        "summary": "Governing pilot merchant policy for order cancellations, customer return windows, and partial refund calculations.",
        "sections": [
            ("Order Cancellation Guidelines", "Customers may initiate self-service cancellations while an order remains in PENDING or AUTHORIZED state. Once warehouse packing commences, cancellation is disabled and the customer must utilize the return workflow."),
            ("Meridian Return Window", "For Meridian Outfitters, customer return requests may be opened within 30 calendar days of documented carrier delivery. Returned goods are subject to merchant warehouse inspection."),
            ("Partial Refund Computation", "Partial line-item refunds cannot exceed the total captured transaction amount minus previous settled refunds. A refund is considered completed only upon PulsePay webhook settlement confirmation."),
            ("Policy Lineage", "This policy supersedes the outdated 14-day return window stated in superseded ADR-001.")
        ]
    },
    {
        "id": "DOC-ORG-MEETING-2026-10-09", "file": "Pilot_Weekly_Decisions_2026-10-09.md",
        "title": "Pilot Weekly Decisions and Actions — 9 October", "project_id": None, "org_id": "ORG-NSC", "scope": "organization",
        "owner": "M-002", "date": "2026-10-09", "version": "1.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["PAY-002", "CHKO-005", "CAT-002"],
        "summary": "Action items, release blocker updates, and cross-organization decisions from the 9 October pilot sync.",
        "sections": [
            ("Key Strategic Decisions", "Checkout release remains gated behind feature flag until duplicate webhook replay verification passes. Meridian agreed to deliver a 2,000-row sample catalog file by 14 October 2026. PulsePay will notify on staging maintenance windows."),
            ("Action Items & Owners", "M-006 (Noah Kim) owns webhook inbox verification proof; M-010 (Owen Garcia) owns regression test execution; M-016 (Morgan Ellis) delivers the sample catalog; M-017 (Taylor Reed) provides PulsePay sandbox schedule."),
            ("Current Blockers & Risks", "Webhook remediation (PAY-002) is blocked pending reproducible trace in staging. Search latency benchmark requires a stable 50,000-product index fixture."),
            ("Next Milestone Gate", "Release readiness gate is scheduled for 16 October 2026. All P0 and P1 blockers must be resolved.")
        ]
    },
    {
        "id": "DOC-PLAT-MIG-010", "file": "Multi_Tenant_Database_Migration_Plan.md",
        "title": "Multi-Tenant Database Migration Plan", "project_id": "NSC-PLAT", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-035", "date": "2026-08-05", "version": "1.1", "status": "Approved",
        "class": "Internal", "groups": ["GRP-PLATFORM"], "issues": ["PLAT-007", "PLAT-009"],
        "summary": "Database schema migration playbook for zero-downtime multi-tenant partition rollouts in PostgreSQL.",
        "sections": [
            ("Migration Strategy", "Utilize expand/contract pattern for database column additions. New columns must be added as nullable or with safe defaults before code deployment."),
            ("Rollback Guidelines", "Never edit an existing migration script. Create forward-rolling corrective migrations or execute designated down-scripts during maintenance windows.")
        ]
    },
    {
        "id": "DOC-SRCH-STD-005", "file": "Search_Synonym_Dictionary_Standard_v2.md",
        "title": "Search Synonym Dictionary Standard", "project_id": "NSC-SRCH", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-021", "date": "2026-07-17", "version": "2.0", "status": "Approved",
        "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["SRCH-002", "SRCH-005"],
        "summary": "Formatting rules, expansion syntax, and validation criteria for merchant synonym dictionary definitions.",
        "sections": [
            ("Synonym Syntax Standards", "Synonyms are specified as one-way mappings ('coat => jacket, outerwear') or bidirectional equivalences ('trousers, pants')."),
            ("Tenant Isolation Constraint", "Synonyms configured for Meridian Outfitters must not expand queries for any other merchant tenant on the shared cluster.")
        ]
    },
    {
        "id": "DOC-CHKO-RCA-008", "file": "Incident_RCA_Checkout_Idempotency_Conflict.md",
        "title": "Incident RCA: Checkout Idempotency Key Conflict", "project_id": "NSC-CHKO", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-026", "date": "2026-08-27", "version": "1.0", "status": "Approved",
        "class": "Restricted", "groups": ["GRP-CHECKOUT", "GRP-SECURITY"], "issues": ["CHKO-012", "CHKO-015"],
        "summary": "Analysis of transient HTTP 409 idempotency conflict errors during Meridian pilot simulated checkout stress tests.",
        "sections": [
            ("Incident Description", "Automated stress testing triggered false-positive HTTP 409 errors due to floating point rounding discrepancies in total cart tax computations."),
            ("Resolution & Invariant", "Standardized all tax calculations to integer minor currency units prior to hashing payload for idempotency verification.")
        ]
    },
    {
        "id": "DOC-INT-MERIDIAN-001", "file": "Merchant_Integration_Guide_Meridian.md",
        "title": "Merchant Integration Guide: Meridian Outfitters", "project_id": "NSC-CAT", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-015", "date": "2026-05-18", "version": "1.5", "status": "Approved",
        "class": "Customer Restricted", "groups": ["GRP-MERIDIAN"], "issues": ["CAT-008"],  # Resolved INT-001 to CAT-008!
        "summary": "Tailored integration specification for Meridian Outfitters ERP catalog feed and inventory synchronization.",
        "sections": [
            ("Catalog Synchronization Protocol", "Meridian exports nightly CSV catalog snapshots to designated SFTP endpoint. The automated batch worker ingests records at 02:00 UTC. Canonical issue tracking corresponds to CAT-008 (Meridian partner feed reference INT-001)."),
            ("Authentication Credentials", "Meridian API clients utilize OAuth2 client credentials scoped exclusively to tenant identifier 'MERIDIAN-01'.")
        ]
    },
    {
        "id": "DOC-INT-PULSEPAY-002", "file": "Partner_Webhook_Specification_PulsePay.md",
        "title": "Partner Webhook Specification: PulsePay Network", "project_id": "NSC-PAY", "org_id": "ORG-NSC", "scope": "project",
        "owner": "M-017", "date": "2026-05-22", "version": "2.2", "status": "Approved",
        "class": "Restricted", "groups": ["GRP-PULSEPAY", "GRP-PAYMENT"], "issues": ["PAY-008", "PAY-010"],
        "summary": "Technical webhook specifications, payload contracts, signature verification, and replay policies for PulsePay.",
        "sections": [
            ("Webhook Delivery Rules", "PulsePay delivers JSON events via HTTPS POST with header 'X-PulsePay-Signature' containing HMAC-SHA256 signature."),
            ("Retry Intervals", "PulsePay retries failed endpoints (non-2xx) at 1m, 5m, 15m, 1h, 6h, and 24h intervals.")
        ]
    }
]

# Extend the original v1 formal set with the approved completion baseline.
md_specs.extend(completion.ADDITIONAL_MARKDOWN_SPECS)

requirement_records = []
for code, project in completion.PROJECTS.items():
    for index, (statement, acceptance) in enumerate(project["requirements"], 1):
        requirement_records.append({
            "requirement_id": f"FR-{code}-{index:03d}",
            "requirement_type": "functional",
            "title": statement,
            "statement": statement,
            "priority": "High" if index in (1, 2, 6, 7) else "Medium",
            "status": "Approved",
            "organization_id": "ORG-NSC",
            "project_id": project["project_id"],
            "owner_id": project["owner"],
            "acceptance_criteria": [acceptance],
            "source_document_ids": ["DOC-ORG-SRS-001", f"DOC-{code}-ANNEX-001"],
            "source_issue_keys": project["issues"],
            "test_case_ids": [],
            "updated_at": "2026-10-12",
            "synthetic": True
        })

nfr_owner = {
    "NFR-SEC-001": "M-012", "NFR-SEC-002": "M-012", "NFR-SEC-003": "M-012",
    "NFR-REL-001": "M-009", "NFR-REL-002": "M-013",
    "NFR-PERF-001": "M-004", "NFR-PERF-002": "M-009",
    "NFR-DATA-001": "M-012", "NFR-DATA-002": "M-011", "NFR-OPS-001": "M-013"
}
for requirement_id, title, statement, priority, acceptance in completion.NON_FUNCTIONAL_REQUIREMENTS:
    requirement_records.append({
        "requirement_id": requirement_id,
        "requirement_type": "non_functional",
        "title": title,
        "statement": statement,
        "priority": priority,
        "status": "Approved",
        "organization_id": "ORG-NSC",
        "project_id": None,
        "owner_id": nfr_owner[requirement_id],
        "acceptance_criteria": [acceptance],
        "source_document_ids": ["DOC-ORG-SRS-001", "DOC-ORG-THREAT-001" if requirement_id.startswith("NFR-SEC") else "DOC-ORG-SDS-001"],
        "source_issue_keys": ["PLAT-001", "PLAT-004"],
        "test_case_ids": [],
        "updated_at": "2026-10-12",
        "synthetic": True
    })

functional_test_cases = []
for code, seeds in completion.FUNCTIONAL_CASE_SEEDS.items():
    project = completion.PROJECTS[code]
    for index, (title, actor, preconditions, steps, expected, priority, tags) in enumerate(seeds, 1):
        requirement_id = f"FR-{code}-{index:03d}"
        case_id = f"FT-{code}-{index:03d}"
        functional_test_cases.append({
            "case_id": case_id,
            "case_type": "functional",
            "project_id": project["project_id"],
            "requirement_ids": [requirement_id],
            "title": title,
            "actor": actor,
            "preconditions": preconditions,
            "steps": steps,
            "expected_result": expected,
            "priority": priority,
            "tags": tags,
            "source_issue_keys": project["issues"],
            "automation_candidate": True,
            "status": "Approved",
            "synthetic": True
        })

for index, seed in enumerate(completion.CROSS_CUTTING_CASES, 1):
    title, actor, preconditions, steps, expected, priority, tags = seed
    requirement_id = completion.NON_FUNCTIONAL_REQUIREMENTS[(index - 1) % len(completion.NON_FUNCTIONAL_REQUIREMENTS)][0]
    functional_test_cases.append({
        "case_id": f"FT-CROSS-{index:03d}",
        "case_type": "cross_cutting",
        "project_id": None,
        "requirement_ids": [requirement_id],
        "title": title,
        "actor": actor,
        "preconditions": preconditions,
        "steps": steps,
        "expected_result": expected,
        "priority": priority,
        "tags": tags,
        "source_issue_keys": ["PLAT-001", "PLAT-004"],
        "automation_candidate": True,
        "status": "Approved",
        "synthetic": True
    })

requirements_by_id = {r["requirement_id"]: r for r in requirement_records}
for case in functional_test_cases:
    for requirement_id in case["requirement_ids"]:
        requirements_by_id[requirement_id]["test_case_ids"].append(case["case_id"])

failed_case_id = "FT-CHKO-007"
blocked_case_id = "FT-PAY-008"
qa_executors = ["M-010", "M-037", "M-038", "M-039", "M-040"]
test_execution_results = []
for index, case in enumerate(functional_test_cases, 1):
    outcome = "Failed" if case["case_id"] == failed_case_id else "Blocked" if case["case_id"] == blocked_case_id else "Passed"
    actual = case["expected_result"]
    defect_issue_key = None
    if outcome == "Failed":
        actual = "Two concurrent requests produced separate order identifiers before the idempotency uniqueness guard completed."
        defect_issue_key = "CHKO-005"
    elif outcome == "Blocked":
        actual = "Execution could not start because the PulsePay sandbox certificate rotation was not complete."
        defect_issue_key = "PAY-002"
    executor_id = "M-010" if outcome in ("Failed", "Blocked") else qa_executors[(index - 1) % len(qa_executors)]
    exec_is_ot = (index > 64) or outcome in ("Failed", "Blocked")
    exec_ts = make_human_timestamp(TODAY, index * 3, is_ot=exec_is_ot, slot_index=index)
    test_execution_results.append({
        "execution_id": f"EXEC-RUN-20261012-{index:03d}",
        "run_id": "RUN-2026-10-12-01",
        "case_id": case["case_id"],
        "build_id": "commerce-demo-1.0.0-rc3",
        "environment": "staging-sim",
        "executed_by": executor_id,
        "executed_at": exec_ts,
        "is_overtime": exec_is_ot,
        "work_mode": "overtime_weekday" if exec_is_ot else "regular_hours",
        "outcome": outcome,
        "actual_result": actual,
        "defect_issue_key": defect_issue_key,
        "evidence_ref": f"synthetic-evidence/{case['case_id']}",
        "synthetic": True
    })

project_code_by_id = {project["project_id"]: code for code, project in completion.PROJECTS.items()}
for spec in md_specs:
    if spec.get("project_id") in project_code_by_id and spec.get("dynamic_project_requirements"):
        code = project_code_by_id[spec["project_id"]]
        spec["requirement_ids"] = [r["requirement_id"] for r in requirement_records if r["project_id"] == spec["project_id"]]
    elif spec["id"] in {"DOC-ORG-SRS-001", "DOC-ORG-RDS-001", "DOC-ORG-RTM-001"}:
        spec["requirement_ids"] = [r["requirement_id"] for r in requirement_records]

# DOCX writing helpers
def shade(cell, color):
    props = cell._tc.get_or_add_tcPr()
    element = OxmlElement("w:shd")
    element.set(qn("w:fill"), color)
    props.append(element)

def put_cell(cell, value, bold=False, color="24364B"):
    cell.text = ""
    run = cell.paragraphs[0].add_run(str(value))
    run.bold = bold
    run.font.name = "Aptos"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

def write_docx(spec):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(.65)
    section.bottom_margin = Inches(.65)
    section.left_margin = Inches(.78)
    section.right_margin = Inches(.78)

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(35, 48, 62)
    normal.paragraph_format.space_after = Pt(5)

    for name, size, color in [("Title", 22, "16324F"), ("Heading 1", 14, "16324F")]:
        style = doc.styles[name]
        style.font.name = "Aptos"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)

    header = section.header.paragraphs[0]
    header.text = "NORTHSTAR COMMERCE SYSTEMS   /   SYNTHETIC ENTERPRISE DATASET"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for run in header.runs:
        run.font.name = "Aptos"; run.font.size = Pt(8); run.font.color.rgb = RGBColor(105, 119, 132)

    footer = section.footer.paragraphs[0]
    footer.text = f"Synthetic demo material  •  {spec['id']}  •  v{spec['version']}"
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in footer.runs:
        run.font.name = "Aptos"; run.font.size = Pt(8); run.font.color.rgb = RGBColor(105, 119, 132)

    p = doc.add_paragraph(style="Title")
    p.paragraph_format.space_after = Pt(3)
    p.add_run(spec["title"])

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    sub = p.add_run(spec["summary"])
    sub.italic = True
    sub.font.color.rgb = RGBColor(81, 96, 111)

    meta = doc.add_table(rows=0, cols=4)
    meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Document ID", spec["id"], "Project", spec.get("project", "N/A")),
        ("Owner", spec["owner"], "Version", spec["version"]),
        ("Updated", spec["date"], "Status", spec["status"]),
        ("Classification", spec["class"], "Access Groups", ", ".join(spec["groups"]))
    ]
    for row in meta_rows:
        cells = meta.add_row().cells
        for i, val in enumerate(row):
            put_cell(cells[i], val, i in [0, 2], "FFFFFF" if i in [0, 2] else "24364B")
            shade(cells[i], "16697A" if i in [0, 2] else "F1F5F8")

    doc.add_paragraph()
    for heading, items in spec["sections"]:
        doc.add_heading(heading, level=1)
        for item in items:
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(3)
            p.add_run(item)

    if spec.get("table"):
        doc.add_heading("Reference Table", level=1)
        data = spec["table"]
        table = doc.add_table(rows=1, cols=len(data[0]))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, val in enumerate(data[0]):
            put_cell(table.rows[0].cells[j], val, True, "FFFFFF")
            shade(table.rows[0].cells[j], "16324F")
        for ix, row in enumerate(data[1:], 1):
            cells = table.add_row().cells
            for j, val in enumerate(row):
                put_cell(cells[j], val)
                shade(cells[j], "F1F5F8" if ix % 2 == 0 else "FFFFFF")

    target_path = ROOT / "documents" / "docx" / spec["file"]
    doc.save(target_path)
    canonicalize_zip_file(target_path)

completion_docx_specs = []
for source_spec in md_specs:
    rendition_name = source_spec.get("docx_rendition")
    if not rendition_name:
        continue
    rendition = dict(source_spec)
    rendition["file"] = rendition_name
    rendition["project"] = source_spec.get("project_id") or "Organization"
    rendition["sections"] = [(heading, [body]) for heading, body in source_spec["sections"]]
    rendition["table"] = source_spec.get("docx_table")
    completion_docx_specs.append(rendition)

all_docx_specs = docx_specs + completion_docx_specs

def markdown_table(headers, rows):
    def cell(value):
        return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")
    output = ["| " + " | ".join(cell(value) for value in headers) + " |",
              "| " + " | ".join("---" for _ in headers) + " |"]
    output.extend("| " + " | ".join(cell(value) for value in row) + " |" for row in rows)
    return "\n".join(output)

def write_formal_markdown(spec):
    path = ROOT / "documents" / "markdown" / "formal" / spec["file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    rel_path = f"documents/markdown/formal/{spec['file']}"
    proj_val = f'"{spec["project_id"]}"' if spec.get("project_id") else "null"
    rendition_paths = [f"documents/docx/{spec['docx_rendition']}"] if spec.get("docx_rendition") else []
    scope_value = spec.get("scope") or ("project" if spec.get("project_id") else "organization")
    lines = [
        "---",
        f"document_id: \"{spec['id']}\"",
        f"title: \"{spec['title']}\"",
        f"project_id: {proj_val}",
        f"organization_id: \"{spec.get('org_id', 'ORG-NSC')}\"",
        f"scope: \"{scope_value}\"",
        f"owner_id: \"{spec['owner']}\"",
        f"created_at: \"{spec['date']}\"",
        f"updated_at: \"{spec['date']}\"",
        f"version: \"{spec['version']}\"",
        f"status: \"{spec['status']}\"",
        f"classification: \"{spec['class']}\"",
        f"access_groups: {json.dumps(spec['groups'])}",
        f"source_issue_keys: {json.dumps(spec['issues'])}",
        f"canonical_document_id: \"{spec.get('canonical_document_id', spec['id'])}\"",
        f"rendition_paths: {json.dumps(rendition_paths)}",
        f"requirement_ids: {json.dumps(spec.get('requirement_ids', []))}",
        f"file_path: \"{rel_path}\"",
        "format: \"markdown\"",
        "synthetic: true",
        "---",
        "",
        f"# {spec['title']}",
        "",
        spec["summary"],
        ""
    ]
    for heading, body in spec["sections"]:
        lines.extend([f"## {heading}", "", body, ""])
    if spec.get("dynamic_project_requirements"):
        code = spec["dynamic_project_requirements"]
        rows = []
        for requirement in requirement_records:
            if requirement["project_id"] != f"NSC-{code}":
                continue
            rows.append([
                requirement["requirement_id"], requirement["priority"], requirement["statement"],
                requirement["acceptance_criteria"][0], ", ".join(requirement["source_issue_keys"]),
                ", ".join(requirement["test_case_ids"])
            ])
        lines.extend(["## Requirement IDs and verification", "",
                      markdown_table(["Requirement", "Priority", "Statement", "Acceptance criteria", "Jira source", "Test cases"], rows), ""])
    if spec.get("dynamic_coverage_matrix"):
        rows = []
        for doc_spec in md_specs:
            scope = doc_spec.get("project_id") or "ORG-NSC"
            fmt = "Markdown + DOCX rendition" if doc_spec.get("docx_rendition") else "Markdown"
            rows.append([doc_spec["id"], doc_spec["title"], scope, doc_spec["owner"], doc_spec["status"], doc_spec["class"], ", ".join(doc_spec["groups"]), fmt])
        for doc_spec in docx_specs:
            rows.append([doc_spec["id"], doc_spec["title"], doc_spec["project"], doc_spec["owner"], doc_spec["status"], doc_spec["class"], ", ".join(doc_spec["groups"]), "DOCX canonical"])
        lines.extend(["## Formal document inventory", "",
                      markdown_table(["Canonical ID", "Title", "Scope", "Owner", "Status", "Classification", "Access groups", "Format"], rows), ""])
        lines.extend(["## Eight project coverage", "",
                      markdown_table(["Project", "Owner", "Access group", "Annex", "Requirement count"], [
                          [p["project_id"], p["owner"], p["group"], f"DOC-{code}-ANNEX-001", sum(1 for r in requirement_records if r["project_id"] == p["project_id"])]
                          for code, p in completion.PROJECTS.items()
                      ]), ""])
    if spec.get("dynamic_rtm"):
        outcome_by_case = {result["case_id"]: result["outcome"] for result in test_execution_results}
        rows = []
        for requirement in requirement_records:
            if requirement["project_id"]:
                code = project_code_by_id[requirement["project_id"]]
                design_refs = ["DOC-ORG-SDS-001", f"DOC-{code}-ANNEX-001", "DOC-ORG-API-001", "DOC-ORG-DBD-001"]
            else:
                design_refs = ["DOC-ORG-SDS-001", "DOC-ORG-THREAT-001", "DOC-ORG-API-001"]
            outcomes = [f"{case_id}: {outcome_by_case.get(case_id, 'Missing')}" for case_id in requirement["test_case_ids"]]
            rows.append([requirement["requirement_id"], requirement["priority"], ", ".join(design_refs), ", ".join(requirement["source_issue_keys"]), ", ".join(requirement["test_case_ids"]), "; ".join(outcomes), "commerce-demo-1.0.0-rc3"])
        lines.extend(["## Requirement traceability", "",
                      markdown_table(["Requirement", "Priority", "Design/API/Data", "Jira issue", "Test case", "Latest execution", "Release candidate"], rows), ""])
    if spec.get("dynamic_adr_index"):
        adr_rows = []
        for doc_spec in md_specs + docx_specs:
            if "ADR" in doc_spec["title"].upper() or "DECISION" in doc_spec["title"].upper():
                adr_rows.append([doc_spec["id"], doc_spec["title"], doc_spec.get("version", ""), doc_spec["status"], doc_spec["owner"], ", ".join(doc_spec["issues"])])
        lines.extend(["## Decision record index", "",
                      markdown_table(["Document ID", "Decision", "Version", "Status", "Owner", "Linked issues"], adr_rows), ""])
    if spec.get("dynamic_risk_register"):
        risk_rows = [
            ["RISK-001", "Concurrent checkout retries may create duplicate orders or captures", "4", "5", "M-005", "Enforce unique durable idempotency and rerun concurrency case FT-CHKO-007", "FT-CHKO-007 fails", "Open"],
            ["RISK-002", "PulsePay certificate rotation may delay signed webhook verification", "4", "4", "M-006", "Coordinate partner window and execute FT-PAY-008", "Certificate unavailable", "Open"],
            ["RISK-003", "Tenant context defects could expose another merchant's records", "2", "5", "M-012", "Gateway-derived tenant scope and pre-retrieval ACL tests", "Any cross-tenant signal", "Mitigating"],
            ["RISK-004", "Catalog sample may not represent the full production SKU distribution", "3", "3", "M-016", "Profile a larger merchant sample before launch", "Sample misses edge formats", "Open"],
            ["RISK-005", "External tax or carrier sandbox instability may block end-to-end UAT", "3", "3", "M-002", "Use contract stubs only for isolated tests; rerun provider scenarios", "Provider outage", "Mitigating"],
            ["RISK-006", "Search relevance may miss target for long-tail apparel queries", "3", "3", "M-004", "Expand judged query set and tune versioned synonyms", "nDCG@10 below 0.82", "Open"],
            ["RISK-007", "Recovery process may exceed pilot RTO if restore is not rehearsed", "2", "4", "M-013", "Run isolated restore drill and record measured RPO/RTO", "Drill misses target", "Mitigating"],
            ["RISK-008", "Superseded or test-only content may be mistaken for active policy", "3", "4", "M-002", "Canonical IDs, status lineage, and isolated fixture namespace", "Stale answer citation", "Open"],
        ]
        lines.extend(["## Risk register", "",
                      markdown_table(["Risk ID", "Risk", "Likelihood", "Impact", "Owner", "Mitigation", "Trigger", "Status"], risk_rows), ""])
    if spec["id"] == "DOC-PAY-ADR-003":
        lines.extend(["## Version Lineage", "", "Supersedes DOC-PAY-ADR-001. The old decision remains available for historical audit and conflict testing.", ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

for s in all_docx_specs: write_docx(s)
for s in md_specs: write_formal_markdown(s)

# Fixtures (6 physical files, 5 registered in documents catalog)
(ROOT / "fixtures" / "duplicate_upload.md").write_bytes(
    (ROOT / "documents" / "markdown" / "formal" / "Payment_Orchestration_ADR_v3.md").read_bytes()
)
(ROOT / "fixtures" / "missing_metadata.md").write_text(
    "# Unindexed Sprint Note\n\nNo document ID, owner, project, version, or classification is intentionally supplied for this scratch fixture.\n",
    encoding="utf-8"
)
(ROOT / "fixtures" / "broken_link.md").write_text(
    "---\ndocument_id: \"FIX-BROKEN-LINK\"\ntitle: \"Broken Link Reference Fixture\"\nproject_id: \"NSC-PLAT\"\norganization_id: \"ORG-NSC\"\nscope: \"fixture\"\nowner_id: \"M-009\"\nclassification: \"Internal\"\n---\n\nSee [the missing runbook](https://docs.northstar.invalid/missing/nonexistent_runbook_path).\n",
    encoding="utf-8"
)
(ROOT / "fixtures" / "conflicting_timestamp.md").write_text(
    "---\ndocument_id: \"FIX-CONFLICT-TIME\"\ntitle: \"Conflicting Timestamp Fixture\"\nproject_id: \"NSC-PAY\"\norganization_id: \"ORG-NSC\"\nscope: \"fixture\"\nowner_id: \"M-006\"\nversion: \"0.9\"\ncreated_at: \"2026-10-09\"\nupdated_at: \"2026-10-09\"\nstatus: \"Draft\"\nclassification: \"Internal\"\naccess_groups: [\"GRP-PAYMENT\"]\n---\n\nOlder version v0.9 artificially updated after v3.0 to test version precedence against chronological timestamps.\n",
    encoding="utf-8"
)
(ROOT / "fixtures" / "orphan_issue_reference.md").write_text(
    "---\ndocument_id: \"FIX-ORPHAN-ISSUE\"\ntitle: \"Orphan Jira Reference Fixture\"\nproject_id: \"NSC-CAT\"\norganization_id: \"ORG-NSC\"\nscope: \"fixture\"\nowner_id: \"M-003\"\nversion: \"1.0\"\nstatus: \"Approved\"\nclassification: \"Internal\"\naccess_groups: [\"GRP-CATALOG\"]\nsource_issue_keys: [\"NONEXISTENT-999\"]\n---\n\nCites issue NONEXISTENT-999 which does not exist in the canonical Jira registry.\n",
    encoding="utf-8"
)
(ROOT / "fixtures" / "attachments" / "payment_webhook_sample.csv").write_text(
    "provider_event_id,event_type,merchant_ref,delivery_attempt,timestamp\nEVT-SYN-1001,payment.succeeded,ORDER-SYN-501,1,2026-09-22T09:14:02Z\nEVT-SYN-1001,payment.succeeded,ORDER-SYN-501,2,2026-09-22T09:15:10Z\nEVT-SYN-1002,payment.failed,ORDER-SYN-502,1,2026-09-23T11:20:00Z\n",
    encoding="utf-8"
)
(ROOT / "fixtures" / "conflicting_policy.md").write_text(
    "---\ndocument_id: \"FIX-CONFLICT-POLICY\"\ntitle: \"Legacy Return Policy Conflict Fixture\"\nproject_id: \"NSC-ORD\"\norganization_id: \"ORG-NSC\"\nscope: \"fixture\"\nowner_id: \"M-008\"\nversion: \"0.9\"\nstatus: \"Archived\"\nclassification: \"Internal\"\naccess_groups: [\"GRP-ALL-STAFF\"]\ntest_only: true\n---\n\nTEST FIXTURE ONLY. This legacy excerpt incorrectly states a 14-calendar-day return window. It is intentionally inconsistent with approved DOC-ORD-POL-005, which governs the Meridian pilot and allows 30 calendar days after delivery. Do not use this fixture as active policy.\n",
    encoding="utf-8"
)
(ROOT / "fixtures" / "cross_tenant_probe.md").write_text(
    "---\ndocument_id: \"FIX-CROSS-TENANT\"\ntitle: \"Meridian Tenant Isolation Probe\"\nproject_id: null\norganization_id: \"ORG-MERIDIAN\"\nscope: \"fixture\"\nowner_id: \"M-064\"\nversion: \"1.0\"\nstatus: \"Draft\"\nclassification: \"Customer Restricted\"\naccess_groups: [\"GRP-MERIDIAN\"]\ntest_only: true\n---\n\nTEST FIXTURE ONLY. Synthetic merchant reference MERIDIAN-ISOLATION-CANARY-4821 must be retrievable by an authorized Meridian principal and must produce no title, count, snippet, or existence signal for Northstar-only or PulsePay-only principals.\n",
    encoding="utf-8"
)
(ROOT / "fixtures" / "offboarded_owner.md").write_text(
    "---\ndocument_id: \"FIX-OFFBOARDING-AUTHOR\"\ntitle: \"Historical Note by Offboarded Engineer\"\nproject_id: \"NSC-CAT\"\norganization_id: \"ORG-NSC\"\nscope: \"fixture\"\nowner_id: \"M-018\"\nversion: \"1.0\"\nstatus: \"Approved\"\nclassification: \"Internal\"\naccess_groups: [\"GRP-CATALOG\"]\ntest_only: true\n---\n\nTEST FIXTURE ONLY. This historical synthetic note was authored before M-018 left the company. Preserve the author attribution for audit history, but deny authentication and active group access after the recorded offboarding date.\n",
    encoding="utf-8"
)

registered_fixtures = [
    {"id": "FIX-DUPLICATE-001", "file": "fixtures/duplicate_upload.md", "title": "Duplicate Upload of ADR-003", "project_id": "NSC-PAY", "org_id": "ORG-NSC", "scope": "fixture", "owner": "M-006", "date": "2026-08-19", "version": "3.0", "status": "Approved", "class": "Restricted", "groups": ["GRP-PAYMENT", "GRP-PULSEPAY"], "issues": ["PAY-001"], "format": "markdown"},
    {"id": "FIX-MISSING-META", "file": "fixtures/missing_metadata.md", "title": "Unindexed Sprint Note (Missing Metadata)", "project_id": "NSC-PLAT", "org_id": "ORG-NSC", "scope": "fixture", "owner": "M-009", "date": "2026-07-01", "version": "1.0", "status": "Draft", "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": [], "format": "markdown"},
    {"id": "FIX-BROKEN-LINK", "file": "fixtures/broken_link.md", "title": "Broken Link Reference Fixture", "project_id": "NSC-PLAT", "org_id": "ORG-NSC", "scope": "fixture", "owner": "M-009", "date": "2026-07-31", "version": "1.0", "status": "Approved", "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": [], "format": "markdown"},
    {"id": "FIX-CONFLICT-TIME", "file": "fixtures/conflicting_timestamp.md", "title": "Conflicting Timestamp Fixture", "project_id": "NSC-PAY", "org_id": "ORG-NSC", "scope": "fixture", "owner": "M-006", "date": "2026-10-09", "version": "0.9", "status": "Draft", "class": "Internal", "groups": ["GRP-PAYMENT"], "issues": [], "format": "markdown"},
    {"id": "FIX-ORPHAN-ISSUE", "file": "fixtures/orphan_issue_reference.md", "title": "Orphan Jira Reference Fixture", "project_id": "NSC-CAT", "org_id": "ORG-NSC", "scope": "fixture", "owner": "M-003", "date": "2026-06-15", "version": "1.0", "status": "Approved", "class": "Internal", "groups": ["GRP-CATALOG"], "issues": ["NONEXISTENT-999"], "format": "markdown"},
    {"id": "FIX-CONFLICT-POLICY", "file": "fixtures/conflicting_policy.md", "title": "Legacy Return Policy Conflict Fixture", "project_id": "NSC-ORD", "org_id": "ORG-NSC", "scope": "fixture", "owner": "M-008", "date": "2026-05-04", "version": "0.9", "status": "Archived", "class": "Internal", "groups": ["GRP-ALL-STAFF"], "issues": ["ORD-001"], "format": "markdown"},
    {"id": "FIX-CROSS-TENANT", "file": "fixtures/cross_tenant_probe.md", "title": "Meridian Tenant Isolation Probe", "project_id": None, "org_id": "ORG-MERIDIAN", "scope": "fixture", "owner": "M-064", "date": "2026-10-12", "version": "1.0", "status": "Draft", "class": "Customer Restricted", "groups": ["GRP-MERIDIAN"], "issues": [], "format": "markdown"},
    {"id": "FIX-OFFBOARDING-AUTHOR", "file": "fixtures/offboarded_owner.md", "title": "Historical Note by Offboarded Engineer", "project_id": "NSC-CAT", "org_id": "ORG-NSC", "scope": "fixture", "owner": "M-018", "date": "2026-07-01", "version": "1.0", "status": "Approved", "class": "Internal", "groups": ["GRP-CATALOG"], "issues": ["CAT-001"], "format": "markdown"}
]

# -------------------------------------------------------------
# 8. Bundled Markdown Documents (56 Bundles, Exactly 1,373 Docs)
# Logical count is computed from bundles, canonical formal docs, and registered fixtures.
# Phase 3 & 4: 123 Working Days only (excluding weekends & VN holidays), rich 12-template prose!
# -------------------------------------------------------------
issues_by_project = {pid: [] for pid in PID_LIST}
for iss in issues:
    issues_by_project[iss["project_id"]].append(iss)

for pid in PID_LIST:
    issues_by_project[pid].sort(key=lambda x: x["created_at"])

# Build historical status lookup from issue_changelog so bundle documents record
# the exact status of the linked issue at doc_ts (recorded_at), never a future status.
status_transitions_by_issue = {}
for ch in changelog:
    if ch.get("field") == "status":
        status_transitions_by_issue.setdefault(ch["issue_key"], []).append((ch["changed_at"], ch["to_value"]))
for ikey in status_transitions_by_issue:
    status_transitions_by_issue[ikey].sort(key=lambda x: x[0])

def get_issue_status_at(issue_obj, at_ts):
    """Return the exact status of issue_obj at ISO timestamp at_ts (+07:00) using changelog history."""
    ikey = issue_obj["issue_key"]
    transitions = status_transitions_by_issue.get(ikey, [])
    if not transitions:
        return "To Do"
    curr = "To Do"
    for ch_ts, to_val in transitions:
        if ch_ts <= at_ts:
            curr = to_val
        else:
            break
    return curr

months = ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]

bundle_docs_map = {(pid, ym): [] for pid in PID_LIST for ym in months}
all_bundled_records = []

bundle_doc_types = [
    "Sprint Planning Update", "Architecture Decision Note", "API Contract Revision",
    "Regression Test Summary", "Performance Benchmark Report", "Merchant Sync Decision",
    "Daily Standup & Blocker Log", "Security Review Note", "Feature Rollout Milestone",
    "Incident Post-Mortem Action", "Database Migration Checklist", "Integration Review Notes"
]

BUNDLE_TEMPLATES = {
    "Sprint Planning Update": (
        "During sprint backlog commitment on [{issue_key}] ({issue_summary}), the {p_name} squad decomposed acceptance criteria, story point capacity, and cross-service dependencies.",
        "Confirmed sprint scope and velocity guardrails. Unfinished items from prior closed iterations are formally tracked via sprint spillover transitions into the active sprint.",
        "Backlog readiness verified with product owner and QA lead; test fixtures and correlation IDs linked in Jira."
    ),
    "Architecture Decision Note": (
        "Architectural review for [{issue_key}] ({issue_summary}) within {p_name}, focusing on service ownership boundaries, failure compensation, and multi-tenant isolation.",
        "Enforced strict tenant_id scoping at the repository layer and durable 72-hour idempotency keys for mutating operations.",
        "Design aligns with DOC-ORG-SDS-001; contract tests and sequence diagrams validated by the tech lead."
    ),
    "API Contract Revision": (
        "Evaluated HTTP request/response payload schemas for [{issue_key}] ({issue_summary}) in {p_name} to ensure backward compatibility and deterministic error codes.",
        "Standardized monetary fields to integer minor currency units alongside ISO 4217 currency codes; added explicit HTTP 409 conflict and HTTP 422 field validation responses.",
        "API schema snapshot tested against staging-sim consumer stubs with zero breaking changes."
    ),
    "Regression Test Summary": (
        "Executed automated regression and negative boundary suite for [{issue_key}] ({issue_summary}) across {p_name} staging fixtures.",
        "Verified idempotent replay, duplicate event suppression, and cross-tenant HTTP 403 rejection before snippet or count generation.",
        "All regression assertions recorded with deterministic seed=42 and correlation trace evidence attached."
    ),
    "Performance Benchmark Report": (
        "Conducted load and latency profiling for [{issue_key}] ({issue_summary}) in {p_name} under the pilot reference workload.",
        "Tuned PostgreSQL composite indexes and Redis lock TTLs to keep p95 latency within the approved service-level objective.",
        "Measured p95 response times, connection pool saturation, and queue lag metrics on the staging telemetry dashboard."
    ),
    "Merchant Sync Decision": (
        "Reviewed Meridian Outfitters pilot integration requirements for [{issue_key}] ({issue_summary}) with {p_name} engineering and merchant support.",
        "Confirmed tenant-isolated configuration rules, CSV batch error reporting, and SFTP nightly sync schedule at 02:00+07:00.",
        "Action items logged with merchant onboarding specialists and verified against tenant boundary checks."
    ),
    "Daily Standup & Blocker Log": (
        "Daily engineering standup checkpoint for {p_name} covering active work on [{issue_key}] ({issue_summary}) (current ticket status: `{issue_status}`).",
        "Reviewed upstream sandbox dependencies, PR review queue, and evening overtime (17:00–22:00+07:00) handoffs during sprint crunch.",
        "Updated Jira status transitions, blocker owners, and same-day escalation checkpoints."
    ),
    "Security Review Note": (
        "Application security and access-control assessment for [{issue_key}] ({issue_summary}) in {p_name}.",
        "Validated deny-by-default authorization, pre-retrieval ACL filtering, secret externalization, and zero persistence of PAN/CVV or raw credentials.",
        "AppSec sign-off recorded; negative cross-tenant and revoked-user probes passed in CI."
    ),
    "Feature Rollout Milestone": (
        "Staged canary rollout readiness check for [{issue_key}] ({issue_summary}) in {p_name}.",
        "Configured feature flag toggle and progressive traffic gates (0% synthetic -> 5% -> 25% -> 50% -> 100%) with automated rollback triggers.",
        "On-call SRE and workstream owner verified rollback runbook steps and alert routing."
    ),
    "Incident Post-Mortem Action": (
        "Follow-up remediation tracking for [{issue_key}] ({issue_summary}) in {p_name} after staging fault-injection and replay testing.",
        "Added transactional outbox and unique inbox constraints so worker restarts or network retries cannot duplicate side effects.",
        "Crash-replay simulation added to continuous integration to prevent regression."
    ),
    "Database Migration Checklist": (
        "Database schema change verification for [{issue_key}] ({issue_summary}) managed by {p_name}.",
        "Applied expand/contract migration sequencing: nullable/default columns and concurrent indexes deployed ahead of application readers/writers.",
        "Forward/down recovery notes and row-count reconciliation verified against isolated backup snapshot."
    ),
    "Integration Review Notes": (
        "Cross-service and partner integration sync for [{issue_key}] ({issue_summary}) in {p_name}.",
        "Verified HMAC-SHA256 webhook signature validation, bounded exponential backoff with jitter, and correlation ID propagation across service hops.",
        "Sandbox integration trace captured and linked to the requirement traceability matrix."
    ),
}

def generate_bundle_section(doc_id, anchor_id, doc_title, date_str, doc_ts, is_ot, work_mode, author_m, author_id, pid, p_name, bundle_groups, issue_key, issue_summary, issue_status, dtype):
    """Generate high-quality, varied technical content for each section based on 12 distinct templates."""
    ctx_text, dec_text, ver_text = BUNDLE_TEMPLATES[dtype]
    shift_label = "Evening Overtime (17:00–22:00+07:00)" if is_ot else "Regular Business Hours (08:00–17:00+07:00)"
    lines = [
        f"### [{doc_id}] {doc_title}",
        f"<a id=\"{anchor_id}\"></a>",
        "",
        f"- **Document ID**: `{doc_id}`",
        f"- **Date**: {date_str} (`{doc_ts}`)",
        f"- **Work Shift**: {shift_label}",
        f"- **Author**: {author_m['display_name']} (`{author_id}`)",
        f"- **Project**: `{pid}`",
        f"- **Scope**: `project`",
        f"- **Classification**: `Internal`",
        f"- **Access Groups**: `{', '.join(bundle_groups)}`",
        f"- **Linked Issue**: [`{issue_key}`](https://jira.northstar.invalid/browse/{issue_key}) (`{issue_status}`)",
        f"- **Record Type**: {dtype}",
        "",
        "#### Context & Technical Objective",
        ctx_text.format(issue_key=issue_key, issue_summary=issue_summary, p_name=p_name, issue_status=issue_status),
        "",
        "#### Technical Decision & Invariants",
        dec_text.format(issue_key=issue_key, issue_summary=issue_summary, p_name=p_name, issue_status=issue_status),
        "",
        "#### Verification & Evidence",
        ver_text.format(issue_key=issue_key, issue_summary=issue_summary, p_name=p_name, issue_status=issue_status),
        "",
        "---"
    ]
    return "\n".join(lines)

# Generate 1,373 documents strictly across the 123 WORKING_DAYS (0 on Saturdays, Sundays, or VN Holidays!)
doc_counter = 0
for w_idx, w_date in enumerate(WORKING_DAYS):
    num_docs = DAILY_DOC_TARGETS[w_idx]  # 11 or 12
    date_str = w_date.isoformat()
    date_tag = w_date.strftime("%Y%m%d")
    ym = w_date.strftime("%Y-%m")

    for d_in_day in range(num_docs):
        doc_counter += 1
        pid_idx = (w_idx * 3 + d_in_day) % 8
        pid = PID_LIST[pid_idx]
        p_name = next(p["name"] for p in projects if p["project_id"] == pid)
        sec_group = next(p["team_group"] for p in projects if p["project_id"] == pid)
        team = project_devs[pid]

        bundle_groups = [sec_group]

        author_id = team[(w_idx + d_in_day) % len(team)]
        author_m = next(m for m in members if m["member_id"] == author_id)

        # Determine if this engineering log was recorded during evening OT (17:00-22:00+07:00)
        doc_is_ot = ((doc_counter % 20) in PROJECT_OT_SLOTS[pid]) or (d_in_day >= 10)
        doc_work_mode = "evening_overtime" if doc_is_ot else "regular_hours"
        doc_ts = make_human_timestamp(w_date, doc_counter + pid_idx, is_ot=doc_is_ot, slot_index=d_in_day)

        # Select an issue created ON OR BEFORE this document date and reconstruct its status at doc_ts
        eligible_issues = [iss for iss in issues_by_project[pid] if iss["created_at"][:10] <= date_str]
        if not eligible_issues:
            eligible_issues = [issues_by_project[pid][0]]
        linked_iss = eligible_issues[(doc_counter + d_in_day) % len(eligible_issues)]
        issue_key = linked_iss["issue_key"]
        issue_summary = linked_iss["summary"]
        issue_status = get_issue_status_at(linked_iss, doc_ts)

        prefix = pid.replace("NSC-", "")
        doc_seq = len(bundle_docs_map[(pid, ym)]) + 1
        doc_id = f"DOC-{prefix}-{date_tag}-{doc_seq:02d}"
        anchor_id = f"doc-{prefix.lower()}-{date_tag}-{doc_seq:02d}"

        dtype = bundle_doc_types[(doc_counter + pid_idx) % len(bundle_doc_types)]
        doc_title = f"{p_name}: {dtype} #{doc_seq} ({date_str})"

        section_text = generate_bundle_section(
            doc_id, anchor_id, doc_title, date_str, doc_ts, doc_is_ot, doc_work_mode,
            author_m, author_id, pid, p_name, bundle_groups,
            issue_key, issue_summary, issue_status, dtype
        )

        section_sha256 = compute_section_sha256(section_text)
        bundle_rel_path = f"documents/markdown/bundles/{pid}-{ym}.md"

        doc_rec = {
            "document_id": doc_id,
            "canonical_document_id": doc_id,
            "title": doc_title,
            "project_id": pid,
            "organization_id": "ORG-NSC",
            "scope": "project",
            "owner_id": author_id,
            "created_at": date_str,
            "updated_at": date_str,
            "recorded_at": doc_ts,
            "is_overtime": doc_is_ot,
            "work_mode": doc_work_mode,
            "version": "1.0",
            "status": "Approved",
            "classification": "Internal",
            "access_groups": bundle_groups,
            "source_issue_keys": [issue_key],
            "requirement_ids": [],
            "rendition_paths": [],
            "file_path": bundle_rel_path,
            "section_anchor": f"#{anchor_id}",
            "content_sha256": section_sha256,
            "format": "markdown_bundle",
            "canonical_url": f"https://docs.northstar.invalid/{pid.lower()}/{doc_id.lower()}",
            "is_current": True,
            "supersedes": [],
            "superseded_by": None,
            "document_role": "canonical",
            "test_only": False,
            "synthetic": True
        }

        bundle_docs_map[(pid, ym)].append((section_text, doc_rec))
        all_bundled_records.append(doc_rec)

assert len(all_bundled_records) == 1373, f"Expected 1373 bundled records, got {len(all_bundled_records)}"

# Write out the 56 bundle files
total_bundles_written = 0
for (pid, ym), sections_data in bundle_docs_map.items():
    p_name = next(p["name"] for p in projects if p["project_id"] == pid)
    sec_group = next(p["team_group"] for p in projects if p["project_id"] == pid)
    bundle_groups = [sec_group]

    bundle_filename = f"{pid}-{ym}.md"
    bundle_abs_path = ROOT / "documents" / "markdown" / "bundles" / bundle_filename

    bundle_header = [
        "---",
        f"bundle_id: \"BUNDLE-{pid}-{ym}\"",
        f"project_id: \"{pid}\"",
        f"project_name: \"{p_name}\"",
        f"period: \"{ym}\"",
        f"classification: \"Internal\"",
        f"access_groups: {json.dumps(bundle_groups)}",
        f"logical_document_count: {len(sections_data)}",
        "synthetic: true",
        "---",
        "",
        f"# {p_name} — Monthly Engineering Records ({ym})",
        "",
        f"This Markdown bundle organizes {len(sections_data)} verified logical project records, decisions, meeting outcomes, and technical milestone updates for {pid} during {ym}.",
        ""
    ]

    body = "\n\n".join(item[0] for item in sections_data)
    bundle_abs_path.write_text("\n".join(bundle_header) + "\n" + body + "\n", encoding="utf-8")
    total_bundles_written += 1

assert total_bundles_written == 56

# -------------------------------------------------------------
# 9. Assemble the complete canonical documents catalog
# -------------------------------------------------------------
canonical_documents = []

# DOCX (10)
for d_idx, s in enumerate(docx_specs):
    p_path = ROOT / "documents" / "docx" / s["file"]
    rel_p = f"documents/docx/{s['file']}"
    d_date = date.fromisoformat(s["date"])
    d_ot = s.get("project") in ("NSC-CHKO", "NSC-PAY") and (d_idx % 3 == 0)
    d_mode = "evening_overtime" if d_ot else "regular_hours"
    d_ts = make_human_timestamp(d_date, 6000 + d_idx, is_ot=d_ot)
    canonical_documents.append({
        "document_id": s["id"], "title": s["title"], "project_id": s["project"],
        "canonical_document_id": s["id"], "rendition_paths": [], "requirement_ids": [],
        "organization_id": "ORG-NSC", "scope": "project",
        "owner_id": s["owner"], "created_at": s["date"], "updated_at": s["date"],
        "recorded_at": d_ts, "is_overtime": d_ot, "work_mode": d_mode,
        "version": s["version"], "status": s["status"], "classification": s["class"],
        "access_groups": s["groups"], "source_issue_keys": s["issues"],
        "file_path": rel_p, "section_anchor": None, "content_sha256": file_hash(p_path),
        "format": "docx", "canonical_url": f"https://docs.northstar.invalid/{s['project'].lower()}/{s['id'].lower()}",
        "is_current": s["status"] != "Superseded", "supersedes": [], "superseded_by": None,
        "document_role": "canonical", "test_only": False, "synthetic": True
    })

# Formal Markdown (46)
for m_idx, s in enumerate(md_specs):
    p_path = ROOT / "documents" / "markdown" / "formal" / s["file"]
    rel_p = f"documents/markdown/formal/{s['file']}"
    d_date = date.fromisoformat(s["date"])
    d_ot = s.get("project_id") in ("NSC-CHKO", "NSC-PAY") and (m_idx % 3 == 0)
    d_mode = "evening_overtime" if d_ot else "regular_hours"
    d_ts = make_human_timestamp(d_date, 6200 + m_idx, is_ot=d_ot)
    canonical_documents.append({
        "document_id": s["id"], "title": s["title"], "project_id": s.get("project_id"),
        "canonical_document_id": s.get("canonical_document_id", s["id"]),
        "rendition_paths": [f"documents/docx/{s['docx_rendition']}"] if s.get("docx_rendition") else [],
        "requirement_ids": s.get("requirement_ids", []),
        "organization_id": s.get("org_id", "ORG-NSC"), "scope": s.get("scope") or ("project" if s.get("project_id") else "organization"),
        "owner_id": s["owner"], "created_at": s["date"], "updated_at": s["date"],
        "recorded_at": d_ts, "is_overtime": d_ot, "work_mode": d_mode,
        "version": s["version"], "status": s["status"], "classification": s["class"],
        "access_groups": s["groups"], "source_issue_keys": s["issues"],
        "file_path": rel_p, "section_anchor": None, "content_sha256": file_hash(p_path),
        "format": "markdown", "canonical_url": f"https://docs.northstar.invalid/docs/{s['id'].lower()}",
        "is_current": s["status"] != "Superseded",
        "supersedes": ["DOC-PAY-ADR-001"] if s["id"] == "DOC-PAY-ADR-003" else [],
        "superseded_by": "DOC-PAY-ADR-003" if s["id"] == "DOC-PAY-ADR-001" else None,
        "document_role": "canonical", "test_only": False, "synthetic": True
    })

# Registered Fixtures (5)
for f_idx, f in enumerate(registered_fixtures):
    p_path = ROOT / f["file"]
    d_date = date.fromisoformat(f["date"])
    d_ot = False
    d_mode = "regular_hours"
    d_ts = make_human_timestamp(d_date, 6400 + f_idx, is_ot=False)
    canonical_documents.append({
        "document_id": f["id"], "title": f["title"], "project_id": f["project_id"],
        "canonical_document_id": "DOC-PAY-ADR-003" if f["id"] == "FIX-DUPLICATE-001" else f["id"], "rendition_paths": [], "requirement_ids": [],
        "organization_id": f["org_id"], "scope": f["scope"],
        "owner_id": f["owner"], "created_at": f["date"], "updated_at": f["date"],
        "recorded_at": d_ts, "is_overtime": d_ot, "work_mode": d_mode,
        "version": f["version"], "status": f["status"], "classification": f["class"],
        "access_groups": f["groups"], "source_issue_keys": f["issues"],
        "file_path": f["file"], "section_anchor": None, "content_sha256": file_hash(p_path),
        "format": f["format"], "canonical_url": f"https://docs.northstar.invalid/fixtures/{f['id'].lower()}",
        "is_current": f["status"] not in ("Superseded", "Archived"), "supersedes": [], "superseded_by": None,
        "document_role": "test_fixture", "test_only": True, "synthetic": True
    })

# Bundled (1,373)
canonical_documents.extend(all_bundled_records)

expected_logical_documents = 1373 + len(docx_specs) + len(md_specs) + len(registered_fixtures)
assert len(canonical_documents) == expected_logical_documents, f"Expected {expected_logical_documents} documents, got {len(canonical_documents)}"

# -------------------------------------------------------------
# 10. Write structured entities and requirement/test JSONL files
# -------------------------------------------------------------
write_jsonl("structured/organizations.jsonl", orgs)
write_jsonl("structured/departments.jsonl", departments)
write_jsonl("structured/members.jsonl", members)
write_jsonl("structured/access_groups.jsonl", groups)
write_jsonl("structured/group_memberships.jsonl", memberships)
write_jsonl("structured/projects.jsonl", projects)
write_jsonl("structured/project_memberships.jsonl", project_memberships)
write_jsonl("structured/sprints.jsonl", sprints)  # Phase 5: Sprints
write_jsonl("structured/issues.jsonl", issues)
write_jsonl("structured/issue_comments.jsonl", comments)
write_jsonl("structured/issue_changelog.jsonl", changelog)
write_jsonl("structured/requirements.jsonl", requirement_records)
write_jsonl("structured/functional_test_cases.jsonl", functional_test_cases)
write_jsonl("structured/test_execution_results.jsonl", test_execution_results)
work_tasks, task_notes, document_reviews, work_reports, workflow_cases = build_workflows(
    issues, canonical_documents, members, project_memberships, projects, VN_HOLIDAYS, TODAY.isoformat()
)
canonical_documents = reconcile_document_snapshots(canonical_documents, document_reviews)
validate_workflows(
    work_tasks, task_notes, document_reviews, work_reports, workflow_cases,
    issues, canonical_documents, members, project_memberships, TODAY.isoformat()
)
continuum_id_mappings = []
for _o in orgs:
    continuum_id_mappings.append({
        "mapping_id": f"MAP-ORG-{_o['org_id']}",
        "entity_kind": "organization",
        "source_file": "structured/organizations.jsonl",
        "source_id": _o["org_id"],
        "continuum_id": _o["continuum_org_id"],
        "target_service": "iam",
        "target_collection": "organizations",
        "organization_id": _o["org_id"],
        "project_id": None,
        "import_eligible": _o["org_id"] == "ORG-NSC",
        "support_status": "IMPORTER_REQUIRED" if _o["org_id"] == "ORG-NSC" else "DATASET_METADATA_ONLY",
        "notes": "Primary Continuum tenant ORG-NSC" if _o["org_id"] == "ORG-NSC" else "External counterparty tenant kept out of ORG-NSC import",
    })
for _m in members:
    continuum_id_mappings.append({
        "mapping_id": f"MAP-USR-{_m['member_id']}",
        "entity_kind": "user_and_org_member",
        "source_file": "structured/members.jsonl",
        "source_id": _m["member_id"],
        "continuum_id": _m["continuum_user_id"],
        "secondary_continuum_id": _m["continuum_org_membership_id"],
        "target_service": "iam",
        "target_collection": "users+organization_members",
        "organization_id": _m["org_id"],
        "project_id": None,
        "continuum_role": _m["continuum_org_role"],
        "import_eligible": _m["continuum_import_eligible"],
        "support_status": "IMPORTER_REQUIRED" if _m["continuum_import_eligible"] else "DATASET_METADATA_ONLY",
        "notes": f"status={_m['continuum_membership_status']}",
    })
for _p in projects:
    continuum_id_mappings.append({
        "mapping_id": f"MAP-PRJ-{_p['project_id']}",
        "entity_kind": "project",
        "source_file": "structured/projects.jsonl",
        "source_id": _p["project_id"],
        "continuum_id": _p["continuum_project_id"],
        "continuum_code": _p["continuum_code"],
        "target_service": "iam",
        "target_collection": "projects",
        "organization_id": "ORG-NSC",
        "project_id": _p["project_id"],
        "import_eligible": True,
        "support_status": "API_SUPPORTED",
        "notes": f"created_by={_p['created_by']} team_leader={_p['team_leader_id']}",
    })
for _pm in project_memberships:
    continuum_id_mappings.append({
        "mapping_id": f"MAP-PM-{_pm['membership_id']}",
        "entity_kind": "project_membership",
        "source_file": "structured/project_memberships.jsonl",
        "source_id": _pm["membership_id"],
        "continuum_id": _pm["continuum_project_member_id"],
        "target_service": "iam",
        "target_collection": "project_members+project_member_roles",
        "organization_id": member_by_id[_pm["member_id"]]["org_id"],
        "project_id": _pm["project_id"],
        "continuum_role": _pm["continuum_role_code"],
        "import_eligible": _pm["continuum_import_eligible"],
        "support_status": "API_SUPPORTED" if (_pm["continuum_import_eligible"] and _pm["continuum_membership_status"] == "ACTIVE") else ("IMPORTER_REQUIRED" if _pm["continuum_import_eligible"] else "DATASET_METADATA_ONLY"),
        "notes": f"status={_pm['continuum_membership_status']}",
    })
for _sp in sprints:
    continuum_id_mappings.append({
        "mapping_id": f"MAP-SPR-{_sp['sprint_id']}",
        "entity_kind": "sprint",
        "source_file": "structured/sprints.jsonl",
        "source_id": _sp["sprint_id"],
        "continuum_id": _sp["continuum_sprint_id"],
        "target_service": "task",
        "target_collection": "sprints",
        "organization_id": "ORG-NSC",
        "project_id": _sp["project_id"],
        "import_eligible": True,
        "support_status": "IMPORTER_REQUIRED",
        "notes": f"status={_sp['continuum_status']} ({_sp['start_date']}..{_sp['end_date']})",
    })
for _t in work_tasks:
    continuum_id_mappings.append({
        "mapping_id": f"MAP-TSK-{_t['key']}",
        "entity_kind": "work_task",
        "source_file": "structured/work_tasks.jsonl",
        "source_id": _t["task_id"],
        "continuum_id": _t["task_id"],
        "continuum_code": _t["key"],
        "target_service": "task",
        "target_collection": "tasks+steps+worklogs+comments+task_events",
        "organization_id": "ORG-NSC",
        "project_id": _t["project_id"],
        "import_eligible": True,
        "support_status": "IMPORTER_REQUIRED",
        "notes": f"source_issue_key={_t['source_issue_key']} status={_t['status']}",
    })
for _n in task_notes:
    continuum_id_mappings.append({
        "mapping_id": f"MAP-TNT-{_n['note_id']}",
        "entity_kind": "task_note",
        "source_file": "structured/task_notes.jsonl",
        "source_id": _n["note_id"],
        "continuum_id": _n["note_id"],
        "target_service": "capture",
        "target_collection": "work_notes",
        "organization_id": "ORG-NSC",
        "project_id": _n["project_id"],
        "import_eligible": True,
        "support_status": "IMPORTER_REQUIRED",
        "notes": "noteType=TASK_NOTE status=CONFIRMED knowledge_eligible=false",
    })
_reviewed_doc_ids = {ev["document_id"] for ev in document_reviews}
for _d in canonical_documents:
    if _d["document_id"] in _reviewed_doc_ids and not _d.get("test_only"):
        continuum_id_mappings.append({
            "mapping_id": f"MAP-DOC-{_d['document_id']}",
            "entity_kind": "project_document",
            "source_file": "structured/documents.jsonl",
            "source_id": _d["document_id"],
            "continuum_id": stable_id("project-document", _d["document_id"]),
            "target_service": "capture",
            "target_collection": "work_notes+work_note_versions",
            "organization_id": _d["organization_id"],
            "project_id": _d["project_id"],
            "import_eligible": True,
            "support_status": "IMPORTER_REQUIRED",
            "notes": f"noteType=PROJECT_DOCUMENT status={_d['status']} version={_d['version']}",
        })
for _r in work_reports:
    continuum_id_mappings.append({
        "mapping_id": f"MAP-RPT-{_r['report_id']}",
        "entity_kind": "work_report",
        "source_file": "structured/work_reports.jsonl",
        "source_id": _r["report_id"],
        "continuum_id": _r["report_id"],
        "target_service": "capture",
        "target_collection": "work_notes+work_note_versions",
        "organization_id": "ORG-NSC",
        "project_id": _r["project_id"],
        "import_eligible": True,
        "support_status": "IMPORTER_REQUIRED",
        "notes": f"noteType=WORK_REPORT scope={_r['report_scope']} type={_r['report_type']} status={_r['status']}",
    })

write_jsonl("structured/documents.jsonl", canonical_documents)
write_jsonl("structured/work_tasks.jsonl", work_tasks)
write_jsonl("structured/task_notes.jsonl", task_notes)
write_jsonl("structured/document_reviews.jsonl", document_reviews)
write_jsonl("structured/work_reports.jsonl", work_reports)
write_jsonl("structured/continuum_id_mapping.jsonl", continuum_id_mappings)
print("Wrote all structured entities, Continuum ID mappings, requirements, functional tests, and execution results.")

# -------------------------------------------------------------
# 11. Dataset/RAG Evaluation Test Suites (158 cases)
# -------------------------------------------------------------
# Dynamically computed metric values:
total_done_issues = sum(1 for i in issues if i["status"] == "Done")
blocked_projects = sorted(list(set(i["project_id"] for i in issues if i["status"] == "Blocked")))
total_blocked_issues = sum(1 for i in issues if i["status"] == "Blocked")
total_overdue_open_issues = sum(1 for i in issues if i["status"] != "Done" and i["due_date"] < TODAY.isoformat())
pay_active_wip_pts = sum(i["story_points"] for i in issues if i["project_id"] == "NSC-PAY" and i["sprint_id"] == "SPRINT-PAY-13" and i["status"] in ["In Progress", "In Review"])
chko_active_wip_pts = sum(i["story_points"] for i in issues if i["project_id"] == "NSC-CHKO" and i["sprint_id"] == "SPRINT-CHKO-13" and i["status"] in ["In Progress", "In Review"])
unique_bundle_files_count = len(set(d["file_path"] for d in canonical_documents if d["format"] == "markdown_bundle"))
total_overtime_issues = sum(1 for i in issues if i.get("is_overtime"))
total_spillover_issues = sum(
    1 for i in issues
    if i["status"] != "Done" and i["sprint_id"].endswith("-13") and i.get("spillover_count", 0) > 0
)
total_bot_comments = sum(1 for c in comments if c.get("actor_type") == "system_bot")
total_weekend_ot_changelog = sum(1 for ch in changelog if ch.get("work_mode") == "weekend_incident_ot")

rag_cases = [
    {"case_id": "RAG-001", "query": "How long must checkout idempotency keys be retained?", "expected": "At least 72 hours; the same key and request hash returns the original cached result.", "gold_document_ids": ["DOC-PAY-ADR-003", "DOC-ARCH-PLAT-001"], "must_not_cite": ["DOC-PAY-ADR-001"], "tags": ["latest_version", "conflict", "citation"]},
    {"case_id": "RAG-002", "query": "What is the current refund window for Meridian Outfitters?", "expected": "A return request may be opened within 30 calendar days of delivery, subject to warehouse inspection.", "gold_document_ids": ["DOC-ORD-POL-005"], "must_not_cite": ["DOC-PAY-ADR-001"], "tags": ["conflict", "current_policy"]},
    {"case_id": "RAG-003", "query": "How are repeated payment webhooks handled after a worker restart?", "expected": "Verify provider event ID in unique inbox within an atomic transaction; acknowledge replay without repeating side effects.", "gold_document_ids": ["DOC-PAY-ADR-003", "DOC-PAY-RCA-006"], "must_not_cite": ["DOC-PAY-ADR-001"], "tags": ["multi_document", "incident", "deduplication"]},
    {"case_id": "RAG-004", "query": "What does the checkout order submission endpoint return after a provider timeout?", "expected": "HTTP 202 Accepted with pending reconciliation reference; do not spawn a new session for uncertain retry.", "gold_document_ids": ["DOC-CHKO-API-002"], "must_not_cite": [], "tags": ["docx_table", "api_contract"]},
    {"case_id": "RAG-005", "query": "Can product catalog copy be automatically translated in v1?", "expected": "Automated machine translation of catalog copy is not approved in the v1 PRD.", "gold_document_ids": ["DOC-CAT-PRD-004"], "must_not_cite": [], "tags": ["answerability", "calibrated_abstention"]},
    {"case_id": "RAG-006", "query": "What sample catalog size and delivery date did Meridian agree to?", "expected": "A 2,000-row sample catalog file by 14 October 2026.", "gold_document_ids": ["DOC-ORG-MEETING-2026-10-09"], "must_not_cite": [], "tags": ["cross_document", "date"]},
    {"case_id": "RAG-007", "query": "List Meridian Outfitters approved internal search synonyms.", "expected": "Specific synonym dictionary entries are not detailed in the general strategy; abstain from fabricating values.", "gold_document_ids": ["DOC-SRCH-STRATEGY-003"], "must_not_cite": [], "tags": ["missing_detail", "calibrated_abstention"]},
    {"case_id": "RAG-008", "query": "What is the critical rollback threshold for checkout 5xx errors?", "expected": "Checkout HTTP 5xx rate exceeding 1.5% over a 5-minute rolling window triggers immediate rollback.", "gold_document_ids": ["DOC-REL-RUN-009"], "must_not_cite": [], "tags": ["runbook", "threshold"]},
    {"case_id": "RAG-009", "query": "How is Available to Promise (ATP) stock calculated?", "expected": "ATP = Physical On-Hand - Allocated Reserves - Safety Buffer.", "gold_document_ids": ["DOC-INV-STD-003"], "must_not_cite": [], "tags": ["formula", "inventory"]},
    {"case_id": "RAG-010", "query": "When is customer self-service order cancellation prohibited?", "expected": "Once an order enters PACKED state, customer cancellation is disabled and returns must be used.", "gold_document_ids": ["DOC-ORD-SOP-004"], "must_not_cite": [], "tags": ["state_machine", "order_lifecycle"]},
    {"case_id": "RAG-011", "query": "What is the default evaluation priority order for promotion rules in cart?", "expected": "Catalog Price Rules -> Item Tier Discounts -> Cart Order Coupons -> Free Shipping.", "gold_document_ids": ["DOC-CART-SPEC-005"], "must_not_cite": [], "tags": ["promotion", "cart_rules"]},
    {"case_id": "RAG-012", "query": "How is Gross Merchandise Value (GMV) defined in analytics?", "expected": "Sum of all captured order totals excluding refunded or voided transactions.", "gold_document_ids": ["DOC-DATA-DICT-008"], "must_not_cite": [], "tags": ["analytics_metric", "data_dictionary"]},
    {"case_id": "RAG-013", "query": "What is the maximum retry window and attempt count for transient payment provider errors?", "expected": "Maximum 5 retry attempts over 20 minutes with exponential backoff and full jitter.", "gold_document_ids": ["DOC-PAY-ADR-003"], "must_not_cite": ["DOC-PAY-ADR-001"], "tags": ["retry_policy", "payments"]},
    {"case_id": "RAG-014", "query": "What header must PulsePay include to verify webhook signature authenticity?", "expected": "X-PulsePay-Signature containing HMAC-SHA256 signature.", "gold_document_ids": ["DOC-INT-PULSEPAY-002"], "must_not_cite": [], "tags": ["security", "webhook"]},
    {"case_id": "RAG-015", "query": "What was the root cause of false-positive HTTP 409 idempotency conflict errors in checkout?", "expected": "Floating point rounding discrepancies in cart tax totals prior to payload hashing; resolved by using integer minor currency units.", "gold_document_ids": ["DOC-CHKO-RCA-008"], "must_not_cite": [], "tags": ["incident_rca", "idempotency"]},
    {"case_id": "RAG-016", "query": "What are the required CSV columns for bulk catalog upload?", "expected": "merchant_sku, product_name, currency, category, and price.", "gold_document_ids": ["DOC-CAT-PRD-004"], "must_not_cite": [], "tags": ["catalog", "import_spec"]},
    {"case_id": "RAG-017", "query": "Can search synonym expansions cross merchant tenant boundaries?", "expected": "No, synonym expansions operate strictly within merchant tenant boundaries and must never cross tenants.", "gold_document_ids": ["DOC-SRCH-STRATEGY-003", "DOC-SRCH-STD-005"], "must_not_cite": [], "tags": ["multi_tenant", "search_isolation"]},
    {"case_id": "RAG-018", "query": "What is the retention period for fact_orders table in analytics?", "expected": "7 years for regulatory compliance.", "gold_document_ids": ["DOC-DATA-DICT-008"], "must_not_cite": [], "tags": ["retention", "compliance"]},
    {"case_id": "RAG-019", "query": "What happens if a checkout session tax quote times out?", "expected": "System transitions to graceful fallback mode using fallback shipping and tax configuration.", "gold_document_ids": ["DOC-CHKO-API-002"], "must_not_cite": [], "tags": ["api_error", "fallback"]},
    {"case_id": "RAG-020", "query": "How long are inventory holds reserved during active checkout sessions?", "expected": "Durable 15-minute TTL during active checkout session.", "gold_document_ids": ["DOC-INV-STD-003"], "must_not_cite": [], "tags": ["ttl", "inventory_reservation"]},
    {"case_id": "RAG-021", "query": "Who is the executive sponsor for Northstar Commerce Systems?", "expected": "Avery Chen (M-001), Executive Sponsor.", "gold_document_ids": ["DOC-ORG-CHARTER-001"], "must_not_cite": [], "tags": ["leadership", "charter"]},
    {"case_id": "RAG-022", "query": "What database partitioning strategy is adopted for zero-downtime multi-tenant tables?", "expected": "Expand/contract pattern adding nullable columns or safe defaults before application deployment.", "gold_document_ids": ["DOC-PLAT-MIG-010"], "must_not_cite": [], "tags": ["database", "migrations"]},
    {"case_id": "RAG-023", "query": "What is the maximum allowed search latency p95 under launch SLA?", "expected": "Strictly below 300ms at 100 queries per second for a 50,000-SKU index.", "gold_document_ids": ["DOC-SRCH-STRATEGY-003", "DOC-ORG-CHARTER-001"], "must_not_cite": [], "tags": ["sla", "latency"]},
    {"case_id": "RAG-024", "query": "What is the policy regarding storing credit card PAN or CVV in Northstar systems?", "expected": "Strictly prohibited; only provider tokens, authorization codes, and minimal transaction metadata may be stored.", "gold_document_ids": ["DOC-PAY-ADR-003", "DOC-SEC-CLASS-002"], "must_not_cite": [], "tags": ["security", "pci_dss"]},
    {"case_id": "RAG-025", "query": "How does the checkout endpoint handle identical idempotency key with different payload body?", "expected": "Returns HTTP 409 IDEMPOTENCY_CONFLICT with structured error details.", "gold_document_ids": ["DOC-CHKO-API-002", "DOC-PAY-ADR-003"], "must_not_cite": [], "tags": ["api_contract", "conflict"]},
    {"case_id": "RAG-026", "query": "What carrier events transition an order to DELIVERED?", "expected": "Logistics carrier shipment status tracking webhook events ingested via webhook.", "gold_document_ids": ["DOC-ORD-SOP-004"], "must_not_cite": [], "tags": ["logistics", "tracking"]},
    {"case_id": "RAG-027", "query": "What is the canary deployment traffic rollout progression for Meridian Outfitters?", "expected": "Internal synthetic test merchants at 0% for 30 min, then Meridian at 5%, 25%, 50%, and 100% over 2 hours.", "gold_document_ids": ["DOC-REL-RUN-009"], "must_not_cite": [], "tags": ["canary", "release"]},
    {"case_id": "RAG-028", "query": "What data classification tier is assigned to security RCAs and vulnerability reports?", "expected": "Level 3 - Restricted, accessible only to GRP-SECURITY and GRP-LEADERS.", "gold_document_ids": ["DOC-SEC-CLASS-002"], "must_not_cite": [], "tags": ["acl", "security_tier"]},
    {"case_id": "RAG-029", "query": "What is the default TTL for anonymous guest carts?", "expected": "Anonymous carts expire after 7 days of inactivity; authenticated customer carts persist for 30 days.", "gold_document_ids": ["DOC-CART-SPEC-005"], "must_not_cite": [], "tags": ["cart", "ttl"]},
    {"case_id": "RAG-030", "query": "What date is set for the final release readiness review in October 2026?", "expected": "16 October 2026.", "gold_document_ids": ["DOC-ORG-MEETING-2026-10-09"], "must_not_cite": [], "tags": ["milestone", "release_date"]},
    {"case_id": "RAG-031", "query": "What are the working hours, lunch break, and overtime window for Northstar engineering teams?", "expected": "Regular hours are 08:00-17:00 ICT (UTC+07:00) with a mandatory 12:00-13:00 lunch break; evening overtime is permitted strictly between 17:00 and 22:00 ICT.", "gold_document_ids": ["DOC-PMP-001", "DOC-OPS-RUNBOOK-001"], "must_not_cite": [], "tags": ["working_hours", "overtime", "vietnam_tz"]},
    {"case_id": "RAG-032", "query": "Which Vietnam public holidays are observed as non-working days during the 2026 project timeline?", "expected": "2026-04-27 (Hung Kings compensatory holiday), 2026-04-30 (Reunification Day), 2026-05-01 (International Labor Day), and 2026-09-01 to 2026-09-02 (National Day holiday window).", "gold_document_ids": ["DOC-PMP-001"], "must_not_cite": [], "tags": ["holidays", "calendar", "vietnam_tz"]},
    {"case_id": "RAG-033", "query": "What automated jobs or bots continue operating during weekends and Vietnam public holidays?", "expected": "Nightly SFTP catalog sync (02:00 ICT), inventory hold expiry sweeper (03:30 ICT), CI/CD regression runner, and Prometheus alert manager run 24/7 while human staff are off except for P0/P1 emergency war-rooms.", "gold_document_ids": ["DOC-OPS-RUNBOOK-001"], "must_not_cite": [], "tags": ["bots", "24x7_ops", "oncall"]},
    {"case_id": "RAG-034", "query": "Why is test case FT-CHKO-007 currently blocked before launch?", "expected": "Blocked by active Highest-priority defect CHKO-005 where downstream tax service timeout stalls fallback shipping/tax transition.", "gold_document_ids": ["DOC-QA-REPORT-001", "DOC-CHKO-API-002"], "must_not_cite": [], "tags": ["traceability", "blocked_defect", "uat"]}
]

acl_cases = [
    {"case_id": "ACL-001", "principal_id": "M-003", "resource_id": "DOC-CAT-PRD-004", "expected_decision": "allow", "reason": "M-003 is an active member of GRP-CATALOG."},
    {"case_id": "ACL-002", "principal_id": "M-016", "resource_id": "DOC-SEC-CLASS-002", "expected_decision": "deny", "reason": "M-016 belongs to Meridian and lacks GRP-SECURITY or GRP-LEADERS access."},
    {"case_id": "ACL-003", "principal_id": "M-018", "resource_id": "DOC-CAT-PRD-004", "expected_decision": "deny", "reason": "Former employee M-018 left on 2026-09-15; all group memberships are revoked."},
    {"case_id": "ACL-004", "principal_id": "M-016", "resource_id": "DOC-CHKO-API-002", "expected_decision": "allow", "reason": "Checkout API contract is explicitly shared with GRP-MERIDIAN."},
    {"case_id": "ACL-005", "principal_id": "M-017", "resource_id": "DOC-PAY-ADR-003", "expected_decision": "allow", "reason": "Active PulsePay member M-017 has explicit access via GRP-PULSEPAY."},
    {"case_id": "ACL-006", "principal_id": "M-017", "resource_id": "DOC-ORD-POL-005", "expected_decision": "deny", "reason": "PulsePay integration staff do not have access to Meridian refund policy."},
    {"case_id": "ACL-007", "principal_id": "M-009", "resource_id": "DOC-SEC-CLASS-002", "expected_decision": "deny", "reason": "Platform engineer M-009 is not in GRP-SECURITY or GRP-LEADERS."},
    {"case_id": "ACL-008", "principal_id": "M-012", "resource_id": "DOC-SEC-CLASS-002", "expected_decision": "allow", "reason": "Principal Security Engineer M-012 is an active member of GRP-SECURITY."},
    {"case_id": "ACL-009", "principal_id": "M-045", "resource_id": "DOC-SRCH-STRATEGY-003", "expected_decision": "deny", "reason": "Former search engineer M-045 left on 2026-08-01; membership is revoked."},
    {"case_id": "ACL-010", "principal_id": "M-070", "resource_id": "DOC-PAY-ADR-003", "expected_decision": "deny", "reason": "Former PulsePay engineer M-070 left on 2026-07-15; partner membership revoked."},
    {"case_id": "ACL-011", "principal_id": "M-064", "resource_id": "DOC-INT-MERIDIAN-001", "expected_decision": "allow", "reason": "Active Meridian merchandiser M-064 has access via GRP-MERIDIAN."},
    {"case_id": "ACL-012", "principal_id": "M-064", "resource_id": "DOC-INT-PULSEPAY-002", "expected_decision": "deny", "reason": "Meridian customer staff cannot view PulsePay partner webhook internal spec."},
    {"case_id": "ACL-013", "principal_id": "M-071", "resource_id": "DOC-INT-PULSEPAY-002", "expected_decision": "allow", "reason": "PulsePay Lead Settlement Engineer M-071 has access via GRP-PULSEPAY."},
    {"case_id": "ACL-014", "principal_id": "M-001", "resource_id": "DOC-SEC-CLASS-002", "expected_decision": "allow", "reason": "Executive Sponsor M-001 is a member of GRP-LEADERS."},
    {"case_id": "ACL-015", "principal_id": "M-020", "resource_id": "DOC-CAT-PRD-004", "expected_decision": "allow", "reason": "Catalog engineer M-020 belongs to GRP-CATALOG."},
    {"case_id": "ACL-016", "principal_id": "M-022", "resource_id": "DOC-CAT-PRD-004", "expected_decision": "deny", "reason": "Search engineer M-022 does not belong to GRP-CATALOG."},
    {"case_id": "ACL-017", "principal_id": "M-025", "resource_id": "DOC-CHKO-RCA-008", "expected_decision": "allow", "reason": "Checkout engineer M-025 belongs to GRP-CHECKOUT."},
    {"case_id": "ACL-018", "principal_id": "M-035", "resource_id": "DOC-PLAT-MIG-010", "expected_decision": "allow", "reason": "Database administrator M-035 belongs to GRP-PLATFORM."},
    {"case_id": "ACL-019", "principal_id": "M-063", "resource_id": "DOC-ORD-POL-005", "expected_decision": "allow", "reason": "Meridian E-Commerce Director M-063 belongs to GRP-MERIDIAN."},
    {"case_id": "ACL-020", "principal_id": "M-073", "resource_id": "DOC-PAY-RCA-006", "expected_decision": "deny", "reason": "PulsePay SRE M-073 does not belong to Northstar internal GRP-SECURITY or GRP-CHECKOUT."},
    {"case_id": "ACL-021", "principal_id": "M-011", "resource_id": "DOC-DATA-DICT-008", "expected_decision": "allow", "reason": "Data Lead M-011 belongs to GRP-DATA."},
    {"case_id": "ACL-022", "principal_id": "M-014", "resource_id": "DOC-ORG-CHARTER-001", "expected_decision": "allow", "reason": "Product designer M-014 belongs to GRP-ALL-STAFF."},
    {"case_id": "ACL-023", "principal_id": "M-016", "resource_id": "DOC-ORG-CHARTER-001", "expected_decision": "deny", "reason": "Meridian user M-016 is external and does not belong to GRP-ALL-STAFF."},
    {"case_id": "ACL-024", "principal_id": "M-017", "resource_id": "DOC-ORG-CHARTER-001", "expected_decision": "deny", "reason": "PulsePay partner M-017 does not belong to Northstar internal employee group."},
    {"case_id": "ACL-025", "principal_id": "M-053", "resource_id": "DOC-ORD-POL-005", "expected_decision": "allow", "reason": "Support engineer M-053 belongs to GRP-ALL-STAFF."},
    {"case_id": "ACL-026", "principal_id": "M-022", "resource_id": "DOC-SRCH-ANNEX-001", "expected_decision": "allow", "reason": "Search engineer M-022 is assigned to the Search project group GRP-SEARCH and can access its project annex."},
    {"case_id": "ACL-027", "principal_id": "M-016", "resource_id": "DOC-CHKO-RCA-008", "expected_decision": "deny", "reason": "External Meridian user M-016 is an external collaborator and never inherits internal GRP-CHECKOUT access to internal RCAs."},
    {"case_id": "ACL-028", "principal_id": "M-017", "resource_id": "DOC-PAY-ANNEX-001", "expected_decision": "deny", "reason": "External PulsePay partner M-017 does not inherit internal GRP-CHECKOUT access to Payment internal annexes."},
    {"case_id": "ACL-029", "principal_id": "M-064", "resource_id": "DOC-CAT-ANNEX-001", "expected_decision": "deny", "reason": "Meridian merchandiser M-064 is scoped to GRP-MERIDIAN and cannot read internal GRP-CATALOG project annexes."},
    {"case_id": "ACL-030", "principal_id": "M-042", "resource_id": "DOC-DATA-DICT-008", "expected_decision": "allow", "reason": "Senior Analytics Developer M-042 is an active member of GRP-DATA and GRP-PLATFORM."}
]

analytics_cases = [
    {"case_id": "ANA-001", "question": "How many Jira issues are in Done status across all projects?", "metric": "issue_count_by_status", "filters": {"status": "Done"}, "expected_value": total_done_issues, "expected_unit": "issues"},
    {"case_id": "ANA-002", "question": "Which projects currently contain blocked issues?", "metric": "blocked_projects_list", "filters": {"status": "Blocked"}, "expected_value": blocked_projects, "expected_unit": "project_ids"},
    {"case_id": "ANA-003", "question": "How many projects have At Risk status?", "metric": "project_count_by_status", "filters": {"status": "At Risk"}, "expected_value": 2, "expected_unit": "projects"},
    {"case_id": "ANA-004", "question": "How many active Northstar employees are in the system?", "metric": "active_member_count_by_org", "filters": {"org_id": "ORG-NSC", "account_status": "active"}, "expected_value": 58, "expected_unit": "members"},
    {"case_id": "ANA-005", "question": "What is the total number of customer and partner profiles?", "metric": "external_member_count", "filters": {"org_types": ["customer_merchant", "integration_partner"]}, "expected_value": 14, "expected_unit": "members"},
    {"case_id": "ANA-006", "question": "How many total Jira issues are registered in project NSC-PAY?", "metric": "project_issue_count", "filters": {"project_id": "NSC-PAY"}, "expected_value": 313, "expected_unit": "issues"},
    {"case_id": "ANA-007", "question": "How many total logical documents are tracked in the catalog?", "metric": "total_logical_documents", "filters": {}, "expected_value": len(canonical_documents), "expected_unit": "logical_documents"},
    {"case_id": "ANA-008", "question": "How many physical Markdown bundle files exist for project updates?", "metric": "bundle_file_count", "filters": {"format": "markdown_bundle"}, "expected_value": unique_bundle_files_count, "expected_unit": "physical_files"},
    {"case_id": "ANA-009", "question": "How many total Jira issues are assigned to former employee M-018?", "metric": "former_member_assigned_issues", "filters": {"assignee_id": "M-018"}, "expected_value": sum(1 for i in issues if i["assignee_id"] == "M-018"), "expected_unit": "issues"},
    {"case_id": "ANA-010", "question": "What is the distribution of issue priorities across the company?", "metric": "issue_count_by_priority", "filters": {}, "expected_value": {p: sum(1 for i in issues if i["priority"] == p) for p in ["Highest", "High", "Medium", "Low"]}, "expected_unit": "issue_priority_map"},
    {"case_id": "ANA-011", "question": "How many issues are in In Progress status?", "metric": "issue_count_by_status", "filters": {"status": "In Progress"}, "expected_value": sum(1 for i in issues if i["status"] == "In Progress"), "expected_unit": "issues"},
    {"case_id": "ANA-012", "question": "How many issues are in In Review status?", "metric": "issue_count_by_status", "filters": {"status": "In Review"}, "expected_value": sum(1 for i in issues if i["status"] == "In Review"), "expected_unit": "issues"},
    {"case_id": "ANA-013", "question": "How many issues are in To Do status?", "metric": "issue_count_by_status", "filters": {"status": "To Do"}, "expected_value": sum(1 for i in issues if i["status"] == "To Do"), "expected_unit": "issues"},
    {"case_id": "ANA-014", "question": "How many total departments exist across the 3 organizations?", "metric": "department_count", "filters": {}, "expected_value": 10, "expected_unit": "departments"},
    {"case_id": "ANA-015", "question": "How many standalone canonical DOCX source documents are indexed, excluding linked renditions?", "metric": "canonical_docx_document_count", "filters": {"format": "docx", "document_role": "canonical"}, "expected_value": len(docx_specs), "expected_unit": "logical_documents"},
    {"case_id": "ANA-016", "question": "How many Jira issues involved evening or weekend overtime (is_overtime = true)?", "metric": "overtime_issue_count", "filters": {"is_overtime": True}, "expected_value": total_overtime_issues, "expected_unit": "issues"},
    {"case_id": "ANA-017", "question": "How many official working days (excluding weekends and 5 Vietnam public holidays) occur in the 180-day window?", "metric": "official_working_days_count", "filters": {"timezone": "+07:00"}, "expected_value": TOTAL_WORKING_DAYS, "expected_unit": "working_days"},
    {"case_id": "ANA-018", "question": "How many automated system bot comments were recorded across all issues?", "metric": "system_bot_comment_count", "filters": {"actor_type": "system_bot"}, "expected_value": total_bot_comments, "expected_unit": "comments"},
    {"case_id": "ANA-019", "question": "How many open issues spilled over from earlier closed sprints into active Sprint 13?", "metric": "sprint_spillover_issue_count", "filters": {"status_ne": "Done", "sprint_number": 13, "spillover_count_gt": 0}, "expected_value": total_spillover_issues, "expected_unit": "issues"},
    {"case_id": "ANA-020", "question": "How many weekend emergency war-room changelog events occurred across the entire timeline?", "metric": "weekend_incident_ot_changelog_count", "filters": {"work_mode": "weekend_incident_ot"}, "expected_value": total_weekend_ot_changelog, "expected_unit": "changelog_entries"}
]

progress_cases = [
    {"case_id": "PRG-001", "project_id": "NSC-PAY", "metric": "blocked_issue_count", "expected_value": sum(1 for i in issues if i["project_id"] == "NSC-PAY" and i["status"] == "Blocked"), "expected_unit": "issues", "note": "Blocked issues in payment orchestration."},
    {"case_id": "PRG-002", "project_id": "NSC-CHKO", "metric": "completion_ratio", "expected_value": round(sum(1 for i in issues if i["project_id"] == "NSC-CHKO" and i["status"] == "Done") / 313, 3), "expected_unit": "ratio", "note": "Completion ratio calculated as Done / Total."},
    {"case_id": "PRG-003", "project_id": "NSC-PAY", "metric": "overdue_open_issue_count", "expected_value": sum(1 for i in issues if i["project_id"] == "NSC-PAY" and i["status"] != "Done" and i["due_date"] < TODAY.isoformat()), "expected_unit": "issues", "note": "Open issues past due date at snapshot date."},
    {"case_id": "PRG-004", "project_id": "NSC-CAT", "metric": "done_issue_count", "expected_value": sum(1 for i in issues if i["project_id"] == "NSC-CAT" and i["status"] == "Done"), "expected_unit": "issues", "note": "Done issues in Catalog project."},
    {"case_id": "PRG-005", "project_id": "ALL", "metric": "total_blocked_issues", "expected_value": total_blocked_issues, "expected_unit": "issues", "note": "Total blocked issues across all 8 projects."},
    {"case_id": "PRG-006", "project_id": "NSC-SRCH", "metric": "completion_ratio", "expected_value": round(sum(1 for i in issues if i["project_id"] == "NSC-SRCH" and i["status"] == "Done") / 313, 3), "expected_unit": "ratio", "note": "Search & Discovery completion ratio."},
    {"case_id": "PRG-007", "project_id": "NSC-CART", "metric": "completion_ratio", "expected_value": round(sum(1 for i in issues if i["project_id"] == "NSC-CART" and i["status"] == "Done") / 312, 3), "expected_unit": "ratio", "note": "Cart & Promotions completion ratio."},
    {"case_id": "PRG-008", "project_id": "NSC-INV", "metric": "completion_ratio", "expected_value": round(sum(1 for i in issues if i["project_id"] == "NSC-INV" and i["status"] == "Done") / 312, 3), "expected_unit": "ratio", "note": "Inventory completion ratio."},
    {"case_id": "PRG-009", "project_id": "NSC-ORD", "metric": "completion_ratio", "expected_value": round(sum(1 for i in issues if i["project_id"] == "NSC-ORD" and i["status"] == "Done") / 312, 3), "expected_unit": "ratio", "note": "Orders completion ratio."},
    {"case_id": "PRG-010", "project_id": "NSC-PLAT", "metric": "completion_ratio", "expected_value": round(sum(1 for i in issues if i["project_id"] == "NSC-PLAT" and i["status"] == "Done") / 312, 3), "expected_unit": "ratio", "note": "Platform completion ratio."},
    {"case_id": "PRG-011", "project_id": "NSC-PAY", "metric": "active_sprint_wip_points", "expected_value": pay_active_wip_pts, "expected_unit": "story_points", "note": "WIP story points in active Sprint 13 for Payment (In Progress + In Review)."},
    {"case_id": "PRG-012", "project_id": "NSC-CHKO", "metric": "active_sprint_wip_points", "expected_value": chko_active_wip_pts, "expected_unit": "story_points", "note": "WIP story points in active Sprint 13 for Checkout (In Progress + In Review)."},
    {"case_id": "PRG-013", "project_id": "ALL", "metric": "stale_project_detection_7d", "expected_value": [], "expected_unit": "project_ids", "note": "Projects without updates within 7 calendar days before 2026-10-12 (all 8 projects have active updates on 2026-10-12)."},
    {"case_id": "PRG-014", "project_id": "NSC-PAY", "metric": "target_launch_date", "expected_value": "2026-10-23", "expected_unit": "date", "note": "Payment milestone target date."},
    {"case_id": "PRG-015", "project_id": "NSC-PLAT", "metric": "target_launch_date", "expected_value": "2026-12-04", "expected_unit": "date", "note": "Platform foundation target date."},
    {"case_id": "PRG-016", "project_id": "NSC-CHKO", "metric": "overtime_hours_sum", "expected_value": round(sum(i.get("overtime_hours", 0.0) for i in issues if i["project_id"] == "NSC-CHKO"), 1), "expected_unit": "hours", "note": "Total logged overtime hours in At-Risk Checkout project (17:00-22:00 ICT)."},
    {"case_id": "PRG-017", "project_id": "NSC-PAY", "metric": "overtime_hours_sum", "expected_value": round(sum(i.get("overtime_hours", 0.0) for i in issues if i["project_id"] == "NSC-PAY"), 1), "expected_unit": "hours", "note": "Total logged overtime hours in At-Risk Payment project (17:00-22:00 ICT)."},
    {"case_id": "PRG-018", "project_id": "NSC-PAY", "metric": "spillover_issue_count", "expected_value": sum(1 for i in issues if i["project_id"] == "NSC-PAY" and i["status"] != "Done" and i["sprint_id"].endswith("-13") and i.get("spillover_count", 0) > 0), "expected_unit": "issues", "note": "Open issues carried over from closed Sprints 1..12 into active Sprint 13 in NSC-PAY."},
    {"case_id": "PRG-019", "project_id": "ALL", "metric": "open_issues_in_closed_sprints", "expected_value": sum(1 for i in issues if i["status"] != "Done" and not i["sprint_id"].endswith("-13")), "expected_unit": "issues", "note": "Zero open issues remain in closed Sprints 1..12 after Agile sprint rollover."}
]

ingestion_cases = [
    {"case_id": "ING-001", "scenario": "Ingest exact duplicate Markdown file upload.", "expected": "Detect identical content_sha256; link duplicate to canonical record without indexing duplicate vector chunks.", "fixture": "fixtures/duplicate_upload.md", "tags": ["duplicate", "sha256"]},
    {"case_id": "ING-002", "scenario": "Ingest superseded ADR-001 alongside active ADR-003.", "expected": "Retain ADR-001 for historical lineage; rank ADR-003 as current authoritative guidance.", "fixture": "structured/documents.jsonl", "tags": ["versioning", "supersedes"]},
    {"case_id": "ING-003", "scenario": "Ingest scratch document lacking document_id, owner, project, or classification.", "expected": "Quarantine document immediately; exclude from default search index and trigger metadata alert.", "fixture": "fixtures/missing_metadata.md", "tags": ["missing_metadata", "quarantine"]},
    {"case_id": "ING-004", "scenario": "Ingest document containing broken URL reference to missing runbook.", "expected": "Flag unresolved reference while preserving raw markdown link; do not hallucinate target content.", "fixture": "fixtures/broken_link.md", "tags": ["broken_link", "referential_integrity"]},
    {"case_id": "ING-005", "scenario": "Extract table cells, headers, and footers from DOCX API contract.", "expected": "Extract title, metadata table, paragraph sections, endpoint tables, and footer metadata with source attribution.", "fixture": "documents/docx/Checkout_API_Contract.docx", "tags": ["docx_extraction", "table", "footer"]},
    {"case_id": "ING-006", "scenario": "Ingest raw CSV attachment containing payment webhook event samples.", "expected": "Record attachment metadata, parse structured CSV headers, and associate with parent incident record.", "fixture": "fixtures/attachments/payment_webhook_sample.csv", "tags": ["csv_attachment", "format_boundary"]},
    {"case_id": "ING-007", "scenario": "Historical Jira issue assigned to inactive member M-018.", "expected": "Preserve historical authorship attribution in changelogs; reject active authentication and current ACL permissions.", "fixture": "structured/issues.jsonl", "tags": ["former_member", "audit_trail"]},
    {"case_id": "ING-008", "scenario": "Document references Jira key NONEXISTENT-999 absent from issue registry.", "expected": "Flag unresolved orphan reference and log validation warning without failing batch ingestion.", "fixture": "fixtures/orphan_issue_reference.md", "tags": ["orphan_jira_key", "referential_integrity"]},
    {"case_id": "ING-009", "scenario": "Draft document updated timestamp is newer than latest approved major version.", "expected": "Evaluate explicit version lineage and approval status rather than raw timestamp alone.", "fixture": "fixtures/conflicting_timestamp.md", "tags": ["version_lineage", "timestamp_conflict"]},
    {"case_id": "ING-010", "scenario": "Ingest monthly Markdown bundle containing multiple section anchors.", "expected": "Parse bundle into distinct logical documents using header anchors; verify section-level sha256 checksums.", "fixture": "documents/markdown/bundles/NSC-CAT-2026-04.md", "tags": ["bundled_markdown", "section_anchor"]},
    {"case_id": "ING-011", "scenario": "Ingest DOCX document with complex multi-column metadata header table.", "expected": "Correctly map Document ID, Owner, Version, Status, and Access Groups into document registry fields.", "fixture": "documents/docx/Platform_Architecture_Overview.docx", "tags": ["docx_metadata", "table_parser"]},
    {"case_id": "ING-012", "scenario": "Ingest document with Customer Restricted classification.", "expected": "Enforce strict tenant boundary check; ensure search index marks chunk as restricted to GRP-MERIDIAN.", "fixture": "documents/markdown/formal/Merchant_Integration_Guide_Meridian.md", "tags": ["acl_classification", "tenant_isolation"]},
    {"case_id": "ING-013", "scenario": "Validate UTF-8 encoding across all structured JSONL records.", "expected": "All lines parse as valid UTF-8 JSON objects without unescaped control characters.", "fixture": "structured/members.jsonl", "tags": ["encoding", "jsonl_schema"]},
    {"case_id": "ING-014", "scenario": "Validate ISO 8601 date parsing across all created_at and updated_at fields.", "expected": "All timestamps parse as valid dates between 2026-04-16 and 2026-10-12 with explicit +07:00 timezone offset.", "fixture": "structured/issues.jsonl", "tags": ["date_validation", "timeline_consistency"]},
    {"case_id": "ING-015", "scenario": "Verify exact match between manifest.json reported counts and structured row counts.", "expected": "Zero variance between manifest metadata and line counts of JSONL entity files.", "fixture": "manifest.json", "tags": ["manifest_verification", "catalog_integrity"]},
    {"case_id": "ING-016", "scenario": "Validate human vs bot timestamp windows across working hours, lunch break, and overtime.", "expected": "Human timestamps occur strictly within 08:00-12:00 or 13:00-17:00 (regular) and 17:00-22:00 (OT) +07:00; 24/7 bots operate during off-hours.", "fixture": "structured/issue_comments.jsonl", "tags": ["overtime", "lunch_break", "bot_activity"]},
    {"case_id": "ING-017", "scenario": "Validate Vietnam public holiday and weekend calendar compliance.", "expected": "Zero routine human issue creation or bundle documentation on Saturdays, Sundays, or the 5 Vietnam public holidays.", "fixture": "structured/documents.jsonl", "tags": ["vn_holidays", "weekend_policy"]},
    {"case_id": "ING-018", "scenario": "Validate Agile sprint rollover changelog lineage.", "expected": "Every issue carried over from closed Sprints 1..12 into Sprint 13 records an explicit field='sprint' transition in issue_changelog.jsonl.", "fixture": "structured/issue_changelog.jsonl", "tags": ["sprint_spillover", "agile_lineage"]},
    {"case_id": "ING-019", "scenario": "Validate offboarding and PTO assignee handover timestamps.", "expected": "Inactive members M-018, M-045, and M-070 have zero activity after left_at and all open issues were reassigned on or before left_at.", "fixture": "structured/issue_changelog.jsonl", "tags": ["offboarding", "pto_handover"]}
]

edge_cases = [
    {"scenario_id": "EDGE-ACL-01", "category": "permissions", "case": "Group-based access filtering", "expected": "Filter ACL prior to search ranking and snippet generation; never leak unauthorized document titles."},
    {"scenario_id": "EDGE-ACL-02", "category": "permissions", "case": "Cross-tenant data isolation", "expected": "Return zero search results, counts, or existence signals when querying foreign merchant tenant resources."},
    {"scenario_id": "EDGE-ACL-03", "category": "permissions", "case": "Former employee access revocation", "expected": "Preserve historical commit and issue attribution while instantly terminating login and group authorizations."},
    {"scenario_id": "EDGE-ACL-04", "category": "permissions", "case": "Partner integration boundary", "expected": "Allow PulsePay access strictly to explicitly shared payment specs; deny access to general commerce policies."},
    {"scenario_id": "EDGE-ACL-05", "category": "permissions", "case": "Quarantine on missing classification", "expected": "Quarantine any document missing security classification or access groups; never apply permissive defaults."},
    {"scenario_id": "EDGE-RAG-01", "category": "retrieval", "case": "Exact duplicate content handling", "expected": "Group or deduplicate identical SHA-256 uploads with canonical source citation."},
    {"scenario_id": "EDGE-RAG-02", "category": "retrieval", "case": "Conflicting document versions", "expected": "Answer authoritatively from current approved version while explicitly noting superseded status of legacy docs."},
    {"scenario_id": "EDGE-RAG-03", "category": "retrieval", "case": "Calibrated abstention on unapproved features", "expected": "Explicitly state when a feature is not approved in PRD (e.g. auto translation) rather than hallucinating."},
    {"scenario_id": "EDGE-RAG-04", "category": "retrieval", "case": "Multi-document synthesis", "expected": "Synthesize answer across multiple related documents (e.g. ADR-003 and RCA-006 for webhook deduplication)."},
    {"scenario_id": "EDGE-RAG-05", "category": "retrieval", "case": "Section-level citation fidelity", "expected": "Return precise section anchor (e.g. #doc-cat-20260416-01) in citation when citing bundled Markdown."},
    {"scenario_id": "EDGE-ING-01", "category": "ingestion", "case": "Broken external documentation link", "expected": "Preserve source text and register broken link warning without halting ingestion pipeline."},
    {"scenario_id": "EDGE-ING-02", "category": "ingestion", "case": "Non-standard attachment format boundary", "expected": "Record attachment file metadata and invoke dedicated tabular parser for CSV datasets."},
    {"scenario_id": "EDGE-ING-03", "category": "ingestion", "case": "DOCX header, table, and footer extraction", "expected": "Extract structural table cells, document title, and footer classification markings into clean text."},
    {"scenario_id": "EDGE-ING-04", "category": "ingestion", "case": "Unindexed scratch file quarantine", "expected": "Exclude scratch notes lacking frontmatter from vector database index."},
    {"scenario_id": "EDGE-ING-05", "category": "ingestion", "case": "High-volume bundled Markdown segmentation", "expected": "Split 56 monthly bundles into 1,373 logical documents using H3 headers and HTML anchors."},
    {"scenario_id": "EDGE-PROG-01", "category": "analytics", "case": "Blocked and overdue Jira task detection", "expected": "Surface issue key, summary, blocker reason, and assignee in operational health dashboard."},
    {"scenario_id": "EDGE-PROG-02", "category": "analytics", "case": "Ambiguous completion definition disambiguation", "expected": "Explicitly state completion metric formula (e.g. Done / Total vs Done / (Total - To Do))."},
    {"scenario_id": "EDGE-PROG-03", "category": "analytics", "case": "Stale update detection across workstreams", "expected": "Identify projects without updates within configurable threshold days from snapshot date."},
    {"scenario_id": "EDGE-SRC-01", "category": "source_sync", "case": "Orphan Jira issue reference in document", "expected": "Flag unresolved issue key while preserving raw reference string for developer remediation."},
    {"scenario_id": "EDGE-SRC-02", "category": "source_sync", "case": "Out-of-order document versioning", "expected": "Rely on explicit version lineage graph (supersedes/superseded_by) rather than lexicographical string comparison."},
    {"scenario_id": "EDGE-ACL-06", "category": "permissions", "case": "Revoked group membership with warm retrieval cache", "expected": "Invalidate or re-key authorization-sensitive cache results immediately after membership revocation; return no stale snippet."},
    {"scenario_id": "EDGE-ACL-07", "category": "permissions", "case": "Historical content authored by offboarded member", "expected": "Keep provenance for authorized auditors while denying the former member authentication and active access."},
    {"scenario_id": "EDGE-RAG-06", "category": "retrieval", "case": "Canonical Markdown and DOCX rendition deduplication", "expected": "Index one logical canonical document and cite its canonical ID; retain the DOCX path only as a rendition."},
    {"scenario_id": "EDGE-RAG-07", "category": "retrieval", "case": "Contradictory test-only policy fixture", "expected": "Prefer the approved canonical policy and isolate the contradictory fixture to explicit evaluation queries."},
    {"scenario_id": "EDGE-ING-06", "category": "ingestion", "case": "Attachment inherits parent tenant and classification", "expected": "Resolve a CSV attachment through its parent record and enforce the parent's tenant and access-group boundary."},
    {"scenario_id": "EDGE-ING-07", "category": "ingestion", "case": "Missing owner metadata", "expected": "Quarantine the document for owner resolution and do not assign a default principal or permissive access group."},
    {"scenario_id": "EDGE-TRACE-01", "category": "traceability", "case": "Approved requirement has no functional test", "expected": "Flag the requirement as uncovered and prevent full coverage reporting until a linked test case exists."},
    {"scenario_id": "EDGE-TRACE-02", "category": "traceability", "case": "Blocked execution is not counted as a pass", "expected": "Keep blocked-only requirements unresolved in RTM and release readiness summaries."},
    {"scenario_id": "EDGE-DATA-01", "category": "integrity", "case": "Evaluation answer leakage into demo index", "expected": "Keep evaluation cases and gold answers outside the user-facing retrieval namespace."},
    {"scenario_id": "EDGE-DATA-02", "category": "integrity", "case": "Manifest drift after package edit", "expected": "Identify the exact path, byte count, or SHA-256 mismatch and require inventory regeneration."},
    {"scenario_id": "EDGE-TIME-01", "category": "temporal", "case": "Evening overtime window enforcement (17:00-22:00+07:00)", "expected": "Classify human engineering actions between 17:00 and 22:00 ICT as evening_overtime and reject human commits outside 08:00-22:00."},
    {"scenario_id": "EDGE-TIME-02", "category": "temporal", "case": "Lunch break quiet window (12:00-13:00+07:00)", "expected": "Ensure zero routine human issue/comment/changelog timestamps fall between 12:00 and 12:59 ICT."},
    {"scenario_id": "EDGE-TIME-03", "category": "temporal", "case": "Vietnam public holiday and weekend separation", "expected": "Prevent routine human engineering events on Saturdays, Sundays, and the 5 VN holidays while permitting 24/7 bots and P0/P1 war-rooms."},
    {"scenario_id": "EDGE-TIME-04", "category": "temporal", "case": "Business-hour SLA vs wall-clock elapsed time", "expected": "Compute SLA cycle time using 8 working hours per business day + logged overtime rather than raw 24h calendar subtraction."},
    {"scenario_id": "EDGE-AGILE-01", "category": "agile", "case": "Closed sprint spillover into active Sprint 13", "expected": "Ensure closed Sprints 1..12 contain only Done issues while unfinished tickets roll over to Sprint 13 with changelog audit records."},
    {"scenario_id": "EDGE-AGILE-02", "category": "agile", "case": "Non-linear code review and blocker loop", "expected": "Handle multi-hop status transitions (In Review -> In Progress rework, Blocked -> In Progress unblock) without assuming monotonic status order."}
]

for _idx, _c in enumerate(rag_cases, 1):
    _cat = "abstention" if "calibrated_abstention" in _c.get("tags", []) else ("conflict" if "conflict" in _c.get("tags", []) else "normal")
    _c.update(_dual_review_meta(_idx, category=_cat))
for _idx, _c in enumerate(acl_cases, 1):
    _cat = "acl_deny" if _c["expected_decision"] == "deny" else "normal"
    _c.update(_dual_review_meta(_idx, category=_cat))
for _idx, _c in enumerate(analytics_cases, 1):
    _c.update(_dual_review_meta(_idx, category="analytics"))
for _idx, _c in enumerate(progress_cases, 1):
    _pid = None if _c["project_id"] == "ALL" else _c["project_id"]
    _c.update(_dual_review_meta(_idx, project_id=_pid, category="progress"))
for _idx, _c in enumerate(ingestion_cases, 1):
    _c.update(_dual_review_meta(_idx, category="ingestion_integrity"))
for _idx, _c in enumerate(edge_cases, 1):
    _c.update(_dual_review_meta(_idx, category=f"edge_{_c['category']}"))

write_jsonl("evaluation/rag_cases.jsonl", rag_cases)
write_jsonl("evaluation/acl_cases.jsonl", acl_cases)
write_jsonl("evaluation/analytics_cases.jsonl", analytics_cases)
write_jsonl("evaluation/progress_cases.jsonl", progress_cases)
write_jsonl("evaluation/ingestion_cases.jsonl", ingestion_cases)
write_jsonl("evaluation/edge_case_matrix.jsonl", edge_cases)
write_jsonl("evaluation/workflow_cases.jsonl", workflow_cases)

total_eval_cases = len(rag_cases) + len(acl_cases) + len(analytics_cases) + len(progress_cases) + len(ingestion_cases) + len(edge_cases) + len(workflow_cases)
assert total_eval_cases == 190, f"Expected 190 eval cases, got {total_eval_cases}"

# -------------------------------------------------------------
# 12. Create Excel Catalog (Dataset_Catalog.xlsx) (Phase 7: Sprints tab added)
# -------------------------------------------------------------
_existing_rel_files = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if is_package_file(path)}
physical_package_count = len(_existing_rel_files | {"Dataset_Catalog.xlsx", "INGESTION_CONTRACT.md", "00_START_HERE.md", "manifest.json"})
wb = openpyxl.Workbook()

NAVY = "16324F"; TEAL = "16697A"; LIGHT_BG = "F8FAFC"; ZEBRA = "F1F5F8"; WHITE = "FFFFFF"; DARK_TEXT = "24364B"; GRAY_TEXT = "64748B"; BORDER_COLOR = "CBD5E1"
font_title = Font(name="Aptos", size=16, bold=True, color=NAVY)
font_subtitle = Font(name="Aptos", size=10, italic=True, color=GRAY_TEXT)
font_header = Font(name="Aptos", size=10, bold=True, color=WHITE)
font_bold = Font(name="Aptos", size=9.5, bold=True, color=DARK_TEXT)
font_cell = Font(name="Aptos", size=9, color=DARK_TEXT)
font_kpi_num = Font(name="Aptos", size=18, bold=True, color=NAVY)
font_kpi_lbl = Font(name="Aptos", size=8.5, bold=True, color=GRAY_TEXT)

fill_header = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
fill_kpi = PatternFill(start_color=LIGHT_BG, end_color=LIGHT_BG, fill_type="solid")
fill_zebra = PatternFill(start_color=ZEBRA, end_color=ZEBRA, fill_type="solid")
thin_side = Side(border_style="thin", color=BORDER_COLOR)
table_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

# Tab 1: Overview
ws_over = wb.active
ws_over.title = "Overview"
ws_over.views.sheetView[0].showGridLines = True

ws_over.cell(2, 2, "Northstar Commerce — Enterprise Synthetic Dataset Catalog (v1.4)").font = font_title
ws_over.cell(3, 2, f"Snapshot Date: {TODAY.isoformat()}  •  180-Day Window ({START.isoformat()} to {TODAY.isoformat()}, {TOTAL_WORKING_DAYS} Working Days + 5 VN Holidays, UTC+07:00 & Overtime 17:00-22:00)").font = font_subtitle

ws_over.merge_cells("B5:K5")
banner_cell = ws_over.cell(5, 2, f"PACKAGE NOTICE: {len(canonical_documents):,} logical documents across 56 monthly bundles, {len(docx_specs)} standalone DOCX sources, {len(completion_docx_specs)} DOCX renditions, {len(md_specs)} formal Markdown sources, and {len(registered_fixtures)} registered fixtures. Package files: {physical_package_count} / 160.")
banner_cell.font = Font(name="Aptos", size=9.5, bold=True, color="0F5132")
banner_cell.fill = PatternFill(start_color="D1E7DD", end_color="D1E7DD", fill_type="solid")
banner_cell.alignment = align_center
ws_over.row_dimensions[5].height = 24

kpis = [
    ("Organizations", "3", "B7:B8"), ("Departments", "10", "C7:C8"), ("Total Members", "74", "D7:D8"),
    ("Active Staff", "71", "E7:E8"), ("Projects", "8", "F7:F8"), ("Sprints", "104", "G7:G8"),
    ("Jira Issues", f"{len(issues):,}", "H7:H8"), ("Logical Documents", f"{len(canonical_documents):,}", "I7:I8"),
    ("Physical Files", str(physical_package_count), "J7:J8"), ("All Test Cases", f"{total_eval_cases + len(functional_test_cases):,}", "K7:K8")
]
for lbl, val, rng in kpis:
    col = rng.split(":")[0][0]
    col_idx = ord(col) - ord('A') + 1
    c_val = ws_over.cell(7, col_idx, val); c_val.font = font_kpi_num; c_val.alignment = align_center; c_val.fill = fill_kpi
    c_lbl = ws_over.cell(8, col_idx, lbl); c_lbl.font = font_kpi_lbl; c_lbl.alignment = align_center; c_lbl.fill = fill_kpi
    c_val.border = Border(left=thin_side, right=thin_side, top=thin_side)
    c_lbl.border = Border(left=thin_side, right=thin_side, bottom=thin_side)

# Issue Status Breakdown Table
ws_over.cell(10, 2, "Issue Status Breakdown").font = font_bold
ws_over.cell(11, 2, "Status").font = font_header; ws_over.cell(11, 2).fill = fill_header
ws_over.cell(11, 3, "Count").font = font_header; ws_over.cell(11, 3).fill = fill_header
ws_over.cell(11, 4, "Percentage").font = font_header; ws_over.cell(11, 4).fill = fill_header

status_counts = {s: sum(1 for i in issues if i["status"] == s) for s in ["Done", "In Progress", "In Review", "To Do", "Blocked"]}
for row_idx, (s, cnt) in enumerate(status_counts.items(), 12):
    ws_over.cell(row_idx, 2, s).font = font_cell
    ws_over.cell(row_idx, 3, cnt).font = font_cell; ws_over.cell(row_idx, 3).alignment = align_right
    ws_over.cell(row_idx, 4, f"{cnt/len(issues):.1%}").font = font_cell; ws_over.cell(row_idx, 4).alignment = align_right
    for c in range(2, 5): ws_over.cell(row_idx, c).border = table_border

chart = BarChart(); chart.type = "col"; chart.style = 10; chart.title = "Jira Issues by Status"
chart.y_axis.title = "Number of Issues"; chart.x_axis.title = "Status"
data_ref = Reference(ws_over, min_col=3, min_row=11, max_row=16)
cats_ref = Reference(ws_over, min_col=2, min_row=12, max_row=16)
chart.add_data(data_ref, titles_from_data=True); chart.set_categories(cats_ref)
chart.height = 7; chart.width = 13
ws_over.add_chart(chart, "F10")

# Project Health Table
ws_over.cell(18, 2, "Project Health and Delivery Status").font = font_bold
headers_proj = ["Project ID", "Project Name", "Portfolio", "Status", "Owner", "Target Date", "Total Issues", "Done Issues", "Completion %"]
for col_idx, h in enumerate(headers_proj, 2):
    c = ws_over.cell(19, col_idx, h); c.font = font_header; c.fill = fill_header; c.alignment = align_center

for row_idx, p in enumerate(projects, 20):
    pid = p["project_id"]
    p_issues = [i for i in issues if i["project_id"] == pid]
    done_cnt = sum(1 for i in p_issues if i["status"] == "Done")
    tot_cnt = len(p_issues)
    pct = f"{done_cnt/tot_cnt:.1%}" if tot_cnt else "0%"
    vals = [pid, p["name"], p["portfolio"], p["status"], p["owner_id"], p["target_date"], tot_cnt, done_cnt, pct]
    for col_idx, v in enumerate(vals, 2):
        c = ws_over.cell(row_idx, col_idx, v); c.font = font_cell; c.border = table_border
        if col_idx in [2, 5, 7, 8, 9, 10]: c.alignment = align_center

ws_over.cell(30, 2, "Domain & Technology Stack Reference").font = font_bold
ws_over.cell(31, 2, "Bagisto open-source ecommerce repository (Laravel + Vue.js architecture inspiration only; all data synthetic): https://github.com/bagisto/bagisto").font = font_subtitle

# Tab 2: Organizations
ws_org = wb.create_sheet(title="Organizations"); ws_org.views.sheetView[0].showGridLines = True
org_cols = ["org_id", "name", "org_type", "domain", "synthetic"]
for c_idx, col in enumerate(org_cols, 1):
    c = ws_org.cell(1, c_idx, col); c.font = font_header; c.fill = fill_header; c.alignment = align_center
for r_idx, o in enumerate(orgs, 2):
    for c_idx, col in enumerate(org_cols, 1):
        c = ws_org.cell(r_idx, c_idx, str(o.get(col, ""))); c.font = font_cell; c.border = table_border

# Tab 3: Projects
ws_proj = wb.create_sheet(title="Projects"); ws_proj.views.sheetView[0].showGridLines = True
proj_cols = ["project_id", "name", "portfolio", "status", "owner_id", "current_sprint_id", "team_group", "start_date", "target_date"]
for c_idx, col in enumerate(proj_cols, 1):
    c = ws_proj.cell(1, c_idx, col); c.font = font_header; c.fill = fill_header; c.alignment = align_center
for r_idx, p in enumerate(projects, 2):
    for c_idx, col in enumerate(proj_cols, 1):
        c = ws_proj.cell(r_idx, c_idx, str(p.get(col, ""))); c.font = font_cell; c.border = table_border

# Tab 4: Sprints (NEW in Phase 7)
ws_sp = wb.create_sheet(title="Sprints"); ws_sp.views.sheetView[0].showGridLines = True
sp_cols = ["sprint_id", "project_id", "sprint_number", "name", "status", "start_date", "end_date", "goal"]
for c_idx, col in enumerate(sp_cols, 1):
    c = ws_sp.cell(1, c_idx, col); c.font = font_header; c.fill = fill_header; c.alignment = align_center
for r_idx, sp in enumerate(sprints, 2):
    for c_idx, col in enumerate(sp_cols, 1):
        c = ws_sp.cell(r_idx, c_idx, str(sp.get(col, ""))); c.font = font_cell
        if r_idx % 2 == 1: c.fill = fill_zebra
ws_sp.freeze_panes = "A2"
ws_sp.auto_filter.ref = f"A1:{get_column_letter(len(sp_cols))}{len(sprints)+1}"

# Tab 5: Canonical logical documents
ws_docs = wb.create_sheet(title="Documents"); ws_docs.views.sheetView[0].showGridLines = True
doc_cols = ["document_id", "canonical_document_id", "title", "project_id", "organization_id", "scope", "owner_id", "created_at", "recorded_at", "is_overtime", "work_mode", "version", "status", "classification", "access_groups", "format", "document_role", "test_only", "file_path", "rendition_paths", "requirement_ids", "section_anchor", "content_sha256"]
for c_idx, col in enumerate(doc_cols, 1):
    c = ws_docs.cell(1, c_idx, col); c.font = font_header; c.fill = fill_header; c.alignment = align_center
for r_idx, d in enumerate(canonical_documents, 2):
    for c_idx, col in enumerate(doc_cols, 1):
        v = d.get(col)
        if isinstance(v, list): v = ", ".join(str(item) for item in v)
        c = ws_docs.cell(r_idx, c_idx, str(v) if v is not None else "")
        c.font = font_cell
        if r_idx % 2 == 1: c.fill = fill_zebra
ws_docs.freeze_panes = "A2"
ws_docs.auto_filter.ref = f"A1:{get_column_letter(len(doc_cols))}{len(canonical_documents)+1}"

# Tab 6: Jira-like issues
ws_iss = wb.create_sheet(title="Issues"); ws_iss.views.sheetView[0].showGridLines = True
iss_cols = ["issue_key", "project_id", "sprint_id", "parent_key", "issue_type", "summary", "status", "priority", "assignee_id", "reporter_id", "created_at", "updated_at", "due_date", "story_points", "is_overtime", "overtime_hours", "work_mode", "spillover_count"]
for c_idx, col in enumerate(iss_cols, 1):
    c = ws_iss.cell(1, c_idx, col); c.font = font_header; c.fill = fill_header; c.alignment = align_center
for r_idx, i in enumerate(issues, 2):
    for c_idx, col in enumerate(iss_cols, 1):
        v = i.get(col)
        c = ws_iss.cell(r_idx, c_idx, str(v) if v is not None else "")
        c.font = font_cell
        if r_idx % 2 == 1: c.fill = fill_zebra
ws_iss.freeze_panes = "A2"
ws_iss.auto_filter.ref = f"A1:{get_column_letter(len(iss_cols))}{len(issues)+1}"

# Tab 7: Members
ws_mem = wb.create_sheet(title="Members"); ws_mem.views.sheetView[0].showGridLines = True
mem_cols = ["member_id", "display_name", "org_id", "department_id", "job_title", "account_status", "joined_at", "left_at", "email"]
for c_idx, col in enumerate(mem_cols, 1):
    c = ws_mem.cell(1, c_idx, col); c.font = font_header; c.fill = fill_header; c.alignment = align_center
for r_idx, m in enumerate(members, 2):
    for c_idx, col in enumerate(mem_cols, 1):
        v = m.get(col)
        c = ws_mem.cell(r_idx, c_idx, str(v) if v is not None else ""); c.font = font_cell; c.border = table_border
        if r_idx % 2 == 1: c.fill = fill_zebra
ws_mem.freeze_panes = "A2"
ws_mem.auto_filter.ref = f"A1:{get_column_letter(len(mem_cols))}{len(members)+1}"

# Tab 8: RAG, ACL, ingestion, progress, and analytics evaluation cases
ws_tc = wb.create_sheet(title="Evaluation Cases"); ws_tc.views.sheetView[0].showGridLines = True
tc_cols = ["case_id", "suite", "scenario_or_query", "expected_result", "source_or_reason", "target_resource_ids", "must_not_cite", "review_status", "tags"]
for c_idx, col in enumerate(tc_cols, 1):
    c = ws_tc.cell(1, c_idx, col); c.font = font_header; c.fill = fill_header; c.alignment = align_center

all_eval_flat = []
for c in rag_cases:
    all_eval_flat.append({"case_id": c["case_id"], "suite": "RAG", "scenario_or_query": c["query"], "expected_result": c["expected"], "source_or_reason": ", ".join(c["gold_document_ids"]), "review_status": c["review_status"], "tags": ", ".join(c["tags"])})
for c in acl_cases:
    all_eval_flat.append({"case_id": c["case_id"], "suite": "ACL", "scenario_or_query": f"Principal {c['principal_id']} accesses {c['resource_id']}", "expected_result": c["expected_decision"], "source_or_reason": c["reason"], "review_status": c["review_status"], "tags": "acl, permissions"})
for c in analytics_cases:
    all_eval_flat.append({"case_id": c["case_id"], "suite": "Analytics", "scenario_or_query": c["question"], "expected_result": str(c["expected_value"]), "source_or_reason": c["metric"], "review_status": c["review_status"], "tags": "analytics, kpi"})
for c in progress_cases:
    all_eval_flat.append({"case_id": c["case_id"], "suite": "Progress", "scenario_or_query": f"Metric {c['metric']} for {c['project_id']}", "expected_result": str(c["expected_value"]), "source_or_reason": c.get("note", ""), "review_status": c["review_status"], "tags": "progress, timeline"})
for c in ingestion_cases:
    all_eval_flat.append({"case_id": c["case_id"], "suite": "Ingestion", "scenario_or_query": c["scenario"], "expected_result": c["expected"], "source_or_reason": c["fixture"], "review_status": c["review_status"], "tags": ", ".join(c["tags"])})
for c in edge_cases:
    all_eval_flat.append({"case_id": c["scenario_id"], "suite": "EdgeCase", "scenario_or_query": c["case"], "expected_result": c["expected"], "source_or_reason": c["category"], "review_status": c["review_status"], "tags": f"edge_case, {c['category']}"})
for c in workflow_cases:
    all_eval_flat.append({"case_id": c["case_id"], "suite": c["suite"], "scenario_or_query": c["query"], "expected_result": c["expected"], "source_or_reason": ", ".join(c["source_ids"]), "target_resource_ids": ", ".join(c["target_resource_ids"]), "must_not_cite": ", ".join(c["must_not_cite"]), "review_status": c["review_status"], "tags": ", ".join(c["tags"])})

for r_idx, tc in enumerate(all_eval_flat, 2):
    for c_idx, col in enumerate(tc_cols, 1):
        v = tc.get(col, "")
        c = ws_tc.cell(r_idx, c_idx, str(v)); c.font = font_cell
        if r_idx % 2 == 1: c.fill = fill_zebra
ws_tc.freeze_panes = "A2"
ws_tc.auto_filter.ref = f"A1:{get_column_letter(len(tc_cols))}{len(all_eval_flat)+1}"

# Tab 9: Requirement-linked product functional test cases
ws_ft = wb.create_sheet(title="Functional Tests"); ws_ft.views.sheetView[0].showGridLines = True
ft_cols = ["case_id", "project_id", "requirement_ids", "title", "actor", "preconditions", "steps", "expected_result", "priority", "tags", "source_issue_keys", "automation_candidate"]
for c_idx, col in enumerate(ft_cols, 1):
    c = ws_ft.cell(1, c_idx, col); c.font = font_header; c.fill = fill_header; c.alignment = align_center
for r_idx, case in enumerate(functional_test_cases, 2):
    row_values = dict(case)
    row_values["requirement_ids"] = ", ".join(case["requirement_ids"])
    row_values["steps"] = "\n".join(f"{index}. {step}" for index, step in enumerate(case["steps"], 1))
    row_values["source_issue_keys"] = ", ".join(case["source_issue_keys"])
    row_values["tags"] = ", ".join(case["tags"])
    for c_idx, col in enumerate(ft_cols, 1):
        v = row_values.get(col, "")
        c = ws_ft.cell(r_idx, c_idx, str(v) if v is not None else "")
        c.font = font_cell
        c.alignment = Alignment(vertical="top", wrap_text=True)
        if r_idx % 2 == 1: c.fill = fill_zebra
ws_ft.freeze_panes = "A2"
ws_ft.auto_filter.ref = f"A1:{get_column_letter(len(ft_cols))}{len(functional_test_cases)+1}"

workflow_sheets = []
for sheet_name, rows, columns in [
    ("Work Tasks", work_tasks, ["task_id", "key", "legacy_key", "parent_task_id", "project_id", "source_issue_key", "type", "status", "priority", "assignee_id", "sprint_id", "subtask_count", "worklog_minutes_total", "comment_count", "title"]),
    ("Task Notes", task_notes, ["note_id", "task_id", "project_id", "author_id", "title", "accomplishments", "approach", "reason", "created_at"]),
    ("Document Reviews", document_reviews, ["event_id", "document_id", "version", "project_id", "action", "actor_id", "at"]),
    ("Work Reports", work_reports, ["report_id", "project_id", "member_id", "report_type", "report_scope", "period_key", "period_start", "period_end", "status", "document_ids", "source_task_ids", "reviewed_by"]),
]:
    sheet = wb.create_sheet(title=sheet_name)
    workflow_sheets.append(sheet)
    sheet.views.sheetView[0].showGridLines = True
    for col_idx, column in enumerate(columns, 1):
        cell = sheet.cell(1, col_idx, column); cell.font = font_header; cell.fill = fill_header
    for row_idx, record in enumerate(rows, 2):
        for col_idx, column in enumerate(columns, 1):
            value = record.get(column)
            if isinstance(value, list): value = ", ".join(str(item) for item in value)
            cell = sheet.cell(row_idx, col_idx, str(value) if value is not None else "")
            cell.font = font_cell
            if row_idx % 2 == 1: cell.fill = fill_zebra
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = f"A1:{get_column_letter(len(columns))}{len(rows)+1}"

for ws in [ws_over, ws_org, ws_proj, ws_sp, ws_docs, ws_iss, ws_mem, ws_tc, ws_ft, *workflow_sheets]:
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        if ws == ws_over:
            ws.column_dimensions[col_letter].width = 16
        else:
            max_len = max(len(str(cell.value or "")) for cell in col[:100])
            ws.column_dimensions[col_letter].width = max(min(max_len + 3, 50), 12)

excel_path = ROOT / "Dataset_Catalog.xlsx"
wb.save(excel_path)
canonicalize_zip_file(excel_path)
print(f"Created professional filterable workbook at {excel_path}.")

# -------------------------------------------------------------
# 13. Align Manifest, Ingestion Contract, and 00_START_HERE.md
# -------------------------------------------------------------
manifest = {
    "dataset_id": "northstar-commerce-demo-v1",
    "version": "1.4.0",
    "as_of_date": TODAY.isoformat(),
    "simulation_window": {
        "start": START.isoformat(),
        "end": TODAY.isoformat(),
        "calendar_days": DAYS_TOTAL,
        "weekdays": TOTAL_WEEKDAYS,
        "working_days": TOTAL_WORKING_DAYS,
        "vn_holidays": len(VN_HOLIDAYS),
        "timezone": "Asia/Ho_Chi_Minh (UTC+07:00)",
        "regular_hours": "08:00-12:00, 13:00-17:00",
        "overtime_window": "17:00-22:00"
    },
    "reproducibility": {
        "deterministic": True,
        "hash_randomness_removed": True,
        "fixed_seed": 42
    },
    "language": "English synthetic project content; Vietnamese operator guide.",
    "domain": "fictional multi-tenant ecommerce platform",
    "technology_reference": {
        "repository": "https://github.com/bagisto/bagisto",
        "stack": "Laravel and Vue.js",
        "note": "Domain and stack inspiration only; dataset is entirely synthetic."
    },
    "canonical_counts": {
        "organizations": len(orgs),
        "departments": len(departments),
        "members": len(members),
        "active_members": sum(1 for m in members if m["account_status"] == "active"),
        "inactive_members": sum(1 for m in members if m["account_status"] == "inactive"),
        "access_groups": len(groups),
        "group_memberships": len(memberships),
        "projects": len(projects),
        "sprints": len(sprints),
        "issues": len(issues),
        "comments": len(comments),
        "changelog_entries": len(changelog),
        "logical_documents": len(canonical_documents),
        "requirements": len(requirement_records),
        "functional_test_cases": len(functional_test_cases),
        "test_execution_results": len(test_execution_results),
        "work_tasks": len(work_tasks),
        "task_notes": len(task_notes),
        "document_review_events": len(document_reviews),
        "work_reports": len(work_reports),
        "continuum_id_mappings": len(continuum_id_mappings),
        "physical_files_in_v1": physical_package_count,
        "physical_files_total_dataset": physical_package_count,
        "physical_breakdown": {
            "markdown_bundles": len(list((ROOT / "documents" / "markdown" / "bundles").glob("*.md"))),
            "docx_canonical_sources": len(docx_specs),
            "docx_renditions": len(completion_docx_specs),
            "markdown_formal_sources": len(md_specs),
            "fixtures_and_attachments": sum(1 for path in (ROOT / "fixtures").rglob("*") if path.is_file()),
            "structured_jsonl": len(list((ROOT / "structured").glob("*.jsonl"))),
            "evaluation_jsonl": len(list((ROOT / "evaluation").glob("*.jsonl"))),
            "documentation_and_catalog": 4,
            "generator_tools": len(list((ROOT / "tools").glob("*.py")))
        },
        "evaluation_cases": {
            "total": total_eval_cases,
            "functional_cases": len(functional_test_cases),
            "rag_cases": len(rag_cases),
            "acl_cases": len(acl_cases),
            "analytics_cases": len(analytics_cases),
            "progress_cases": len(progress_cases),
            "ingestion_cases": len(ingestion_cases),
            "edge_scenarios": len(edge_cases),
            "workflow_cases": len(workflow_cases)
        }
    },
    "packaging_model": "Canonical Markdown with linked DOCX renditions and project-month bundles (Project1 package stays within the <= 160 physical file hard cap)",
    "primary_formats": [".md", ".docx", ".xlsx", ".jsonl", ".csv"],
    "structured_format": "JSONL UTF-8, one entity per line",
    "synthetic_data_only": True,
    "file_inventory_policy": {
        "hash_algorithm": "SHA-256",
        "path_base": "Project1",
        "size_unit": "bytes",
        "manifest_excluded_from_own_inventory": True
    },
    "limitations": [
        "Synthetic data only; email domains use example.invalid.",
        f"Daily updates are packaged into 56 project-month Markdown bundles; {len(canonical_documents):,} canonical logical documents are registered, with DOCX renditions linked by canonical_document_id.",
        "Evaluation answer keys are stored separately from functional test cases and must not be indexed in the demo retrieval namespace.",
        "Task Notes are confirmed work records, not official knowledge; Document and Work Report eligibility requires approval and an ingestion consumer not present in this repository.",
        "No proprietary or actual Bagisto source code is copied."
    ]
}

ingestion_contract_text = f"""# Ingestion Contract — Northstar Commerce Dataset v1.4

## 1. Định dạng nội dung, Lịch làm việc & Quy cách đóng gói
- **Canonical Content Formats**: Markdown (.md) và Word (.docx).
- **Múi giờ, Giờ hành chính, Nghỉ trưa, OT & Ngày lễ Việt Nam**:
  - Toàn bộ dấu thời gian thực thi của con người và bot đều dùng chuẩn ISO 8601 kèm múi giờ Việt Nam `+07:00` (`YYYY-MM-DDTHH:MM:SS+07:00`).
  - **Giờ hành chính (Regular Working Hours)**: `08:00–12:00` và `13:00–17:00` (nghỉ trưa `12:00–13:00` tuyệt đối không có hoạt động của nhân sự).
  - **Khung giờ Tăng ca / Overtime (OT)**: `17:00–22:00+07:00` (từ 5h chiều đến 10h tối theo giờ Việt Nam), được gắn nhãn tường minh `is_overtime: true`, `overtime_hours`, và `work_mode: "evening_overtime"`.
  - **Nghỉ Thứ Bảy, Chủ Nhật & 5 Ngày Lễ Việt Nam**: Nhân sự nghỉ vào Thứ Bảy, Chủ Nhật và 5 ngày lễ quốc gia trong kỳ (`2026-04-27` nghỉ bù Giỗ Tổ Hùng Vương, `2026-04-30`, `2026-05-01`, `2026-09-01`, `2026-09-02`), tổng cộng đúng **123 ngày làm việc chính thức (official working days)** trên 128 ngày trong tuần.
  - **Ngoại lệ OT Cuối tuần (Weekend Incident War-Room)**: Chỉ phát sinh vào 3 ngày Thứ Bảy (`2026-08-29`, `2026-09-26`, `2026-10-10`) trong khung `17:00–22:00+07:00` (`work_mode: "weekend_incident_ot"`) cho 6 ticket sự cố P0/P1 & Canary (`CHKO-012`, `CHKO-015`, `PAY-002`, `PAY-003`, `CHKO-005`, `PLAT-005`).
  - **Hệ thống tự động / Bot 24/7**: 4 bot hệ thống (`BOT-SFTP-SYNC` lúc `02:00:00+07:00`, `BOT-INV-EXPIRY` lúc `03:30:00+07:00`, `BOT-CI-RUNNER`, `BOT-ALERT-MANAGER`) hoạt động 24/7 kể cả ban đêm, cuối tuần và ngày lễ (`actor_type: "system_bot"`).
  - **Cách tính `business_hours_elapsed`**: Tổng thời gian giao nhau (intersection) của khoảng `[created_at, updated_at]` với hai ca hành chính `08:00–12:00` và `13:00–17:00` trên các ngày làm việc chính thức (loại trừ cuối tuần và 5 ngày lễ Việt Nam), cộng với `overtime_hours`, làm tròn 1 chữ số thập phân.
- **Physical Packaging**:
  - Toàn bộ 1.373 bản ghi cập nhật kỹ thuật hàng ngày được đóng gói thành đúng 56 file Markdown bundle theo từng dự án và từng tháng (`documents/markdown/bundles/<PROJECT>-<YYYY-MM>.md`).
  - Lịch trình cập nhật diễn ra trên đúng **123 ngày làm việc chính thức (official working days)** trong khoảng từ `2026-04-16` đến `2026-10-12` (20 ngày đầu có 12 tài liệu/ngày và 103 ngày tiếp theo có 11 tài liệu/ngày = 1.373 tài liệu). Không tạo cập nhật của con người vào cuối tuần hoặc ngày lễ Việt Nam.
  - Mỗi bản ghi tài liệu logic trong bundle sở hữu thẻ neo định danh duy nhất (ví dụ `<a id="doc-cat-20260416-01"></a>`) và mã băm `content_sha256` độc lập theo 12 mẫu cấu trúc tài liệu chuyên biệt.
  - Có {len(docx_specs)} tài liệu DOCX canonical, {len(completion_docx_specs)} DOCX rendition được liên kết với Markdown canonical, và {len(md_specs)} tài liệu Markdown formal.

## 2. Định danh, Khóa ngoại & Trích dẫn RAG
- **Khóa chính**: `document_id` (ví dụ `DOC-CAT-20260416-01`) và `issue_id` / `issue_key` (ví dụ `CAT-001`) là định danh bất biến.
- **Markdown/DOCX rendition**: Bản Word xuất từ Markdown giữ cùng `canonical_document_id`; `rendition_paths` trỏ đến file DOCX và không tạo logical document/chunk trùng lặp.
- **Requirement/test IDs**: `structured/requirements.jsonl` lưu 64 FR và 10 NFR; `structured/functional_test_cases.jsonl` lưu {len(functional_test_cases)} test chức năng có liên kết requirement; kết quả mô phỏng nằm trong `structured/test_execution_results.jsonl` được phân bổ thực thi bởi đội ngũ 5 QA (`M-010`, `M-037`..`M-040`).
- **Phạm vi tài liệu cấp công ty (Organization-level Scope)**: Các tài liệu chiến lược chung của công ty (Charter, Meeting Decisions) có `project_id: null`, `organization_id: "ORG-NSC"`, và `scope: "organization"`.
- **Khớp nối thời gian Issue - Document**: Mọi `source_issue_key` liên kết trong tài liệu đều tồn tại trong `issues.jsonl` và có ngày tạo `issue.created_at[:10] <= document.created_at[:10]`.
- **Ánh xạ mã tham chiếu ngoại vi**: Mã tham chiếu đối tác `INT-001` được ánh xạ chuẩn xác vào ticket chính quy `CAT-008`. Mã `NONEXISTENT-999` chỉ xuất hiện duy nhất trong fixture kiểm thử lỗi mồ côi `fixtures/orphan_issue_reference.md`.
- **Trích dẫn nguồn RAG**: Khi trả về nguồn tham khảo cho người dùng, công cụ retrieval bắt buộc trả về `file_path` cùng với `section_anchor` chính xác.

## 3. Quy chuẩn kiểm soát quyền truy cập (ACL Pre-filtering)
- **Quy tắc vàng**: Bộ lọc ACL phải được áp dụng **TRƯỚC** khi tính toán khoảng cách vector ranking và trích xuất snippet văn bản.
- Tuyệt đối không để rò rỉ tiêu đề, trích đoạn hoặc tín hiệu tồn tại của tài liệu khi người dùng không thuộc nhóm quyền cho phép.
- **Cách ly đa tenant**: Người dùng thuộc tenant Meridian Outfitters (`ORG-MERIDIAN`) và đối tác PulsePay (`ORG-PULSEPAY`) chỉ tham gia dự án với vai trò `external_collaborator`, giữ đúng nhóm `GRP-MERIDIAN` / `GRP-PULSEPAY` và tuyệt đối không được kế thừa nhóm nội bộ (`GRP-CHECKOUT`, `GRP-CATALOG`, v.v.) của Northstar.
- **Cựu nhân viên (Inactive Staff) & Nghỉ phép (PTO)**: Nhân viên đã nghỉ việc (`M-018`, `M-045`, `M-070`, `account_status: inactive`) bị thu hồi toàn bộ phiên đăng nhập và nhóm quyền (`status: revoked`) ngay tại ngày `left_at`. Không có bất kỳ issue mở hay hoạt động nào sau `left_at`; các ticket đang dở dang được bàn giao (`field: "assignee"`) trước hoặc đúng ngày nghỉ.

## 4. Mô hình Agile Sprint, Spillover & Cách tính Story Points
- Mỗi dự án có 13 sprint liên tiếp, mỗi sprint dài 14 ngày tính cả ngày bắt đầu và kết thúc, từ `2026-04-14` đến `2026-10-12`.
- Các Sprint 1..12 đã đóng (`status: "closed"`) chỉ chứa các issue đã hoàn tất (`Done`). Toàn bộ các issue chưa hoàn thành từ Sprint trước đều được tự động chuyển tiếp (Spillover) sang `Sprint 13` (`status: "active"`, từ `2026-09-29` đến `2026-10-12`) kèm lịch sử `field: "sprint"` trong `issue_changelog.jsonl` và trường `spillover_count`.
- Chỉ số **Active Sprint WIP Story Points** (dùng cho PRG-011, PRG-012) được định nghĩa là: Tổng `story_points` của tất cả các issue thuộc dự án đó, nằm trong sprint đang active (`current_sprint_id`), và có trạng thái là `In Progress` hoặc `In Review`.

## 5. Quy chuẩn Mã băm Toàn vẹn (Canonical Checksum)
- Mã băm `content_sha256` của từng section trong Markdown bundle được tính toán trên đoạn văn bản chuẩn hóa:
  - Bắt đầu từ dòng tiêu đề `### [{doc_id}] ...` cho đến dòng phân cách `---`.
  - Toàn bộ ký tự xuống dòng được chuẩn hóa thành `\\n` (LF), cắt bỏ khoảng trắng thừa ở đầu/cuối (`strip()`), và mã hóa UTF-8 trước khi băm SHA-256.

## 6. File Inventory trong Manifest
- `manifest.json` ghi `file_inventory` với đường dẫn tương đối trong `Project1`, kích thước byte và SHA-256 của từng file vật lý.
- Inventory được sắp xếp theo đường dẫn và bao gồm toàn bộ file trong package `Project1`, ngoại trừ chính `manifest.json` để tránh checksum tự tham chiếu. `physical_files_in_v1` vẫn tính cả manifest.

## 7. Namespace và dữ liệu test
- Nạp `evaluation/` ({total_eval_cases} test cases) vào namespace benchmark riêng; không đưa gold answer, expected value hoặc expected ACL decision vào index demo.
- `fixtures/` chứa test-only duplicate, thiếu metadata, broken link, timestamp/policy conflict, cross-tenant canary, offboarded author và attachment.

## 8. Continuum Task Workspace, Group Note & ID Mapping (v1.4)
- **Không tạo Team / Không tạo lịch sử AI Chat**: Phù hợp phạm vi Continuum đã chốt, dataset không sinh thực thể Team/Team Membership và không seed lịch sử AI Chat. Quyền truy cập được quyết định tường minh bởi `continuum_org_role` (`ADMIN`, `MEMBER`) và `continuum_role_code` cấp dự án (`TEAM_LEADER`, `MEMBER`), tuyệt đối không suy diễn từ chức danh hay phòng ban.
- `structured/work_tasks.jsonl` có {len(work_tasks)} Continuum Work Task synthetic (bao phủ đủ 8 dự án, khóa chuẩn regex `^[A-Z0-9]{{2,10}}-[1-9][0-9]*$` như `NSCCAT-1..8` kèm `legacy_key` bảo toàn tương thích ngược, subtask 1 cấp, trạng thái `CANCELLED`, vòng lặp rework, checklist `steps`, `worklogs`, `comments`, và `task_events` có `reason >= 5` ký tự khi `BLOCKED`/`CANCELLED`/reopen). `task_id` là định danh 24 hex ổn định cho benchmark, **không phải ID MongoDB đang tồn tại**. `source_issue_key` ánh xạ về 2.500 Jira-like issues lịch sử; không đánh đồng toàn bộ 2.500 Jira issues là Continuum Task.
- **Ba dạng Group Note bắt buộc (không tạo entity Notebook thứ tư)**:
  1. `structured/task_notes.jsonl`: {len(task_notes)} `TASK_NOTE` trỏ đến `task_id` cùng project, luôn `status="CONFIRMED"` và `knowledge_eligible=false` (không đưa vào chỉ mục tri thức chính thức).
  2. `structured/documents.jsonl` + `structured/document_reviews.jsonl`: {len(document_reviews)} event review trên các `PROJECT_DOCUMENT` chính thức (bao gồm `SUBMITTED`, `CHANGES_REQUESTED`, `REJECTED`, `APPROVED`, `DRAFT_SAVED`, `ARCHIVED`). Chỉ phiên bản `APPROVED` chưa bị `ARCHIVED` mới đủ điều kiện làm nguồn tri thức; bản `DRAFT_SAVED` hoặc `REJECTED` tiếp theo không ghi đè phiên bản đã duyệt.
  3. `structured/work_reports.jsonl`: {len(work_reports)} `WORK_REPORT` bao phủ đầy đủ cả hai kỳ (`DAILY` và `WEEKLY`), cả hai luồng (`MEMBER` → `TEAM_LEADER`/`ADMIN` và `LEADER` → chỉ Organization `ADMIN` Manager phê duyệt theo đúng `ProjectReportRosterService`), và đủ trạng thái (`DRAFT`, `PENDING_REVIEW`, `CHANGES_REQUESTED`, `APPROVED`, `REJECTED`, kèm `is_overdue`).
- **Gián đoạn đời thực & bàn giao (Disruption Windows)**: Các khoảng nghỉ ốm (`M-019` ngày `2026-08-19..20`), mất mạng do bão (`M-027` ngày `2026-09-14..15`) và nghỉ phép năm (`M-029` ngày `2026-08-26..27`) được ghi nhận tường minh trong `leave_windows`, không phát sinh hoạt động của người vắng mặt trong khung giờ nghỉ và có đầy đủ sự kiện bàn giao sang nhân sự dự phòng.
- `structured/continuum_id_mapping.jsonl` ({len(continuum_id_mappings)} bản ghi) ánh xạ tường minh từng thực thể Northstar sang ID ứng viên 24-hex của Continuum, collection đích và trạng thái hỗ trợ (`API_SUPPORTED`, `IMPORTER_REQUIRED`, `DATASET_METADATA_ONLY`).
- `evaluation/` ({total_eval_cases} ca kiểm thử, gồm {len(workflow_cases)} `workflow_cases`) nằm hoàn toàn trong namespace benchmark riêng, gắn trạng thái kiểm duyệt kép `review_status: "unreviewed"` (`"chưa duyệt"`). Không khẳng định AI ingestion runtime hiện đã tiêu thụ outbox events của Capture.
"""
(ROOT / "INGESTION_CONTRACT.md").write_text(ingestion_contract_text, encoding="utf-8")

readme_vi = f"""# Bộ Dữ Liệu Northstar Commerce v1.4 — Hướng Dẫn Vận Hành & Khai Thác

## 1. Bối cảnh kịch bản (Dataset Scenario)
Bộ dữ liệu mô phỏng công ty công nghệ hư cấu **Northstar Commerce Systems**, đang xây dựng nền tảng thương mại điện tử đa tenant (multi-tenant ecommerce platform) cho khách hàng merchant pilot là **Meridian Outfitters**, tích hợp với đối tác cổng thanh toán **PulsePay Network**.
- Nguồn cảm hứng domain và công nghệ: Dự án mã nguồn mở **Bagisto** (kiến trúc Laravel + Vue.js: https://github.com/bagisto/bagisto).
- **Tính chân thực vận hành (Enterprise Realism v1.2)**:
  - **Múi giờ & Khung giờ làm việc**: Chuẩn giờ Việt Nam `UTC+07:00`. Giờ hành chính `08:00–12:00` và `13:00–17:00` (nghỉ trưa `12:00–13:00` không phát sinh commit/comment của con người).
  - **Tăng ca (Overtime - OT)**: Khung giờ OT buổi tối từ `17:00–22:00+07:00`, tập trung cao ở 2 dự án `At Risk` (`NSC-CHKO`, `NSC-PAY`) và các ngày cuối Sprint, có đánh dấu `is_overtime`, `overtime_hours`, `work_mode` và `business_hours_elapsed`.
  - **Lịch nghỉ Thứ Bảy, Chủ Nhật & 5 Ngày Lễ Việt Nam**: Nhân sự nghỉ Thứ Bảy, Chủ Nhật và 5 ngày lễ (`2026-04-27`, `2026-04-30`, `2026-05-01`, `2026-09-01`, `2026-09-02`) = **123 ngày làm việc chính thức**. Chỉ có 3 ngày Thứ Bảy trực chiến sự cố P0/P1 (`2026-08-29`, `2026-09-26`, `2026-10-10` từ `17:00–22:00+07:00`) và 4 Bot tự động chạy 24/7.
- **Tính tổng hợp (Synthetic)**: 100% dữ liệu nhân sự, công ty, ticket, thẻ thanh toán, sự cố và tài liệu đều là dữ liệu giả lập phục vụ kiểm thử và demo. Mọi địa chỉ email sử dụng tên miền an toàn `example.invalid`.

## 2. Quy mô dữ liệu chuẩn (Canonical Data Scale)
- **3 Tổ chức (Organizations)**: `ORG-NSC` (Northstar), `ORG-MERIDIAN` (Meridian), `ORG-PULSEPAY` (PulsePay).
- **10 Phòng ban (Departments)**: 8 phòng ban Northstar, 1 Merchandising (Meridian), 1 API Ops (PulsePay).
- **74 Hồ sơ thành viên (Members)**: 60 nhân sự nội bộ Northstar, 8 nhân sự Meridian, 6 nhân sự PulsePay. Trong đó có **71 thành viên active** (100% đều tham gia hoạt động trong dự án) và **3 cựu nhân viên** (`M-018`, `M-045`, `M-070`, đã thu hồi quyền và bàn giao toàn bộ việc trước ngày nghỉ).
- **{len(groups)} Nhóm truy cập**: Cách ly tuyệt đối giữa nhân sự nội bộ Northstar và cộng tác viên bên ngoài (`external_collaborator`).
- **8 Dự án (Projects)**: `NSC-CAT`, `NSC-SRCH`, `NSC-CART`, `NSC-CHKO`, `NSC-PAY`, `NSC-INV`, `NSC-ORD`, `NSC-PLAT` với tỷ lệ hoàn thành phân hóa theo sức khỏe dự án (`On Track` ~68–75% Done vs `At Risk` ~35–38% Done).
- **104 Sprints**: 13 sprint liên tiếp × 8 dự án. Sprints 1..12 đã đóng (0 issue mở bị bỏ quên; toàn bộ việc dở dang được spillover sang Sprint 13 kèm lịch sử chuyển Sprint).
- **180 Ngày giả lập (Simulation Window)**: Từ `2026-04-16` đến `2026-10-12` (128 weekdays = **123 ngày làm việc chính thức** + 5 ngày lễ Việt Nam).
- **{len(canonical_documents):,} Bản ghi tài liệu logic (Logical Documents)**: Được đăng ký đầy đủ trong `structured/documents.jsonl`; DOCX rendition dùng chung canonical ID với Markdown.
- **Đúng 2.500 Jira-like Issues**: Có cấu trúc phân cấp `parent_key` (Epic -> Story/Task/Bug), vòng lặp review/rework/unblock phi tuyến tính, `{len(comments):,}` bình luận đa lượt (gồm cả nhân sự, đối tác và 4 bot hệ thống) và `{len(changelog):,}` bản ghi lịch sử chuyển đổi trạng thái/sprint/assignee.
- **Continuum Task Workspace & Group Note v1.4**: {len(work_tasks)} Continuum Work Task (có checklist, worklog, comment, task_events, subtask 1 cấp, CANCELLED & bàn giao nghỉ ốm/mưa bão/PTO), {len(task_notes)} Task Note, {len(document_reviews)} event review tài liệu, {len(work_reports)} Work Report (`DAILY` & `WEEKLY`, luồng `MEMBER` & `LEADER`) và {len(continuum_id_mappings)} bản ghi `continuum_id_mapping`; tất cả là synthetic, không phải seed MongoDB.
- **{total_eval_cases} Evaluation Cases** và **{len(functional_test_cases)} Functional Test Cases**: Đầy đủ các kịch bản RAG, ACL đa tenant, Analytics OT/Spillover, Ingestion và Edge Cases.

## 3. Kiến trúc đóng gói: File vật lý vs Bản ghi logic
Package `Project1` tuân thủ giới hạn cứng **<= 160 file vật lý** ({physical_package_count} / 160 files):
- **56 Monthly Markdown Bundles**: 8 dự án × 7 tháng lưu trữ 1.373 bản ghi cập nhật kỹ thuật trên **123 ngày làm việc chính thức** (20 ngày đầu có 12 docs/ngày, 103 ngày sau có 11 docs/ngày) sử dụng 12 mẫu cấu trúc tài liệu khác nhau.
- **{len(docx_specs)} DOCX canonical sources** và **{len(completion_docx_specs)} DOCX renditions**.
- **{len(md_specs)} Tài liệu Markdown formal** và **{len(registered_fixtures)} Fixture records**.
- Tổng cộng: 1.373 + {len(docx_specs)} + {len(md_specs)} + {len(registered_fixtures)} = **{len(canonical_documents):,} Logical Documents**.

## 4. Thứ tự nạp dữ liệu khuyến nghị (Ingestion Pipeline)
1. **Thực thể nền tảng**: `organizations` → `departments` → `members` → `access_groups` → `group_memberships`.
2. **Dự án & Sprints**: `projects` → `sprints` → `project_memberships`.
3. **Tiến độ và nhiệm vụ**: `issues` → `issue_comments` → `issue_changelog`; tiếp theo `work_tasks` → `task_notes` và `work_reports` theo `source_issue_key`/`task_id`.
4. **Nạp kho tài liệu (Content Ingestion)**:
   - Nạp Markdown canonical trong `documents/markdown/formal/`; DOCX rendition dùng chung `canonical_document_id` nên không tạo chunk trùng.
   - Phân đoạn 56 bundles trong `documents/markdown/bundles/` theo các thẻ neo `<a id="..."></a>` để tạo đúng 1.373 chunks tài liệu tương ứng với `structured/documents.jsonl`.
5. **Đánh chỉ mục vector & tìm kiếm**:
   - Gắn nhãn `access_groups`, `classification`, và `scope` vào từng chunk.
   - Áp dụng bộ lọc ACL trước khi retrieval (Pre-filtering).
6. **Test nghiệp vụ và benchmark**:
   - Test chức năng lấy từ `structured/functional_test_cases.jsonl`; đối chiếu requirement và kết quả trong `structured/test_execution_results.jsonl`.
   - Bộ dữ liệu kiểm thử retrieval/ACL/ingestion/workflow lấy từ `evaluation/` vào namespace riêng biệt, **không đưa gold answers vào index demo**. Task Note không là nguồn tri thức chính thức; Document/Report được duyệt chỉ đủ điều kiện làm nguồn khi có consumer runtime.

## 5. Hướng dẫn sử dụng Dataset_Catalog.xlsx
1. Mở file `Dataset_Catalog.xlsx` bằng Microsoft Excel hoặc LibreOffice Calc.
2. **Tab Overview**: Xem tổng quan chỉ số KPI, biểu đồ phân bố trạng thái Jira issue và bảng tiến độ 8 dự án.
3. **Tab Sprints**: Tra cứu 104 sprint của 8 dự án, xem mục tiêu sprint và trạng thái active/closed.
4. **Tab Documents**: Sử dụng bộ lọc (AutoFilter) theo `project_id`, `scope`, `is_overtime`, `work_mode`, `classification`, `status` hoặc `format`.
5. **Tab Issues**: Tra cứu 2.500 ticket theo `status`, `sprint_id`, `parent_key`, `is_overtime`, `overtime_hours`, `spillover_count`, `assignee_id`, hoặc `priority`.
6. **Tab Evaluation Cases**: Xem {total_eval_cases} kịch bản RAG, ACL, ingestion, tiến độ, analytics và workflow.
7. **Tab Functional Tests**: Lọc {len(functional_test_cases)} test theo project, requirement, actor, priority và kết quả kỳ chạy.
8. **Tab Work Tasks / Task Notes / Document Reviews / Work Reports**: Tra chuỗi nguồn việc làm, ghi nhận, phê duyệt và báo cáo theo ID/project.
"""
(ROOT / "00_START_HERE.md").write_text(readme_vi, encoding="utf-8")

# Write the manifest last so it can inventory every other generated file.
manifest_path = ROOT / "manifest.json"
file_inventory = []
for file_path in sorted(p for p in ROOT.rglob("*") if is_package_file(p) and p != manifest_path):
    relative_path = file_path.relative_to(ROOT).as_posix()
    raw_bytes = file_path.read_bytes()
    file_inventory.append({
        "path": relative_path,
        "size_bytes": len(raw_bytes),
        "sha256": hashlib.sha256(raw_bytes).hexdigest()
    })
manifest["file_inventory"] = file_inventory
manifest["canonical_counts"]["file_inventory_entries"] = len(file_inventory)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# -------------------------------------------------------------
# 14. Self-Validation of Dataset Integrity (Phase 8)
# -------------------------------------------------------------
print("\n--- RUNNING COMPREHENSIVE DATASET INTEGRITY VALIDATION ---")
validation_errors = []

# 1. Counts match manifest
manifest_loaded = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
mc = manifest_loaded["canonical_counts"]
if mc["logical_documents"] != len(canonical_documents): validation_errors.append("Manifest documents mismatch")
if mc["issues"] != len(issues): validation_errors.append("Manifest issues mismatch")
if mc["members"] != len(members): validation_errors.append("Manifest members mismatch")
if mc["sprints"] != len(sprints): validation_errors.append("Manifest sprints mismatch")
if mc.get("requirements") != len(requirement_records): validation_errors.append("Manifest requirement count mismatch")
if mc.get("functional_test_cases") != len(functional_test_cases): validation_errors.append("Manifest functional test count mismatch")
if mc.get("test_execution_results") != len(test_execution_results): validation_errors.append("Manifest test execution count mismatch")

# 1a. Manifest inventories every physical v1 file except itself.
inventory = manifest_loaded.get("file_inventory", [])
inventory_by_path = {entry.get("path"): entry for entry in inventory}
manifest_path = ROOT / "manifest.json"
actual_inventory_paths = sorted(
    p.relative_to(ROOT).as_posix()
    for p in ROOT.rglob("*")
    if is_package_file(p) and p != manifest_path
)
if len(inventory) != len(inventory_by_path):
    validation_errors.append("Manifest file inventory contains duplicate paths")
if sorted(inventory_by_path) != actual_inventory_paths:
    validation_errors.append("Manifest file inventory paths do not match v1 files")
if mc.get("file_inventory_entries") != len(actual_inventory_paths):
    validation_errors.append("Manifest file inventory count mismatch")
for entry in inventory:
    relative_path = entry.get("path", "")
    file_path = ROOT / relative_path
    if not file_path.is_file():
        validation_errors.append(f"Manifest inventory file missing: {relative_path}")
        continue
    raw_bytes = file_path.read_bytes()
    if entry.get("size_bytes") != len(raw_bytes):
        validation_errors.append(f"Manifest file size mismatch: {relative_path}")
    if entry.get("sha256") != hashlib.sha256(raw_bytes).hexdigest():
        validation_errors.append(f"Manifest SHA-256 mismatch: {relative_path}")

# 2. All JSONL parse
jsonl_files = list((ROOT / "structured").glob("*.jsonl")) + list((ROOT / "evaluation").glob("*.jsonl"))
for jf in jsonl_files:
    try:
        with open(jf, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                if line.strip(): json.loads(line)
    except Exception as e:
        validation_errors.append(f"Failed parsing {jf.name}: {e}")

# 3. Document files, section anchors, and checksums exist
doc_ids = set()
canonical_ids = set()
member_ids = {m["member_id"] for m in members}
group_ids = {g["group_id"] for g in groups}
for d in canonical_documents:
    did = d["document_id"]
    if did in doc_ids: validation_errors.append(f"Duplicate document ID: {did}")
    doc_ids.add(did)
    canonical_id = d.get("canonical_document_id")
    if not canonical_id: validation_errors.append(f"Missing canonical document ID: {did}")
    if did == canonical_id:
        if canonical_id in canonical_ids: validation_errors.append(f"Duplicate canonical document ID: {canonical_id}")
        canonical_ids.add(canonical_id)
    if d.get("owner_id") not in member_ids:
        validation_errors.append(f"Document owner invalid: {did}")
    if not set(d.get("access_groups", [])).issubset(group_ids):
        validation_errors.append(f"Document access group invalid: {did}")
    if not set(d.get("requirement_ids", [])).issubset(requirements_by_id):
        validation_errors.append(f"Document requirement reference invalid: {did}")
    doc_d = date.fromisoformat(d["created_at"][:10])
    if doc_d.weekday() >= 5 or doc_d in VN_HOLIDAYS:
        validation_errors.append(f"Document created on weekend or VN holiday: {did} ({d['created_at']})")

    file_p = ROOT / d["file_path"]
    if not file_p.exists():
        validation_errors.append(f"Document file missing: {d['file_path']}")
    else:
        anchor = d.get("section_anchor")
        if anchor:
            raw_text = file_p.read_text(encoding="utf-8")
            anchor_tag = f"id=\"{anchor.lstrip('#')}\""
            if anchor_tag not in raw_text:
                validation_errors.append(f"Anchor {anchor} missing in {d['file_path']}")
            if d.get("content_sha256"):
                section_start = raw_text.find(f"### [{did}]")
                section_end = raw_text.find("\n---", section_start)
                if section_start < 0 or section_end < 0:
                    validation_errors.append(f"Bundle section boundaries invalid: {did}")
                else:
                    actual_hash = compute_section_sha256(raw_text[section_start:section_end + len("\n---")])
                    if actual_hash != d["content_sha256"]:
                        validation_errors.append(f"Bundle section checksum mismatch: {did}")
    for rendition_path in d.get("rendition_paths", []):
        if not (ROOT / rendition_path).is_file():
            validation_errors.append(f"Document rendition missing: {did} -> {rendition_path}")
    if d.get("document_role") == "test_fixture" and not d.get("test_only"):
        validation_errors.append(f"Fixture is not marked test-only: {did}")

for d in canonical_documents:
    if d.get("canonical_document_id") not in doc_ids:
        validation_errors.append(f"Canonical document reference missing: {d['document_id']} -> {d.get('canonical_document_id')}")

# 4. Foreign key integrity & Multi-tenant ACL Isolation
org_ids = {o["org_id"] for o in orgs}
dept_ids = {d["department_id"] for d in departments}
member_ids = {m["member_id"] for m in members}
group_ids = {g["group_id"] for g in groups}
proj_ids = {p["project_id"] for p in projects}
sprint_ids = {sp["sprint_id"] for sp in sprints}
iss_keys = {i["issue_key"] for i in issues}

group_membership_ids = [item["membership_id"] for item in memberships]
group_membership_pairs = {(item["member_id"], item["group_id"]) for item in memberships}
group_memberships_by_member = {}
if len(group_membership_ids) != len(set(group_membership_ids)):
    validation_errors.append("Duplicate group membership IDs")
if len(group_membership_pairs) != len(memberships):
    validation_errors.append("Duplicate member/group membership pairs")
for item in memberships:
    if item["member_id"] not in member_ids or item["group_id"] not in group_ids:
        validation_errors.append(f"Invalid group membership reference: {item['membership_id']}")
        continue
    group_memberships_by_member.setdefault(item["member_id"], []).append(item)
    member = member_by_id[item["member_id"]]
    expected_status = "revoked" if member["account_status"] == "inactive" else "active"
    if item["status"] != expected_status:
        validation_errors.append(f"Group membership status does not match account status: {item['membership_id']}")
    # External members must NEVER belong to internal Northstar groups
    if member["org_id"] == "ORG-MERIDIAN" and item["group_id"] != "GRP-MERIDIAN":
        validation_errors.append(f"External Meridian member leaked into internal group: {member['member_id']} -> {item['group_id']}")
    if member["org_id"] == "ORG-PULSEPAY" and item["group_id"] != "GRP-PULSEPAY":
        validation_errors.append(f"External PulsePay member leaked into internal group: {member['member_id']} -> {item['group_id']}")

for project in projects:
    team_ids = set([project["owner_id"]] + project_devs[project["project_id"]])
    for member_id in team_ids:
        if (member_id, project["team_group"]) not in group_membership_pairs:
            validation_errors.append(f"Project team lacks matching access group: {project['project_id']} / {member_id}")
for document in canonical_documents:
    if document.get("format") == "markdown_bundle":
        project = next((p for p in projects if p["project_id"] == document.get("project_id")), None)
        if not project or document.get("access_groups") != [project["team_group"]]:
            validation_errors.append(f"Project bundle ACL is not scoped to its project group: {document['document_id']}")
for case in acl_cases:
    resource = next((d for d in canonical_documents if d["document_id"] == case["resource_id"]), None)
    principal = member_by_id.get(case["principal_id"])
    principal_groups = {
        item["group_id"] for item in group_memberships_by_member.get(case["principal_id"], [])
        if item["status"] == "active"
    }
    allowed = bool(
        principal and principal["account_status"] == "active" and resource
        and principal_groups.intersection(resource.get("access_groups", []))
    )
    actual_decision = "allow" if allowed else "deny"
    if actual_decision != case["expected_decision"]:
        validation_errors.append(f"ACL evaluation expectation mismatch: {case['case_id']} expected {case['expected_decision']} got {actual_decision}")

# Requirements and functional tests must form a complete, resolvable baseline.
requirement_ids = {r["requirement_id"] for r in requirement_records}
case_ids = {c["case_id"] for c in functional_test_cases}
result_case_ids = {r["case_id"] for r in test_execution_results}
if len(requirement_ids) != len(requirement_records): validation_errors.append("Duplicate requirement IDs")
if len(case_ids) != len(functional_test_cases): validation_errors.append("Duplicate functional test IDs")
if case_ids != result_case_ids: validation_errors.append("Functional tests and execution results do not align")
if len(requirement_records) != 74: validation_errors.append(f"Expected 74 requirements, got {len(requirement_records)}")
if len(functional_test_cases) != 84: validation_errors.append(f"Expected 84 functional cases, got {len(functional_test_cases)}")
for requirement in requirement_records:
    if not requirement["test_case_ids"]:
        validation_errors.append(f"Requirement has no test: {requirement['requirement_id']}")
    if not set(requirement["test_case_ids"]).issubset(case_ids):
        validation_errors.append(f"Requirement references missing test: {requirement['requirement_id']}")
    if requirement["owner_id"] not in member_ids:
        validation_errors.append(f"Requirement owner invalid: {requirement['requirement_id']}")
    if not set(requirement["source_issue_keys"]).issubset(iss_keys):
        validation_errors.append(f"Requirement issue reference invalid: {requirement['requirement_id']}")
for case in functional_test_cases:
    if not set(case["requirement_ids"]).issubset(requirement_ids):
        validation_errors.append(f"Functional test requirement reference invalid: {case['case_id']}")
    if not set(case["source_issue_keys"]).issubset(iss_keys):
        validation_errors.append(f"Functional test issue reference invalid: {case['case_id']}")
outcome_counts = {outcome: sum(1 for result in test_execution_results if result["outcome"] == outcome) for outcome in ["Passed", "Failed", "Blocked"]}
if outcome_counts != {"Passed": 82, "Failed": 1, "Blocked": 1}:
    validation_errors.append(f"Unexpected functional execution distribution: {outcome_counts}")
for result in test_execution_results:
    if result.get("defect_issue_key") and result["defect_issue_key"] not in iss_keys:
        validation_errors.append(f"Execution references missing defect issue: {result['execution_id']}")

# Check issues, working calendar, OT window, and Agile sprint rules
inactive_member_ids = {m["member_id"] for m in members if m["account_status"] == "inactive"}
chko_005 = next((i for i in issues if i["issue_key"] == "CHKO-005"), None)
if not chko_005 or chko_005["status"] != "Blocked":
    validation_errors.append("CHKO-005 must be in Blocked status to align with FT-CHKO-007")

for i in issues:
    if i["project_id"] not in proj_ids: validation_errors.append(f"Issue project invalid: {i['issue_key']}")
    if i["sprint_id"] not in sprint_ids: validation_errors.append(f"Issue sprint invalid: {i['issue_key']}")
    if i["assignee_id"] not in member_ids: validation_errors.append(f"Issue assignee invalid: {i['issue_key']}")
    if i["reporter_id"] not in member_ids: validation_errors.append(f"Issue reporter invalid: {i['issue_key']}")
    if i.get("parent_key") and i["parent_key"] not in iss_keys:
        validation_errors.append(f"Issue parent_key invalid: {i['issue_key']} -> {i.get('parent_key')}")
    if i["status"] != "Done" and i["assignee_id"] in inactive_member_ids:
        validation_errors.append(f"Open issue assigned to inactive member: {i['issue_key']} -> {i['assignee_id']}")
    # Closed sprints 1..12 must not have open issues
    if i["status"] != "Done" and not i["sprint_id"].endswith("-13"):
        validation_errors.append(f"Open issue left in closed sprint: {i['issue_key']} ({i['status']}) in {i['sprint_id']}")
    # Check timestamp timezone and working day / hours
    for ts_field in ("created_at", "updated_at"):
        ts_val = i[ts_field]
        if not ts_val.endswith("+07:00"):
            validation_errors.append(f"Issue {i['issue_key']} {ts_field} missing +07:00 offset: {ts_val}")
        d_part = date.fromisoformat(ts_val[:10])
        h_part = int(ts_val[11:13])
        if ts_field == "created_at" and (d_part.weekday() >= 5 or d_part in VN_HOLIDAYS):
            validation_errors.append(f"Issue {i['issue_key']} created on weekend/holiday: {ts_val}")
        if h_part == 12:
            validation_errors.append(f"Issue {i['issue_key']} {ts_field} occurs during 12:00-13:00 lunch break: {ts_val}")
        if h_part < 8 or h_part >= 22:
            validation_errors.append(f"Issue {i['issue_key']} {ts_field} outside 08:00-22:00 human window: {ts_val}")

# Active Sprint 13 must be current, in-date, populated, and useful for WIP queries.
sprint_by_id = {sp["sprint_id"]: sp for sp in sprints}
for p in projects:
    current_id = p.get("current_sprint_id")
    current_sprint = sprint_by_id.get(current_id)
    if not current_sprint or current_sprint.get("status") != "active":
        validation_errors.append(f"Project current sprint is not active: {p['project_id']}")
        continue
    if current_sprint["project_id"] != p["project_id"]:
        validation_errors.append(f"Current sprint project mismatch: {p['project_id']}")
    if not (current_sprint["start_date"] <= TODAY.isoformat() <= current_sprint["end_date"]):
        validation_errors.append(f"Current sprint does not cover as-of date: {p['project_id']}")
    if (date.fromisoformat(current_sprint["end_date"]) - date.fromisoformat(current_sprint["start_date"])).days != 13:
        validation_errors.append(f"Sprint is not 14 inclusive days: {current_id}")
    sprint_issues = [i for i in issues if i["sprint_id"] == current_id]
    if not sprint_issues:
        validation_errors.append(f"Current sprint has no issues: {current_id}")
    wip_points = sum(
        i["story_points"] for i in sprint_issues
        if i["status"] in ("In Progress", "In Review")
    )
    if wip_points <= 0:
        validation_errors.append(f"Current sprint has no WIP story points: {current_id}")

# Check multi-turn comments and human vs bot timestamps
if len(comments) < len(issues):
    validation_errors.append(f"Comment count below issue count: {len(comments)} comments for {len(issues)} issues")
comment_issue_keys = {c["issue_key"] for c in comments}
if comment_issue_keys != {i["issue_key"] for i in issues}:
    validation_errors.append("Issue comments do not cover the canonical issue set")
if len({c["body"] for c in comments}) < int(len(comments) * 0.90):
    validation_errors.append("Comment body diversity is below the 90% unique-content threshold")

for c in comments:
    ts_val = c["created_at"]
    if not ts_val.endswith("+07:00"):
        validation_errors.append(f"Comment {c['comment_id']} missing +07:00 offset: {ts_val}")
    if c.get("actor_type") == "human":
        h_part = int(ts_val[11:13])
        if h_part == 12 or h_part < 8 or h_part >= 22:
            validation_errors.append(f"Human comment {c['comment_id']} outside working/OT hours: {ts_val}")
        au = member_by_id.get(c["author_id"])
        if au and au["left_at"] and ts_val[:10] > au["left_at"]:
            validation_errors.append(f"Comment {c['comment_id']} authored by {c['author_id']} after left_at {au['left_at']}")

# Check all 71 active members participate in issues or comments
active_member_ids_set = {m["member_id"] for m in members if m["account_status"] == "active"}
participating_ids = (
    {i["assignee_id"] for i in issues}
    | {i["reporter_id"] for i in issues}
    | {c["author_id"] for c in comments if c.get("actor_type") == "human"}
    | {r["executed_by"] for r in test_execution_results}
)
missing_active_members = active_member_ids_set - participating_ids
if missing_active_members:
    validation_errors.append(f"Active members with zero participation: {sorted(missing_active_members)}")

# Check issue status changelog latest entry matches current status & monotonic timestamps
latest_changelog_status = {}
changelog_by_issue = {}
for ch in changelog:
    changelog_by_issue.setdefault(ch["issue_key"], []).append(ch)
    if ch.get("field") == "status":
        latest_changelog_status[ch["issue_key"]] = ch["to_value"]
    au = member_by_id.get(ch["changed_by"])
    if au and au["left_at"] and ch["changed_at"][:10] > au["left_at"]:
        validation_errors.append(f"Changelog {ch['changelog_id']} authored by {ch['changed_by']} after left_at {au['left_at']}")

for ikey, ch_list in changelog_by_issue.items():
    ts_seq = [c["changed_at"] for c in ch_list]
    if ts_seq != sorted(ts_seq):
        validation_errors.append(f"Non-monotonic changelog timestamps for {ikey}: {ts_seq}")
    status_ts_seq = [c["changed_at"] for c in ch_list if c.get("field") == "status"]
    if len(status_ts_seq) != len(set(status_ts_seq)):
        validation_errors.append(f"Duplicate status transition timestamps for {ikey}: {status_ts_seq}")

for i in issues:
    ikey = i["issue_key"]
    curr_status = i["status"]
    if curr_status == "To Do":
        if ikey in latest_changelog_status and latest_changelog_status[ikey] != "To Do":
            validation_errors.append(f"To Do issue has unexpected status changelog: {ikey}")
    else:
        if latest_changelog_status.get(ikey) != curr_status:
            validation_errors.append(f"Issue status changelog mismatch for {ikey}: issue is {curr_status}, changelog says {latest_changelog_status.get(ikey)}")

# Check document source issue dates: issue created_at[:10] <= doc created_at[:10]
issue_created_lookup = {i["issue_key"]: i["created_at"][:10] for i in issues}
issue_by_key = {i["issue_key"]: i for i in issues}
for d in canonical_documents:
    doc_created = d["created_at"][:10]
    for s_key in d.get("source_issue_keys", []):
        if s_key == "NONEXISTENT-999":
            continue
        if s_key not in issue_created_lookup:
            validation_errors.append(f"Document {d['document_id']} references nonexistent issue {s_key}")
        else:
            iss_created = issue_created_lookup[s_key]
            if iss_created > doc_created:
                validation_errors.append(f"Document {d['document_id']} created at {doc_created} cites future issue {s_key} created at {iss_created}")

# Check PR #2 Finding 1: ANA-019 counts strictly open issues in Sprint 13 with spillover_count > 0
ana_019 = next((c for c in analytics_cases if c["case_id"] == "ANA-019"), None)
expected_open_s13_spillover = sum(
    1 for i in issues
    if i["status"] != "Done" and i["sprint_id"].endswith("-13") and i.get("spillover_count", 0) > 0
)
if not ana_019 or ana_019["expected_value"] != expected_open_s13_spillover:
    validation_errors.append(
        f"ANA-019 expected_value mismatch: got {ana_019['expected_value'] if ana_019 else None}, expected {expected_open_s13_spillover}"
    )
if not ana_019 or ana_019.get("filters") != {"status_ne": "Done", "sprint_number": 13, "spillover_count_gt": 0}:
    validation_errors.append(f"ANA-019 filters mismatch: {ana_019.get('filters') if ana_019 else None}")

# Check PR #2 Finding 2: Every bundle document records the exact changelog status of its linked issue at recorded_at
for (pid, ym), sections_data in bundle_docs_map.items():
    for section_text, doc_rec in sections_data:
        linked_key = doc_rec["source_issue_keys"][0]
        expected_hist_status = get_issue_status_at(issue_by_key[linked_key], doc_rec["recorded_at"])
        expected_link_line = f"- **Linked Issue**: [`{linked_key}`](https://jira.northstar.invalid/browse/{linked_key}) (`{expected_hist_status}`)"
        if expected_link_line not in section_text:
            validation_errors.append(
                f"Bundle {doc_rec['document_id']} at {doc_rec['recorded_at']} has wrong historical status for {linked_key} (expected {expected_hist_status})"
            )

# Check PR #2 Finding 3: Every Done issue's completion date and Done changelog transition fall within its assigned sprint window
for i in issues:
    if i["status"] == "Done":
        sp = sprint_by_id.get(i["sprint_id"])
        done_date_str = i["updated_at"][:10]
        if not sp or not (sp["start_date"] <= done_date_str <= sp["end_date"]):
            validation_errors.append(
                f"Done issue {i['issue_key']} completed at {done_date_str} outside assigned sprint {i['sprint_id']} ({sp['start_date'] if sp else None}..{sp['end_date'] if sp else None})"
            )
    if i.get("spillover_count", 0) > 0:
        has_sprint_ch = any(
            ch.get("field") == "sprint" and ch.get("from_value") == i["initial_sprint_id"] and ch.get("to_value") == i["sprint_id"]
            for ch in changelog_by_issue.get(i["issue_key"], [])
        )
        if not has_sprint_ch:
            validation_errors.append(f"Spillover issue {i['issue_key']} missing sprint changelog from {i['initial_sprint_id']} to {i['sprint_id']}")

# Check PR #2 Finding 4: Enum alignment between INGESTION_CONTRACT.md, structured JSONL, and evaluation cases
valid_work_modes = {"regular_hours", "evening_overtime", "weekend_incident_ot", "automated_bot"}
valid_actor_types = {"human", "system_bot"}
for i in issues:
    if i.get("work_mode") not in valid_work_modes:
        validation_errors.append(f"Invalid work_mode on issue {i['issue_key']}: {i.get('work_mode')}")
    expected_biz_hrs = calc_business_hours_between(i["created_at"], i["updated_at"], i.get("overtime_hours", 0.0))
    if i.get("business_hours_elapsed") != expected_biz_hrs:
        validation_errors.append(
            f"business_hours_elapsed mismatch on {i['issue_key']}: got {i.get('business_hours_elapsed')}, expected {expected_biz_hrs}"
        )
for c in comments:
    if c.get("work_mode") not in valid_work_modes:
        validation_errors.append(f"Invalid work_mode on comment {c['comment_id']}: {c.get('work_mode')}")
    if c.get("actor_type") not in valid_actor_types:
        validation_errors.append(f"Invalid actor_type on comment {c['comment_id']}: {c.get('actor_type')}")
for ch in changelog:
    if ch.get("work_mode") not in valid_work_modes:
        validation_errors.append(f"Invalid work_mode on changelog {ch['changelog_id']}: {ch.get('work_mode')}")
for d in canonical_documents:
    if d.get("work_mode") not in valid_work_modes:
        validation_errors.append(f"Invalid work_mode on document {d['document_id']}: {d.get('work_mode')}")
if total_bot_comments != 76:
    validation_errors.append(f"Expected 76 system_bot comments, got {total_bot_comments}")
if total_weekend_ot_changelog <= 0:
    validation_errors.append(f"Expected positive weekend_incident_ot changelog count, got {total_weekend_ot_changelog}")

# 5. Check physical file counts
v1_files = [f for f in ROOT.rglob("*") if is_package_file(f)]
total_dataset_files = [f for f in ROOT.rglob("*") if is_package_file(f)]
print(f"Physical Files in Project1 package: {len(v1_files)}")
print(f"Total Physical Files in Dataset: {len(total_dataset_files)} (Hard Cap: 160)")

if len(total_dataset_files) > 160:
    validation_errors.append(f"PHYSICAL FILE COUNT HARD CAP EXCEEDED: {len(total_dataset_files)} > 160!")
if len(v1_files) != mc.get("physical_files_in_v1"):
    validation_errors.append(f"Manifest v1 physical file count mismatch: {len(v1_files)}")
if len(total_dataset_files) != mc.get("physical_files_total_dataset"):
    validation_errors.append(f"Manifest dataset physical file count mismatch: {len(total_dataset_files)}")
# 6. Check Excel open
try:
    test_wb = openpyxl.load_workbook(ROOT / "Dataset_Catalog.xlsx", read_only=True)
    if not {"Overview", "Sprints", "Documents", "Issues", "Evaluation Cases", "Functional Tests"}.issubset(test_wb.sheetnames):
        validation_errors.append("One or more required catalog sheets are missing")
    if test_wb["Functional Tests"].max_row != len(functional_test_cases) + 1:
        validation_errors.append("Functional test catalog row count mismatch")
    test_wb.close()
except Exception as e:
    validation_errors.append(f"Excel read failed: {e}")

if validation_errors:
    print(f"VALIDATION FAILED with {len(validation_errors)} errors:")
    for err in validation_errors[:15]:
        print(" -", err)
    sys.exit(1)
else:
    print("SUCCESS: ALL 8 PHASES AND REALISM INTEGRITY VALIDATION CHECKS PASSED PERFECTLY!")
    print(f"Logical Documents: {len(canonical_documents)}")
    print(f"Total Physical Files in Dataset: {len(total_dataset_files)} (<= 160)")
    print(f"Jira Issues: {len(issues)} (Overtime Issues: {total_overtime_issues}, Spillover Issues: {total_spillover_issues})")
    print(f"Comments: {len(comments)} (System Bot Comments: {total_bot_comments})")
    print(f"Changelog Entries: {len(changelog)} (Weekend War-Room OT Events: {total_weekend_ot_changelog})")
    print(f"Members: {len(members)} (Active: {sum(m['account_status']=='active' for m in members)})")
    print(f"Sprints: {len(sprints)}")
    print(f"Evaluation Cases: {total_eval_cases}")
