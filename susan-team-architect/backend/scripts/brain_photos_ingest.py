#!/usr/bin/env python3
"""Ingest Apple Photos metadata into Jake's Brain.

Reads the Photos.sqlite database (READ ONLY) and creates episodic memories
from photo events — groups of photos taken within a 2-hour window.

Phase 3 "THE EYES" Wave 3 — Apple Photos metadata ingestion.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_photos_ingest.py [--dry-run] [--limit N] [--days N]
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment bootstrap (same as all other ingest scripts)
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
# Constants
# ---------------------------------------------------------------------------
PHOTOS_DB = Path.home() / "Pictures" / "Photos Library.photoslibrary" / "database" / "Photos.sqlite"

# Apple Core Data epoch: 2001-01-01 00:00:00 UTC
APPLE_EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)

# Photos taken within this window are grouped into one event
EVENT_GAP_HOURS = 2

# Minimum photos to constitute a meaningful event
MIN_PHOTOS_PER_EVENT = 1

# Minimum chunk length to bother ingesting
MIN_CHUNK_LEN = 50

# Default lookback period in days
DEFAULT_DAYS = 90


def content_hash(text: str) -> str:
    """SHA256 hash of text for deduplication."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def apple_ts_to_datetime(ts: float | None) -> datetime | None:
    """Convert Apple Core Data timestamp to Python datetime."""
    if ts is None or ts == 0:
        return None
    try:
        return APPLE_EPOCH + timedelta(seconds=ts)
    except (OverflowError, ValueError):
        return None


def reverse_geocode_approx(lat: float, lon: float) -> str:
    """Best-effort reverse geocode from coordinates.

    Uses a simple quadrant-based description when no geocoding API is
    available.  If the geopy library is installed we try that first.
    """
    if lat is None or lon is None:
        return ""
    try:
        # Attempt geopy if available (pip install geopy)
        from geopy.geocoders import Nominatim  # type: ignore
        geolocator = Nominatim(user_agent="jake-brain-photos", timeout=5)
        location = geolocator.reverse(f"{lat}, {lon}", exactly_one=True, language="en")
        if location and location.address:
            # Shorten to city/state level
            parts = [p.strip() for p in location.address.split(",")]
            if len(parts) >= 3:
                return ", ".join(parts[-3:])
            return location.address
    except Exception:
        pass

    # Fallback: just show coords
    return f"({lat:.4f}, {lon:.4f})"


