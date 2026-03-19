"""Tests for the Jake/Claw hybrid control plane."""
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from decision_os.claw_control import ClawControlPlane
from decision_os.models import ActionPacket, SignalEvent, SignalSeverity


def _prepare_root(tmp_path: Path, monkeypatch) -> Path:
    root = tmp_path / "startup-intelligence-os"
    (root / ".startup-os").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("DECISION_OS_ROOT", str(root))
    return root


def test_onboard_seeds_registry_and_profiles(tmp_path, monkeypatch):
    root = _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()

    result = control.onboard(profile_id="work-safe")

    assert result["profile"] == "work-safe"
    registry = yaml.safe_load((root / ".startup-os" / "control-plane" / "claw" / "registry.yaml").read_text())
    assert registry["active_profile"] == "work-safe"
    assert registry["services"]["telegram"]["state"] == "connected"
    assert registry["services"]["github"]["state"] == "connected"
    assert registry["services"]["microsoft-365-direct"]["mode"] == "blocked"
    assert (root / ".startup-os" / "control-plane" / "claw" / "profiles" / "default.yaml").exists()
    assert (root / ".startup-os" / "control-plane" / "claw" / "profiles" / "work-safe.yaml").exists()


def test_sync_promotes_bridge_and_generates_briefs(tmp_path, monkeypatch):
    _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    def fake_run(cmd, timeout):
        joined = " ".join(cmd)
        if joined.startswith("gh auth status"):
            return {"returncode": 0, "stdout": "github.com", "stderr": ""}
        if joined.startswith("pgrep -x Slack"):
            return {"returncode": 0, "stdout": "4242", "stderr": ""}
        if "tell application \"Mail\"" in joined:
            return {"returncode": 0, "stdout": "Oracle Exchange", "stderr": ""}
        if "tell application \"Calendar\"" in joined:
            return {"returncode": 0, "stdout": "Oracle Exchange", "stderr": ""}
        return {"returncode": 1, "stdout": "", "stderr": "unhandled"}

    monkeypatch.setattr(control, "_run", fake_run)

    result = control.sync()
    payload = control.registry_payload()
    services = {item["service"]: item for item in payload["services"]}

    assert any(change["service"] == "slack" for change in result["changes"])
    assert services["slack"]["mode"] == "bridge"
    assert services["slack"]["state"] == "connected"
    assert services["apple-work-mail"]["state"] == "connected"
    assert services["apple-work-calendar"]["state"] == "connected"
    assert "work-inbox-digest.md" in " ".join(result["generated_briefs"])
    assert "work-calendar-digest.md" in " ".join(result["generated_briefs"])
    assert "approval-queue.md" in " ".join(result["generated_briefs"])


def test_sync_accepts_work_calendar_backed_by_exchange_mail(tmp_path, monkeypatch):
    _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    def fake_run(cmd, timeout):
        joined = " ".join(cmd)
        if joined.startswith("gh auth status"):
            return {"returncode": 0, "stdout": "github.com", "stderr": ""}
        if joined.startswith("pgrep -x Slack"):
            return {"returncode": 1, "stdout": "", "stderr": ""}
        if 'tell application "Mail"' in joined:
            return {"returncode": 0, "stdout": "iCloud, Exchange", "stderr": ""}
        if 'tell application "Calendar"' in joined:
            return {"returncode": 0, "stdout": "Work, Home, Family", "stderr": ""}
        return {"returncode": 1, "stdout": "", "stderr": "unhandled"}

    monkeypatch.setattr(control, "_run", fake_run)

    result = control.sync(["apple-work-mail", "apple-work-calendar"])
    payload = control.registry_payload()
    services = {item["service"]: item for item in payload["services"]}

    assert any(change["service"] == "apple-work-calendar" for change in result["changes"])
    assert services["apple-work-mail"]["state"] == "connected"
    assert services["apple-work-calendar"]["state"] == "connected"
    assert "work-calendar-digest.md" in " ".join(result["generated_briefs"])


