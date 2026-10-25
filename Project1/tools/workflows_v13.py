"""Deterministic, standalone Work Task and Work Note benchmark slice."""

from datetime import date, timedelta
from hashlib import sha256


STATUS_MAP = {
    "To Do": "TODO",
    "In Progress": "IN_PROGRESS",
    "In Review": "IN_REVIEW",
    "Blocked": "BLOCKED",
    "Done": "DONE",
}
TYPE_MAP = {"Task": "TASK", "Bug": "BUG", "Story": "STORY"}
WORKFLOW_STATUSES = ("Done", "In Review", "Blocked", "In Progress", "To Do")


def stable_id(kind, key):
    """ObjectId-shaped synthetic identifier; never a live MongoDB identifier."""
    return sha256(f"northstar-v1.3/{kind}/{key}".encode()).hexdigest()[:24]


def at(day, hour, minute=0):
    return f"{day}T{hour:02d}:{minute:02d}:00+07:00"


def next_workday(day, holidays):
    candidate = date.fromisoformat(day) + timedelta(days=1)
    while candidate.weekday() >= 5 or candidate in holidays:
        candidate += timedelta(days=1)
    return candidate.isoformat()


def _pick_documents(project_id, documents, issues_by_key):
    candidates = [
        doc for doc in documents
        if doc["project_id"] == project_id
        and doc["status"] == "Approved"
        and not doc["test_only"]
        and doc["created_at"] <= "2026-09-30"
        and any(
            key in issues_by_key and issues_by_key[key]["issue_type"] in TYPE_MAP
            for key in doc["source_issue_keys"]
        )
    ]
    candidates.sort(key=lambda doc: (doc["created_at"], doc["document_id"]))
    if len(candidates) < 2:
        raise ValueError(f"Two approved source documents required for {project_id}")
    return candidates[:2]


def _note_fields(issue):
    summary = issue["summary"]
    description = issue["description"]
    criterion = description.split("Acceptance Criteria: 1. ", 1)[-1].split(" 2. ", 1)[0].strip().rstrip(".")
    if criterion == description:
        criterion = "the stated task acceptance criteria"
    status = issue["status"]
    accomplishments = {
        "Done": f"Completed {summary}; recorded evidence that {criterion.lower()}.",
        "In Review": f"Prepared {summary} for review; the reviewer must verify that {criterion.lower()}.",
        "Blocked": f"Documented the unresolved dependency for {summary}; {criterion.lower()} is not yet verified.",
        "In Progress": f"Advanced {summary}; validation that {criterion.lower()} is still in progress.",
        "To Do": f"Scoped {summary} against the acceptance criteria; implementation has not started.",
    }[status]
    approach = {
        "Bug": f"Reproduced the failure path and checked the expected behavior: {criterion}.",
        "Story": f"Mapped the user requirement to the first acceptance check: {criterion}.",
        "Task": f"Followed the operational task steps and checked the required outcome: {criterion}.",
    }[issue["issue_type"]]
    purpose = description.split(" to ensure ", 1)
    reason = (
        f"The chosen approach supports {purpose[1].split(' Acceptance Criteria:', 1)[0].rstrip('.')} while keeping the decision traceable."
        if len(purpose) == 2 else
        f"This keeps the acceptance evidence for {summary.lower()} traceable to the task."
    )
    return accomplishments, approach, reason


