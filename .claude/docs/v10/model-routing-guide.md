# V10.0 Model Routing Guide

## The 80% Rule
From Anthropic's BrowseComp research: token usage alone explains 80% of performance variance. This means efficient token allocation matters more than prompt engineering.

## Routing Table

| Task Category | Recommended Model | Rationale |
|--------------|-------------------|-----------|
| **Search/Find/List** | Haiku | Low complexity, high volume |
| **Syntax check/Lint** | Haiku | Pattern matching, no reasoning |
| **Simple code review** | Haiku | Checklist-based evaluation |
| **Feature implementation** | Sonnet | Balanced quality and cost |
| **Complex debugging** | Sonnet | Requires reasoning chains |
| **Test generation** | Sonnet | Needs understanding of intent |
| **Research synthesis** | Sonnet | Multi-source integration |
| **Architecture design** | Opus | High-stakes, complex tradeoffs |
| **Strategic decisions** | Opus | Nuanced reasoning required |
| **Novel problem solving** | Opus | Maximum capability needed |

## Cost Multipliers

| Model | Relative Cost | When to Use |
|-------|--------------|-------------|
| Haiku | 1x (baseline) | 60% of tasks — search, validation, formatting |
| Sonnet | 5x | 30% of tasks — implementation, synthesis |
| Opus | 15x | 10% of tasks — architecture, strategy, novel |

## Blended Cost Target
If 60% Haiku + 30% Sonnet + 10% Opus:
- Blended cost = 0.6(1) + 0.3(5) + 0.1(15) = **3.6x** vs. 15x all-Opus
- **76% cost reduction** with minimal quality impact

## Implementation

### In Agent Definitions
```yaml
model: haiku   # for search/validation agents
model: sonnet  # for implementation agents
model: opus    # for orchestrator/lead agents
```

### In Agent Tool Calls
```json
{
  "subagent_type": "Explore",
  "model": "haiku",
  "prompt": "Find all files matching..."
}
```

### Via Hook Advisory
The `model-router.sh` hook provides cost optimization suggestions when model isn't specified.

## Anti-Patterns
- Using Opus for file search (Haiku is 15x cheaper and equally accurate)
- Using Haiku for architecture decisions (false economy — rework costs more)
- Not specifying model (defaults to parent, which may be Opus)
- Running sequential tasks that could be parallel (time cost)
