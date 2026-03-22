"""Context Assembler — build optimal brain context per request.

Given an intent (user query or task), pulls the MINIMUM relevant context from
all 4 brain layers + entity graph. Returns a structured ContextBundle that can
be injected into any prompt without blowing context budgets.

Design goals:
  - Minimum viable context: don't pull 500 memories when 10 will do
  - Layer-aware: each layer has a different role in the context
  - Budget-aware: caller specifies token budget, assembler respects it
  - Deterministic: same query → same bundle (for testing/reproducibility)
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("jake.context")

SUSAN_BACKEND = "/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend"
if SUSAN_BACKEND not in sys.path:
    sys.path.insert(0, SUSAN_BACKEND)


@dataclass
class ContextBundle:
    """Assembled context for a single request."""

    intent: str
    memories: list[dict] = field(default_factory=list)          # from brain_search
    entities: list[dict] = field(default_factory=list)          # from entity graph
    relationships: list[dict] = field(default_factory=list)     # graph edges
    recent_working: list[dict] = field(default_factory=list)    # current session
    token_estimate: int = 0
    assembled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_prompt_block(self, max_memories: int = 8) -> str:
        """Format as a prompt-injectable context block."""
        lines = ["<jake_brain_context>"]

        # Working memory (highest recency)
        if self.recent_working:
            lines.append("\n## Current Session Context")
            for w in self.recent_working[:3]:
                lines.append(f"- {w.get('content', '')[:200]}")

        # Key entities
        if self.entities:
            lines.append("\n## Relevant People & Projects")
            for e in self.entities[:5]:
                name = e.get("name", "")
                etype = e.get("entity_type", "")
                attrs = e.get("attributes", {})
                line = f"- {name} ({etype})"
                if attrs:
                    key_attrs = ", ".join(f"{k}: {v}" for k, v in list(attrs.items())[:3])
                    line += f": {key_attrs}"
                lines.append(line)

        # Relationships
        if self.relationships:
            lines.append("\n## Relationships")
            for r in self.relationships[:5]:
                src = r.get("source_name", r.get("entity_id", "?"))
                rel = r.get("relation_type", "relates to")
                tgt = r.get("target_name", r.get("target_id", "?"))
                lines.append(f"- {src} {rel} {tgt}")

        # Memories (most relevant first)
        if self.memories:
            lines.append("\n## Relevant Memories")
            for mem in self.memories[:max_memories]:
                layer = mem.get("layer", "?").upper()
                score = mem.get("composite_score", 0)
                content = mem.get("content", "")[:300]
                lines.append(f"[{layer} {score:.2f}] {content}")

        lines.append("</jake_brain_context>")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "memory_count": len(self.memories),
            "entity_count": len(self.entities),
            "relationship_count": len(self.relationships),
            "working_count": len(self.recent_working),
            "token_estimate": self.token_estimate,
            "assembled_at": self.assembled_at.isoformat(),
        }


class ContextAssembler:
    """Pull minimum context from brain layers for a given intent."""

    # Approximate chars-per-token
    CHARS_PER_TOKEN: int = 4

    def __init__(self, retriever=None, store=None):
        """Lazy-init retriever and store to avoid import cost at module load."""
        self._retriever = retriever
        self._store = store

    def _get_retriever(self):
        if self._retriever is None:
            from jake_brain.retriever import BrainRetriever
            self._retriever = BrainRetriever()
        return self._retriever

    def _get_store(self):
        if self._store is None:
            from jake_brain.store import BrainStore
            self._store = BrainStore()
        return self._store

    def assemble(
        self,
        intent: str,
        project: str | None = None,
        people: list[str] | None = None,
        session_id: str | None = None,
        top_memories: int = 10,
        top_entities: int = 5,
        token_budget: int = 4000,
    ) -> ContextBundle:
        """Assemble optimal context for the given intent.

        Args:
            intent: The user's query or task description.
            project: Filter memories to this project.
            people: Boost/filter by these people.
            session_id: Include working memory for this session.
            top_memories: Max memories to pull.
            top_entities: Max entities to pull.
            token_budget: Approximate token budget for the bundle.

        Returns:
            ContextBundle with all relevant context assembled.
        """
        bundle = ContextBundle(intent=intent)
        budget_remaining = token_budget

        try:
            retriever = self._get_retriever()
            store = self._get_store()

            # 1. Semantic search across brain layers
            memories = retriever.search(
                query=intent,
                project=project,
                people=people,
                top_k=top_memories,
            )
            # Trim to budget
            memories_trimmed = []
            for mem in memories:
                content_len = len(mem.get("content", ""))
                token_cost = content_len // self.CHARS_PER_TOKEN + 10
                if token_cost > budget_remaining:
                    break
                memories_trimmed.append(mem)
                budget_remaining -= token_cost
            bundle.memories = memories_trimmed

            # 2. Entity resolution — find entities mentioned in the intent
            mentioned_entities = self._extract_entity_hints(intent, people)
            entities = []
            relationships = []
            for name in mentioned_entities[:top_entities]:
                entity = store.find_entity(name)
                if entity:
                    entities.append(entity)
                    # Pull graph edges (1-hop)
                    graph = store.get_entity_graph(entity["id"], max_depth=1)
                    for rel in graph[:3]:
                        if rel not in relationships:
                            relationships.append(rel)

            bundle.entities = entities
            bundle.relationships = relationships

            # 3. Working memory for current session
            if session_id:
                working = store.get_session_working(session_id)
                bundle.recent_working = working[:5]

        except Exception as e:
            logger.error(f"Context assembly failed: {e}")
            # Return partial bundle rather than failing

        # Estimate tokens
        prompt_text = bundle.to_prompt_block()
        bundle.token_estimate = len(prompt_text) // self.CHARS_PER_TOKEN

        return bundle

    def assemble_for_morning_brief(self) -> ContextBundle:
        """Special assembly for morning brief — pulls all daily-relevant context."""
        bundle = ContextBundle(intent="morning brief and daily priorities")

        try:
            retriever = self._get_retriever()
            store = self._get_store()

            # Pull all high-relevance memories from the last 48h across all sources
            from datetime import timedelta
            time_start = datetime.now(timezone.utc) - timedelta(hours=48)

            memories = retriever.search(
                query="today's priorities meetings emails tasks",
                top_k=15,
                time_start=time_start,
            )
            bundle.memories = memories

            # Pull key entities — Mike, family, current projects
            key_people = ["mike rodgers", "james", "jacob", "alex", "matt cohlmia"]
            entities = []
            for name in key_people:
                entity = store.find_entity(name)
                if not entity:
                    entity = store.find_entity(name.title())
                if entity:
                    entities.append(entity)
            bundle.entities = entities[:6]

        except Exception as e:
            logger.error(f"Morning brief context assembly failed: {e}")

        prompt_text = bundle.to_prompt_block()
        bundle.token_estimate = len(prompt_text) // self.CHARS_PER_TOKEN
        return bundle

    def assemble_person_context(self, person_name: str) -> ContextBundle:
        """Assemble full context about a specific person."""
        bundle = ContextBundle(intent=f"everything about {person_name}")

        try:
            retriever = self._get_retriever()
            recall = retriever.recall_about_person(person_name, top_k=10)

            if recall.get("entity"):
                bundle.entities = [recall["entity"]]
            bundle.relationships = recall.get("graph", [])[:10]
            bundle.memories = recall.get("memories", [])

        except Exception as e:
            logger.error(f"Person context assembly failed for {person_name}: {e}")

        prompt_text = bundle.to_prompt_block()
        bundle.token_estimate = len(prompt_text) // self.CHARS_PER_TOKEN
        return bundle

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_entity_hints(
        self,
        intent: str,
        people: list[str] | None = None,
    ) -> list[str]:
        """Extract likely entity names from the intent string."""
        hints: list[str] = list(people or [])

        # Known names to check for in intent
        KNOWN_NAMES = [
            "mike", "james", "jacob", "alex", "jen", "matt cohlmia", "matt",
            "ellen", "jordan", "oracle", "susan", "hermes",
        ]
        intent_lower = intent.lower()
        for name in KNOWN_NAMES:
            if name in intent_lower and name not in [h.lower() for h in hints]:
                hints.append(name)

        return hints[:8]  # cap to avoid over-fetching
