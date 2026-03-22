#!/usr/bin/env python3
"""Ingest Google Photos metadata into Jake's Brain.

Fetches photo/video metadata from Google Photos via the Library API, groups them
into daily events, and stores episodic memories via the Brain pipeline.

Part of Phase 3 "THE EYES" Wave 3 — life data ingestion.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_gphotos_ingest.py [--dry-run] [--limit N] [--days N]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment bootstrap (same pattern as all other brain ingest scripts)
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ---------------------------------------------------------------------------
# Google Photos OAuth config
# ---------------------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/photoslibrary.readonly"]
TOKEN_FILE = Path.home() / ".hermes" / "google_photos_token.pickle"
CREDS_FILE = Path.home() / ".hermes" / "google_credentials.json"
API_BASE = "https://photoslibrary.googleapis.com/v1"

# Defaults
DEFAULT_DAYS = 90
PAGE_SIZE = 100


def content_hash(text: str) -> str:
    """SHA256 hash of text for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# OAuth2 Authentication
# ---------------------------------------------------------------------------
def get_credentials():
    """Obtain Google Photos API credentials with automatic token refresh.

    Returns google.oauth2.credentials.Credentials or None if setup is missing.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        print("ERROR: Required packages not installed. Run:")
        print("  pip install google-auth google-auth-oauthlib google-auth-httplib2")
        return None

    if not CREDS_FILE.exists():
        print(f"ERROR: Google credentials file not found at {CREDS_FILE}")
        print()
        print("Setup instructions:")
        print("  1. Go to https://console.cloud.google.com/apis/credentials")
        print("  2. Create an OAuth 2.0 Client ID (Desktop application)")
        print("  3. Download the JSON and save it as:")
        print(f"     {CREDS_FILE}")
        print("  4. Enable the Google Photos Library API:")
        print("     https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com")
        print("  5. Run this script again — it will open a browser for authorization.")
        return None

    creds = None

    if TOKEN_FILE.exists():
        try:
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as exc:
                print(f"Token refresh failed: {exc}")
                print("Re-authorizing...")
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print(f"Token saved to {TOKEN_FILE}")

    return creds


# ---------------------------------------------------------------------------
# Google Photos API helpers
# ---------------------------------------------------------------------------
def photos_api_get(creds, endpoint: str, params: dict | None = None) -> dict | None:
    """GET request to the Google Photos Library API."""
    import requests

    headers = {"Authorization": f"Bearer {creds.token}"}
    url = f"{API_BASE}/{endpoint}"
    try:
        resp = requests.get(url, headers=headers, params=params or {}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        print(f"  API GET error ({endpoint}): {exc}")
        return None


def photos_api_post(creds, endpoint: str, body: dict) -> dict | None:
    """POST request to the Google Photos Library API."""
    import requests

    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE}/{endpoint}"
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        print(f"  API POST error ({endpoint}): {exc}")
        return None


def fetch_albums(creds) -> dict[str, str]:
    """Fetch all albums and return a mapping of album ID -> album title."""
    albums: dict[str, str] = {}
    page_token = None

    while True:
        params = {"pageSize": 50}
        if page_token:
            params["pageToken"] = page_token

        data = photos_api_get(creds, "albums", params)
        if not data:
            break

        for album in data.get("albums", []):
            album_id = album.get("id", "")
            title = album.get("title", "Untitled")
            if album_id:
                albums[album_id] = title

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return albums


def fetch_album_items(creds, album_id: str) -> set[str]:
    """Fetch all media item IDs belonging to an album."""
    item_ids: set[str] = set()
    page_token = None

    while True:
        body: dict = {
            "albumId": album_id,
            "pageSize": PAGE_SIZE,
        }
        if page_token:
            body["pageToken"] = page_token

        data = photos_api_post(creds, "mediaItems:search", body)
        if not data:
            break

        for item in data.get("mediaItems", []):
            item_id = item.get("id", "")
            if item_id:
                item_ids.add(item_id)

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return item_ids


def fetch_media_items(
    creds,
    since: datetime,
    limit: int | None = None,
) -> list[dict]:
    """Fetch media items created after `since`, paginating through all results.

    Returns list of raw mediaItem dicts.
    """
    items: list[dict] = []
    page_token = None

    # Use date filter via search endpoint
    start_date = since
    end_date = datetime.now(timezone.utc)

    body: dict = {
        "pageSize": PAGE_SIZE,
        "filters": {
            "dateFilter": {
                "ranges": [
                    {
                        "startDate": {
                            "year": start_date.year,
                            "month": start_date.month,
                            "day": start_date.day,
                        },
                        "endDate": {
                            "year": end_date.year,
                            "month": end_date.month,
                            "day": end_date.day,
                        },
                    }
                ]
            }
        },
    }

    while True:
        if page_token:
            body["pageToken"] = page_token

        data = photos_api_post(creds, "mediaItems:search", body)
        if not data:
            break

        batch = data.get("mediaItems", [])
        items.extend(batch)

        if limit and len(items) >= limit:
            items = items[:limit]
            break

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return items


# ---------------------------------------------------------------------------
# Grouping and chunk building
# ---------------------------------------------------------------------------
def parse_media_item(item: dict) -> dict:
    """Parse a raw mediaItem into a clean record."""
    meta = item.get("mediaMetadata", {})
    creation_time = meta.get("creationTime", "")
    photo_meta = meta.get("photo", {})
    video_meta = meta.get("video", {})

    # Determine if photo or video
    mime = item.get("mimeType", "")
    is_video = mime.startswith("video/") or bool(video_meta)

    camera_make = photo_meta.get("cameraMake", video_meta.get("cameraMake", ""))
    camera_model = photo_meta.get("cameraModel", video_meta.get("cameraModel", ""))

    return {
        "id": item.get("id", ""),
        "filename": item.get("filename", ""),
        "mime_type": mime,
        "is_video": is_video,
        "creation_time": creation_time,
        "width": meta.get("width", ""),
        "height": meta.get("height", ""),
        "camera_make": camera_make,
        "camera_model": camera_model,
        "focal_length": photo_meta.get("focalLength"),
        "aperture": photo_meta.get("apertureFNumber"),
    }


def group_by_date(items: list[dict]) -> dict[str, list[dict]]:
    """Group parsed media items by date (YYYY-MM-DD)."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        ct = item.get("creation_time", "")
        if ct:
            date_key = ct[:10]  # YYYY-MM-DD
        else:
            date_key = "unknown"
        groups[date_key].append(item)
    return dict(sorted(groups.items(), reverse=True))