def build_workflows(issues, documents, members, project_memberships, projects, holidays, as_of):
    """Return tasks, notes, review events, reports and independent gold cases."""
    issues_by_key = {issue["issue_key"]: issue for issue in issues}
    members_by_id = {member["member_id"]: member for member in members}
    active_project_members = {
        (item["project_id"], item["member_id"])
        for item in project_memberships if item["status"] == "active"
    }
    membership_roles = {
        (item["project_id"], item["member_id"]): item["role"]
        for item in project_memberships if item["status"] == "active"
    }
    tasks, notes, reviews, reports, cases = [], [], [], [], []
    for project in sorted(projects, key=lambda row: row["project_id"]):
        project_id = project["project_id"]
        docs = _pick_documents(project_id, documents, issues_by_key)
        pool = [
            issue for issue in issues
            if issue["project_id"] == project_id
            and issue["issue_type"] in TYPE_MAP
            and issue["assignee_id"] in members_by_id
            and members_by_id[issue["assignee_id"]]["account_status"] == "active"
            and (project_id, issue["assignee_id"]) in active_project_members
            and issue["created_at"][:10] < as_of
        ]
        eligible_keys = {issue["issue_key"] for issue in pool}
        anchor_key = next(
            (key for key in docs[0]["source_issue_keys"] if key in eligible_keys),
            None,
        )
        if anchor_key is None:
            raise ValueError(f"No eligible source task for {docs[0]['document_id']}")
        selected = [issues_by_key[anchor_key]]
        for status in WORKFLOW_STATUSES:
            match = next(
                (issue for issue in pool
                 if issue["status"] == status
                 and issue["issue_key"] not in {row["issue_key"] for row in selected}),
                None,
            )
            if match is None:
                raise ValueError(f"Missing {status} task fixture for {project_id}")
            selected.append(match)
        if len({row["issue_key"] for row in selected}) < 6:
            match = next(
                (issue for issue in pool if issue["issue_key"] not in {row["issue_key"] for row in selected}),
                None,
            )
            if match is None:
                raise ValueError(f"Need six distinct task fixtures for {project_id}")
            selected.append(match)
        selected = selected[:6]
        project_task_by_issue = {}
        for issue in selected:
            issue_key = issue["issue_key"]
            task_id = stable_id("task", issue_key)
            project_task_by_issue[issue_key] = task_id
            task = {
                "task_id": task_id,
                "key": f"WT-{issue_key}",
                "organization_id": "ORG-NSC",
                "project_id": project_id,
                "title": issue["summary"],
                "description": issue["description"],
                "type": TYPE_MAP[issue["issue_type"]],
                "status": STATUS_MAP[issue["status"]],
                "priority": "HIGH" if issue["priority"] in ("High", "Highest") else "LOW" if issue["priority"] == "Low" else "MEDIUM",
                "assignee_id": issue["assignee_id"],
                "created_by": issue["reporter_id"],
                "sprint_id": issue["sprint_id"],
                "source_issue_key": issue_key,
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "synthetic": True,
            }
            tasks.append(task)
            # A note is a member's confirmed work record, never an approved knowledge source.
            accomplishments, approach, reason = _note_fields(issue)
            note = {
                "note_id": stable_id("note", issue_key),
                "task_id": task_id,
                "project_id": project_id,
                "organization_id": "ORG-NSC",
                "author_id": issue["assignee_id"],
                "title": f"Work record for {issue_key}: {issue['summary']}",
                "accomplishments": accomplishments,
                "approach": approach,
                "reason": reason,
                "type": "TASK_NOTE",
                "status": "CONFIRMED",
                "knowledge_eligible": False,
                "created_at": issue["updated_at"],
                "updated_at": issue["updated_at"],
                "synthetic": True,
            }
            notes.append(note)

        for doc_index, doc in enumerate(docs):
            doc_id = doc["document_id"]
            version = str(doc["version"])
            draft_version = f"{int(float(version)) + 1}.0-draft"
            first_day = next_workday(doc["recorded_at"][:10], holidays)
            if first_day > as_of:
                raise ValueError(f"Document review after as-of date: {doc_id}")
            reviewer_id = next(
                member_id for member_id in sorted(members_by_id)
                if member_id != doc["owner_id"]
                and members_by_id[member_id]["account_status"] == "active"
                and membership_roles.get((project_id, member_id)) in ("owner", "tech_lead")
                and members_by_id[member_id]["org_id"] == "ORG-NSC"
            )
            actions = ["SUBMITTED", "APPROVED"] if doc_index else ["SUBMITTED", "CHANGES_REQUESTED", "RESUBMITTED", "APPROVED"]
            for action_index, action in enumerate(actions):
                reviews.append({
                    "event_id": stable_id("review", f"{doc_id}:{version}:{action_index}"),
                    "document_id": doc_id,
                    "version": version,
                    "project_id": project_id,
                    "organization_id": "ORG-NSC",
                    "action": action,
                    "actor_id": doc["owner_id"] if action in ("SUBMITTED", "RESUBMITTED") else reviewer_id,
                    "at": at(first_day, (9, 10, 11, 14)[action_index] if len(actions) == 4 else (9, 14)[action_index]),
                    "synthetic": True,
                })
            if doc_index == 0:
                draft_day = next_workday(first_day, holidays)
                if draft_day <= as_of:
                    reviews.append({
                        "event_id": stable_id("review", f"{doc_id}:draft-v2"),
                        "document_id": doc_id,
                        "version": draft_version,
                        "project_id": project_id,
                        "organization_id": "ORG-NSC",
                        "action": "DRAFT_SAVED",
                        "actor_id": doc["owner_id"],
                        "at": at(draft_day, 9),
                        "draft_content": f"Unapproved follow-up proposal for {doc['title']}.",
                        "knowledge_eligible": False,
                        "synthetic": True,
                    })

        leader_ids = [member_id for (pid, member_id), role in membership_roles.items() if pid == project_id and role == "tech_lead"]
        report_scope = "LEADER" if leader_ids else "MEMBER"
        report_member = (
            leader_ids[0] if leader_ids else
            next(task["assignee_id"] for task in tasks if task["project_id"] == project_id and membership_roles.get((project_id, task["assignee_id"])) == "contributor")
        )
        report_reviewer = next(
            member_id for member_id in sorted(members_by_id)
            if member_id != report_member
            and members_by_id[member_id]["account_status"] == "active"
            and membership_roles.get((project_id, member_id)) == "owner"
            and members_by_id[member_id]["org_id"] == "ORG-NSC"
        )
        anchor_task = project_task_by_issue[anchor_key]
        report_id = stable_id("report", project_id)
        reports.append({
            "report_id": report_id,
            "project_id": project_id,
            "organization_id": "ORG-NSC",
            "member_id": report_member,
            "report_scope": report_scope,
            "frequency": "WEEKLY",
            "period_start": "2026-09-28",
            "period_end": "2026-10-04",
            "due_at": at("2026-10-05", 17),
            "status": "CHANGES_REQUESTED" if project_id == "NSC-CHKO" else "REJECTED" if project_id == "NSC-PAY" else "APPROVED",
            "accomplishments": f"Reviewed delivery evidence for {docs[0]['title']} and the linked work task.",
            "approach": "Compared the task note, source issue and reviewed project document.",
            "reason": "Preserve the decision trail for the next project handover.",
            "blockers": None,
            "next_steps": "Apply the approved document during the next work cycle.",
            "document_ids": [docs[0]["document_id"]],
            "source_task_ids": [anchor_task],
            "created_at": at("2026-10-05", 9),
            "submitted_at": at("2026-10-05", 15),
            "reviewed_by": report_reviewer,
            "reviewed_at": at("2026-10-06", 14),
            "review_comment": "Revise the blocker evidence before resubmission." if project_id == "NSC-CHKO" else "Report evidence is insufficient for approval." if project_id == "NSC-PAY" else "Evidence and project scope confirmed.",
            "review_history": [
                {"action": "PENDING_REVIEW", "reviewer_id": report_member, "at": at("2026-10-05", 15)},
                {"action": "CHANGES_REQUESTED" if project_id == "NSC-CHKO" else "REJECTED" if project_id == "NSC-PAY" else "APPROVED", "reviewer_id": report_reviewer, "at": at("2026-10-06", 14)},
            ],
            "knowledge_eligible": project_id not in ("NSC-CHKO", "NSC-PAY"),
            "synthetic": True,
        })
        cases.append({
            "case_id": f"WF-{len(cases)+1:03d}",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": f"For {anchor_key}, which task note and approved document explain the work?",
            "expected": f"Task {anchor_task} has note {stable_id('note', anchor_key)} and approved document {docs[0]['document_id']}.",
            "source_ids": [anchor_task, stable_id("note", anchor_key), docs[0]["document_id"]] + ([report_id] if reports[-1]["status"] == "APPROVED" else []),
            "must_not_cite": [f"{docs[0]['document_id']}@{int(float(docs[0]['version'])) + 1}.0-draft"] + ([report_id] if reports[-1]["status"] != "APPROVED" else []),
            "principal_id": report_member,
            "tags": ["task_note_link", "approved_source", "project_scope"],
        })
        outsider = next(
            member["member_id"] for member in members
            if member["org_id"] != "ORG-NSC"
            and member["account_status"] == "active"
            and (project_id, member["member_id"]) not in active_project_members
        )
        cases.append({
            "case_id": f"WF-{len(cases)+1:03d}",
            "suite": "WORKFLOW_ACL",
            "answer_channel": "access",
            "query": f"Can {outsider} read the task note for {anchor_key}?",
            "expected": "DENY; do not reveal the note title, excerpt or existence.",
            "source_ids": [stable_id("note", anchor_key)],
            "must_not_cite": [stable_id("note", anchor_key)],
            "principal_id": outsider,
            "tags": ["cross_tenant", "project_membership", "pre_filter"],
        })
    superseded = next(doc for doc in documents if doc["document_id"] == "DOC-PAY-ADR-001")
    replacement = next(doc for doc in documents if doc["document_id"] == superseded["superseded_by"])
    pay_owner = next(
        member_id for (pid, member_id), role in membership_roles.items()
        if pid == "NSC-PAY" and role == "owner"
    )
    archived_fixture = next(doc for doc in documents if doc["document_id"] == "FIX-CONFLICT-POLICY")
    fixture_archive_day = next_workday(archived_fixture["recorded_at"][:10], holidays)
    for index, (action, hour) in enumerate((
        ("DRAFT_SAVED", 9),
        ("ARCHIVED", 14),
    )):
        reviews.append({
            "event_id": stable_id("review", f"{archived_fixture['document_id']}:archive:{index}"),
            "document_id": archived_fixture["document_id"],
            "version": str(archived_fixture["version"]),
            "project_id": archived_fixture["project_id"],
            "organization_id": "ORG-NSC",
            "action": action,
            "actor_id": archived_fixture["owner_id"],
            "at": at(fixture_archive_day, hour),
            "reason": "TEST_FIXTURE_REVOKED" if action == "ARCHIVED" else None,
            "knowledge_eligible": False,
            "synthetic": True,
        })
    first_doc = next(row for row in documents if row["document_id"] == reviews[0]["document_id"])
    cases.append({
        "case_id": f"WF-{len(cases)+1:03d}",
        "suite": "WORKFLOW_KNOWLEDGE",
        "answer_channel": "knowledge",
        "query": f"Is the unapproved follow-up to {first_doc['title']} an authoritative source?",
        "expected": "No. The latest approved version remains authoritative until a new version is approved.",
        "source_ids": [first_doc["document_id"]],
        "must_not_cite": [f"{first_doc['document_id']}@{int(float(first_doc['version'])) + 1}.0-draft"],
        "principal_id": reports[0]["member_id"],
        "tags": ["draft_exclusion", "versioning"],
    })
    former = next(member for member in members if member["account_status"] == "inactive")
    former_project = next(
        item["project_id"] for item in project_memberships
        if item["member_id"] == former["member_id"]
    )
    former_doc = next(
        doc for doc in documents
        if doc["project_id"] == former_project and doc["status"] == "Approved" and not doc["test_only"]
    )
    cases.append({
        "case_id": f"WF-{len(cases)+1:03d}",
        "suite": "WORKFLOW_ACL",
        "answer_channel": "access",
        "query": f"Can offboarded member {former['member_id']} read {former_doc['document_id']} now?",
        "expected": "DENY; historical authorship does not restore current access.",
        "source_ids": [former_doc["document_id"]],
        "must_not_cite": [former_doc["document_id"]],
        "principal_id": former["member_id"],
        "tags": ["offboarding", "revoked_access"],
    })
    cases.append({
        "case_id": f"WF-{len(cases)+1:03d}",
        "suite": "WORKFLOW_KNOWLEDGE",
        "answer_channel": "knowledge",
        "query": "Which payment ADR remains authoritative after the older ADR is superseded?",
        "expected": f"{replacement['document_id']} is current; {superseded['document_id']} is superseded and excluded from active citations.",
        "source_ids": [replacement["document_id"]],
        "must_not_cite": [superseded["document_id"]],
        "principal_id": pay_owner,
        "tags": ["supersession", "approved_version"],
    })
    cases.append({
        "case_id": f"WF-{len(cases)+1:03d}",
        "suite": "WORKFLOW_KNOWLEDGE",
        "answer_channel": "knowledge",
        "query": "May the archived conflicting policy fixture be cited as current policy?",
        "expected": "No. The test-only fixture is archived and excluded from official knowledge.",
        "source_ids": [archived_fixture["document_id"]],
        "must_not_cite": [archived_fixture["document_id"]],
        "principal_id": archived_fixture["owner_id"],
        "tags": ["archive", "test_fixture", "source_exclusion"],
    })
    rejected_report = next(report for report in reports if report["status"] == "REJECTED")
    cases.append({
        "case_id": f"WF-{len(cases)+1:03d}",
        "suite": "WORKFLOW_KNOWLEDGE",
        "answer_channel": "knowledge",
        "query": "Can the rejected payment work report be cited as approved knowledge?",
        "expected": "No. Rejected Work Reports are not knowledge eligible.",
        "source_ids": [rejected_report["report_id"]],
        "must_not_cite": [rejected_report["report_id"]],
        "principal_id": pay_owner,
        "tags": ["rejected_report", "source_exclusion"],
    })
    return tasks, notes, reviews, reports, cases