def query_photos(db_path: Path, since: datetime, limit: int | None = None) -> list[dict]:
    """Query Photos.sqlite for photo/video metadata since a given date.

    Opens the database in read-only mode. Never modifies it.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Photos database not found: {db_path}")

    # Open in read-only mode via URI
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row

    since_apple_ts = (since - APPLE_EPOCH).total_seconds()

    query = """
        SELECT
            a.Z_PK,
            a.ZDATECREATED,
            a.ZLATITUDE,
            a.ZLONGITUDE,
            a.ZFILENAME,
            a.ZKIND,
            a.ZFAVORITE,
            a.ZTRASHEDSTATE,
            aa.ZTITLE,
            aa.ZORIGINALFILENAME
        FROM ZASSET a
        LEFT JOIN ZADDITIONALASSETATTRIBUTES aa
            ON a.Z_PK = aa.ZASSET
        WHERE a.ZTRASHEDSTATE = 0
          AND a.ZDATECREATED > ?
        ORDER BY a.ZDATECREATED DESC
    """
    params: list = [since_apple_ts]

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    rows = conn.execute(query, params).fetchall()

    # Fetch album membership
    album_map: dict[int, list[str]] = defaultdict(list)
    try:
        album_query = """
            SELECT za.Z_26ASSETS AS asset_pk, ga.ZTITLE AS album_name
            FROM Z_26ASSETS za
            JOIN ZGENERICALBUM ga ON za.Z_34ALBUMS = ga.Z_PK
            WHERE ga.ZTITLE IS NOT NULL
              AND ga.ZTRASHEDSTATE = 0
        """
        for row in conn.execute(album_query).fetchall():
            album_map[row["asset_pk"]].append(row["album_name"])
    except sqlite3.OperationalError:
        # Album join table name varies by Photos version; try alternate
        try:
            album_query = """
                SELECT za.Z_34ASSETS AS asset_pk, ga.ZTITLE AS album_name
                FROM Z_34ASSETS za
                JOIN ZGENERICALBUM ga ON za.Z_26ALBUMS = ga.Z_PK
                WHERE ga.ZTITLE IS NOT NULL
                  AND ga.ZTRASHEDSTATE = 0
            """
            for row in conn.execute(album_query).fetchall():
                album_map[row["asset_pk"]].append(row["album_name"])
        except sqlite3.OperationalError:
            pass  # Album data unavailable — continue without it

    # Fetch face/person data
    face_map: dict[int, list[str]] = defaultdict(list)
    try:
        face_query = """
            SELECT df.ZASSET AS asset_pk, p.ZFULLNAME AS person_name
            FROM ZDETECTEDFACE df
            JOIN ZPERSON p ON df.ZPERSON = p.Z_PK
            WHERE p.ZFULLNAME IS NOT NULL
              AND p.ZFULLNAME != ''
        """
        for row in conn.execute(face_query).fetchall():
            face_map[row["asset_pk"]].append(row["person_name"])
    except sqlite3.OperationalError:
        pass  # Face data unavailable — continue without it

    conn.close()

    photos = []
    for row in rows:
        dt = apple_ts_to_datetime(row["ZDATECREATED"])
        if not dt:
            continue

        pk = row["Z_PK"]
        lat = row["ZLATITUDE"] if row["ZLATITUDE"] and row["ZLATITUDE"] != -180.0 else None
        lon = row["ZLONGITUDE"] if row["ZLONGITUDE"] and row["ZLONGITUDE"] != -180.0 else None

        photos.append({
            "pk": pk,
            "date": dt,
            "latitude": lat,
            "longitude": lon,
            "filename": row["ZFILENAME"] or "",
            "kind": "video" if row["ZKIND"] == 1 else "photo",
            "favorite": bool(row["ZFAVORITE"]),
            "title": row["ZTITLE"] or "",
            "camera_make": "",
            "camera_model": "",
            "albums": album_map.get(pk, []),
            "people": face_map.get(pk, []),
        })

    return photos


def group_into_events(photos: list[dict]) -> list[dict]:
    """Group photos into events based on temporal proximity.

    Photos taken within EVENT_GAP_HOURS of each other belong to the same event.
    """
    if not photos:
        return []

    # Sort by date ascending
    sorted_photos = sorted(photos, key=lambda p: p["date"])

    events: list[dict] = []
    current_event: list[dict] = [sorted_photos[0]]

    for photo in sorted_photos[1:]:
        gap = (photo["date"] - current_event[-1]["date"]).total_seconds() / 3600
        if gap <= EVENT_GAP_HOURS:
            current_event.append(photo)
        else:
            events.append(_summarize_event(current_event))
            current_event = [photo]

    # Don't forget the last event
    if current_event:
        events.append(_summarize_event(current_event))

    return events


def _summarize_event(photos: list[dict]) -> dict:
    """Summarize a group of photos into an event record."""
    start = min(p["date"] for p in photos)
    end = max(p["date"] for p in photos)

    # Collect unique people, albums, locations
    all_people: set[str] = set()
    all_albums: set[str] = set()
    all_locations: list[tuple[float, float]] = []
    favorites = sum(1 for p in photos if p["favorite"])
    videos = sum(1 for p in photos if p["kind"] == "video")
    photo_count = len(photos) - videos

    for p in photos:
        all_people.update(p["people"])
        all_albums.update(p["albums"])
        if p["latitude"] and p["longitude"]:
            all_locations.append((p["latitude"], p["longitude"]))

    # Use the most common location (centroid of first cluster)
    location_str = ""
    avg_lat, avg_lon = None, None
    if all_locations:
        avg_lat = sum(loc[0] for loc in all_locations) / len(all_locations)
        avg_lon = sum(loc[1] for loc in all_locations) / len(all_locations)
        location_str = reverse_geocode_approx(avg_lat, avg_lon)

    return {
        "start": start,
        "end": end,
        "photo_count": photo_count,
        "video_count": videos,
        "total": len(photos),
        "favorites": favorites,
        "people": sorted(all_people),
        "albums": sorted(all_albums),
        "location": location_str,
        "latitude": avg_lat,
        "longitude": avg_lon,
        "cameras": list({p["camera_model"] for p in photos if p["camera_model"]}),
    }


def build_event_chunk(event: dict) -> dict | None:
    """Build an episodic memory chunk from a photo event."""
    date_str = event["start"].strftime("%B %d, %Y")
    time_str = event["start"].strftime("%I:%M %p")

    # Build human-readable description
    parts = [f"{date_str} at {time_str}"]

    # Media counts
    media_parts = []
    if event["photo_count"] > 0:
        media_parts.append(f"{event['photo_count']} photo{'s' if event['photo_count'] != 1 else ''}")
    if event["video_count"] > 0:
        media_parts.append(f"{event['video_count']} video{'s' if event['video_count'] != 1 else ''}")
    if media_parts:
        parts.append(f" — {' and '.join(media_parts)} taken")

    if event["location"]:
        parts.append(f" at {event['location']}")

    if event["albums"]:
        parts.append(f". Album{'s' if len(event['albums']) > 1 else ''}: {', '.join(event['albums'])}")

    if event["people"]:
        parts.append(f". People: {', '.join(event['people'])}")

    if event["favorites"] > 0:
        parts.append(f". {event['favorites']} favorited")

    if event["cameras"]:
        parts.append(f". Camera: {', '.join(event['cameras'])}")

    # Duration
    duration = event["end"] - event["start"]
    if duration.total_seconds() > 60:
        hours = duration.total_seconds() / 3600
        if hours >= 1:
            parts.append(f". Duration: {hours:.1f} hours")
        else:
            parts.append(f". Duration: {int(duration.total_seconds() / 60)} minutes")

    content = "Apple Photos event: " + "".join(parts)

    if len(content) < MIN_CHUNK_LEN:
        return None

    # Build metadata
    metadata = {
        "photo_count": event["photo_count"],
        "video_count": event["video_count"],
        "favorites": event["favorites"],
        "albums": event["albums"],
        "cameras": event["cameras"],
    }
    if event["latitude"] is not None:
        metadata["latitude"] = round(event["latitude"], 6)
        metadata["longitude"] = round(event["longitude"], 6)

    # Dedup key: date + total count
    dedup_key = f"{event['start'].strftime('%Y-%m-%d-%H')}:{event['total']}"

    return {
        "content": content,
        "source": f"apple_photos:event:{dedup_key}",
        "source_type": "apple_photos",
        "occurred_at": event["start"].isoformat(),
        "people": event["people"],
        "metadata": metadata,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Apple Photos metadata into Jake's Brain"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be ingested without doing it",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of photos queried from the database",
    )
    parser.add_argument(
        "--days", type=int, default=DEFAULT_DAYS,
        help=f"Look back N days (default: {DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--db", type=str, default=None,
        help="Override path to Photos.sqlite (default: auto-detect)",
    )
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else PHOTOS_DB
    since = datetime.now(timezone.utc) - timedelta(days=args.days)

    print("=" * 60)
    print("Jake Brain — Apple Photos Metadata Ingestion")
    print(f"Database: {db_path}")
    print(f"Lookback: {args.days} days (since {since.strftime('%Y-%m-%d')})")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # 1. Query Photos database
    # -----------------------------------------------------------------------
    if not db_path.exists():
        print(f"\nERROR: Photos database not found at {db_path}")
        print("Make sure Photos.app has a library at ~/Pictures/Photos Library.photoslibrary/")
        print("Or specify a custom path with --db /path/to/Photos.sqlite")
        sys.exit(1)

    try:
        photos = query_photos(db_path, since=since, limit=args.limit)
    except sqlite3.OperationalError as exc:
        print(f"\nERROR: Could not read Photos database: {exc}")
        print("This may require Full Disk Access for Terminal in System Settings > Privacy.")
        sys.exit(1)
    except Exception as exc:
        print(f"\nERROR: Failed to query Photos database: {exc}")
        sys.exit(1)

    if not photos:
        print("\nNo photos found in the specified time range.")
        return

    print(f"\nPhotos found: {len(photos)}")

    # Count stats
    video_count = sum(1 for p in photos if p["kind"] == "video")
    photo_count = len(photos) - video_count
    fav_count = sum(1 for p in photos if p["favorite"])
    with_location = sum(1 for p in photos if p["latitude"])
    with_people = sum(1 for p in photos if p["people"])
    all_people: set[str] = set()
    for p in photos:
        all_people.update(p["people"])

    print(f"  Photos: {photo_count}, Videos: {video_count}")
    print(f"  Favorites: {fav_count}")
    print(f"  With GPS: {with_location}")
    print(f"  With faces: {with_people}")
    if all_people:
        print(f"  People detected: {sorted(all_people)}")

    # -----------------------------------------------------------------------
    # 2. Group into events
    # -----------------------------------------------------------------------
    events = group_into_events(photos)
    events = [e for e in events if e["total"] >= MIN_PHOTOS_PER_EVENT]

    print(f"\nEvents grouped: {len(events)} (gap threshold: {EVENT_GAP_HOURS}h)")

    # -----------------------------------------------------------------------
    # 3. Build chunks
    # -----------------------------------------------------------------------
    all_chunks: list[dict] = []
    seen_hashes: set[str] = set()

    for event in events:
        chunk = build_event_chunk(event)
        if not chunk:
            continue

        h = content_hash(chunk["content"])
        if h not in seen_hashes:
            seen_hashes.add(h)
            all_chunks.append(chunk)

    print(f"Chunks built: {len(all_chunks)} (after dedup)")

    if not all_chunks:
        print("No chunks to ingest.")
        return

    # -----------------------------------------------------------------------
    # 4. Dry-run preview or ingest
    # -----------------------------------------------------------------------
    if args.dry_run:
        print(f"\n[DRY RUN] Would ingest {len(all_chunks)} chunks. Previewing first 10:\n")
        for i, chunk in enumerate(all_chunks[:10], 1):
            preview = chunk["content"][:120].replace("\n", " ")
            print(f"  {i}. [{chunk['source_type']:15s}] [{len(chunk['content']):5d} chars] {preview}...")
        if len(all_chunks) > 10:
            print(f"  ... and {len(all_chunks) - 10} more")
        return

    # Ingest
    from jake_brain.pipeline import BrainPipeline

    print(f"\nIngesting {len(all_chunks)} event chunks into Jake's Brain...")
    pipeline = BrainPipeline()

    results = {"success": 0, "failed": 0, "people": set(), "topics": set()}

    for i, chunk in enumerate(all_chunks, 1):
        try:
            result = pipeline.ingest_conversation(
                text=chunk["content"],
                session_id=f"photos-ingest-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                source=chunk["source"],
                source_type=chunk["source_type"],
                occurred_at=chunk.get("occurred_at"),
            )
            extraction = result.get("extraction", {})
            results["success"] += 1
            results["people"].update(extraction.get("people", []))
            results["topics"].update(extraction.get("topics", []))

            if i % 20 == 0 or i == len(all_chunks):
                print(f"  [{i}/{len(all_chunks)}] Ingested — "
                      f"people so far: {len(results['people'])}, "
                      f"topics so far: {len(results['topics'])}")
        except Exception as exc:
            results["failed"] += 1
            print(f"  [{i}/{len(all_chunks)}] FAILED — {exc}")

    print(f"\n{'=' * 60}")
    print("Apple Photos Ingestion Complete")
    print(f"  Photos scanned:     {len(photos)}")
    print(f"  Events grouped:     {len(events)}")
    print(f"  Chunks ingested:    {results['success']}")
    print(f"  Chunks failed:      {results['failed']}")
    print(f"  People discovered:  {sorted(results['people'])}")
    print(f"  Topics discovered:  {sorted(results['topics'])}")
    print(f"{'=' * 60}")

    # Show updated brain stats
    try:
        stats = pipeline.stats()
        print(f"\nBrain Stats After Ingestion:")
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
