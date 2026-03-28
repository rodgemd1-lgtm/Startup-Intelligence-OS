"""Base agent class — RAG query, BE lens injection, cost tracking.

V1.5: Routes through OpenRouter by default (Gemini 2.0 Flash, DeepSeek V3.2,
GLM-4.5-Air:free). Anthropic is kept as fallback only.
"""
from __future__ import annotations
import json
import logging
import os
import time
from anthropic import Anthropic
from rag_engine.retriever import Retriever
from susan_core.config import config
from jake_cost.router import router, ModelTier, Provider, _MODEL_PRICING, _LOCAL_FALLBACK
from jake_cost.openrouter_client import get_openrouter_client, OpenRouterClient
from jake_cost.ollama_client import is_ollama_running, get_ollama_client

logger = logging.getLogger(__name__)

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

# Set True to force all agents back to Anthropic (emergency rollback)
FORCE_ANTHROPIC = os.environ.get("FORCE_ANTHROPIC", "").lower() in ("1", "true", "yes")


class BaseAgent:
    """Base class for all Susan agents. Routes via OpenRouter by default."""

    agent_id: str = "base"
    agent_name: str = "Base Agent"
    role: str = "Agent"
    # Default task type for routing — subclasses can override
    task_type: str = "employee_run"
    rag_data_types: list[str] = []
    system_prompt: str = ""

    def __init__(self, company_id: str = "shared"):
        self.company_id = company_id
        self.retriever = Retriever()
        # Resolve model via router
        self._routing = router.route(self.task_type)
        self.model = self._routing.model_id
        self.provider = self._routing.provider
        self._ollama = None

        # Initialize the appropriate client
        if FORCE_ANTHROPIC or self.provider == Provider.ANTHROPIC:
            self._anthropic = Anthropic(api_key=config.anthropic_api_key)
            self._openrouter = None
            self.provider = Provider.ANTHROPIC
            self.model = config.model_sonnet
        elif self.provider == Provider.LOCAL:
            # Try Ollama first; fall back to FREE_BULK via OpenRouter
            if is_ollama_running():
                self._ollama = get_ollama_client()
                self._anthropic = None
                self._openrouter = None
            else:
                logger.info(
                    f"[{self.agent_id}] Ollama not running, falling back to {_LOCAL_FALLBACK.value}"
                )
                self._routing = router.route(self.task_type, force_tier=_LOCAL_FALLBACK)
                self.model = self._routing.model_id
                self.provider = self._routing.provider
                self._anthropic = None
                try:
                    self._openrouter = get_openrouter_client()
                except ValueError:
                    self._anthropic = Anthropic(api_key=config.anthropic_api_key)
                    self._openrouter = None
                    self.provider = Provider.ANTHROPIC
                    self.model = config.model_sonnet
        else:
            self._anthropic = None
            try:
                self._openrouter = get_openrouter_client()
            except ValueError:
                logger.warning(
                    f"[{self.agent_id}] OPENROUTER_API_KEY not set, falling back to Anthropic"
                )
                self._anthropic = Anthropic(api_key=config.anthropic_api_key)
                self._openrouter = None
                self.provider = Provider.ANTHROPIC
                self.model = config.model_sonnet

    def get_system_prompt(self) -> str:
        """Build full system prompt with BE lens injection."""
        try:
            from pathlib import Path
            from control_plane.prompts import compile_prompt_bundle_for_agent, render_runtime_prompt

            authoring_dir = Path(__file__).resolve().parents[1] / "agents"
            bundle = compile_prompt_bundle_for_agent(
                agent_id=self.agent_id,
                authoring_dir=authoring_dir,
                fallback_name=self.agent_name,
                fallback_role=self.role,
                fallback_system_prompt=self.system_prompt,
            )
            compiled_prompt = render_runtime_prompt(bundle)
            return f"{compiled_prompt}\n\n{BE_LENS}"
        except Exception:
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

        if self.provider == Provider.LOCAL and self._ollama:
            result = self._run_local(full_prompt, max_tokens)
        elif self.provider == Provider.OPENROUTER and self._openrouter:
            result = self._run_openrouter(full_prompt, max_tokens)
        else:
            result = self._run_anthropic(full_prompt, max_tokens)

        duration_ms = int((time.time() - start) * 1000)
        result["duration_ms"] = duration_ms

        # Log run to Supabase
        self._log_run(result)

        return result

    def _run_openrouter(self, full_prompt: str, max_tokens: int) -> dict:
        """Execute via OpenRouter (Gemini, DeepSeek, GLM, GPT-4o)."""
        resp = self._openrouter.chat(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}],
            system=self.get_system_prompt(),
            max_tokens=max_tokens,
        )

        # Use cost from OpenRouter response, or estimate from router
        cost = resp.cost_usd
        if not cost:
            pricing = _MODEL_PRICING.get(self._routing.tier, {})
            cost = (
                resp.input_tokens * pricing.get("input_per_1m", 0) / 1_000_000
                + resp.output_tokens * pricing.get("output_per_1m", 0) / 1_000_000
            )

        return {
            "text": resp.text,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "cost_usd": round(cost, 6),
            "model": self.model,
            "provider": "openrouter",
            "tier": self._routing.tier.value,
        }

    def _run_local(self, full_prompt: str, max_tokens: int) -> dict:
        """Execute via Ollama (M5 Max local inference — zero cost)."""
        resp = self._ollama.chat(
            messages=[{"role": "user", "content": full_prompt}],
            system=self.get_system_prompt(),
            max_tokens=max_tokens,
        )
        return {
            "text": resp.text,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "cost_usd": 0.0,
            "model": resp.model,
            "provider": "local",
            "tier": "local",
        }

    def _run_anthropic(self, full_prompt: str, max_tokens: int) -> dict:
        """Execute via Anthropic direct (legacy / fallback)."""
        response = self._anthropic.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.get_system_prompt(),
            messages=[{"role": "user", "content": full_prompt}],
        )

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (
            input_tokens * config.cost_per_m_input.get(self.model, 3.0) / 1_000_000
            + output_tokens * config.cost_per_m_output.get(self.model, 15.0) / 1_000_000
        )

        return {
            "text": response.content[0].text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "model": self.model,
            "provider": "anthropic",
            "tier": "sonnet",
        }

    def _log_run(self, result: dict) -> None:
        """Log agent run to Supabase for cost tracking."""
        try:
            from supabase import create_client
            sb = create_client(config.supabase_url, config.supabase_key)
            sb.table("agent_runs").insert({
                "company_id": self.company_id,
                "agent_id": self.agent_id,
                "model": result.get("model", self.model),
                "input_tokens": result.get("input_tokens", 0),
                "output_tokens": result.get("output_tokens", 0),
                "cost_usd": float(result.get("cost_usd", 0)),
                "duration_ms": result.get("duration_ms", 0),
            }).execute()
        except Exception:
            pass  # Don't fail on logging errors

    def run_json(self, prompt: str, max_tokens: int = 4096) -> dict:
        """Execute and parse JSON from the response."""
        result = self.run(prompt, max_tokens)
        text = result["text"]
        # Extract JSON from response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            try:
                parsed = json.loads(text[start:end])
                result["parsed"] = parsed
            except json.JSONDecodeError:
                result["parsed"] = None
        else:
            result["parsed"] = None
        return result
