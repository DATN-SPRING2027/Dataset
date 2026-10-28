"""Deterministic Continuum Task Workspace & Group Note (Task Note, Document, Work Report) slice for Northstar v1.4."""

from datetime import date, timedelta
from hashlib import sha256
import re


STATUS_MAP = {
    "To Do": "TODO",
    "In Progress": "IN_PROGRESS",
    "In Review": "IN_REVIEW",
    "Blocked": "BLOCKED",
    "Done": "DONE",
}
TYPE_MAP = {"Task": "TASK", "Bug": "BUG", "Story": "STORY"}
WORKFLOW_STATUSES = ("Done", "In Review", "Blocked", "In Progress", "To Do")
TASK_KEY_RE = re.compile(r"^[A-Z0-9]{2,10}-[1-9][0-9]*$")

ALLOWED_TRANSITIONS = {
    "TODO": {"IN_PROGRESS", "BLOCKED", "CANCELLED"},
    "IN_PROGRESS": {"TODO", "IN_REVIEW", "BLOCKED", "DONE", "CANCELLED"},
    "IN_REVIEW": {"IN_PROGRESS", "BLOCKED", "DONE", "CANCELLED"},
    "BLOCKED": {"TODO", "IN_PROGRESS", "IN_REVIEW", "CANCELLED"},
    "DONE": {"IN_PROGRESS"},
    "CANCELLED": {"TODO"},
}

# Explicit Continuum Organization ADMIN (Manager) roles in ORG-NSC (never inferred from job title)
ORG_NSC_MANAGERS = {"M-001", "M-002"}

# Explicit Continuum Project TEAM_LEADER (Leader) roles per Northstar project
PROJECT_TEAM_LEADERS = {
    "NSC-CAT": "M-003",
    "NSC-SRCH": "M-004",
    "NSC-CART": "M-005",
    "NSC-CHKO": "M-005",
    "NSC-PAY": "M-006",
    "NSC-INV": "M-007",
    "NSC-ORD": "M-008",
    "NSC-PLAT": "M-009",
}

# Verified zero-activity windows across all 2,500 issues / comments / changelogs / docs for real-life disruptions
NORTHSTAR_DISRUPTION_WINDOWS = {
    "NSC-CAT": {
        "disruption_id": "DIS-NSC-CAT-SICK-01",
        "kind": "sick_leave",
        "affected_member_id": "M-019",
        "backup_member_id": "M-020",
        "unavailable_from": "2026-08-19T08:00:00+07:00",
        "unavailable_to": "2026-08-20T22:00:00+07:00",
        "handover_day": "2026-08-19",
        "completion_day": "2026-08-21",
        "summary_vi_en": "Liam Vance (M-019) nghỉ ốm sốt siêu vi 2 ngày (19-20/08/2026); bàn giao validation CSV schema cho Emma Watson (M-020).",
    },
    "NSC-PAY": {
        "disruption_id": "DIS-NSC-PAY-STORM-01",
        "kind": "storm_network_outage",
        "affected_member_id": "M-027",
        "backup_member_id": "M-028",
        "unavailable_from": "2026-09-14T08:00:00+07:00",
        "unavailable_to": "2026-09-15T22:00:00+07:00",
        "handover_day": "2026-09-14",
        "completion_day": "2026-09-16",
        "summary_vi_en": "Mưa bão lớn gây đứt cáp quang khu vực WFH của Benjamin Anderson (M-027) ngày 14-15/09/2026; Mia Thomas (M-028) tiếp nhận replay test PulsePay.",
    },
    "NSC-INV": {
        "disruption_id": "DIS-NSC-INV-PTO-01",
        "kind": "annual_leave_pto",
        "affected_member_id": "M-029",
        "backup_member_id": "M-030",
        "unavailable_from": "2026-08-26T08:00:00+07:00",
        "unavailable_to": "2026-08-27T22:00:00+07:00",
        "handover_day": "2026-08-26",
        "completion_day": "2026-08-28",
        "summary_vi_en": "Lucas Jackson (M-029) nghỉ phép năm đã duyệt (26-27/08/2026); Charlotte White (M-030) nhận bàn giao kiểm thử khóa Redis TTL.",
    },
}


def stable_id(kind, key):
    """ObjectId-shaped synthetic identifier; never a live MongoDB identifier."""
    return sha256(f"northstar-v1.3/{kind}/{key}".encode()).hexdigest()[:24]


def project_code(project_id):
    """Continuum project code matching ^[A-Z0-9]{2,10}$ (e.g. NSC-CAT -> NSCCAT)."""
    return project_id.replace("-", "")


def at(day, hour, minute=0, second=0):
    return f"{day}T{hour:02d}:{minute:02d}:{second:02d}+07:00"


def next_workday(day, holidays):
    candidate = date.fromisoformat(day) + timedelta(days=1)
    while candidate.weekday() >= 5 or candidate in holidays:
        candidate += timedelta(days=1)
    return candidate.isoformat()


def _dual_review_meta(index, org_id="ORG-NSC", project_id=None, as_of="2026-10-12", category="normal", mandatory=None, forbidden=None):
    return {
        "organization_id": org_id,
        "project_id": project_id,
        "as_of_date": as_of,
        "case_category": category,
        "mandatory_points": mandatory or [],
        "forbidden_claims": forbidden or [],
        "split": "test" if index % 4 == 0 else "dev",
        "review_status": "unreviewed",
        "review_status_label_vi": "chưa duyệt",
        "reviewer_1": None,
        "reviewer_2": None,
        "adjudication_status": "pending_dual_review",
        "adjudication_notes": None,
    }


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


def _build_steps(task_key, summary, status):
    subject = summary.rstrip(".")
    all_done = status == "DONE"
    first_done = status in ("IN_PROGRESS", "IN_REVIEW", "BLOCKED", "DONE")
    second_done = status in ("IN_REVIEW", "DONE")
    return [
        {"id": f"{task_key}-S1", "text": f"Confirm contract & tenant guardrails for {subject.lower()}", "done": first_done},
        {"id": f"{task_key}-S2", "text": "Implement core logic and automated integration fixture", "done": second_done},
        {"id": f"{task_key}-S3", "text": "Verify staging telemetry, audit event, and peer review sign-off", "done": all_done},
    ]


