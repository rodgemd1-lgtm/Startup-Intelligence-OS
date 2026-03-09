"""Ingest TransformFit training research, structured exercise catalogs, and user research."""
from __future__ import annotations

from collections import defaultdict
import csv
from html import unescape
import json
from pathlib import Path
import re
import sys
from typing import Any

import httpx
from supabase import create_client
import yaml

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.chunker import chunk_text
from rag_engine.ingestion.appstore import AppStoreIngestor
from rag_engine.ingestion.markdown import MarkdownIngestor
from rag_engine.ingestion.reddit import RedditIngestor
from rag_engine.ingestion.web import WebIngestor
from rag_engine.retriever import Retriever
from susan_core.config import config
from susan_core.schemas import KnowledgeChunk


DOMAIN_ROOT = BACKEND_ROOT / "data" / "domains" / "transformfit_training_intelligence"
MANIFEST_PATH = DOMAIN_ROOT / "datasets" / "open_sources.yaml"
PROGRAMS_DIR = DOMAIN_ROOT / "programs"
CUES_PATH = DOMAIN_ROOT / "coaching_cues" / "transformfit_moments_of_truth_cues.yaml"
SIMULATION_DIR = DOMAIN_ROOT / "simulations"
EDITORIAL_PATHS = {
    "business_strategy": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_TEAM_ARCHITECTURE_AND_HIRING_STRATEGY.md",
    ],
    "market_research": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_MARKET_AND_TEAM_BENCHMARK_2026.md",
    ],
    "expert_knowledge": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_ROLE_ATLAS_AND_SCORECARDS_2026.md",
    ],
    "operational_protocols": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_EXPERT_COUNCILS_AND_ADVISORY_NETWORK.md",
    ],
    "exercise_science": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_WORKOUT_PROGRAM_STUDIO_BRIEF.md",
    ],
    "program_library": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_PROGRAM_LIBRARY_2026.md",
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_PROGRAM_SELECTION_SYSTEM.md",
        Path("/Users/mikerodgers/adapt-evolve-progress/docs/methodology/PROGRAM_PHILOSOPHY.md"),
        Path("/Users/mikerodgers/adapt-evolve-progress/docs/methodology/PROGRAM_FULL_BODY_12WEEK.md"),
        Path("/Users/mikerodgers/adapt-evolve-progress/docs/methodology/PROGRAM_UPPER_LOWER_12WEEK.md"),
        Path("/Users/mikerodgers/adapt-evolve-progress/docs/methodology/PROGRAM_PPL_12WEEK.md"),
    ],
    "training_research": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_TRAINING_RESEARCH_STUDIO_BRIEF.md",
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_TRAINING_SOURCE_MAP.md",
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_PROGRAM_EVIDENCE_NOTES_2026.md",
    ],
    "guru_research": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_GURU_AND_INFLUENCER_RECOMMENDATION_MAP_2026.md",
    ],
    "frontier_academic_research": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_FRONTIER_ACADEMIC_RESEARCH_2026.md",
    ],
    "consumer_failure_patterns": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_CONSUMER_FAILURE_PATTERNS_2026.md",
    ],
    "predictive_coaching": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_PREDICTIVE_COACHING_CUE_SYSTEM_2026.md",
    ],
    "simulation_models": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_MONTE_CARLO_SIMULATION_SYSTEM_2026.md",
    ],
    "session_ux": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_WORKOUT_SESSION_STUDIO_BRIEF.md",
        Path("/Users/mikerodgers/adapt-evolve-progress/docs/WORKOUT_LOGGING_UX_PLAN.md"),
    ],
    "coaching_architecture": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_COACHING_ARCHITECTURE_BRIEF.md",
        Path("/Users/mikerodgers/adapt-evolve-progress/docs/AI_ARCHITECTURE.md"),
    ],
    "social_growth": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_SOCIAL_MEDIA_STUDIO_BRIEF.md",
    ],
    "sports_psychology": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_CONVERSATION_DESIGN_AND_COACHING_SYSTEM.md",
    ],
    "behavioral_economics": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_BEHAVIOR_CHANGE_AND_ADHERENCE_SYSTEM.md",
    ],
    "algorithm_design": [
        DOMAIN_ROOT / "editorial" / "TRANSFORMFIT_ALGORITHM_LAB_BRIEF.md",
        Path("/Users/mikerodgers/adapt-evolve-progress/docs/AI_ARCHITECTURE.md"),
    ],
}
RESET_TYPES = [
    "business_strategy",
    "market_research",
    "expert_knowledge",
    "operational_protocols",
    "guru_research",
    "frontier_academic_research",
    "consumer_failure_patterns",
    "predictive_coaching",
    "simulation_models",
    "program_library",
    "exercise_science",
    "training_research",
    "exercise_catalog",
    "sleep_recovery",
    "nutrition",
    "user_research",
    "session_ux",
    "coaching_architecture",
    "social_growth",
    "sports_psychology",
    "behavioral_economics",
    "algorithm_design",
]


