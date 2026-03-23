"""Research Agent Employee — autonomous background research on queued topics.

Runs nightly at 3 AM. Processes the research queue from jake_tasks:
- Finds tasks with task_type='research' and status='pending'
- Runs deep research on each topic via Susan RAG + web search
- Stores findings in jake_episodic
- Updates task status to 'done'
- Sends digest to Telegram
"""
from __future__ import annotations

import os
import sys
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


def get_research_queue(limit: int = 5) -> list[dict]:
    """Fetch pending research tasks from jake_tasks."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            return []
        client = create_client(url, key)
        result = client.table("jake_tasks").select("*").eq(
            "status", "pending"
        ).ilike("task_type", "%research%").order(
            "priority", desc=True
        ).limit(limit).execute()
        return result.data or []
    except Exception:
        return []


def research_topic(topic: str, context: str = "") -> dict:
    """Research a topic using Susan RAG and web search tools."""
    findings = {}

    # 1. Search Susan RAG
    try:
        from supabase import create_client
        from rag_engine.embedder import Embedder
        from susan_core.config import config

        client = create_client(config.supabase_url, config.supabase_key)
        embedder = Embedder()
        embedding = embedder.embed(topic)

        result = client.rpc("search_knowledge", {
            "query_embedding": embedding,
            "match_threshold": 0.75,
            "match_count": 8,
        }).execute()
        rag_results = result.data or []
        findings["rag"] = rag_results[:5]
    except Exception:
        findings["rag"] = []

    # 2. Search brain memory for related context
    try:
        from jake_brain.retriever import BrainRetriever
        retriever = BrainRetriever()
        brain_results = retriever.search(topic, top_k=5)
        findings["brain"] = [{"content": r.content, "score": r.score} for r in brain_results]
    except Exception:
        findings["brain"] = []

    return findings


def synthesize_findings(topic: str, findings: dict, context: str = "") -> str:
    """Use Claude to synthesize research findings into a useful report."""
    try:
        import anthropic
        from jake_cost.router import ModelRouter
        from jake_cost.tracker import cost_tracker

        router = ModelRouter()
        decision = router.route("research_query", complexity="medium")

        rag_text = "\n".join([
            f"- [{r.get('data_type', 'general')}] {r.get('content', '')[:300]}"
            for r in findings.get("rag", [])[:5]
        ])
        brain_text = "\n".join([
            f"- {r['content'][:200]}"
            for r in findings.get("brain", [])[:3]
        ])

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        prompt = f"""Research synthesis request from Jake's Research Agent.

TOPIC: {topic}
CONTEXT: {context or 'None provided'}

SUSAN RAG RESULTS:
{rag_text or 'No results found'}

BRAIN MEMORY:
{brain_text or 'No relevant memories'}

Synthesize the above into a research brief:
1. Key Findings (top 3 insights)
2. What's Confirmed (things we know with confidence)
3. Knowledge Gaps (what we still don't know)
4. Recommended Actions (1-3 concrete next steps)
5. Jake's Take (1 sentence hot take on this topic)

Be concise, direct, and useful. Under 250 words."""

        response = client.messages.create(
            model=decision.model_id,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        usage = response.usage
        cost_tracker.record_anthropic_call(
            decision.tier, usage.input_tokens, usage.output_tokens, actor="research_agent"
        )
        return response.content[0].text
    except Exception as e:
        rag_count = len(findings.get("rag", []))
        brain_count = len(findings.get("brain", []))
        return f"[Synthesis unavailable]\n\nRaw findings: {rag_count} RAG results, {brain_count} brain memories found for '{topic}'"


def mark_task_complete(task_id: str, result_summary: str) -> None:
    """Update task status to done."""
    try:
        from supabase import create_client
        from datetime import datetime, timezone
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            return
        client = create_client(url, key)
        client.table("jake_tasks").update({
            "status": "done",
            "result": result_summary[:2000],
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", task_id).execute()
    except Exception:
        pass


def store_episodic(topic: str, synthesis: str) -> None:
    """Store research findings in jake_episodic."""
    try:
        from jake_brain.store import BrainStore
        store = BrainStore()
        store.store_episodic(
            content=f"Research: {topic}\n\n{synthesis}",
            source=f"research_agent:{topic[:50]}",
            data_type="research_finding",
            importance=0.75,
        )
    except Exception:
        pass


def send_telegram_digest(results: list[dict]) -> None:
    """Send research digest to Telegram."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id or not results:
        return
    try:
        import urllib.request, json as _json
        items = "\n".join([
            f"• *{r['topic'][:50]}* — {r.get('synthesis', '')[:100]}..."
            for r in results[:3]
        ])
        msg = f"🔬 *Research Agent Digest*\n\nCompleted {len(results)} research task(s):\n\n{items}"
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = _json.dumps({"chat_id": chat_id, "text": msg[:4000], "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def run() -> dict:
    """Main entry point for the Research Agent employee."""
    load_env()
    from jake_security.audit import audit, AuditEvent
    from jake_security.rate_limiter import rate_limiter

    audit.log(AuditEvent.EMPLOYEE_RUN, actor="research_agent", resource="research_queue")

    if not rate_limiter.acquire("employee_run", actor="research_agent"):
        return {"status": "rate_limited", "tasks": 0}

    queue = get_research_queue(limit=5)
    if not queue:
        audit.log(AuditEvent.EMPLOYEE_COMPLETE, actor="research_agent", context={"tasks": 0})
        return {"status": "queue_empty", "tasks": 0}

    results = []
    for task in queue:
        topic = task.get("title", task.get("description", "Unknown topic"))
        context = task.get("context", "")

        # Research
        findings = research_topic(topic, context)

        # Synthesize
        synthesis = synthesize_findings(topic, findings, context)

        # Store
        store_episodic(topic, synthesis)

        # Mark complete
        if task.get("id"):
            mark_task_complete(task["id"], synthesis[:500])

        results.append({
            "topic": topic,
            "task_id": task.get("id"),
            "synthesis": synthesis[:200],
            "rag_results": len(findings.get("rag", [])),
            "brain_results": len(findings.get("brain", [])),
            "status": "complete",
        })

    # Send digest
    send_telegram_digest(results)

    audit.log(
        AuditEvent.EMPLOYEE_COMPLETE,
        actor="research_agent",
        context={"tasks_completed": len(results)},
    )
    return {"status": "complete", "tasks": len(results), "results": results}


if __name__ == "__main__":
    result = run()
    print(f"Research Agent complete: {result['tasks']} tasks processed")
    if result.get("results"):
        for r in result["results"]:
            print(f"  ✓ {r['topic'][:60]} ({r['rag_results']} RAG, {r['brain_results']} brain)")
