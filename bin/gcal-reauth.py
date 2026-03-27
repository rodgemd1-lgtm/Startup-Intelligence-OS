#!/usr/bin/env python3
"""Re-authorize Google Calendar OAuth for Jake's morning pipeline.

Run this when the calendar section shows "invalid_client: Unauthorized".

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python ../../bin/gcal-reauth.py

This will:
1. Open a browser window for Google OAuth consent
2. Save the new tokens to ~/.hermes/google_oauth_tokens.json
3. Test the connection by listing today's events
"""

import json
import sys
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Missing deps. Run:")
    print("  pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
VAULT_DIR = Path.home() / ".jake-vault"
TOKEN_FILE = VAULT_DIR / "google_oauth_tokens.json"
LEGACY_TOKEN_FILE = Path.home() / ".hermes" / "google_oauth_tokens.json"

# Check for existing client credentials (vault first, then legacy)
source_file = TOKEN_FILE if TOKEN_FILE.exists() else LEGACY_TOKEN_FILE
if source_file.exists():
    with open(source_file) as f:
        existing = json.load(f)
    client_id = existing.get("client_id", "")
    client_secret = existing.get("client_secret", "")
    if client_id and client_secret:
        print(f"Found existing client ID: {client_id[:30]}...")
        print()
        reuse = input("Re-use existing client_id/secret? [Y/n] ").strip().lower()
        if reuse != "n":
            # Use existing credentials
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
                }
            }
        else:
            client_config = None
    else:
        client_config = None
else:
    client_config = None

if client_config is None:
    print("Need new OAuth credentials.")
    print("1. Go to https://console.cloud.google.com/apis/credentials")
    print("2. Create OAuth 2.0 Client ID (type: Desktop)")
    print("3. Download the client_secret JSON file")
    print()
    cred_path = input("Path to downloaded credentials JSON: ").strip()
    if not Path(cred_path).exists():
        print(f"File not found: {cred_path}")
        sys.exit(1)
    with open(cred_path) as f:
        client_config = json.load(f)

print()
print("Opening browser for Google OAuth consent...")
print("(If browser doesn't open, copy the URL from the terminal)")
print()

flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
creds = flow.run_local_server(port=0)

# Save tokens
installed = client_config.get("installed", client_config.get("web", {}))
tokens = {
    "client_id": installed["client_id"],
    "client_secret": installed["client_secret"],
    "refresh_token": creds.refresh_token,
    "scopes": SCOPES,
}

VAULT_DIR.mkdir(parents=True, exist_ok=True)
with open(TOKEN_FILE, "w") as f:
    json.dump(tokens, f, indent=2)
TOKEN_FILE.chmod(0o600)
print(f"Tokens saved to vault: {TOKEN_FILE}")

# Also save credentials JSON to vault
installed = client_config.get("installed", client_config.get("web", {}))
cred_vault = VAULT_DIR / "google_credentials.json"
with open(cred_vault, "w") as f:
    json.dump(client_config, f, indent=2)
cred_vault.chmod(0o600)
print(f"Credentials saved to vault: {cred_vault}")

# Sync vault to all consumers
import subprocess
sync_script = VAULT_DIR / "sync.sh"
if sync_script.exists():
    print("\nSyncing vault to all consumers...")
    subprocess.run([str(sync_script)], check=False)
else:
    # Manual fallback — copy to legacy location
    LEGACY_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LEGACY_TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"Also saved to legacy: {LEGACY_TOKEN_FILE}")

# Test
print()
print("Testing calendar access...")
service = build("calendar", "v3", credentials=creds)
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
start = now.replace(hour=0, minute=0, second=0).isoformat()
end = now.replace(hour=23, minute=59, second=59).isoformat()

events = (
    service.events()
    .list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        maxResults=5,
        singleEvents=True,
        orderBy="startTime",
    )
    .execute()
    .get("items", [])
)

if events:
    print(f"Found {len(events)} events today:")
    for e in events:
        summary = e.get("summary", "No title")
        start_t = e.get("start", {}).get("dateTime", e.get("start", {}).get("date", ""))
        print(f"  - {start_t}: {summary}")
else:
    print("No events today (calendar is clear)")

print()
print("Google Calendar OAuth is working. Morning pipeline will use these tokens.")
