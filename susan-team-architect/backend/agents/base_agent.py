"""Base agent class — RAG query, BE lens injection, cost tracking."""
from __future__ import annotations
import json
import time
from anthropic import Anthropic
from rag_engine.retriever import Retriever
from susan_core.config import config

BE_LENS = """<behavioral_economics_lens>
Before finalizing any output, apply these checks:

1. LOSS AUDIT: Does this help users feel the cost of NOT acting?
2. OWNERSHIP CHECK: Does the user own something that makes leaving feel like a loss?
3. IDENTITY ALIGNMENT: Does this reinforce who they're becoming?
4. FRICTION AUDIT: Is the return threshold under 2 minutes?
5. PROGRESS VISIBILITY: Is progress visible, named, and personalized?

Default to LOSS FRAMING for all re-engagement copy.
Reference the Apex Ventures BE Repository for scripts and benchmarks.
</behavioral_economics_lens>"""


class BaseAgent:
    """Base class for all 22 Susan agents."""

    agent_id: str = "base"
    agent_name: str = "Base Agent"
    role: str = "Agent"
    model: str = config.model_sonnet
    rag_data_types: list[str] = []
    system_prompt: str = ""

    def __init__(self, company_id: str = "shared"):
        self.company_id = company_id
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.retriever = Retriever()

    def get_system_prompt(self) -> str:
        """Build full system prompt with BE lens injection."""
        return f"{self.system_prompt}\n\n{BE_LENS}"

    def query_rag(
        self,
        question: str,
        data_types: list[str] | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Query the RAG knowledge base for relevant context."""
        types = data_types or self.rag_data_types or None
        return self.retriever.search(
            query=question,
            company_id=self.company_id,
            data_types=types,
            agent_id=self.agent_id,
            top_k=top_k,
        )

    def run(self, prompt: str, max_tokens: int = 4096) -> dict:
        """Execute the agent with RAG context and cost tracking."""
        # Get RAG context
        rag_results = self.query_rag(prompt)
        rag_context = ""
        if rag_results:
            rag_context = "\n\n<knowledge_base>\n"
            for r in rag_results:
                rag_context += f"[{r['data_type']}] {r['content']}\n---\n"
            rag_context += "</knowledge_base>\n"

        full_prompt = f"{rag_context}\n{prompt}" if rag_context else prompt

        start = time.time()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.get_system_prompt(),
            messages=[{"role": "user", "content": full_prompt}],
        )
        duration_ms = int((time.time() - start) * 1000)

        # Track costs
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (
            input_tokens * config.cost_per_m_input.get(self.model, 3.0) / 1_000_000
            + output_tokens * config.cost_per_m_output.get(self.model, 15.0) / 1_000_000
        )

        # Log run
        try:
            from supabase import create_client
            sb = create_client(config.supabase_url, config.supabase_key)
            sb.table("agent_runs").insert({
                "company_id": self.company_id,
                "agent_id": self.agent_id,
                "model": self.model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": float(cost),
                "duration_ms": duration_ms,
            }).execute()
        except Exception:
            pass  # Don't fail on logging errors

        text = response.content[0].text
        return {
            "text": text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "duration_ms": duration_ms,
        }

    def run_json(self, prompt: str, max_tokens: int = 4096) -> dict:
        """Execute and parse JSON from the response."""
        result = self.run(prompt, max_tokens)
        text = result["text"]
        # Extract JSON from response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            parsed = json.loads(text[start:end])
            result["parsed"] = parsed
        else:
            result["parsed"] = None
        return result