def test_sync_detects_active_open_remote_desktop_session(tmp_path, monkeypatch):
    _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    def fake_run(cmd, timeout):
        joined = " ".join(cmd)
        if 'tell application "System Events"' in joined and 'process "Genspark"' in joined:
            return {
                "returncode": 0,
                "stdout": "rodgemd1-f06c8559-1084-vm:99 - Genspark Claw - Genspark",
                "stderr": "",
            }
        return {"returncode": 1, "stdout": "", "stderr": "unhandled"}

    monkeypatch.setattr(control, "_run", fake_run)

    result = control.sync(["open-remote-desktop"])
    payload = control.registry_payload()
    services = {item["service"]: item for item in payload["services"]}

    assert any(change["service"] == "open-remote-desktop" for change in result["changes"])
    assert services["open-remote-desktop"]["state"] == "connected"


def test_sync_detects_google_bundle_from_genspark_confirmation(tmp_path, monkeypatch):
    _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    def fake_run(cmd, timeout):
        joined = " ".join(cmd)
        if "google-bundle-probe" in joined:
            return {
                "returncode": 0,
                "stdout": "\n".join(
                    [
                        "Gmail — Logged in",
                        "Google Calendar — Logged in",
                        "Google Drive — Logged in",
                    ]
                ),
                "stderr": "",
            }
        return {"returncode": 1, "stdout": "", "stderr": "unhandled"}

    monkeypatch.setattr(control, "_run", fake_run)

    result = control.sync(["google-bundle"])
    payload = control.registry_payload()
    services = {item["service"]: item for item in payload["services"]}

    assert any(change["service"] == "google-bundle" for change in result["changes"])
    assert services["google-bundle"]["state"] == "connected"


def test_sync_detects_chrome_hosted_open_remote_desktop_session(tmp_path, monkeypatch):
    _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    def fake_run(cmd, timeout):
        joined = " ".join(cmd)
        if 'tell application "System Events"' in joined and 'process "Genspark"' in joined:
            return {"returncode": 0, "stdout": "", "stderr": ""}
        if "open-remote-desktop-probe" in joined:
            return {
                "returncode": 0,
                "stdout": "rodgemd1-f06c8559-1084-vm:99 - Genspark Claw - Memory usage - 66.1 MB",
                "stderr": "",
            }
        return {"returncode": 1, "stdout": "", "stderr": "unhandled"}

    monkeypatch.setattr(control, "_run", fake_run)

    result = control.sync(["open-remote-desktop"])
    payload = control.registry_payload()
    services = {item["service"]: item for item in payload["services"]}

    assert any(change["service"] == "open-remote-desktop" for change in result["changes"])
    assert services["open-remote-desktop"]["state"] == "connected"


def test_sync_detects_playwright_hosted_open_remote_desktop_session(tmp_path, monkeypatch):
    _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    def fake_run(cmd, timeout):
        joined = " ".join(cmd)
        if 'tell application "System Events"' in joined and 'process "Genspark"' in joined:
            return {"returncode": 1, "stdout": "", "stderr": "not running"}
        if "open-remote-desktop-probe" in joined:
            return {"returncode": 1, "stdout": "", "stderr": "no local chrome session"}
        if cmd[0].endswith("playwright_cli.sh") and cmd[1:] == ["tab-list"]:
            return {
                "returncode": 0,
                "stdout": "0: (current) [rodgemd1-f06c8559-1084-vm:99 - Genspark Claw](https://example.test)",
                "stderr": "",
            }
        return {"returncode": 1, "stdout": "", "stderr": "unhandled"}

    monkeypatch.setattr(control, "_run", fake_run)

    result = control.sync(["open-remote-desktop"])
    payload = control.registry_payload()
    services = {item["service"]: item for item in payload["services"]}

    assert any(change["service"] == "open-remote-desktop" for change in result["changes"])
    assert services["open-remote-desktop"]["state"] == "connected"


