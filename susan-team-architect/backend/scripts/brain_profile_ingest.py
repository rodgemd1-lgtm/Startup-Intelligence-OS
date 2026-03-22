#!/usr/bin/env python3
"""Ingest Mike Rodgers' comprehensive profile into Jake's Brain as semantic memories.

Each profile chunk is ingested as a semantic fact via BrainPipeline.ingest_conversation()
with source="profile_interview" and source_type="ingestion". SHA256 dedup prevents
duplicate ingestion on re-runs.

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/brain_profile_ingest.py [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jake_brain.pipeline import BrainPipeline

# Each chunk is a semantic fact about Mike Rodgers, grouped into 200-500 char blocks.
PROFILE_CHUNKS = [
    # --- Identity ---
    (
        "Mike Rodgers (Michael Rodgers) lives in Denver, Colorado. He grew up in Oskaloosa, Iowa. "
        "His birthday is January 30 — he posted a birthday celebration from Milan, Italy in January 2026. "
        "He is over 30 years old."
    ),
    (
        "Mike Rodgers' spouse is James Loehr (@loehrjames on Instagram). "
        "Mike has two sons: Jacob (15, plays offensive line and defensive line football, is a recruiting target) "
        "and Alex (12, the Alex Recruiting app is named after him). Mike's ex-wife is Jen."
    ),
    (
        "Mike's social media: Instagram @rodgemd1 with 35K followers, Spotify as 'Mr.Rodgers', "
        "LinkedIn at linkedin.com/in/mike-rodgers-14416414/, GitHub as rodgemd1-lgtm."
    ),

    # --- Career Timeline ---
    (
        "After high school Mike served in the United States Army Iowa National Guard, "
        "where he earned the Primary Leadership Development Course with Distinction."
    ),
    (
        "Mike attended Iowa State University and earned a Bachelor's in Industrial Engineering, "
        "graduating with Distinction. He also did graduate studies at Brunel University London."
    ),
    (
        "Career: Aurora Health Care (2013-2018) — Operations Improvement Manager, then Business Innovation Manager, "
        "then Director of Strategic Innovation. Advocate Aurora Health (2018-2020) — VP of Commercial Innovation, "
        "led InvestMKE $5M healthtech venture fund."
    ),
    (
        "Mike was Executive Board Member and then Chairman of MKE Tech Hub Coalition (2017-2020). "
        "He worked at EmOpti (2020-2021) as VP of Business Development (telemedicine startup). "
        "Then Cerner Corporation (~2020-2021) as Enterprise Strategy Executive."
    ),
    (
        "Mike has been at Oracle since 2021 as Senior Director of Marketing and Competitive Intelligence. "
        "He presented at JD Edwards INFOCUS 2025 and Blueprint 4D 2024. "
        "He has worked across 7 different industries throughout his career. "
        "He self-describes his title as 'Enterprise Strategy' because it covers many areas."
    ),

    # --- Awards ---
    (
        "Mike's awards: Milwaukee 40 Under 40 Nominee (2018), "
        "Emergency Care Innovation of the Year Award from George Washington University School of Medicine (2017), "
        "Primary Leadership Development Course Distinction from the US Army."
    ),

    # --- Skills & Superpower ---
    (
        "Mike's professional skills include Six Sigma, Lean Manufacturing, Innovation Development, "
        "Continuous Improvement, Value Stream Mapping, Kanban, Project Management, ISO 9000, and 5S."
    ),
    (
        "Mike's superpower is being 'The Fixer' — he takes highly complex situations and boils them down "
        "to the right information at the right time. He turns complex issues into simple concepts people "
        "can understand. He can get into any situation, learn how to do it, and fix it."
    ),

    # --- Weakness ---
    (
        "Mike's self-identified weakness: he thinks four steps ahead and sometimes communicates step 4 "
        "instead of step 1. He can fail to level-set or understand where people are at first. "
        "He strives for perfection and goes to 125%, which can make it hard for people to follow."
    ),

    # --- Decision-Making ---
    (
        "Mike's decision-making style: he seeks information, does research, plans, then decides. "
        "He is methodical and research-first in his approach."
    ),

    # --- Instagram Brand ---
    (
        "Mike's Instagram brand (@rodgemd1, 35K followers): posts every 2-3 days. "
        "Content pillars are physique/gym (Fit Over 30 angle), motivational philosophy overlaid on photos, "
        "music, and relationship/lifestyle content with James."
    ),
    (
        "Mike's Instagram brand voice: masculine vulnerability — physical strength combined with emotional depth "
        "and self-reflection. Common hashtags: #BuiltNotBorn, #MensMentality, #WorkInSilence, #BalanceIsEverything. "
        "Military/Army thread woven through imagery."
    ),
    (
        "Mike released 'Beautiful Ruin' — a piano-based emotional single promoted in his Instagram bio. "
        "Previous brand was 'Fit Over 30 | Muscle - Hormones - Habit'. Current brand is 'Fitness x Music'."
    ),

    # --- Music Taste ---
    (
        "Mike's music taste spans country, pop, rock, hip-hop, R&B, and EDM. "
        "Heavy rotation artists: Morgan Wallen, Missy Elliott (current phase — 'I don't know why'), "
        "BigXthaPlug (5 tracks in first 34 liked songs)."
    ),
    (
        "Mike's classic hip-hop favorites: DMX, Bone Thugs-N-Harmony, Busta Rhymes (2000s era). "
        "Country: Eric Church, HARDY (outlaw/gritty country). R&B slow jams: Brian McKnight, Joe. "
        "He listens to slow songs to concentrate while working."
    ),
    (
        "Mike has his own music: 'Beautiful Ruin' by Michael Rodgers on Spotify. "
        "He has 976 liked songs on Spotify. His taste is eclectic — swings from Texas rap "
        "to R&B to outlaw country to club mashups."
    ),

    # --- Fitness ---
    (
        "Mike's current fitness goal: 'big chest muscles so James wants to touch them.' "
        "He follows a Fit Over 30 angle — muscle, hormones, habits for men over 30. "
        "He is a regular gym-goer and posts physique content on Instagram."
    ),
    (
        "TransformFit is the fitness business Mike is building. "
        "UX/UI designs are complete and it needs alpha testing."
    ),

    # --- Hobbies & Interests ---
    (
        "Mike's hobbies: snowboarding (James got him into it, goes with the kids), "
        "music (both listening and creating), climbing (appeared in Instagram posts). "
        "He is a self-described nerd who loves computers and went 'stupid crazy' into AI."
    ),
    (
        "Mike would love to play hockey but games are at 10 PM, so he sticks to kickball and volleyball "
        "for social sports. He travels frequently — was in Milan, Italy in January 2026 "
        "and is frequently on planes."
    ),

    # --- Personality ---
    (
        "Mike has a dry sense of humor and loves dad jokes — he constantly irritates James with them. "
        "People consistently misunderstand his humor. "
        "He's proud of helping Jacob see his full potential and of James being proud of his own fitness transformation."
    ),

    # --- Companies Building ---
    (
        "Mike is building multiple companies: TransformFit (fitness app, UX/UI complete, needs alpha testing), "
        "Virtual Architect (future company), and plans to commercialize Susan as a product. "
        "He's building Jake PA to free up time between his day job and side businesses."
    ),

    # --- Friend Network ---
    (
        "Mike's best friend is JC (@johnjcampbell on Instagram), who is moving away — "
        "farewell post on March 20, 2026. Mike has 500+ LinkedIn connections and 5K LinkedIn followers."
    ),

    # --- Published Writing ---
    (
        "Mike has published 5 LinkedIn articles on innovation, telemedicine, and startup strategy (2020). "
        "His most popular article 'Amidst the COVID-19 Pandemic, Telemedicine Has Proven to be an Essential Asset' "
        "received 295 reactions."
    ),
]


def chunk_hash(text: str) -> str:
    """SHA256 hash of chunk text for dedup."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def main():
    parser = argparse.ArgumentParser(description="Ingest Mike Rodgers profile into Jake's Brain")
    parser.add_argument("--dry-run", action="store_true", help="Show chunks without ingesting")
    args = parser.parse_args()

    print("=" * 60)
    print("Jake Brain — Mike Rodgers Profile Ingest")
    print(f"Chunks to ingest: {len(PROFILE_CHUNKS)}")
    print("=" * 60)

    # Show all chunks
    for i, chunk in enumerate(PROFILE_CHUNKS, 1):
        h = chunk_hash(chunk)
        preview = chunk[:80].replace("\n", " ")
        print(f"  {i:2d}. [{h}] {preview}...")

    if args.dry_run:
        print(f"\n[DRY RUN] Would ingest {len(PROFILE_CHUNKS)} chunks. Exiting.")
        return

    print(f"\nIngesting {len(PROFILE_CHUNKS)} profile chunks into Jake's Brain...\n")
    pipeline = BrainPipeline()

    results = {"success": 0, "failed": 0, "skipped": 0, "people": set(), "topics": set()}
    seen_hashes: set[str] = set()
    now = datetime.now(timezone.utc).isoformat()

    for i, chunk in enumerate(PROFILE_CHUNKS, 1):
        h = chunk_hash(chunk)
        if h in seen_hashes:
            results["skipped"] += 1
            print(f"  [{i}/{len(PROFILE_CHUNKS)}] SKIP (duplicate hash {h})")
            continue
        seen_hashes.add(h)

        try:
            result = pipeline.ingest_conversation(
                text=chunk,
                session_id=f"profile-ingest-{h}",
                source="profile_interview",
                source_type="ingestion",
                occurred_at=now,
            )
            extraction = result.get("extraction", {})
            results["success"] += 1
            results["people"].update(extraction.get("people", []))
            results["topics"].update(extraction.get("topics", []))
            print(
                f"  [{i}/{len(PROFILE_CHUNKS)}] OK — "
                f"people={extraction.get('people', [])}, "
                f"topics={extraction.get('topics', [])}, "
                f"importance={extraction.get('importance', 0):.2f}"
            )
        except Exception as exc:
            results["failed"] += 1
            print(f"  [{i}/{len(PROFILE_CHUNKS)}] FAILED — {exc}")

    print(f"\n{'=' * 60}")
    print("Profile Ingest Complete")
    print(f"  Success: {results['success']}")
    print(f"  Failed:  {results['failed']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  People discovered:  {sorted(results['people'])}")
    print(f"  Topics discovered:  {sorted(results['topics'])}")
    print(f"{'=' * 60}")

    # Show updated brain stats
    try:
        stats = pipeline.stats()
        print("\nBrain Stats After Ingest:")
        for key, val in stats.items():
            print(f"  {key}: {val}")
    except Exception as exc:
        print(f"\nCouldn't get brain stats: {exc}")


if __name__ == "__main__":
    main()
