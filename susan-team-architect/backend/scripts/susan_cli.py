"""Unified Susan protocol CLI for slash commands, MCP, and local workflows."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
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
    return {"shared", "transformfit", "oracle-health-ai-enablement", "alex-recruiting"}


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
