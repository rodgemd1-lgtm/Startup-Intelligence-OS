"""Mirror the Oracle Health SharePoint corpus into Mike Job Studio storage.

This creates a Mike Job Studio-owned Supabase Storage prefix for the Oracle Health
SharePoint corpus by:
1. Copying already-uploaded Oracle Health objects server-side inside Supabase.
2. Repairing the original invalid-key failures from local disk using sanitized keys.
3. Refreshing Mike Job Studio studio-memory so the new storage location is queryable.
"""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
import json
import mimetypes
import re
import sys
import time
import unicodedata

from supabase import create_client
from supabase.lib.client_options import SyncClientOptions

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor
from susan_core.config import config
from scripts.build_mike_job_studio_email_corpus import (
    COMPANY_ID as MIKE_COMPANY_ID,
    COMPANY_MEMORY_ROOT,
    STUDIO_MEMORY_TYPE,
    _delete_existing,
    _write_locator,
)


BUCKET_NAME = "oracle-health-corpus"
BUCKET_PUBLIC = False
BUCKET_FILE_SIZE_LIMIT = 52_428_800
CHUNK_SIZE_BYTES = 45 * 1024 * 1024
SOURCE_COMPANY_ID = "oracle-health-ai-enablement"
TARGET_COMPANY_ID = "mike-job-studio"
SOURCE_PREFIX = f"{SOURCE_COMPANY_ID}/market-intelligence"
TARGET_PREFIX = f"{TARGET_COMPANY_ID}/linked-corpora/oracle-health-market-intelligence"
SOURCE_DIR = (
    BACKEND_ROOT
    / "data"
    / "studio_assets"
    / "companies"
    / SOURCE_COMPANY_ID
    / "raw-docs"
)
SOURCE_ARTIFACT_DIR = BACKEND_ROOT / "artifacts" / "oracle_health_corpus_storage"
SOURCE_MANIFEST_PATH = SOURCE_ARTIFACT_DIR / "manifest.json"
ARTIFACT_DIR = BACKEND_ROOT / "artifacts" / "mike_job_studio_oracle_health_storage"
MANIFEST_PATH = ARTIFACT_DIR / "manifest.json"
SUMMARY_PATH = ARTIFACT_DIR / "summary.json"
RETRY_LIMIT = 3
RETRY_SLEEP_SECONDS = 5


def ensure_bucket(supabase) -> None:
    buckets = supabase.storage.list_buckets()
    existing = None
    for bucket in buckets:
        bucket_id = bucket.id if hasattr(bucket, "id") else bucket.get("id")
        if bucket_id == BUCKET_NAME:
            existing = bucket
            break

    options = {
        "public": BUCKET_PUBLIC,
        "file_size_limit": BUCKET_FILE_SIZE_LIMIT,
    }
    if existing is None:
        supabase.storage.create_bucket(BUCKET_NAME, name=BUCKET_NAME, options=options)
        return

    current_public = existing.public if hasattr(existing, "public") else existing.get("public")
    current_limit = (
        existing.file_size_limit
        if hasattr(existing, "file_size_limit")
        else existing.get("file_size_limit")
    )
    if current_public != BUCKET_PUBLIC or int(current_limit or 0) < BUCKET_FILE_SIZE_LIMIT:
        supabase.storage.update_bucket(BUCKET_NAME, options)


