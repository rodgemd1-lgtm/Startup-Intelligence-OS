"""Knowledge graph operations — entity resolution, relationship management, traversal."""
from __future__ import annotations

from jake_brain.store import BrainStore
from jake_brain.extractor import Extraction


class KnowledgeGraph:
    """Manages Jake's knowledge graph (entities + relationships)."""

    def __init__(self, store: BrainStore | None = None):
        self.store = store or BrainStore()

    def process_extraction(
        self,
        extraction: Extraction,
        episode_id: str | None = None,
    ) -> dict:
        """Process an extraction — upsert entities, update mention counts, create relationships.

        Returns summary of what was created/updated.
        """
        created_entities = []
        updated_entities = []
        created_relationships = []

        # Process people
        for person in extraction.people:
            entity = self._resolve_person(person)
            if entity:
                if entity.get("_created"):
                    created_entities.append(entity["name"])
                else:
                    updated_entities.append(entity["name"])

        # Process project as entity
        if extraction.project:
            self.store.upsert_entity(
                name=extraction.project,
                entity_type="project",
                importance=0.6,
            )

        # Link people to project if both present
        if extraction.project and extraction.people:
            project_entity = self.store.find_entity(extraction.project, "project")
            if project_entity:
                for person in extraction.people:
                    person_entity = self._resolve_person(person)
                    if person_entity:
                        self.store.upsert_relationship(
                            source_entity_id=person_entity["id"],
                            target_entity_id=project_entity["id"],
                            relationship_type="discussed_in",
                            source_episode_id=episode_id,
                        )
                        created_relationships.append(
                            f"{person_entity['name']} → discussed_in → {extraction.project}"
                        )

        return {
            "created_entities": created_entities,
            "updated_entities": updated_entities,
            "created_relationships": created_relationships,
        }

    def _resolve_person(self, name: str) -> dict | None:
        """Resolve a person name to an entity, creating if needed.

        Uses strict matching for now (exact name + type).
        """
        # Normalize name
        normalized = name.strip().lower()

        # Map known aliases to canonical names
        aliases = {
            "mike": "Mike Rodgers",
            "mike rodgers": "Mike Rodgers",
            "james": "James Loehr",
            "james loehr": "James Loehr",
            "jacob": "Jacob",
            "alex": "Alex",
            "jen": "Jen",
            "matt": "Matt Cohlmia",
            "matt cohlmia": "Matt Cohlmia",
            "jordan": "Jordan Voss",
            "jordan voss": "Jordan Voss",
            "ellen": "Ellen",
        }

        canonical = aliases.get(normalized, name.title())

        # Determine entity type
        family_members = {"James Loehr", "Jacob", "Alex", "Jen"}
        entity_type = "family_member" if canonical in family_members else "person"

        # Check if exists
        existing = self.store.find_entity(canonical, entity_type)
        if existing:
            # Bump mention count (handled by upsert_entity)
            self.store.upsert_entity(
                name=canonical,
                entity_type=entity_type,
            )
            return existing

        # Create new
        entity = self.store.upsert_entity(
            name=canonical,
            entity_type=entity_type,
            importance=0.6 if entity_type == "family_member" else 0.5,
        )
        entity["_created"] = True
        return entity

    def seed_initial_entities(self) -> dict:
        """Seed the knowledge graph with known entities and relationships.

        Call this once after table creation to populate Mike's known world.
        """
        stats = {"entities": 0, "relationships": 0}

        # --- People & Family ---
        mike = self.store.upsert_entity("Mike Rodgers", "person", {
            "role": "founder, co-founder of 3 companies",
            "email": "mrodgers@outlook.com",
        }, importance=1.0)

        james = self.store.upsert_entity("James Loehr", "family_member", {
            "relationship": "husband",
        }, importance=0.9)

        jacob = self.store.upsert_entity("Jacob", "family_member", {
            "age": 15,
            "interests": "football (OL/DL)",
            "status": "recruiting target",
        }, importance=0.9)

        alex = self.store.upsert_entity("Alex", "family_member", {
            "age": 12,
            "note": "Alex Recruiting app named after him",
        }, importance=0.9)

        jen = self.store.upsert_entity("Jen", "family_member", {
            "relationship": "ex-wife",
            "note": "Mike interacts with her regularly",
        }, importance=0.7)

        matt = self.store.upsert_entity("Matt Cohlmia", "person", {
            "role": "Oracle Health executive",
            "relationship": "stakeholder",
        }, importance=0.8)

        jordan = self.store.upsert_entity("Jordan Voss", "person", {
            "context": "referenced in quality bar test",
        }, importance=0.5)

        stats["entities"] += 7

        # --- Companies ---
        oracle = self.store.upsert_entity("Oracle Health", "company", {
            "type": "employer / AI enablement",
        }, importance=0.9)

        startup_os = self.store.upsert_entity("Startup Intelligence OS", "company", {
            "type": "personal project",
            "description": "Susan-powered multi-agent platform",
        }, importance=0.9)

        alex_rec = self.store.upsert_entity("Alex Recruiting", "company", {
            "type": "personal project",
            "description": "Jacob's football recruiting app",
        }, importance=0.8)

        transformfit = self.store.upsert_entity("TransformFit", "company", {
            "type": "future company",
            "status": "planned",
        }, importance=0.5)

        virtual_arch = self.store.upsert_entity("Virtual Architect", "company", {
            "type": "future company",
            "status": "planned",
        }, importance=0.5)

        stats["entities"] += 5

        # --- Projects ---
        hermes = self.store.upsert_entity("Hermes V5", "project", {
            "description": "OpenClaw-powered AI assistant",
            "status": "active build",
        }, importance=0.9)

        susan = self.store.upsert_entity("Susan Team Architect", "project", {
            "description": "73-agent RAG-powered foundry",
            "chunks": "94K+",
        }, importance=0.8)

        brain = self.store.upsert_entity("The Brain (Phase 2)", "project", {
            "description": "Jake's 4-layer cognitive memory engine",
            "status": "building now",
        }, importance=0.9)

        stats["entities"] += 3

        # --- Relationships ---
        rels = [
            (mike["id"], james["id"], "spouse_of", {}),
            (mike["id"], jacob["id"], "parent_of", {}),
            (mike["id"], alex["id"], "parent_of", {}),
            (mike["id"], jen["id"], "ex_spouse_of", {}),
            (mike["id"], oracle["id"], "works_at", {"role": "AI enablement"}),
            (mike["id"], startup_os["id"], "works_at", {"role": "founder"}),
            (mike["id"], alex_rec["id"], "works_at", {"role": "founder"}),
            (matt["id"], oracle["id"], "stakeholder_of", {"role": "executive"}),
            (jacob["id"], alex_rec["id"], "named_after", {"note": "app for his recruiting"}),
            (alex["id"], alex_rec["id"], "named_after", {"note": "app named after Alex"}),
            (hermes["id"], startup_os["id"], "relates_to", {}),
            (susan["id"], startup_os["id"], "relates_to", {}),
            (brain["id"], hermes["id"], "relates_to", {"note": "brain powers hermes"}),
        ]

        for src, tgt, rel_type, props in rels:
            self.store.upsert_relationship(src, tgt, rel_type, properties=props)
            stats["relationships"] += 1

        return stats
