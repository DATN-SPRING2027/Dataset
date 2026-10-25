"""Regression checks for the standalone Project1 workflow slice."""

import copy
import json
import sys
import unittest
from datetime import date
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1] / "Project1"
sys.path.insert(0, str(PROJECT / "tools"))
from workflows_v13 import build_workflows, validate_workflows  # noqa: E402


def rows(name):
    return [json.loads(line) for line in (PROJECT / "structured" / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()]


class WorkflowDatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.issues = rows("issues")
        cls.documents = rows("documents")
        cls.members = rows("members")
        cls.memberships = rows("project_memberships")
        cls.projects = rows("projects")
        cls.generated = (
            rows("work_tasks"),
            rows("task_notes"),
            rows("document_reviews"),
            rows("work_reports"),
            [json.loads(line) for line in (PROJECT / "evaluation" / "workflow_cases.jsonl").read_text(encoding="utf-8").splitlines()],
        )

    def validate(self, generated):
        validate_workflows(
            *generated, self.issues, self.documents, self.members,
            self.memberships, "2026-10-12"
        )

    def test_generated_slice_has_valid_links_and_scope(self):
        self.validate(self.generated)
        tasks, notes, reviews, reports, cases = self.generated
        self.assertEqual((len(tasks), len(notes), len(reviews), len(reports), len(cases)), (48, 48, 58, 8, 21))
        self.assertEqual({row["project_id"] for row in tasks}, {row["project_id"] for row in self.projects})
        self.assertTrue(all(not row["knowledge_eligible"] for row in notes))
        self.assertEqual(sum(row["status"] == "APPROVED" for row in reports), 6)
        self.assertEqual(sum(row["report_scope"] == "LEADER" for row in reports), 2)
        self.assertEqual({row["status"] for row in reports}, {"APPROVED", "CHANGES_REQUESTED", "REJECTED"})
        self.assertEqual(sum(row["action"] == "ARCHIVED" for row in reviews), 1)
        self.assertTrue(any("archive" in row["tags"] for row in cases))
        self.assertEqual(sum(row["expected"].startswith("DENY") for row in cases), 9)

    def test_same_sources_reproduce_all_rows(self):
        holidays = {date(2026, 4, 27), date(2026, 4, 30), date(2026, 5, 1), date(2026, 9, 1), date(2026, 9, 2)}
        rebuilt = build_workflows(
            self.issues, self.documents, self.members, self.memberships,
            self.projects, holidays, "2026-10-12"
        )
        self.assertEqual(rebuilt, self.generated)

    def test_gold_sources_never_overlap_forbidden_citations(self):
        cases = self.generated[4]
        for case in cases:
            with self.subTest(case_id=case["case_id"]):
                self.assertFalse(set(case["source_ids"]) & set(case["must_not_cite"]))
                self.assertTrue(case["target_resource_ids"])
                if case["expected"].startswith("DENY"):
                    self.assertEqual(case["source_ids"], [])

    def test_validator_rejects_conflicting_gold_source(self):
        generated = copy.deepcopy(self.generated)
        case = generated[4][0]
        case["must_not_cite"].append(case["source_ids"][0])
        with self.assertRaisesRegex(ValueError, "both allowed and forbidden"):
            self.validate(generated)

    def test_review_snapshot_follows_terminal_event(self):
        documents = {doc["document_id"]: doc for doc in self.documents}
        terminal_by_document = {}
        for event in self.generated[2]:
            with self.subTest(document_id=event["document_id"], action=event["action"]):
                doc = documents[event["document_id"]]
                self.assertGreaterEqual(doc["updated_at"], event["at"][:10])
            if event["action"] in ("APPROVED", "ARCHIVED"):
                previous = terminal_by_document.get(event["document_id"])
                if previous is None or previous["at"] < event["at"]:
                    terminal_by_document[event["document_id"]] = event
        for document_id, event in terminal_by_document.items():
            expected_status = "Approved" if event["action"] == "APPROVED" else "Archived"
            self.assertEqual(documents[document_id]["status"], expected_status)

    def test_validator_rejects_stale_review_snapshot(self):
        documents = copy.deepcopy(self.documents)
        event = next(row for row in self.generated[2] if row["action"] == "APPROVED")
        document = next(row for row in documents if row["document_id"] == event["document_id"])
        document["updated_at"] = document["created_at"]
        with self.assertRaisesRegex(ValueError, "Document snapshot predates review"):
            validate_workflows(
                *self.generated, self.issues, documents, self.members,
                self.memberships, "2026-10-12"
            )

    def test_cross_project_note_is_rejected(self):
        generated = copy.deepcopy(self.generated)
        generated[1][0]["project_id"] = "NSC-PAY"
        with self.assertRaisesRegex(ValueError, "Invalid Task Note relation"):
            self.validate(generated)

    def test_unapproved_note_cannot_be_marked_as_knowledge(self):
        generated = copy.deepcopy(self.generated)
        generated[1][0]["knowledge_eligible"] = True
        with self.assertRaisesRegex(ValueError, "Invalid Task Note relation"):
            self.validate(generated)

    def test_self_review_is_rejected(self):
        generated = copy.deepcopy(self.generated)
        event = next(row for row in generated[2] if row["action"] == "APPROVED")
        document = next(row for row in self.documents if row["document_id"] == event["document_id"])
        event["actor_id"] = document["owner_id"]
        with self.assertRaisesRegex(ValueError, "Self-review"):
            self.validate(generated)

    def test_report_reviewer_without_permission_is_rejected(self):
        generated = copy.deepcopy(self.generated)
        report = generated[3][0]
        contributor = next(
            item["member_id"] for item in self.memberships
            if item["project_id"] == report["project_id"]
            and item["role"] == "contributor"
            and item["member_id"] != report["member_id"]
        )
        report["reviewed_by"] = contributor
        with self.assertRaisesRegex(ValueError, "Report reviewer lacks permission"):
            self.validate(generated)

    def test_rejected_report_cannot_become_knowledge(self):
        generated = copy.deepcopy(self.generated)
        report = next(row for row in generated[3] if row["status"] == "REJECTED")
        report["knowledge_eligible"] = True
        with self.assertRaisesRegex(ValueError, "Invalid Work Report knowledge status"):
            self.validate(generated)

    def test_manifest_covers_real_package_and_hard_cap(self):
        manifest = json.loads((PROJECT / "manifest.json").read_text(encoding="utf-8"))
        actual = {path.relative_to(PROJECT).as_posix() for path in PROJECT.rglob("*") if path.is_file()}
        listed = {row["path"] for row in manifest["file_inventory"]} | {"manifest.json"}
        self.assertEqual(actual, listed)
        self.assertLessEqual(len(actual), 160)
        self.assertEqual(manifest["canonical_counts"]["evaluation_cases"]["total"], 179)


if __name__ == "__main__":
    unittest.main()
