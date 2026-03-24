# Agent Registry

Machine-readable registry of all Susan agents, extracted from `susan-team-architect/agents/*.md`.

## Stats

- **Total agents:** 81
- **Groups:** 12

## Groups

| Group | Count | Purpose |
|-------|-------|---------|
| orchestration | 1 | System orchestration (Susan) |
| strategy | 6 | Business strategy, legal, finance, partnerships, fundraising |
| product | 9 | UX, product management, brand, accessibility, conversation design |
| engineering | 8 | Full-stack, AI/ML, data science, security, QA, knowledge engineering |
| science | 7 | Exercise science, nutrition, sleep, workout programming |
| psychology | 3 | Behavioral economics, sports psychology, gamification |
| growth | 7 | Growth, community, customer success, PR, ASO, outreach |
| research | 6 | Research direction, ops, web/arxiv/reddit/appstore researchers |
| studio | 13 | Content studios: decks, landing pages, marketing, articles, memos |
| film_studio | 16 | Film production: directing, writing, cinematography, editing, VFX, audio |
| slideworks | 3 | Consulting-quality slide deck pipeline (strategy, design, build) |
| oracle_health | 2 | Oracle Health marketing and product marketing |

## Routing

The `routing` section maps question categories to recommended agent teams. Use it for automatic agent selection when a query type is known.

## Usage

```python
import json

with open("registry.json") as f:
    registry = json.load(f)

# Get all agents in a group
engineering = registry["groups"]["engineering"]

# Get agent details
atlas = registry["agents"]["atlas-engineering"]
print(atlas["description"])

# Route a question type to agents
team = registry["routing"]["strategy_question"]
```

## Source

Generated from frontmatter in `susan-team-architect/agents/*.md`.