def _delete_existing(company_id: str, data_type: str) -> None:
    supabase = create_client(config.supabase_url, config.supabase_key)
    supabase.table("knowledge_chunks").delete().eq("company_id", company_id).eq("data_type", data_type).execute()


def _strip_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _chunk_blocks(blocks: list[str], group_size: int) -> list[str]:
    grouped: list[str] = []
    for index in range(0, len(blocks), group_size):
        grouped.append("\n\n".join(blocks[index:index + group_size]))
    return grouped


def _plain_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "simpleText" in value:
            return str(value["simpleText"])
        if "runs" in value:
            return "".join(str(run.get("text", "")) for run in value.get("runs", []))
    if isinstance(value, list):
        return " ".join(_plain_text(item) for item in value)
    return ""


def _store_structured_chunks(
    retriever: Retriever,
    texts: list[str],
    *,
    company_id: str,
    data_type: str,
    source: str,
    source_url: str,
    metadata: dict[str, Any],
) -> int:
    chunks = []
    for text in texts:
        for chunk in chunk_text(text, max_tokens=500, overlap=0):
            chunks.append(
                KnowledgeChunk(
                    content=chunk,
                    company_id=company_id,
                    data_type=data_type,
                    source=source,
                    source_url=source_url,
                    metadata=metadata,
                )
            )
    return retriever.store_chunks(chunks)


def _ingest_free_exercise_db(
    retriever: Retriever,
    company_id: str,
    url: str,
    data_type: str,
    group_size: int,
) -> int:
    response = httpx.get(url, timeout=60, follow_redirects=True)
    response.raise_for_status()
    exercises = response.json()
    blocks = []
    for item in exercises:
        instructions = " | ".join((item.get("instructions") or [])[:4])
        blocks.append(
            "\n".join(
                [
                    f"Exercise: {item.get('name', 'Unknown')}",
                    f"Category: {item.get('category', 'Unknown')}",
                    f"Level: {item.get('level', 'Unknown')}",
                    f"Mechanic: {item.get('mechanic', 'Unknown')}",
                    f"Equipment: {item.get('equipment', 'Unknown')}",
                    f"Primary muscles: {', '.join(item.get('primaryMuscles') or []) or 'Unknown'}",
                    f"Secondary muscles: {', '.join(item.get('secondaryMuscles') or []) or 'None listed'}",
                    f"Instructions: {instructions or 'No instructions listed'}",
                ]
            )
        )
    texts = _chunk_blocks(blocks, group_size)
    return _store_structured_chunks(
        retriever,
        texts,
        company_id=company_id,
        data_type=data_type,
        source="structured:free-exercise-db",
        source_url=url,
        metadata={"dataset_id": "free_exercise_db", "record_count": len(exercises)},
    )


