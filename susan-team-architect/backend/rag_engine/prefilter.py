# rag_engine/prefilter.py
"""Lexical + metadata prefilter for vector search.

Generates parameterized SQL clause fragments that can be composed into
a WHERE clause before the similarity search runs, narrowing the
candidate set and reducing embedding-comparison cost.

All user-supplied values are returned as bind parameters to prevent
SQL injection.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PrefilterSpec:
    """Describes the metadata and keyword constraints to apply before
    vector similarity search."""

    company_id: str = ""
    data_types: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    min_similarity: float = 0.0


def apply_prefilter_sql(
    spec: PrefilterSpec,
) -> dict[str, tuple[str, list[Any]]]:
    """Build parameterized SQL filter clauses from a :class:`PrefilterSpec`.

    Returns a dict mapping logical filter names to
    ``(sql_template, param_values)`` tuples.  The SQL template uses
    ``%s`` placeholders; the caller must pass *param_values* through
    its database driver so they are properly escaped.
    """
    parts: dict[str, tuple[str, list[Any]]] = {}

    if spec.company_id:
        parts["company_id"] = (
            "company_id = %s OR company_id = 'shared'",
            [spec.company_id],
        )

    if spec.data_types:
        parts["data_type"] = (
            "data_type = ANY(%s)",
            [spec.data_types],
        )

    if spec.keywords:
        placeholders = " OR ".join("content ILIKE %s" for _ in spec.keywords)
        params = [f"%{kw}%" for kw in spec.keywords]
        parts["keywords"] = (f"({placeholders})", params)

    return parts
