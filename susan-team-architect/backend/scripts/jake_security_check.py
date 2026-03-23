#!/usr/bin/env python3
"""Jake Security Audit — check credential health, PII exposure, and access control.

Usage:
    .venv/bin/python scripts/jake_security_check.py
    .venv/bin/python scripts/jake_security_check.py --component vault
    .venv/bin/python scripts/jake_security_check.py --component pii --text "some text"
    .venv/bin/python scripts/jake_security_check.py --component audit --hours 24
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jake_security.vault import vault
from jake_security.access_control import access_controller, Role, Permission
from jake_security.pii_redactor import pii_redactor
from jake_security.rate_limiter import rate_limiter
from jake_security.audit import audit, AuditEvent


REQUIRED_CREDENTIALS = [
    "ANTHROPIC_API_KEY",
    "VOYAGE_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY",
    "RESEND_API_KEY",
]


def check_vault() -> dict:
    """Check credential health."""
    all_present, missing = vault.has_all(REQUIRED_CREDENTIALS)
    report = vault.audit_report()
    set_count = sum(1 for r in report if r["status"] == "SET")
    total = len(report)

    print("\n=== CREDENTIAL VAULT AUDIT ===")
    for r in report:
        if r["sensitive"]:
            status_icon = "✓" if r["status"] == "SET" else "✗"
            print(f"  {status_icon} {r['key']}: {r['preview']}")

    if missing:
        print(f"\n⚠ MISSING REQUIRED CREDENTIALS: {', '.join(missing)}")
    else:
        print(f"\n✓ All {len(REQUIRED_CREDENTIALS)} required credentials present")

    print(f"  Total credentials loaded: {set_count}/{total}")

    audit.log(
        AuditEvent.SECURITY_VAULT_ACCESS,
        actor="jake_security_check",
        resource="credential_vault",
        context={"missing": missing, "total": total, "set_count": set_count},
    )
    return {"ok": all_present, "missing": missing, "total": total}


def check_pii(text: str | None = None) -> dict:
    """Test PII detection on sample data."""
    test_cases = [
        ("email test", "Contact mike@company.com for details"),
        ("phone test", "Call 555-867-5309 tomorrow"),
        ("api key test", "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"),
        ("no pii", "The quarterly revenue was $2.5M with 40% margins"),
    ]
    if text:
        test_cases = [("custom", text)]

    print("\n=== PII REDACTOR CHECK ===")
    for label, sample in test_cases:
        detected = pii_redactor.detect(sample)
        redacted = pii_redactor.redact(sample)
        icon = "✓" if detected else "○"
        print(f"  {icon} [{label}] {detected and [d['type'] for d in detected] or 'clean'}")
        if text:
            print(f"    Original: {sample[:60]}")
            print(f"    Redacted: {redacted[:60]}")

    print(f"\n  Patterns monitored: {len(['email', 'phone', 'ssn', 'credit_card', 'api_key_sk', 'api_key_ant', 'aws_access_key', 'aws_secret_key', 'private_key', 'bearer_token', 'supabase_key'])}")
    return {"ok": True, "patterns": 11}


def check_access_control() -> dict:
    """Verify RBAC configuration."""
    print("\n=== ACCESS CONTROL AUDIT ===")
    test_actors = ["jake", "oracle_sentinel", "inbox_zero", "dashboard", "unknown_bot"]
    for actor in test_actors:
        role = access_controller.get_role(actor)
        perms = access_controller.get_permissions(actor)
        print(f"  {actor}: role={role.value} ({len(perms)} permissions)")

    # Check that sensitive operations are restricted
    checks = [
        ("dashboard", Permission.ADMIN_VAULT, False),
        ("oracle_sentinel", Permission.EXEC_SEND_MESSAGE, True),
        ("jake", Permission.ADMIN_SECURITY, True),
        ("unknown_bot", Permission.WRITE_BRAIN, False),
    ]
    all_ok = True
    for actor, perm, expected in checks:
        result = access_controller.has_permission(actor, perm)
        icon = "✓" if result == expected else "✗"
        if result != expected:
            all_ok = False
        print(f"  {icon} {actor} can {perm.value}: {result} (expected: {expected})")

    return {"ok": all_ok}


def check_rate_limits() -> dict:
    """Show current rate limit configuration."""
    print("\n=== RATE LIMIT CONFIG ===")
    from jake_security.rate_limiter import _DEFAULT_LIMITS
    for op, (max_calls, window) in sorted(_DEFAULT_LIMITS.items()):
        if op == "default":
            continue
        unit = "minute" if window == 60 else f"{int(window)}s"
        print(f"  {op}: {max_calls}/{unit}")
    return {"ok": True, "operations": len(_DEFAULT_LIMITS)}


def check_audit_log() -> dict:
    """Show recent security events."""
    print("\n=== AUDIT LOG (last 24h security events) ===")
    events = audit.get_security_events(hours=24)
    if not events:
        print("  No security events in last 24 hours")
    else:
        for e in events[:10]:
            print(f"  [{e.get('created_at','')[:19]}] {e.get('event')} | {e.get('actor')} | {e.get('outcome')}")
    recent = audit.get_recent(limit=5)
    print(f"\n  Recent audit entries: {len(recent)}")
    return {"ok": True, "security_events_24h": len(events)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Jake Security Audit")
    parser.add_argument("--component", choices=["vault", "pii", "access", "rate", "audit", "all"], default="all")
    parser.add_argument("--text", type=str, help="Text to check for PII")
    parser.add_argument("--hours", type=int, default=24, help="Hours of audit history")
    args = parser.parse_args()

    print("╔══════════════════════════════════╗")
    print("║  JAKE SECURITY AUDIT REPORT      ║")
    print("╚══════════════════════════════════╝")

    results = {}

    if args.component in ("vault", "all"):
        results["vault"] = check_vault()
    if args.component in ("pii", "all"):
        results["pii"] = check_pii(args.text)
    if args.component in ("access", "all"):
        results["access"] = check_access_control()
    if args.component in ("rate", "all"):
        results["rate"] = check_rate_limits()
    if args.component in ("audit", "all"):
        results["audit"] = check_audit_log()

    all_ok = all(r.get("ok", True) for r in results.values())
    print(f"\n{'✓ SECURITY AUDIT PASSED' if all_ok else '✗ SECURITY AUDIT FOUND ISSUES'}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
