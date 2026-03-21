"""Create/update Notion pages via Notion API — Tier 2 (confirm before writing)."""

from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone

from jake_brain.actions import BaseAction, SafetyTier, ActionResult, register
from jake_brain.actions.audit import log_action

logger = logging.getLogger("jake-actions")

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


@register
@dataclass
class UpdateNotionAction(BaseAction):
    """Create a new Notion page in a specified database. Tier 2 — confirm before writing."""

    tier: SafetyTier = SafetyTier.CONFIRM
    name: str = "update_notion"
    description: str = "Create/update a Notion page (Tier 2 — requires confirmation)"

    # Either create a new page in a database, or update an existing page
    database_id: str = ""       # If set: create new page in this database
    page_id: str = ""           # If set: update this existing page
    title: str = ""
    content: str = ""           # Text content to append as paragraph block
    properties: dict = field(default_factory=dict)  # Extra Notion properties

    def preview(self) -> str:
        if self.database_id:
            return (
                f"📝 Create Notion page\n"
                f"  Database: {self.database_id[:20]}...\n"
                f"  Title: {self.title}\n"
                f"  Content: {self.content[:200]}{'...' if len(self.content) > 200 else ''}"
            )
        return (
            f"📝 Update Notion page\n"
            f"  Page: {self.page_id[:20]}...\n"
            f"  Title: {self.title or '(keep existing)'}\n"
            f"  Content: {self.content[:200]}{'...' if len(self.content) > 200 else ''}"
        )

    def _headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }

    def _post(self, url: str, payload: dict, token: str) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self._headers(token), method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())

    def _patch(self, url: str, payload: dict, token: str) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self._headers(token), method="PATCH")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())

    def execute(self) -> ActionResult:
        token = os.environ.get("NOTION_API_TOKEN") or os.environ.get("NOTION_API_KEY")
        if not token:
            return ActionResult(success=False, message="NOTION_API_TOKEN not set", error="missing env var")

        if not self.database_id and not self.page_id:
            return ActionResult(success=False, message="Either database_id or page_id required", error="validation")

        try:
            if self.database_id:
                # Create new page
                page_props: dict = {"Name": {"title": [{"text": {"content": self.title}}]}}
                page_props.update(self.properties)

                children = []
                if self.content:
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": self.content[:2000]}}]
                        }
                    })

                payload: dict = {
                    "parent": {"database_id": self.database_id},
                    "properties": page_props,
                }
                if children:
                    payload["children"] = children

                result = self._post(f"{NOTION_API}/pages", payload, token)
                page_url = result.get("url", "")
                msg = f"Notion page created: {self.title} — {page_url}"
                log_action(self.name, int(self.tier), self.preview(), True, msg, {"page_id": result.get("id"), "url": page_url})
                return ActionResult(success=True, message=msg, data={"page_id": result.get("id"), "url": page_url})

            else:
                # Update existing page title + append content block
                updates: dict = {}
                if self.title:
                    updates["Name"] = {"title": [{"text": {"content": self.title}}]}
                updates.update(self.properties)

                if updates:
                    self._patch(f"{NOTION_API}/pages/{self.page_id}", {"properties": updates}, token)

                if self.content:
                    self._patch(
                        f"{NOTION_API}/blocks/{self.page_id}/children",
                        {"children": [{
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text", "text": {"content": self.content[:2000]}}]},
                        }]},
                        token,
                    )

                msg = f"Notion page {self.page_id} updated"
                log_action(self.name, int(self.tier), self.preview(), True, msg)
                return ActionResult(success=True, message=msg, data={"page_id": self.page_id})

        except urllib.error.HTTPError as e:
            err = e.read().decode()
            log_action(self.name, int(self.tier), self.preview(), False, err)
            return ActionResult(success=False, message=f"Notion API error {e.code}", error=err)
        except Exception as exc:
            log_action(self.name, int(self.tier), self.preview(), False, str(exc))
            return ActionResult(success=False, message=str(exc), error=str(exc))
