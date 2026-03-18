"""Birch scoring engine — 3-axis composite scoring."""
from __future__ import annotations

import re
from typing import Literal

from birch.schemas import RawSignal, ScoredSignal
from birch.rubric import Rubric


class BirchScorer:
    RELEVANCE_WEIGHT = 0.40
    ACTIONABILITY_WEIGHT = 0.35
    URGENCY_WEIGHT = 0.25

    def __init__(self, rubric: Rubric) -> None:
        self._rubric = rubric

    def score(self, raw: RawSignal) -> ScoredSignal:
        best_company = ""
        best_relevance = 0

        text = f"{raw.title} {raw.content}".lower()

        for company, company_rubric in self._rubric.companies.items():
            relevance = self._score_relevance(text, company_rubric)
            if relevance > best_relevance:
                best_relevance = relevance
                best_company = company

        actionability = self._score_actionability(text, best_company)
        urgency = self._score_urgency(raw)

        composite = int(
            best_relevance * self.RELEVANCE_WEIGHT
            + actionability * self.ACTIONABILITY_WEIGHT
            + urgency * self.URGENCY_WEIGHT
        )
        composite = max(0, min(100, composite))
        tier = self.classify_tier(composite)

        routed_to = ""
        if tier == 1 and best_company:
            routed_to = "competitive-response"

        return ScoredSignal(
            source=raw.source,
            title=raw.title,
            content=raw.content,
            url=raw.url,
            relevance=best_relevance,
            actionability=actionability,
            urgency=urgency,
            score=composite,
            tier=tier,
            company=best_company,
            routed_to=routed_to,
        )

    def _score_relevance(self, text: str, rubric) -> int:
        keyword_hits = sum(1 for kw in rubric.keywords if kw.lower() in text)
        competitor_hits = sum(1 for c in rubric.competitors if c.lower() in text)
        if not rubric.keywords and not rubric.competitors:
            return 0
        # Any keyword or competitor hit is a strong signal
        # Base 20 per keyword hit, 30 per competitor hit, capped at 100
        score = keyword_hits * 20 + competitor_hits * 30
        return max(0, min(100, score))

    def _score_actionability(self, text: str, company: str) -> int:
        if not company:
            return 10
        rubric = self._rubric.companies.get(company)
        if not rubric:
            return 10
        action_hits = sum(1 for p in rubric.action_patterns if p.lower() in text)
        # High base when company matches, each action verb boosts significantly
        return max(10, min(100, 40 + action_hits * 20))

    def _score_urgency(self, raw: RawSignal) -> int:
        text = f"{raw.title} {raw.content}".lower()
        urgency_words = ["breaking", "just", "today", "announces", "launches", "immediate", "launch", "announce"]
        hits = sum(1 for w in urgency_words if w in text)
        return max(10, min(100, 20 + hits * 20))

    @staticmethod
    def classify_tier(score: int) -> Literal[1, 2, 3]:
        if score >= 80:
            return 1
        elif score >= 50:
            return 2
        return 3
