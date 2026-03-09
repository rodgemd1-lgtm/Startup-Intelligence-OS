"""Configuration for Susan Team Architect."""
import os
from pathlib import Path
from dataclasses import dataclass

# Load .env file if present
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

@dataclass
class Config:
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    voyage_api_key: str = os.environ.get("VOYAGE_API_KEY", "")
    supabase_url: str = os.environ.get("SUPABASE_URL", "")
    supabase_key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")
    firecrawl_api_key: str = os.environ.get("FIRECRAWL_API_KEY", "")
    exa_api_key: str = os.environ.get("EXA_API_KEY", "")
    jina_api_key: str = os.environ.get("JINA_API_KEY", "")

    # Model routing
    model_opus: str = "claude-opus-4-6"
    model_sonnet: str = "claude-sonnet-4-6"
    model_haiku: str = "claude-haiku-4-5-20251001"

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = Path(__file__).parent.parent / "data"
    artifacts_dir: Path = Path(__file__).parent.parent / "artifacts"
    phase_cache_dir: Path = Path(__file__).parent.parent / "artifacts" / "phase_cache"
    domains_dir: Path = Path(__file__).parent.parent / "data" / "domains"
    scrape_manifests_dir: Path = Path(__file__).parent.parent / "data" / "scrape_manifests"
    fitness_domain_dir: Path = Path(__file__).parent.parent / "data" / "domains" / "fitness_app_intelligence"
    companies_dir: Path = Path.cwd() / "companies"

    # RAG settings
    chunk_size: int = 500  # tokens
    chunk_overlap: int = 50  # tokens
    embedding_model: str = "voyage-3"
    embedding_dim: int = 1024
    rag_top_k: int = 5

    # Cost tracking (per 1M tokens)
    cost_per_m_input: dict = None
    cost_per_m_output: dict = None

    def __post_init__(self):
        self.cost_per_m_input = {
            self.model_opus: 15.0,
            self.model_sonnet: 3.0,
            self.model_haiku: 0.25,
        }
        self.cost_per_m_output = {
            self.model_opus: 75.0,
            self.model_sonnet: 15.0,
            self.model_haiku: 1.25,
        }


config = Config()
