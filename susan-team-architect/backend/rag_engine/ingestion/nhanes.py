"""NHANES health data synthesis — generates population health profiles from CDC data."""
from __future__ import annotations
import os
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_text
from susan_core.config import config


class NHANESIngestor(BaseIngestor):
    """Synthesize NHANES population health data for user persona grounding."""

    def ingest(
        self,
        source: str = "",
        company_id: str = "shared",
        data_type: str = "user_research",
        agent_id: str | None = None,
        num_profiles: int = 20,
        **kwargs,
    ) -> int:
        """Generate synthetic user profiles grounded in NHANES population data.

        Args:
            source: Ignored
            num_profiles: Number of diverse profiles to generate
        """
        # Route through jake_cost (OpenRouter default, Anthropic fallback)
        if os.environ.get("FORCE_ANTHROPIC"):
            from anthropic import Anthropic
            client, model, provider = Anthropic(api_key=config.anthropic_api_key), config.model_sonnet, "anthropic"
        else:
            try:
                from jake_cost.router import ModelRouter
                from jake_cost.openrouter_client import OpenRouterClient
                router = ModelRouter()
                decision = router.route("content_generation", complexity="medium")
                client, model, provider = OpenRouterClient(), decision.model_id, "openrouter"
            except ImportError:
                from anthropic import Anthropic
                client, model, provider = Anthropic(api_key=config.anthropic_api_key), config.model_sonnet, "anthropic"

        prompt = f"""Based on your knowledge of NHANES (National Health and Nutrition Examination Survey)
population health data from the CDC, generate {num_profiles} diverse, realistic user profiles
for a fitness app. Each profile should be grounded in real population health statistics.

For each profile include:
- Demographics: age, sex, BMI category, activity level
- Health markers: resting heart rate range, blood pressure category, cholesterol status
- Fitness level: VO2max estimate, strength benchmark, flexibility
- Behavioral factors: motivation type, barriers to exercise, dietary patterns
- App usage prediction: likely engagement pattern, churn risk factors

Make profiles diverse across:
- Age ranges (18-65+)
- BMI categories (underweight, normal, overweight, obese)
- Activity levels (sedentary, lightly active, moderately active, very active)
- Health conditions (healthy, pre-diabetic, hypertensive, etc.)
- Motivation types (weight loss, muscle gain, health improvement, athletic performance)

Format each profile as a standalone paragraph. Separate profiles with ---"""

        if provider == "openrouter":
            result = client.chat(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=8192)
            text = result["content"]
        else:
            response = client.messages.create(model=model, max_tokens=8192, messages=[{"role": "user", "content": prompt}])
            text = response.content[0].text
        profiles = [p.strip() for p in text.split("---") if p.strip()]

        chunks = self._make_chunks(
            texts=profiles,
            data_type=data_type,
            company_id=company_id,
            agent_id=agent_id,
            source="nhanes:synthetic_profiles",
            metadata={"type": "user_persona", "grounding": "NHANES"},
        )
        return self.retriever.store_chunks(chunks)
