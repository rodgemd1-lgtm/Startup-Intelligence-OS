"""Scoring rubric definitions — configurable per company/domain."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CompanyRubric(BaseModel):
    keywords: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    action_patterns: list[str] = Field(
        default_factory=lambda: ["launch", "announce", "acquire", "partner", "hire", "raise"],
    )


class Rubric(BaseModel):
    companies: dict[str, CompanyRubric] = Field(default_factory=dict)