def _ingest_wger(
    retriever: Retriever,
    company_id: str,
    url: str,
    data_type: str,
    group_size: int,
) -> int:
    items: list[dict[str, Any]] = []
    next_url = url
    while next_url:
        response = httpx.get(next_url, timeout=60, follow_redirects=True)
        response.raise_for_status()
        payload = response.json()
        items.extend(payload.get("results", []))
        next_url = payload.get("next")

    blocks = []
    for item in items:
        translation = (item.get("translations") or [{}])[0]
        primary = ", ".join(m.get("name_en") or m.get("name") or "" for m in item.get("muscles") or []) or "Unknown"
        secondary = ", ".join(m.get("name_en") or m.get("name") or "" for m in item.get("muscles_secondary") or []) or "None listed"
        equipment = ", ".join(eq.get("name") or "" for eq in item.get("equipment") or []) or "Unknown"
        blocks.append(
            "\n".join(
                [
                    f"Exercise: {translation.get('name', 'Unknown')}",
                    f"Category: {(item.get('category') or {}).get('name', 'Unknown')}",
                    f"Primary muscles: {primary}",
                    f"Secondary muscles: {secondary}",
                    f"Equipment: {equipment}",
                    f"Description: {_strip_html(translation.get('description', 'No description listed'))}",
                ]
            )
        )

    texts = _chunk_blocks(blocks, group_size)
    return _store_structured_chunks(
        retriever,
        texts,
        company_id=company_id,
        data_type=data_type,
        source="structured:wger",
        source_url=url,
        metadata={"dataset_id": "wger_exerciseinfo", "record_count": len(items)},
    )


def _render_program(program: dict[str, Any]) -> str:
    lines = [
        f"Program: {program.get('name', 'Unknown')}",
        f"Program ID: {program.get('id', 'unknown')}",
        f"Goal: {program.get('goal', 'unknown')}",
        f"Target athlete: {program.get('target_athlete', 'unknown')}",
        f"Training age: {program.get('training_age', 'unknown')}",
        f"Frequency: {program.get('frequency_days', 'unknown')} days/week",
        f"Duration: {program.get('duration_weeks', 'unknown')} weeks",
        f"Session length: {program.get('session_length_minutes', 'unknown')} minutes",
        f"Equipment profile: {program.get('equipment_profile', 'unknown')}",
        f"Split: {program.get('split', 'unknown')}",
    ]
    if program.get("phases"):
        lines.append("Phases:")
        for phase in program["phases"]:
            lines.append(f"- Weeks {phase.get('weeks')}: {phase.get('name')} — {phase.get('focus')}")
    if program.get("progression"):
        lines.append("Progression rules:")
        for key, value in program["progression"].items():
            lines.append(f"- {key}: {value}")
    if program.get("reentry"):
        lines.append("Re-entry rules:")
        for key, value in program["reentry"].items():
            lines.append(f"- {key}: {value}")
    if program.get("sessions"):
        lines.append("Sessions:")
        for session in program["sessions"]:
            lines.append(f"{session.get('day')}: {session.get('focus')}")
            for exercise in session.get("exercises", []):
                lines.append(
                    f"* {exercise.get('name')} — {exercise.get('sets')} sets, {exercise.get('reps')} reps, RIR {exercise.get('rir')}, rest {exercise.get('rest_seconds')}s, substitutions: {', '.join(exercise.get('substitutions', [])) or 'none'}"
                )
    if program.get("coaching_notes"):
        lines.append("Coaching notes:")
        for key, value in program["coaching_notes"].items():
            lines.append(f"- {key}: {value}")
    if program.get("coach_cue_profile"):
        lines.append("Coach cue profile:")
        for key, value in program["coach_cue_profile"].items():
            if isinstance(value, list):
                lines.append(f"- {key}: {', '.join(str(item) for item in value)}")
            else:
                lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def _ingest_program_library(retriever: Retriever, company_id: str) -> int:
    total = 0
    for path in sorted(PROGRAMS_DIR.glob("*.yaml")):
        program = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        total += _store_structured_chunks(
            retriever,
            [_render_program(program)],
            company_id=company_id,
            data_type="program_library",
            source=f"structured:transformfit-program:{program.get('id', path.stem)}",
            source_url=str(path),
            metadata={
                "program_id": program.get("id", path.stem),
                "program_name": program.get("name", path.stem),
                "goal": program.get("goal"),
                "training_age": program.get("training_age"),
                "frequency_days": program.get("frequency_days"),
                "equipment_profile": program.get("equipment_profile"),
            },
        )
    return total


def _walk_video_renderers(obj: Any, renderers: list[dict[str, Any]]) -> None:
    if isinstance(obj, dict):
        video_renderer = obj.get("videoRenderer")
        if isinstance(video_renderer, dict):
            renderers.append(video_renderer)
        for value in obj.values():
            _walk_video_renderers(value, renderers)
    elif isinstance(obj, list):
        for item in obj:
            _walk_video_renderers(item, renderers)


