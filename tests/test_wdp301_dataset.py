"""Integrity, separation, security canary, schema, and timeline tests for `wdp301-spring2027-dataset`."""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

DATASET_ROOT = Path(__file__).resolve().parent.parent
PKG_DIR = DATASET_ROOT / "wdp301-spring2027-dataset"
META_PATH = PKG_DIR / "metadata" / "timeline_and_mapping.json"
CHAT_SEED_PATH = PKG_DIR / "seed" / "chat_fixture.json"
WORK_SEED_PATH = PKG_DIR / "seed" / "workspace_enrichment_fixture.json"
EVAL_PATH = PKG_DIR / "eval" / "wdp301_eval_cases.json"
SEEDER_PATH = PKG_DIR / "scripts" / "seed_wdp301_dev.mjs"
README_PATH = PKG_DIR / "README.md"

OBJECT_ID_RE = re.compile(r"^[0-9a-f]{24}$")
FIXTURE_ID_RE = re.compile(r"^6f301[0-9a-f]{19}$")
UUID_V4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
VALID_REACTIONS = {"👍", "❤️", "😂", "😮", "😢", "🙏"}
FORBIDDEN_SEED_KEYS = {
    "expectedAnswer",
    "goldAnswer",
    "goldAnswers",
    "requiredAnswerFacts",
    "requiredSourceMessageIds",
    "requiredSourceIds",
    "expectedStatus",
    "forbiddenSubstrings",
    "evalCases",
    "groundTruth",
    "password",
    "passwordHash",
}
FORBIDDEN_SECRET_AND_PII_PATTERNS = [
    re.compile(r'"(?:password|passwordHash|secret|apiKey|serviceToken)"\s*:\s*"[^"]+"', re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"mongodb\+srv://[^\s'\"]+:[^\s'\"]+@[^\s'\"]*mongodb\.net", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"[A-Za-z0-9._%+-]+@gmail\.com", re.IGNORECASE),
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_keys(obj: object) -> set[str]:
    found: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            found.add(k)
            found.update(_walk_keys(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(_walk_keys(item))
    return found


def test_strict_separation_zero_secrets_and_zero_personal_emails() -> None:
    chat = _load(CHAT_SEED_PATH)
    work = _load(WORK_SEED_PATH)
    assert chat["synthetic"] is True and chat["containsGoldAnswers"] is False
    assert work["synthetic"] is True and work["containsGoldAnswers"] is False

    for label, payload in (("chat_fixture", chat), ("workspace_enrichment", work)):
        keys = _walk_keys(payload)
        assert keys.isdisjoint(FORBIDDEN_SEED_KEYS), (
            f"Forbidden gold/secret keys in {label}: {keys & FORBIDDEN_SEED_KEYS}"
        )

    for path in (
        META_PATH,
        CHAT_SEED_PATH,
        WORK_SEED_PATH,
        EVAL_PATH,
        SEEDER_PATH,
        README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for pat in FORBIDDEN_SECRET_AND_PII_PATTERNS:
            assert not pat.search(text), f"Forbidden pattern {pat.pattern} found in {path}"


def test_chat_fixture_chronology_edge_cases_and_human_only_invariants() -> None:
    meta = _load(META_PATH)
    chat = _load(CHAT_SEED_PATH)
    actor_keys = {a["key"] for a in meta["actors"]}
    convs = {c["key"]: c for c in chat["conversations"]}

    directs = [c for c in chat["conversations"] if c["type"] == "DIRECT"]
    rooms = [c for c in chat["conversations"] if c["type"] == "ROOM"]
    assert len(directs) == 7
    assert len(rooms) == 4

    seen_msg_ids: set[str] = set()
    seen_client_ids: set[str] = set()

    for conv_key, conv in convs.items():
        assert FIXTURE_ID_RE.match(conv["id"]), f"Bad conv id {conv['id']}"
        assert conv["ownerActorKey"] in conv["memberActorKeys"]
        if conv["type"] == "DIRECT":
            assert len(conv["memberActorKeys"]) == 2
        else:
            assert len(conv["memberActorKeys"]) >= 4
            assert conv.get("creationKey")
            assert conv.get("title")

        for non_member in chat["verifiedNonMemberActorKeys"]:
            assert non_member not in conv["memberActorKeys"]

        prev_ts: dt.datetime | None = None
        conv_msg_ids: set[str] = set()
        for msg in conv["messages"]:
            assert FIXTURE_ID_RE.match(msg["id"]), f"Bad msg id {msg['id']}"
            assert UUID_V4_RE.match(msg["clientMessageId"]), f"Bad UUID {msg['clientMessageId']}"
            assert msg["id"] not in seen_msg_ids
            assert msg["clientMessageId"] not in seen_client_ids
            assert msg["senderActorKey"] in conv["memberActorKeys"]
            assert msg["senderActorKey"] in actor_keys

            # Strictly human-only messages (0 pre-seeded AI bot replies)
            for ai_key in (
                "authorType",
                "assistantMention",
                "triggerMessageId",
                "assistantStatus",
                "assistantFailureCode",
                "assistantMeta",
                "sourceReferences",
            ):
                assert ai_key not in msg

            for reaction in msg.get("reactions", []):
                assert reaction["emoji"] in VALID_REACTIONS
                assert set(reaction["actorKeys"]).issubset(set(conv["memberActorKeys"]))

            base_day = dt.date(2026, 11, 28) + dt.timedelta(days=msg["dayOffset"])
            ts = dt.datetime.fromisoformat(f"{base_day.isoformat()}T{msg['timeLocal']}+07:00")
            if prev_ts is not None:
                assert ts > prev_ts, f"Non-ascending timestamp in {conv_key} at {msg['id']}"
            prev_ts = ts

            if msg["deletedOffsetMinutes"] is not None:
                assert msg["content"] == ""
                assert msg["isPinned"] is False
                assert msg["links"] == []
            else:
                assert msg["content"].strip() != ""

            if msg["replyToMessageId"] is not None:
                assert msg["replyToMessageId"] in conv_msg_ids

            seen_msg_ids.add(msg["id"])
            seen_client_ids.add(msg["clientMessageId"])
            conv_msg_ids.add(msg["id"])

    # DM-01 edge-case checks
    dm01 = convs["dm_wdp_01_pm_be"]
    dm01_msgs = dm01["messages"]
    assert len(dm01_msgs) > chat["uiInitialPageSizeReference"]
    off_page = dm01_msgs[: -chat["uiInitialPageSizeReference"]]
    assert len(off_page) >= 30

    # Last-week (-7d) guaranteed to fall in previous ISO calendar week for EVERY weekday
    last_week = [m for m in dm01_msgs if m["dayOffset"] == -7]
    assert len(last_week) >= 8
    for wd in range(7):
        anchor = dt.date(2026, 11, 23) + dt.timedelta(days=wd)
        prev_mon = anchor - dt.timedelta(days=anchor.weekday() + 7)
        prev_sun = prev_mon + dt.timedelta(days=6)
        assert prev_mon <= (anchor - dt.timedelta(days=7)) <= prev_sun

    # Long technical message (>1200 chars with all critical BE-114 facts in first 1180 chars)
    long_msgs = [m for m in dm01_msgs if len(m["content"]) >= 1200]
    assert long_msgs
    head = long_msgs[0]["content"][:1180]
    for token in (
        "12 giây",
        "45 giây",
        "PAYMENT_BOUNDED_RETRY_ENABLED=true",
        "không xóa bản ghi sổ cái",
        "403 FORBIDDEN",
    ):
        assert token in head

    # Midnight +07:00 boundary pair in DM-07
    dm07_msgs = convs["dm_wdp_07_pm_doc_midnight_pi"]["messages"]
    assert any(m["dayOffset"] == -1 and m["timeLocal"] >= "23:45:00" for m in dm07_msgs)
    assert any(m["dayOffset"] == 0 and m["timeLocal"] <= "00:15:00" for m in dm07_msgs)

    # Canary tokens strictly isolated to their designated conversations
    dm05_text = "\n".join(m["content"] for m in convs["dm_wdp_05_pm_db_sag_canary"]["messages"])
    rm04_text = "\n".join(m["content"] for m in convs["room_wdp_04_leaders_private"]["messages"])
    assert "CANARY-WDP-PRIV-01" in dm05_text and "CANARY-WDP-PRIV-02" in dm05_text
    assert "CANARY-WDP-LEADERS-ONLY-03" in rm04_text
    for conv_key, conv in convs.items():
        text = "\n".join(m["content"] for m in conv["messages"])
        if conv_key != "dm_wdp_05_pm_db_sag_canary":
            assert "CANARY-WDP-PRIV-01" not in text and "CANARY-WDP-PRIV-02" not in text
        if conv_key != "room_wdp_04_leaders_private":
            assert "CANARY-WDP-LEADERS-ONLY-03" not in text


def test_workspace_enrichment_covers_all_eight_projects_and_valid_handovers() -> None:
    meta = _load(META_PATH)
    work = _load(WORK_SEED_PATH)
    active_projects = set(meta["projects"].keys())
    assert len(active_projects) == 8

    assert {c["projectCode"] for c in work["taskComments"]} == active_projects
    assert {w["projectCode"] for w in work["taskWorklogs"]} == active_projects
    assert {n["projectCode"] for n in work["workNotes"]} == active_projects
    assert {r["projectCode"] for r in work["workReports"]} == active_projects

    assert len(work["taskComments"]) >= 50
    assert len(work["taskWorklogs"]) >= 30
    assert len(work["workNotes"]) >= 20
    assert any(n["schemaVersion"] == 2 for n in work["workNotes"])
    assert any(n["schemaVersion"] == 1 for n in work["workNotes"])

    report_statuses = {r["status"] for r in work["workReports"]}
    assert {"APPROVED", "PENDING_REVIEW", "CHANGES_REQUESTED", "DRAFT", "OVERDUE"}.issubset(
        report_statuses
    )

    assert len(work["handovers"]) == 2
    ho_statuses = {h["status"] for h in work["handovers"]}
    assert ho_statuses == {"OPEN", "COMPLETED"}
    for h in work["handovers"]:
        assert FIXTURE_ID_RE.match(h["id"])
        assert len(h["item"]["dependencyFingerprint"]) == 64
        assert len(h["revision"]["sourceFingerprint"]) == 64
        if h["status"] == "COMPLETED":
            assert h.get("completionReviewNote")


def test_eval_cases_disjoint_dev_test_sources_and_honest_provenance() -> None:
    chat = _load(CHAT_SEED_PATH)
    work = _load(WORK_SEED_PATH)
    ev = _load(EVAL_PATH)

    assert ev["synthetic"] is True
    assert ev["review_status"] == "unreviewed"

    valid_source_ids = set()
    for c in chat["conversations"]:
        for m in c["messages"]:
            valid_source_ids.add(m["id"])
    for n in work["workNotes"]:
        valid_source_ids.add(n["id"])
    for r in work["workReports"]:
        valid_source_ids.add(r["id"])
    for h in work["handovers"]:
        valid_source_ids.add(h["id"])

    seen_case_ids: set[str] = set()
    dev_sources: set[str] = set()
    test_sources: set[str] = set()
    acl_deny_count = 0

    for case in ev["cases"]:
        assert case["caseId"] not in seen_case_ids
        seen_case_ids.add(case["caseId"])
        assert case["split"] in {"dev", "test"}
        assert case["review_status"] == "unreviewed"
        assert case["reviewer_1"] is None and case["reviewer_2"] is None

        if str(case["expectedStatus"]).startswith(("DENY_", "REJECT_")):
            acl_deny_count += 1

        bucket = dev_sources if case["split"] == "dev" else test_sources
        for sid in [*case["requiredSourceIds"], *case["optionalSourceIds"]]:
            assert sid in valid_source_ids, f"Unknown source ID {sid} in {case['caseId']}"
            bucket.add(sid)

    assert dev_sources.isdisjoint(test_sources), (
        f"dev/test source overlap: {dev_sources & test_sources}"
    )
    assert len(ev["cases"]) >= 45
    assert acl_deny_count >= 6
    assert len(ev["liveE2eScenarios"]) == 3
