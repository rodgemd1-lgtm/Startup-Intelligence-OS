"""AI Employee Registry."""
from .oracle_sentinel import OracleSentinel
from .research_agent import ResearchAgent
from .content_creator import ContentCreator
from .family_coordinator import FamilyCoordinator

EMPLOYEE_REGISTRY = {
    "oracle_sentinel": OracleSentinel,
    "research_agent": ResearchAgent,
    "content_creator": ContentCreator,
    "family_coordinator": FamilyCoordinator,
}

EMPLOYEE_SCHEDULES = {
    "oracle_sentinel": "0 6 * * 1-5",     # Daily 6 AM weekdays
    "research_agent": "0 22 * * *",        # Daily 10 PM
    "content_creator": "0 9 * * 1",        # Monday 9 AM
    "family_coordinator": "0 7 * * 0",     # Sunday 7 AM (weekly family summary)
}
