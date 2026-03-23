"""Unified Susan protocol CLI for slash commands, MCP, and local workflows."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from pathlib import Path as _Path
import shlex
import sys

import yaml

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from control_plane.protocols import (
    get_company_foundry_blueprint,
    get_company_status,
    get_team_manifest,
    get_visual_assets,
    refresh_company_data,
    route_company_task,
    run_susan_plan,
    search_company_knowledge,
    sync_project_protocols,
)


def _dump(payload: object) -> None:
    print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=False))


def _default_company() -> str:
    return os.environ.get("SUSAN_DEFAULT_COMPANY", "").strip() or "shared"


def _known_companies() -> set[str]:
    return {"shared", "transformfit", "oracle-health-ai-enablement", "alex-recruiting", "mike-job-studio"}


def _parse_types(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    types = [item.strip() for item in raw.split(",") if item.strip()]
    return types or None


def _query_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan query")
    parser.add_argument("query", nargs="+")
    parser.add_argument("--company", default=_default_company())
    parser.add_argument("--types", default="")
    parser.add_argument("--top-k", type=int, default=8)
    return parser


def _route_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan route")
    parser.add_argument("company", nargs="?")
    parser.add_argument("task", nargs="+")
    parser.add_argument("--top-k", type=int, default=6)
    return parser


def _status_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan status")
    parser.add_argument("company", nargs="?", default=_default_company())
    return parser


def _assets_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan assets")
    parser.add_argument("company", nargs="?", default=_default_company())
    parser.add_argument("--limit", type=int, default=20)
    return parser


def _team_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan team")
    parser.add_argument("company", nargs="?", default=_default_company())
    return parser


def _refresh_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan refresh")
    parser.add_argument("company", nargs="?", default=_default_company())
    return parser


def _plan_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan plan")
    parser.add_argument("company", nargs="?", default=_default_company())
    parser.add_argument("--mode", default="quick", choices=["quick", "deep", "design", "foundry", "full"])
    parser.add_argument("--refresh", action="store_true")
    return parser


def _foundry_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan foundry")
    parser.add_argument("company", nargs="?", default=_default_company())
    return parser


def _bootstrap_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan bootstrap")
    parser.add_argument("--config", default=str(BACKEND_ROOT / "data" / "project_protocol_targets.yaml"))
    return parser


def _raw_arguments(raw: str) -> list[str]:
    return shlex.split(raw) if raw.strip() else []


def cmd_query(args: argparse.Namespace) -> int:
    query = " ".join(args.query) if isinstance(args.query, list) else args.query
    payload = {
        "company_id": args.company,
        "query": query,
        "results": search_company_knowledge(
            query=query,
            company_id=args.company,
            data_types=_parse_types(args.types),
            top_k=args.top_k,
        ),
    }
    _dump(payload)
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    company = args.company or _default_company()
    task = " ".join(args.task) if isinstance(args.task, list) else args.task
    _dump(route_company_task(company, task, top_k=args.top_k))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    _dump(get_company_status(args.company))
    return 0


def cmd_assets(args: argparse.Namespace) -> int:
    payload = {
        "company_id": args.company,
        "assets": get_visual_assets(args.company, args.limit),
    }
    _dump(payload)
    return 0


def cmd_team(args: argparse.Namespace) -> int:
    _dump(get_team_manifest(args.company))
    return 0


def cmd_refresh(args: argparse.Namespace) -> int:
    _dump(refresh_company_data(args.company))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    _dump(run_susan_plan(args.company, mode=args.mode, refresh=args.refresh))
    return 0


def cmd_foundry(args: argparse.Namespace) -> int:
    _dump(get_company_foundry_blueprint(args.company))
    return 0


def cmd_bootstrap(args: argparse.Namespace) -> int:
    results = sync_project_protocols(Path(args.config))
    _dump({"results": results})
    return 0


def cmd_shell(subcommand: str, raw: str) -> int:
    dispatch = {
        "shell-query": (_query_parser(), cmd_query),
        "shell-route": (_route_parser(), cmd_route),
        "shell-status": (_status_parser(), cmd_status),
        "shell-assets": (_assets_parser(), cmd_assets),
        "shell-team": (_team_parser(), cmd_team),
        "shell-refresh": (_refresh_parser(), cmd_refresh),
        "shell-plan": (_plan_parser(), cmd_plan),
        "shell-foundry": (_foundry_parser(), cmd_foundry),
        "shell-bootstrap": (_bootstrap_parser(), cmd_bootstrap),
        "shell-production": (_production_parser(), cmd_production),
    }
    parser, handler = dispatch[subcommand]
    parsed = parser.parse_args(_raw_arguments(raw))
    if subcommand == "shell-route" and _default_company() != "shared":
        if parsed.company and parsed.company not in _known_companies():
            parsed.task = [parsed.company, *parsed.task]
            parsed.company = _default_company()
        elif not parsed.company:
            parsed.company = _default_company()
    return handler(parsed)


def _production_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan production")
    parser.add_argument("subcmd", choices=["start", "status", "list", "advance", "route", "auto-run"])
    parser.add_argument("target", nargs="*", default=[])
    parser.add_argument("--company", default=_default_company())
    parser.add_argument("--format", default="film",
                        choices=["film", "reel", "photo", "carousel", "image", "documentary"])
    parser.add_argument("--title", default=None)
    parser.add_argument("--force", action="store_true")
    return parser


def cmd_production(args: argparse.Namespace) -> int:
    """Manage film/image productions."""
    from susan_core.production_engine import ProductionEngine

    engine = ProductionEngine()
    subcmd = args.subcmd

    if subcmd == "start":
        brief = " ".join(args.target) if args.target else "Untitled production"
        prod = engine.start(brief=brief, company_id=args.company,
                            format=args.format, title=args.title)
        orch = engine.orchestrate(prod.production_id)
        _dump({
            "production_id": prod.production_id,
            "brief": prod.brief,
            "company_id": prod.company_id,
            "format": prod.format,
            "phase": prod.status.value,
            "agents_assigned": orch["agents_assigned_this_phase"],
            "instruction": orch["instruction"],
        })

    elif subcmd == "status":
        if not args.target:
            print("Error: production_id required")
            return 1
        status = engine.get_status(args.target[0])
        _dump(status)

    elif subcmd == "list":
        prods = engine.list_productions(args.company)
        _dump({
            "company_id": args.company,
            "productions": [
                {"id": p.production_id, "brief": p.brief,
                 "format": p.format, "phase": p.status.value}
                for p in prods
            ],
            "total": len(prods),
        })

    elif subcmd == "advance":
        if not args.target:
            print("Error: production_id required")
            return 1
        try:
            new_status = engine.advance_phase(args.target[0], force=args.force)
            _dump({"production_id": args.target[0], "new_phase": new_status.value})
        except Exception as e:
            _dump({"error": str(e)})

    elif subcmd == "route":
        if not args.target:
            print("Error: task_type required")
            return 1
        result = engine.route_to_tool(args.target[0])
        _dump(result)

    elif subcmd == "auto-run":
        if not args.target:
            print("Error: production_id required")
            return 1
        steps = engine.auto_run(args.target[0])
        _dump({"production_id": args.target[0], "steps": steps})

    return 0


def cmd_scrape(args: argparse.Namespace) -> int:
    """Dispatch scrape subcommands."""
    subcmd = args.scrape_command

    if subcmd == "url":
        from rag_engine.ingestion.web import WebIngestor
        from rag_engine.ingestion.jina_reader import JinaReaderIngestor
        if args.tool == "jina":
            ingestor = JinaReaderIngestor()
        else:
            ingestor = WebIngestor()
        count = ingestor.ingest(source=args.target, company_id=args.company,
                                 data_type=args.type, agent_id=args.agent)
        print(f"Ingested {count} chunks from {args.target}")

    elif subcmd == "search":
        from rag_engine.ingestion.exa_search import ExaSearchIngestor
        ingestor = ExaSearchIngestor()
        count = ingestor.ingest(source=args.target, company_id=args.company,
                                 data_type=args.type, agent_id=args.agent,
                                 num_results=args.num_results, search_type=args.search_type)
        print(f"Ingested {count} chunks from Exa search: {args.target}")

    elif subcmd == "crawl":
        from rag_engine.ingestion.web import WebIngestor
        ingestor = WebIngestor()
        count = ingestor.crawl(source=args.target, company_id=args.company,
                                data_type=args.type, agent_id=args.agent,
                                max_pages=args.max_pages)
        print(f"Crawled {count} chunks from {args.target}")

    elif subcmd == "dynamic":
        from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
        ingestor = PlaywrightIngestor()
        count = ingestor.ingest(source=args.target, company_id=args.company,
                                 data_type=args.type, agent_id=args.agent,
                                 wait_for=args.wait_for)
        print(f"Ingested {count} chunks via Playwright from {args.target}")

    elif subcmd == "batch":
        from rag_engine.batch import execute_manifest
        result = execute_manifest(_Path(args.target), dry_run=args.dry_run, resume=args.resume)
        _dump(result)

    elif subcmd == "plan":
        from exa_py import Exa
        from susan_core.config import config as _config
        client = Exa(api_key=_config.exa_api_key)
        response = client.search(args.target, num_results=args.num_results,
                                  type="autoprompt", use_autoprompt=True)
        manifest = {
            "manifest": {
                "name": args.target,
                "company": args.company,
                "data_type": args.type,
                "created": "2026-03-09",
                "priority": "medium",
            },
            "sources": [{"tool": "jina", "url": r.url} for r in response.results],
        }
        output = args.output or f"data/scrape_manifests/{args.target.replace(' ', '_')[:40]}.yaml"
        _Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            yaml.safe_dump(manifest, f, sort_keys=False, allow_unicode=True)
        print(f"Manifest written to {output} ({len(manifest['sources'])} URLs)")

    elif subcmd == "status":
        from rag_engine.retriever import Retriever
        retriever = Retriever()
        result = retriever.supabase.table("knowledge_chunks") \
            .select("data_type", count="exact") \
            .eq("company_id", args.company) \
            .execute()
        counts: dict[str, int] = {}
        if result.data:
            for row in result.data:
                dt = row.get("data_type", "unknown")
                counts[dt] = counts.get(dt, 0) + 1
        total = sum(counts.values())
        _dump({"company": args.company, "total_chunks": total, "by_data_type": counts})

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="susan")
    subparsers = parser.add_subparsers(dest="command", required=True)

    query = subparsers.add_parser("query")
    query.add_argument("query", nargs="+")
    query.add_argument("--company", default=_default_company())
    query.add_argument("--types", default="")
    query.add_argument("--top-k", type=int, default=8)
    query.set_defaults(func=cmd_query)

    route = subparsers.add_parser("route")
    route.add_argument("company", nargs="?")
    route.add_argument("task", nargs="+")
    route.add_argument("--top-k", type=int, default=6)
    route.set_defaults(func=cmd_route)

    status = subparsers.add_parser("status")
    status.add_argument("company", nargs="?", default=_default_company())
    status.set_defaults(func=cmd_status)

    assets = subparsers.add_parser("assets")
    assets.add_argument("company", nargs="?", default=_default_company())
    assets.add_argument("--limit", type=int, default=20)
    assets.set_defaults(func=cmd_assets)

    team = subparsers.add_parser("team")
    team.add_argument("company", nargs="?", default=_default_company())
    team.set_defaults(func=cmd_team)

    refresh = subparsers.add_parser("refresh")
    refresh.add_argument("company", nargs="?", default=_default_company())
    refresh.set_defaults(func=cmd_refresh)

    plan = subparsers.add_parser("plan")
    plan.add_argument("company", nargs="?", default=_default_company())
    plan.add_argument("--mode", default="quick", choices=["quick", "deep", "design", "foundry", "full"])
    plan.add_argument("--refresh", action="store_true")
    plan.set_defaults(func=cmd_plan)

    foundry = subparsers.add_parser("foundry")
    foundry.add_argument("company", nargs="?", default=_default_company())
    foundry.set_defaults(func=cmd_foundry)

    bootstrap = subparsers.add_parser("bootstrap")
    bootstrap.add_argument("--config", default=str(BACKEND_ROOT / "data" / "project_protocol_targets.yaml"))
    bootstrap.set_defaults(func=cmd_bootstrap)

    # ── production subcommand ───────────────────────────────────
    production = subparsers.add_parser("production", help="Film & Image Studio production lifecycle")
    production.add_argument("subcmd", choices=["start", "status", "list", "advance", "route", "auto-run"])
    production.add_argument("target", nargs="*", default=[])
    production.add_argument("--company", default=_default_company())
    production.add_argument("--format", default="film",
                            choices=["film", "reel", "photo", "carousel", "image", "documentary"])
    production.add_argument("--title", default=None)
    production.add_argument("--force", action="store_true")
    production.set_defaults(func=cmd_production)

    # ── scrape subcommand with nested sub-subcommands ───────────
    scrape = subparsers.add_parser("scrape", help="Scraper CLI for data collection")
    scrape_sub = scrape.add_subparsers(dest="scrape_command", required=True)

    s_url = scrape_sub.add_parser("url")
    s_url.add_argument("target", help="URL to scrape")
    s_url.add_argument("--tool", choices=["firecrawl", "jina"], default="jina")
    s_url.add_argument("--company", default=_default_company())
    s_url.add_argument("--type", default="market_research")
    s_url.add_argument("--agent", default=None)

    s_search = scrape_sub.add_parser("search")
    s_search.add_argument("target", help="Exa search query")
    s_search.add_argument("--num-results", type=int, default=10)
    s_search.add_argument("--search-type", choices=["autoprompt", "keyword", "neural"], default="autoprompt")
    s_search.add_argument("--company", default=_default_company())
    s_search.add_argument("--type", default="market_research")
    s_search.add_argument("--agent", default=None)

    s_crawl = scrape_sub.add_parser("crawl")
    s_crawl.add_argument("target", help="Base URL to deep crawl")
    s_crawl.add_argument("--max-pages", type=int, default=50)
    s_crawl.add_argument("--company", default=_default_company())
    s_crawl.add_argument("--type", default="market_research")
    s_crawl.add_argument("--agent", default=None)

    s_dynamic = scrape_sub.add_parser("dynamic")
    s_dynamic.add_argument("target", help="URL to scrape with Playwright")
    s_dynamic.add_argument("--wait-for", default=None, help="CSS selector to wait for")
    s_dynamic.add_argument("--company", default=_default_company())
    s_dynamic.add_argument("--type", default="market_research")
    s_dynamic.add_argument("--agent", default=None)

    s_batch = scrape_sub.add_parser("batch")
    s_batch.add_argument("target", help="Path to manifest YAML")
    s_batch.add_argument("--dry-run", action="store_true")
    s_batch.add_argument("--resume", action="store_true")
    s_batch.add_argument("--company", default=_default_company())

    s_plan = scrape_sub.add_parser("plan")
    s_plan.add_argument("target", help="Domain topic for Exa discovery")
    s_plan.add_argument("--num-results", type=int, default=20)
    s_plan.add_argument("--output", default=None, help="Output manifest YAML path")
    s_plan.add_argument("--company", default=_default_company())
    s_plan.add_argument("--type", default="market_research")

    s_status = scrape_sub.add_parser("status")
    s_status.add_argument("--company", default=_default_company())

    scrape.set_defaults(func=cmd_scrape)

    for name in [
        "shell-query",
        "shell-route",
        "shell-status",
        "shell-assets",
        "shell-team",
        "shell-refresh",
        "shell-plan",
        "shell-foundry",
        "shell-bootstrap",
        "shell-production",
    ]:
        shell = subparsers.add_parser(name)
        shell.add_argument("raw", nargs="?", default="")
        shell.set_defaults(func=lambda args, subcommand=name: cmd_shell(subcommand, args.raw))

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
