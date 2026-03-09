# rag_engine/prefilter.py
"""Lexical + metadata prefilter for vector search.

Generates SQL clause fragments that can be composed into a WHERE clause
before the similarity search runs, narrowing the candidate set and
reducing embedding-comparison cost.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PrefilterSpec:
    """Describes the metadata and keyword constraints to apply before
    vector similarity search."""

    company_id: str = ""
    data_types: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    min_similarity: float = 0.0


def apply_prefilter_sql(spec: PrefilterSpec) -> dict[str, str]:
    """Build SQL filter clauses from a :class:`PrefilterSpec`.

    Returns a dict mapping logical filter names to SQL expression strings.
    The caller is responsible for joining them with ``AND`` and
    interpolating them safely into its query builder.
    """
    parts: dict[str, str] = {}

    if spec.company_id:
        parts["company_id"] = (
            f"company_id = '{spec.company_id}' OR company_id = 'shared'"
        )

    if spec.data_types:
        type_list = ", ".join(f"'{t}'" for t in spec.data_types)
        parts["data_type"] = f"data_type IN ({type_list})"

    if spec.keywords:
        keyword_conditions = " OR ".join(
            f"content ILIKE '%{kw}%'" for kw in spec.keywords
        )
        parts["keywords"] = f"({keyword_conditions})"

    return parts