def _build_task_events_and_worklogs(task, is_ot=False, work_mode="regular_hours", extra_reason=None):
    tid = task["task_id"]
    pid = task["project_id"]
    creator = task["created_by"]
    assignee = task["assignee_id"] or creator
    c_ts = task["created_at"]
    u_ts = task["updated_at"]
    st = task["status"]

    events = [
        {
            "event_id": stable_id("task_event", f"{tid}:created"),
            "task_id": tid,
            "project_id": pid,
            "organization_id": "ORG-NSC",
            "type": "TASK_CREATED",
            "actor_id": creator,
            "occurred_at": c_ts,
            "from_status": None,
            "to_status": "TODO",
            "reason": None,
            "is_overtime": False,
            "work_mode": "regular_hours",
        }
    ]
    worklogs = []
    comments = []

    if st == "TODO":
        return events, worklogs, comments

    mid_day = c_ts[:10]
    mid_ts = at(mid_day, 10, 15) if at(mid_day, 10, 15) > c_ts and at(mid_day, 10, 15) <= u_ts else c_ts

    if st == "CANCELLED":
        events.append({
            "event_id": stable_id("task_event", f"{tid}:cancelled"),
            "task_id": tid,
            "project_id": pid,
            "organization_id": "ORG-NSC",
            "type": "TASK_STATUS_TRANSITIONED",
            "actor_id": creator,
            "occurred_at": u_ts,
            "from_status": "TODO",
            "to_status": "CANCELLED",
            "reason": extra_reason or "Superseded by consolidated multi-tenant contract specification.",
            "is_overtime": False,
            "work_mode": "regular_hours",
        })
        comments.append({
            "comment_id": stable_id("task_comment", f"{tid}:c1"),
            "task_id": tid,
            "project_id": pid,
            "organization_id": "ORG-NSC",
            "author_id": creator,
            "actor_type": "human",
            "body": extra_reason or "Cancelled duplicate task after scope consolidation in sprint refinement.",
            "created_at": u_ts,
            "is_overtime": False,
            "work_mode": "regular_hours",
        })
        return events, worklogs, comments

    # Transition TODO -> IN_PROGRESS
    events.append({
        "event_id": stable_id("task_event", f"{tid}:in_progress"),
        "task_id": tid,
        "project_id": pid,
        "organization_id": "ORG-NSC",
        "type": "TASK_STATUS_TRANSITIONED",
        "actor_id": assignee,
        "occurred_at": mid_ts if st != "IN_PROGRESS" else u_ts,
        "from_status": "TODO",
        "to_status": "IN_PROGRESS",
        "reason": None,
        "is_overtime": False if st != "IN_PROGRESS" else is_ot,
        "work_mode": "regular_hours" if st != "IN_PROGRESS" else work_mode,
    })

    wl_minutes = 210 if is_ot else 180
    worklogs.append({
        "worklog_id": stable_id("worklog", f"{tid}:wl1"),
        "task_id": tid,
        "project_id": pid,
        "organization_id": "ORG-NSC",
        "author_id": assignee,
        "minutes": wl_minutes,
        "note": (
            f"[OT 17:00-22:00+07:00] Executed sprint crunch verification for {task['title']}."
            if is_ot else f"Implemented and tested acceptance steps for {task['title']}."
        ),
        "logged_at": u_ts,
        "created_at": u_ts,
        "is_overtime": is_ot,
        "work_mode": work_mode,
    })
    events.append({
        "event_id": stable_id("task_event", f"{tid}:wl1"),
        "task_id": tid,
        "project_id": pid,
        "organization_id": "ORG-NSC",
        "type": "TASK_WORKLOG_ADDED",
        "actor_id": assignee,
        "occurred_at": u_ts,
        "from_status": None,
        "to_status": None,
        "reason": None,
        "is_overtime": is_ot,
        "work_mode": work_mode,
    })

    if st == "BLOCKED":
        events.append({
            "event_id": stable_id("task_event", f"{tid}:blocked"),
            "task_id": tid,
            "project_id": pid,
            "organization_id": "ORG-NSC",
            "type": "TASK_STATUS_TRANSITIONED",
            "actor_id": assignee,
            "occurred_at": u_ts,
            "from_status": "IN_PROGRESS",
            "to_status": "BLOCKED",
            "reason": extra_reason or "Blocked on upstream partner sandbox fixture and retry contract confirmation.",
            "is_overtime": is_ot,
            "work_mode": work_mode,
        })
    elif st == "IN_REVIEW":
        events.append({
            "event_id": stable_id("task_event", f"{tid}:in_review"),
            "task_id": tid,
            "project_id": pid,
            "organization_id": "ORG-NSC",
            "type": "TASK_STATUS_TRANSITIONED",
            "actor_id": assignee,
            "occurred_at": u_ts,
            "from_status": "IN_PROGRESS",
            "to_status": "IN_REVIEW",
            "reason": None,
            "is_overtime": is_ot,
            "work_mode": work_mode,
        })
    elif st == "DONE":
        rev_ts = mid_ts if mid_ts <= u_ts else u_ts
        events.append({
            "event_id": stable_id("task_event", f"{tid}:in_review"),
            "task_id": tid,
            "project_id": pid,
            "organization_id": "ORG-NSC",
            "type": "TASK_STATUS_TRANSITIONED",
            "actor_id": assignee,
            "occurred_at": rev_ts,
            "from_status": "IN_PROGRESS",
            "to_status": "IN_REVIEW",
            "reason": None,
            "is_overtime": False,
            "work_mode": "regular_hours",
        })
        events.append({
            "event_id": stable_id("task_event", f"{tid}:done"),
            "task_id": tid,
            "project_id": pid,
            "organization_id": "ORG-NSC",
            "type": "TASK_STATUS_TRANSITIONED",
            "actor_id": assignee,
            "occurred_at": u_ts,
            "from_status": "IN_REVIEW",
            "to_status": "DONE",
            "reason": None,
            "is_overtime": is_ot,
            "work_mode": work_mode,
        })

    comments.append({
        "comment_id": stable_id("task_comment", f"{tid}:c1"),
        "task_id": tid,
        "project_id": pid,
        "organization_id": "ORG-NSC",
        "author_id": assignee,
        "actor_type": "human",
        "body": extra_reason or f"Updated Continuum task {task['key']} ({st}): verified checklist progress and tenant isolation.",
        "created_at": u_ts,
        "is_overtime": is_ot,
        "work_mode": work_mode,
    })
    events.sort(key=lambda item: item["occurred_at"])
    return events, worklogs, comments


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
    """Return Continuum tasks, task notes, document reviews, work reports, and workflow gold cases."""
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
    project_anchors = {}

    for p_idx, project in enumerate(sorted(projects, key=lambda row: row["project_id"])):
        project_id = project["project_id"]
        p_code = project_code(project_id)
        prefix = project_id.replace("NSC-", "")
        squad_leader = PROJECT_TEAM_LEADERS[project_id]
        org_manager = "M-002" if project_id != "NSC-PLAT" else "M-001"
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
        for seq_num, issue in enumerate(selected, start=1):
            issue_key = issue["issue_key"]
            task_id = stable_id("task", issue_key)
            project_task_by_issue[issue_key] = task_id
            c_status = STATUS_MAP[issue["status"]]
            t_key = f"{p_code}-{seq_num}"
            is_ot = bool(issue.get("is_overtime", False))
            w_mode = issue.get("work_mode", "regular_hours")
            if w_mode not in ("regular_hours", "evening_overtime", "weekend_incident_ot"):
                w_mode = "regular_hours"

            task = {
                "task_id": task_id,
                "key": t_key,
                "legacy_key": f"WT-{issue_key}",
                "organization_id": "ORG-NSC",
                "continuum_organization_id": stable_id("org", "ORG-NSC"),
                "project_id": project_id,
                "continuum_project_id": stable_id("project", project_id),
                "title": issue["summary"],
                "description": issue["description"],
                "type": TYPE_MAP[issue["issue_type"]],
                "status": c_status,
                "priority": "HIGH" if issue["priority"] in ("High", "Highest") else "LOW" if issue["priority"] == "Low" else "MEDIUM",
                "assignee_id": issue["assignee_id"],
                "created_by": issue["reporter_id"],
                "parent_id": None,
                "sprint_id": issue["sprint_id"],
                "continuum_sprint_id": stable_id("sprint", issue["sprint_id"]),
                "labels": [lb[:40] for lb in issue.get("labels", ["commerce", "synthetic"])[:10]],
                "steps": _build_steps(t_key, issue["summary"], c_status),
                "start_date": issue["created_at"][:10],
                "due_date": issue["due_date"],
                "completed_at": issue["updated_at"] if c_status == "DONE" else None,
                "version": 3 if c_status == "DONE" else 2 if c_status in ("IN_PROGRESS", "IN_REVIEW", "BLOCKED") else 1,
                "is_overtime": is_ot,
                "work_mode": w_mode,
                "disruption_id": None,
                "source_issue_key": issue_key,
                "created_at": issue["created_at"],
                "updated_at": issue["updated_at"],
                "synthetic": True,
            }
            ev_list, wl_list, cm_list = _build_task_events_and_worklogs(task, is_ot=is_ot, work_mode=w_mode)
            task["task_events"] = ev_list
            task["worklogs"] = wl_list
            task["comments"] = cm_list
            tasks.append(task)

            accomplishments, approach, reason = _note_fields(issue)
            notes.append({
                "note_id": stable_id("note", issue_key),
                "task_id": task_id,
                "project_id": project_id,
                "organization_id": "ORG-NSC",
                "author_id": issue["assignee_id"],
                "title": f"Work record for {issue_key}: {issue['summary']}"[:160],
                "accomplishments": accomplishments,
                "approach": approach,
                "reason": reason,
                "type": "TASK_NOTE",
                "status": "CONFIRMED",
                "knowledge_eligible": False,
                "is_overtime": is_ot,
                "work_mode": w_mode,
                "created_at": issue["updated_at"],
                "updated_at": issue["updated_at"],
                "synthetic": True,
            })

        anchor_task = project_task_by_issue[anchor_key]
        contributors = sorted(
            mid for (pid, mid), role in membership_roles.items()
            if pid == project_id and role == "contributor" and mid not in ORG_NSC_MANAGERS and mid != squad_leader
        )

        # Task #7 per project: 1-level Subtask (with real-life handover/disruption where applicable)
        disruption = NORTHSTAR_DISRUPTION_WINDOWS.get(project_id)
        sub_id = stable_id("subtask", f"{project_id}:sub-07")
        sub_key = f"{p_code}-7"
        if disruption:
            sub_assignee = disruption["backup_member_id"]
            h_day = disruption["handover_day"]
            c_day = disruption["completion_day"]
            s_num = min(13, max(1, ((date.fromisoformat(c_day) - date(2026, 4, 14)).days // 14) + 1))
            sub_sprint = f"SPRINT-{prefix}-{s_num:02d}"
            sub_title = f"Handover verification subtask ({disruption['kind']}): {issues_by_key[anchor_key]['summary']}"[:250]
            sub_desc = (
                f"Subtask bàn giao thực tế ({disruption['disruption_id']}): {disruption['summary_vi_en']} "
                f"Đảm bảo không gián đoạn tiến độ {project_id} và giữ nguyên kiểm soát tenant."
            )
            sub_created = at(h_day, 9, 20)
            sub_updated = at(c_day, 15, 40)
            sub_reason = disruption["summary_vi_en"]
            sub_dis_id = disruption["disruption_id"]
        else:
            sub_assignee = contributors[0]
            sub_sprint = f"SPRINT-{prefix}-13"
            sub_title = f"Subtask checklist & contract verification: {issues_by_key[anchor_key]['summary']}"[:250]
            sub_desc = f"1-level Continuum subtask breaking down regression & contract checks under parent {anchor_key}."
            sub_created = at("2026-10-01", 9, 30)
            sub_updated = at("2026-10-02", 16, 10)
            sub_reason = f"Completed 1-level subtask verification under parent task {p_code}-1."
            sub_dis_id = None

        subtask = {
            "task_id": sub_id,
            "key": sub_key,
            "legacy_key": None,
            "organization_id": "ORG-NSC",
            "continuum_organization_id": stable_id("org", "ORG-NSC"),
            "project_id": project_id,
            "continuum_project_id": stable_id("project", project_id),
            "title": sub_title,
            "description": sub_desc,
            "type": "TASK",
            "status": "DONE",
            "priority": "HIGH" if disruption else "MEDIUM",
            "assignee_id": sub_assignee,
            "created_by": squad_leader,
            "parent_id": anchor_task,
            "sprint_id": sub_sprint,
            "continuum_sprint_id": stable_id("sprint", sub_sprint),
            "labels": ["subtask", "handover" if disruption else "verification", "continuum-native"],
            "steps": _build_steps(sub_key, sub_title, "DONE"),
            "start_date": sub_created[:10],
            "due_date": sub_updated[:10],
            "completed_at": sub_updated,
            "version": 3,
            "is_overtime": False,
            "work_mode": "regular_hours",
            "disruption_id": sub_dis_id,
            "source_issue_key": anchor_key,
            "created_at": sub_created,
            "updated_at": sub_updated,
            "synthetic": True,
        }
        ev_list, wl_list, cm_list = _build_task_events_and_worklogs(subtask, extra_reason=sub_reason)
        if disruption:
            ev_list.insert(1, {
                "event_id": stable_id("task_event", f"{sub_id}:handover"),
                "task_id": sub_id,
                "project_id": project_id,
                "organization_id": "ORG-NSC",
                "type": "TASK_UPDATED",
                "actor_id": squad_leader,
                "occurred_at": at(disruption["handover_day"], 9, 25),
                "from_status": None,
                "to_status": None,
                "reason": f"Reassigned from {disruption['affected_member_id']} to {sub_assignee}: {disruption['kind']}",
                "is_overtime": False,
                "work_mode": "regular_hours",
            })
            ev_list.sort(key=lambda item: item["occurred_at"])
        subtask["task_events"] = ev_list
        subtask["worklogs"] = wl_list
        subtask["comments"] = cm_list
        tasks.append(subtask)

        notes.append({
            "note_id": stable_id("note", f"{project_id}:sub-07"),
            "task_id": sub_id,
            "project_id": project_id,
            "organization_id": "ORG-NSC",
            "author_id": sub_assignee,
            "title": (
                f"Ghi nhận bàn giao ({disruption['kind']}) cho {sub_key}"
                if disruption else f"Subtask verification note for {sub_key}"
            )[:160],
            "accomplishments": sub_reason,
            "approach": "Tiếp nhận branch, chạy bộ kiểm thử cô lập tenant trên staging-sim và đối chiếu tài liệu đã duyệt.",
            "reason": "Bảo đảm chuỗi truy vết công việc liên tục khi phát sinh nghỉ ốm/mất mạng/nghỉ phép mà không vi phạm lịch làm việc.",
            "type": "TASK_NOTE",
            "status": "CONFIRMED",
            "knowledge_eligible": False,
            "is_overtime": False,
            "work_mode": "regular_hours",
            "created_at": sub_updated,
            "updated_at": sub_updated,
            "synthetic": True,
        })

        # Task #8 per project: CANCELLED governance/change-request task (4 projects) or Rework IN_REVIEW task (4 projects)
        t8_id = stable_id("extra_task", f"{project_id}:task-08")
        t8_key = f"{p_code}-8"
        is_cancelled_slot = p_idx % 2 == 1
        t8_assignee = None if is_cancelled_slot else contributors[min(1, len(contributors) - 1)]
        t8_status = "CANCELLED" if is_cancelled_slot else "IN_REVIEW"
        t8_title = (
            f"Cancelled legacy export stub superseded by unified contract ({project_id})"
            if is_cancelled_slot else f"Customer CR & edge-case rework verification ({project_id})"
        )
        t8_reason = (
            "Cancelled after Meridian pilot sync consolidated schema validation into canonical endpoint."
            if is_cancelled_slot else
            "Reworked edge-case rounding and retry guard after QA code review feedback."
        )
        task8 = {
            "task_id": t8_id,
            "key": t8_key,
            "legacy_key": None,
            "organization_id": "ORG-NSC",
            "continuum_organization_id": stable_id("org", "ORG-NSC"),
            "project_id": project_id,
            "continuum_project_id": stable_id("project", project_id),
            "title": t8_title,
            "description": t8_reason,
            "type": "STORY" if not is_cancelled_slot else "TASK",
            "status": t8_status,
            "priority": "LOW" if is_cancelled_slot else "HIGH",
            "assignee_id": t8_assignee,
            "created_by": squad_leader,
            "parent_id": None,
            "sprint_id": f"SPRINT-{prefix}-13",
            "continuum_sprint_id": stable_id("sprint", f"SPRINT-{prefix}-13"),
            "labels": ["cancelled-scope"] if is_cancelled_slot else ["rework", "customer-cr"],
            "steps": _build_steps(t8_key, t8_title, t8_status),
            "start_date": "2026-10-05",
            "due_date": "2026-10-14",
            "completed_at": None,
            "version": 2,
            "is_overtime": False,
            "work_mode": "regular_hours",
            "disruption_id": None,
            "source_issue_key": anchor_key,
            "created_at": at("2026-10-05", 9, 10),
            "updated_at": at("2026-10-07", 15, 20),
            "synthetic": True,
        }
        ev8, wl8, cm8 = _build_task_events_and_worklogs(task8, extra_reason=t8_reason)
        task8["task_events"] = ev8
        task8["worklogs"] = wl8
        task8["comments"] = cm8
        tasks.append(task8)

        note8_author = squad_leader if is_cancelled_slot else t8_assignee
        notes.append({
            "note_id": stable_id("note", f"{project_id}:task-08"),
            "task_id": t8_id,
            "project_id": project_id,
            "organization_id": "ORG-NSC",
            "author_id": note8_author,
            "title": f"Task note for {t8_key}: {t8_title}"[:160],
            "accomplishments": t8_reason,
            "approach": "Recorded scope disposition and linked canonical specification to prevent duplicate engineering effort.",
            "reason": "Keep cancelled/reworked decisions auditable inside the Continuum task tab without polluting official AI knowledge.",
            "type": "TASK_NOTE",
            "status": "CONFIRMED",
            "knowledge_eligible": False,
            "is_overtime": False,
            "work_mode": "regular_hours",
            "created_at": at("2026-10-07", 15, 25),
            "updated_at": at("2026-10-07", 15, 25),
            "synthetic": True,
        })

        # Document review events (preserve all 58 original IDs)
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
                and (
                    membership_roles.get((project_id, member_id)) in ("owner", "tech_lead")
                    or member_id in ORG_NSC_MANAGERS
                )
                and (project_id, member_id) in active_project_members
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

        # Preserve original 8 Work Reports (report_id = stable_id("report", project_id))
        leader_ids = [member_id for (pid, member_id), role in membership_roles.items() if pid == project_id and role == "tech_lead"]
        orig_scope = "LEADER" if leader_ids else "MEMBER"
        orig_member = (
            leader_ids[0] if leader_ids else
            next(
                task["assignee_id"] for task in tasks
                if task["project_id"] == project_id
                and task["assignee_id"] in contributors
            )
        )
        orig_reviewer = next(
            member_id for member_id in sorted(members_by_id)
            if member_id != orig_member
            and members_by_id[member_id]["account_status"] == "active"
            and membership_roles.get((project_id, member_id)) == "owner"
            and members_by_id[member_id]["org_id"] == "ORG-NSC"
        )
        report_id = stable_id("report", project_id)
        orig_status = "CHANGES_REQUESTED" if project_id == "NSC-CHKO" else "REJECTED" if project_id == "NSC-PAY" else "APPROVED"
        reports.append({
            "report_id": report_id,
            "project_id": project_id,
            "organization_id": "ORG-NSC",
            "member_id": orig_member,
            "report_scope": orig_scope,
            "report_type": "WEEKLY",
            "frequency": "WEEKLY",
            "period_key": "2026-W40",
            "period_start": "2026-09-28",
            "period_end": "2026-10-04",
            "is_overdue": False,
            "roster_submission_state": orig_status,
            "due_at": at("2026-10-05", 17),
            "status": orig_status,
            "accomplishments": f"Reviewed delivery evidence for {docs[0]['title']} and the linked work task.",
            "approach": "Compared the task note, source issue and reviewed project document.",
            "reason": "Preserve the decision trail for the next project handover.",
            "blockers": "Pending reproducible staging trace on P0 blocker." if project_id in ("NSC-CHKO", "NSC-PAY") else None,
            "next_steps": "Apply the approved document during the next work cycle.",
            "document_ids": [docs[0]["document_id"]],
            "source_task_ids": [anchor_task],
            "created_at": at("2026-10-05", 9),
            "submitted_at": at("2026-10-05", 15),
            "reviewed_by": orig_reviewer,
            "reviewed_at": at("2026-10-06", 14),
            "review_comment": "Revise the blocker evidence before resubmission." if project_id == "NSC-CHKO" else "Report evidence is insufficient for approval." if project_id == "NSC-PAY" else "Evidence and project scope confirmed.",
            "review_history": [
                {"action": "PENDING_REVIEW", "reviewer_id": orig_member, "at": at("2026-10-05", 15)},
                {"action": orig_status, "reviewer_id": orig_reviewer, "at": at("2026-10-06", 14)},
            ],
            "knowledge_eligible": orig_status == "APPROVED",
            "synthetic": True,
        })

        # Counterpart WEEKLY report so EVERY project has BOTH MEMBER->Leader and LEADER->Manager (Org ADMIN)!
        counterpart_id = stable_id("report_counterpart_weekly", project_id)
        if orig_scope == "LEADER":
            # Add MEMBER -> TEAM_LEADER weekly report for NSC-CAT and NSC-SRCH
            cp_member = contributors[0]
            cp_reviewer = squad_leader
            cp_scope = "MEMBER"
            cp_accomplishments = (
                f"Hoàn tất kiểm thử subtask {sub_key} và cập nhật tiến độ thực thi cho {docs[0]['title']} "
                f"(kể cả bàn giao nghỉ ốm {disruption['disruption_id']})."
                if disruption else
                f"Completed sprint implementation and regression checks for {sub_key} and {docs[1]['title']}."
            )
        else:
            # Add LEADER -> Organization ADMIN Manager weekly report for NSC-CART, NSC-CHKO, NSC-PAY, NSC-INV, NSC-ORD, NSC-PLAT
            cp_member = squad_leader
            cp_reviewer = org_manager
            cp_scope = "LEADER"
            cp_accomplishments = (
                f"Báo cáo cấp Leader lên Manager ({org_manager}): tổng hợp tiến độ Sprint 13, rủi ro OT 17:00-22:00 và kiểm soát blocker của {project_id}."
            )
        reports.append({
            "report_id": counterpart_id,
            "project_id": project_id,
            "organization_id": "ORG-NSC",
            "member_id": cp_member,
            "report_scope": cp_scope,
            "report_type": "WEEKLY",
            "frequency": "WEEKLY",
            "period_key": "2026-W41",
            "period_start": "2026-10-05",
            "period_end": "2026-10-11",
            "is_overdue": False,
            "roster_submission_state": "APPROVED",
            "due_at": at("2026-10-12", 17),
            "status": "APPROVED",
            "accomplishments": cp_accomplishments,
            "approach": "Đối chiếu trực tiếp worklog, checklist subtask, Task Note và Project Document đã duyệt trước khi trình duyệt.",
            "reason": "Đảm bảo đủ cả hai luồng báo cáo Member→Leader và Leader→Manager theo đúng phân quyền Continuum Capture.",
            "blockers": "Tiếp tục theo dõi sát P0 idempotency/webhook gate trước mốc 16/10." if project_id in ("NSC-CHKO", "NSC-PAY") else None,
            "next_steps": "Hoàn tất nghiệm thu Sprint 13 và chuẩn bị tài liệu release readiness.",
            "document_ids": [docs[1]["document_id"]],
            "source_task_ids": [anchor_task, sub_id],
            "created_at": at("2026-10-12", 8, 45),
            "submitted_at": at("2026-10-12", 10, 30),
            "reviewed_by": cp_reviewer,
            "reviewed_at": at("2026-10-12", 14, 20),
            "review_comment": "Approved. Scope, metrics, and mitigation actions align with release gate.",
            "review_history": [
                {"action": "PENDING_REVIEW", "reviewer_id": cp_member, "at": at("2026-10-12", 10, 30)},
                {"action": "APPROVED", "reviewer_id": cp_reviewer, "at": at("2026-10-12", 14, 20)},
            ],
            "knowledge_eligible": True,
            "synthetic": True,
        })

        # Add 1 DAILY Work Report per project (exercising DAILY cadence + APPROVED / PENDING_REVIEW / DRAFT / OVERDUE)
        daily_id = stable_id("report_daily", project_id)
        daily_scope = "LEADER" if p_idx in (3, 4) else "MEMBER"
        daily_member = squad_leader if daily_scope == "LEADER" else contributors[min(1, len(contributors) - 1)]
        is_daily_overdue = (project_id == "NSC-ORD")
        daily_status = (
            "PENDING_REVIEW" if project_id == "NSC-CHKO"
            else "DRAFT" if project_id in ("NSC-SRCH", "NSC-ORD")
            else "APPROVED"
        )
        daily_roster_state = "OVERDUE" if is_daily_overdue else daily_status
        daily_reviewer = (
            (org_manager if daily_scope == "LEADER" else squad_leader)
            if daily_status == "APPROVED" else None
        )
        daily_submitted = (
            at("2026-10-09", 16, 15) if daily_status in ("APPROVED", "PENDING_REVIEW") else None
        )
        daily_reviewed_at = at("2026-10-09", 16, 50) if daily_status == "APPROVED" else None
        daily_hist = []
        if daily_status in ("APPROVED", "PENDING_REVIEW"):
            daily_hist.append({"action": "PENDING_REVIEW", "reviewer_id": daily_member, "at": daily_submitted})
        if daily_status == "APPROVED":
            daily_hist.append({"action": "APPROVED", "reviewer_id": daily_reviewer, "at": daily_reviewed_at})

        reports.append({
            "report_id": daily_id,
            "project_id": project_id,
            "organization_id": "ORG-NSC",
            "member_id": daily_member,
            "report_scope": daily_scope,
            "report_type": "DAILY",
            "frequency": "DAILY",
            "period_key": "2026-10-08",
            "period_start": "2026-10-08",
            "period_end": "2026-10-08",
            "is_overdue": is_daily_overdue,
            "roster_submission_state": daily_roster_state,
            "due_at": at("2026-10-08", 20, 0) if is_daily_overdue else at("2026-10-09", 17, 0),
            "status": daily_status,
            "accomplishments": f"Báo cáo ngày 08/10/2026 cho {project_id}: rà soát tiến độ task {p_code}-1 và subtask {sub_key}.",
            "approach": "Cập nhật kết quả chạy regression suite cuối ngày và ghi chú phụ thuộc liên dự án.",
            "reason": "Theo dõi nhịp độ vận hành hằng ngày trong giai đoạn nước rút Sprint 13.",
            "blockers": "Đang chờ xác nhận lịch bảo trì sandbox đối tác." if project_id == "NSC-PAY" else None,
            "next_steps": "Tiếp tục xử lý các mục checklist còn mở trong ca sáng ngày kế tiếp.",
            "document_ids": [docs[0]["document_id"]],
            "source_task_ids": [sub_id],
            "created_at": at("2026-10-09", 8, 30),
            "submitted_at": daily_submitted,
            "reviewed_by": daily_reviewer,
            "reviewed_at": daily_reviewed_at,
            "review_comment": "Daily checkpoint verified." if daily_status == "APPROVED" else None,
            "review_history": daily_hist,
            "knowledge_eligible": daily_status == "APPROVED",
            "synthetic": True,
        })

        project_anchors[project_id] = {
            "anchor_key": anchor_key,
            "anchor_task": anchor_task,
            "sub_id": sub_id,
            "task8_id": t8_id,
            "docs": docs,
            "orig_report_id": report_id,
            "orig_report_status": orig_status,
            "orig_member": orig_member,
            "counterpart_report_id": counterpart_id,
            "daily_report_id": daily_id,
            "daily_status": daily_status,
            "squad_leader": squad_leader,
            "org_manager": org_manager,
            "contributors": contributors,
        }

        # Preserve original WF-001 .. WF-016 IDs and core fields
        c_idx1 = len(cases) + 1
        cases.append({
            "case_id": f"WF-{c_idx1:03d}",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": f"For {anchor_key}, which task note and approved document explain the work?",
            "expected": f"Task {anchor_task} has note {stable_id('note', anchor_key)} and approved document {docs[0]['document_id']}.",
            "target_resource_ids": [anchor_task],
            "source_ids": [anchor_task, stable_id("note", anchor_key), docs[0]["document_id"]] + ([report_id] if orig_status == "APPROVED" else []),
            "must_not_cite": [f"{docs[0]['document_id']}@{int(float(docs[0]['version'])) + 1}.0-draft"] + ([report_id] if orig_status != "APPROVED" else []),
            "principal_id": orig_member,
            "tags": ["task_note_link", "approved_source", "project_scope"],
            **_dual_review_meta(
                c_idx1,
                project_id=project_id,
                as_of=as_of,
                category="normal",
                mandatory=[anchor_task, stable_id("note", anchor_key), docs[0]["document_id"]],
                forbidden=["Cite unapproved draft v2", "Treat Task Note as official approved knowledge"],
            ),
        })
        outsider = next(
            member["member_id"] for member in members
            if member["org_id"] != "ORG-NSC"
            and member["account_status"] == "active"
            and (project_id, member["member_id"]) not in active_project_members
        )
        c_idx2 = len(cases) + 1
        cases.append({
            "case_id": f"WF-{c_idx2:03d}",
            "suite": "WORKFLOW_ACL",
            "answer_channel": "access",
            "query": f"Can {outsider} read the task note for {anchor_key}?",
            "expected": "DENY; do not reveal the note title, excerpt or existence.",
            "target_resource_ids": [stable_id("note", anchor_key)],
            "source_ids": [],
            "must_not_cite": [stable_id("note", anchor_key)],
            "principal_id": outsider,
            "tags": ["cross_tenant", "project_membership", "pre_filter"],
            **_dual_review_meta(
                c_idx2,
                project_id=project_id,
                as_of=as_of,
                category="access_denied",
                mandatory=["Deny cross-tenant access before retrieval"],
                forbidden=["Leak Task Note title or existence"],
            ),
        })

    # Add a REJECTED proposal review sequence on DOC-SRCH-STRATEGY-003 (which is In Review in canonical docs)
    srch_in_review_doc = next(doc for doc in documents if doc["document_id"] == "DOC-SRCH-STRATEGY-003")
    srch_rej_day = next_workday(srch_in_review_doc["recorded_at"][:10], holidays)
    for r_i, (r_act, r_hr, r_actor) in enumerate((
        ("SUBMITTED", 10, srch_in_review_doc["owner_id"]),
        ("REJECTED", 15, "M-002"),
    )):
        reviews.append({
            "event_id": stable_id("review", f"{srch_in_review_doc['document_id']}:rejected-proposal:{r_i}"),
            "document_id": srch_in_review_doc["document_id"],
            "version": "3.0-experimental",
            "project_id": "NSC-SRCH",
            "organization_id": "ORG-NSC",
            "action": r_act,
            "actor_id": r_actor,
            "at": at(srch_rej_day, r_hr),
            "reason": "Cross-session behavioral profiling violates pilot privacy boundary." if r_act == "REJECTED" else None,
            "knowledge_eligible": False,
            "synthetic": True,
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

    # Preserve original WF-017 .. WF-021
    first_doc = next(row for row in documents if row["document_id"] == reviews[0]["document_id"])
    cases.append({
        "case_id": "WF-017",
        "suite": "WORKFLOW_KNOWLEDGE",
        "answer_channel": "knowledge",
        "query": f"Is the unapproved follow-up to {first_doc['title']} an authoritative source?",
        "expected": "No. The latest approved version remains authoritative until a new version is approved.",
        "target_resource_ids": [f"{first_doc['document_id']}@{int(float(first_doc['version'])) + 1}.0-draft"],
        "source_ids": [first_doc["document_id"]],
        "must_not_cite": [f"{first_doc['document_id']}@{int(float(first_doc['version'])) + 1}.0-draft"],
        "principal_id": reports[0]["member_id"],
        "tags": ["draft_exclusion", "versioning"],
        **_dual_review_meta(17, project_id=first_doc["project_id"], as_of=as_of, category="draft_vs_approved"),
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
        "case_id": "WF-018",
        "suite": "WORKFLOW_ACL",
        "answer_channel": "access",
        "query": f"Can offboarded member {former['member_id']} read {former_doc['document_id']} now?",
        "expected": "DENY; historical authorship does not restore current access.",
        "target_resource_ids": [former_doc["document_id"]],
        "source_ids": [],
        "must_not_cite": [former_doc["document_id"]],
        "principal_id": former["member_id"],
        "tags": ["offboarding", "revoked_access"],
        **_dual_review_meta(18, project_id=former_project, as_of=as_of, category="access_denied"),
    })
    cases.append({
        "case_id": "WF-019",
        "suite": "WORKFLOW_KNOWLEDGE",
        "answer_channel": "knowledge",
        "query": "Which payment ADR remains authoritative after the older ADR is superseded?",
        "expected": f"{replacement['document_id']} is current; {superseded['document_id']} is superseded and excluded from active citations.",
        "target_resource_ids": [superseded["document_id"]],
        "source_ids": [replacement["document_id"]],
        "must_not_cite": [superseded["document_id"]],
        "principal_id": pay_owner,
        "tags": ["supersession", "approved_version"],
        **_dual_review_meta(19, project_id="NSC-PAY", as_of=as_of, category="superseded_decision"),
    })
    cases.append({
        "case_id": "WF-020",
        "suite": "WORKFLOW_KNOWLEDGE",
        "answer_channel": "knowledge",
        "query": "May the archived conflicting policy fixture be cited as current policy?",
        "expected": "No. The test-only fixture is archived and excluded from official knowledge.",
        "target_resource_ids": [archived_fixture["document_id"]],
        "source_ids": [],
        "must_not_cite": [archived_fixture["document_id"]],
        "principal_id": archived_fixture["owner_id"],
        "tags": ["archive", "test_fixture", "source_exclusion"],
        **_dual_review_meta(20, project_id=archived_fixture["project_id"], as_of=as_of, category="conflict"),
    })
    rejected_report = next(report for report in reports if report["status"] == "REJECTED")
    cases.append({
        "case_id": "WF-021",
        "suite": "WORKFLOW_KNOWLEDGE",
        "answer_channel": "knowledge",
        "query": "Can the rejected payment work report be cited as approved knowledge?",
        "expected": "No. Rejected Work Reports are not knowledge eligible.",
        "target_resource_ids": [rejected_report["report_id"]],
        "source_ids": [],
        "must_not_cite": [rejected_report["report_id"]],
        "principal_id": pay_owner,
        "tags": ["rejected_report", "source_exclusion"],
        **_dual_review_meta(21, project_id="NSC-PAY", as_of=as_of, category="draft_vs_approved"),
    })

    # New enriched evaluation cases WF-022 .. WF-032 covering v1.4 gaps
    chko_info = project_anchors["NSC-CHKO"]
    cat_info = project_anchors["NSC-CAT"]
    pay_info = project_anchors["NSC-PAY"]
    inv_info = project_anchors["NSC-INV"]
    srch_info = project_anchors["NSC-SRCH"]
    ord_info = project_anchors["NSC-ORD"]
    cart_info = project_anchors["NSC-CART"]

    extra_cases = [
        {
            "case_id": "WF-022",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": "Ai là người lập và ai phê duyệt báo cáo tuần cấp Leader (LEADER report) của dự án NSC-CHKO tuần 05/10–11/10/2026?",
            "expected": f"Leader Sofia Nguyen (M-005) lập báo cáo {chko_info['counterpart_report_id']} và Organization Manager Jordan Lee (M-002, role ADMIN) phê duyệt.",
            "target_resource_ids": [chko_info["counterpart_report_id"]],
            "source_ids": [chko_info["counterpart_report_id"], chko_info["docs"][1]["document_id"]],
            "must_not_cite": [chko_info["orig_report_id"]],
            "principal_id": "M-002",
            "tags": ["leader_report", "manager_review", "bilingual_vi"],
            **_dual_review_meta(22, project_id="NSC-CHKO", as_of=as_of, category="normal", mandatory=["M-005", "M-002", chko_info["counterpart_report_id"]]),
        },
        {
            "case_id": "WF-023",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": "Khi Liam Vance (M-019) nghỉ ốm ngày 19–20/08/2026 tại NSC-CAT, subtask nào được bàn giao và ai tiếp nhận?",
            "expected": f"Subtask {cat_info['sub_id']} (NSCCAT-7) được bàn giao sang Emma Watson (M-020), kèm Task Note {stable_id('note', 'NSC-CAT:sub-07')} và báo cáo tuần {cat_info['counterpart_report_id']}.",
            "target_resource_ids": [cat_info["sub_id"]],
            "source_ids": [cat_info["sub_id"], stable_id("note", "NSC-CAT:sub-07"), cat_info["counterpart_report_id"]],
            "must_not_cite": [],
            "principal_id": "M-003",
            "tags": ["sick_leave", "handover", "subtask_traceability"],
            **_dual_review_meta(23, project_id="NSC-CAT", as_of=as_of, category="normal", mandatory=["M-019", "M-020", cat_info["sub_id"]]),
        },
        {
            "case_id": "WF-024",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": "Sự cố mưa bão đứt cáp quang ngày 14–15/09/2026 ảnh hưởng nhân sự nào trong NSC-PAY và được xử lý bàn giao ra sao?",
            "expected": f"Benjamin Anderson (M-027) bị mất kết nối mạng do mưa bão; Mia Thomas (M-028) tiếp nhận và hoàn thành subtask {pay_info['sub_id']} (NSCPAY-7) ngày 16/09/2026.",
            "target_resource_ids": [pay_info["sub_id"]],
            "source_ids": [pay_info["sub_id"], stable_id("note", "NSC-PAY:sub-07"), pay_info["counterpart_report_id"]],
            "must_not_cite": [pay_info["orig_report_id"]],
            "principal_id": "M-006",
            "tags": ["storm_outage", "handover", "resilience"],
            **_dual_review_meta(24, project_id="NSC-PAY", as_of=as_of, category="normal", mandatory=["M-027", "M-028", pay_info["sub_id"]]),
        },
        {
            "case_id": "WF-025",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": "Trong thời gian Lucas Jackson (M-029) nghỉ phép năm 26–27/08/2026 ở NSC-INV, ai đảm nhận kiểm thử khóa Redis TTL?",
            "expected": f"Charlotte White (M-030) nhận bàn giao và hoàn thành subtask {inv_info['sub_id']} (NSCINV-7) có ghi nhận trong Task Note {stable_id('note', 'NSC-INV:sub-07')}.",
            "target_resource_ids": [inv_info["sub_id"]],
            "source_ids": [inv_info["sub_id"], stable_id("note", "NSC-INV:sub-07")],
            "must_not_cite": [],
            "principal_id": "M-007",
            "tags": ["pto_handover", "subtask"],
            **_dual_review_meta(25, project_id="NSC-INV", as_of=as_of, category="normal", mandatory=["M-029", "M-030"]),
        },
        {
            "case_id": "WF-026",
            "suite": "WORKFLOW_KNOWLEDGE",
            "answer_channel": "knowledge",
            "query": "Báo cáo ngày (DAILY report) đang ở trạng thái DRAFT của NSC-SRCH hoặc OVERDUE của NSC-ORD có được nạp làm tri thức AI chính thức không?",
            "expected": "Không. Chỉ Work Report ở trạng thái APPROVED mới có knowledge_eligible=true; các bản DRAFT và OVERDUE bị loại khỏi nguồn tri thức chính thức.",
            "target_resource_ids": [srch_info["daily_report_id"], ord_info["daily_report_id"]],
            "source_ids": [],
            "must_not_cite": [srch_info["daily_report_id"], ord_info["daily_report_id"]],
            "principal_id": "M-002",
            "tags": ["daily_report", "draft_exclusion", "overdue_exclusion"],
            **_dual_review_meta(26, project_id="NSC-SRCH", as_of=as_of, category="draft_vs_approved"),
        },
        {
            "case_id": "WF-027",
            "suite": "WORKFLOW_KNOWLEDGE",
            "answer_channel": "knowledge",
            "query": "Báo cáo ngày (DAILY report) đã APPROVED của NSC-CAT ngày 08/10/2026 do ai duyệt và liên kết tới tài liệu nào?",
            "expected": f"Báo cáo ngày {cat_info['daily_report_id']} của NSC-CAT đã được Leader Maya Patel (M-003) duyệt (APPROVED) và tham chiếu {cat_info['docs'][0]['document_id']}.",
            "target_resource_ids": [cat_info["daily_report_id"]],
            "source_ids": [cat_info["daily_report_id"], cat_info["docs"][0]["document_id"]],
            "must_not_cite": [],
            "principal_id": "M-003",
            "tags": ["daily_report", "approved_source"],
            **_dual_review_meta(27, project_id="NSC-CAT", as_of=as_of, category="normal"),
        },
        {
            "case_id": "WF-028",
            "suite": "WORKFLOW_KNOWLEDGE",
            "answer_channel": "knowledge",
            "query": "Phiên bản đề xuất thử nghiệm 3.0-experimental của DOC-SRCH-STRATEGY-003 có được phê duyệt áp dụng cho pilot không?",
            "expected": "Không. Bản 3.0-experimental đã bị từ chối (REJECTED) do vi phạm ranh giới quyền riêng tư (cross-session profiling).",
            "target_resource_ids": ["DOC-SRCH-STRATEGY-003@3.0-experimental"],
            "source_ids": [],
            "must_not_cite": ["DOC-SRCH-STRATEGY-003@3.0-experimental"],
            "principal_id": "M-004",
            "tags": ["rejected_document", "privacy_boundary"],
            **_dual_review_meta(28, project_id="NSC-SRCH", as_of=as_of, category="draft_vs_approved"),
        },
        {
            "case_id": "WF-029",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": "Vì sao task NSCCART-8 trong dự án NSC-CART chuyển sang trạng thái CANCELLED?",
            "expected": f"Task {cart_info['task8_id']} (NSCCART-8) bị hủy (CANCELLED) vì phạm vi kiểm tra schema đã được hợp nhất vào endpoint chuẩn sau buổi đồng bộ với Meridian.",
            "target_resource_ids": [cart_info["task8_id"]],
            "source_ids": [cart_info["task8_id"], stable_id("note", "NSC-CART:task-08")],
            "must_not_cite": [],
            "principal_id": "M-005",
            "tags": ["cancelled_task", "scope_consolidation"],
            **_dual_review_meta(29, project_id="NSC-CART", as_of=as_of, category="normal"),
        },
        {
            "case_id": "WF-030",
            "suite": "WORKFLOW_ACL",
            "answer_channel": "access",
            "query": "Nhân sự nội bộ M-021 (chỉ thuộc NSC-SRCH, không thuộc NSC-PAY) có được đọc Task Note nội bộ của NSCPAY-7 không?",
            "expected": "DENY; nhân sự nội bộ nhưng không có Project Membership active tại NSC-PAY và không phải Organization ADMIN nên không được truy cập Task Note dự án khác.",
            "target_resource_ids": [stable_id("note", "NSC-PAY:sub-07")],
            "source_ids": [],
            "must_not_cite": [stable_id("note", "NSC-PAY:sub-07")],
            "principal_id": "M-021",
            "tags": ["internal_cross_project_deny", "project_membership"],
            **_dual_review_meta(30, project_id="NSC-PAY", as_of=as_of, category="access_denied"),
        },
        {
            "case_id": "WF-031",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": "Báo cáo ngày của NSC-CHKO ngày 08/10/2026 hiện ở trạng thái nào và đã đủ điều kiện làm nguồn tri thức chưa?",
            "expected": f"Báo cáo ngày {chko_info['daily_report_id']} đang ở trạng thái PENDING_REVIEW nên chưa đủ điều kiện làm nguồn tri thức chính thức (knowledge_eligible=false).",
            "target_resource_ids": [chko_info["daily_report_id"]],
            "source_ids": [],
            "must_not_cite": [chko_info["daily_report_id"]],
            "principal_id": "M-005",
            "tags": ["pending_review_report", "source_exclusion"],
            **_dual_review_meta(31, project_id="NSC-CHKO", as_of=as_of, category="draft_vs_approved"),
        },
        {
            "case_id": "WF-032",
            "suite": "WORKFLOW",
            "answer_channel": "workspace",
            "query": "Northstar có lưu bảng lương cá nhân hoặc lịch sử hội thoại AI Chat của nhân sự trong bộ dữ liệu không?",
            "expected": "Không có bằng chứng trong dataset: bảng lương cá nhân ngoài phạm vi mô phỏng và lịch sử AI Chat không được tạo sẵn trong dataset.",
            "target_resource_ids": ["DOC-ORG-CHARTER-001"],
            "source_ids": ["DOC-ORG-CHARTER-001"],
            "must_not_cite": [],
            "principal_id": "M-001",
            "tags": ["calibrated_abstention", "missing_evidence"],
            **_dual_review_meta(32, project_id=None, as_of=as_of, category="missing_evidence"),
        },
    ]
    cases.extend(extra_cases)
    subtask_counts = {}
    for _t in tasks:
        if _t.get("parent_id"):
            subtask_counts[_t["parent_id"]] = subtask_counts.get(_t["parent_id"], 0) + 1
    for _t in tasks:
        _t["parent_task_id"] = _t["parent_id"]
        _t["subtask_count"] = subtask_counts.get(_t["task_id"], 0)
        _t["worklog_minutes_total"] = sum(w["minutes"] for w in _t.get("worklogs", []))
        _t["comment_count"] = len(_t.get("comments", []))
    return tasks, notes, reviews, reports, cases


def reconcile_document_snapshots(documents, reviews):
    """Apply synthetic review history and Continuum Capture mapping fields to as-of document metadata."""
    events_by_document = {}
    for event in reviews:
        events_by_document.setdefault(event["document_id"], []).append(event)

    def infer_continuum_doc_type(doc):
        title_u = doc["title"].upper()
        if "API" in title_u or "WEBHOOK" in title_u:
            return "API_SPECIFICATION"
        if "DATABASE" in title_u or "DATA DICTIONARY" in title_u or "MIGRATION" in title_u:
            return "DATABASE_DESIGN"
        if "ARCHITECTURE" in title_u or "ADR" in title_u or "SDS" in title_u:
            return "ARCHITECTURE"
        if "PRD" in title_u or "SRS" in title_u or "REQUIREMENT" in title_u or "ANNEX" in title_u:
            return "REQUIREMENT"
        if "TEST" in title_u or "RUNBOOK" in title_u or "RCA" in title_u or "SOP" in title_u:
            return "TECHNICAL_SPECIFICATION"
        if "DESIGN" in title_u:
            return "DESIGN"
        return "OTHER"

    status_to_continuum = {
        "Approved": "APPROVED",
        "In Review": "PENDING_REVIEW",
        "Draft": "DRAFT",
        "Archived": "ARCHIVED",
        "Superseded": "ARCHIVED",
    }

    reconciled = []
    for document in documents:
        current = dict(document)
        events = sorted(events_by_document.get(document["document_id"], []), key=lambda row: row["at"])
        if events:
            current["updated_at"] = max(current["updated_at"], events[-1]["at"][:10])
            terminal = next((event for event in reversed(events) if event["action"] in ("APPROVED", "ARCHIVED")), None)
            if terminal:
                current["status"] = "Approved" if terminal["action"] == "APPROVED" else "Archived"
                if terminal["action"] == "ARCHIVED":
                    current["is_current"] = False
        current["continuum_document_id"] = stable_id("document", current["document_id"])
        current["continuum_document_type"] = infer_continuum_doc_type(current)
        current["continuum_status"] = status_to_continuum.get(current["status"], "OTHER")
        current["knowledge_eligible"] = bool(
            current["status"] == "Approved" and not current.get("test_only") and current.get("project_id") is not None
        )
        reconciled.append(current)
    return reconciled


def validate_workflows(tasks, notes, reviews, reports, cases, issues, documents, members, memberships, as_of):
    """Raise on orphaned references, Continuum contract mismatch, ACL leak, or unsafe knowledge status."""
    task_by_id = {row["task_id"]: row for row in tasks}
    issue_by_key = {row["issue_key"]: row for row in issues}
    document_by_id = {row["document_id"]: row for row in documents}
    member_by_id = {row["member_id"]: row for row in members}
    project_member = {(row["project_id"], row["member_id"]) for row in memberships if row["status"] == "active"}
    historical_project_member = {(row["project_id"], row["member_id"]) for row in memberships}
    membership_roles = {(row["project_id"], row["member_id"]): row["role"] for row in memberships if row["status"] == "active"}

    if len(tasks) != 64 or len(task_by_id) != len(tasks):
        raise ValueError(f"Expected 64 unique Work Tasks, got {len(tasks)}")
    if len({row["note_id"] for row in notes}) != len(notes):
        raise ValueError("Duplicate Task Note ID")
    if len({row["event_id"] for row in reviews}) != len(reviews):
        raise ValueError("Duplicate document review event ID")
    if len({row["report_id"] for row in reports}) != len(reports):
        raise ValueError("Duplicate Work Report ID")

    seen_keys = set()
    for task in tasks:
        if not TASK_KEY_RE.match(task["key"]) or task["key"] in seen_keys:
            raise ValueError(f"Invalid or duplicate Continuum task key: {task['key']}")
        seen_keys.add(task["key"])
        issue = issue_by_key.get(task["source_issue_key"])
        if not issue or task["project_id"] != issue["project_id"]:
            raise ValueError(f"Invalid issue mapping: {task['key']}")
        if task.get("legacy_key") and task["status"] != STATUS_MAP[issue["status"]]:
            raise ValueError(f"Invalid legacy issue status mapping: {task['key']}")
        if task["assignee_id"] is not None and (task["project_id"], task["assignee_id"]) not in project_member:
            raise ValueError(f"Assignee outside project: {task['key']}")
        if task["status"] in ("IN_PROGRESS", "IN_REVIEW") and task["assignee_id"] is None:
            raise ValueError(f"Active task missing assignee: {task['key']}")
        eff_parent_id = task.get("parent_task_id") if task.get("parent_task_id") is not None else task.get("parent_id")
        if eff_parent_id is not None:
            parent = task_by_id.get(eff_parent_id)
            if not parent or parent["project_id"] != task["project_id"]:
                raise ValueError(f"Invalid 1-level subtask parent on {task['key']}")
            if (parent.get("parent_task_id") or parent.get("parent_id")) is not None:
                raise ValueError(f"Nested subtask depth > 1 on {task['key']}")
        for ev in task.get("task_events", []):
            if ev["type"] == "TASK_STATUS_TRANSITIONED":
                f_st, t_st = ev["from_status"], ev["to_status"]
                if t_st not in ALLOWED_TRANSITIONS.get(f_st, set()):
                    raise ValueError(f"Invalid task transition {f_st}->{t_st} on {task['key']}")
                if (f_st == "BLOCKED" or t_st in ("BLOCKED", "CANCELLED") or f_st in ("DONE", "CANCELLED")) and len(str(ev.get("reason") or "").strip()) < 5:
                    raise ValueError(f"Missing transition reason on {task['key']}")
        for wl in task.get("worklogs", []):
            if not (1 <= wl["minutes"] <= 1440):
                raise ValueError(f"Invalid worklog minutes on {task['key']}")

    # Verify sick leave / storm / PTO windows have zero actions by affected member
    for proj_id, dis in NORTHSTAR_DISRUPTION_WINDOWS.items():
        u_id = dis["affected_member_id"]
        u_from, u_to = dis["unavailable_from"], dis["unavailable_to"]
        for note in notes:
            if note["author_id"] == u_id and u_from <= note["created_at"] <= u_to:
                raise ValueError(f"Member {u_id} wrote note during unavailable window {dis['disruption_id']}")
        for task in tasks:
            for wl in task.get("worklogs", []):
                wl_actor = wl.get("user_id") or wl.get("author_id")
                if wl_actor == u_id and u_from <= wl["logged_at"] <= u_to:
                    raise ValueError(f"Member {u_id} logged work during disruption unavailability {dis['disruption_id']}")

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
        if (event["project_id"], event["actor_id"]) not in permitted_members and event["actor_id"] not in ORG_NSC_MANAGERS:
            raise ValueError(f"Reviewer outside project: {event['event_id']}")
        member = member_by_id[event["actor_id"]]
        if member["left_at"] and event["at"][:10] > member["left_at"]:
            raise ValueError(f"Review after offboarding: {event['event_id']}")
        if event["action"] in ("APPROVED", "CHANGES_REQUESTED", "REJECTED") and event["actor_id"] == doc["owner_id"]:
            raise ValueError(f"Self-review: {event['event_id']}")
        if event["action"] in ("APPROVED", "CHANGES_REQUESTED", "REJECTED", "ARCHIVED"):
            has_perm = (
                membership_roles.get((event["project_id"], event["actor_id"])) in ("owner", "tech_lead")
                or event["actor_id"] in ORG_NSC_MANAGERS
            )
            if not has_perm:
                raise ValueError(f"Review permission missing: {event['event_id']}")
        if not (doc["recorded_at"] < event["at"] <= as_of + "T23:59:59+07:00"):
            raise ValueError(f"Review outside document timeline: {event['event_id']}")
        if event["action"] in ("DRAFT_SAVED", "REJECTED") and event.get("knowledge_eligible"):
            raise ValueError(f"Unapproved draft/rejected doc is knowledge eligible: {event['event_id']}")

    review_groups = {}
    review_events_by_document = {}
    for event in reviews:
        review_groups.setdefault((event["document_id"], event["version"]), []).append(event)
        review_events_by_document.setdefault(event["document_id"], []).append(event)
    for source, events in review_groups.items():
        actions = [row["action"] for row in sorted(events, key=lambda row: row["at"])]
        if actions not in (
            ["SUBMITTED", "APPROVED"],
            ["SUBMITTED", "CHANGES_REQUESTED", "RESUBMITTED", "APPROVED"],
            ["SUBMITTED", "REJECTED"],
            ["DRAFT_SAVED", "ARCHIVED"],
            ["DRAFT_SAVED"],
        ):
            raise ValueError(f"Invalid review lifecycle: {source}")
    for document_id, document_events in review_events_by_document.items():
        doc = document_by_id[document_id]
        events = sorted(document_events, key=lambda row: row["at"])
        terminal = next((event for event in reversed(events) if event["action"] in ("APPROVED", "ARCHIVED")), None)
        expected_status = "Approved" if terminal and terminal["action"] == "APPROVED" else "Archived" if terminal else doc["status"]
        if doc["updated_at"] < events[-1]["at"][:10] or doc["status"] != expected_status:
            raise ValueError(f"Document snapshot predates review or has wrong status: {document_id}")

    valid_report_statuses = ("DRAFT", "PENDING_REVIEW", "APPROVED", "CHANGES_REQUESTED", "REJECTED")
    project_scopes = {}
    for report in reports:
        pid = report["project_id"]
        st = report["status"]
        scope = report["report_scope"]
        author = report["member_id"]
        rev = report["reviewed_by"]
        if st not in valid_report_statuses or report["knowledge_eligible"] != (st == "APPROVED"):
            raise ValueError(f"Invalid Work Report knowledge status: {report['report_id']}")
        if report["period_end"] < report["period_start"] or not (report["period_end"] < report["created_at"][:10]):
            raise ValueError(f"Invalid Work Report period: {report['report_id']}")
        if (pid, author) not in project_member:
            raise ValueError(f"Report author outside project: {report['report_id']}")

        expected_leader = PROJECT_TEAM_LEADERS[pid]
        if scope == "LEADER":
            if author != expected_leader:
                raise ValueError(f"Leader report has non-leader author: {report['report_id']}")
        else:
            if author == expected_leader or author in ORG_NSC_MANAGERS:
                raise ValueError(f"Member report authored by leader/manager: {report['report_id']}")

        if st in ("APPROVED", "CHANGES_REQUESTED", "REJECTED"):
            if not rev or rev == author:
                raise ValueError(f"Invalid Work Report review: {report['report_id']}")
            if scope == "LEADER":
                if rev not in ORG_NSC_MANAGERS:
                    raise ValueError(f"LEADER report requires Org ADMIN Manager reviewer: {report['report_id']}")
            else:
                if membership_roles.get((pid, rev)) not in ("owner", "tech_lead") and rev not in ORG_NSC_MANAGERS:
                    raise ValueError(f"Report reviewer lacks permission: {report['report_id']}")
            if not (report["created_at"] <= report["submitted_at"] <= report["due_at"] and report["submitted_at"] <= report["reviewed_at"] <= as_of + "T23:59:59+07:00"):
                raise ValueError(f"Invalid Work Report chronology: {report['report_id']}")
            if report["review_history"][-1]["action"] != st:
                raise ValueError(f"Report review history mismatch: {report['report_id']}")
        elif st == "PENDING_REVIEW":
            if not report["submitted_at"] or rev is not None:
                raise ValueError(f"Invalid PENDING_REVIEW report state: {report['report_id']}")
        elif st == "DRAFT":
            if report["submitted_at"] is not None or rev is not None:
                raise ValueError(f"Invalid DRAFT report state: {report['report_id']}")

        if not all(doc_id in document_by_id and document_by_id[doc_id]["project_id"] == pid for doc_id in report["document_ids"]):
            raise ValueError(f"Report document outside project: {report['report_id']}")
        if not all(task_id in task_by_id and task_by_id[task_id]["project_id"] == pid for task_id in report["source_task_ids"]):
            raise ValueError(f"Report task outside project: {report['report_id']}")
        project_scopes.setdefault(pid, set()).add(scope)

    for pid in PROJECT_TEAM_LEADERS:
        if project_scopes.get(pid) != {"MEMBER", "LEADER"}:
            raise ValueError(f"Project {pid} missing MEMBER or LEADER report coverage: {project_scopes.get(pid)}")

    if len(cases) != 32 or len({row["case_id"] for row in cases}) != len(cases):
        raise ValueError(f"Expected 32 unique workflow evaluation cases, got {len(cases)}")
    all_sources = set(task_by_id) | {row["note_id"] for row in notes} | set(document_by_id) | {row["report_id"] for row in reports}
    all_targets = all_sources | {f"{row['document_id']}@{row['version']}" for row in reviews}
    if any(source_id not in all_sources for case in cases for source_id in case["source_ids"]):
        raise ValueError("Workflow evaluation references a missing source")
    if any(not case.get("target_resource_ids") or any(target not in all_targets for target in case["target_resource_ids"]) for case in cases):
        raise ValueError("Workflow evaluation references a missing target resource")
    if any(source_id not in all_targets for case in cases for source_id in case["must_not_cite"]):
        raise ValueError("Workflow evaluation forbids an unknown source")
    if any(set(case["source_ids"]) & set(case["must_not_cite"]) for case in cases):
        raise ValueError("Workflow evaluation marks a source both allowed and forbidden")
    if any(case["expected"].startswith("DENY") and case["source_ids"] for case in cases):
        raise ValueError("Denied workflow evaluation has citeable sources")
    if any(case.get("review_status") != "unreviewed" for case in cases):
        raise ValueError("Unreviewed workflow evaluation case missing review_status='unreviewed'")
