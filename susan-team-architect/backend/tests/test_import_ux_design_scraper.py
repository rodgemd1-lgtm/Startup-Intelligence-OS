from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from scripts.import_ux_design_scraper import (
    classify_markdown_export,
    parse_pipeline_steps,
    parse_sidepanel_components,
    parse_table_names,
    parse_workflow_phases,
)


def test_parse_pipeline_steps_extracts_ids_and_names() -> None:
    source = """
    { id: 'inject', name: 'Inject Content Script', type: 'content-script' },
    { id: 'tokens', name: 'Design Tokens', type: 'content-script' },
    """
    assert parse_pipeline_steps(source) == [
        ("inject", "Inject Content Script"),
        ("tokens", "Design Tokens"),
    ]


def test_parse_table_names_extracts_table_names() -> None:
    sql = """
    CREATE TABLE projects (
      id UUID PRIMARY KEY
    );
    CREATE TABLE screenshots (
      id UUID PRIMARY KEY
    );
    """
    assert parse_table_names(sql) == ["projects", "screenshots"]


def test_parse_workflow_phases_extracts_phase_metadata() -> None:
    source = """
    discover: {
      id: 'discover',
      name: 'Discover',
      description: 'Research and data gathering',
    },
    deliver: {
      id: 'deliver',
      name: 'Deliver',
      description: 'Package outputs',
    },
    """
    assert parse_workflow_phases(source) == [
        ("discover", "Discover", "Research and data gathering"),
        ("deliver", "Deliver", "Package outputs"),
    ]


def test_parse_sidepanel_components_extracts_component_imports() -> None:
    source = """
    import { Sidebar } from './components/common/Sidebar';
    import { WorkflowPanel } from './components/workflow/WorkflowPanel';
    import { ChatContainer } from './components/chat/ChatContainer';
    """
    assert parse_sidepanel_components(source) == [
        "ChatContainer",
        "Sidebar",
        "WorkflowPanel",
    ]


def test_classify_markdown_export_routes_to_expected_types() -> None:
    assert classify_markdown_export(Path("Acme/CLAUDE.md")) == "studio_templates"
    assert classify_markdown_export(Path("Acme/prompts/master-prompt.md")) == "studio_templates"
    assert classify_markdown_export(Path("Acme/README.md")) == "studio_case_library"
    assert classify_markdown_export(Path("Acme/analysis/research-insights.md")) == "ux_research"
