"""Tests for Birch signal scoring engine."""
import pytest


def test_raw_signal_creation():
    from birch.schemas import RawSignal

    sig = RawSignal(
        source="firehose",
        title="Epic launches Agent Factory",
        content="Epic Systems announced...",
    )
    assert sig.source == "firehose"
    assert sig.id.startswith("sig-")


def test_scored_signal_tier_1():
    from birch.schemas import ScoredSignal

    sig = ScoredSignal(
        source="firehose",
        title="Epic Agent Factory",
        content="...",
        relevance=92,
        actionability=85,
        urgency=80,
        score=87,
        tier=1,
        company="oracle-health",
    )
    assert sig.tier == 1
    assert sig.score == 87


def test_scorer_high_relevance():
    from birch.scorer import BirchScorer
    from birch.schemas import RawSignal
    from birch.rubric import Rubric, CompanyRubric

    rubric = Rubric(companies={
        "oracle-health": CompanyRubric(
            keywords=["epic", "ehr", "himss", "clinical ai", "oracle health"],
            competitors=["epic", "meditech", "athenahealth", "cerner"],
        ),
    })
    scorer = BirchScorer(rubric=rubric)
    raw = RawSignal(
        source="firehose",
        title="Epic launches Agent Factory at HIMSS",
        content="Epic Systems announced Agent Factory, a no-code AI agent builder for healthcare",
    )
    scored = scorer.score(raw)
    assert scored.score >= 70  # High relevance to Oracle Health
    assert scored.tier in (1, 2)
    assert scored.company == "oracle-health"


def test_scorer_low_relevance():
    from birch.scorer import BirchScorer
    from birch.schemas import RawSignal
    from birch.rubric import Rubric, CompanyRubric

    rubric = Rubric(companies={
        "oracle-health": CompanyRubric(
            keywords=["epic", "ehr", "clinical ai"],
            competitors=["epic", "meditech"],
        ),
    })
    scorer = BirchScorer(rubric=rubric)
    raw = RawSignal(
        source="firehose",
        title="Tesla announces new factory in Austin",
        content="Tesla will build a new manufacturing facility...",
    )
    scored = scorer.score(raw)
    assert scored.score < 50
    assert scored.tier == 3


def test_scorer_tier_classification():
    from birch.scorer import BirchScorer

    assert BirchScorer.classify_tier(85) == 1
    assert BirchScorer.classify_tier(65) == 2
    assert BirchScorer.classify_tier(30) == 3
    assert BirchScorer.classify_tier(80) == 1
    assert BirchScorer.classify_tier(50) == 2
    assert BirchScorer.classify_tier(49) == 3
