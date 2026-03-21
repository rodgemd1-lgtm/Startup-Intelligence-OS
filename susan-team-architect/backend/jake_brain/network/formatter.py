"""
InterfaceFormatter — adapts Jake's responses to the current interface.

Each interface has different constraints and expectations:
  telegram    — concise, emoji OK, 3-5 bullet max, no code blocks
  mac         — rich markdown, full context, code blocks fine
  claude_code — full markdown, technical depth, verbose OK
  email       — formal tone, subject line, greeting/sign-off

Usage:
    fmt = InterfaceFormatter()
    msg = fmt.format(content, interface=Interface.TELEGRAM)
"""

from __future__ import annotations

import re
import textwrap
from typing import Optional
from .presence import Interface


class InterfaceFormatter:
    """Adapt response content to the target interface."""

    # Max characters before truncation (None = no limit)
    LIMITS = {
        Interface.TELEGRAM: 4096,   # Telegram max message length
        Interface.MAC: None,
        Interface.CLAUDE_CODE: None,
        Interface.EMAIL: None,
        Interface.UNKNOWN: None,
    }

    def format(
        self,
        content: str,
        interface: Optional[Interface] = None,
        subject: Optional[str] = None,       # email only
        truncate: bool = True,
    ) -> str:
        """Format content for the given interface."""
        if interface is None:
            interface = Interface.UNKNOWN

        dispatch = {
            Interface.TELEGRAM: self._format_telegram,
            Interface.MAC: self._format_mac,
            Interface.CLAUDE_CODE: self._format_claude,
            Interface.EMAIL: self._format_email,
            Interface.UNKNOWN: self._format_mac,
        }
        fn = dispatch.get(interface, self._format_mac)
        result = fn(content, subject=subject)

        limit = self.LIMITS.get(interface)
        if truncate and limit and len(result) > limit:
            result = result[: limit - 20] + "\n\n_[truncated]_"
        return result

    # ── interface-specific formatters ────────────────────────────────────────

    def _format_telegram(self, content: str, **_) -> str:
        """Concise, plain, max 5 bullets. Strip heavy markdown."""
        lines = content.strip().splitlines()
        out = []
        bullet_count = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if out:
                    out.append("")
                continue

            # Convert markdown headers to bold-ish caps
            if stripped.startswith("### "):
                out.append(f"*{stripped[4:].upper()}*")
                continue
            if stripped.startswith("## "):
                out.append(f"*{stripped[3:].upper()}*")
                continue
            if stripped.startswith("# "):
                out.append(f"*{stripped[2:].upper()}*")
                continue

            # Limit bullet points
            is_bullet = stripped.startswith(("- ", "* ", "• "))
            if is_bullet:
                if bullet_count >= 5:
                    continue
                bullet_count += 1
                # Keep it clean
                out.append("• " + stripped[2:])
                continue

            # Strip code fences
            if stripped.startswith("```"):
                continue

            out.append(stripped)

        # Strip consecutive blank lines
        result = "\n".join(out)
        result = re.sub(r"\n{3,}", "\n\n", result).strip()
        return result

    def _format_mac(self, content: str, **_) -> str:
        """Full markdown, no changes needed."""
        return content.strip()

    def _format_claude(self, content: str, **_) -> str:
        """Full markdown with technical depth — same as mac."""
        return content.strip()

    def _format_email(self, content: str, subject: Optional[str] = None, **_) -> str:
        """Formal email format with subject, greeting, body, sign-off."""
        body = content.strip()
        # Strip markdown headers → plain text
        body = re.sub(r"^#{1,6}\s+", "", body, flags=re.MULTILINE)
        # Convert bullets → dashes
        body = re.sub(r"^[-*•]\s+", "  - ", body, flags=re.MULTILINE)
        # Strip bold/italic
        body = re.sub(r"\*\*(.+?)\*\*", r"\1", body)
        body = re.sub(r"\*(.+?)\*", r"\1", body)

        parts = []
        if subject:
            parts.append(f"Subject: {subject}\n")
        parts.append("Hi Mike,\n")
        parts.append(textwrap.fill(body, width=80, replace_whitespace=False))
        parts.append("\n\nBest,\nJake")
        return "\n".join(parts)

    # ── helpers ───────────────────────────────────────────────────────────────

    def summarize_for_notification(self, content: str, max_chars: int = 200) -> str:
        """
        Produce a short notification-safe summary (no markdown).
        Used for push notifications, banners, etc.
        """
        # Strip markdown
        text = re.sub(r"[#*`_~\[\]()]", "", content)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= max_chars:
            return text
        return text[:max_chars - 1] + "…"
