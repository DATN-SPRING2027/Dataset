"""Deterministic Continuum package materializer for synthetic organizations (Orgs 2, 3, and 4)."""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from continuum_synth import (  # noqa: E402
    VN_HOLIDAYS_2026,
    add_working_days,
    build_excel_catalog,
    build_file_inventory,
    build_working_days,
    list_package_files,
    make_ot_ts,
    make_regular_ts,
    make_vn_ts,
    render_formal_docx,
    sha256_file,
    sha256_text,
    snap_working_day,
    synth_oid,
    validate_continuum_organization_bundle,
    write_jsonl,
)


def make_eval_case(
    case_id: str,
    org_id: str,
    project_id: str | None,
    as_of: str,
    idx: int,
    suite: str,
    answer_channel: str,
    case_category: str,
    principal_id: str,
    question: str,
    expected_answer: str,
    target_resource_ids: list[str],
    source_ids: list[str],
    must_not_cite: list[str] | None = None,
    mandatory_points: list[str] | None = None,
    forbidden_claims: list[str] | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Create a Continuum benchmark case with mandatory dual-reviewer unreviewed governance metadata."""
    return {
        "case_id": case_id,
        "organization_id": org_id,
        "project_id": project_id,
        "as_of_date": as_of,
        "suite": suite,
        "answer_channel": answer_channel,
        "case_category": case_category,
        "principal_id": principal_id,
        "question": question,
        "expected_answer": expected_answer,
        "target_resource_ids": target_resource_ids,
        "source_ids": source_ids,
        "must_not_cite": must_not_cite or [],
        "mandatory_points": mandatory_points or [],
        "forbidden_claims": forbidden_claims or [],
        "tags": tags or [],
        "split": "test" if idx % 4 == 0 else "dev",
        "review_status": "unreviewed",
        "review_status_label_vi": "chưa duyệt",
        "reviewer_1": None,
        "reviewer_2": None,
        "adjudication_status": "pending_dual_review",
        "adjudication_notes": None,
        "synthetic": True,
    }


def expand_project_tasks(
    namespace: str,
    org_id: str,
    project: dict[str, Any],
    leader_id: str,
    member_ids: list[str],
    sim_start: date,
    as_of: date,
    task_blueprints: list[dict[str, Any]],
    unavailable_by_user: dict[str, list[tuple[str, str]]] | None = None,
    user_left_at: dict[str, str] | None = None,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """
    Deterministically materialize tasks, comments, worklogs, task_events, and Task Notes
    for a single project while strictly honoring VN working hours, OT, offboarding, and unavailability windows.
    """
    unavailable = unavailable_by_user or {}
    left_map = user_left_at or {}
    pid = project["project_id"]
    pcode = project["code"]

    tasks: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    worklogs: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []

    task_id_by_seq: dict[int, str] = {}
    for seq, _bp in enumerate(task_blueprints, start=1):
        tkey = f"{pcode}-{seq}"
        task_id_by_seq[seq] = synth_oid(namespace, "task", tkey)

    def is_user_available_on(uid: str, ts: str) -> bool:
        left_d = left_map.get(uid)
        if left_d and ts[:10] > left_d:
            return False
        for u_s, u_e in unavailable.get(uid, []):
            if u_s <= ts <= u_e:
                return False
        return True

    def safe_day_for_actor(uid: str, target_d: date, seed_num: int, is_ot: bool = False, slot: int = 0) -> tuple[date, str]:
        d_cur = snap_working_day(target_d, sim_start, as_of, prefer_forward=True)
        for attempt in range(25):
            ts_cand = (
                make_ot_ts(d_cur, seed_num + attempt, slot=slot)
                if is_ot
                else make_regular_ts(d_cur, seed_num + attempt, slot=slot)
            )
            if is_user_available_on(uid, ts_cand):
                return d_cur, ts_cand
            d_cur = add_working_days(d_cur, 1, sim_start, as_of, cap_at_end=False)
            if d_cur > as_of:
                d_cur = snap_working_day(target_d - timedelta(days=attempt + 1), sim_start, as_of, prefer_forward=False)
        raise RuntimeError(f"Could not find available working timestamp for {uid} near {target_d} in {pid}")

    for seq, bp in enumerate(task_blueprints, start=1):
        tkey = f"{pcode}-{seq}"
        tid = task_id_by_seq[seq]
        st = bp["status"]
        ttype = bp.get("type", "TASK")
        prio = bp.get("priority", "MEDIUM")
        creator = bp.get("created_by", leader_id)
        assignee = bp.get("assignee_id")
        if assignee is None and st != "CANCELLED" and not bp.get("allow_unassigned"):
            assignee = member_ids[(seq - 1) % len(member_ids)]

        parent_seq = bp.get("parent_seq")
        parent_id = task_id_by_seq[parent_seq] if parent_seq else None
        sprint_id = bp.get("sprint_id")
        is_ot = bool(bp.get("is_overtime", False))
        oncall_ts = bp.get("oncall_ts")  # Explicit timestamp when created/handled under scheduled on-call

        base_d = date.fromisoformat(bp["start_date"])
        if oncall_ts:
            created_at = oncall_ts["created_at"]
            created_mode = oncall_ts["work_mode"]
            created_ot = bool(oncall_ts.get("is_overtime", False))
            created_actor_type = oncall_ts.get("actor_type", "human")
            start_day_str = created_at[:10]
        else:
            c_day, created_at = safe_day_for_actor(creator, base_d, seed_num=seq * 13 + 7, is_ot=False, slot=0)
            created_mode = "regular_hours"
            created_ot = False
            created_actor_type = "human"
            start_day_str = c_day.isoformat()

        dur_days = int(bp.get("duration_days", 4))
        end_target = date.fromisoformat(bp["updated_date"]) if bp.get("updated_date") else add_working_days(
            date.fromisoformat(start_day_str), dur_days, sim_start, as_of
        )

        act_actor = assignee or creator
        if oncall_ts and oncall_ts.get("updated_at"):
            updated_at = oncall_ts["updated_at"]
            upd_mode = oncall_ts.get("updated_work_mode", created_mode)
            upd_ot = bool(oncall_ts.get("updated_is_overtime", False))
        else:
            _, updated_at = safe_day_for_actor(act_actor, end_target, seed_num=seq * 17 + 11, is_ot=is_ot, slot=2)
            if updated_at < created_at:
                _, updated_at = safe_day_for_actor(
                    act_actor, date.fromisoformat(created_at[:10]), seed_num=seq * 19 + 23, is_ot=True, slot=3
                )
                is_ot = True
            upd_mode = "evening_overtime" if is_ot else "regular_hours"
            upd_ot = is_ot

        due_date = bp.get("due_date") or add_working_days(
            date.fromisoformat(start_day_str), max(dur_days + 2, 5), sim_start, as_of + timedelta(days=30), cap_at_end=False
        ).isoformat()

        steps_raw = bp.get("steps") or [
            f"Phân tích yêu cầu & đối chiếu tài liệu thiết kế cho {tkey}",
            f"Thực thi logic nghiệp vụ & kiểm tra phân quyền tenant trên {pid}",
            f"Chạy bộ kiểm thử hồi quy và ghi nhận bằng chứng nghiệm thu",
        ]
        steps = []
        for s_i, s_txt in enumerate(steps_raw, start=1):
            done_flag = True if st == "DONE" else (s_i == 1 if st in ("IN_PROGRESS", "IN_REVIEW", "BLOCKED") else False)
            steps.append({
                "id": f"step-{tkey.lower()}-{s_i}",
                "text": s_txt[:200],
                "done": done_flag,
                "order": s_i,
            })

        task_row = {
            "task_id": tid,
            "continuum_task_id": tid,
            "key": tkey,
            "organization_id": org_id,
            "continuum_org_id": synth_oid(namespace, "org", org_id),
            "project_id": pid,
            "continuum_project_id": synth_oid(namespace, "project", pid),
            "title": bp["title"][:250],
            "description": bp["description"],
            "type": ttype,
            "status": st,
            "priority": prio,
            "assignee_id": assignee,
            "created_by": creator,
            "parent_id": parent_id,
            "sprint_id": sprint_id,
            "milestone_id": bp.get("milestone_id"),
            "waterfall_phase_id": bp.get("waterfall_phase_id"),
            "kanban_class_of_service": bp.get("kanban_class_of_service"),
            "incident_id": bp.get("incident_id"),
            "disruption_id": bp.get("disruption_id"),
            "spillover_count": int(bp.get("spillover_count", 0)),
            "labels": [lb[:40] for lb in bp.get("labels", [pid.lower(), ttype.lower()])[:10]],
            "steps": steps,
            "start_date": start_day_str,
            "due_date": due_date,
            "completed_at": updated_at if st == "DONE" else None,
            "version": 4 if bp.get("rework") else (3 if st == "DONE" else 2 if st != "TODO" else 1),
            "created_at": created_at,
            "created_work_mode": created_mode,
            "created_is_overtime": created_ot,
            "created_actor_type": created_actor_type,
            "updated_at": updated_at,
            "work_mode": upd_mode,
            "is_overtime": upd_ot,
            "synthetic": True,
        }
        tasks.append(task_row)

        # Build monotonic task_events + worklogs + comments
        ev_seq: list[dict[str, Any]] = [
            {
                "event_id": synth_oid(namespace, "task_event", f"{tkey}:created"),
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "type": "TASK_CREATED",
                "actor_id": None if created_actor_type == "system_bot" else creator,
                "actor_type": created_actor_type,
                "occurred_at": created_at,
                "from_status": None,
                "to_status": "TODO",
                "reason": None,
                "work_mode": created_mode,
                "is_overtime": created_ot,
            }
        ]

        # Optional handover reassignment event before final work
        if bp.get("handover_from_user_id") and bp.get("handover_date"):
            ho_day, ho_ts = safe_day_for_actor(
                leader_id, date.fromisoformat(bp["handover_date"]), seed_num=seq * 29 + 3, is_ot=False, slot=1
            )
            if ho_ts < created_at:
                ho_ts = created_at
            if ho_ts > updated_at:
                ho_ts = updated_at
            ev_seq.append({
                "event_id": synth_oid(namespace, "task_event", f"{tkey}:handover"),
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "type": "TASK_UPDATED",
                "actor_id": leader_id,
                "actor_type": "human",
                "occurred_at": ho_ts,
                "from_status": None,
                "to_status": None,
                "reason": bp.get(
                    "handover_reason",
                    f"Bàn giao công việc từ {bp['handover_from_user_id']} sang {act_actor} để bảo đảm SLA tiến độ.",
                ),
                "work_mode": "regular_hours",
                "is_overtime": False,
            })

        # Optional sprint rollover event for Hybrid spillover tasks
        if bp.get("spillover_from_sprint_id") and bp.get("spillover_date"):
            _, sp_ts = safe_day_for_actor(
                leader_id, date.fromisoformat(bp["spillover_date"]), seed_num=seq * 31 + 5, is_ot=False, slot=1
            )
            if sp_ts < created_at:
                sp_ts = created_at
            if sp_ts > updated_at:
                sp_ts = updated_at
            ev_seq.append({
                "event_id": synth_oid(namespace, "task_event", f"{tkey}:spillover"),
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "type": "TASK_UPDATED",
                "actor_id": leader_id,
                "actor_type": "human",
                "occurred_at": sp_ts,
                "from_status": None,
                "to_status": None,
                "reason": f"Chuyển tiếp (spillover) từ {bp['spillover_from_sprint_id']} sang {sprint_id} trước khi đóng sprint.",
                "work_mode": "regular_hours",
                "is_overtime": False,
            })

        if st == "CANCELLED":
            cancel_reason = bp.get(
                "transition_reason",
                "Hủy phạm vi trùng lặp hoặc hoãn sang giai đoạn tiếp theo theo quyết định quản trị thay đổi.",
            )
            ev_seq.append({
                "event_id": synth_oid(namespace, "task_event", f"{tkey}:cancelled"),
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "type": "TASK_STATUS_TRANSITIONED",
                "actor_id": leader_id,
                "actor_type": "human",
                "occurred_at": updated_at,
                "from_status": "TODO",
                "to_status": "CANCELLED",
                "reason": cancel_reason,
                "work_mode": upd_mode,
                "is_overtime": upd_ot,
            })
            comments.append({
                "comment_id": synth_oid(namespace, "comment", f"{tkey}:c1"),
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "author_id": leader_id,
                "actor_type": "human",
                "body": f"[{tkey}] Xác nhận chuyển trạng thái CANCELLED: {cancel_reason}",
                "created_at": updated_at,
                "work_mode": upd_mode,
                "is_overtime": upd_ot,
            })
        elif st != "TODO":
            # Midpoint timestamp between created_at and updated_at
            mid_target = date.fromisoformat(created_at[:10]) + timedelta(
                days=max(0, (date.fromisoformat(updated_at[:10]) - date.fromisoformat(created_at[:10])).days // 2)
            )
            if oncall_ts and oncall_ts.get("in_progress_at"):
                ip_ts = oncall_ts["in_progress_at"]
                ip_mode = oncall_ts.get("updated_work_mode", upd_mode)
                ip_ot = bool(oncall_ts.get("updated_is_overtime", False))
            else:
                _, ip_ts = safe_day_for_actor(act_actor, mid_target, seed_num=seq * 23 + 3, is_ot=False, slot=1)
                if ip_ts < created_at:
                    ip_ts = created_at if created_actor_type == "human" else updated_at
                if ip_ts > updated_at:
                    ip_ts = updated_at
                ip_mode = upd_mode if ip_ts == updated_at else "regular_hours"
                ip_ot = upd_ot if ip_ts == updated_at else False

            ev_seq.append({
                "event_id": synth_oid(namespace, "task_event", f"{tkey}:in_progress"),
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "type": "TASK_STATUS_TRANSITIONED",
                "actor_id": act_actor,
                "actor_type": "human",
                "occurred_at": ip_ts,
                "from_status": "TODO",
                "to_status": "IN_PROGRESS",
                "reason": None,
                "work_mode": ip_mode,
                "is_overtime": ip_ot,
            })

            # Optional rework cycle (IN_PROGRESS -> IN_REVIEW -> IN_PROGRESS -> final)
            if bp.get("rework") and ip_ts < updated_at:
                ev_seq.append({
                    "event_id": synth_oid(namespace, "task_event", f"{tkey}:rework_review"),
                    "task_id": tid,
                    "project_id": pid,
                    "organization_id": org_id,
                    "type": "TASK_STATUS_TRANSITIONED",
                    "actor_id": act_actor,
                    "actor_type": "human",
                    "occurred_at": ip_ts,
                    "from_status": "IN_PROGRESS",
                    "to_status": "IN_REVIEW",
                    "reason": None,
                    "work_mode": ip_mode,
                    "is_overtime": ip_ot,
                })
                ev_seq.append({
                    "event_id": synth_oid(namespace, "task_event", f"{tkey}:rework_back"),
                    "task_id": tid,
                    "project_id": pid,
                    "organization_id": org_id,
                    "type": "TASK_STATUS_TRANSITIONED",
                    "actor_id": leader_id if is_user_available_on(leader_id, ip_ts) else act_actor,
                    "actor_type": "human",
                    "occurred_at": ip_ts,
                    "from_status": "IN_REVIEW",
                    "to_status": "IN_PROGRESS",
                    "reason": bp.get("rework_reason", "Yêu cầu bổ sung kiểm thử biên sau khi phát hiện sai lệch nghiệp vụ."),
                    "work_mode": ip_mode,
                    "is_overtime": ip_ot,
                })

            wl_minutes = int(bp.get("worklog_minutes", 240 if upd_ot else 180))
            wl_id = synth_oid(namespace, "worklog", f"{tkey}:wl1")
            worklogs.append({
                "worklog_id": wl_id,
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "author_id": act_actor,
                "minutes": wl_minutes,
                "note": bp.get(
                    "worklog_note",
                    f"Thực hiện và kiểm chứng các hạng mục kỹ thuật cho {tkey}: {bp['title'][:120]}",
                ),
                "logged_at": updated_at,
                "created_at": updated_at,
                "work_mode": upd_mode,
                "is_overtime": upd_ot,
            })
            ev_seq.append({
                "event_id": synth_oid(namespace, "task_event", f"{tkey}:wl1"),
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "type": "TASK_WORKLOG_ADDED",
                "actor_id": act_actor,
                "actor_type": "human",
                "occurred_at": updated_at,
                "from_status": None,
                "to_status": None,
                "reason": None,
                "work_mode": upd_mode,
                "is_overtime": upd_ot,
            })

            if st == "BLOCKED":
                blk_reason = bp.get(
                    "transition_reason",
                    "Đang bị chặn bởi phụ thuộc tích hợp hoặc chờ xác nhận chính sách nghiệm thu.",
                )
                ev_seq.append({
                    "event_id": synth_oid(namespace, "task_event", f"{tkey}:blocked"),
                    "task_id": tid,
                    "project_id": pid,
                    "organization_id": org_id,
                    "type": "TASK_STATUS_TRANSITIONED",
                    "actor_id": act_actor,
                    "actor_type": "human",
                    "occurred_at": updated_at,
                    "from_status": "IN_PROGRESS",
                    "to_status": "BLOCKED",
                    "reason": blk_reason,
                    "work_mode": upd_mode,
                    "is_overtime": upd_ot,
                })
            elif st == "IN_REVIEW":
                ev_seq.append({
                    "event_id": synth_oid(namespace, "task_event", f"{tkey}:in_review"),
                    "task_id": tid,
                    "project_id": pid,
                    "organization_id": org_id,
                    "type": "TASK_STATUS_TRANSITIONED",
                    "actor_id": act_actor,
                    "actor_type": "human",
                    "occurred_at": updated_at,
                    "from_status": "IN_PROGRESS",
                    "to_status": "IN_REVIEW",
                    "reason": None,
                    "work_mode": upd_mode,
                    "is_overtime": upd_ot,
                })
            elif st == "DONE":
                ev_seq.append({
                    "event_id": synth_oid(namespace, "task_event", f"{tkey}:in_review_done"),
                    "task_id": tid,
                    "project_id": pid,
                    "organization_id": org_id,
                    "type": "TASK_STATUS_TRANSITIONED",
                    "actor_id": act_actor,
                    "actor_type": "human",
                    "occurred_at": updated_at,
                    "from_status": "IN_PROGRESS",
                    "to_status": "IN_REVIEW",
                    "reason": None,
                    "work_mode": upd_mode,
                    "is_overtime": upd_ot,
                })
                ev_seq.append({
                    "event_id": synth_oid(namespace, "task_event", f"{tkey}:done"),
                    "task_id": tid,
                    "project_id": pid,
                    "organization_id": org_id,
                    "type": "TASK_STATUS_TRANSITIONED",
                    "actor_id": leader_id if is_user_available_on(leader_id, updated_at) and upd_mode == "regular_hours" else act_actor,
                    "actor_type": "human",
                    "occurred_at": updated_at,
                    "from_status": "IN_REVIEW",
                    "to_status": "DONE",
                    "reason": None,
                    "work_mode": upd_mode,
                    "is_overtime": upd_ot,
                })

            comments.append({
                "comment_id": synth_oid(namespace, "comment", f"{tkey}:c1"),
                "task_id": tid,
                "project_id": pid,
                "organization_id": org_id,
                "author_id": act_actor,
                "actor_type": "human",
                "body": bp.get(
                    "comment_body",
                    f"[{tkey}] Cập nhật kết quả thực thi ({st}): đã đối chiếu điều kiện biên và ghi nhận bằng chứng kiểm thử.",
                ),
                "created_at": updated_at,
                "work_mode": upd_mode,
                "is_overtime": upd_ot,
            })

            # Optional automated bot comment (e.g., CI/CD, heartbeat alert, SMS gateway probe)
            if bp.get("bot_comment"):
                bc = bp["bot_comment"]
                comments.append({
                    "comment_id": synth_oid(namespace, "comment", f"{tkey}:bot1"),
                    "task_id": tid,
                    "project_id": pid,
                    "organization_id": org_id,
                    "author_id": bc["bot_id"],
                    "actor_type": "system_bot",
                    "body": bc["body"],
                    "created_at": bc["created_at"],
                    "work_mode": "automated_bot",
                    "is_overtime": False,
                })

        # Ensure strict monotonic order while keeping TASK_CREATED first and terminal status transition last
        events.extend(sorted(ev_seq, key=lambda e: e["occurred_at"]))

        # Generate Task Note when requested or for the first 20 rich tasks per project
        if bp.get("task_note") or seq <= 20:
            tn_spec = bp.get("task_note") or {}
            note_author = tn_spec.get("author_id") or act_actor
            note_ts = tn_spec.get("created_at") or updated_at
            note_mode = tn_spec.get("work_mode") or upd_mode
            note_ot = bool(tn_spec.get("is_overtime", upd_ot))
            if not is_user_available_on(note_author, note_ts):
                _, note_ts = safe_day_for_actor(note_author, end_target, seed_num=seq * 37 + 9, is_ot=False, slot=2)
                note_mode = "regular_hours"
                note_ot = False
            if note_ts < created_at:
                note_ts = updated_at
                note_mode = upd_mode
                note_ot = upd_ot

            note_id = synth_oid(namespace, "task_note", tkey)
            notes.append({
                "note_id": note_id,
                "continuum_work_note_id": note_id,
                "task_id": tid,
                "task_key": tkey,
                "project_id": pid,
                "organization_id": org_id,
                "author_id": note_author,
                "type": "TASK_NOTE",
                "status": "CONFIRMED",
                "knowledge_eligible": False,
                "title": tn_spec.get("title", f"Task Note [{tkey}]: {bp['title']}")[:180],
                "accomplishments": tn_spec.get(
                    "accomplishments",
                    f"Ghi nhận tiến độ thực tế của {tkey} ({st}): {bp['description'][:220]}",
                ),
                "approach": tn_spec.get(
                    "approach",
                    f"Thực hiện theo checklist kỹ thuật của {pid}, kiểm tra ràng buộc dữ liệu và ghi log kiểm chứng.",
                ),
                "reason": tn_spec.get(
                    "reason",
                    "Lưu vết quyết định thực thi tại tab công việc để đồng đội tra cứu nhanh mà không trộn vào kho tri thức chính thức.",
                ),
                "is_temporary_workaround": bool(tn_spec.get("is_temporary_workaround", False)),
                "created_at": note_ts,
                "updated_at": note_ts,
                "work_mode": note_mode,
                "is_overtime": note_ot,
                "synthetic": True,
            })

    return tasks, comments, worklogs, events, notes


def render_project_documents_and_versions(
    pkg_root: Path,
    namespace: str,
    org_id: str,
    org_banner: str,
    doc_specs: list[dict[str, Any]],
    fixed_dt: tuple[int, int, int, int, int, int] = (2026, 10, 16, 0, 0, 0),
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Write canonical Markdown + DOCX renditions and produce project_documents + document_versions rows.
    """
    project_documents: list[dict[str, Any]] = []
    document_versions: list[dict[str, Any]] = []

    for d_spec in doc_specs:
        did = d_spec["document_id"]
        pid = d_spec["project_id"]
        dtype = d_spec["document_type"]
        owner_id = d_spec["created_by"]
        versions_spec = d_spec["versions"]

        rel_md = f"documents/markdown/{did}.md"
        md_path = pkg_root / rel_md
        md_path.parent.mkdir(parents=True, exist_ok=True)

        # Render the authoritative or latest visible version to Markdown & optional DOCX
        latest_ver = versions_spec[-1]
        approved_vers = [v for v in versions_spec if v["status"] == "APPROVED"]
        display_ver = approved_vers[-1] if (approved_vers and d_spec["status"] != "ARCHIVED") else latest_ver

        ver_history_lines = [
            "| Version | Status | Author | Created At | Reviewed By | Reviewed At | Change Summary |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for v in versions_spec:
            ver_history_lines.append(
                f"| v{v['version_number']} | `{v['status']}` | `{owner_id}` | `{v['created_at']}` | "
                f"`{v.get('reviewed_by') or '-'}` | `{v.get('reviewed_at') or '-'}` | {v['change_summary']} |"
            )

        md_sections_str = []
        for h_title, bullets in display_ver["sections"]:
            md_sections_str.append(f"## {h_title}\n" + "\n".join(f"- {b}" for b in bullets))

        ref_tbl = display_ver.get("reference_table")
        if ref_tbl and len(ref_tbl) >= 2:
            hdr_line = "| " + " | ".join(ref_tbl[0]) + " |"
            sep_line = "| " + " | ".join(":---" for _ in ref_tbl[0]) + " |"
            body_lines = ["| " + " | ".join(r) + " |" for r in ref_tbl[1:]]
            md_sections_str.append("## Bảng Tham Chiếu Chi Tiết\n" + "\n".join([hdr_line, sep_line, *body_lines]))

        md_body = (
            f"# [{did}] {d_spec['title']}\n\n"
            f"- **Organization**: `{org_id}` (`100% Synthetic Continuum Dataset`)\n"
            f"- **Project**: `{pid}`\n"
            f"- **Document Type**: `{dtype}`\n"
            f"- **Current Snapshot Status**: `{d_spec['status']}`\n"
            f"- **Author (`created_by`)**: `{owner_id}`\n"
            f"- **Displayed Content Version**: `v{display_ver['version_number']}` (`{display_ver['status']}`)\n"
            f"- **Linked Tasks**: {', '.join(f'`{k}`' for k in d_spec.get('linked_task_keys', [])) or 'N/A'}\n\n"
            f"> {d_spec['summary']}\n\n"
            f"## Lịch Sử Phiên Bản & Phê Duyệt (Version Lineage)\n"
            + "\n".join(ver_history_lines)
            + "\n\n"
            + "\n\n".join(md_sections_str)
            + "\n"
        )
        md_path.write_text(md_body, encoding="utf-8", newline="\n")
        md_sha = sha256_file(md_path)

        rendition_paths: list[str] = []
        docx_sha: str | None = None
        if d_spec.get("render_docx", False):
            rel_docx = f"documents/docx/{did}.docx"
            docx_path = pkg_root / rel_docx
            meta_pairs = [
                ("Document ID", did, "Project", pid),
                ("Document Type", dtype, "Snapshot Status", d_spec["status"]),
                ("Owner", owner_id, "Displayed Version", f"v{display_ver['version_number']} ({display_ver['status']})"),
                ("Organization", org_id, "Synthetic Scope", "100% Synthetic Benchmark"),
            ]
            docx_sha = render_formal_docx(
                target_path=docx_path,
                org_banner=org_banner,
                doc_id=did,
                title=d_spec["title"],
                summary=d_spec["summary"],
                metadata_pairs=meta_pairs,
                sections=display_ver["sections"],
                reference_table=ref_tbl,
                fixed_dt=fixed_dt,
            )
            rendition_paths.append(rel_docx)

        approved_nums = [v["version_number"] for v in versions_spec if v["status"] == "APPROVED"]
        latest_app_num = max(approved_nums) if approved_nums else None
        knowledge_eligible = (latest_app_num is not None) and (d_spec["status"] != "ARCHIVED")

        for v in versions_spec:
            vnum = v["version_number"]
            vid = synth_oid(namespace, "doc_version", f"{did}:v{vnum}")
            v_text = "\n".join(f"{h}: " + " ".join(bs) for h, bs in v["sections"])
            document_versions.append({
                "version_id": vid,
                "continuum_version_id": vid,
                "document_id": did,
                "project_id": pid,
                "organization_id": org_id,
                "version_number": vnum,
                "status": v["status"],
                "author_id": owner_id,
                "change_summary": v["change_summary"],
                "content_excerpt": v["content_excerpt"],
                "content_sha256": sha256_text(v_text),
                "created_at": v["created_at"],
                "work_mode": v.get("work_mode", "regular_hours"),
                "is_overtime": bool(v.get("is_overtime", False)),
                "submitted_at": v.get("submitted_at"),
                "reviewed_by": v.get("reviewed_by"),
                "reviewed_at": v.get("reviewed_at"),
                "review_work_mode": v.get("review_work_mode", "regular_hours"),
                "review_is_overtime": bool(v.get("review_is_overtime", False)),
                "review_comment": v.get("review_comment"),
                "knowledge_eligible": (v["status"] == "APPROVED") and (vnum == latest_app_num) and (d_spec["status"] != "ARCHIVED"),
                "synthetic": True,
            })

        project_documents.append({
            "document_id": did,
            "continuum_work_note_id": synth_oid(namespace, "project_doc", did),
            "project_id": pid,
            "organization_id": org_id,
            "title": d_spec["title"],
            "summary": d_spec["summary"],
            "document_type": dtype,
            "status": d_spec["status"],
            "created_by": owner_id,
            "current_version_number": versions_spec[-1]["version_number"],
            "latest_approved_version_number": latest_app_num,
            "knowledge_eligible": knowledge_eligible,
            "supersedes_document_id": d_spec.get("supersedes_document_id"),
            "superseded_by_document_id": d_spec.get("superseded_by_document_id"),
            "linked_task_ids": d_spec.get("linked_task_ids", []),
            "linked_task_keys": d_spec.get("linked_task_keys", []),
            "file_path": rel_md,
            "content_sha256": md_sha,
            "rendition_paths": rendition_paths,
            "docx_sha256": docx_sha,
            "created_at": versions_spec[0]["created_at"],
            "updated_at": max(
                [v.get("reviewed_at") or v["created_at"] for v in versions_spec]
            ),
            "synthetic": True,
        })

    return project_documents, document_versions


def build_id_mappings(
    namespace: str,
    primary_org_id: str,
    bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build complete deterministic Continuum target ID mapping table."""
    mappings: list[dict[str, Any]] = []

    def add(entity_type: str, source_file: str, source_id: str, target_id: str, org_id: str, pid: str | None, collection: str, eligible: bool, support: str, notes: str = "") -> None:
        mappings.append({
            "mapping_id": f"MAP-{entity_type.upper()}-{source_id}",
            "entity_type": entity_type,
            "source_file": source_file,
            "source_id": source_id,
            "target_continuum_id": target_id,
            "organization_id": org_id,
            "project_id": pid,
            "target_collection": collection,
            "import_eligible": eligible,
            "support_status": support,
            "notes": notes,
        })

    for o in bundle["organizations"]:
        eligible = o["org_id"] == primary_org_id
        add("organization", "structured/organizations.jsonl", o["org_id"], o["continuum_org_id"], o["org_id"], None, "organizations", eligible, "IMPORTER_REQUIRED" if eligible else "DATASET_METADATA_ONLY", o["org_type"])

    for u in bundle["users"]:
        eligible = u["primary_org_id"] == primary_org_id
        add("user", "structured/users.jsonl", u["user_id"], u["continuum_user_id"], u["primary_org_id"], None, "users", eligible, "IMPORTER_REQUIRED" if eligible else "DATASET_METADATA_ONLY", f"status={u['status']}")

    for om in bundle["organization_memberships"]:
        eligible = om["organization_id"] == primary_org_id
        add("organization_membership", "structured/organization_memberships.jsonl", om["membership_id"], synth_oid(namespace, "org_mem", om["membership_id"]), om["organization_id"], None, "organization_members", eligible, "IMPORTER_REQUIRED" if eligible else "DATASET_METADATA_ONLY", f"status={om['status']}")

    for p in bundle["projects"]:
        add("project", "structured/projects.jsonl", p["project_id"], p["continuum_project_id"], p["organization_id"], p["project_id"], "projects", True, "API_SUPPORTED", f"code={p['code']} methodology={p['methodology']}")

    for pm in bundle["project_memberships"]:
        add("project_membership", "structured/project_memberships.jsonl", pm["membership_id"], synth_oid(namespace, "proj_mem", pm["membership_id"]), pm["organization_id"], pm["project_id"], "project_members+project_member_roles", True, "API_SUPPORTED" if pm["status"] == "ACTIVE" else "IMPORTER_REQUIRED", f"status={pm['status']}")

    for s in bundle.get("sprints", []):
        add("sprint", "structured/sprints.jsonl", s["sprint_id"], s["continuum_sprint_id"], s["organization_id"], s["project_id"], "sprints", True, "IMPORTER_REQUIRED", f"status={s['status']}")

    for t in bundle["tasks"]:
        add("task", "structured/tasks.jsonl", t["task_id"], t["continuum_task_id"], t["organization_id"], t["project_id"], "tasks", True, "IMPORTER_REQUIRED", f"key={t['key']} status={t['status']}")

    for n in bundle["task_notes"]:
        add("task_note", "structured/task_notes.jsonl", n["note_id"], n["continuum_work_note_id"], n["organization_id"], n["project_id"], "work_notes", True, "IMPORTER_REQUIRED", "noteType=TASK_NOTE knowledge_eligible=false")

    for d in bundle["project_documents"]:
        add("project_document", "structured/project_documents.jsonl", d["document_id"], d["continuum_work_note_id"], d["organization_id"], d["project_id"], "work_notes+work_note_versions", True, "IMPORTER_REQUIRED", f"docType={d['document_type']} status={d['status']}")

    for r in bundle["work_reports"]:
        add("work_report", "structured/work_reports.jsonl", r["report_id"], r["continuum_work_note_id"], r["organization_id"], r["project_id"], "work_notes+work_note_versions", True, "IMPORTER_REQUIRED", f"scope={r['report_scope']} freq={r['frequency']} status={r['status']}")

    return mappings


def materialize_organization_package(
    pkg_root: Path,
    namespace: str,
    dataset_id: str,
    version: str,
    org_display_name: str,
    methodology_label: str,
    bundle: dict[str, Any],
    extra_structured_files: dict[str, list[dict[str, Any]]],
    negative_fixtures: list[dict[str, Any]],
    source_attribution: list[dict[str, Any]],
    assumptions: list[str],
    readme_markdown: str,
    ingestion_contract_markdown: str,
    fixed_dt: tuple[int, int, int, int, int, int] = (2026, 10, 16, 0, 0, 0),
) -> dict[str, Any]:
    """
    Validate bundle against Continuum rules, write all JSONL, fixtures, XLSX, docs, and manifest.json.
    """
    bundle["id_mappings"] = build_id_mappings(namespace, bundle["primary_org_id"], bundle)

    errors = validate_continuum_organization_bundle(bundle)
    if errors:
        joined = "\n  - ".join(errors[:25])
        raise ValueError(f"[{dataset_id}] Continuum validation failed ({len(errors)} errors):\n  - {joined}")

    # Write core structured JSONL files
    core_jsonl_map = {
        "structured/organizations.jsonl": bundle["organizations"],
        "structured/users.jsonl": bundle["users"],
        "structured/organization_memberships.jsonl": bundle["organization_memberships"],
        "structured/role_assignments.jsonl": bundle["role_assignments"],
        "structured/projects.jsonl": bundle["projects"],
        "structured/project_memberships.jsonl": bundle["project_memberships"],
        "structured/sprints.jsonl": bundle.get("sprints", []),
        "structured/tasks.jsonl": bundle["tasks"],
        "structured/task_comments.jsonl": bundle["task_comments"],
        "structured/task_worklogs.jsonl": bundle["task_worklogs"],
        "structured/task_events.jsonl": bundle["task_events"],
        "structured/task_notes.jsonl": bundle["task_notes"],
        "structured/project_documents.jsonl": bundle["project_documents"],
        "structured/document_versions.jsonl": bundle["document_versions"],
        "structured/work_report_settings.jsonl": bundle["work_report_settings"],
        "structured/work_reports.jsonl": bundle["work_reports"],
        "structured/disruption_events.jsonl": bundle.get("disruption_events", []),
        "structured/continuum_id_mapping.jsonl": bundle["id_mappings"],
    }
    for rel_p, rows in core_jsonl_map.items():
        write_jsonl(pkg_root / rel_p, rows)

    for rel_p, rows in sorted(extra_structured_files.items()):
        write_jsonl(pkg_root / rel_p, rows)

    # Write isolated evaluation suite
    write_jsonl(pkg_root / "evaluation/benchmark_cases.jsonl", bundle["evaluation_cases"])

    # Write test-only negative fixtures
    neg_path = pkg_root / "fixtures/negative_cases.json"
    neg_path.parent.mkdir(parents=True, exist_ok=True)
    neg_path.write_text(
        json.dumps(
            {
                "test_only": True,
                "description": "Deliberately invalid Continuum mutations verified to fail validate_continuum_organization_bundle.",
                "cases": negative_fixtures,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    # Build Excel Catalog
    tasks = bundle["tasks"]
    status_order = ["DONE", "IN_PROGRESS", "IN_REVIEW", "TODO", "BLOCKED", "CANCELLED"]
    status_breakdown = [(st, sum(1 for t in tasks if t["status"] == st)) for st in status_order]
    kpis = [
        ("Primary Org", bundle["primary_org_id"]),
        ("Methodology", methodology_label),
        ("Users", str(len(bundle["users"]))),
        ("Projects", str(len(bundle["projects"]))),
        ("Sprints", str(len(bundle.get("sprints", [])))),
        ("Tasks", str(len(tasks))),
        ("Task Notes", str(len(bundle["task_notes"]))),
        ("Project Docs", str(len(bundle["project_documents"]))),
        ("Work Reports", str(len(bundle["work_reports"]))),
        ("Eval Cases", str(len(bundle["evaluation_cases"]))),
    ]
    sheets = [
        ("Projects", bundle["projects"], ["project_id", "code", "name", "methodology", "status", "created_by", "start_date", "target_date"]),
        ("Users", bundle["users"], ["user_id", "display_name", "email", "primary_org_id", "job_title", "status", "joined_at", "left_at"]),
        ("Role Assignments", bundle["role_assignments"], ["assignment_id", "organization_id", "project_id", "user_id", "role_code"]),
        ("Sprints", bundle.get("sprints", []), ["sprint_id", "project_id", "name", "status", "start_date", "end_date", "goal"]),
        ("Tasks", tasks, ["task_id", "key", "project_id", "parent_id", "sprint_id", "type", "status", "priority", "assignee_id", "start_date", "due_date", "is_overtime", "work_mode", "title"]),
        ("Task Notes", bundle["task_notes"], ["note_id", "task_key", "project_id", "author_id", "status", "knowledge_eligible", "is_temporary_workaround", "created_at", "title"]),
        ("Project Documents", bundle["project_documents"], ["document_id", "project_id", "document_type", "status", "created_by", "current_version_number", "latest_approved_version_number", "knowledge_eligible", "file_path", "title"]),
        ("Work Reports", bundle["work_reports"], ["report_id", "project_id", "member_id", "report_scope", "frequency", "period_start", "period_end", "status", "is_overdue", "reviewed_by", "knowledge_eligible"]),
        ("Evaluation Cases", bundle["evaluation_cases"], ["case_id", "suite", "answer_channel", "case_category", "principal_id", "review_status", "split", "question", "expected_answer"]),
    ]
    build_excel_catalog(
        target_path=pkg_root / "Dataset_Catalog.xlsx",
        title=f"{org_display_name} — Continuum Synthetic Dataset ({version})",
        subtitle=f"As-of Date: {bundle['as_of_date']}  •  Methodology: {methodology_label}  •  100% Synthetic  •  Timezone: Asia/Ho_Chi_Minh (+07:00)",
        kpis=kpis,
        status_breakdown=status_breakdown,
        sheets=sheets,
        fixed_dt=fixed_dt,
    )

    # Write README.md and INGESTION_CONTRACT.md
    (pkg_root / "README.md").write_text(readme_markdown.strip() + "\n", encoding="utf-8", newline="\n")
    (pkg_root / "INGESTION_CONTRACT.md").write_text(ingestion_contract_markdown.strip() + "\n", encoding="utf-8", newline="\n")

    # Build file inventory excluding manifest.json
    inventory = build_file_inventory(pkg_root, exclude_names={"manifest.json"})
    manifest = {
        "dataset_id": dataset_id,
        "version": version,
        "organization_name": org_display_name,
        "primary_org_id": bundle["primary_org_id"],
        "methodology": methodology_label,
        "as_of_date": bundle["as_of_date"],
        "simulation_window": bundle["simulation_window"],
        "confirmed_product_scope": {
            "team_entity_included": False,
            "ai_chat_history_included": False,
            "fourth_notebook_entity_included": False,
            "group_note_forms": ["TASK_NOTE", "PROJECT_DOCUMENT", "WORK_REPORT"],
            "evaluation_review_status": "unreviewed (chưa duyệt)",
            "synthetic_data_only": True,
        },
        "implementation_assumptions": assumptions,
        "source_attribution": source_attribution,
        "canonical_counts": {
            "organizations": len(bundle["organizations"]),
            "users": len(bundle["users"]),
            "active_users": sum(1 for u in bundle["users"] if u["status"] == "ACTIVE"),
            "suspended_or_offboarded_users": sum(1 for u in bundle["users"] if u["status"] != "ACTIVE"),
            "organization_memberships": len(bundle["organization_memberships"]),
            "role_assignments": len(bundle["role_assignments"]),
            "projects": len(bundle["projects"]),
            "project_memberships": len(bundle["project_memberships"]),
            "sprints": len(bundle.get("sprints", [])),
            "tasks": len(bundle["tasks"]),
            "subtasks": sum(1 for t in bundle["tasks"] if t.get("parent_id")),
            "task_comments": len(bundle["task_comments"]),
            "task_worklogs": len(bundle["task_worklogs"]),
            "task_events": len(bundle["task_events"]),
            "task_notes": len(bundle["task_notes"]),
            "project_documents": len(bundle["project_documents"]),
            "docx_renditions": sum(len(d.get("rendition_paths", [])) for d in bundle["project_documents"]),
            "document_versions": len(bundle["document_versions"]),
            "work_report_settings": len(bundle["work_report_settings"]),
            "work_reports": len(bundle["work_reports"]),
            "disruption_events": len(bundle.get("disruption_events", [])),
            "evaluation_cases": len(bundle["evaluation_cases"]),
            "negative_fixtures": len(negative_fixtures),
            "continuum_id_mappings": len(bundle["id_mappings"]),
            "extra_structured_counts": {k: len(v) for k, v in sorted(extra_structured_files.items())},
            "physical_files_total": len(inventory) + 1,
            "file_inventory_entries": len(inventory),
        },
        "file_inventory": inventory,
    }
    manifest_path = pkg_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def build_org_identity_graph(
    namespace: str,
    primary_org_id: str,
    org_specs: list[tuple[str, str, str, str, str]],
    user_specs: list[tuple[str, str, str, str, str, str, str | None]],
    org_admin_ids: set[str],
    project_specs: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """
    Deterministically construct Continuum IAM entities:
    organizations, users, organization_memberships, role_assignments, projects, project_memberships.
    Roles are explicitly assigned (never inferred from job_title or department).
    """
    organizations: list[dict[str, Any]] = []
    for oid, name, org_type, domain, plan in org_specs:
        organizations.append({
            "org_id": oid,
            "continuum_org_id": synth_oid(namespace, "org", oid),
            "name": name,
            "org_type": org_type,
            "domain": domain,
            "plan": plan,
            "is_primary_continuum_tenant": oid == primary_org_id,
            "synthetic": True,
        })

    users: list[dict[str, Any]] = []
    org_memberships: list[dict[str, Any]] = []
    role_assignments: list[dict[str, Any]] = []
    org_domains = {oid: dom for oid, _, _, dom, _ in org_specs}

    for uid, display_name, oid, dept, job_title, joined_at, left_at in user_specs:
        is_offboarded = left_at is not None
        email_local = uid.lower().replace("-", ".")
        email = f"{email_local}@{org_domains[oid]}"
        users.append({
            "user_id": uid,
            "continuum_user_id": synth_oid(namespace, "user", uid),
            "display_name": display_name,
            "email": email,
            "primary_org_id": oid,
            "department_label": dept,
            "job_title": job_title,
            "status": "SUSPENDED" if is_offboarded else "ACTIVE",
            "joined_at": joined_at,
            "left_at": left_at,
            "synthetic": True,
        })
        om_id = f"OM-{oid}-{uid}"
        org_memberships.append({
            "membership_id": om_id,
            "organization_id": oid,
            "user_id": uid,
            "status": "REMOVED" if is_offboarded else "ACTIVE",
            "joined_at": joined_at,
            "left_at": left_at,
            "synthetic": True,
        })
        org_role = "ADMIN" if (oid == primary_org_id and uid in org_admin_ids) else "MEMBER"
        role_assignments.append({
            "assignment_id": f"RA-ORG-{oid}-{uid}",
            "organization_id": oid,
            "project_id": None,
            "user_id": uid,
            "role_code": org_role,
            "scope_note": "Explicit Continuum organization role (never inferred from job_title)",
            "synthetic": True,
        })

    projects: list[dict[str, Any]] = []
    project_memberships: list[dict[str, Any]] = []
    user_left_lookup = {u["user_id"]: u["left_at"] for u in users}

    for p_spec in project_specs:
        pid = p_spec["project_id"]
        code = p_spec["code"]
        leader_id = p_spec["leader_id"]
        creator_id = p_spec["created_by"]
        projects.append({
            "project_id": pid,
            "continuum_project_id": synth_oid(namespace, "project", pid),
            "organization_id": primary_org_id,
            "code": code,
            "name": p_spec["name"],
            "description": p_spec["description"],
            "methodology": p_spec["methodology"],
            "visibility": p_spec.get("visibility", "PRIVATE"),
            "status": "ACTIVE",
            "created_by": creator_id,
            "leader_id": leader_id,
            "start_date": p_spec["start_date"],
            "target_date": p_spec["target_date"],
            "synthetic": True,
        })
        roster_ids = list(
            dict.fromkeys([creator_id, leader_id, *p_spec["member_ids"], *p_spec.get("former_member_ids", [])])
        )
        for uid in roster_ids:
            is_off = user_left_lookup.get(uid) is not None
            pm_id = f"PM-{pid}-{uid}"
            project_memberships.append({
                "membership_id": pm_id,
                "organization_id": primary_org_id,
                "project_id": pid,
                "user_id": uid,
                "status": "INACTIVE" if is_off else "ACTIVE",
                "joined_at": p_spec["start_date"],
                "left_at": user_left_lookup.get(uid),
                "synthetic": True,
            })
            proj_role = "TEAM_LEADER" if uid == leader_id else "MEMBER"
            role_assignments.append({
                "assignment_id": f"RA-PRJ-{pid}-{uid}",
                "organization_id": primary_org_id,
                "project_id": pid,
                "user_id": uid,
                "role_code": proj_role,
                "scope_note": "Explicit Continuum project role",
                "synthetic": True,
            })

    return organizations, users, org_memberships, role_assignments, projects, project_memberships


def build_work_reports_for_org(
    namespace: str,
    org_id: str,
    projects: list[dict[str, Any]],
    org_admin_list: list[str],
    regular_members_by_project: dict[str, list[str]],
    docs_by_project: dict[str, list[str]],
    tasks_by_project: dict[str, list[str]],
    report_narratives: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Generate Work Report Settings + 9 Work Reports per project (36 total across 4 projects)
    covering WEEKLY & DAILY cadences, MEMBER->TEAM_LEADER & LEADER->Org ADMIN Manager flows,
    and statuses APPROVED, PENDING_REVIEW, CHANGES_REQUESTED, REJECTED, DRAFT, plus overdue DRAFT.
    """
    settings: list[dict[str, Any]] = []
    reports: list[dict[str, Any]] = []

    for p_idx, proj in enumerate(projects):
        pid = proj["project_id"]
        leader_id = proj["leader_id"]
        manager_id = org_admin_list[p_idx % len(org_admin_list)]
        if manager_id == leader_id:
            manager_id = org_admin_list[(p_idx + 1) % len(org_admin_list)]
        reg_members = regular_members_by_project[pid]
        p_docs = docs_by_project[pid]
        p_tasks = tasks_by_project[pid]
        nar = report_narratives[pid]

        settings.append({
            "setting_id": f"WRS-{pid}-MEMBER",
            "organization_id": org_id,
            "project_id": pid,
            "report_scope": "MEMBER",
            "frequency": "DAILY",
            "weekly_supplementary_enabled": True,
            "due_hour_ict": "17:00",
            "reviewer_role": "TEAM_LEADER_OR_ORG_ADMIN",
            "synthetic": True,
        })
        settings.append({
            "setting_id": f"WRS-{pid}-LEADER",
            "organization_id": org_id,
            "project_id": pid,
            "report_scope": "LEADER",
            "frequency": "WEEKLY",
            "daily_checkpoint_enabled": True,
            "due_hour_ict": "17:00",
            "reviewer_role": "ORG_ADMIN_MANAGER_ONLY",
            "synthetic": True,
        })

        # 9 reports per project (all timestamps fall on safe Oct 2026 Mon-Fri working days outside 12:00-13:00):
        # 1) WEEKLY MEMBER -> TEAM_LEADER (APPROVED, W40: 2026-09-28..2026-10-02, filed Mon 2026-10-05)
        # 2) WEEKLY MEMBER -> TEAM_LEADER (CHANGES_REQUESTED or REJECTED, W40, filed Mon 2026-10-05)
        # 3) WEEKLY LEADER -> ORG_ADMIN (APPROVED, W40, filed Mon 2026-10-05)
        # 4) WEEKLY MEMBER -> TEAM_LEADER (APPROVED, W41: 2026-10-05..2026-10-09, filed Mon 2026-10-12)
        # 5) WEEKLY LEADER -> ORG_ADMIN (APPROVED or CHANGES_REQUESTED, W41, filed Mon 2026-10-12)
        # 6) DAILY MEMBER -> TEAM_LEADER (APPROVED, 2026-10-13, filed Tue 2026-10-13)
        # 7) DAILY LEADER -> ORG_ADMIN (APPROVED, 2026-10-14, filed Wed 2026-10-14)
        # 8) DAILY MEMBER -> TEAM_LEADER (PENDING_REVIEW, 2026-10-15, filed Thu 2026-10-15)
        # 9) DAILY MEMBER -> TEAM_LEADER (DRAFT + is_overdue=True on p_idx%2==0 else DRAFT current on 2026-10-16)
        w2_status = "REJECTED" if p_idx == 1 else "CHANGES_REQUESTED"
        w5_status = "CHANGES_REQUESTED" if p_idx == 2 else "APPROVED"
        is_r9_overdue = (p_idx % 2 == 0)

        slots = [
            ("WR-W40-M1", "MEMBER", "WEEKLY", "2026-W40", "2026-09-28", "2026-10-02", reg_members[0], leader_id, "APPROVED", False, "2026-10-05T09:15:00+07:00", "2026-10-05T10:30:00+07:00", "2026-10-05T15:20:00+07:00", "2026-10-05T17:00:00+07:00", nar["weekly_member_ok"], [p_docs[0]], p_tasks[:2]),
            ("WR-W40-M2", "MEMBER", "WEEKLY", "2026-W40", "2026-09-28", "2026-10-02", reg_members[1 % len(reg_members)], leader_id, w2_status, False, "2026-10-05T09:40:00+07:00", "2026-10-05T11:10:00+07:00", "2026-10-05T16:05:00+07:00", "2026-10-05T17:00:00+07:00", nar["weekly_member_revise"], [p_docs[1]], p_tasks[2:4]),
            ("WR-W40-L1", "LEADER", "WEEKLY", "2026-W40", "2026-09-28", "2026-10-02", leader_id, manager_id, "APPROVED", False, "2026-10-05T13:30:00+07:00", "2026-10-05T14:45:00+07:00", "2026-10-06T09:30:00+07:00", "2026-10-06T17:00:00+07:00", nar["weekly_leader_w40"], p_docs[:2], p_tasks[:3]),
            ("WR-W41-M1", "MEMBER", "WEEKLY", "2026-W41", "2026-10-05", "2026-10-09", reg_members[2 % len(reg_members)], leader_id, "APPROVED", False, "2026-10-12T08:50:00+07:00", "2026-10-12T10:15:00+07:00", "2026-10-12T14:30:00+07:00", "2026-10-12T17:00:00+07:00", nar["weekly_member_w41"], [p_docs[2]], p_tasks[4:6]),
            ("WR-W41-L1", "LEADER", "WEEKLY", "2026-W41", "2026-10-05", "2026-10-09", leader_id, manager_id, w5_status, False, "2026-10-12T13:20:00+07:00", "2026-10-12T15:00:00+07:00", "2026-10-13T09:20:00+07:00", "2026-10-13T17:00:00+07:00", nar["weekly_leader_w41"], [p_docs[0], p_docs[2]], p_tasks[5:8]),
            ("WR-D1013-M1", "MEMBER", "DAILY", "2026-10-13", "2026-10-13", "2026-10-13", reg_members[0], leader_id, "APPROVED", False, "2026-10-13T16:10:00+07:00", "2026-10-13T16:25:00+07:00", "2026-10-14T08:45:00+07:00", "2026-10-14T10:00:00+07:00", nar["daily_member_ok"], [p_docs[0]], [p_tasks[0]]),
            ("WR-D1014-L1", "LEADER", "DAILY", "2026-10-14", "2026-10-14", "2026-10-14", leader_id, manager_id, "APPROVED", False, "2026-10-14T16:15:00+07:00", "2026-10-14T16:35:00+07:00", "2026-10-15T09:10:00+07:00", "2026-10-15T10:00:00+07:00", nar["daily_leader_ok"], [p_docs[1]], [p_tasks[1]]),
            ("WR-D1015-M1", "MEMBER", "DAILY", "2026-10-15", "2026-10-15", "2026-10-15", reg_members[3 % len(reg_members)], None, "PENDING_REVIEW", False, "2026-10-15T16:20:00+07:00", "2026-10-15T16:40:00+07:00", None, "2026-10-16T17:00:00+07:00", nar["daily_member_pending"], [p_docs[2]], [p_tasks[2]]),
            ("WR-D1014-M2", "MEMBER", "DAILY", "2026-10-14", "2026-10-14", "2026-10-14", reg_members[4 % len(reg_members)], None, "DRAFT", is_r9_overdue, "2026-10-15T08:30:00+07:00", None, None, "2026-10-15T11:00:00+07:00" if is_r9_overdue else "2026-10-16T17:00:00+07:00", nar["daily_member_draft"], [p_docs[0]], [p_tasks[3]]),
        ]

        for tag, scope, freq, pkey, p_start, p_end, author, reviewer, st, overdue_flag, c_at, sub_at, rev_at, due_at, summary_txt, d_ids, t_ids in slots:
            rid = f"{pid}-{tag}"
            rev_comment = None
            if st == "APPROVED":
                rev_comment = "Đã đối chiếu bằng chứng task, worklog và tài liệu dự án liên quan; phê duyệt báo cáo."
            elif st == "CHANGES_REQUESTED":
                rev_comment = "Yêu cầu bổ sung mã task bị chặn, số liệu kiểm thử hồi quy và kế hoạch xử lý dứt điểm trước khi duyệt lại."
            elif st == "REJECTED":
                rev_comment = "Từ chối báo cáo: trích dẫn nhầm bản nháp chưa được phê duyệt và thiếu bằng chứng nghiệm thu môi trường staging."

            reports.append({
                "report_id": rid,
                "continuum_work_note_id": synth_oid(namespace, "work_report", rid),
                "organization_id": org_id,
                "project_id": pid,
                "member_id": author,
                "report_scope": scope,
                "report_type": freq,
                "frequency": freq,
                "period_key": pkey,
                "period_start": p_start,
                "period_end": p_end,
                "status": st,
                "is_overdue": overdue_flag,
                "roster_submission_state": "OVERDUE" if overdue_flag else st,
                "due_at": due_at,
                "summary": summary_txt,
                "accomplishments": summary_txt,
                "blockers": nar["blocker_note"] if st in ("CHANGES_REQUESTED", "REJECTED", "PENDING_REVIEW") else None,
                "next_steps": nar["next_steps"],
                "document_ids": d_ids,
                "source_task_ids": t_ids,
                "created_at": c_at,
                "work_mode": "regular_hours",
                "is_overtime": False,
                "submitted_at": sub_at,
                "reviewed_by": reviewer,
                "reviewed_at": rev_at,
                "review_work_mode": "regular_hours",
                "review_is_overtime": False,
                "review_comment": rev_comment,
                "knowledge_eligible": st == "APPROVED",
                "synthetic": True,
            })

    return settings, reports


def build_standard_negative_fixtures(namespace: str, bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Return 8 structured negative test cases per organization that automated tests apply to a deep copy
    of `bundle` to verify `validate_continuum_organization_bundle` rejects contract/security violations.
    """
    primary_org = bundle["primary_org_id"]
    ext_user = next(u["user_id"] for u in bundle["users"] if u["primary_org_id"] != primary_org)
    first_proj = bundle["projects"][0]["project_id"]
    non_admin_leader = bundle["projects"][1]["leader_id"]
    approved_dv = next(dv for dv in bundle["document_versions"] if dv["status"] == "APPROVED")
    leader_rep = next(r for r in bundle["work_reports"] if r["report_scope"] == "LEADER" and r["status"] == "APPROVED")
    subtask = next(t for t in bundle["tasks"] if t.get("parent_id") is not None)
    root_other = next(
        t for t in bundle["tasks"]
        if t["project_id"] == subtask["project_id"]
        and t["task_id"] not in {subtask["task_id"], subtask["parent_id"]}
        and t.get("parent_id") is None
    )
    dis = bundle["disruption_events"][0]

    return [
        {
            "fixture_id": f"{namespace.upper()}-NEG-01",
            "mutation_type": "cross_tenant_project_membership",
            "payload": {
                "membership_id": f"PM-ILLEGAL-{ext_user}",
                "organization_id": primary_org,
                "project_id": first_proj,
                "user_id": ext_user,
                "status": "ACTIVE",
            },
            "expected_error_substring": "Cross-organization project_membership forbidden",
        },
        {
            "fixture_id": f"{namespace.upper()}-NEG-02",
            "mutation_type": "document_self_review",
            "target_version_id": approved_dv["version_id"],
            "author_id": approved_dv["author_id"],
            "expected_error_substring": "Invalid or self document review",
        },
        {
            "fixture_id": f"{namespace.upper()}-NEG-03",
            "mutation_type": "leader_report_non_admin_reviewer",
            "target_report_id": leader_rep["report_id"],
            "invalid_reviewer_id": non_admin_leader,
            "expected_error_substring": "LEADER report",
        },
        {
            "fixture_id": f"{namespace.upper()}-NEG-04",
            "mutation_type": "nested_subtask_depth_2",
            "target_task_id": root_other["task_id"],
            "new_parent_id": subtask["task_id"],
            "expected_error_substring": "1-level max subtask nesting",
        },
        {
            "fixture_id": f"{namespace.upper()}-NEG-05",
            "mutation_type": "lunch_break_human_action",
            "target_comment_id": bundle["task_comments"][0]["comment_id"],
            "invalid_timestamp": "2026-10-13T12:30:00+07:00",
            "expected_error_substring": "mandatory lunch break 12:00-13:00",
        },
        {
            "fixture_id": f"{namespace.upper()}-NEG-06",
            "mutation_type": "unavailable_window_activity",
            "target_worklog_id": bundle["task_worklogs"][0]["worklog_id"],
            "affected_user_id": dis["affected_user_id"],
            "invalid_timestamp": dis["unavailable_from"][:10] + "T10:15:00+07:00",
            "expected_error_substring": "during unavailable window",
        },
        {
            "fixture_id": f"{namespace.upper()}-NEG-07",
            "mutation_type": "task_note_marked_knowledge_eligible",
            "target_note_id": bundle["task_notes"][0]["note_id"],
            "expected_error_substring": "must NEVER have knowledge_eligible=True",
        },
        {
            "fixture_id": f"{namespace.upper()}-NEG-08",
            "mutation_type": "unreviewed_eval_marked_approved",
            "target_case_id": bundle["evaluation_cases"][0]["case_id"],
            "expected_error_substring": "review_status='unreviewed'",
        },
    ]
