#!/usr/bin/env python3
"""CLI for Jake's Brain — test, seed, search, and manage cognitive memory.

Usage:
    python scripts/jake_brain_cli.py seed          # Seed initial entities + relationships
    python scripts/jake_brain_cli.py stats         # Show brain statistics
    python scripts/jake_brain_cli.py search "query" # Search across all layers
    python scripts/jake_brain_cli.py person "name"  # Recall everything about a person
    python scripts/jake_brain_cli.py ingest "text"  # Ingest a text chunk
    python scripts/jake_brain_cli.py consolidate    # Run consolidation pipeline
    python scripts/jake_brain_cli.py test           # Run end-to-end smoke test
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jake_brain.pipeline import BrainPipeline


def cmd_seed(pipeline: BrainPipeline) -> None:
    """Seed initial entities and relationships."""
    print("Seeding Jake's brain with initial entities and relationships...")
    result = pipeline.seed()
    print(f"  Entities created/updated: {result['entities']}")
    print(f"  Relationships created: {result['relationships']}")
    print("Done.")


def cmd_stats(pipeline: BrainPipeline) -> None:
    """Show brain statistics."""
    summary = pipeline.stats()
    stats = summary["stats"]
    print("\n=== Jake's Brain Stats ===")
    for table, count in stats.items():
        print(f"  {table:20s}: {count:,}")
    print(f"\n  Total memories: {sum(stats.values()):,}")
    if summary["top_facts"]:
        print("\n  Top semantic facts:")
        for i, fact in enumerate(summary["top_facts"][:5], 1):
            print(f"    {i}. {fact}")
    print()


def cmd_search(pipeline: BrainPipeline, query: str, project: str | None = None) -> None:
    """Search across all memory layers."""
    print(f'\nSearching brain for: "{query}"')
    if project:
        print(f"  Project filter: {project}")

    results = pipeline.retriever.search(query, project=project, top_k=10)
    if not results:
        print("  No memories found.")
        return

    print(f"\n  Found {len(results)} memories:\n")
    for i, mem in enumerate(results, 1):
        layer = mem["layer"].upper()
        score = mem["composite_score"]
        content = mem["content"][:200].replace("\n", " ")
        print(f"  {i}. [{layer} score={score:.3f}] {content}")
    print()


def cmd_person(pipeline: BrainPipeline, name: str) -> None:
    """Recall everything about a person."""
    print(f'\nRecalling everything about: "{name}"')
    result = pipeline.recall_person(name)

    if result["entity"]:
        e = result["entity"]
        print(f"\n  Entity: {e['name']} ({e['entity_type']})")
        print(f"  Importance: {e['importance']}")
        if e.get("properties"):
            print(f"  Properties: {json.dumps(e['properties'], indent=4)}")
    else:
        print(f"\n  No entity found for '{name}'")

    if result["graph"]:
        print(f"\n  Knowledge Graph ({len(result['graph'])} connected entities):")
        for node in result["graph"]:
            depth_indent = "    " * (node["depth"] + 1)
            print(f"{depth_indent}{node['relationship']} → {node['entity_name']} ({node['entity_type']})")

    if result["memories"]:
        print(f"\n  Related Memories ({len(result['memories'])}):")
        for mem in result["memories"][:5]:
            layer = mem["layer"].upper()
            score = mem["composite_score"]
            content = mem["content"][:150].replace("\n", " ")
            print(f"    [{layer} {score:.3f}] {content}")
    print()


def cmd_ingest(pipeline: BrainPipeline, text: str) -> None:
    """Ingest a text chunk into the brain."""
    print(f"Ingesting text ({len(text)} chars)...")
    result = pipeline.ingest_conversation(text)
    print(f"  Episode ID: {result['episode_id']}")
    print(f"  Extraction: {json.dumps(result['extraction'], indent=2)}")
    print(f"  Graph: {json.dumps(result['graph'], indent=2)}")
    print(f"  Semantic facts stored: {result['semantic_stored']}")
    print(f"  Procedural patterns stored: {result['procedural_stored']}")


def cmd_consolidate(pipeline: BrainPipeline) -> None:
    """Run consolidation pipeline."""
    print("Running consolidation...")
    result = pipeline.consolidate()
    print(f"  Episodic → Semantic: {json.dumps(result['episodic_to_semantic'])}")
    print(f"  Contradictions found: {result['contradictions']}")


def cmd_test(pipeline: BrainPipeline) -> None:
    """End-to-end smoke test."""
    print("\n=== Jake Brain Smoke Test ===\n")

    # 1. Ingest a test conversation
    test_text = (
        "Mike and James discussed Jacob's football schedule. Jacob has a game "
        "on Saturday against Lincoln High. Mike decided to attend the game instead "
        "of working on the Oracle Health presentation. Matt Cohlmia said the "
        "presentation can wait until Monday."
    )
    print("1. Ingesting test conversation...")
    result = pipeline.ingest_conversation(
        text=test_text,
        session_id="smoke-test-001",
        source="smoke-test",
        source_type="manual",
    )
    print(f"   Episode: {result['episode_id']}")
    print(f"   People: {result['extraction']['people']}")
    print(f"   Topics: {result['extraction']['topics']}")
    print(f"   Decisions: {result['extraction']['decisions']}")
    print(f"   Importance: {result['extraction']['importance']}")

    # 2. Search for it
    print("\n2. Searching for 'Jacob football game'...")
    memories = pipeline.retriever.search("Jacob football game", top_k=3)
    if memories:
        for mem in memories:
            print(f"   [{mem['layer']} score={mem['composite_score']:.3f}] {mem['content'][:100]}")
    else:
        print("   No results (brain search RPC may not be deployed yet)")

    # 3. Check stats
    print("\n3. Brain stats:")
    stats = pipeline.store.brain_stats()
    for table, count in stats.items():
        print(f"   {table}: {count}")

    print("\n=== Smoke Test Complete ===\n")


def main():
    parser = argparse.ArgumentParser(description="Jake's Brain CLI")
    parser.add_argument("command", choices=["seed", "stats", "search", "person", "ingest", "consolidate", "test"])
    parser.add_argument("query", nargs="?", default="", help="Query text (for search/person/ingest)")
    parser.add_argument("--project", help="Project filter for search")
    args = parser.parse_args()

    pipeline = BrainPipeline()

    if args.command == "seed":
        cmd_seed(pipeline)
    elif args.command == "stats":
        cmd_stats(pipeline)
    elif args.command == "search":
        cmd_search(pipeline, args.query, args.project)
    elif args.command == "person":
        cmd_person(pipeline, args.query)
    elif args.command == "ingest":
        cmd_ingest(pipeline, args.query)
    elif args.command == "consolidate":
        cmd_consolidate(pipeline)
    elif args.command == "test":
        cmd_test(pipeline)


if __name__ == "__main__":
    main()
