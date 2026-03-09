"""Capture TransformFit and competitor screenshots, upload them to Supabase Storage, and index metadata."""
from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen
import hashlib
import json
import mimetypes
import sys

from firecrawl import FirecrawlApp
from supabase import create_client
import yaml

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.retriever import Retriever
from susan_core.config import config
from susan_core.schemas import KnowledgeChunk


COMPANY_ID = "transformfit"
BUCKET_NAME = "transformfit-assets"
TARGETS_PATH = (
    BACKEND_ROOT
    / "data"
    / "domains"
    / "transformfit_training_intelligence"
    / "studios"
    / "firecrawl_capture_targets.yaml"
)
ARTIFACT_DIR = BACKEND_ROOT / "artifacts" / "transformfit_visual_assets"


def _safe_slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in text).strip("-")


def ensure_bucket(supabase) -> None:
    buckets = supabase.storage.list_buckets()
    names = {b.name if hasattr(b, "name") else b.get("name") for b in buckets}
    if BUCKET_NAME not in names:
        supabase.storage.create_bucket(
            BUCKET_NAME,
            name=BUCKET_NAME,
            options={"public": True, "file_size_limit": 10485760},
        )


def download_bytes(url: str) -> bytes:
    with urlopen(url) as response:
        return response.read()


def upload_bytes(supabase, path: str, payload: bytes, content_type: str) -> str:
    bucket = supabase.storage.from_(BUCKET_NAME)
    if bucket.exists(path):
        bucket.remove([path])
    bucket.upload(path, payload, {"content-type": content_type})
    public = bucket.get_public_url(path)
    return public if isinstance(public, str) else public.get("publicUrl") or public.get("public_url")


def build_asset_chunk(*, title: str, target_url: str, public_url: str, reason: str, page_title: str, markdown: str, storage_path: str) -> KnowledgeChunk:
    excerpt = " ".join(markdown.split())[:500]
    content = (
        f"Screenshot asset: {title}\n"
        f"Target URL: {target_url}\n"
        f"Page title: {page_title or 'unknown'}\n"
        f"Capture reason: {reason}\n"
        f"Storage URL: {public_url}\n"
        f"Screenshot summary excerpt: {excerpt}"
    )
    return KnowledgeChunk(
        content=content,
        company_id=COMPANY_ID,
        access_level="company",
        data_type="visual_asset",
        source="transformfit_screenshot",
        source_url=target_url,
        metadata={
            "asset_type": "screenshot",
            "title": title,
            "storage_bucket": BUCKET_NAME,
            "storage_path": storage_path,
            "public_url": public_url,
            "capture_reason": reason,
            "page_title": page_title,
        },
    )


def main() -> int:
    targets = yaml.safe_load(TARGETS_PATH.read_text(encoding="utf-8"))["targets"]
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    firecrawl = FirecrawlApp(api_key=config.firecrawl_api_key)
    supabase = create_client(config.supabase_url, config.supabase_key)
    retriever = Retriever()
    ensure_bucket(supabase)

    chunks: list[KnowledgeChunk] = []
    manifest: list[dict] = []
    errors: list[dict] = []

    for target in targets:
        try:
            result = firecrawl.scrape(target["url"], formats=["markdown", "screenshot"], max_age=0)
            screenshot_url = getattr(result, "screenshot", None)
            markdown = getattr(result, "markdown", "") or ""
            page_title = ""
            if getattr(result, "metadata", None):
                page_title = getattr(result.metadata, "title", "") or ""
            if not screenshot_url:
                errors.append({"target": target["name"], "url": target["url"], "error": "missing_screenshot"})
                continue

            raw = download_bytes(screenshot_url)
            digest = hashlib.sha256(target["url"].encode("utf-8")).hexdigest()[:12]
            filename = f"{_safe_slug(target['name'])}-{digest}.png"
            local_path = ARTIFACT_DIR / filename
            local_path.write_bytes(raw)
            storage_path = f"{COMPANY_ID}/{filename}"
            content_type = mimetypes.guess_type(filename)[0] or "image/png"
            public_url = upload_bytes(supabase, storage_path, raw, content_type)

            chunks.append(
                build_asset_chunk(
                    title=target["name"],
                    target_url=target["url"],
                    public_url=public_url,
                    reason=target["reason"],
                    page_title=page_title,
                    markdown=markdown,
                    storage_path=storage_path,
                )
            )
            manifest.append(
                {
                    "title": target["name"],
                    "target_url": target["url"],
                    "storage_path": storage_path,
                    "public_url": public_url,
                    "reason": target["reason"],
                    "page_title": page_title,
                    "local_path": str(local_path),
                }
            )
        except Exception as exc:
            errors.append({"target": target["name"], "url": target["url"], "error": str(exc)})

    stored = retriever.store_chunks(chunks)
    (ARTIFACT_DIR / "manifest.json").write_text(json.dumps({"assets": manifest, "errors": errors}, indent=2), encoding="utf-8")
    print({"captured": len(manifest), "stored": stored, "errors": errors, "bucket": BUCKET_NAME, "artifact_dir": str(ARTIFACT_DIR)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
