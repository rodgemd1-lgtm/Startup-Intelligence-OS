"""Daily Cycle Chain: SCOUT -> ARIA digest assembly."""
from chains.schemas import ChainDef, ChainStep, ScheduledTrigger

daily_cycle = ChainDef(
    name="daily-cycle",
    description="Morning intelligence cycle: scan signals, assemble daily brief",
    trigger=ScheduledTrigger(cron="0 6 * * *"),
    autonomy="MANUAL",  # starts MANUAL, graduates to AUTONOMOUS
    steps=[
        ChainStep(agent="scout", output_key="signals"),
        ChainStep(agent="aria", input_key="signals", output_key="brief"),
    ],
)
