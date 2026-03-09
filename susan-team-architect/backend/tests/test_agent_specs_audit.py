from pathlib import Path
import json
import subprocess


def test_agent_spec_audit_for_upgraded_agents():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["./.venv/bin/python", "scripts/audit_agent_specs.py"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    findings = json.loads(result.stdout)
    upgraded = {
        "aria-growth",
        "marcus-ux",
        "echo-neuro-design",
        "lens-accessibility",
        "atlas-engineering",
        "nova-ai",
        "coach-exercise-science",
        "freya-behavioral-economics",
        "compass-product",
        "steve-strategy",
    }
    for finding in findings:
        if finding["agent"] in upgraded:
            assert finding["passes"], finding
