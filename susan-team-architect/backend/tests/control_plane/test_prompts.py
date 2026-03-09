from pathlib import Path

from control_plane.prompts import compile_prompt_bundle, render_runtime_prompt


def test_prompt_compiler_includes_operator_grade_sections():
    path = Path(__file__).resolve().parents[3] / "agents" / "landing-page-studio.md"
    bundle = compile_prompt_bundle(path)
    rendered = render_runtime_prompt(bundle)

    assert "5 Whys Protocol" in rendered
    assert "JTBD Frame" in rendered
    assert "Moments of Truth" in rendered
    assert "Science Router" in rendered
    assert "Output Contract" in rendered


def test_susan_prompt_compiler_includes_relational_orchestration_sections():
    path = Path(__file__).resolve().parents[3] / "agents" / "susan.md"
    bundle = compile_prompt_bundle(path)
    rendered = render_runtime_prompt(bundle)

    assert "Cognitive Architecture" in rendered
    assert "5 Whys Protocol" in rendered
    assert "Moments of Truth" in rendered
    assert "Relationship layer" in rendered
    assert "Greet Mike by name when appropriate" in rendered