def content_type_for(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def remote_size(bucket, path: str) -> int | None:
    try:
        info = bucket.info(path)
        return int(info.get("size")) if info.get("size") is not None else None
    except Exception:
        return None


def sanitize_relative_path(relative_path: str) -> str:
    normalized = unicodedata.normalize("NFKD", relative_path).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.replace("[", "(").replace("]", ")")
    normalized = normalized.replace("&", "and")
    normalized = re.sub(r"[^A-Za-z0-9./() _-]+", "-", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"/{2,}", "/", normalized)
    parts = [part.strip(" .") or "item" for part in normalized.split("/")]
    return "/".join(parts)


def target_storage_path(relative_path: str) -> str:
    return f"{TARGET_PREFIX}/{sanitize_relative_path(relative_path)}"


def copy_object(bucket, from_path: str, to_path: str, expected_size: int) -> str:
    existing_remote_size = remote_size(bucket, to_path)
    if existing_remote_size == expected_size:
        return "skipped"

    last_error: Exception | None = None
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            if existing_remote_size is not None:
                bucket.remove([to_path])
            bucket.copy(from_path, to_path)
            verified_size = remote_size(bucket, to_path)
            if verified_size != expected_size:
                raise RuntimeError(
                    f"Remote size mismatch after copy: expected={expected_size} remote={verified_size}"
                )
            return "copied"
        except Exception as exc:
            last_error = exc
            if attempt == RETRY_LIMIT:
                break
            time.sleep(RETRY_SLEEP_SECONDS * attempt)
            existing_remote_size = remote_size(bucket, to_path)

    raise RuntimeError(f"Failed to copy object {from_path} -> {to_path}: {last_error}") from last_error


def upload_object(bucket, storage_path: str, payload, content_type: str, expected_size: int) -> str:
    existing_remote_size = remote_size(bucket, storage_path)
    if existing_remote_size == expected_size:
        return "skipped"

    options = {
        "content-type": content_type,
        "cache-control": "3600",
    }

    last_error: Exception | None = None
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            if existing_remote_size is None:
                bucket.upload(storage_path, payload, options)
            else:
                bucket.update(storage_path, payload, options)
            verified_size = remote_size(bucket, storage_path)
            if verified_size != expected_size:
                raise RuntimeError(
                    f"Remote size mismatch after upload: expected={expected_size} remote={verified_size}"
                )
            return "uploaded"
        except Exception as exc:
            last_error = exc
            if attempt == RETRY_LIMIT:
                break
            time.sleep(RETRY_SLEEP_SECONDS * attempt)
            existing_remote_size = remote_size(bucket, storage_path)

    raise RuntimeError(f"Failed to upload object {storage_path}: {last_error}") from last_error


def upload_local_file(bucket, local_path: Path, storage_path: str, content_type: str) -> tuple[str, dict]:
    local_size = local_path.stat().st_size
    if local_size <= BUCKET_FILE_SIZE_LIMIT:
        status = upload_object(bucket, storage_path, str(local_path), content_type, local_size)
        return status, {
            "object_mode": "raw",
            "part_count": 1,
            "part_paths": [storage_path],
        }

    part_paths: list[str] = []
    part_sizes: list[int] = []
    overall_status = "skipped"

    with local_path.open("rb") as handle:
        part_index = 0
        while True:
            chunk = handle.read(CHUNK_SIZE_BYTES)
            if not chunk:
                break
            part_index += 1
            part_path = f"{storage_path}.part{part_index:04d}"
            part_status = upload_object(bucket, part_path, chunk, "application/octet-stream", len(chunk))
            if part_status == "uploaded":
                overall_status = "uploaded"
            part_paths.append(part_path)
            part_sizes.append(len(chunk))

    return overall_status, {
        "object_mode": "chunked",
        "part_count": len(part_paths),
        "part_paths": part_paths,
        "part_sizes": part_sizes,
        "chunk_size_bytes": CHUNK_SIZE_BYTES,
        "original_content_type": content_type,
    }


def build_entry(
    relative_path: str,
    local_path: Path,
    storage_path: str,
    content_type: str,
    status: str,
    extra: dict | None = None,
) -> dict:
    stat = local_path.stat()
    entry = {
        "company_id": TARGET_COMPANY_ID,
        "bucket_name": BUCKET_NAME,
        "storage_path": storage_path,
        "relative_path": relative_path,
        "local_path": str(local_path),
        "size_bytes": stat.st_size,
        "content_type": content_type,
        "status": status,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(),
    }
    if extra:
        entry.update(extra)
    return entry


def main() -> int:
    if not SOURCE_MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Source manifest not found: {SOURCE_MANIFEST_PATH}")
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Source corpus not found: {SOURCE_DIR}")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    source_manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    client_options = SyncClientOptions(storage_client_timeout=3600, postgrest_client_timeout=120)
    supabase = create_client(config.supabase_url, config.supabase_key, options=client_options)
    ensure_bucket(supabase)
    bucket = supabase.storage.from_(BUCKET_NAME)

    manifest: list[dict] = []
    copied_remote_objects = 0
    uploaded_local_repairs = 0
    skipped_existing = 0
    failed = 0
    sanitized_paths = 0
    repaired_from_local = 0
    ext_counts = Counter()
    started_at = datetime.now(tz=UTC)

    for index, source_entry in enumerate(source_manifest, start=1):
        relative_path = source_entry["relative_path"]
        local_path = Path(source_entry["local_path"])
        content_type = source_entry.get("content_type") or content_type_for(local_path)
        ext_counts[local_path.suffix.lower() or "<no_ext>"] += 1
        sanitized_relative = sanitize_relative_path(relative_path)
        target_path = target_storage_path(relative_path)
        if sanitized_relative != relative_path:
            sanitized_paths += 1

        try:
            if source_entry.get("status") in {"uploaded", "skipped"}:
                if source_entry.get("object_mode") == "chunked":
                    source_part_paths = source_entry.get("part_paths", [])
                    source_part_sizes = source_entry.get("part_sizes", [])
                    target_part_paths: list[str] = []
                    copied_any = False
                    for part_path, part_size in zip(source_part_paths, source_part_sizes):
                        suffix = part_path.rsplit(".part", 1)[-1]
                        target_part_path = f"{target_path}.part{suffix}"
                        part_status = copy_object(bucket, part_path, target_part_path, int(part_size))
                        copied_any = copied_any or part_status == "copied"
                        skipped_existing += 1 if part_status == "skipped" else 0
                        copied_remote_objects += 1 if part_status == "copied" else 0
                        target_part_paths.append(target_part_path)
                    manifest.append(
                        build_entry(
                            relative_path,
                            local_path,
                            target_path,
                            content_type,
                            "copied" if copied_any else "skipped",
                            {
                                "object_mode": "chunked",
                                "part_count": len(target_part_paths),
                                "part_paths": target_part_paths,
                                "part_sizes": source_part_sizes,
                                "chunk_size_bytes": source_entry.get("chunk_size_bytes", CHUNK_SIZE_BYTES),
                                "original_content_type": source_entry.get("original_content_type", content_type),
                                "source_storage_path": source_entry["storage_path"],
                                "source_part_paths": source_part_paths,
                            },
                        )
                    )
                else:
                    copy_status = copy_object(bucket, source_entry["storage_path"], target_path, int(source_entry["size_bytes"]))
                    skipped_existing += 1 if copy_status == "skipped" else 0
                    copied_remote_objects += 1 if copy_status == "copied" else 0
                    manifest.append(
                        build_entry(
                            relative_path,
                            local_path,
                            target_path,
                            content_type,
                            copy_status,
                            {
                                "object_mode": "raw",
                                "part_count": 1,
                                "part_paths": [target_path],
                                "source_storage_path": source_entry["storage_path"],
                            },
                        )
                    )
            else:
                repaired_from_local += 1
                upload_status, extra = upload_local_file(bucket, local_path, target_path, content_type)
                skipped_existing += 1 if upload_status == "skipped" else 0
                uploaded_local_repairs += 1 if upload_status == "uploaded" else 0
                extra["repair_reason"] = source_entry.get("error", "source storage upload failed")
                manifest.append(build_entry(relative_path, local_path, target_path, content_type, upload_status, extra))
        except Exception as exc:
            failed += 1
            entry = build_entry(relative_path, local_path, target_path, content_type, "failed")
            entry["error"] = str(exc)
            if source_entry.get("storage_path"):
                entry["source_storage_path"] = source_entry["storage_path"]
            manifest.append(entry)

        if index % 25 == 0 or index == len(source_manifest):
            print(
                json.dumps(
                    {
                        "processed": index,
                        "total": len(source_manifest),
                        "copied_remote_objects": copied_remote_objects,
                        "uploaded_local_repairs": uploaded_local_repairs,
                        "skipped_existing": skipped_existing,
                        "failed": failed,
                    }
                )
            )

    summary = {
        "company_id": TARGET_COMPANY_ID,
        "bucket_name": BUCKET_NAME,
        "bucket_public": BUCKET_PUBLIC,
        "storage_prefix": TARGET_PREFIX,
        "source_prefix": SOURCE_PREFIX,
        "source_dir": str(SOURCE_DIR),
        "artifact_dir": str(ARTIFACT_DIR),
        "started_at": started_at.isoformat(),
        "completed_at": datetime.now(tz=UTC).isoformat(),
        "file_count": len(source_manifest),
        "copied_remote_objects": copied_remote_objects,
        "uploaded_local_repairs": uploaded_local_repairs,
        "repaired_from_local_entries": repaired_from_local,
        "skipped_existing": skipped_existing,
        "failed": failed,
        "sanitized_paths": sanitized_paths,
        "ext_counts": dict(sorted(ext_counts.items())),
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    email_summary_path = BACKEND_ROOT / "artifacts" / "mike_job_studio_email_corpus" / "summary.json"
    if email_summary_path.exists():
        email_summary = json.loads(email_summary_path.read_text(encoding="utf-8"))
        _write_locator(email_summary)
        _delete_existing(MIKE_COMPANY_ID, STUDIO_MEMORY_TYPE)
        MarkdownIngestor().ingest(str(COMPANY_MEMORY_ROOT), company_id=MIKE_COMPANY_ID, data_type=STUDIO_MEMORY_TYPE)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
