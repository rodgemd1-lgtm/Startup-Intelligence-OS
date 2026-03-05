# Algorithm R&D — ML Pipelines, Experimentation & Personalization

> Recommendation engines, search ranking, A/B testing, and ML infrastructure.

---

## 1. ML Pipeline Architecture

### Production ML Pipeline Stages
```
Data Collection → Feature Engineering → Model Training →
Evaluation → Deployment → Monitoring → Retraining
```

### Pipeline Tools
| Stage | Tool | Purpose |
|-------|------|---------|
| **Data ingestion** | Airbyte, Fivetran | ETL/ELT from sources |
| **Feature store** | Feast, Tecton | Feature engineering & serving |
| **Training** | Modal, Replicate, Lambda | GPU compute |
| **Experiment tracking** | Weights & Biases, MLflow | Track experiments |
| **Model serving** | Replicate, Modal, BentoML | Inference API |
| **Monitoring** | Arize, WhyLabs | Model drift detection |
| **Orchestration** | Prefect, Dagster, Airflow | Pipeline orchestration |

---

## 2. Recommendation Engine Patterns

### Collaborative Filtering
- **User-based**: "Users similar to you also liked X"
- **Item-based**: "Users who liked A also liked B"
- **Matrix factorization**: SVD, ALS for latent factors
- Best for: E-commerce, content, social

### Content-Based Filtering
- Use embeddings (OpenAI, Cohere) to represent items
- Cosine similarity for nearest-neighbor search
- Best for: Articles, products with rich metadata

### Hybrid Approach (Recommended)
```
Score = α × collaborative_score + β × content_score + γ × context_score
```
Where context = time, location, device, session behavior

### RAG-Enhanced Recommendations (2026 Pattern)
1. Embed all items into vector database (Pinecone/Qdrant)
2. Embed user query / behavior into same space
3. Retrieve top-k candidates via ANN search
4. Re-rank with LLM considering user context
5. Return personalized, explainable recommendations

---

## 3. Search Ranking

### Search Architecture
```
Query → Query Understanding → Retrieval → Ranking → Re-ranking → Results
```

### Implementation Stack
| Component | Tool |
|-----------|------|
| **Full-text search** | Meilisearch, Typesense, Elasticsearch |
| **Vector search** | Pinecone, Qdrant, Weaviate |
| **Hybrid search** | Meilisearch (built-in), custom blend |
| **Query understanding** | Claude API for intent classification |
| **Re-ranking** | Cohere Rerank, cross-encoder models |

### Search Quality Metrics
| Metric | What It Measures |
|--------|-----------------|
| **MRR** (Mean Reciprocal Rank) | Position of first relevant result |
| **NDCG** (Normalized DCG) | Quality of ranking order |
| **Precision@K** | % relevant results in top K |
| **Recall@K** | % of all relevant results found in top K |
| **Click-through rate** | User engagement with results |
| **Zero-result rate** | Queries returning no results |

---

## 4. A/B Testing & Experimentation

### Experimentation Framework
1. **Hypothesis**: "Changing X will improve Y by Z%"
2. **Design**: Control vs. variant, sample size calculation
3. **Implement**: Feature flag the change
4. **Run**: Minimum 1-2 weeks, sufficient sample size
5. **Analyze**: Statistical significance (p < 0.05)
6. **Decision**: Ship, iterate, or kill

### Feature Flag Tools
| Tool | Purpose | Pricing |
|------|---------|---------|
| **LaunchDarkly** | Enterprise feature flags | $10/seat/mo+ |
| **PostHog** | Feature flags + analytics | Free tier |
| **Statsig** | Feature gates + experiments | Free tier |
| **Flagsmith** | Open-source feature flags | Free (self-hosted) |
| **GrowthBook** | Open-source A/B testing | Free (self-hosted) |

### Statistical Significance
- **Sample size calculator**: Use Evan Miller's tool
- **Minimum detectable effect**: Usually 5-10% for most tests
- **Duration**: At least 1 full business cycle (7 days minimum)
- **Sequential testing**: Use Bayesian methods for early stopping

---

## 5. Personalization Engine

### Personalization Layers
| Layer | What It Personalizes | Data Required |
|-------|---------------------|---------------|
| **Content** | What users see | Behavior, preferences |
| **Layout** | How content is arranged | Engagement patterns |
| **Messaging** | Tone, copy, CTAs | Segment, persona |
| **Timing** | When to engage | Activity patterns |
| **Pricing** | What they pay (carefully) | Segment, willingness |

### Implementation Approach
1. Start with **segment-based** (3-5 personas)
2. Graduate to **behavior-based** (real-time signals)
3. Evolve to **ML-driven** (automated optimization)

---

## 6. Data Infrastructure

### Modern Data Stack for Startups
| Layer | Tool | Purpose |
|-------|------|---------|
| **Warehouse** | BigQuery, Snowflake, ClickHouse | Central data store |
| **ETL** | Airbyte (open-source), Fivetran | Data ingestion |
| **Transform** | dbt | SQL transformations |
| **Analytics** | PostHog, Metabase | Dashboards, queries |
| **Reverse ETL** | Census, Hightouch | Sync data to tools |
| **Orchestration** | Dagster, Prefect | Pipeline scheduling |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
