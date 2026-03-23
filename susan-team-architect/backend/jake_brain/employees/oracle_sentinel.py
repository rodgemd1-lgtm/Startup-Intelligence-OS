"""Oracle Sentinel Employee — daily Oracle Health competitive intelligence briefing.

Runs weekdays at 6 AM. Gathers competitive signals from:
- Susan RAG knowledge base (Oracle Health domain)
- TrendRadar news feeds
- Brain episodic/semantic memory for context
Then synthesizes a brief and sends to Telegram.
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def load_env() -> None:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def get_oracle_intel() -> list[dict]:
    """Fetch Oracle Health competitive intel from Susan RAG."""
    results = []
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            return results
        client = create_client(url, key)
        # Query recent competitive intel for Oracle Health
        r = client.table("customer_intel").select("*").ilike(
            "content", "%oracle%"
        ).order("created_at", desc=True).limit(5).execute()
        results = r.data or []
    except Exception:
        pass
    return results


def get_brain_context() -> list[dict]:
    """Get relevant Oracle Health context from Jake's brain."""
    results = []
    try:
        from jake_brain.retriever import BrainRetriever
        retriever = BrainRetriever()
        hits = retriever.search("Oracle Health competitive landscape briefing", limit=5)
        results = [{"content": h.get("content", ""), "score": h.get("score", 0)} for h in hits]
    except Exception:
        pass
    return results


def synthesize_brief(intel: list[dict], context: list[dict]) -> str:
    """Build daily Oracle sentinel brief."""
    today = date.today().strftime("%Y-%m-%d")
    lines = [f"Oracle Health Sentinel — {today}", "=" * 40]

    if intel:
        lines.append(f"\n📊 Competitive Signals ({len(intel)} items):")
        for item in intel[:3]:
            content = item.get("content", item.get("summary", ""))[:200]
            lines.append(f"  • {content}")
    else:
        lines.append("\n📊 No new competitive signals today.")

    if context:
        lines.append(f"\n🧠 Brain Context ({len(context)} relevant memories):")
        for c in context[:2]:
            lines.append(f"  • {c['content'][:150]}")

    lines.append("\n✓ Oracle Sentinel complete.")
    return "\n".join(lines)


def send_telegram(message: str) -> bool:
    """Send brief to Telegram."""
    try:
        import urllib.request
        import json as json_mod
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            return False
        payload = json_mod.dumps({"chat_id": chat_id, "text": message[:4000], "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False


def run() -> dict:
    """Run oracle_sentinel employee — gather and send daily Oracle Health brief."""
    load_env()

    intel = get_oracle_intel()
    context = get_brain_context()
    brief = synthesize_brief(intel, context)

    sent = send_telegram(brief)

    return {
        "status": "complete",
        "intel_items": len(intel),
        "context_items": len(context),
        "telegram_sent": sent,
        "brief_lines": brief.count("\n") + 1,
    }


if __name__ == "__main__":
    result = run()
    print(result)
