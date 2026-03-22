#!/usr/bin/env python3
"""Microsoft Graph API authentication for Jake's Brain.

Uses MSAL device code flow (one-time setup) to get an OAuth2 refresh token
that is stored in ~/.hermes/.env. Subsequent calls use the cached token.

One-time setup:
    python scripts/ms_graph_auth.py --setup

After setup, import and use get_access_token() in any script.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Requires: pip install msal
try:
    import msal
except ImportError:
    print("ERROR: msal not installed. Run: pip install msal")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Oracle Microsoft 365 config
# ---------------------------------------------------------------------------

# Oracle's Azure AD tenant
ORACLE_TENANT_ID = "4e2c6054-71cb-48f1-bd6c-3a9705aca71b"

# Microsoft Graph Explorer — a public, Microsoft-provided app that Oracle allows.
# This is the canonical public client for delegated Graph API access.
GRAPH_EXPLORER_CLIENT_ID = "de8bc8b5-d9f9-48b1-a8ad-b748da725064"

# Scopes needed for email read access
MAIL_SCOPES = [
    "https://graph.microsoft.com/Mail.Read",
    # offline_access is auto-added by MSAL — don't include explicitly
]

# Where credentials are stored
HERMES_ENV = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / ".env"
MSAL_CACHE_PATH = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")) / ".msal_cache.json"

# Token keys in .env
ENV_KEY_REFRESH_TOKEN = "MICROSOFT_GRAPH_REFRESH_TOKEN"
ENV_KEY_CLIENT_ID = "MICROSOFT_GRAPH_CLIENT_ID"
ENV_KEY_TENANT_ID = "MICROSOFT_GRAPH_TENANT_ID"


# ---------------------------------------------------------------------------
# MSAL app factory
# ---------------------------------------------------------------------------

def _make_app(client_id: str = GRAPH_EXPLORER_CLIENT_ID,
              tenant_id: str = ORACLE_TENANT_ID) -> msal.PublicClientApplication:
    """Create MSAL public client application with file-based token cache."""
    cache = msal.SerializableTokenCache()
    if MSAL_CACHE_PATH.exists():
        cache.deserialize(MSAL_CACHE_PATH.read_text())

    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache,
    )

    # Persist cache on every call
    original_acquire = app.acquire_token_by_device_flow
    return app, cache


def _save_cache(cache: msal.SerializableTokenCache) -> None:
    """Persist the MSAL token cache to disk."""
    if cache.has_state_changed:
        MSAL_CACHE_PATH.write_text(cache.serialize())
        MSAL_CACHE_PATH.chmod(0o600)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_access_token(client_id: str = GRAPH_EXPLORER_CLIENT_ID,
                     tenant_id: str = ORACLE_TENANT_ID) -> str | None:
    """Return a valid access token for Microsoft Graph, refreshing if needed.

    Returns None if no credentials are configured (run --setup first).
    Raises on unexpected errors.
    """
    app, cache = _make_app(client_id, tenant_id)

    # Try silent token acquisition from cache (uses refresh token automatically)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(MAIL_SCOPES, account=accounts[0])
        _save_cache(cache)
        if result and "access_token" in result:
            return result["access_token"]
        if result and "error" in result:
            print(f"  Silent token failed: {result.get('error_description', result['error'])}")

    # Also try reading refresh token from .env if MSAL cache is empty
    env_token = _read_env_value(ENV_KEY_REFRESH_TOKEN)
    if env_token:
        result = app.acquire_token_by_refresh_token(env_token, scopes=MAIL_SCOPES)
        _save_cache(cache)
        if result and "access_token" in result:
            # Persist new refresh token back to .env if rotated
            if "refresh_token" in result and result["refresh_token"] != env_token:
                _write_env_value(ENV_KEY_REFRESH_TOKEN, result["refresh_token"])
            return result["access_token"]
        if result and "error" in result:
            print(f"  Refresh token failed: {result.get('error_description', result['error'])}")
            print("  Run: python scripts/ms_graph_auth.py --setup")
            return None

    return None  # No credentials configured


def setup_device_code_flow(client_id: str = GRAPH_EXPLORER_CLIENT_ID,
                           tenant_id: str = ORACLE_TENANT_ID) -> bool:
    """Run the one-time device code auth flow.

    Prints a URL and code for the user to open in a browser.
    Returns True on success, False on failure.
    """
    app, cache = _make_app(client_id, tenant_id)

    flow = app.initiate_device_flow(scopes=MAIL_SCOPES)
    if "user_code" not in flow:
        print(f"ERROR: Failed to initiate device flow: {flow.get('error_description', flow)}")
        return False

    print("\n" + "=" * 60)
    print("MICROSOFT GRAPH API — ONE-TIME SETUP")
    print("=" * 60)
    print(f"\nStep 1: Open this URL in your browser:")
    print(f"  https://microsoft.com/devicelogin")
    print(f"\nStep 2: Enter this code: {flow['user_code']}")
    print(f"\nStep 3: Sign in with: mike.r.rodgers@oracle.com")
    print(f"\nWaiting for authentication (expires in {flow.get('expires_in', 900)}s)...")
    print("=" * 60 + "\n")

    result = app.acquire_token_by_device_flow(flow)  # blocks until user authenticates
    _save_cache(cache)

    if "access_token" not in result:
        print(f"ERROR: Authentication failed: {result.get('error_description', result.get('error', 'unknown'))}")
        return False

    # Store refresh token in .env for fallback
    if "refresh_token" in result:
        _write_env_value(ENV_KEY_REFRESH_TOKEN, result["refresh_token"])
        _write_env_value(ENV_KEY_CLIENT_ID, client_id)
        _write_env_value(ENV_KEY_TENANT_ID, tenant_id)
        print("  Refresh token saved to ~/.hermes/.env")

    # Verify it works
    token = result["access_token"]
    print(f"\nAuthentication successful!")
    print(f"  User: {result.get('id_token_claims', {}).get('preferred_username', 'unknown')}")
    print(f"  Token expires in: {result.get('expires_in', '?')}s")
    print(f"\nGraph API email access is now configured. No more Mail.app needed.")
    return True


def test_graph_email(token: str) -> None:
    """Quick test: fetch 3 emails from Graph API."""
    import requests
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$top=3&$select=subject,from,receivedDateTime,isRead"
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        msgs = r.json().get("value", [])
        print(f"\nTest successful — {len(msgs)} emails from inbox:")
        for m in msgs:
            sender = m.get("from", {}).get("emailAddress", {}).get("address", "?")
            print(f"  [{m.get('isRead') and 'read' or 'UNREAD'}] {m.get('subject', '?')} — {sender}")
    else:
        print(f"Graph API test failed: {r.status_code} — {r.text[:200]}")


# ---------------------------------------------------------------------------
# .env file helpers
# ---------------------------------------------------------------------------

def _read_env_value(key: str) -> str | None:
    """Read a value from ~/.hermes/.env."""
    if not HERMES_ENV.exists():
        return None
    for line in HERMES_ENV.read_text().splitlines():
        if line.startswith(f"{key}="):
            return line[len(key) + 1:].strip()
    return None


def _write_env_value(key: str, value: str) -> None:
    """Write or update a key=value in ~/.hermes/.env."""
    env_text = HERMES_ENV.read_text() if HERMES_ENV.exists() else ""
    lines = env_text.splitlines()
    new_line = f"{key}={value}"
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = new_line
            updated = True
            break
    if not updated:
        lines.append(new_line)
    HERMES_ENV.write_text("\n".join(lines) + "\n")
    HERMES_ENV.chmod(0o600)
    print(f"  Written: {key}=***")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Microsoft Graph API auth setup for Jake")
    parser.add_argument("--setup", action="store_true", help="Run one-time device code auth flow")
    parser.add_argument("--test", action="store_true", help="Test current token by fetching inbox")
    parser.add_argument("--status", action="store_true", help="Check if token is configured")
    args = parser.parse_args()

    if args.setup:
        success = setup_device_code_flow()
        if success and args.test:
            token = get_access_token()
            if token:
                test_graph_email(token)
        sys.exit(0 if success else 1)

    if args.test:
        token = get_access_token()
        if token:
            test_graph_email(token)
        else:
            print("No token. Run: python scripts/ms_graph_auth.py --setup")
            sys.exit(1)
        sys.exit(0)

    if args.status:
        token = get_access_token()
        if token:
            print("Graph API token: ACTIVE")
            print("Email via Microsoft Graph: READY (no Mail.app needed)")
        else:
            print("Graph API token: NOT CONFIGURED")
            print("Run: python scripts/ms_graph_auth.py --setup")
        sys.exit(0)

    parser.print_help()