def _ingest_youtube_channel_videos(
    retriever: Retriever,
    company_id: str,
    source: dict[str, Any],
) -> int:
    response = httpx.get(
        source["url"],
        timeout=60,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", response.text)
    if not match:
        return 0
    payload = json.loads(match.group(1))
    renderers: list[dict[str, Any]] = []
    _walk_video_renderers(payload, renderers)

    seen_ids: set[str] = set()
    blocks: list[str] = []
    max_videos = int(source.get("max_videos", 24))
    channel_name = source.get("channel_name", source.get("title", "Unknown channel"))

    for renderer in renderers:
        video_id = renderer.get("videoId")
        if not video_id or video_id in seen_ids:
            continue
        seen_ids.add(video_id)
        title = _plain_text(renderer.get("title"))
        published = _plain_text(renderer.get("publishedTimeText"))
        views = _plain_text(renderer.get("viewCountText")) or _plain_text(renderer.get("shortViewCountText"))
        description = _plain_text(renderer.get("descriptionSnippet"))
        blocks.append(
            "\n".join(
                [
                    f"Channel: {channel_name}",
                    f"Handle: {source.get('channel_handle', '')}",
                    f"Video title: {title or 'Unknown'}",
                    f"Published: {published or 'Unknown'}",
                    f"Views: {views or 'Unknown'}",
                    f"Description: {description or 'No description available'}",
                    f"Video URL: https://www.youtube.com/watch?v={video_id}",
                ]
            )
        )
        if len(blocks) >= max_videos:
            break

    texts = _chunk_blocks(blocks, int(source.get("group_size", 4)))
    return _store_structured_chunks(
        retriever,
        texts,
        company_id=company_id,
        data_type=source["data_type"],
        source="structured:youtube_channel_recent_videos",
        source_url=source["url"],
        metadata={
            "dataset_id": "youtube_channel_recent_videos",
            "channel_name": channel_name,
            "channel_handle": source.get("channel_handle"),
            "record_count": len(blocks),
        },
    )


def _render_cue_entry(entry: dict[str, Any]) -> str:
    lines = [
        f"Cue ID: {entry.get('id', 'unknown')}",
        f"Moment: {entry.get('moment', 'unknown')}",
        f"Trigger logic: {entry.get('trigger_logic', 'unknown')}",
        f"Predictive value: {entry.get('predictive_value', 'unknown')}",
        f"Primary agents: {', '.join(entry.get('primary_agents', [])) or 'unknown'}",
        f"Default cue: {entry.get('default_cue', 'unknown')}",
    ]
    if entry.get("cue_principles"):
        lines.append(f"Cue principles: {', '.join(entry['cue_principles'])}")
    if entry.get("profile_variants"):
        lines.append("Profile variants:")
        for key, value in entry["profile_variants"].items():
            lines.append(f"- {key}: {value}")
    if entry.get("actions"):
        lines.append(f"Actions: {', '.join(entry['actions'])}")
    if entry.get("avoid"):
        lines.append(f"Avoid: {', '.join(entry['avoid'])}")
    return "\n".join(lines)


def _ingest_cue_library(retriever: Retriever, company_id: str) -> int:
    entries = yaml.safe_load(CUES_PATH.read_text(encoding="utf-8")) or []
    texts = [_render_cue_entry(entry) for entry in entries]
    return _store_structured_chunks(
        retriever,
        texts,
        company_id=company_id,
        data_type="predictive_coaching",
        source="structured:transformfit_coach_cues",
        source_url=str(CUES_PATH),
        metadata={"dataset_id": "transformfit_moments_of_truth_cues", "record_count": len(entries)},
    )


def _render_simulation_summary(summary: dict[str, Any]) -> list[str]:
    texts = [
        "\n".join(
            [
                "TransformFit Monte Carlo Summary",
                f"Generated at: {summary.get('generated_at', 'unknown')}",
                f"Users per archetype: {summary.get('users_per_archetype', 'unknown')}",
                f"Total users per condition: {summary.get('total_users_per_condition', 'unknown')}",
                f"Completion rate lift: {summary.get('completion_rate_lift', 'unknown')}",
                f"Dropout rate reduction: {summary.get('dropout_rate_reduction', 'unknown')}",
                f"Top recommended cues: {', '.join(summary.get('recommended_top_cues', []))}",
            ]
        )
    ]

    archetype_lines = ["Archetype simulation summary:"]
    for row in summary.get("archetype_summary", []):
        archetype_lines.append(
            f"- {row.get('label')}: completion {row.get('completion_rate_with_coach')} with coach vs {row.get('completion_rate_without_coach')} without; dropout {row.get('dropout_rate_with_coach')} vs {row.get('dropout_rate_without_coach')}"
        )
    texts.append("\n".join(archetype_lines))

    risk_lines = ["Risk windows:"]
    for row in summary.get("risk_windows", [])[:12]:
        risk_lines.append(
            f"- {row.get('trigger_id')}: {row.get('occurrences_with_coach')} occurrences with coach, priority {row.get('recommended_priority')}"
        )
    texts.append("\n".join(risk_lines))
    return texts


def _ingest_simulation_models(retriever: Retriever, company_id: str) -> int:
    summary_path = SIMULATION_DIR / "transformfit_monte_carlo_summary.json"
    if not summary_path.exists():
        return 0
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return _store_structured_chunks(
        retriever,
        _render_simulation_summary(summary),
        company_id=company_id,
        data_type="simulation_models",
        source="structured:transformfit_monte_carlo",
        source_url=str(summary_path),
        metadata={"dataset_id": "transformfit_monte_carlo_summary"},
    )


def main() -> int:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8")) or {}
    company_id = manifest.get("company_id", "transformfit")

    for data_type in RESET_TYPES:
        _delete_existing(company_id, data_type)

    totals: dict[str, int] = defaultdict(int)
    markdown_ingestor = MarkdownIngestor()
    web_ingestor = WebIngestor()
    reddit_ingestor = RedditIngestor()
    appstore_ingestor = AppStoreIngestor()
    retriever = Retriever()

    for data_type, paths in EDITORIAL_PATHS.items():
        for path in paths:
            if path.exists():
                totals[data_type] += markdown_ingestor.ingest(str(path), company_id=company_id, data_type=data_type)

    if PROGRAMS_DIR.exists():
        totals["program_library"] += _ingest_program_library(retriever, company_id)
    if CUES_PATH.exists():
        totals["predictive_coaching"] += _ingest_cue_library(retriever, company_id)
    if SIMULATION_DIR.exists():
        totals["simulation_models"] += _ingest_simulation_models(retriever, company_id)

    for source in manifest.get("web_sources", []):
        totals[source["data_type"]] += web_ingestor.ingest(
            source["url"],
            company_id=company_id,
            data_type=source["data_type"],
        )

    for source in manifest.get("structured_sources", []):
        dataset_id = source["dataset_id"]
        if dataset_id == "free_exercise_db":
            totals[source["data_type"]] += _ingest_free_exercise_db(
                retriever,
                company_id,
                source["url"],
                source["data_type"],
                int(source.get("group_size", 5)),
            )
        elif dataset_id == "wger_exerciseinfo":
            totals[source["data_type"]] += _ingest_wger(
                retriever,
                company_id,
                source["url"],
                source["data_type"],
                int(source.get("group_size", 5)),
            )
        elif dataset_id == "youtube_channel_recent_videos":
            totals[source["data_type"]] += _ingest_youtube_channel_videos(
                retriever,
                company_id,
                source,
            )

    for source in manifest.get("reddit_sources", []):
        totals[source["data_type"]] += reddit_ingestor.ingest(
            company_id=company_id,
            data_type=source["data_type"],
            subreddits=source.get("subreddits", []),
            limit=int(source.get("limit", 20)),
            time_filter=source.get("time_filter", "year"),
        )

    for source in manifest.get("appstore_sources", []):
        totals[source["data_type"]] += appstore_ingestor.ingest(
            company_id=company_id,
            data_type=source["data_type"],
            apps=source.get("apps", {}),
        )

    print(
        json.dumps(
            {
                "company_id": company_id,
                "manifest": str(MANIFEST_PATH),
                "stored": dict(totals),
                "total": sum(totals.values()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
