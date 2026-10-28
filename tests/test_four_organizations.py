"""End-to-end verification suite across all FOUR Continuum synthetic organizations."""

from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

DATASET_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DATASET_ROOT / "tools"))

from continuum_synth import (  # noqa: E402
    SAFE_EMAIL_RE,
    list_package_files,
    sha256_file,
    validate_continuum_organization_bundle,
)

ORG_DIRS = {
    "northstar": DATASET_ROOT / "Project1",
    "nova": DATASET_ROOT / "Organization2-Nova-Solutions",
    "cloudops": DATASET_ROOT / "Organization3-CloudOps-Services",
    "mediflow": DATASET_ROOT / "Organization4-MediFlow",
}

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{32,}\b"),
]

ICD10_RE = re.compile(r"\b[A-TV-Z][0-9]{2}\.[0-9A-Z]{1,4}\b")
DOSAGE_RE = re.compile(r"\b\d+\s*(?:mg|ml|mcg)\s*/\s*(?:ngày|lần|viên|day)\b", re.IGNORECASE)
FORBIDDEN_CLINICAL_TABLES = ("clinical_encounters", "lab_test_results", "drug_prescriptions", "icd10_diagnoses")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [json.loads(line) for line in text.splitlines()]


def load_new_org_bundle(pkg_root: Path) -> dict[str, Any]:
    manifest = json.loads((pkg_root / "manifest.json").read_text(encoding="utf-8"))
    oncall_path = pkg_root / "structured" / "oncall_schedules.jsonl"
    return {
        "as_of_date": manifest["as_of_date"],
        "primary_org_id": manifest["primary_org_id"],
        "simulation_window": manifest["simulation_window"],
        "organizations": read_jsonl(pkg_root / "structured" / "organizations.jsonl"),
        "users": read_jsonl(pkg_root / "structured" / "users.jsonl"),
        "organization_memberships": read_jsonl(pkg_root / "structured" / "organization_memberships.jsonl"),
        "role_assignments": read_jsonl(pkg_root / "structured" / "role_assignments.jsonl"),
        "projects": read_jsonl(pkg_root / "structured" / "projects.jsonl"),
        "project_memberships": read_jsonl(pkg_root / "structured" / "project_memberships.jsonl"),
        "sprints": read_jsonl(pkg_root / "structured" / "sprints.jsonl"),
        "tasks": read_jsonl(pkg_root / "structured" / "tasks.jsonl"),
        "task_comments": read_jsonl(pkg_root / "structured" / "task_comments.jsonl"),
        "task_worklogs": read_jsonl(pkg_root / "structured" / "task_worklogs.jsonl"),
        "task_events": read_jsonl(pkg_root / "structured" / "task_events.jsonl"),
        "task_notes": read_jsonl(pkg_root / "structured" / "task_notes.jsonl"),
        "project_documents": read_jsonl(pkg_root / "structured" / "project_documents.jsonl"),
        "document_versions": read_jsonl(pkg_root / "structured" / "document_versions.jsonl"),
        "work_report_settings": read_jsonl(pkg_root / "structured" / "work_report_settings.jsonl"),
        "work_reports": read_jsonl(pkg_root / "structured" / "work_reports.jsonl"),
        "disruption_events": read_jsonl(pkg_root / "structured" / "disruption_events.jsonl"),
        "oncall_schedules": read_jsonl(oncall_path) if oncall_path.exists() else [],
        "evaluation_cases": read_jsonl(pkg_root / "evaluation" / "benchmark_cases.jsonl"),
        "id_mappings": read_jsonl(pkg_root / "structured" / "continuum_id_mapping.jsonl"),
    }


