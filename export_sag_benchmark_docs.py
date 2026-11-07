"""Export indexed SAG benchmark project documents from PostgreSQL for MongoDB & Vault sync."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

ROOT = Path(__file__).resolve().parent
SAG_ROOT = ROOT.parent / "sag-laya-integration" / "SAG"
SAG_API_ROOT = SAG_ROOT / "apps" / "api"
if str(SAG_API_ROOT) not in sys.path:
    sys.path.insert(0, str(SAG_API_ROOT))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(SAG_ROOT)

from benchmark_support import (  # noqa: E402
    default_benchmark_project_id,
    default_benchmark_project_name,
)
from run_all_datasets_sag import ALL_SEVEN_KEYS  # noqa: E402


def _create_schema_engine(database_url: str, schema: str | None = None):
    schema_name = (schema or "sag").strip() or "sag"
    parsed_db = make_url(database_url)
    q_db = dict(parsed_db.query)
    q_db.pop("search_path", None)
    return create_async_engine(
        parsed_db.set(query=q_db),
        connect_args={"server_settings": {"search_path": f"{schema_name},public"}},
    )

MONGO_ORG_ID = "6ad615f6e1f989c367a1eac8"
MONGO_USER_ID = "6acc9a5425f02c9d92a01012"
TEAM_LEADER_ROLE_ID = "d0e4a4b1835649a8f2867257"

PROJECT_CODES = {
    "retrievalci_v0": "BENCH01",
    "vn_mteb": "BENCH02",
    "wixqa_enterprise": "BENCH03",
    "org1_northstar": "ORG1_NSC",
    "org2_nova": "ORG2_NOVA",
    "org3_cloudops": "ORG3_CLD",
    "org4_mediflow": "ORG4_MED",
}


def _infer_document_type(logical_source_id: str, filename: str) -> str:
    combined = f"{logical_source_id} {filename}".upper()
    if "ARCH" in combined:
        return "ARCHITECTURE"
    if "API" in combined:
        return "API_SPECIFICATION"
    if "DB" in combined or "DATA" in combined or "SCHEMA" in combined:
        return "DATABASE_DESIGN"
    if "REQ" in combined or "SRS" in combined or "PRD" in combined or "BRS" in combined:
        return "REQUIREMENT"
    if "DES" in combined or "UI" in combined or "UX" in combined:
        return "DESIGN"
    if "RSR" in combined or "RESEARCH" in combined or "BENCH" in combined:
        return "RESEARCH"
    if "MVP" in combined or "CHARTER" in combined:
        return "MVP"
    return "TECHNICAL_SPECIFICATION"


def _infer_continuum_status_and_eligibility(storage_path: str, logical_id: str) -> tuple[str, str, bool]:
    """Return (continuum_status, raw_dataset_status, knowledge_eligible) from materialized file header."""
    p = Path(storage_path)
    head = ""
    if p.exists() and p.suffix.lower() in (".md", ".txt", ".json"):
        try:
            head = p.read_text(encoding="utf-8", errors="ignore")[:600]
        except Exception:
            head = ""
    ke = "knowledge_eligible=false" not in head.lower() and "knowledge_eligible=`false`" not in head.lower()
    upper_head = head.upper()
    for raw_st, cont_st in (
        ("STATUS=PENDING_REVIEW", "PENDING_REVIEW"),
        ("STATUS=`PENDING_REVIEW`", "PENDING_REVIEW"),
        ("STATUS=IN REVIEW", "PENDING_REVIEW"),
        ("STATUS=`IN REVIEW`", "PENDING_REVIEW"),
        ("STATUS=CHANGES_REQUESTED", "CHANGES_REQUESTED"),
        ("STATUS=`CHANGES_REQUESTED`", "CHANGES_REQUESTED"),
        ("STATUS=REJECTED", "REJECTED"),
        ("STATUS=`REJECTED`", "REJECTED"),
        ("STATUS=ARCHIVED", "ARCHIVED"),
        ("STATUS=`ARCHIVED`", "ARCHIVED"),
        ("STATUS=SUPERSEDED", "ARCHIVED"),
        ("STATUS=`SUPERSEDED`", "ARCHIVED"),
        ("STATUS=DRAFT", "DRAFT"),
        ("STATUS=`DRAFT`", "DRAFT"),
        ("STATUS=OVERDUE", "DRAFT"),
        ("STATUS=`OVERDUE`", "DRAFT"),
        ("STATUS=CONFIRMED", "DRAFT"),
        ("STATUS=`CONFIRMED`", "DRAFT"),
    ):
        if raw_st in upper_head:
            raw_val = raw_st.split("=", 1)[1].strip("`")
            return cont_st, raw_val, False
    return ("APPROVED" if ke else "ARCHIVED"), ("APPROVED" if ke else "ARCHIVED"), ke


def _deterministic_oid(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]


async def export_all() -> dict:
    from sag_api.core.config import settings

    engine = _create_schema_engine(settings.database_url, getattr(settings, "database_schema", "sag"))
    projects_payload = []

    try:
        async with engine.begin() as conn:
            for key in ALL_SEVEN_KEYS:
                pid = default_benchmark_project_id(key, "ORG-NSC")
                project_name = default_benchmark_project_name(key)
                code = PROJECT_CODES[key]
                docs_rows = (
                    await conn.execute(
                        text(
                            """
                            SELECT
                                d.id AS sag_doc_id,
                                d.tenant_id,
                                d.project_id,
                                d.owner_id,
                                d.logical_source_id,
                                d.source_id,
                                d.filename,
                                d.content_type,
                                d.size_bytes,
                                d.storage_path,
                                d.status AS doc_status,
                                d.chunk_count,
                                d.event_count,
                                d.progress,
                                d.token_usage,
                                d.parser_provider,
                                d.parser_status,
                                d.created_at,
                                d.updated_at,
                                v.id AS sag_version_id,
                                v.version_no,
                                v.file_hash,
                                v.status AS ver_status,
                                v.search_status,
                                v.knowledge_status,
                                (
                                    SELECT r.id
                                    FROM ingestion_runs r
                                    WHERE r.document_version_id = v.id
                                    ORDER BY r.created_at DESC
                                    LIMIT 1
                                ) AS run_id,
                                (
                                    SELECT r.current_stage
                                    FROM ingestion_runs r
                                    WHERE r.document_version_id = v.id
                                    ORDER BY r.created_at DESC
                                    LIMIT 1
                                ) AS current_stage
                            FROM documents d
                            JOIN document_versions v ON v.document_id = d.id AND v.version_no = 1
                            WHERE d.project_id = :pid AND d.is_active = TRUE
                            ORDER BY d.logical_source_id ASC
                            """
                        ),
                        {"pid": pid},
                    )
                ).mappings().all()

                doc_items = []
                for row in docs_rows:
                    logical_id = str(row["logical_source_id"] or row["filename"])
                    mongo_doc_id = _deterministic_oid(f"continuum:doc:{pid}:{logical_id}")
                    mongo_ver_id = _deterministic_oid(f"continuum:ver:{pid}:{logical_id}:1")
                    vault_uuid = str(
                        uuid.uuid5(uuid.NAMESPACE_URL, f"continuum:vault:{pid}:{logical_id}:1")
                    )
                    storage_path = str(row["storage_path"] or "")
                    filename = str(row["filename"] or Path(logical_id).name)
                    doc_type = _infer_document_type(logical_id, filename)
                    cont_status, raw_ds_status, ke_flag = _infer_continuum_status_and_eligibility(storage_path, logical_id)
                    doc_items.append(
                        {
                            "mongoDocId": mongo_doc_id,
                            "mongoVerId": mongo_ver_id,
                            "vaultUuid": vault_uuid,
                            "logicalSourceId": logical_id,
                            "filename": filename,
                            "title": f"{filename} ({logical_id})" if logical_id != filename else filename,
                            "description": f"Synchronized benchmark corpus artifact ({logical_id}, status={raw_ds_status}, knowledge_eligible={ke_flag}) for {project_name}.",
                            "documentType": doc_type,
                            "continuumStatus": cont_status,
                            "datasetStatus": raw_ds_status,
                            "knowledgeEligible": ke_flag,
                            "contentType": str(row["content_type"] or "text/markdown"),
                            "sizeBytes": int(row["size_bytes"] or 0),
                            "storagePath": storage_path,
                            "fileHash": str(row["file_hash"] or ""),
                            "sagDocumentId": str(row["sag_doc_id"]),
                            "sagVersionId": str(row["sag_version_id"]),
                            "sagVersionNo": int(row["version_no"] or 1),
                            "sagSourceId": str(row["source_id"] or ""),
                            "runId": str(row["run_id"] or ""),
                            "currentStage": str(row["current_stage"] or "COMPLETE"),
                            "docStatus": str(row["doc_status"] or "READY"),
                            "verStatus": str(row["ver_status"] or "SEARCH_READY"),
                            "searchStatus": str(row["search_status"] or "SEARCH_READY"),
                            "knowledgeStatus": str(row["knowledge_status"] or "DATA_READY"),
                            "chunkCount": int(row["chunk_count"] or 0),
                            "eventCount": int(row["event_count"] or 0),
                            "progress": int(row["progress"] or 100),
                            "tokenUsage": int(row["token_usage"] or 0),
                            "parserProvider": str(row["parser_provider"] or "original"),
                            "parserStatus": str(row["parser_status"] or "ok"),
                            "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
                            "updatedAt": row["updated_at"].isoformat() if row["updated_at"] else None,
                        }
                    )

                projects_payload.append(
                    {
                        "datasetKey": key,
                        "projectId": pid,
                        "code": code,
                        "name": project_name,
                        "description": f"{project_name} — Synchronized E2E Benchmark Corpus ({len(doc_items)} indexed documents).",
                        "organizationId": MONGO_ORG_ID,
                        "userId": MONGO_USER_ID,
                        "teamLeaderRoleId": TEAM_LEADER_ROLE_ID,
                        "documents": doc_items,
                    }
                )
    finally:
        await engine.dispose()

    out_path = ROOT / "reports" / "sag-mongo-sync-manifest.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "organizationId": MONGO_ORG_ID,
        "userId": MONGO_USER_ID,
        "teamLeaderRoleId": TEAM_LEADER_ROLE_ID,
        "projectCount": len(projects_payload),
        "totalDocuments": sum(len(p["documents"]) for p in projects_payload),
        "projects": projects_payload,
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"Exported {payload['projectCount']} projects and {payload['totalDocuments']} documents to {out_path}",
        flush=True,
    )
    return payload


if __name__ == "__main__":
    asyncio.run(export_all())
