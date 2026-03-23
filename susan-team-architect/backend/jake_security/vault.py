"""Credential Vault — secure loading and access of API keys.

Reads from ~/.hermes/.env (primary) and falls back to env vars.
Never logs credentials. Provides masked previews for auditing.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional


_HERMES_ENV = Path.home() / ".hermes" / ".env"
_SENSITIVE_KEYS = {
    "ANTHROPIC_API_KEY", "VOYAGE_API_KEY", "SUPABASE_SERVICE_KEY",
    "SUPABASE_ANON_KEY", "OPENAI_API_KEY", "FIRECRAWL_API_KEY",
    "RESEND_API_KEY", "TELEGRAM_BOT_TOKEN", "GITHUB_PAT",
    "STRIPE_SECRET_KEY", "TWILIO_AUTH_TOKEN",
}


class CredentialVault:
    """Secure credential store. Loads from ~/.hermes/.env + environment."""

    def __init__(self, env_path: Path | None = None):
        self._env_path = env_path or _HERMES_ENV
        self._cache: dict[str, str] = {}
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if self._env_path.exists():
            with open(self._env_path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, _, val = line.partition("=")
                        self._cache[key.strip()] = val.strip().strip('"').strip("'")
        self._loaded = True

    def get(self, key: str, default: str = "") -> str:
        """Return credential value. Falls back to environment variables."""
        self._load()
        return self._cache.get(key) or os.environ.get(key, default)

    def require(self, key: str) -> str:
        """Return credential or raise RuntimeError if missing."""
        value = self.get(key)
        if not value:
            raise RuntimeError(
                f"Required credential '{key}' not found in vault or environment. "
                f"Set it in {self._env_path} or as an environment variable."
            )
        return value

    def mask(self, key: str) -> str:
        """Return masked preview: sk-ant-...abc1 style."""
        value = self.get(key)
        if not value:
            return "[NOT SET]"
        if len(value) <= 8:
            return "***"
        return value[:6] + "..." + value[-4:]

    def audit_report(self) -> list[dict]:
        """Return credential health report (masked values only — never raw)."""
        self._load()
        all_keys = set(self._cache.keys()) | _SENSITIVE_KEYS
        report = []
        for key in sorted(all_keys):
            val = self.get(key)
            report.append({
                "key": key,
                "status": "SET" if val else "MISSING",
                "preview": self.mask(key) if val else "[NOT SET]",
                "sensitive": key in _SENSITIVE_KEYS,
            })
        return report

    def has_all(self, keys: list[str]) -> tuple[bool, list[str]]:
        """Check multiple credentials. Returns (all_present, missing_keys)."""
        missing = [k for k in keys if not self.get(k)]
        return (len(missing) == 0, missing)


vault = CredentialVault()