def apply_negative_mutation(bundle: dict[str, Any], fx: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(bundle)
    mtype = fx["mutation_type"]
    if mtype == "cross_tenant_project_membership":
        mutated["project_memberships"].append(fx["payload"])
    elif mtype == "document_self_review":
        for dv in mutated["document_versions"]:
            if dv["version_id"] == fx["target_version_id"]:
                dv["reviewed_by"] = fx["author_id"]
    elif mtype == "leader_report_non_admin_reviewer":
        for r in mutated["work_reports"]:
            if r["report_id"] == fx["target_report_id"]:
                r["reviewed_by"] = fx["invalid_reviewer_id"]
    elif mtype == "nested_subtask_depth_2":
        for t in mutated["tasks"]:
            if t["task_id"] == fx["target_task_id"]:
                t["parent_id"] = fx["new_parent_id"]
    elif mtype == "lunch_break_human_action":
        for c in mutated["task_comments"]:
            if c["comment_id"] == fx["target_comment_id"]:
                c["created_at"] = fx["invalid_timestamp"]
    elif mtype == "unavailable_window_activity":
        for wl in mutated["task_worklogs"]:
            if wl["worklog_id"] == fx["target_worklog_id"]:
                wl["author_id"] = fx["affected_user_id"]
                wl["logged_at"] = fx["invalid_timestamp"]
                # Ensure author is also in historical project members so unavailability check triggers cleanly
                t_proj = wl["project_id"]
                t_org = wl["organization_id"]
                mutated["project_memberships"].append({
                    "membership_id": "PM-TEMP-UNAVAIL",
                    "organization_id": t_org,
                    "project_id": t_proj,
                    "user_id": fx["affected_user_id"],
                    "status": "ACTIVE",
                })
    elif mtype == "task_note_marked_knowledge_eligible":
        for n in mutated["task_notes"]:
            if n["note_id"] == fx["target_note_id"]:
                n["knowledge_eligible"] = True
    elif mtype == "unreviewed_eval_marked_approved":
        for ec in mutated["evaluation_cases"]:
            if ec["case_id"] == fx["target_case_id"]:
                ec["review_status"] = "approved"
    else:
        raise ValueError(f"Unknown negative fixture mutation_type: {mtype}")
    return mutated


class FourOrganizationsDatasetSuiteTest(unittest.TestCase):
    def test_all_four_manifests_match_physical_files_and_sha256(self) -> None:
        for org_key, root in ORG_DIRS.items():
            with self.subTest(org=org_key):
                manifest_path = root / "manifest.json"
                self.assertTrue(manifest_path.is_file(), f"Missing manifest.json in {root}")
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                inventory = manifest["file_inventory"]
                inv_by_path = {entry["path"]: entry for entry in inventory}

                disk_files = [
                    p.relative_to(root).as_posix()
                    for p in list_package_files(root)
                    if p.name != "manifest.json"
                ]
                self.assertEqual(sorted(inv_by_path.keys()), disk_files)
                if org_key == "northstar":
                    self.assertLessEqual(len(disk_files) + 1, 160)

                for rel_p, entry in inv_by_path.items():
                    fp = root / rel_p
                    self.assertEqual(fp.stat().st_size, entry["size_bytes"], f"Size mismatch on {org_key}:{rel_p}")
                    self.assertEqual(sha256_file(fp), entry["sha256"], f"SHA-256 mismatch on {org_key}:{rel_p}")

    def test_new_organizations_pass_continuum_validator_with_zero_errors(self) -> None:
        for org_key in ("nova", "cloudops", "mediflow"):
            with self.subTest(org=org_key):
                bundle = load_new_org_bundle(ORG_DIRS[org_key])
                errors = validate_continuum_organization_bundle(bundle)
                self.assertEqual(errors, [], f"Validation errors in {org_key}: {errors}")

    def test_all_24_negative_fixtures_are_rejected_with_expected_errors(self) -> None:
        total_checked = 0
        for org_key in ("nova", "cloudops", "mediflow"):
            root = ORG_DIRS[org_key]
            bundle = load_new_org_bundle(root)
            neg_doc = json.loads((root / "fixtures" / "negative_cases.json").read_text(encoding="utf-8"))
            self.assertTrue(neg_doc.get("test_only"))
            self.assertEqual(len(neg_doc["cases"]), 8)
            for fx in neg_doc["cases"]:
                with self.subTest(org=org_key, fixture_id=fx["fixture_id"]):
                    mutated = apply_negative_mutation(bundle, fx)
                    errs = validate_continuum_organization_bundle(mutated)
                    self.assertTrue(
                        any(fx["expected_error_substring"] in e for e in errs),
                        f"Expected substring {fx['expected_error_substring']!r} not found in {errs}",
                    )
                    total_checked += 1
        self.assertEqual(total_checked, 24)

    def test_confirmed_product_scope_boundaries_across_all_four_orgs(self) -> None:
        forbidden_filenames = {"teams.jsonl", "team_memberships.jsonl", "ai_chat_history.jsonl", "notebooks.jsonl"}
        for org_key, root in ORG_DIRS.items():
            with self.subTest(org=org_key):
                structured_names = {p.name for p in (root / "structured").glob("*.jsonl")}
                self.assertFalse(structured_names & forbidden_filenames)
                self.assertIn("continuum_id_mapping.jsonl", structured_names)

                task_notes = read_jsonl(root / "structured" / "task_notes.jsonl")
                work_reports = read_jsonl(root / "structured" / "work_reports.jsonl")
                docs_file = "documents.jsonl" if org_key == "northstar" else "project_documents.jsonl"
                docs = read_jsonl(root / "structured" / docs_file)

                self.assertGreaterEqual(len(task_notes), 64)
                self.assertTrue(all(n.get("knowledge_eligible") is False for n in task_notes))
                self.assertGreaterEqual(len(docs), 24)
                self.assertGreaterEqual(len(work_reports), 24)
                self.assertEqual({r["report_scope"] for r in work_reports}, {"MEMBER", "LEADER"})
                self.assertEqual({r.get("frequency") or r.get("report_type") for r in work_reports}, {"DAILY", "WEEKLY"})

    def test_methodologies_and_domain_distinctiveness(self) -> None:
        # Org 2: Nova Solutions — Pure Waterfall
        nova = load_new_org_bundle(ORG_DIRS["nova"])
        self.assertEqual(nova["sprints"], [])
        self.assertTrue(all(t["sprint_id"] is None for t in nova["tasks"]))
        self.assertEqual({p["methodology"] for p in nova["projects"]}, {"WATERFALL"})
        gates = read_jsonl(ORG_DIRS["nova"] / "structured" / "waterfall_phase_gates.jsonl")
        crs = read_jsonl(ORG_DIRS["nova"] / "structured" / "change_requests.jsonl")
        self.assertEqual(len(gates), 6)
        self.assertTrue(any(cr["cr_id"] == "CR-2026-08" for cr in crs))

        # Org 3: CloudOps Services — Pure Kanban + 24/7 Bots & Workaround vs Permanent Fix
        cld = load_new_org_bundle(ORG_DIRS["cloudops"])
        self.assertEqual(cld["sprints"], [])
        self.assertTrue(all(t["sprint_id"] is None for t in cld["tasks"]))
        self.assertEqual({p["methodology"] for p in cld["projects"]}, {"KANBAN"})
        self.assertTrue(any(n.get("is_temporary_workaround") is True and n["task_key"] == "CLDINC-9" for n in cld["task_notes"]))
        self.assertTrue(any(c.get("actor_type") == "system_bot" for c in cld["task_comments"]))

        # Org 4: MediFlow — Project-scoped Hybrid (3 HYBRID with 15 sprints + 1 WATERFALL with sprint_id=null)
        med = load_new_org_bundle(ORG_DIRS["mediflow"])
        self.assertEqual(len(med["sprints"]), 15)
        med_pil_tasks = [t for t in med["tasks"] if t["project_id"] == "MED-PIL"]
        self.assertEqual(len(med_pil_tasks), 32)
        self.assertTrue(all(t["sprint_id"] is None for t in med_pil_tasks))
        self.assertTrue(any(t["key"] == "MEDAPT-25" and t["spillover_count"] == 1 for t in med["tasks"]))
        cfb = read_jsonl(ORG_DIRS["mediflow"] / "structured" / "clinic_feedback_log.jsonl")
        self.assertEqual(
            {row["decision_status"] for row in cfb},
            {"APPROVED_INTO_BACKLOG", "REJECTED_PRIVACY_RISK", "PENDING_EVALUATION"},
        )

    def test_all_358_evaluation_cases_are_unreviewed_and_isolated_with_provenance_and_deny(self) -> None:
        total_cases = 0
        for org_key, root in ORG_DIRS.items():
            eval_files = sorted((root / "evaluation").glob("*.jsonl"))
            org_cases: list[dict[str, Any]] = []
            for ef in eval_files:
                org_cases.extend(read_jsonl(ef))
            self.assertGreaterEqual(len(org_cases), 56)
            total_cases += len(org_cases)

            for c in org_cases:
                self.assertEqual(c.get("review_status"), "unreviewed", f"Unexpected review_status on {c.get('case_id')}")
                self.assertIsNone(c.get("reviewer_1"))
                self.assertIsNone(c.get("reviewer_2"))

            deny_count = sum(
                str(c.get("expected_answer") or c.get("expected") or "").startswith("DENY")
                for c in org_cases
            )
            self.assertGreaterEqual(deny_count, 6, f"Insufficient DENY cases in {org_key}")

            if org_key != "northstar":
                self.assertTrue(any(c["suite"] == "END_TO_END_CHAIN" for c in org_cases))

            # Ensure evaluation case IDs never leak into corpus documents/notes/reports
            case_ids = {str(c.get("case_id") or c["scenario_id"]) for c in org_cases}
            self.assertEqual(len(case_ids), len(org_cases), f"Duplicate evaluation case IDs in {org_key}")
            corpus_blob = (root / "structured" / "task_notes.jsonl").read_text(encoding="utf-8") + (
                root / "structured" / "work_reports.jsonl"
            ).read_text(encoding="utf-8")
            for cid in case_ids:
                self.assertNotIn(cid, corpus_blob)

        self.assertEqual(total_cases, 358)

    def test_safety_no_secrets_no_real_emails_and_mediflow_zero_clinical_records(self) -> None:
        for org_key, root in ORG_DIRS.items():
            users_file = "members.jsonl" if org_key == "northstar" else "users.jsonl"
            for u in read_jsonl(root / "structured" / users_file):
                self.assertRegex(u["email"], SAFE_EMAIL_RE)

            for p in list_package_files(root):
                if p.suffix.lower() in {".jsonl", ".md", ".json", ".py"}:
                    txt = p.read_text(encoding="utf-8")
                    for pat in SECRET_PATTERNS:
                        self.assertIsNone(pat.search(txt), f"Secret-like pattern in {p}")
                    if org_key == "mediflow" and "tools" not in p.parts:
                        self.assertIsNone(ICD10_RE.search(txt), f"Clinical ICD-10 code pattern found in {p}")
                        self.assertIsNone(DOSAGE_RE.search(txt), f"Prescription dosage pattern found in {p}")
                        for tbl in FORBIDDEN_CLINICAL_TABLES:
                            if "evaluation" not in p.parts:
                                self.assertNotIn(tbl, txt, f"Forbidden clinical table {tbl} found in {p}")


if __name__ == "__main__":
    unittest.main()