def test_sync_detects_notion_from_playwright_remote_screenshot(tmp_path, monkeypatch):
    root = _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    screenshot_path = root / ".playwright-cli" / "notion.png"
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot_path.write_bytes(b"fake image")

    def fake_run(cmd, timeout):
        if cmd[0].endswith("playwright_cli.sh") and cmd[1:] == ["screenshot"]:
            return {
                "returncode": 0,
                "stdout": "### Result\n- [Screenshot of viewport](.playwright-cli/notion.png)\n",
                "stderr": "",
            }
        if cmd[:2] == ["swift", "-e"] and str(screenshot_path) in cmd:
            return {
                "returncode": 0,
                "stdout": "\n".join(
                    [
                        "Mike Rodgers's Notion",
                        "notion.so/2cddebb66b1f804bb3ffcf8aa6c43002",
                        "Home",
                        "Private",
                    ]
                ),
                "stderr": "",
            }
        return {"returncode": 1, "stdout": "", "stderr": "unhandled"}

    monkeypatch.setattr(control, "_run", fake_run)

    result = control.sync(["notion"])
    payload = control.registry_payload()
    services = {item["service"]: item for item in payload["services"]}

    assert any(change["service"] == "notion" for change in result["changes"])
    assert services["notion"]["state"] == "connected"


def test_remote_brief_aggregates_alerts_briefs_and_commands(tmp_path, monkeypatch):
    root = _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    brief_path = root / ".startup-os" / "briefs" / "claw" / "work-inbox-digest.md"
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text("# Work Inbox Digest\n\n- Digest ready for review\n", encoding="utf-8")

    monkeypatch.setattr(
        "decision_os.claw_control.collect_signals",
        lambda _store: [
            SignalEvent(
                signal_type="fresh_intel",
                severity=SignalSeverity.info,
                title="Fresh intel is available",
                next_action="Review the latest brief",
            )
        ],
    )
    monkeypatch.setattr(
        "decision_os.claw_control.list_action_packets",
        lambda _store: [ActionPacket(request_text="Summarize Oracle work inbox")],
    )

    payload = control.remote_brief(operator="mike", signal_limit=3, packet_limit=3)

    assert payload["operator"] == "mike"
    assert "telegram" in payload["connectors"]
    assert payload["alerts"][0]["title"] == "Fresh intel is available"
    assert payload["intel"]["action_packets"][0]["request_text"] == "Summarize Oracle work inbox"
    assert payload["intel"]["briefs"][0]["name"] == "work-inbox-digest.md"
    command_names = {item["command"] for item in payload["allowed_remote_commands"]}
    assert {"brief", "status", "sync", "signals"}.issubset(command_names)


def test_remote_command_sync_and_unknown_command(tmp_path, monkeypatch):
    _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    monkeypatch.setattr(
        control,
        "sync",
        lambda services=None: {"services": services or [], "changes": [], "generated_briefs": []},
    )

    sync_result = control.remote_command("sync", ["notion"])
    unknown_result = control.remote_command("do-not-send-email", [])

    assert sync_result["ok"] is True
    assert sync_result["result"]["services"] == ["notion"]
    assert unknown_result["ok"] is False
    assert unknown_result["error"] == "Unsupported remote command."


def test_eject_disables_connector_and_records_log(tmp_path, monkeypatch):
    root = _prepare_root(tmp_path, monkeypatch)
    control = ClawControlPlane()
    control.onboard()

    record = control.eject("slack", "safety hold")
    logs = control.read_logs(limit=10)

    assert record.state.value == "disabled"
    assert record.last_error == "safety hold"
    assert any(event.action == "eject" and event.service == "slack" for event in logs)
    snapshots = list((root / ".startup-os" / "control-plane" / "claw" / "snapshots").glob("registry-*.yaml"))
    assert snapshots
