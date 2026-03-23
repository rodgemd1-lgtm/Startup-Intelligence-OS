"""PII Redactor — detect and redact sensitive data before logging or storage.

Covers: email addresses, phone numbers, SSNs, credit cards, API keys,
AWS keys, private keys, and known personal names.
"""
from __future__ import annotations

import re
from typing import Optional


_PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("email", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "[EMAIL]"),
    ("phone", re.compile(r"\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE]"),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    ("credit_card", re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"), "[CC]"),
    ("api_key_sk", re.compile(r"\bsk-[A-Za-z0-9\-_]{20,}\b"), "[API_KEY]"),
    ("api_key_ant", re.compile(r"\bsk-ant-[A-Za-z0-9\-_]{20,}\b"), "[API_KEY]"),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[AWS_KEY]"),
    ("aws_secret_key", re.compile(r"(?i)aws.{0,20}secret.{0,20}['\"]?([A-Za-z0-9/+=]{40})['\"]?"), "[AWS_SECRET]"),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"), "[PRIVATE_KEY]"),
    ("bearer_token", re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*"), "Bearer [TOKEN]"),
    ("supabase_key", re.compile(r"\beyJ[A-Za-z0-9\-_=]{20,}\.[A-Za-z0-9\-_=]{20,}\.[A-Za-z0-9\-_=]{20,}\b"), "[JWT]"),
]

# Known personal names to redact in logs (configurable)
_PERSONAL_NAMES: list[str] = [
    "Mike Rodgers", "James Loehr", "Matt Cohlmia",
]


class PIIRedactor:
    """Detects and redacts PII from strings before logging or storage."""

    def __init__(self, redact_names: bool = False, custom_names: list[str] | None = None):
        self._redact_names = redact_names
        self._custom_names = custom_names or []

    def redact(self, text: str) -> str:
        """Return text with all PII patterns replaced by placeholders."""
        if not text:
            return text
        for _name, pattern, replacement in _PATTERNS:
            text = pattern.sub(replacement, text)
        if self._redact_names:
            for name in _PERSONAL_NAMES + self._custom_names:
                text = text.replace(name, f"[{name.split()[0].upper()}]")
        return text

    def contains_pii(self, text: str) -> bool:
        """Return True if the text contains any PII."""
        if not text:
            return False
        for _name, pattern, _repl in _PATTERNS:
            if pattern.search(text):
                return True
        return False

    def detect(self, text: str) -> list[dict]:
        """Return list of detected PII types and their positions."""
        findings = []
        for pii_type, pattern, _repl in _PATTERNS:
            for match in pattern.finditer(text):
                findings.append({
                    "type": pii_type,
                    "start": match.start(),
                    "end": match.end(),
                    "preview": text[match.start():match.start()+4] + "***",
                })
        return findings

    def safe_log(self, text: str, label: str = "") -> str:
        """Return a log-safe version of the text with PII redacted."""
        redacted = self.redact(text)
        if label:
            return f"[{label}] {redacted}"
        return redacted


pii_redactor = PIIRedactor()
