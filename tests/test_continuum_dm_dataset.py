"""Integrity, separation, security canary, and timeline tests for `continuum-dm-ai-dataset`."""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

DATASET_ROOT = Path(__file__).resolve().parent.parent
DM_DATASET_DIR = DATASET_ROOT / "continuum-dm-ai-dataset"
SEED_PATH = DM_DATASET_DIR / "seed" / "dm_seed_fixture.json"
EVAL_PATH = DM_DATASET_DIR / "eval" / "dm_eval_cases.json"
SCRIPT_PATH = DM_DATASET_DIR / "scripts" / "seed_dm_chat_dev.mjs"
README_PATH = DM_DATASET_DIR / "README.md"

OBJECT_ID_RE = re.compile(r"^[0-9a-f]{24}$")
UUID_V4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
FORBIDDEN_SEED_KEYS = {
    "expectedAnswer",
    "goldAnswer",
    "goldAnswers",
    "requiredAnswerFacts",
    "requiredSourceMessageIds",
    "expectedStatus",
    "forbiddenSubstrings",
    "evalCases",
    "groundTruth",
    "password",
    "passwordHash",
}
FORBIDDEN_SECRET_PATTERNS = [
    re.compile(r'"(?:password|passwordHash|secret|apiKey|serviceToken)"\s*:\s*"[^"]+"', re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"mongodb\+srv://[^\s'\"]+:[^\s'\"]+@[^\s'\"]*mongodb\.net", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]


def _load_seed() -> dict:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def _load_eval() -> dict:
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


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


def test_seed_and_eval_strict_separation_and_zero_secrets() -> None:
    seed = _load_seed()
    assert seed["synthetic"] is True
    assert seed["containsGoldAnswers"] is False

    seed_keys = _walk_keys(seed)
    assert seed_keys.isdisjoint(FORBIDDEN_SEED_KEYS), (
        f"Forbidden gold/secret keys found in seed fixture: {seed_keys & FORBIDDEN_SEED_KEYS}"
    )

    # Zero credentials or secrets across all dataset files
    for path in (SEED_PATH, EVAL_PATH, SCRIPT_PATH, README_PATH):
        text = path.read_text(encoding="utf-8")
        for pat in FORBIDDEN_SECRET_PATTERNS:
            assert not pat.search(text), f"Secret-like pattern {pat.pattern} found in {path}"


def test_seed_fixture_ids_chronology_off_page_and_human_only_invariants() -> None:
    seed = _load_seed()
    actor_by_key = {a["key"]: a for a in seed["actors"]}
    convs = {c["key"]: c for c in seed["conversations"]}
    assert set(convs.keys()) == {"dm_org1_ab", "dm_org1_ac", "dm_org2_xy"}

    seen_msg_ids: set[str] = set()
    seen_client_ids: set[str] = set()

    for conv_key, conv in convs.items():
        assert conv["type"] == "DIRECT"
        assert OBJECT_ID_RE.match(conv["id"])
        assert len(conv["memberActorKeys"]) == 2
        prev_ts: dt.datetime | None = None
        conv_msg_ids: set[str] = set()

        for msg in conv["messages"]:
            assert OBJECT_ID_RE.match(msg["id"]), f"Bad ObjectId {msg['id']}"
            assert UUID_V4_RE.match(msg["clientMessageId"]), f"Bad UUIDv4 {msg['clientMessageId']}"
            assert msg["id"] not in seen_msg_ids
            assert msg["clientMessageId"] not in seen_client_ids
            assert msg["senderActorKey"] in conv["memberActorKeys"]
            assert msg["senderActorKey"] in actor_by_key

            # Human messages only — zero pre-seeded AI bot fields
            assert "assistant" not in msg and "authorType" not in msg and "sourceReferences" not in msg

            # Anchor on 2026-11-28 (+07:00) and verify strict chronological order
            base_day = dt.date(2026, 11, 28) + dt.timedelta(days=msg["dayOffset"])
            ts = dt.datetime.fromisoformat(f"{base_day.isoformat()}T{msg['timeLocal']}+07:00")
            if prev_ts is not None:
                assert ts > prev_ts, f"Non-ascending timestamp in {conv_key} at {msg['id']}"
            prev_ts = ts

            if msg["deletedOffsetMinutes"] is not None:
                assert msg["content"] == ""
                assert msg["isPinned"] is False
            else:
                assert msg["content"].strip() != ""

            if msg["replyToMessageId"] is not None:
                assert msg["replyToMessageId"] in conv_msg_ids

            seen_msg_ids.add(msg["id"])
            seen_client_ids.add(msg["clientMessageId"])
            conv_msg_ids.add(msg["id"])

    # Verify A-B specific requirements
    ab = convs["dm_org1_ab"]
    ab_msgs = ab["messages"]
    page_size = seed["uiInitialPageSizeReference"]
    assert page_size == 50
    assert len(ab_msgs) > page_size  # 68 messages -> 18 strictly off-page
    off_page_msgs = ab_msgs[:-page_size]
    assert len(off_page_msgs) >= 15
    assert any(m["dayOffset"] <= -14 for m in off_page_msgs)

    # Last-week messages (-7d) must always fall in the previous ISO calendar week for EVERY weekday!
    last_week_msgs = [m for m in ab_msgs if m["dayOffset"] == -7]
    assert len(last_week_msgs) >= 8
    for weekday_offset in range(7):
        anchor = dt.date(2026, 11, 23) + dt.timedelta(days=weekday_offset)  # Mon..Sun
        prev_week_start = anchor - dt.timedelta(days=anchor.weekday() + 7)
        prev_week_end = prev_week_start + dt.timedelta(days=6)
        target = anchor + dt.timedelta(days=-7)
        assert prev_week_start <= target <= prev_week_end

    # Yesterday rich discussion, long technical message, correction, pre-edited, pre-deleted, live E2E candidates
    yesterday_msgs = [m for m in ab_msgs if m["dayOffset"] == -1]
    assert len(yesterday_msgs) >= 12
    long_msgs = [m for m in yesterday_msgs if len(m["content"]) >= 1200]
    assert long_msgs, "Missing long technical message (>= 1200 chars)"
    # All critical PAY-123 rollback/timeout facts must fit inside contract.md's 1200-char snippet cap!
    head_1180 = long_msgs[0]["content"][:1180]
    for token in ("10 giây", "45 giây", "8 giây", "PAY_PARTIAL_REFUND_ENABLED", "không xóa sổ cái"):
        assert token in head_1180, f"Expected '{token}' within first 1180 chars of long technical message"
    assert any("đính chính" in m["content"].lower() for m in yesterday_msgs), "Missing correction message"
    assert sum(1 for m in ab_msgs if m["editedOffsetMinutes"] is not None) >= 2
    assert sum(1 for m in ab_msgs if m["deletedOffsetMinutes"] is not None) >= 2

    candidates = ab["liveE2eCandidates"]
    ab_by_id = {m["id"]: m for m in ab_msgs}
    for key in ("editAfterOrBeforeAi", "deleteAfterAi", "prePostRaceEditOrDelete"):
        cand = candidates[key]
        msg = ab_by_id[cand["messageId"]]
        assert msg["senderActorKey"] == cand["senderActorKey"]
        assert msg["deletedOffsetMinutes"] is None
        assert cand["topicCode"] in msg["content"]

    # Non-member isolation in A-B
    assert "org1_user_c" not in ab["memberActorKeys"]
    assert "org1_manager" not in ab["memberActorKeys"]
    assert "org1_user_c" in ab["verifiedNonMemberActorKeys"]
    assert "org1_manager" in ab["verifiedNonMemberActorKeys"]


def test_canary_secrets_are_strictly_isolated_to_their_target_conversations() -> None:
    seed = _load_seed()
    text_by_conv = {
        c["key"]: "\n".join(m["content"] for m in c["messages"])
        for c in seed["conversations"]
    }

    ac_canaries = ["CANARY-AC-991", "ORCHID-8842-PRIVATE", "CANARY-AC-992", "PHOENIX-ALPHA", "VinaPay-VIP-09"]
    org2_canaries = ["CANARY-ORG2-774", "COBALT-7741-ORG2", "CANARY-ORG2-775", "QUARTZ-5509-ORG2", "DeltaAudit"]

    for token in ac_canaries:
        assert token in text_by_conv["dm_org1_ac"]
        assert token not in text_by_conv["dm_org1_ab"]
        assert token not in text_by_conv["dm_org2_xy"]

    for token in org2_canaries:
        assert token in text_by_conv["dm_org2_xy"]
        assert token not in text_by_conv["dm_org1_ab"]
        assert token not in text_by_conv["dm_org1_ac"]


def test_eval_cases_cover_all_required_categories_and_reference_valid_seed_ids() -> None:
    seed = _load_seed()
    eval_data = _load_eval()
    assert eval_data["synthetic"] is True

    msg_by_id: dict[str, tuple[str, int, dict]] = {}
    page_size = seed["uiInitialPageSizeReference"]
    off_page_ids: set[str] = set()
    for conv in seed["conversations"]:
        total = len(conv["messages"])
        for idx, msg in enumerate(conv["messages"]):
            msg_by_id[msg["id"]] = (conv["key"], idx, msg)
            if conv["key"] == "dm_org1_ab" and idx < total - page_size:
                off_page_ids.add(msg["id"])

    cases = eval_data["cases"]
    assert len(cases) >= 15

    cases_by_id = {c["caseId"]: c for c in cases}
    assert len(cases_by_id) == len(cases), "Duplicate caseId found in dm_eval_cases.json"

    dev_cases = [c for c in cases if c["split"] == "dev"]
    test_cases = [c for c in cases if c["split"] == "test"]
    dev_ids = {c["caseId"] for c in dev_cases}
    test_ids = {c["caseId"] for c in test_cases}
    assert dev_ids and test_ids
    assert dev_ids.isdisjoint(test_ids)
    assert len(dev_ids) + len(test_ids) == len(cases)

    # Strict dev/test evidence disjointness (zero required or optional source-message overlap across splits!)
    dev_required_source_ids = {mid for c in dev_cases for mid in c["requiredSourceMessageIds"]}
    test_required_source_ids = {mid for c in test_cases for mid in c["requiredSourceMessageIds"]}
    assert dev_required_source_ids and test_required_source_ids
    assert dev_required_source_ids.isdisjoint(test_required_source_ids), (
        f"dev/test requiredSourceMessageIds overlap: {sorted(dev_required_source_ids & test_required_source_ids)}"
    )

    dev_evidence_source_ids = {
        mid
        for c in dev_cases
        for mid in (c["requiredSourceMessageIds"] + c["optionalSourceMessageIds"])
    }
    test_evidence_source_ids = {
        mid
        for c in test_cases
        for mid in (c["requiredSourceMessageIds"] + c["optionalSourceMessageIds"])
    }
    assert dev_evidence_source_ids.isdisjoint(test_evidence_source_ids), (
        f"dev/test evidence source overlap: {sorted(dev_evidence_source_ids & test_evidence_source_ids)}"
    )

    # Robustness pairs (diacritics vs no-diacritics) must stay strictly within the same split (never dev <-> test)
    for case in cases:
        pair_id = case.get("robustnessPairOf")
        if pair_id is not None:
            assert pair_id in cases_by_id, f"Unknown robustnessPairOf {pair_id} on {case['caseId']}"
            paired = cases_by_id[pair_id]
            assert paired["split"] == case["split"], (
                f"Robustness pair {case['caseId']} ({case['split']}) leaks across split from {pair_id} ({paired['split']})"
            )
            assert paired["diacritics"] != case["diacritics"], (
                f"Robustness pair {case['caseId']} must contrast diacritics mode with {pair_id}"
            )

    # Both dev and test must cover diacritics + unaccented queries and strictly off-page required citations
    assert {c["diacritics"] for c in dev_cases} == {"with_diacritics", "without_diacritics"}
    assert {c["diacritics"] for c in test_cases} == {"with_diacritics", "without_diacritics"}
    assert dev_required_source_ids & off_page_ids, "dev split must require at least one off-page message ID"
    assert test_required_source_ids & off_page_ids, "test split must require at least one off-page message ID"

    categories: set[str] = set()
    has_diacritics = False
    has_no_diacritics = False
    has_off_page_required = False
    has_acl_deny_matrix = False

    for case in cases:
        categories.add(case["category"])
        assert case["review_status"] == "unreviewed"
        assert case["reviewer_1"] is None
        assert case["reviewer_2"] is None
        if case["diacritics"] == "with_diacritics":
            has_diacritics = True
        if case["diacritics"] == "without_diacritics":
            has_no_diacritics = True

        for mid in case["requiredSourceMessageIds"]:
            assert mid in msg_by_id, f"Unknown required source ID {mid} in {case['caseId']}"
            conv_key, _, msg = msg_by_id[mid]
            assert conv_key == case["conversationKey"], (
                f"Required source {mid} belongs to {conv_key}, not {case['conversationKey']}"
            )
            assert msg["deletedOffsetMinutes"] is None, (
                f"Required source {mid} in {case['caseId']} points to a deleted message!"
            )
            if mid in off_page_ids:
                has_off_page_required = True

        for mid in case["optionalSourceMessageIds"] + case["forbiddenSourceMessageIds"]:
            assert mid in msg_by_id, f"Unknown source ID {mid} in {case['caseId']}"

        if case["expectedStatus"] == "ACL_DENY":
            denied_actors = {item["actorKey"] for item in case["aclDenyActors"]}
            assert {"org1_user_c", "org1_manager", "org2_user_x"}.issubset(denied_actors)
            has_acl_deny_matrix = True

    assert has_diacritics and has_no_diacritics
    assert has_off_page_required, "Eval suite must require at least one strictly off-page message ID"
    assert has_acl_deny_matrix, "Eval suite must include ACL deny probes for C, Manager, and Org 2"

    required_category_prefixes = (
        "time_window_yesterday",
        "time_window_last_week",
        "correction_handling",
        "conflicting_unresolved",
        "off_page_older_history",
        "insufficient_evidence",
        "cross_conversation_canary",
        "cross_organization_canary",
        "prompt_injection",
    )
    for prefix in required_category_prefixes:
        assert any(cat.startswith(prefix) for cat in categories), f"Missing eval category prefix {prefix}"

    # Verify live E2E mutation scenarios forbid pre-seeded bot replies
    live_scenarios = eval_data["liveE2eMutationScenarios"]
    assert len(live_scenarios) == 3
    for sc in live_scenarios:
        assert sc["requiresLiveRuntime"] is True
        assert sc["preSeededBotReplyAllowed"] is False
        assert sc["candidateMessageId"] in msg_by_id
