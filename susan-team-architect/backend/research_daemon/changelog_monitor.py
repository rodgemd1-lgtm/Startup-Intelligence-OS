"""
Dependency changelog monitoring for the Research Daemon.

Scans package.json, pyproject.toml, and requirements.txt to discover
dependencies, then checks for newer versions using simple version comparison.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from research_daemon.schemas import ChangelogEntry


def _parse_version_tuple(version: str) -> tuple[int, ...]:
    """
    Parse a version string into a comparable tuple of integers.

    Handles versions like '2.10.0', '^0.3.0', '>=3.11', '~4.0'.
    Strips leading non-numeric characters (^, >=, ~=, etc.).
    """
    cleaned = re.sub(r"^[^0-9]*", "", version.strip())
    parts = []
    for segment in cleaned.split("."):
        digits = re.match(r"(\d+)", segment)
        if digits:
            parts.append(int(digits.group(1)))
    return tuple(parts) if parts else (0,)


def _compare_versions(current: str, latest: str) -> int:
    """
    Compare two version strings.

    Returns:
        -1 if current < latest (update available)
         0 if current == latest
         1 if current > latest
    """
    cur = _parse_version_tuple(current)
    lat = _parse_version_tuple(latest)

    for c, l in zip(cur, lat):
        if c < l:
            return -1
        if c > l:
            return 1

    if len(cur) < len(lat):
        return -1
    if len(cur) > len(lat):
        return 1
    return 0


def _classify_severity(current: str, latest: str) -> str:
    """Classify update severity based on semver-like version comparison."""
    cur = _parse_version_tuple(current)
    lat = _parse_version_tuple(latest)

    cur_major = cur[0] if len(cur) > 0 else 0
    lat_major = lat[0] if len(lat) > 0 else 0
    cur_minor = cur[1] if len(cur) > 1 else 0
    lat_minor = lat[1] if len(lat) > 1 else 0

    if lat_major > cur_major:
        return "breaking"
    if lat_minor > cur_minor:
        return "minor"
    return "patch"


# ---------------------------------------------------------------------------
# Known latest versions registry
# ---------------------------------------------------------------------------
# This serves as a local reference for version checking without network calls.
# Updated periodically. The daemon compares declared versions against this
# registry. In production, this would be replaced by PyPI/npm API calls.

_KNOWN_LATEST_VERSIONS: dict[str, dict[str, Any]] = {
    # Python packages (from pyproject.toml)
    "anthropic": {
        "version": "0.52.0",
        "url": "https://github.com/anthropics/anthropic-sdk-python/releases",
        "notes": "Claude SDK with streaming, tool use, batch API",
    },
    "voyageai": {
        "version": "0.4.0",
        "url": "https://github.com/voyage-ai/voyageai-python/releases",
        "notes": "Voyage AI embedding SDK",
    },
    "supabase": {
        "version": "2.22.0",
        "url": "https://github.com/supabase/supabase-py/releases",
        "notes": "Supabase Python client",
    },
    "pydantic": {
        "version": "2.12.0",
        "url": "https://github.com/pydantic/pydantic/releases",
        "notes": "Data validation library",
    },
    "fastapi": {
        "version": "0.118.0",
        "url": "https://github.com/fastapi/fastapi/releases",
        "notes": "FastAPI web framework",
    },
    "pyyaml": {
        "version": "6.0.2",
        "url": "https://github.com/yaml/pyyaml/releases",
        "notes": "YAML parser",
    },
    "firecrawl-py": {
        "version": "4.1.0",
        "url": "https://github.com/mendableai/firecrawl/releases",
        "notes": "Firecrawl web scraping SDK",
    },
    "httpx": {
        "version": "0.28.0",
        "url": "https://github.com/encode/httpx/releases",
        "notes": "HTTP client",
    },
    "tiktoken": {
        "version": "0.9.0",
        "url": "https://github.com/openai/tiktoken/releases",
        "notes": "Token counting library",
    },
    "playwright": {
        "version": "1.51.0",
        "url": "https://github.com/microsoft/playwright-python/releases",
        "notes": "Browser automation",
    },
    "exa-py": {
        "version": "1.2.0",
        "url": "https://github.com/exa-labs/exa-py/releases",
        "notes": "Exa search SDK",
    },
    "pytest": {
        "version": "8.4.0",
        "url": "https://github.com/pytest-dev/pytest/releases",
        "notes": "Testing framework",
    },
    # JS/TS packages (from package.json)
    "next": {
        "version": "16.2.0",
        "url": "https://github.com/vercel/next.js/releases",
        "notes": "Next.js React framework",
    },
    "react": {
        "version": "19.2.3",
        "url": "https://github.com/facebook/react/releases",
        "notes": "React UI library",
    },
    "react-dom": {
        "version": "19.2.3",
        "url": "https://github.com/facebook/react/releases",
        "notes": "React DOM renderer",
    },
    "tailwindcss": {
        "version": "4.1.0",
        "url": "https://github.com/tailwindlabs/tailwindcss/releases",
        "notes": "Tailwind CSS utility framework",
    },
    "typescript": {
        "version": "5.8.0",
        "url": "https://github.com/microsoft/TypeScript/releases",
        "notes": "TypeScript compiler",
    },
    "eslint": {
        "version": "9.20.0",
        "url": "https://github.com/eslint/eslint/releases",
        "notes": "JavaScript linter",
    },
    "swr": {
        "version": "2.4.1",
        "url": "https://github.com/vercel/swr/releases",
        "notes": "SWR data fetching",
    },
}


class ChangelogMonitor:
    """Monitor dependency changelogs and generate update reports."""

    def __init__(self, project_root: Path) -> None:
        """
        Args:
            project_root: Root of the repository (Startup-Intelligence-OS/).
        """
        self.project_root = Path(project_root)

    # ------------------------------------------------------------------
    # Dependency scanning
    # ------------------------------------------------------------------

    def _parse_package_json(self, path: Path) -> dict[str, str]:
        """Parse dependencies from a package.json file."""
        deps: dict[str, str] = {}
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for section in ("dependencies", "devDependencies"):
                for pkg, ver in data.get(section, {}).items():
                    deps[pkg] = ver
        except (FileNotFoundError, json.JSONDecodeError, PermissionError):
            pass
        return deps

    def _parse_pyproject_toml(self, path: Path) -> dict[str, str]:
        """Parse dependencies from a pyproject.toml file (simple regex, no toml lib)."""
        deps: dict[str, str] = {}
        try:
            content = path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError):
            return deps

        # Match lines like: "pydantic>=2.10.0",
        pattern = re.compile(
            r'"([a-zA-Z0-9_-]+(?:\[[a-zA-Z0-9_,]+\])?)\s*([><=!~]+\s*[\d.]+[^"]*)"'
        )
        for match in pattern.finditer(content):
            raw_name = match.group(1)
            version_spec = match.group(2).strip()
            # Strip extras like [binary]
            clean_name = re.sub(r"\[.*?\]", "", raw_name)
            deps[clean_name] = version_spec

        return deps

    def _parse_requirements_txt(self, path: Path) -> dict[str, str]:
        """Parse dependencies from a requirements.txt file."""
        deps: dict[str, str] = {}
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, PermissionError):
            return deps

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            # Match: package>=version or package==version
            match = re.match(r"([a-zA-Z0-9_-]+)\s*([><=!~]+.+)?", line)
            if match:
                name = match.group(1)
                version = match.group(2).strip() if match.group(2) else ""
                deps[name] = version

        return deps

    def scan_dependencies(self) -> dict[str, str]:
        """
        Read all dependency files in the project and return a merged dict
        of {package_name: version_spec}.
        """
        all_deps: dict[str, str] = {}

        # pyproject.toml in backend
        pyproject = self.project_root / "susan-team-architect" / "backend" / "pyproject.toml"
        all_deps.update(self._parse_pyproject_toml(pyproject))

        # package.json in v5 app
        pkg_json = self.project_root / "apps" / "v5" / "package.json"
        all_deps.update(self._parse_package_json(pkg_json))

        # requirements.txt if present
        for req_path in self.project_root.rglob("requirements.txt"):
            # Skip node_modules and venvs
            parts = req_path.parts
            if any(skip in parts for skip in ("node_modules", ".venv", "venv", "__pycache__")):
                continue
            all_deps.update(self._parse_requirements_txt(req_path))

        return all_deps

    def check_for_updates(self, dependencies: dict[str, str]) -> list[ChangelogEntry]:
        """
        For each dependency, check if a newer version exists in the known registry.

        Args:
            dependencies: Dict of {package: current_version_spec}.

        Returns:
            List of ChangelogEntry objects for packages with available updates.
        """
        entries: list[ChangelogEntry] = []

        for pkg, current_spec in dependencies.items():
            # Normalize package name for lookup
            lookup_name = pkg.lower().replace("_", "-")
            # Also try without dashes
            alt_name = pkg.lower().replace("-", "")

            known = _KNOWN_LATEST_VERSIONS.get(lookup_name)
            if not known:
                known = _KNOWN_LATEST_VERSIONS.get(alt_name)
            if not known:
                # Try original casing
                known = _KNOWN_LATEST_VERSIONS.get(pkg)
            if not known:
                continue

            latest_version = known["version"]
            comparison = _compare_versions(current_spec, latest_version)

            if comparison < 0:
                severity = _classify_severity(current_spec, latest_version)

                entry = ChangelogEntry(
                    package=pkg,
                    version=latest_version,
                    release_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    changes_summary=known.get("notes", ""),
                    breaking_changes=(
                        [f"Major version bump: {current_spec} -> {latest_version}"]
                        if severity == "breaking"
                        else []
                    ),
                    new_features=(
                        [f"Minor version update: {current_spec} -> {latest_version}"]
                        if severity == "minor"
                        else []
                    ),
                    deprecations=[],
                    url=known.get("url", ""),
                    severity=severity,
                )
                entries.append(entry)

        return entries

    def generate_update_report(self, entries: list[ChangelogEntry]) -> str:
        """
        Generate a markdown report of all available dependency updates.

        Args:
            entries: List of ChangelogEntry objects.

        Returns:
            Markdown-formatted report string.
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines: list[str] = [
            "# Dependency Update Report",
            "",
            f"Generated: {now}",
            f"Total updates available: {len(entries)}",
            "",
        ]

        if not entries:
            lines.append("All dependencies are up to date.")
            return "\n".join(lines)

        # Group by severity
        breaking = [e for e in entries if e.severity == "breaking"]
        minor = [e for e in entries if e.severity == "minor"]
        patch = [e for e in entries if e.severity == "patch"]

        if breaking:
            lines.append("## Breaking Changes")
            lines.append("")
            for entry in breaking:
                lines.append(f"### {entry.package} -> {entry.version}")
                lines.append(f"- **Severity**: BREAKING")
                lines.append(f"- **Summary**: {entry.changes_summary}")
                if entry.breaking_changes:
                    for bc in entry.breaking_changes:
                        lines.append(f"  - {bc}")
                lines.append(f"- **Release**: [{entry.version}]({entry.url})")
                lines.append("")

        if minor:
            lines.append("## Minor Updates")
            lines.append("")
            for entry in minor:
                lines.append(f"- **{entry.package}** -> {entry.version} — {entry.changes_summary}")
                if entry.url:
                    lines.append(f"  - [Release notes]({entry.url})")

            lines.append("")

        if patch:
            lines.append("## Patch Updates")
            lines.append("")
            for entry in patch:
                lines.append(f"- **{entry.package}** -> {entry.version} — {entry.changes_summary}")
            lines.append("")

        lines.append("---")
        lines.append(f"*Report generated by Research Daemon changelog monitor.*")

        return "\n".join(lines)

    def save_report(self, report: str, path: Path) -> None:
        """
        Write the update report to a markdown file.

        Args:
            report: Markdown report string.
            path: Output file path (default: .claude/docs/dependency-updates.md).
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report, encoding="utf-8")
