"""Brain-specific configuration — layer weights, decay rates, thresholds."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class BrainConfig:
    """Tunable parameters for Jake's cognitive memory engine."""

    # Layer weights for composite ranking
    weight_working: float = 1.3
    weight_episodic: float = 1.0
    weight_semantic: float = 1.2
    weight_procedural: float = 1.5

    # Decay
    episodic_half_life_days: float = 30.0  # 30-day half-life for episodic memories
    access_boost_per_hit: float = 0.05     # 5% boost per access, max 10 hits
    max_access_boost_hits: int = 10

    # Promotion thresholds
    promotion_episode_threshold: int = 3    # 3+ episodes → promote to semantic
    working_auto_promote_importance: float = 0.7  # working memories above this auto-promote
    working_expiry_hours: int = 24

    # Entity resolution
    entity_match_strict: bool = True        # strict matching (exact name + type) for now
    entity_fuzzy_threshold: float = 0.85    # for future fuzzy matching

    # Contradiction detection
    contradiction_similarity_threshold: float = 0.85  # if two semantic facts are this similar
    contradiction_flag_threshold: float = 0.3          # ...and confidence difference is within this

    # Extraction
    known_people: list[str] = field(default_factory=lambda: [
        "mike", "mike rodgers", "james", "james loehr", "jacob", "alex",
        "jen", "matt cohlmia", "matt", "jordan voss", "jordan", "ellen",
    ])

    known_projects: dict[str, list[str]] = field(default_factory=lambda: {
        "oracle-health": ["oracle health", "oracle-health", "cohlmia", "myhelp"],
        "alex-recruiting": ["alex recruiting", "recruiting", "jacob.*recruit"],
        "startup-os": ["startup intelligence", "susan", "startup-os"],
        "hermes": ["hermes", "openclaw", "telegram bot"],
        "transformfit": ["transformfit", "transform fit"],
        "virtual-architect": ["virtual architect"],
    })

    # Batch sizes
    embed_batch_size: int = 128
    store_batch_size: int = 100


# Singleton
brain_config = BrainConfig()
