"""Export available local Outlook cache mail into markdown and ingest it into Susan."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
import gzip
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import sys

from supabase import create_client

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor
from susan_core.config import config


STUDIO_ASSETS_ROOT = BACKEND_ROOT / "data" / "studio_assets"
OUTLOOK_FILES_ROOT = Path(
    "/Users/mikerodgers/Library/Group Containers/UBF8T346G9.Office/Outlook/Outlook 15 Profiles/Main Profile/Files"
)
EFM_ROOT = OUTLOOK_FILES_ROOT / "S0" / "4" / "EFMData"
COMPANY_ID = "mike-job-studio"
COMPANY_MEMORY_ROOT = STUDIO_ASSETS_ROOT / "companies" / COMPANY_ID
OUTPUT_ROOT = STUDIO_ASSETS_ROOT / "generated" / COMPANY_ID / "email_corpus"
LEGACY_SHARED_OUTPUT_ROOT = STUDIO_ASSETS_ROOT / "shared" / "memory" / "mike_job_studio_email_corpus"
MESSAGES_ROOT = OUTPUT_ROOT / "messages"
WORK_MESSAGES_ROOT = OUTPUT_ROOT / "work_messages"
AUTHORED_MESSAGES_ROOT = OUTPUT_ROOT / "authored_messages"
ARTIFACT_ROOT = BACKEND_ROOT / "artifacts" / "mike_job_studio_email_corpus"
LOCATOR_PATH = COMPANY_MEMORY_ROOT / "MIKE_JOB_STUDIO_DATA_LOCATOR.md"
ORACLE_HEALTH_COMPANY_ID = "oracle-health-ai-enablement"
ORACLE_HEALTH_ROOT = STUDIO_ASSETS_ROOT / "companies" / ORACLE_HEALTH_COMPANY_ID
ORACLE_HEALTH_RAW_DOCS_PATH = ORACLE_HEALTH_ROOT / "raw-docs"
ORACLE_HEALTH_LOCATOR_PATH = ORACLE_HEALTH_ROOT / "OH_MARKETING_AND_COMPETITIVE_INTELLIGENCE_LOCATOR.md"
ORACLE_HEALTH_STORAGE_SUMMARY_PATH = BACKEND_ROOT / "artifacts" / "oracle_health_corpus_storage" / "summary.json"
MIKE_ORACLE_HEALTH_STORAGE_SUMMARY_PATH = (
    BACKEND_ROOT / "artifacts" / "mike_job_studio_oracle_health_storage" / "summary.json"
)

STUDIO_MEMORY_TYPE = "studio_memory"
DATA_TYPE = "mike_job_studio_email"
WORK_DATA_TYPE = "mike_job_studio_email_work"
AUTHORED_DATA_TYPE = "mike_job_studio_email_authored"
LEGACY_SHARED_COMPANY_ID = "shared"
MIKE_EMAIL = "mike.r.rodgers@oracle.com"
CUTOFF_DAYS = 365


@dataclass
class EmailRecord:
    source_kind: str
    source_path: str
    email_date: datetime
    subject: str
    sender: str
    to: str
    cc: str
    body: str
    metadata_quality: str
    authored_by_mike: bool
    dedupe_key: str


def _delete_existing(company_id: str, data_type: str) -> None:
    supabase = create_client(config.supabase_url, config.supabase_key)
    supabase.table("knowledge_chunks").delete().eq("company_id", company_id).eq("data_type", data_type).execute()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "email"


def _clean_text(value: str) -> str:
    value = html.unescape(value)
    value = value.replace("\r", "\n").replace("\xa0", " ")
    value = re.sub(r"\n{3,}", "\n\n", value)
    value = re.sub(r"[ \t]+", " ", value)
    return "\n".join(line.strip() for line in value.split("\n")).strip()


def _html_to_text(raw_html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw_html)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|tr|li|table|h1|h2|h3|h4|h5|h6)>", "\n", text)
    text = re.sub(r"(?i)<li[^>]*>", "- ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    return _clean_text(text)


def _clean_html_fragment(value: str) -> str:
    return _clean_text(re.sub(r"(?is)<[^>]+>", " ", value))


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except Exception:
        return None
    if parsed is None:
        return None
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(tzinfo=None)
    return parsed


def _first_meaningful_line(body: str) -> str:
    skip_prefixes = (
        "confidential - oracle",
        "get outlook for mac",
        "this message is intended for oracle employees only",
        "including external recipients",
    )
    for line in body.splitlines():
        cleaned = " ".join(line.split())
        lowered = cleaned.lower()
        if not cleaned:
            continue
        if any(lowered.startswith(prefix) for prefix in skip_prefixes):
            continue
        if len(cleaned) < 6:
            continue
        return cleaned[:180]
    return "Outlook cache email"


def _quality_rank(value: str) -> int:
    return {"high": 3, "medium": 2, "low": 1}.get(value, 0)


def _dedupe_signature(subject: str, body: str) -> str:
    body_norm = re.sub(r"\s+", " ", body).strip().lower()
    subject_norm = subject.strip().lower()
    return hashlib.sha1(f"{subject_norm}\n{body_norm}".encode("utf-8")).hexdigest()


def _is_work_related(record: EmailRecord) -> bool:
    joined = "\n".join(
        [
            record.sender,
            record.to,
            record.cc,
            record.subject,
            record.body[:4000],
        ]
    ).lower()
    if "@oracle.com" in joined:
        return True
    work_markers = (
        "oracle restricted",
        "oracle internal",
        "oracle health",
        "competitive intel",
        "kpi",
        "guidepoint",
        "alphasights",
        "matt cohlmia",
        "bharat sutariya",
        "seema",
        "provider business models",
        "erp opportunity",
        "annual goals",
    )
    return any(marker in joined for marker in work_markers)


def _parse_mime(path: Path) -> EmailRecord | None:
    with path.open("rb") as handle:
        message = BytesParser(policy=policy.default).parse(handle)

    body = ""
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_content()
                    break
                except Exception:
                    continue
        if not body:
            for part in message.walk():
                if part.get_content_disposition() == "attachment":
                    continue
                if part.get_content_type() == "text/html":
                    try:
                        body = _html_to_text(part.get_content())
                        break
                    except Exception:
                        continue
    else:
        try:
            body = message.get_content()
        except Exception:
            body = ""
        if message.get_content_type() == "text/html":
            body = _html_to_text(body)

    email_date = _parse_date(message.get("Date")) or datetime.fromtimestamp(path.stat().st_mtime)
    subject = _clean_text(message.get("Subject", "")) or _first_meaningful_line(body)
    sender = _clean_text(message.get("From", ""))
    to = _clean_text(message.get("To", ""))
    cc = _clean_text(message.get("Cc", ""))
    body = _clean_text(body)

    return EmailRecord(
        source_kind="mime",
        source_path=str(path),
        email_date=email_date,
        subject=subject,
        sender=sender,
        to=to,
        cc=cc,
        body=body,
        metadata_quality="high",
        authored_by_mike=MIKE_EMAIL in sender.lower(),
        dedupe_key=_dedupe_signature(subject, body),
    )


def _extract_html_header(raw_html: str, label: str) -> str:
    pattern = rf"{label}:<\/b>&nbsp;(.*?)<br"
    match = re.search(pattern, raw_html, re.IGNORECASE | re.DOTALL)
    if not match:
        pattern = rf"{label}:\s*(.*?)(?:<br|\n)"
        match = re.search(pattern, raw_html, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return _clean_html_fragment(match.group(1))


def _parse_dat(path: Path) -> EmailRecord | None:
    raw_html = gzip.decompress(path.read_bytes()).decode("utf-8", errors="ignore")
    body = _html_to_text(raw_html)

    sender = _extract_html_header(raw_html, "From")
    sent = _extract_html_header(raw_html, "Sent")
    to = _extract_html_header(raw_html, "To")
    cc = _extract_html_header(raw_html, "Cc")
    subject = _extract_html_header(raw_html, "Subject")

    email_date = _parse_date(sent) or datetime.fromtimestamp(path.stat().st_mtime)
    if not subject:
        subject = _first_meaningful_line(body)

    populated_fields = sum(bool(value) for value in (sender, sent, to, subject))
    metadata_quality = "medium" if populated_fields >= 3 else "low"

    return EmailRecord(
        source_kind="efm_html",
        source_path=str(path),
        email_date=email_date,
        subject=subject,
        sender=sender,
        to=to,
        cc=cc,
        body=body,
        metadata_quality=metadata_quality,
        authored_by_mike=MIKE_EMAIL in sender.lower(),
        dedupe_key=_dedupe_signature(subject, body),
    )


def _choose_record(candidate: EmailRecord, existing: EmailRecord) -> EmailRecord:
    if _quality_rank(candidate.metadata_quality) != _quality_rank(existing.metadata_quality):
        return candidate if _quality_rank(candidate.metadata_quality) > _quality_rank(existing.metadata_quality) else existing
    if candidate.source_kind != existing.source_kind:
        return candidate if candidate.source_kind == "mime" else existing
    return candidate if candidate.email_date > existing.email_date else existing


def _collect_records() -> tuple[list[EmailRecord], dict[str, int]]:
    cutoff = datetime.now() - timedelta(days=CUTOFF_DAYS)
    raw_records: list[EmailRecord] = []
    source_counts = {"mime": 0, "efm_html": 0}

    for mime_path in sorted(OUTLOOK_FILES_ROOT.rglob("*.mime")):
        record = _parse_mime(mime_path)
        if record and record.email_date >= cutoff:
            raw_records.append(record)
            source_counts["mime"] += 1

    for dat_path in sorted(EFM_ROOT.glob("*.dat")):
        record = _parse_dat(dat_path)
        if record and record.email_date >= cutoff:
            raw_records.append(record)
            source_counts["efm_html"] += 1

    deduped: dict[str, EmailRecord] = {}
    for record in raw_records:
        current = deduped.get(record.dedupe_key)
        deduped[record.dedupe_key] = record if current is None else _choose_record(record, current)

    ordered = sorted(deduped.values(), key=lambda item: (item.email_date, item.subject.lower()))
    return ordered, source_counts


def _write_record(path: Path, record: EmailRecord) -> None:
    path.write_text(
        "\n".join(
            [
                "# Mike Job Studio Email",
                "",
                f"- company_id: `{COMPANY_ID}`",
                f"- data_type: `{DATA_TYPE}`",
                f"- source_kind: `{record.source_kind}`",
                f"- source_path: `{record.source_path}`",
                "- extraction_basis: `local Outlook cache`",
                f"- metadata_quality: `{record.metadata_quality}`",
                f"- authored_by_mike: `{'true' if record.authored_by_mike else 'false'}`",
                f"- email_date: `{record.email_date.isoformat()}`",
                f"- subject: `{record.subject}`",
                f"- from: `{record.sender or 'unknown'}`",
                f"- to: `{record.to or 'unknown'}`",
                f"- cc: `{record.cc or 'none'}`",
                "",
                "## Body",
                "",
                record.body or "[No body extracted]",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_locator(summary: dict[str, object]) -> None:
    COMPANY_MEMORY_ROOT.mkdir(parents=True, exist_ok=True)

    oracle_health_lines = [
        f"- Oracle Health raw corpus path: `{ORACLE_HEALTH_RAW_DOCS_PATH}`",
        f"- Oracle Health locator: `{ORACLE_HEALTH_LOCATOR_PATH}`",
    ]
    if ORACLE_HEALTH_STORAGE_SUMMARY_PATH.exists():
        oracle_summary = json.loads(ORACLE_HEALTH_STORAGE_SUMMARY_PATH.read_text(encoding="utf-8"))
        oracle_health_lines.extend(
            [
                f"- Oracle Health Supabase bucket: `{oracle_summary.get('bucket_name', 'unknown')}`",
                f"- Oracle Health storage prefix: `{oracle_summary.get('storage_prefix', 'unknown')}`",
                f"- Oracle Health uploaded objects: `{oracle_summary.get('uploaded', 'unknown')}`",
                f"- Oracle Health failed objects: `{oracle_summary.get('failed', 'unknown')}`",
            ]
        )

    mike_oracle_health_lines: list[str] = []
    if MIKE_ORACLE_HEALTH_STORAGE_SUMMARY_PATH.exists():
        mike_oracle_summary = json.loads(MIKE_ORACLE_HEALTH_STORAGE_SUMMARY_PATH.read_text(encoding="utf-8"))
        mike_oracle_health_lines = [
            "## Mike Job Studio Oracle Health storage mirror",
            "",
            f"- mirror bucket: `{mike_oracle_summary.get('bucket_name', 'unknown')}`",
            f"- mirror prefix: `{mike_oracle_summary.get('storage_prefix', 'unknown')}`",
            f"- files represented: `{mike_oracle_summary.get('file_count', 'unknown')}`",
            f"- remote copies created: `{mike_oracle_summary.get('copied_remote_objects', 'unknown')}`",
            f"- local repair uploads: `{mike_oracle_summary.get('uploaded_local_repairs', 'unknown')}`",
            f"- skipped existing objects: `{mike_oracle_summary.get('skipped_existing', 'unknown')}`",
            f"- failed mirror operations: `{mike_oracle_summary.get('failed', 'unknown')}`",
            f"- manifest path: `{mike_oracle_summary.get('artifact_dir', 'unknown')}/manifest.json`",
            "",
        ]

    locator_lines = [
        "# Mike Job Studio Data Locator",
        "",
        "## Purpose",
        "",
        "This file registers the currently attached Mike Job Studio datasets inside Startup Intelligence OS.",
        "",
        "## Mike Job Studio email corpus",
        "",
        f"- company_id: `{COMPANY_ID}`",
        f"- data_type (all): `{DATA_TYPE}`",
        f"- data_type (work): `{WORK_DATA_TYPE}`",
        f"- data_type (authored): `{AUTHORED_DATA_TYPE}`",
        f"- corpus path: `{OUTPUT_ROOT}`",
        f"- message path: `{MESSAGES_ROOT}`",
        f"- work message path: `{WORK_MESSAGES_ROOT}`",
        f"- authored message path: `{AUTHORED_MESSAGES_ROOT}`",
        f"- summary path: `{ARTIFACT_ROOT / 'summary.json'}`",
        f"- unique markdown emails written: `{summary['unique_records_written']}`",
        f"- work-related markdown emails written: `{summary['work_related']}`",
        f"- authored by Mike: `{summary['authored_by_mike']}`",
        f"- available cache window start: `{summary['available_date_window']['start']}`",
        f"- available cache window end: `{summary['available_date_window']['end']}`",
        "",
        "## Coverage caveat",
        "",
        str(summary["caveat"]),
        "",
        "## Linked Oracle Health corpus",
        "",
        *oracle_health_lines,
        "",
        *mike_oracle_health_lines,
        "## Retrieval instructions",
        "",
        "Use the Mike Job Studio company when querying the email corpus. Use the locator files to jump into linked raw corpora that are not fully embedded as markdown.",
        "",
        f"- Susan company_id: `{COMPANY_ID}`",
        f"- Query authored writing style with data_type: `{AUTHORED_DATA_TYPE}`",
        f"- Query work-memory with data_type: `{WORK_DATA_TYPE}`",
        f"- Query broad cache recall with data_type: `{DATA_TYPE}`",
        "",
    ]
    LOCATOR_PATH.write_text("\n".join(locator_lines), encoding="utf-8")


def _write_outputs(records: list[EmailRecord], source_counts: dict[str, int]) -> dict[str, object]:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    if LEGACY_SHARED_OUTPUT_ROOT.exists():
        shutil.rmtree(LEGACY_SHARED_OUTPUT_ROOT)
    if ARTIFACT_ROOT.exists():
        shutil.rmtree(ARTIFACT_ROOT)

    MESSAGES_ROOT.mkdir(parents=True, exist_ok=True)
    WORK_MESSAGES_ROOT.mkdir(parents=True, exist_ok=True)
    AUTHORED_MESSAGES_ROOT.mkdir(parents=True, exist_ok=True)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

    authored_by_mike = 0
    work_related = 0
    metadata_counts = {"high": 0, "medium": 0, "low": 0}
    files = []
    work_files = []
    authored_files = []

    for index, record in enumerate(records, start=1):
        authored_by_mike += 1 if record.authored_by_mike else 0
        metadata_counts[record.metadata_quality] += 1
        stem = f"{record.email_date.date().isoformat()}-{index:04d}-{_slugify(record.subject)}"
        target = MESSAGES_ROOT / f"{stem}.md"
        _write_record(target, record)
        files.append(str(target))
        if _is_work_related(record):
            work_target = WORK_MESSAGES_ROOT / f"{stem}.md"
            _write_record(work_target, record)
            work_files.append(str(work_target))
            work_related += 1
        if record.authored_by_mike:
            authored_target = AUTHORED_MESSAGES_ROOT / f"{stem}.md"
            _write_record(authored_target, record)
            authored_files.append(str(authored_target))

    min_date = min(record.email_date for record in records)
    max_date = max(record.email_date for record in records)
    summary = {
        "company_id": COMPANY_ID,
        "data_types": {
            "all": DATA_TYPE,
            "work": WORK_DATA_TYPE,
            "authored": AUTHORED_DATA_TYPE,
        },
        "source_root": str(OUTLOOK_FILES_ROOT),
        "output_root": str(OUTPUT_ROOT),
        "raw_records_scanned": sum(source_counts.values()),
        "raw_source_counts": source_counts,
        "unique_records_written": len(records),
        "work_related": work_related,
        "authored_by_mike": authored_by_mike,
        "metadata_counts": metadata_counts,
        "available_date_window": {
            "start": min_date.isoformat(),
            "end": max_date.isoformat(),
        },
        "caveat": (
            "This corpus reflects the locally available Outlook cache on disk. "
            "The discovered cache window is narrower than a full trailing year, so this is not a confirmed full-mailbox export."
        ),
        "files": files,
        "work_files": work_files,
        "authored_files": authored_files,
    }

    index_lines = [
        "# Mike Job Studio Email Corpus Index",
        "",
        "This corpus was exported from the locally available Outlook cache on Mike Rodgers' Mac and converted into markdown for Susan.",
        "",
        "## Coverage",
        "",
        f"- company_id: `{COMPANY_ID}`",
        f"- data_type (all): `{DATA_TYPE}`",
        f"- data_type (work): `{WORK_DATA_TYPE}`",
        f"- data_type (authored): `{AUTHORED_DATA_TYPE}`",
        f"- source_root: `{OUTLOOK_FILES_ROOT}`",
        f"- raw cache items scanned: `{summary['raw_records_scanned']}`",
        f"- raw `.mime` items: `{source_counts['mime']}`",
        f"- raw `EFMData/*.dat` items: `{source_counts['efm_html']}`",
        f"- unique markdown emails written: `{summary['unique_records_written']}`",
        f"- work-related markdown emails written: `{work_related}`",
        f"- authored by Mike (high-confidence sender match): `{authored_by_mike}`",
        f"- available cache window start: `{summary['available_date_window']['start']}`",
        f"- available cache window end: `{summary['available_date_window']['end']}`",
        "",
        "## Caveat",
        "",
        summary["caveat"],
        "",
        "## Querying",
        "",
        f"- Susan company_id: `{COMPANY_ID}`",
        f"- Susan data_type (all): `{DATA_TYPE}`",
        f"- Susan data_type (work): `{WORK_DATA_TYPE}`",
        f"- Susan data_type (authored): `{AUTHORED_DATA_TYPE}`",
        f"- corpus path: `{OUTPUT_ROOT}`",
        "",
    ]
    (OUTPUT_ROOT / "MIKE_JOB_STUDIO_EMAIL_CORPUS_INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")
    (ARTIFACT_ROOT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_locator(summary)
    return summary


def main() -> int:
    records, source_counts = _collect_records()
    if not records:
        raise SystemExit("No Outlook cache emails found in the available local profile window.")

    summary = _write_outputs(records, source_counts)
    _delete_existing(LEGACY_SHARED_COMPANY_ID, DATA_TYPE)
    _delete_existing(LEGACY_SHARED_COMPANY_ID, WORK_DATA_TYPE)
    _delete_existing(LEGACY_SHARED_COMPANY_ID, AUTHORED_DATA_TYPE)
    _delete_existing(COMPANY_ID, DATA_TYPE)
    _delete_existing(COMPANY_ID, WORK_DATA_TYPE)
    _delete_existing(COMPANY_ID, AUTHORED_DATA_TYPE)
    _delete_existing(COMPANY_ID, STUDIO_MEMORY_TYPE)

    ingestor = MarkdownIngestor()
    stored_all = ingestor.ingest(str(MESSAGES_ROOT), company_id=COMPANY_ID, data_type=DATA_TYPE)
    stored_work = ingestor.ingest(str(WORK_MESSAGES_ROOT), company_id=COMPANY_ID, data_type=WORK_DATA_TYPE)
    stored_authored = ingestor.ingest(str(AUTHORED_MESSAGES_ROOT), company_id=COMPANY_ID, data_type=AUTHORED_DATA_TYPE)
    stored_memory = ingestor.ingest(str(COMPANY_MEMORY_ROOT), company_id=COMPANY_ID, data_type=STUDIO_MEMORY_TYPE)

    result = {
        "company_id": COMPANY_ID,
        "data_types": {
            "all": DATA_TYPE,
            "work": WORK_DATA_TYPE,
            "authored": AUTHORED_DATA_TYPE,
            "studio_memory": STUDIO_MEMORY_TYPE,
        },
        "output_root": str(OUTPUT_ROOT),
        "stored_chunks": {
            "all": stored_all,
            "work": stored_work,
            "authored": stored_authored,
            "studio_memory": stored_memory,
        },
        "unique_records_written": summary["unique_records_written"],
        "work_related": summary["work_related"],
        "available_date_window": summary["available_date_window"],
        "authored_by_mike": summary["authored_by_mike"],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