def build_event_chunk(
    date_key: str,
    items: list[dict],
    album_membership: dict[str, list[str]],
) -> dict:
    """Build an episodic memory chunk from a day's photos/videos.

    Creates a natural-language summary of the day's media.
    """
    photo_count = sum(1 for i in items if not i["is_video"])
    video_count = sum(1 for i in items if i["is_video"])

    # Collect cameras
    cameras: set[str] = set()
    for item in items:
        if item["camera_make"] and item["camera_model"]:
            cameras.add(f"{item['camera_make']} {item['camera_model']}")
        elif item["camera_model"]:
            cameras.add(item["camera_model"])
        elif item["camera_make"]:
            cameras.add(item["camera_make"])

    # Collect albums this day's items belong to
    day_albums: set[str] = set()
    for item in items:
        item_id = item["id"]
        for album_name in album_membership.get(item_id, []):
            day_albums.add(album_name)

    # Build the content string
    parts: list[str] = []

    # Date header
    try:
        date_obj = datetime.strptime(date_key, "%Y-%m-%d")
        date_display = date_obj.strftime("%B %d, %Y")
    except ValueError:
        date_display = date_key

    # Summary line
    media_parts: list[str] = []
    if photo_count:
        media_parts.append(f"{photo_count} photo{'s' if photo_count != 1 else ''}")
    if video_count:
        media_parts.append(f"{video_count} video{'s' if video_count != 1 else ''}")
    media_str = " and ".join(media_parts) if media_parts else "media"

    parts.append(f"{date_display} — {media_str} on Google Photos.")

    if day_albums:
        parts.append(f"Albums: {', '.join(sorted(day_albums))}.")

    if cameras:
        parts.append(f"Camera{'s' if len(cameras) > 1 else ''}: {', '.join(sorted(cameras))}.")

    # File types summary
    mime_counts: dict[str, int] = defaultdict(int)
    for item in items:
        ext = Path(item["filename"]).suffix.lower() if item["filename"] else ""
        if ext:
            mime_counts[ext] += 1
    if mime_counts:
        ext_parts = [f"{count}x {ext}" for ext, count in sorted(mime_counts.items(), key=lambda x: -x[1])]
        parts.append(f"Formats: {', '.join(ext_parts)}.")

    content = f"Google Photos ({date_key}): " + " ".join(parts)

    # Dedup hash: date + counts (so re-runs on the same day with same count skip)
    dedup_key = f"{date_key}:{photo_count}:{video_count}:{len(day_albums)}"

    # Metadata for the episodic record
    metadata = {
        "photo_count": photo_count,
        "video_count": video_count,
        "cameras": sorted(cameras),
        "albums": sorted(day_albums),
        "total_items": len(items),
    }

    return {
        "content": content,
        "source": f"google_photos:{date_key}",
        "source_type": "google_photos",
        "occurred_at": f"{date_key}T12:00:00Z",
        "dedup_hash": content_hash(dedup_key),
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Ingest Google Photos metadata into Jake's Brain"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be ingested without doing it",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of media items to fetch from API",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"How many days back to fetch (default: {DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--skip-albums",
        action="store_true",
        help="Skip fetching album membership (faster but less context)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Jake Brain — Google Photos Metadata Ingestion")
    print(f"Lookback: {args.days} days | Limit: {args.limit or 'none'}")
    print("=" * 60)

    # 1. Authenticate
    print("\nAuthenticating with Google Photos API...")
    creds = get_credentials()
    if not creds:
        sys.exit(1)
    print("  Authenticated successfully.")

    # 2. Fetch albums (for membership context)
    album_membership: dict[str, list[str]] = defaultdict(list)  # item_id -> [album_names]
    albums: dict[str, str] = {}

    if not args.skip_albums:
        print("\nFetching albums...")
        albums = fetch_albums(creds)
        print(f"  Found {len(albums)} album(s).")

        if albums:
            for album_id, album_title in albums.items():
                print(f"    - {album_title}")
                item_ids = fetch_album_items(creds, album_id)
                for item_id in item_ids:
                    album_membership[item_id].append(album_title)
            print(f"  Mapped {len(album_membership)} items to albums.")
    else:
        print("\nSkipping album fetch (--skip-albums).")

    # 3. Fetch media items
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    print(f"\nFetching media items since {since.strftime('%Y-%m-%d')}...")

    raw_items = fetch_media_items(creds, since=since, limit=args.limit)
    print(f"  Fetched {len(raw_items)} media item(s).")

    if not raw_items:
        print("\nNo media items found in the specified date range.")
        return

    # 4. Parse and group
    parsed = [parse_media_item(item) for item in raw_items]
    daily_groups = group_by_date(parsed)
    print(f"  Grouped into {len(daily_groups)} daily event(s).")

    total_photos = sum(1 for p in parsed if not p["is_video"])
    total_videos = sum(1 for p in parsed if p["is_video"])
    print(f"  Photos: {total_photos} | Videos: {total_videos}")

    # 5. Build chunks
    all_chunks: list[dict] = []
    seen_hashes: set[str] = set()

    for date_key, items in daily_groups.items():
        chunk = build_event_chunk(date_key, items, album_membership)
        h = chunk["dedup_hash"]
        if h not in seen_hashes:
            seen_hashes.add(h)
            all_chunks.append(chunk)

    print(f"\n{'=' * 60}")
    print(f"Chunks prepared: {len(all_chunks)}")
    print(f"  Media items covered: {len(parsed)}")
    print(f"  Daily events: {len(daily_groups)}")
    print(f"  Albums referenced: {len(albums)}")

    if not all_chunks:
        print("No chunks to ingest.")
        return

    # 6. Dry run or ingest
    if args.dry_run:
        print(f"\n[DRY RUN] Would ingest {len(all_chunks)} chunks. Previewing:\n")
        for i, chunk in enumerate(all_chunks, 1):
            preview = chunk["content"][:120].replace("\n", " ")
            meta = chunk.get("metadata", {})
            albums_str = ", ".join(meta.get("albums", [])) or "none"
            print(
                f"  {i}. [{chunk['source']:30s}] "
                f"photos={meta.get('photo_count', 0)} "
                f"videos={meta.get('video_count', 0)} "
                f"albums=[{albums_str}]"
            )
            print(f"     {preview}...")
        return

    # Import pipeline only when actually ingesting
    from jake_brain.pipeline import BrainPipeline

    print(f"\nIngesting {len(all_chunks)} chunks into Jake's Brain...")
    pipeline = BrainPipeline()

    results = {"success": 0, "failed": 0, "people": set(), "topics": set()}

    for i, chunk in enumerate(all_chunks, 1):
        try:
            result = pipeline.ingest_conversation(
                text=chunk["content"],
                session_id=f"gphotos-ingest-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                source=chunk["source"],
                source_type=chunk["source_type"],
                occurred_at=chunk.get("occurred_at"),
            )
            extraction = result.get("extraction", {})
            results["success"] += 1
            results["people"].update(extraction.get("people", []))
            results["topics"].update(extraction.get("topics", []))

            if i % 10 == 0 or i == len(all_chunks):
                print(
                    f"  [{i}/{len(all_chunks)}] Ingested — "
                    f"people so far: {len(results['people'])}, "
                    f"topics so far: {len(results['topics'])}"
                )
        except Exception as exc:
            results["failed"] += 1
            print(f"  [{i}/{len(all_chunks)}] FAILED — {exc}")

    print(f"\n{'=' * 60}")
    print("Google Photos Ingestion Complete")
    print(f"  Days scanned:       {args.days}")
    print(f"  Media items found:  {len(parsed)}")
    print(f"    Photos:           {total_photos}")
    print(f"    Videos:           {total_videos}")
    print(f"  Daily events:       {len(daily_groups)}")
    print(f"  Albums referenced:  {len(albums)}")
    print(f"  Chunks ingested:    {results['success']}")
    print(f"  Chunks failed:      {results['failed']}")
    print(f"  People discovered:  {sorted(results['people'])}")
    print(f"  Topics discovered:  {sorted(results['topics'])}")
    print(f"{'=' * 60}")

    # Show updated brain stats
    try:
        stats = pipeline.stats()
        print("\nBrain Stats After Ingestion:")
        for key, val in stats.items():
            if isinstance(val, dict):
                for k2, v2 in val.items():
                    print(f"  {k2}: {v2}")
            else:
                print(f"  {key}: {val}")
    except Exception as exc:
        print(f"\nCouldn't get brain stats: {exc}")


if __name__ == "__main__":
    main()
