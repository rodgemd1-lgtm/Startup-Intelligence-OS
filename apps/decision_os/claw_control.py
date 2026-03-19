"""Jake/Claw hybrid control plane for connector state and bridge operations."""
from __future__ import annotations

import re
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .models import _now
from .operator import collect_signals, list_action_packets
from .store import Store, startup_os_dir


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _truncate(value: str, limit: int = 44) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def _has_exchange_token(value: str) -> bool:
    lowered = value.lower()
    return any(token in lowered for token in ("oracle", "cerner", "exchange"))


def _calendar_names(value: str) -> list[str]:
    return [item.strip().lower() for item in value.split(",") if item.strip()]


def _has_all_tokens(value: str, tokens: list[str]) -> bool:
    lowered = value.lower()
    return all(token.lower() in lowered for token in tokens)


def _path_from_markdown_link(value: str, prefix: str) -> str:
    pattern = re.compile(rf"\(({re.escape(prefix)}[^)]+)\)")
    match = pattern.search(value)
    return match.group(1) if match else ""


def _preview_text(value: str, limit: int = 220) -> str:
    compact = " ".join(line.strip() for line in value.splitlines() if line.strip())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


class ConnectorMode(str, Enum):
    native = "native"
    bridge = "bridge"
    blocked = "blocked"


class ConnectorState(str, Enum):
    connected = "connected"
    pending = "pending"
    failed = "failed"
    disabled = "disabled"


class ConnectorRecord(BaseModel):
    name: str
    mode: ConnectorMode
    state: ConnectorState
    auth_source: str
    scope: list[str] = Field(default_factory=list)
    last_verified_at: str = ""
    last_error: str = ""


class ConnectorRegistry(BaseModel):
    version: int = 1
    active_profile: str = "default"
    updated_at: str = Field(default_factory=_now)
    services: dict[str, ConnectorRecord] = Field(default_factory=dict)


class ControlProfile(BaseModel):
    id: str
    name: str
    description: str
    connector_defaults: dict[str, str] = Field(default_factory=dict)
    policy: dict[str, Any] = Field(default_factory=dict)


