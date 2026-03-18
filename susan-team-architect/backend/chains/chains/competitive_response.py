"""Competitive Response Chain: SCOUT -> HERALD -> SENTINEL-HEALTH."""
from chains.schemas import ChainDef, ChainStep, SignalTrigger

competitive_response = ChainDef(
    name="competitive-response",
    description="Detect competitive signals, draft response, compliance check",
    trigger=SignalTrigger(min_score=80, signal_types=["competitor_move"]),
    autonomy="SUPERVISED",
    steps=[
        ChainStep(agent="scout", output_key="signals"),
        ChainStep(agent="herald", input_key="signals", output_key="drafts"),
        ChainStep(
            agent="sentinel-health",
            input_key="drafts",
            output_key="cleared",
            gate=True,
        ),
    ],
)
