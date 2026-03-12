"""Upload the Oracle Health market intelligence corpus into Supabase Storage.

The corpus is mounted locally at:
    data/studio_assets/companies/oracle-health-ai-enablement/raw-docs

This script uploads the full raw document set into a private Supabase bucket and
emits a local manifest for auditability and resume-friendly reruns.
"""
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
import json
import mimetypes
import sys
import time

from supabase import create_client
from supabase.lib.client_options import SyncClientOptions

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from susan_core.config import config


COMPANY_ID = "oracle-health-ai-enablement"
BUCKET_NAME = "oracle-health-corpus"
BUCKET_PUBLIC = False
BUCKET_FILE_SIZE_LIMIT = 52_428_800
CHUNK_SIZE_BYTES = 45 * 1024 * 1024
STORAGE_PREFIX = f"{COMPANY_ID}/market-intelligence"
SOURCE_DIR = (
    BACKEND_ROOT
    / "data"
    / "studio_assets"
    / "companies"
    / COMPANY_ID
    / "raw-docs"
)
ARTIFACT_DIR = BACKEND_ROOT / "artifacts" / "oracle_health_corpus_storage"
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


def iter_files(source_dir: Path) -> list[Path]:
    files = [path for path in source_dir.rglob("*") if path.is_file()]
    return sorted(files, key=lambda path: (-(path.stat().st_size), path.relative_to(source_dir).as_posix()))


def storage_path_for(path: Path) -> str:
    return f"{STORAGE_PREFIX}/{path.relative_to(SOURCE_DIR).as_posix()}"


def content_type_for(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def remote_size(bucket, path: str) -> int | None:
    try:
        info = bucket.info(path)
        return int(info.get("size")) if info.get("size") is not None else None
    except Exception:
        return None


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


def upload_one(bucket, local_path: Path, storage_path: str, content_type: str) -> tuple[str, dict]:
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
    status = "skipped"

    with local_path.open("rb") as handle:
        part_index = 0
        while True:
            chunk = handle.read(CHUNK_SIZE_BYTES)
            if not chunk:
                break
            part_index += 1
            part_path = f"{storage_path}.part{part_index:04d}"
            part_status = upload_object(
                bucket,
                part_path,
                chunk,
                "application/octet-stream",
                len(chunk),
            )
            if part_status == "uploaded":
                status = "uploaded"
            part_paths.append(part_path)
            part_sizes.append(len(chunk))

    return status, {
        "object_mode": "chunked",
        "part_count": len(part_paths),
        "part_paths": part_paths,
        "part_sizes": part_sizes,
        "chunk_size_bytes": CHUNK_SIZE_BYTES,
        "original_content_type": content_type,
    }


def build_entry(local_path: Path, storage_path: str, content_type: str, status: str, extra: dict | None = None) -> dict:
    stat = local_path.stat()
    entry = {
        "company_id": COMPANY_ID,
        "bucket_name": BUCKET_NAME,
        "storage_path": storage_path,
        "relative_path": local_path.relative_to(SOURCE_DIR).as_posix(),
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
    if not SOURCE_DIR.exists():
        raise FileNotFoundError(f"Source corpus not found: {SOURCE_DIR}")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    client_options = SyncClientOptions(storage_client_timeout=3600, postgrest_client_timeout=120)
    supabase = create_client(config.supabase_url, config.supabase_key, options=client_options)
    ensure_bucket(supabase)
    bucket = supabase.storage.from_(BUCKET_NAME)

    files = iter_files(SOURCE_DIR)
    total_bytes = sum(path.stat().st_size for path in files)
    ext_counts = Counter(path.suffix.lower() or "<no_ext>" for path in files)

    manifest: list[dict] = []
    uploaded = 0
    skipped = 0
    failed = 0
    chunked = 0
    processed_bytes = 0
    started_at = datetime.now(tz=UTC)

    for index, local_path in enumerate(files, start=1):
        storage_path = storage_path_for(local_path)
        content_type = content_type_for(local_path)
        try:
            status, extra = upload_one(bucket, local_path, storage_path, content_type)
            if status == "uploaded":
                uploaded += 1
            else:
                skipped += 1
            if extra.get("object_mode") == "chunked":
                chunked += 1
            manifest.append(build_entry(local_path, storage_path, content_type, status, extra))
        except Exception as exc:
            failed += 1
            entry = build_entry(local_path, storage_path, content_type, "failed")
            entry["error"] = str(exc)
            manifest.append(entry)

        processed_bytes += local_path.stat().st_size
        if index % 10 == 0 or index == len(files):
            print(
                json.dumps(
                    {
                        "processed": index,
                        "total": len(files),
                        "uploaded": uploaded,
                        "skipped": skipped,
                        "chunked": chunked,
                        "failed": failed,
                        "processed_gb": round(processed_bytes / 1024 / 1024 / 1024, 2),
                        "total_gb": round(total_bytes / 1024 / 1024 / 1024, 2),
                    }
                )
            )

    summary = {
        "company_id": COMPANY_ID,
        "bucket_name": BUCKET_NAME,
        "bucket_public": BUCKET_PUBLIC,
        "storage_prefix": STORAGE_PREFIX,
        "source_dir": str(SOURCE_DIR),
        "artifact_dir": str(ARTIFACT_DIR),
        "started_at": started_at.isoformat(),
        "completed_at": datetime.now(tz=UTC).isoformat(),
        "file_count": len(files),
        "uploaded": uploaded,
        "skipped": skipped,
        "chunked_files": chunked,
        "failed": failed,
        "total_bytes": total_bytes,
        "ext_counts": dict(sorted(ext_counts.items())),
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    upload_object(
        bucket,
        f"{STORAGE_PREFIX}/_manifests/manifest.json",
        MANIFEST_PATH.read_bytes(),
        "application/json",
        MANIFEST_PATH.stat().st_size,
    )
    upload_object(
        bucket,
        f"{STORAGE_PREFIX}/_manifests/summary.json",
        SUMMARY_PATH.read_bytes(),
        "application/json",
        SUMMARY_PATH.stat().st_size,
    )
    print(json.dumps(summary, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
