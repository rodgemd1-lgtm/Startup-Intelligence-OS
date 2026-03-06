"""NHANES health data synthesis — generates population health profiles from CDC data."""
from __future__ import annotations
from anthropic import Anthropic
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
        client = Anthropic(api_key=config.anthropic_api_key)

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

        response = client.messages.create(
            model=config.model_sonnet,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )

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
