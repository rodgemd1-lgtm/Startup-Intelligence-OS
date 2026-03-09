"""Intelligence ingestion subsystem for the Decision & Capability OS.

Fetches, normalizes, deduplicates, and persists evidence from external
sources.  Uses only stdlib + pydantic + PyYAML — no heavy HTTP clients.

Source configuration lives in ``data/ingestion-sources.yaml``.
"""
from __future__ import annotations

import datetime
import hashlib
import os
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

import yaml

from .models import Evidence, _now
from .store import Store
from .telemetry import start_run


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_DATA_DIR = Path(__file__).resolve().parent / "data"
_SOURCES_PATH = _DATA_DIR / "ingestion-sources.yaml"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_CONTENT_LENGTH = 5_000
FETCH_TIMEOUT_SECONDS = 15
USER_AGENT = "DecisionOS-Ingestion/0.1"

CONFIDENCE_BY_TYPE: dict[str, float] = {
    "web": 0.8,
    "doc": 0.9,
    "api": 0.85,
    "manual": 0.95,
    "unknown": 0.5,
}


# ---------------------------------------------------------------------------
# Helpers — fetch & normalize
# ---------------------------------------------------------------------------

_STRIP_TAGS_RE = re.compile(r"<[^>]+>")
_COLLAPSE_WS_RE = re.compile(r"\s{2,}")


def _strip_html(raw: str) -> str:
    """Remove HTML tags and collapse excessive whitespace."""
    text = _STRIP_TAGS_RE.sub(" ", raw)
    text = _COLLAPSE_WS_RE.sub(" ", text)
    return text.strip()


def _fetch_url(url: str) -> str:
    """Fetch raw content from *url* using stdlib only.

    Returns the decoded body text, or an empty string on failure.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SECONDS) as resp:
            raw_bytes = resp.read()
            # Best-effort encoding detection
            charset = resp.headers.get_content_charset() or "utf-8"
            try:
                return raw_bytes.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                return raw_bytes.decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return ""


def _normalize(raw_content: str) -> str:
    """Strip HTML, collapse whitespace, and truncate."""
    text = _strip_html(raw_content)
    return text[:MAX_CONTENT_LENGTH]


def _content_hash(content: str) -> str:
    """SHA-256 hex digest of normalized content for dedup."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Helpers — scoring
# ---------------------------------------------------------------------------

def _recency_score(fetched_at: str | None = None) -> float:
    """Score from 1.0 (today) decaying by 0.1 per day, min 0.1."""
    if not fetched_at:
        return 1.0
    try:
        fetched = datetime.datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return 0.5
    now = datetime.datetime.now(datetime.timezone.utc)
    days_old = max(0, (now - fetched).days)
    return max(0.1, round(1.0 - days_old * 0.1, 2))


def _source_type_from_url(url: str) -> str:
    """Infer source type from URL for confidence assignment."""
    lower = url.lower()
    if any(ext in lower for ext in (".pdf", ".doc", ".docx", ".md", ".txt")):
        return "doc"
    if "api" in lower or "/v1/" in lower or "/v2/" in lower:
        return "api"
    return "web"


# ---------------------------------------------------------------------------
# IntelligenceIngestion
# ---------------------------------------------------------------------------

class IntelligenceIngestion:
    """Fetch, normalize, deduplicate, and persist evidence from URLs."""

    def __init__(self, store: Store) -> None:
        self._store = store

    # -- helpers --

    def _existing_hashes(self) -> set[str]:
        """Collect dedup hashes from already-persisted evidence."""
        hashes: set[str] = set()
        for ev in self._store.evidence.list_all():
            if ev.dedup_hash:
                hashes.add(ev.dedup_hash)
        return hashes

    # -- public API --

    def ingest_url(
        self,
        url: str,
        domain: str = "",
        topic_tags: list[str] | None = None,
    ) -> Evidence | None:
        """Fetch URL content, normalize, deduplicate, and persist.

        Returns the ``Evidence`` object on success, or ``None`` if the
        content is a duplicate or the fetch failed.
        """
        topic_tags = topic_tags or []

        raw = _fetch_url(url)
        if not raw:
            return None

        normalized = _normalize(raw)
        if not normalized:
            return None

        dedup = _content_hash(normalized)

        # Deduplication
        existing = self._existing_hashes()
        if dedup in existing:
            return None

        source_type = _source_type_from_url(url)
        now_ts = _now()

        evidence = Evidence(
            source_url=url,
            source_type=source_type,
            title=self._extract_title(normalized, url),
            content=normalized,
            topic_tags=topic_tags,
            domain=domain,
            confidence=CONFIDENCE_BY_TYPE.get(source_type, 0.5),
            recency_score=_recency_score(now_ts),
            fetched_at=now_ts,
            normalized=True,
            dedup_hash=dedup,
        )

        self._store.evidence.save(evidence)
        return evidence

    def ingest_batch(self, sources: list[dict]) -> list[Evidence]:
        """Ingest multiple sources.

        Each source dict should contain:
            - url (str, required)
            - domain (str, optional)
            - topic_tags (list[str], optional)

        Returns the list of successfully persisted Evidence objects
        (skips duplicates and failed fetches).
        """
        results: list[Evidence] = []
        for src in sources:
            url = src.get("url", "")
            if not url:
                continue
            ev = self.ingest_url(
                url=url,
                domain=src.get("domain", ""),
                topic_tags=src.get("topic_tags", []),
            )
            if ev is not None:
                results.append(ev)
        return results

    def get_sources_config(self) -> list[dict]:
        """Load configured sources from ``data/ingestion-sources.yaml``.

        Returns an empty list if the config file does not exist.
        """
        if not _SOURCES_PATH.exists():
            return []
        try:
            data = yaml.safe_load(_SOURCES_PATH.read_text()) or {}
        except Exception:
            return []
        return data.get("sources", [])

    def run_scheduled(self) -> list[Evidence]:
        """Run ingestion from all configured sources.

        Creates a telemetry run, iterates over configured sources,
        and returns all newly ingested evidence.
        """
        tracer = start_run(
            self._store,
            trigger="scheduled_ingestion",
            mode="ingestion",
        )

        sources = self.get_sources_config()
        tracer.log("sources_loaded", data={
            "source_count": len(sources),
            "urls": [s.get("url", "") for s in sources],
        }, confidence=0.9)

        results: list[Evidence] = []
        skipped = 0
        failed = 0

        for src in sources:
            url = src.get("url", "")
            if not url:
                skipped += 1
                continue
            ev = self.ingest_url(
                url=url,
                domain=src.get("domain", ""),
                topic_tags=src.get("topic_tags", []),
            )
            if ev is not None:
                results.append(ev)
            else:
                # Could be dup or fetch failure — count as skipped
                skipped += 1

        tracer.log("ingestion_completed", data={
            "ingested": len(results),
            "skipped": skipped,
            "evidence_ids": [e.id for e in results],
        }, confidence=0.85)

        tracer.complete()
        return results

    # -- internal helpers --

    @staticmethod
    def _extract_title(content: str, url: str) -> str:
        """Best-effort title extraction from content or URL."""
        # Try first line as title (common for RSS / plaintext)
        first_line = content.split("\n")[0].strip()
        if 5 < len(first_line) < 200:
            return first_line

        # Fall back to URL-based title
        path = url.rstrip("/").split("/")[-1]
        clean = path.replace("-", " ").replace("_", " ").replace(".html", "")
        if clean:
            return clean[:120]

        return "Untitled source"
