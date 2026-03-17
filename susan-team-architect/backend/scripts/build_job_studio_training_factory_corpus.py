"""Build the Job Studio Training Factory corpus from local corpora and repos.

This script normalizes the local Oracle Health binary corpus, adjacent local repos,
and Susan behavioral-science/training docs into markdown/text files that can be
ingested later for Job Studio training workflows.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from pathlib import Path
import json
import os
import re
import subprocess
import sys
import zipfile
from xml.etree import ElementTree as ET

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


COMPANY_ID = "mike-job-studio"
STUDIO_ASSETS_ROOT = BACKEND_ROOT / "data" / "studio_assets"
GENERATED_ROOT = STUDIO_ASSETS_ROOT / "generated" / "job_studio_training_factory"
ARTIFACT_ROOT = BACKEND_ROOT / "artifacts" / "job_studio_training_factory_corpus"
ORACLE_SOURCE_ROOT = Path("/Users/mikerodgers/Desktop/OH Marketing and Competitive Intelligence")
REPO_SOURCES = {
    "oracle-health-ai-enablement": Path("/Users/mikerodgers/AI-Enablement-Oracle-Chat"),
    "oracle-health-vendor-intelligence": Path("/Users/mikerodgers/oracle-health-vendor-intelligence"),
    "founder-intelligence-os": Path("/Users/mikerodgers/founder-intelligence-os"),
    "ux-design-scraper": Path("/Users/mikerodgers/ux-design-scraper"),
}
BEHAVIORAL_SOURCES = {
    "be-module": BACKEND_ROOT / "data" / "be_module",
    "transformfit-training-editorial": BACKEND_ROOT / "data" / "domains" / "transformfit_training_intelligence" / "editorial",
    "training-research-agent": BACKEND_ROOT.parent / "agents" / "training-research-studio.md",
    "behavioral-economics-skill": BACKEND_ROOT.parent / "skills" / "behavioral-economics" / "SKILL.md",
}
OUTPUT_DIRS = {
    "oracle_health_extracted": GENERATED_ROOT / "oracle_health_extracted",
    "repo_harvest": GENERATED_ROOT / "repo_harvest",
    "behavioral_science_seed": GENERATED_ROOT / "behavioral_science_seed",
}
SUMMARY_PATH = ARTIFACT_ROOT / "summary.json"
MANIFEST_PATH = ARTIFACT_ROOT / "manifest.json"
FAILURES_PATH = ARTIFACT_ROOT / "failures.json"
PDFTOTEXT_BIN = os.environ.get("PDFTOTEXT_BIN", "/opt/homebrew/bin/pdftotext")
CHECKPOINT_EVERY = 5
TEXT_LIKE_SUFFIXES = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".csv",
    ".conf",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".css",
    ".html",
    ".sql",
    ".sh",
    ".rst",
    ".url",
}
MEDIA_SUFFIXES = {".mp4", ".m4a", ".png", ".jpg", ".jpeg", ".gif", ".mov"}
SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
}
EXTRACTION_TIMEOUT_SECONDS = 8


@dataclass
class ExtractedDoc:
    source_path: str
    relative_path: str
    group: str
    extractor: str
    status: str
    output_path: str | None
    char_count: int
    notes: list[str]


def _doc_entry(doc: ExtractedDoc) -> dict[str, object]:
    return {
        "group": doc.group,
        "source_path": doc.source_path,
        "relative_path": doc.relative_path,
        "extractor": doc.extractor,
        "status": doc.status,
        "output_path": doc.output_path,
        "char_count": doc.char_count,
        "notes": doc.notes,
    }


def _build_summary(
    all_docs: list[ExtractedDoc],
    group_summaries: dict[str, dict[str, object]],
    *,
    run_status: str,
    active_group: str | None = None,
) -> dict[str, object]:
    return {
        "company_id": COMPANY_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_status": run_status,
        "active_group": active_group,
        "generated_root": str(GENERATED_ROOT),
        "artifact_root": str(ARTIFACT_ROOT),
        "source_totals": {
            "documents_seen": len(all_docs),
            "documents_extracted": sum(1 for doc in all_docs if doc.status == "ok"),
            "documents_cached": sum(1 for doc in all_docs if doc.status == "cached"),
            "documents_skipped": sum(1 for doc in all_docs if doc.status == "skipped"),
            "documents_failed": sum(1 for doc in all_docs if doc.status == "error"),
            "extracted_chars": sum(doc.char_count for doc in all_docs if doc.status in {"ok", "cached"}),
        },
        "groups": group_summaries,
    }


def _write_checkpoint(
    all_docs: list[ExtractedDoc],
    group_summaries: dict[str, dict[str, object]],
    *,
    run_status: str,
    active_group: str | None = None,
) -> dict[str, object]:
    manifest = [_doc_entry(doc) for doc in all_docs]
    failures = [entry for entry in manifest if entry["status"] == "error"]
    summary = _build_summary(all_docs, group_summaries, run_status=run_status, active_group=active_group)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    FAILURES_PATH.write_text(json.dumps(failures, indent=2, ensure_ascii=True), encoding="utf-8")
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    return summary


def _safe_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _sanitize_segment(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._() -]+", "-", value).strip(" .") or "item"


def _target_path(group_root: Path, relative_path: str) -> Path:
    parts = [_sanitize_segment(part) for part in relative_path.split("/")]
    target = group_root.joinpath(*parts)
    return target.with_suffix(target.suffix + ".md")


def _read_text(path: Path) -> str:
    result = subprocess.run(
        ["/bin/cat", str(path)],
        capture_output=True,
        check=False,
        timeout=EXTRACTION_TIMEOUT_SECONDS,
    )
    payload = result.stdout
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return payload.decode(encoding)
        except Exception:
            continue
    return payload.decode("utf-8", errors="ignore")


def _textutil_to_text(path: Path) -> str:
    result = subprocess.run(
        ["/usr/bin/textutil", "-convert", "txt", "-stdout", str(path)],
        capture_output=True,
        text=True,
        check=False,
        timeout=EXTRACTION_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "textutil conversion failed")
    return result.stdout


def _mdls_text(path: Path) -> str:
    result = subprocess.run(
        ["/usr/bin/mdls", "-name", "kMDItemTextContent", "-raw", str(path)],
        capture_output=True,
        text=True,
        check=False,
        timeout=EXTRACTION_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        return ""
    text = result.stdout.strip()
    if text in {"(null)", '""'}:
        return ""
    return text


def _extract_zip_xml(path: Path, member_names: list[str]) -> str:
    lines: list[str] = []
    available_members = set(_zip_list(path))
    for member_name in member_names:
        if member_name not in available_members:
            continue
        raw = _zip_member(path, member_name)
        root = ET.fromstring(raw)
        text_nodes = [node.text.strip() for node in root.iter() if node.text and node.text.strip()]
        if text_nodes:
            lines.append("\n".join(text_nodes))
    return "\n\n".join(lines).strip()


def _extract_docx(path: Path) -> str:
    try:
        members = [
            name
            for name in _zip_list(path)
            if name.startswith("word/") and name.endswith(".xml")
        ]
        content = _extract_zip_xml(path, sorted(members))
        if content:
            return content
    except Exception:
        pass
    try:
        content = _textutil_to_text(path)
        if content.strip():
            return content
    except Exception:
        pass
    content = _mdls_text(path)
    if content.strip():
        return content
    raise RuntimeError("docx extraction failed across zip, textutil, and mdls fallbacks")


def _extract_pptx(path: Path) -> str:
    try:
        members = [
            name
            for name in _zip_list(path)
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
        lines: list[str] = []
        for index, member_name in enumerate(sorted(members), start=1):
            text = _extract_zip_xml(path, [member_name])
            if text:
                lines.append(f"# Slide {index}")
                lines.append(text)
                lines.append("")
        content = "\n".join(lines).strip()
        if content:
            return content
    except Exception:
        pass
    content = _mdls_text(path)
    if content.strip():
        return content
    raise RuntimeError("pptx extraction failed across zip and mdls fallbacks")


def _extract_pdf(path: Path) -> str:
    if Path(PDFTOTEXT_BIN).exists():
        result = subprocess.run(
            [PDFTOTEXT_BIN, str(path), "-"],
            capture_output=True,
            text=True,
            check=False,
            timeout=EXTRACTION_TIMEOUT_SECONDS,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    content = _mdls_text(path)
    if content.strip():
        return content
    raise RuntimeError(f"pdf extraction failed; pdftotext unavailable or returned no text for {path.name}")


def _extract_workbook(path: Path) -> str:
    try:
        shared_strings = _extract_shared_strings(path)
        sheet_members = [
            name
            for name in _zip_list(path)
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        ]
        lines: list[str] = []
        for index, member_name in enumerate(sorted(sheet_members), start=1):
            raw = _zip_member(path, member_name)
            root = ET.fromstring(raw)
            lines.append(f"# Sheet {index}")
            row_values: list[str] = []
            for cell in root.iter():
                tag = cell.tag.split("}")[-1]
                if tag == "c":
                    cell_type = cell.attrib.get("t", "")
                    value_node = next((child for child in cell if child.tag.split("}")[-1] == "v"), None)
                    if value_node is None or value_node.text is None:
                        continue
                    value = value_node.text.strip()
                    if cell_type == "s":
                        try:
                            shared_value = shared_strings[int(value)]
                        except Exception:
                            shared_value = value
                        row_values.append(shared_value)
                    else:
                        row_values.append(value)
                elif tag == "row" and row_values:
                    lines.append(" | ".join(row_values))
                    row_values = []
            if row_values:
                lines.append(" | ".join(row_values))
            lines.append("")
        content = "\n".join(lines).strip()
        if content:
            return content
    except Exception:
        pass
    content = _mdls_text(path)
    if content.strip():
        return content
    raise RuntimeError("workbook extraction failed across zip and mdls fallbacks")


def _extract_eml(path: Path) -> str:
    message = BytesParser(policy=policy.default).parsebytes(_read_bytes(path))
    parts: list[str] = []
    headers = {
        "Subject": message.get("Subject", ""),
        "From": message.get("From", ""),
        "To": message.get("To", ""),
        "Cc": message.get("Cc", ""),
        "Date": message.get("Date", ""),
    }
    for key, value in headers.items():
        if value:
            parts.append(f"{key}: {value}")
    body = ""
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
        if not body:
            for part in message.walk():
                if part.get_content_disposition() == "attachment":
                    continue
                if part.get_content_type() == "text/html":
                    body = re.sub(r"(?is)<[^>]+>", " ", part.get_content())
                    break
    else:
        body = message.get_content()
    if body:
        parts.append("")
        parts.append(body)
    return "\n".join(parts)


def _read_bytes(path: Path) -> bytes:
    result = subprocess.run(
        ["/bin/cat", str(path)],
        capture_output=True,
        check=False,
        timeout=EXTRACTION_TIMEOUT_SECONDS,
    )
    return result.stdout


def _zip_list(path: Path) -> list[str]:
    result = subprocess.run(
        ["unzip", "-Z1", str(path)],
        capture_output=True,
        text=True,
        check=False,
        timeout=EXTRACTION_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "zip member listing failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _zip_member(path: Path, member_name: str) -> bytes:
    result = subprocess.run(
        ["unzip", "-p", str(path), member_name],
        capture_output=True,
        check=False,
        timeout=EXTRACTION_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="ignore").strip() or "zip member extraction failed")
    return result.stdout


def _extract_shared_strings(path: Path) -> list[str]:
    members = set(_zip_list(path))
    if "xl/sharedStrings.xml" not in members:
        return []
    raw = _zip_member(path, "xl/sharedStrings.xml")
    root = ET.fromstring(raw)
    strings: list[str] = []
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag == "t" and node.text:
            strings.append(node.text.strip())
    return strings


def _extract_by_suffix(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix in TEXT_LIKE_SUFFIXES:
        if suffix == ".csv":
            return _read_text(path), "text"
        return _read_text(path), "text"
    if suffix == ".docx":
        return _extract_docx(path), "docx"
    if suffix == ".doc":
        return _textutil_to_text(path), "textutil"
    if suffix == ".pptx":
        return _extract_pptx(path), "pptx"
    if suffix == ".pdf":
        return _extract_pdf(path), "pdftotext"
    if suffix in {".xlsx", ".xlsm"}:
        return _extract_workbook(path), "openpyxl"
    if suffix == ".eml":
        return _extract_eml(path), "eml"
    if suffix in {".msg", ".xls", ".xlsb", ".vsdx"}:
        text = _mdls_text(path)
        return text, "mdls"
    if suffix in MEDIA_SUFFIXES:
        return "", "media"
    return _mdls_text(path), "mdls"


def _extract_with_timeout(path: Path) -> tuple[str, str]:
    return _extract_by_suffix(path)


def _write_output(group_root: Path, relative_path: str, source_path: Path, content: str, extractor: str) -> Path:
    target_path = _target_path(group_root, relative_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Source: {source_path.name}",
        "",
        f"- original_path: {source_path}",
        f"- relative_path: {relative_path}",
        f"- extractor: {extractor}",
        f"- extracted_at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Content",
        "",
        content.strip(),
        "",
    ]
    target_path.write_text("\n".join(lines), encoding="utf-8")
    return target_path


def _walk_files(root: Path, include_all_files: bool) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if not path.is_file():
            continue
        if include_all_files:
            files.append(path)
        else:
            if path.suffix.lower() in TEXT_LIKE_SUFFIXES and path.stat().st_size <= 2_000_000:
                files.append(path)
    return sorted(files)


def _cached_doc(path: Path, relative_path: str, group_name: str, group_output_root: Path) -> ExtractedDoc | None:
    target_path = _target_path(group_output_root, relative_path)
    if not target_path.exists():
        return None
    content = target_path.read_text(encoding="utf-8", errors="ignore")
    return ExtractedDoc(
        source_path=str(path),
        relative_path=relative_path,
        group=group_name,
        extractor="cached",
        status="cached",
        output_path=str(target_path),
        char_count=len(content),
        notes=["Reused existing normalized output"],
    )


def _extract_group(
    source_root: Path,
    group_output_root: Path,
    group_name: str,
    include_all_files: bool,
    checkpoint_callback=None,
) -> tuple[list[ExtractedDoc], Counter]:
    docs: list[ExtractedDoc] = []
    counters: Counter = Counter()
    files = _walk_files(source_root, include_all_files)
    for index, path in enumerate(files, start=1):
        if index == 1 or index % 25 == 0:
            print(f"[{group_name}] {index}/{len(files)} {path.name}")
        relative_path = _safe_rel(path, source_root)
        cached_doc = _cached_doc(path, relative_path, group_name, group_output_root)
        if cached_doc is not None:
            docs.append(cached_doc)
            counters["cached_docs"] += 1
            counters["cached_chars"] += cached_doc.char_count
            counters[f"ext:{path.suffix.lower() or '<none>'}"] += 1
            if checkpoint_callback and (index == 1 or index % CHECKPOINT_EVERY == 0 or index == len(files)):
                checkpoint_callback(docs, counters, len(files))
            continue
        try:
            content, extractor = _extract_with_timeout(path)
            notes: list[str] = []
            status = "ok"
            output_path = None
            if content.strip():
                target = _write_output(group_output_root, relative_path, path, content, extractor)
                output_path = str(target)
                counters["extracted_docs"] += 1
                counters["extracted_chars"] += len(content)
            else:
                status = "skipped"
                notes.append("No extractable text found")
                counters["skipped_docs"] += 1
            counters[f"ext:{path.suffix.lower() or '<none>'}"] += 1
            docs.append(
                ExtractedDoc(
                    source_path=str(path),
                    relative_path=relative_path,
                    group=group_name,
                    extractor=extractor,
                    status=status,
                    output_path=output_path,
                    char_count=len(content),
                    notes=notes,
                )
            )
        except Exception as exc:
            counters["failed_docs"] += 1
            counters[f"ext:{path.suffix.lower() or '<none>'}"] += 1
            docs.append(
                ExtractedDoc(
                    source_path=str(path),
                    relative_path=relative_path,
                    group=group_name,
                    extractor="error",
                    status="error",
                    output_path=None,
                    char_count=0,
                    notes=[str(exc)],
                )
            )
        if checkpoint_callback and (index == 1 or index % CHECKPOINT_EVERY == 0 or index == len(files)):
            checkpoint_callback(docs, counters, len(files))
    return docs, counters


def _extract_single_file(
    source_path: Path,
    group_output_root: Path,
    group_name: str,
    checkpoint_callback=None,
) -> tuple[list[ExtractedDoc], Counter]:
    counters: Counter = Counter()
    cached_doc = _cached_doc(source_path, source_path.name, group_name, group_output_root)
    if cached_doc is not None:
        counters["cached_docs"] += 1
        counters["cached_chars"] += cached_doc.char_count
        counters[f"ext:{source_path.suffix.lower() or '<none>'}"] += 1
        docs = [cached_doc]
        if checkpoint_callback:
            checkpoint_callback(docs, counters, 1)
        return docs, counters
    try:
        content, extractor = _extract_with_timeout(source_path)
        notes: list[str] = []
        status = "ok"
        output_path = None
        if content.strip():
            target = _write_output(group_output_root, source_path.name, source_path, content, extractor)
            output_path = str(target)
            counters["extracted_docs"] += 1
            counters["extracted_chars"] += len(content)
        else:
            status = "skipped"
            notes.append("No extractable text found")
            counters["skipped_docs"] += 1
        counters[f"ext:{source_path.suffix.lower() or '<none>'}"] += 1
        return [
            ExtractedDoc(
                source_path=str(source_path),
                relative_path=source_path.name,
                group=group_name,
                extractor=extractor,
                status=status,
                output_path=output_path,
                char_count=len(content),
                notes=notes,
            )
        ], counters
    except Exception as exc:
        counters["failed_docs"] += 1
        counters[f"ext:{source_path.suffix.lower() or '<none>'}"] += 1
        return [
            ExtractedDoc(
                source_path=str(source_path),
                relative_path=source_path.name,
                group=group_name,
                extractor="error",
                status="error",
                output_path=None,
                char_count=0,
                notes=[str(exc)],
            )
        ], counters


def main() -> int:
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT_DIRS.values():
        path.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    group_summaries: dict[str, dict[str, object]] = {}

    all_docs: list[ExtractedDoc] = []

    def group_checkpoint(group_key: str, source_root: Path):
        def _checkpoint(group_docs: list[ExtractedDoc], counters: Counter, total_files: int) -> None:
            partial_groups = dict(group_summaries)
            partial_groups[group_key] = {
                "source_root": str(source_root),
                "source_files": total_files,
                "extracted_docs": counters["extracted_docs"],
                "cached_docs": counters["cached_docs"],
                "skipped_docs": counters["skipped_docs"],
                "failed_docs": counters["failed_docs"],
                "extracted_chars": counters["extracted_chars"] + counters["cached_chars"],
            }
            _write_checkpoint(
                all_docs + list(group_docs),
                partial_groups,
                run_status="running",
                active_group=group_key,
            )

        return _checkpoint

    for repo_name, repo_root in REPO_SOURCES.items():
        if not repo_root.exists():
            continue
        docs, counters = _extract_group(
            repo_root,
            OUTPUT_DIRS["repo_harvest"] / repo_name,
            "repo_harvest",
            include_all_files=False,
            checkpoint_callback=group_checkpoint(f"repo:{repo_name}", repo_root),
        )
        all_docs.extend(docs)
        group_summaries[f"repo:{repo_name}"] = {
            "source_root": str(repo_root),
            "source_files": len(docs),
            "extracted_docs": counters["extracted_docs"],
            "cached_docs": counters["cached_docs"],
            "skipped_docs": counters["skipped_docs"],
            "failed_docs": counters["failed_docs"],
            "extracted_chars": counters["extracted_chars"] + counters["cached_chars"],
        }
        _write_checkpoint(all_docs, group_summaries, run_status="running", active_group=f"repo:{repo_name}")

    for source_name, source_root in BEHAVIORAL_SOURCES.items():
        if not source_root.exists():
            continue
        if source_root.is_file():
            docs, counters = _extract_single_file(
                source_root,
                OUTPUT_DIRS["behavioral_science_seed"] / source_name,
                "behavioral_science_seed",
                checkpoint_callback=group_checkpoint(f"behavioral:{source_name}", source_root),
            )
        else:
            docs, counters = _extract_group(
                source_root,
                OUTPUT_DIRS["behavioral_science_seed"] / source_name,
                "behavioral_science_seed",
                include_all_files=False,
                checkpoint_callback=group_checkpoint(f"behavioral:{source_name}", source_root),
            )
        all_docs.extend(docs)
        group_summaries[f"behavioral:{source_name}"] = {
            "source_root": str(source_root),
            "source_files": len(docs),
            "extracted_docs": counters["extracted_docs"],
            "cached_docs": counters["cached_docs"],
            "skipped_docs": counters["skipped_docs"],
            "failed_docs": counters["failed_docs"],
            "extracted_chars": counters["extracted_chars"] + counters["cached_chars"],
        }
        _write_checkpoint(all_docs, group_summaries, run_status="running", active_group=f"behavioral:{source_name}")

    if ORACLE_SOURCE_ROOT.exists():
        docs, counters = _extract_group(
            ORACLE_SOURCE_ROOT,
            OUTPUT_DIRS["oracle_health_extracted"],
            "oracle_health_extracted",
            include_all_files=True,
            checkpoint_callback=group_checkpoint("oracle_health_extracted", ORACLE_SOURCE_ROOT),
        )
        all_docs.extend(docs)
        group_summaries["oracle_health_extracted"] = {
            "source_root": str(ORACLE_SOURCE_ROOT),
            "source_files": len(docs),
            "extracted_docs": counters["extracted_docs"],
            "cached_docs": counters["cached_docs"],
            "skipped_docs": counters["skipped_docs"],
            "failed_docs": counters["failed_docs"],
            "extracted_chars": counters["extracted_chars"] + counters["cached_chars"],
        }
        _write_checkpoint(all_docs, group_summaries, run_status="running", active_group="oracle_health_extracted")

    for doc in all_docs:
        entry = _doc_entry(doc)
        manifest.append(entry)
        if doc.status == "error":
            failures.append(entry)

    summary = _write_checkpoint(all_docs, group_summaries, run_status="completed")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