class ControlEvent(BaseModel):
    timestamp: str = Field(default_factory=_now)
    level: str = "info"
    action: str
    service: str = ""
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ClawControlPlane:
    """Persistent registry and operator surfaces for the Jake/Claw hybrid stack."""

    def __init__(self) -> None:
        self.startup_os = startup_os_dir()
        self.control_root = self.startup_os / "control-plane" / "claw"
        self.profile_dir = self.control_root / "profiles"
        self.snapshot_dir = self.control_root / "snapshots"
        self.registry_path = self.control_root / "registry.yaml"
        self.log_path = self.control_root / "events.jsonl"
        self.briefs_dir = self.startup_os / "briefs" / "claw"

    def onboard(self, profile_id: str = "default", force: bool = False) -> dict[str, Any]:
        self._ensure_layout()
        profiles = self._base_profiles()
        if profile_id not in profiles:
            raise ValueError(f"Unknown profile: {profile_id}")
        registry_exists = self.registry_path.exists()

        written_profiles: list[str] = []
        for pid, profile in profiles.items():
            path = self.profile_dir / f"{pid}.yaml"
            if force or not path.exists():
                path.write_text(
                    yaml.safe_dump(profile.model_dump(mode="json"), sort_keys=False, allow_unicode=True),
                    encoding="utf-8",
                )
                written_profiles.append(str(path.relative_to(self.startup_os.parent)))

        registry = self._load_registry()
        registry.active_profile = profile_id
        registry.updated_at = _now()
        for service_id, record in self._seed_services().items():
            registry.services.setdefault(service_id, record)
        self._save_registry(registry, snapshot=force or registry_exists)
        self._append_event(
            "info",
            "onboard",
            message=f"Claw control plane onboarded with profile '{profile_id}'.",
            details={"profile": profile_id, "force": force},
        )

        return {
            "profile": profile_id,
            "registry": str(self.registry_path.relative_to(self.startup_os.parent)),
            "profiles_written": written_profiles,
            "service_count": len(registry.services),
            "logs": str(self.log_path.relative_to(self.startup_os.parent)),
        }

    def sync(self, service_names: list[str] | None = None) -> dict[str, Any]:
        self._ensure_layout()
        registry = self._load_registry()
        target_names = service_names or list(registry.services.keys())
        before = registry.model_dump(mode="json")
        changes: list[dict[str, str]] = []

        for service_name in target_names:
            record = registry.services.get(service_name)
            if record is None:
                raise ValueError(f"Unknown service: {service_name}")
            if record.state == ConnectorState.disabled:
                self._append_event(
                    "warning",
                    "sync-skipped",
                    service=service_name,
                    message="Skipped sync because connector is disabled.",
                )
                continue

            update = self._probe(service_name, record)
            if not update:
                continue

            old_mode = record.mode.value
            old_state = record.state.value
            old_error = record.last_error

            meta = {"verified", "clear_error"}
            for field, value in update.items():
                if field in meta:
                    continue
                setattr(record, field, value)

            if update.get("verified", False):
                record.last_verified_at = _now()
            if update.get("clear_error", False):
                record.last_error = ""

            registry.services[service_name] = record
            registry.updated_at = _now()

            if (
                record.mode.value != old_mode
                or record.state.value != old_state
                or record.last_error != old_error
            ):
                changes.append(
                    {
                        "service": service_name,
                        "mode": f"{old_mode}->{record.mode.value}",
                        "state": f"{old_state}->{record.state.value}",
                    }
                )

        if registry.model_dump(mode="json") != before:
            self._save_registry(registry, snapshot=True)

        generated_briefs = self._refresh_briefs(registry)
        self._append_event(
            "info",
            "sync",
            message="Claw control-plane sync completed.",
            details={
                "services": target_names,
                "changes": changes,
                "generated_briefs": generated_briefs,
            },
        )
        return {
            "services": target_names,
            "changes": changes,
            "generated_briefs": generated_briefs,
        }

    def eject(self, service_name: str, reason: str) -> ConnectorRecord:
        self._ensure_layout()
        registry = self._load_registry()
        record = registry.services.get(service_name)
        if record is None:
            raise ValueError(f"Unknown service: {service_name}")

        self._save_registry(registry, snapshot=True)

        record.state = ConnectorState.disabled
        record.last_error = reason
        record.last_verified_at = _now()
        registry.services[service_name] = record
        registry.updated_at = _now()
        self._save_registry(registry, snapshot=False)
        self._append_event(
            "warning",
            "eject",
            service=service_name,
            message=f"Connector disabled: {reason}",
        )
        return record

    def registry_payload(self) -> dict[str, Any]:
        registry = self._load_registry()
        services = []
        for service_name in sorted(registry.services):
            record = registry.services[service_name]
            services.append(
                {
                    "service": service_name,
                    "mode": record.mode.value,
                    "state": record.state.value,
                    "auth_source": record.auth_source,
                    "scope": record.scope,
                    "last_verified_at": record.last_verified_at,
                    "last_error": record.last_error,
                }
            )
        return {
            "active_profile": registry.active_profile,
            "updated_at": registry.updated_at,
            "registry_path": str(self.registry_path.relative_to(self.startup_os.parent)),
            "services": services,
        }

    def format_status_table(self) -> str:
        payload = self.registry_payload()
        rows = payload["services"]
        columns = [
            ("service", 24),
            ("mode", 8),
            ("state", 10),
            ("auth_source", 28),
            ("scope", 34),
            ("last_verified_at", 20),
            ("last_error", 36),
        ]
        lines = [
            "jake: claw control plane status",
            f"  active_profile: {payload['active_profile']}",
            f"  registry: {payload['registry_path']}",
            "",
        ]

        header = "  ".join(label.ljust(width) for label, width in columns)
        divider = "  ".join("-" * width for _, width in columns)
        lines.append(header)
        lines.append(divider)
        for row in rows:
            row_values = {
                **row,
                "scope": ",".join(row["scope"]),
                "last_error": row["last_error"] or "-",
                "last_verified_at": row["last_verified_at"] or "-",
            }
            lines.append(
                "  ".join(
                    _truncate(str(row_values[label]), width).ljust(width) for label, width in columns
                )
            )
        return "\n".join(lines)

    def read_logs(self, limit: int = 20) -> list[ControlEvent]:
        if not self.log_path.exists():
            return []
        events: list[ControlEvent] = []
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(ControlEvent.model_validate_json(line))
            except Exception:
                continue
        return events[-limit:]

    def format_logs(self, limit: int = 20) -> str:
        events = self.read_logs(limit=limit)
        lines = [
            "jake: claw control plane logs",
            f"  log_path: {self.log_path.relative_to(self.startup_os.parent)}",
            "",
        ]
        if not events:
            lines.append("  (no events yet)")
            return "\n".join(lines)

        for event in events:
            service = f" [{event.service}]" if event.service else ""
            lines.append(
                f"  {event.timestamp} {event.level.upper():<7} {event.action}{service} - {event.message}"
            )
        return "\n".join(lines)

    def remote_command_catalog(self) -> list[dict[str, str]]:
        return [
            {
                "command": "brief",
                "description": "Summarize current alerts, briefs, action packets, and connector health.",
                "approval": "none",
            },
            {
                "command": "status",
                "description": "Show connector registry and verification state.",
                "approval": "none",
            },
            {
                "command": "sync",
                "description": "Refresh connector probes and regenerate work briefs.",
                "approval": "none",
            },
            {
                "command": "context",
                "description": "Show active workspace, company, project, and branch context.",
                "approval": "none",
            },
            {
                "command": "signals",
                "description": "List current alerts and attention-needed signals.",
                "approval": "none",
            },
            {
                "command": "action-packets",
                "description": "List queued structured asks and execution packets.",
                "approval": "none",
            },
            {
                "command": "briefs",
                "description": "Read the latest generated work brief previews.",
                "approval": "none",
            },
            {
                "command": "remote-desktop-status",
                "description": "Check whether the interactive remote desktop bridge is ready.",
                "approval": "none",
            },
        ]

    def remote_brief(self, operator: str = "mike", signal_limit: int = 5, packet_limit: int = 5) -> dict[str, Any]:
        registry = self.registry_payload()
        store = Store()
        context = store.context()
        status = store.status()
        services = registry["services"]
        connected = [service["service"] for service in services if service["state"] == "connected"]
        attention = [
            {
                "service": service["service"],
                "state": service["state"],
                "last_error": service["last_error"],
            }
            for service in services
            if service["state"] in {"pending", "failed"}
        ]
        telegram = next((service for service in services if service["service"] == "telegram"), None)
        remote_desktop = next(
            (service for service in services if service["service"] == "open-remote-desktop"),
            None,
        )
        signals = [
            signal.model_dump(mode="json")
            for signal in collect_signals(store)[: max(signal_limit, 0)]
        ]
        packets = [
            packet.model_dump(mode="json")
            for packet in list_action_packets(store)[: max(packet_limit, 0)]
        ]

        return {
            "operator": operator,
            "generated_at": _now(),
            "workspace": {
                "name": context.get("name", "startup-intelligence-os"),
                "mode": context.get("mode", ""),
                "active_company": context.get("active_company", ""),
                "active_project": context.get("active_project", ""),
                "active_decision": context.get("active_decision", ""),
                "active_branch": context.get("active_branch", ""),
            },
            "connectors": {
                "connected": connected,
                "attention_needed": attention,
                "telegram": telegram,
                "remote_desktop": remote_desktop,
            },
            "alerts": signals,
            "intel": {
                "action_packets": packets,
                "briefs": self._brief_documents(),
            },
            "status": status,
            "allowed_remote_commands": self.remote_command_catalog(),
        }

    def format_remote_brief(self, operator: str = "mike", signal_limit: int = 5, packet_limit: int = 5) -> str:
        payload = self.remote_brief(operator=operator, signal_limit=signal_limit, packet_limit=packet_limit)
        lines = [
            "jake: claw remote brief",
            f"  operator: {payload['operator']}",
            f"  generated_at: {payload['generated_at']}",
            "",
            "Workspace:",
            f"  name: {payload['workspace']['name']}",
            f"  company: {payload['workspace']['active_company'] or '-'}",
            f"  project: {payload['workspace']['active_project'] or '-'}",
            f"  decision: {payload['workspace']['active_decision'] or '-'}",
            f"  branch: {payload['workspace']['active_branch'] or '-'}",
            "",
            "Connectors:",
            f"  connected: {', '.join(payload['connectors']['connected']) or '-'}",
        ]
        attention = payload["connectors"]["attention_needed"]
        if attention:
            lines.append("  attention:")
            for item in attention:
                detail = f" ({item['last_error']})" if item["last_error"] else ""
                lines.append(f"    - {item['service']}: {item['state']}{detail}")
        else:
            lines.append("  attention: none")

        lines.append("")
        lines.append("Alerts:")
        if payload["alerts"]:
            for signal in payload["alerts"]:
                lines.append(
                    f"  - [{signal['severity']}] {signal['title']} — {signal.get('next_action', '') or signal.get('description', '')}"
                )
        else:
            lines.append("  - none")

        lines.append("")
        lines.append("Intel:")
        if payload["intel"]["briefs"]:
            lines.append("  briefs:")
            for brief in payload["intel"]["briefs"]:
                lines.append(f"    - {brief['name']}: {brief['preview']}")
        else:
            lines.append("  briefs: none")
        if payload["intel"]["action_packets"]:
            lines.append("  action_packets:")
            for packet in payload["intel"]["action_packets"]:
                lines.append(f"    - {packet['request_text']}")
        else:
            lines.append("  action_packets: none")

        lines.append("")
        lines.append("Remote Commands:")
        for command in payload["allowed_remote_commands"]:
            lines.append(f"  - {command['command']}: {command['description']}")
        return "\n".join(lines)

    def remote_command(self, command: str, args: list[str] | None = None) -> dict[str, Any]:
        parsed_args = list(args or [])
        store = Store()
        commands = {
            "brief": lambda: self.remote_brief(),
            "status": self.registry_payload,
            "sync": lambda: self.sync(parsed_args or None),
            "context": store.context,
            "signals": lambda: [
                signal.model_dump(mode="json")
                for signal in collect_signals(store)
            ],
            "action-packets": lambda: [
                packet.model_dump(mode="json")
                for packet in list_action_packets(store)
            ],
            "briefs": self._brief_documents,
            "remote-desktop-status": lambda: next(
                (
                    service
                    for service in self.registry_payload()["services"]
                    if service["service"] == "open-remote-desktop"
                ),
                {},
            ),
        }
        runner = commands.get(command)
        if runner is None:
            return {
                "ok": False,
                "command": command,
                "args": parsed_args,
                "error": "Unsupported remote command.",
                "allowed_remote_commands": self.remote_command_catalog(),
            }
        result = runner()
        self._append_event(
            "info",
            "remote-command",
            message=f"Executed remote command '{command}'.",
            details={"command": command, "args": parsed_args},
        )
        return {
            "ok": True,
            "command": command,
            "args": parsed_args,
            "result": result,
        }

    def _ensure_layout(self) -> None:
        for path in (
            self.control_root,
            self.profile_dir,
            self.snapshot_dir,
            self.briefs_dir,
        ):
            _ensure_dir(path)

    def _base_profiles(self) -> dict[str, ControlProfile]:
        return {
            "default": ControlProfile(
                id="default",
                name="default",
                description="Personal and productivity tools run through native connectors where possible.",
                connector_defaults={
                    "github": "native",
                    "google-bundle": "native",
                    "slack": "native",
                    "notion": "native",
                    "box": "native",
                    "zoom": "native",
                    "open-remote-desktop": "bridge",
                },
                policy={
                    "work_surfaces": "draft-only",
                    "send_requires_approval": True,
                    "meeting_changes_require_approval": True,
                },
            ),
            "work-safe": ControlProfile(
                id="work-safe",
                name="work-safe",
                description="Bridge-first work profile for Oracle mail/calendar and desktop-only surfaces.",
                connector_defaults={
                    "apple-work-mail": "bridge",
                    "apple-work-calendar": "bridge",
                    "microsoft-365-direct": "blocked",
                },
                policy={
                    "work_surfaces": "draft-only",
                    "allow_external_forwarding": False,
                    "send_requires_approval": True,
                    "meeting_changes_require_approval": True,
                },
            ),
        }

    def _seed_services(self) -> dict[str, ConnectorRecord]:
        now = _now()
        return {
            "telegram": ConnectorRecord(
                name="telegram",
                mode=ConnectorMode.native,
                state=ConnectorState.connected,
                auth_source="genspark-telegram-bot",
                scope=["read", "draft", "notify", "remote-command"],
                last_verified_at=now,
            ),
            "github": ConnectorRecord(
                name="github",
                mode=ConnectorMode.native,
                state=ConnectorState.connected,
                auth_source="genspark-github-pat",
                scope=["read-repos", "clone", "analyze", "draft-patches"],
                last_verified_at=now,
            ),
            "google-bundle": ConnectorRecord(
                name="google-bundle",
                mode=ConnectorMode.native,
                state=ConnectorState.pending,
                auth_source="genspark-google-oauth",
                scope=["gmail-read", "calendar-read", "drive-read", "draft"],
            ),
            "slack": ConnectorRecord(
                name="slack",
                mode=ConnectorMode.native,
                state=ConnectorState.pending,
                auth_source="genspark-slack-oauth",
                scope=["read", "draft", "notify"],
            ),
            "notion": ConnectorRecord(
                name="notion",
                mode=ConnectorMode.native,
                state=ConnectorState.pending,
                auth_source="genspark-notion-oauth",
                scope=["read", "write-notes", "draft"],
            ),
            "box": ConnectorRecord(
                name="box",
                mode=ConnectorMode.native,
                state=ConnectorState.pending,
                auth_source="genspark-box-oauth",
                scope=["read", "search", "sync"],
            ),
            "zoom": ConnectorRecord(
                name="zoom",
                mode=ConnectorMode.native,
                state=ConnectorState.pending,
                auth_source="genspark-zoom-oauth",
                scope=["read-meetings", "prep", "draft"],
            ),
            "open-remote-desktop": ConnectorRecord(
                name="open-remote-desktop",
                mode=ConnectorMode.bridge,
                state=ConnectorState.pending,
                auth_source="genspark-vnc-surface",
                scope=["remote-access", "session-control"],
            ),
            "apple-work-mail": ConnectorRecord(
                name="apple-work-mail",
                mode=ConnectorMode.bridge,
                state=ConnectorState.pending,
                auth_source="macos-internet-accounts-exchange",
                scope=["read", "search", "summarize", "draft"],
            ),
            "apple-work-calendar": ConnectorRecord(
                name="apple-work-calendar",
                mode=ConnectorMode.bridge,
                state=ConnectorState.pending,
                auth_source="macos-internet-accounts-exchange",
                scope=["read", "summarize", "draft"],
            ),
            "microsoft-365-direct": ConnectorRecord(
                name="microsoft-365-direct",
                mode=ConnectorMode.blocked,
                state=ConnectorState.failed,
                auth_source="oracle-tenant-policy",
                scope=["mail-read", "calendar-read"],
                last_verified_at=now,
                last_error="Oracle blocks third-party Microsoft 365 consent.",
            ),
        }

    def _load_registry(self) -> ConnectorRegistry:
        if not self.registry_path.exists():
            registry = ConnectorRegistry(services=self._seed_services())
            self._save_registry(registry, snapshot=False)
            return registry
        raw = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
        return ConnectorRegistry.model_validate(raw)

    def _save_registry(self, registry: ConnectorRegistry, snapshot: bool) -> None:
        self._ensure_layout()
        registry.updated_at = _now()
        if snapshot and self.registry_path.exists():
            stamp = registry.updated_at.replace(":", "-")
            snapshot_path = self.snapshot_dir / f"registry-{stamp}.yaml"
            shutil.copy2(self.registry_path, snapshot_path)
        self.registry_path.write_text(
            yaml.safe_dump(registry.model_dump(mode="json"), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    def _append_event(
        self,
        level: str,
        action: str,
        message: str,
        service: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        self._ensure_layout()
        event = ControlEvent(
            level=level,
            action=action,
            service=service,
            message=message,
            details=details or {},
        )
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json() + "\n")

    def _probe(self, service_name: str, record: ConnectorRecord) -> dict[str, Any]:
        if service_name == "google-bundle":
            return self._probe_google_bundle(record)
        if service_name == "github":
            return self._probe_github()
        if service_name == "slack":
            return self._probe_slack(record)
        if service_name == "apple-work-mail":
            return self._probe_apple_mail(record)
        if service_name == "apple-work-calendar":
            return self._probe_apple_calendar(record)
        if service_name == "notion":
            return self._probe_notion(record)
        if service_name == "open-remote-desktop":
            return self._probe_open_remote_desktop(record)
        if service_name == "microsoft-365-direct":
            return {
                "mode": ConnectorMode.blocked,
                "state": ConnectorState.failed,
                "last_error": "Oracle blocks third-party Microsoft 365 consent.",
                "verified": True,
            }
        return {}

    def _probe_google_bundle(self, record: ConnectorRecord) -> dict[str, Any]:
        result = self._genspark_google_confirmation_result()
        if result["returncode"] == 0 and _has_all_tokens(
            result["stdout"],
            ["Gmail", "Google Calendar", "Google Drive", "Logged in"],
        ):
            self._append_event(
                "info",
                "probe",
                service="google-bundle",
                message="Genspark confirmed Gmail, Calendar, and Drive are logged in.",
            )
            return {
                "mode": ConnectorMode.native,
                "state": ConnectorState.connected,
                "clear_error": True,
                "verified": True,
            }
        if record.state != ConnectorState.connected:
            return {
                "mode": record.mode,
                "state": ConnectorState.pending,
                "last_error": "Genspark has not yet confirmed Gmail, Calendar, and Drive from the shared browser session.",
            }
        return {}

    def _probe_github(self) -> dict[str, Any]:
        result = self._run(["gh", "auth", "status"], timeout=8)
        if result["returncode"] == 0:
            self._append_event(
                "info",
                "probe",
                service="github",
                message="Verified GitHub auth via gh CLI.",
            )
            return {
                "mode": ConnectorMode.native,
                "state": ConnectorState.connected,
                "clear_error": True,
                "verified": True,
            }
        self._append_event(
            "warning",
            "probe",
            service="github",
            message="gh CLI auth probe unavailable; preserving prior verified GitHub state.",
            details={"stderr": result["stderr"]},
        )
        return {}

    def _probe_slack(self, record: ConnectorRecord) -> dict[str, Any]:
        result = self._run(["pgrep", "-x", "Slack"], timeout=5)
        if result["returncode"] == 0:
            self._append_event(
                "info",
                "probe",
                service="slack",
                message="Slack desktop session detected; promoting connector to bridge mode.",
            )
            return {
                "mode": ConnectorMode.bridge,
                "state": ConnectorState.connected,
                "auth_source": "local-slack-session",
                "clear_error": True,
                "verified": True,
            }
        if record.state != ConnectorState.connected:
            return {
                "mode": record.mode,
                "state": ConnectorState.pending,
                "last_error": "Slack bridge not detected; native connector still pending auth.",
            }
        return {}

    def _probe_apple_mail(self, record: ConnectorRecord) -> dict[str, Any]:
        result = self._mail_accounts_result()
        if result["returncode"] != 0:
            return {
                "mode": record.mode,
                "state": ConnectorState.pending,
                "last_error": "Apple Mail probe unavailable or blocked by Automation permissions; Exchange account not yet verified.",
            }
        if _has_exchange_token(result["stdout"]):
            self._append_event(
                "info",
                "probe",
                service="apple-work-mail",
                message="Apple Mail reports a work Exchange-style account.",
            )
            return {
                "mode": ConnectorMode.bridge,
                "state": ConnectorState.connected,
                "clear_error": True,
                "verified": True,
            }
        return {
            "mode": record.mode,
            "state": ConnectorState.pending,
            "last_error": "No Oracle/Exchange account detected in Apple Mail.",
        }

    def _probe_apple_calendar(self, record: ConnectorRecord) -> dict[str, Any]:
        script = (
            'tell application "Calendar"\n'
            "  set oldDelims to AppleScript's text item delimiters\n"
            '  set AppleScript\'s text item delimiters to ", "\n'
            '  set calendarNames to name of every calendar\n'
            '  set joinedNames to calendarNames as text\n'
            "  set AppleScript's text item delimiters to oldDelims\n"
            '  return joinedNames\n'
            'end tell\n'
        )
        result = self._run(["osascript", "-e", script], timeout=4)
        if result["returncode"] != 0:
            return {
                "mode": record.mode,
                "state": ConnectorState.pending,
                "last_error": "Apple Calendar probe unavailable or blocked by Automation permissions; Exchange calendar not yet verified.",
            }
        if _has_exchange_token(result["stdout"]):
            self._append_event(
                "info",
                "probe",
                service="apple-work-calendar",
                message="Apple Calendar reports an Exchange-style work calendar.",
            )
            return {
                "mode": ConnectorMode.bridge,
                "state": ConnectorState.connected,
                "clear_error": True,
                "verified": True,
            }

        # Some Apple Calendar setups expose a user-facing "Work" calendar even when the
        # backing source name is only discoverable via Mail's Exchange account metadata.
        mail_result = self._mail_accounts_result()
        names = _calendar_names(result["stdout"])
        if mail_result["returncode"] == 0 and _has_exchange_token(mail_result["stdout"]):
            if any(name == "work" or name.startswith("work ") or " work" in name for name in names):
                self._append_event(
                    "info",
                    "probe",
                    service="apple-work-calendar",
                    message="Apple Calendar reports a Work calendar alongside an Exchange mail account.",
                )
                return {
                    "mode": ConnectorMode.bridge,
                    "state": ConnectorState.connected,
                    "clear_error": True,
                    "verified": True,
                }
        return {
            "mode": record.mode,
            "state": ConnectorState.pending,
            "last_error": "No Oracle/Exchange calendar source detected in Apple Calendar.",
        }

    def _probe_open_remote_desktop(self, record: ConnectorRecord) -> dict[str, Any]:
        script = (
            'tell application "System Events"\n'
            '  tell process "Genspark"\n'
            "    set oldDelims to AppleScript's text item delimiters\n"
            '    set AppleScript\'s text item delimiters to ", "\n'
            '    set windowNames to name of every window\n'
            '    set joinedNames to windowNames as text\n'
            "    set AppleScript's text item delimiters to oldDelims\n"
            '    return joinedNames\n'
            '  end tell\n'
            'end tell\n'
        )
        result = self._run(["osascript", "-e", script], timeout=4)
        lowered = result["stdout"].lower() if result["returncode"] == 0 else ""
        if "genspark claw" in lowered and "-vm:" in lowered:
            self._append_event(
                "info",
                "probe",
                service="open-remote-desktop",
                message="Detected active Genspark remote desktop session.",
            )
            return {
                "mode": ConnectorMode.bridge,
                "state": ConnectorState.connected,
                "clear_error": True,
                "verified": True,
            }

        chrome_result = self._chrome_genspark_remote_result()
        chrome_lowered = chrome_result["stdout"].lower() if chrome_result["returncode"] == 0 else ""
        if "genspark claw" in chrome_lowered and "-vm:" in chrome_lowered:
            self._append_event(
                "info",
                "probe",
                service="open-remote-desktop",
                message="Detected active Chrome-hosted Genspark remote desktop session.",
            )
            return {
                "mode": ConnectorMode.bridge,
                "state": ConnectorState.connected,
                "clear_error": True,
                "verified": True,
            }

        playwright_result = self._playwright_cli_result(["tab-list"], timeout=8)
        playwright_lowered = playwright_result["stdout"].lower() if playwright_result["returncode"] == 0 else ""
        if "genspark claw" in playwright_lowered and "-vm:" in playwright_lowered:
            self._append_event(
                "info",
                "probe",
                service="open-remote-desktop",
                message="Detected active Playwright-hosted Genspark remote desktop session.",
            )
            return {
                "mode": ConnectorMode.bridge,
                "state": ConnectorState.connected,
                "clear_error": True,
                "verified": True,
            }

        if (
            result["returncode"] != 0
            and chrome_result["returncode"] != 0
            and playwright_result["returncode"] != 0
        ):
            return {
                "mode": record.mode,
                "state": ConnectorState.pending,
                "last_error": "Genspark remote desktop probe unavailable; active VM session not yet verified.",
            }
        return {
            "mode": record.mode,
            "state": ConnectorState.pending,
            "last_error": "No active Genspark remote desktop window detected.",
        }

    def _probe_notion(self, record: ConnectorRecord) -> dict[str, Any]:
        screenshot_result = self._playwright_cli_result(["screenshot"], timeout=12)
        if screenshot_result["returncode"] == 0:
            relative_path = _path_from_markdown_link(screenshot_result["stdout"], ".playwright-cli/")
            if relative_path:
                image_path = self.startup_os.parent / relative_path
                ocr_result = self._ocr_image_text_result(image_path)
                if ocr_result["returncode"] == 0:
                    recognized = ocr_result["stdout"]
                    if any(
                        _has_all_tokens(recognized, tokens)
                        for tokens in (
                            ["notion.so/", "mike rogers", "notion"],
                            ["notion.so/", "home", "private"],
                            ["notion - google chrome", "mike rogers", "notion"],
                        )
                    ):
                        self._append_event(
                            "info",
                            "probe",
                            service="notion",
                            message="Detected a signed-in Notion workspace in the shared remote browser session.",
                        )
                        return {
                            "mode": ConnectorMode.native,
                            "state": ConnectorState.connected,
                            "clear_error": True,
                            "verified": True,
                        }
                    if record.state == ConnectorState.connected:
                        return {}
                    return {
                        "mode": record.mode,
                        "state": ConnectorState.pending,
                        "last_error": "Notion workspace not yet visible in the shared remote browser session.",
                    }
        if record.state == ConnectorState.connected:
            return {}
        return {
            "mode": record.mode,
            "state": ConnectorState.pending,
            "last_error": "Notion probe unavailable; shared remote browser session not yet verified.",
        }

    def _refresh_briefs(self, registry: ConnectorRegistry) -> list[str]:
        generated: list[str] = []
        inbox = registry.services.get("apple-work-mail")
        calendar = registry.services.get("apple-work-calendar")
        if inbox and inbox.state == ConnectorState.connected:
            path = self.briefs_dir / "work-inbox-digest.md"
            path.write_text(
                "\n".join(
                    [
                        "# Work Inbox Digest",
                        "",
                        "- Status: connected through Apple Exchange local bridge",
                        "- Next step: implement mailbox summarization run against the verified account",
                        "- Policy: draft-only; send requires approval",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            generated.append(str(path.relative_to(self.startup_os.parent)))
        if calendar and calendar.state == ConnectorState.connected:
            cal_path = self.briefs_dir / "work-calendar-digest.md"
            cal_path.write_text(
                "\n".join(
                    [
                        "# Work Calendar Digest",
                        "",
                        "- Status: connected through Apple Exchange local bridge",
                        "- Next step: generate day-of briefing and meeting prep notes",
                        "- Policy: draft-only; meeting changes require approval",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            generated.append(str(cal_path.relative_to(self.startup_os.parent)))

            queue_path = self.briefs_dir / "approval-queue.md"
            queue_path.write_text(
                "\n".join(
                    [
                        "# Approval Queue",
                        "",
                        "- No approval-gated items queued yet.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            generated.append(str(queue_path.relative_to(self.startup_os.parent)))
        return generated

    def _run(self, cmd: list[str], timeout: int) -> dict[str, Any]:
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return {
                "returncode": completed.returncode,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
            }
        except FileNotFoundError:
            return {"returncode": 127, "stdout": "", "stderr": f"Missing command: {cmd[0]}"}
        except subprocess.TimeoutExpired:
            return {"returncode": 124, "stdout": "", "stderr": f"Timed out: {' '.join(cmd)}"}

    def _brief_documents(self) -> list[dict[str, str]]:
        docs: list[dict[str, str]] = []
        for path in sorted(self.briefs_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            docs.append(
                {
                    "name": path.name,
                    "path": str(path.relative_to(self.startup_os.parent)),
                    "preview": _preview_text(text),
                }
            )
        return docs

    def _mail_accounts_result(self) -> dict[str, Any]:
        script = (
            'tell application "Mail"\n'
            "  set oldDelims to AppleScript's text item delimiters\n"
            '  set AppleScript\'s text item delimiters to ", "\n'
            '  set accountNames to name of every account\n'
            '  set joinedNames to accountNames as text\n'
            "  set AppleScript's text item delimiters to oldDelims\n"
            '  return joinedNames\n'
            'end tell\n'
        )
        return self._run(["osascript", "-e", script], timeout=4)

    def _genspark_google_confirmation_result(self) -> dict[str, Any]:
        script = """
import Cocoa
import ApplicationServices

let probe = "google-bundle-probe"

func axValue<T>(_ element: AXUIElement, _ attr: String, as type: T.Type) -> T? {
    var value: CFTypeRef?
    let err = AXUIElementCopyAttributeValue(element, attr as CFString, &value)
    guard err == .success, let cast = value as? T else { return nil }
    return cast
}

func axString(_ element: AXUIElement, _ attr: String) -> String {
    var value: CFTypeRef?
    let err = AXUIElementCopyAttributeValue(element, attr as CFString, &value)
    guard err == .success, let text = value as? String else { return "" }
    return text
}

func collectTabs(_ element: AXUIElement, out: inout [AXUIElement]) {
    if axString(element, kAXRoleAttribute) == "AXRadioButton" {
        out.append(element)
    }
    if let children: [AXUIElement] = axValue(element, kAXChildrenAttribute, as: [AXUIElement].self) {
        for child in children {
            collectTabs(child, out: &out)
        }
    }
}

func collectMatches(_ element: AXUIElement, hits: inout [String]) {
    let title = axString(element, kAXTitleAttribute)
    let desc = axString(element, kAXDescriptionAttribute)
    let value = axString(element, kAXValueAttribute)
    let text = [title, desc, value].joined(separator: " | ")
    for needle in ["Gmail — Logged in", "Google Calendar — Logged in", "Google Drive — Logged in"] {
        if text.localizedCaseInsensitiveContains(needle) {
            hits.append(text)
        }
    }
    if let children: [AXUIElement] = axValue(element, kAXChildrenAttribute, as: [AXUIElement].self) {
        for child in children {
            collectMatches(child, hits: &hits)
        }
    }
}

for app in NSRunningApplication.runningApplications(withBundleIdentifier: "com.google.Chrome") {
    let appElement = AXUIElementCreateApplication(app.processIdentifier)
    guard let windows: [AXUIElement] = axValue(appElement, kAXWindowsAttribute, as: [AXUIElement].self) else {
        continue
    }
    for window in windows {
        var tabs: [AXUIElement] = []
        collectTabs(window, out: &tabs)
        let gensparkTabs = tabs.filter { axString($0, kAXDescriptionAttribute) == "Genspark" }
        if gensparkTabs.isEmpty {
            var hits: [String] = []
            collectMatches(window, hits: &hits)
            if hits.isEmpty == false {
                print(hits.joined(separator: "\\n"))
                exit(0)
            }
            continue
        }
        for tab in gensparkTabs {
            _ = AXUIElementPerformAction(tab, kAXPressAction as CFString)
            Thread.sleep(forTimeInterval: 0.7)
            var hits: [String] = []
            collectMatches(window, hits: &hits)
            if hits.isEmpty == false {
                print(hits.joined(separator: "\\n"))
                exit(0)
            }
        }
    }
}
exit(1)
"""
        return self._run(["swift", "-e", script], timeout=6)

    def _chrome_genspark_remote_result(self) -> dict[str, Any]:
        script = """
import Cocoa
import ApplicationServices

let probe = "open-remote-desktop-probe"

func axValue<T>(_ element: AXUIElement, _ attr: String, as type: T.Type) -> T? {
    var value: CFTypeRef?
    let err = AXUIElementCopyAttributeValue(element, attr as CFString, &value)
    guard err == .success, let cast = value as? T else { return nil }
    return cast
}

func axString(_ element: AXUIElement, _ attr: String) -> String {
    var value: CFTypeRef?
    let err = AXUIElementCopyAttributeValue(element, attr as CFString, &value)
    guard err == .success, let text = value as? String else { return "" }
    return text
}

func collectRemoteMarkers(_ element: AXUIElement, hits: inout [String]) {
    let role = axString(element, kAXRoleAttribute)
    if role == "AXRadioButton" {
        let desc = axString(element, kAXDescriptionAttribute)
        if desc.localizedCaseInsensitiveContains("genspark claw") && desc.localizedCaseInsensitiveContains("-vm:") {
            hits.append(desc)
        }
    }
    if let children: [AXUIElement] = axValue(element, kAXChildrenAttribute, as: [AXUIElement].self) {
        for child in children {
            collectRemoteMarkers(child, hits: &hits)
        }
    }
}

for app in NSRunningApplication.runningApplications(withBundleIdentifier: "com.google.Chrome") {
    let appElement = AXUIElementCreateApplication(app.processIdentifier)
    guard let windows: [AXUIElement] = axValue(appElement, kAXWindowsAttribute, as: [AXUIElement].self) else {
        continue
    }
    for window in windows {
        let title = axString(window, kAXTitleAttribute)
        if title.localizedCaseInsensitiveContains("genspark claw") && title.localizedCaseInsensitiveContains("-vm:") {
            print(title)
            exit(0)
        }
        var hits: [String] = []
        collectRemoteMarkers(window, hits: &hits)
        if hits.isEmpty == false {
            print(hits.joined(separator: "\\n"))
            exit(0)
        }
    }
}
exit(1)
"""
        return self._run(["swift", "-e", script], timeout=6)

    def _playwright_cli_result(self, args: list[str], timeout: int) -> dict[str, Any]:
        script_path = Path.home() / ".codex" / "skills" / "playwright" / "scripts" / "playwright_cli.sh"
        if not script_path.exists():
            return {
                "returncode": 127,
                "stdout": "",
                "stderr": f"Missing Playwright CLI wrapper: {script_path}",
            }
        return self._run([str(script_path), *args], timeout=timeout)

    def _ocr_image_text_result(self, image_path: Path) -> dict[str, Any]:
        if not image_path.exists():
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": f"Missing image for OCR: {image_path}",
            }
        script = """
import Foundation
import Vision
import AppKit

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path)
guard let image = NSImage(contentsOf: url) else {
    fputs("Unable to load image\\n", stderr)
    exit(1)
}
var rect = CGRect(origin: .zero, size: image.size)
guard let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
    fputs("Unable to convert image\\n", stderr)
    exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])

do {
    try handler.perform([request])
    let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    print(lines.joined(separator: "\\n"))
} catch {
    fputs("\\(error)\\n", stderr)
    exit(1)
}
"""
        return self._run(["swift", "-e", script, str(image_path)], timeout=20)
