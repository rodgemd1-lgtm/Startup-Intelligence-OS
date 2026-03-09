"""Unit tests for Decision OS persistence layer."""
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Override root before importing store
_test_dir = tempfile.mkdtemp(prefix="decision-os-test-")
os.environ["DECISION_OS_ROOT"] = _test_dir

# Create minimal .startup-os structure
os.makedirs(os.path.join(_test_dir, ".startup-os", "decisions"), exist_ok=True)
os.makedirs(os.path.join(_test_dir, ".startup-os", "capabilities"), exist_ok=True)
os.makedirs(os.path.join(_test_dir, ".startup-os", "projects"), exist_ok=True)
os.makedirs(os.path.join(_test_dir, ".startup-os", "companies"), exist_ok=True)

from decision_os.models import Decision, Capability, Run, Evidence
from decision_os.store import Store


def test_store_crud():
    store = Store()

    # Create
    d = Decision(title="Test CRUD")
    store.decisions.save(d)
    assert store.decisions.count() >= 1

    # Read
    loaded = store.decisions.get(d.id)
    assert loaded is not None
    assert loaded.title == "Test CRUD"
    assert loaded.id == d.id

    # List
    all_decs = store.decisions.list_all()
    assert any(x.id == d.id for x in all_decs)

    # Delete
    store.decisions.delete(d.id)
    assert store.decisions.get(d.id) is None


def test_store_status():
    store = Store()
    status = store.status()
    assert "decisions" in status
    assert "capabilities" in status
    assert "runs" in status
    assert "evidence" in status


def test_capability_persistence():
    store = Store()
    c = Capability(name="Test Capability", owner="test")
    store.capabilities.save(c)

    loaded = store.capabilities.get(c.id)
    assert loaded is not None
    assert loaded.name == "Test Capability"

    store.capabilities.delete(c.id)


def test_run_persistence():
    store = Store()
    r = Run(trigger="test_run")
    r.add_event("step_1", data={"x": 1})
    store.runs.save(r)

    loaded = store.runs.get(r.id)
    assert loaded is not None
    assert len(loaded.events) == 1
    assert loaded.events[0].step == "step_1"

    store.runs.delete(r.id)


def test_evidence_persistence():
    store = Store()
    e = Evidence(source_url="https://example.com", title="Test Evidence")
    store.evidence.save(e)

    loaded = store.evidence.get(e.id)
    assert loaded is not None
    assert loaded.source_url == "https://example.com"

    store.evidence.delete(e.id)


def cleanup():
    shutil.rmtree(_test_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        test_store_crud()
        test_store_status()
        test_capability_persistence()
        test_run_persistence()
        test_evidence_persistence()
        print("All store tests passed!")
    finally:
        cleanup()
