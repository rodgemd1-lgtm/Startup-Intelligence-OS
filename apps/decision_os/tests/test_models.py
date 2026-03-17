"""Unit tests for Decision OS domain models."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from decision_os.models import (
    Decision, Capability, Project, Company, Run, Session, Artifact, Evidence,
    ScoredOption, DebateEntry, OutputContract, DepartmentPack, SignalEvent,
    ActionPacket, GraphLink, DecisionRequirement, SignalSeverity,
    DecisionStatus, CapabilityMaturity, ProjectStatus, CompanyStage, RunStatus,
)


def test_decision_has_deterministic_id():
    d = Decision(title="Test decision")
    assert d.id.startswith("dec-")
    assert len(d.id) > 4
    assert d.status == DecisionStatus.draft
    assert d.created_at


def test_decision_id_is_stable():
    d1 = Decision(title="Same title", created_at="2026-01-01T00:00:00Z")
    d2 = Decision(title="Same title", created_at="2026-01-01T00:00:00Z")
    assert d1.id == d2.id


def test_capability_has_id():
    c = Capability(name="Test capability")
    assert c.id.startswith("cap-")
    assert c.maturity == CapabilityMaturity.nascent


def test_project_has_id():
    p = Project(name="Test project")
    assert p.id.startswith("proj-")
    assert p.status == ProjectStatus.planning


def test_company_has_id():
    c = Company(name="Test Co")
    assert c.id.startswith("co-")
    assert c.stage == CompanyStage.concept


def test_run_lifecycle():
    r = Run(trigger="test")
    assert r.id.startswith("run-")
    assert r.status == RunStatus.running

    evt = r.add_event("step_1", data={"key": "val"}, confidence=0.8)
    assert evt.step == "step_1"
    assert evt.confidence == 0.8
    assert abs(evt.uncertainty - 0.2) < 0.01
    assert len(r.events) == 1

    output = OutputContract(
        recommendation="Do X",
        counter_recommendation="Don't do X",
        why_now="Because Y",
        failure_modes=["Z could fail"],
        next_experiment="Test Z",
    )
    r.complete(output)
    assert r.status == RunStatus.completed
    assert r.completed_at
    assert r.output.recommendation == "Do X"


def test_scored_option():
    opt = ScoredOption(title="Option A", description="Do something")
    assert opt.title == "Option A"
    assert opt.total_score == 0.0


def test_debate_entry():
    de = DebateEntry(mode="builder_pov", argument="This will work because...")
    assert de.mode == "builder_pov"
    assert de.confidence == 0.5


def test_evidence():
    ev = Evidence(source_url="https://example.com", title="Test")
    assert ev.id.startswith("ev-")
    assert ev.confidence == 0.5


def test_session():
    s = Session(operator="mike")
    assert s.id.startswith("sess-")
    assert s.operator == "mike"


def test_artifact():
    a = Artifact(name="test artifact")
    assert a.id.startswith("art-")


def test_department_pack_defaults():
    pack = DepartmentPack(
        name="Founder Decision Room",
        owner_agent="jake",
        decision_requirement=DecisionRequirement.required,
    )
    assert pack.id.startswith("dept-")
    assert pack.decision_requirement == DecisionRequirement.required


def test_action_packet_defaults():
    packet = ActionPacket(request_text="Help me build a project")
    assert packet.id.startswith("ap-")
    assert packet.status == "proposed"


def test_signal_event_defaults():
    signal = SignalEvent(signal_type="test", title="Test signal")
    assert signal.id.startswith("sig-")
    assert signal.severity == SignalSeverity.warning


def test_graph_link_has_deterministic_id():
    link = GraphLink(source_id="a", target_id="b", relation="depends_on")
    assert link.id.startswith("link-")


if __name__ == "__main__":
    test_decision_has_deterministic_id()
    test_decision_id_is_stable()
    test_capability_has_id()
    test_project_has_id()
    test_company_has_id()
    test_run_lifecycle()
    test_scored_option()
    test_debate_entry()
    test_evidence()
    test_session()
    test_artifact()
    print("All model tests passed!")
