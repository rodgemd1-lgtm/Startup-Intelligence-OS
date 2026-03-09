"""Ingest TransformFit app-repo design, UX, operating, and studio docs into Susan's RAG store."""
from __future__ import annotations

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rag_engine.ingestion.markdown import MarkdownIngestor


COMPANY_ID = "transformfit"
PROJECT_ROOT = Path("/Users/mikerodgers/adapt-evolve-progress")
DOCS_ROOT = PROJECT_ROOT / "docs"
DESIGN_ROOT = DOCS_ROOT / "design"
COMPANY_ROOT = DOCS_ROOT / "company"
RESEARCH_ROOT = DOCS_ROOT / "research" / "fitness-intelligence"
METHODOLOGY_ROOT = DOCS_ROOT / "methodology"
TEAMS_ROOT = DOCS_ROOT / "teams"

PATHS = {
    "emotional_design": [
        DESIGN_ROOT / "TRANSFORMFIT_DESIGN_PRINCIPLES_2026.md",
    ],
    "product_expertise": [
        DESIGN_ROOT / "TRANSFORMFIT_LANDING_PAGE_STUDIO_GUIDE.md",
        DESIGN_ROOT / "TRANSFORMFIT_DESIGN_SPEC.md",
    ],
    "content_strategy": [
        DESIGN_ROOT / "TRANSFORMFIT_LANDING_PAGE_VNEXT_BLUEPRINT.md",
        DOCS_ROOT / "APP_STORE_LISTING.md",
    ],
    "session_ux": [
        DOCS_ROOT / "WORKOUT_LOGGING_UX_PLAN.md",
    ],
    "ux_research": [
        DESIGN_ROOT / "UX-JOURNEY-MAP.md",
        DOCS_ROOT / "USER-FLOW.md",
        DOCS_ROOT / "USER-FLOW-TEST-SCRIPT.md",
        RESEARCH_ROOT / "REAL_UX_RESEARCH.md",
        RESEARCH_ROOT / "REAL_WORKFLOW_RESEARCH.md",
    ],
    "business_strategy": [
        DESIGN_ROOT / "REDESIGN_PLAN.md",
        DOCS_ROOT / "25X_IMPROVEMENT_PLAN.md",
        DOCS_ROOT / "FEATURE_EXPANSION_PLAN.md",
        DOCS_ROOT / "MASTER_PLAN_PHASE2_PLUS.md",
        DOCS_ROOT / "RESEARCH-GAP-ANALYSIS.md",
        DOCS_ROOT / "ROADMAP.md",
        DOCS_ROOT / "ROADMAP_V2_FULL.md",
        DOCS_ROOT / "TRANSFORMFIT_ORG.md",
    ],
    "user_research": [
        COMPANY_ROOT / "USER_PERSONAS.md",
        DOCS_ROOT / "USER_PANEL.md",
    ],
    "coaching_architecture": [
        DOCS_ROOT / "AI_ARCHITECTURE.md",
        COMPANY_ROOT / "CREWAI_AGENT_PROMPTS.md",
    ],
    "training_research": [
        METHODOLOGY_ROOT / "PROGRAM_PHILOSOPHY.md",
        METHODOLOGY_ROOT / "PROGRAM_FULL_BODY_12WEEK.md",
        METHODOLOGY_ROOT / "PROGRAM_PPL_12WEEK.md",
        METHODOLOGY_ROOT / "PROGRAM_UPPER_LOWER_12WEEK.md",
    ],
    "operational_protocols": [
        DOCS_ROOT / "AUTOMATION_MAP.md",
        COMPANY_ROOT / "ORG_STRUCTURE.md",
        TEAMS_ROOT / "09-transformfit-build-squad.md",
    ],
}


def main() -> int:
    ingestor = MarkdownIngestor()
    total = 0
    for data_type, paths in PATHS.items():
        for path in paths:
            if path.exists():
                total += ingestor.ingest(str(path), company_id=COMPANY_ID, data_type=data_type)
    print({"stored": total, "company_id": COMPANY_ID, "source_root": str(DOCS_ROOT)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
