"""Create a GitHub issue — Tier 2 (confirm before creating)."""

from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field

from jake_brain.actions import BaseAction, SafetyTier, ActionResult, register
from jake_brain.actions.audit import log_action

logger = logging.getLogger("jake-actions")

GITHUB_API = "https://api.github.com/repos/{owner}/{repo}/issues"


@register
@dataclass
class CreateGithubIssueAction(BaseAction):
    """Create a GitHub issue via the GitHub REST API. Tier 2 — confirm before creating."""

    tier: SafetyTier = SafetyTier.CONFIRM
    name: str = "create_github_issue"
    description: str = "Create a GitHub issue (Tier 2 — requires confirmation)"

    owner: str = ""
    repo: str = ""
    title: str = ""
    body: str = ""
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)

    def preview(self) -> str:
        labels_str = ", ".join(self.labels) if self.labels else "none"
        return (
            f"🐛 Create GitHub issue\n"
            f"  Repo: {self.owner}/{self.repo}\n"
            f"  Title: {self.title}\n"
            f"  Labels: {labels_str}\n"
            f"  Body: {self.body[:200]}{'...' if len(self.body) > 200 else ''}"
        )

    def execute(self) -> ActionResult:
        token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            return ActionResult(success=False, message="GITHUB_PERSONAL_ACCESS_TOKEN not set", error="missing env var")

        if not all([self.owner, self.repo, self.title]):
            return ActionResult(success=False, message="owner, repo, and title are required", error="validation")

        url = GITHUB_API.format(owner=self.owner, repo=self.repo)
        payload: dict = {"title": self.title}
        if self.body:
            payload["body"] = self.body
        if self.labels:
            payload["labels"] = self.labels
        if self.assignees:
            payload["assignees"] = self.assignees

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "Content-Type": "application/json",
                    "User-Agent": "jake-hands/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                issue_number = result.get("number", "?")
                html_url = result.get("html_url", "")
                msg = f"Issue #{issue_number} created in {self.owner}/{self.repo}: {html_url}"
                log_action(self.name, int(self.tier), self.preview(), True, msg, {"issue_number": issue_number, "url": html_url})
                return ActionResult(success=True, message=msg, data={"issue_number": issue_number, "url": html_url})

        except urllib.error.HTTPError as e:
            err = e.read().decode()
            log_action(self.name, int(self.tier), self.preview(), False, err)
            return ActionResult(success=False, message=f"GitHub API error {e.code}", error=err)
        except Exception as exc:
            log_action(self.name, int(self.tier), self.preview(), False, str(exc))
            return ActionResult(success=False, message=str(exc), error=str(exc))