def validate_workflows(tasks, notes, reviews, reports, cases, issues, documents, members, memberships, as_of):
    """Raise on orphaned references, invalid ACL/timeline, or unsafe knowledge status."""
    task_by_id = {row["task_id"]: row for row in tasks}
    issue_by_key = {row["issue_key"]: row for row in issues}
    document_by_id = {row["document_id"]: row for row in documents}
    member_by_id = {row["member_id"]: row for row in members}
    project_member = {(row["project_id"], row["member_id"]) for row in memberships if row["status"] == "active"}
    historical_project_member = {(row["project_id"], row["member_id"]) for row in memberships}
    membership_roles = {(row["project_id"], row["member_id"]): row["role"] for row in memberships if row["status"] == "active"}
    if len(tasks) != 48 or len(task_by_id) != len(tasks):
        raise ValueError("Expected 48 unique Work Tasks")
    if len({row["note_id"] for row in notes}) != len(notes):
        raise ValueError("Duplicate Task Note ID")
    if len({row["event_id"] for row in reviews}) != len(reviews):
        raise ValueError("Duplicate document review event ID")
    if len({row["report_id"] for row in reports}) != len(reports):
        raise ValueError("Duplicate Work Report ID")
    for task in tasks:
        issue = issue_by_key.get(task["source_issue_key"])
        if not issue or task["project_id"] != issue["project_id"] or task["status"] != STATUS_MAP[issue["status"]]:
            raise ValueError(f"Invalid issue mapping: {task['key']}")
        if (task["project_id"], task["assignee_id"]) not in project_member:
            raise ValueError(f"Assignee outside project: {task['key']}")
    for note in notes:
        task = task_by_id.get(note["task_id"])
        member = member_by_id.get(note["author_id"])
        if not task or not member or note["project_id"] != task["project_id"] or note["knowledge_eligible"]:
            raise ValueError(f"Invalid Task Note relation: {note['note_id']}")
        if (note["project_id"], note["author_id"]) not in project_member:
            raise ValueError(f"Note author outside project: {note['note_id']}")
        if member["left_at"] and note["created_at"][:10] > member["left_at"]:
            raise ValueError(f"Note after offboarding: {note['note_id']}")
        if not (task["created_at"] <= note["created_at"] <= as_of + "T23:59:59+07:00"):
            raise ValueError(f"Note outside task timeline: {note['note_id']}")
    for event in reviews:
        doc = document_by_id.get(event["document_id"])
        if not doc or doc["project_id"] != event["project_id"] or event["actor_id"] not in member_by_id:
            raise ValueError(f"Invalid document review: {event['event_id']}")
        permitted_members = historical_project_member if event["action"] in ("SUBMITTED", "RESUBMITTED") else project_member
        if (event["project_id"], event["actor_id"]) not in permitted_members:
            raise ValueError(f"Reviewer outside project: {event['event_id']}")
        member = member_by_id[event["actor_id"]]
        if member["left_at"] and event["at"][:10] > member["left_at"]:
            raise ValueError(f"Review after offboarding: {event['event_id']}")
        if event["action"] in ("APPROVED", "CHANGES_REQUESTED") and event["actor_id"] == doc["owner_id"]:
            raise ValueError(f"Self-review: {event['event_id']}")
        if event["action"] in ("APPROVED", "CHANGES_REQUESTED", "ARCHIVED") and membership_roles.get((event["project_id"], event["actor_id"])) not in ("owner", "tech_lead"):
            raise ValueError(f"Review permission missing: {event['event_id']}")
        if not (doc["recorded_at"] < event["at"] <= as_of + "T23:59:59+07:00"):
            raise ValueError(f"Review outside document timeline: {event['event_id']}")
        if event["action"] == "DRAFT_SAVED" and event["knowledge_eligible"]:
            raise ValueError(f"Unapproved draft is knowledge eligible: {event['event_id']}")
    review_groups = {}
    for event in reviews:
        review_groups.setdefault((event["document_id"], event["version"]), []).append(event)
    for source, events in review_groups.items():
        actions = [row["action"] for row in sorted(events, key=lambda row: row["at"])]
        if actions not in (["SUBMITTED", "APPROVED"], ["SUBMITTED", "CHANGES_REQUESTED", "RESUBMITTED", "APPROVED"], ["DRAFT_SAVED", "ARCHIVED"], ["DRAFT_SAVED"]):
            raise ValueError(f"Invalid review lifecycle: {source}")
    for report in reports:
        if report["member_id"] == report["reviewed_by"] or report["period_end"] < report["period_start"]:
            raise ValueError(f"Invalid Work Report review: {report['report_id']}")
        if report["status"] not in ("APPROVED", "CHANGES_REQUESTED", "REJECTED") or report["knowledge_eligible"] != (report["status"] == "APPROVED"):
            raise ValueError(f"Invalid Work Report knowledge status: {report['report_id']}")
        if not (report["period_end"] < report["created_at"][:10] and report["submitted_at"] <= report["due_at"]):
            raise ValueError(f"Invalid Work Report period: {report['report_id']}")
        if not (report["created_at"] <= report["submitted_at"] <= report["reviewed_at"] <= as_of + "T23:59:59+07:00"):
            raise ValueError(f"Invalid Work Report chronology: {report['report_id']}")
        if any((report["project_id"], member_id) not in project_member for member_id in (report["member_id"], report["reviewed_by"])):
            raise ValueError(f"Report actor outside project: {report['report_id']}")
        if membership_roles.get((report["project_id"], report["reviewed_by"])) != "owner":
            raise ValueError(f"Report reviewer lacks permission: {report['report_id']}")
        if report["report_scope"] == "LEADER" and membership_roles.get((report["project_id"], report["member_id"])) != "tech_lead":
            raise ValueError(f"Leader report has non-leader author: {report['report_id']}")
        if report["review_history"][-1]["action"] != report["status"]:
            raise ValueError(f"Report review history mismatch: {report['report_id']}")
        if not all(doc_id in document_by_id and document_by_id[doc_id]["project_id"] == report["project_id"] for doc_id in report["document_ids"]):
            raise ValueError(f"Report document outside project: {report['report_id']}")
        if not all(task_id in task_by_id and task_by_id[task_id]["project_id"] == report["project_id"] for task_id in report["source_task_ids"]):
            raise ValueError(f"Report task outside project: {report['report_id']}")
    if len(cases) != 21 or len({row["case_id"] for row in cases}) != len(cases):
        raise ValueError("Expected twenty-one unique workflow evaluation cases")
    all_sources = set(task_by_id) | {row["note_id"] for row in notes} | set(document_by_id) | {row["report_id"] for row in reports}
    if any(source_id not in all_sources for case in cases for source_id in case["source_ids"]):
        raise ValueError("Workflow evaluation references a missing source")
