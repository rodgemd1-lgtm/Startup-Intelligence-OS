"""Apply the foundry operating-table migration to the linked Supabase Postgres database."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from urllib.parse import quote, urlparse, urlunparse

import psycopg

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from susan_core.config import config


MIGRATION_PATH = BACKEND_ROOT / "supabase" / "migrations" / "20260307020000_foundry_operating_tables.sql"
POOLER_URL_PATH = BACKEND_ROOT / "supabase" / ".temp" / "pooler-url"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply the foundry operating-table migration.")
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Run foundry writeback backfill after the migration succeeds.",
    )
    return parser.parse_args()


def _connection_url() -> str:
    direct = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if direct:
        return str(direct)

    if not POOLER_URL_PATH.exists():
        raise RuntimeError("Supabase pooler URL not found in supabase/.temp/pooler-url.")

    raw_url = POOLER_URL_PATH.read_text(encoding="utf-8").strip()
    parsed = urlparse(raw_url)
    if parsed.password:
        final = raw_url
    else:
        password = ""
        env_path = BACKEND_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("SUPABASE_DB_PASSWORD="):
                    password = line.partition("=")[2].strip()
                    break
        if not password:
            raise RuntimeError(
                "SUPABASE_DB_PASSWORD is not available. Add it to backend/.env or use a full DATABASE_URL."
            )
        auth = parsed.username or "postgres"
        netloc = f"{auth}:{quote(password, safe='')}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        final = urlunparse(
            (
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )
    if "sslmode=" not in final:
        final += ("&" if "?" in final else "?") + "sslmode=require"
    return final


def main() -> int:
    args = _parse_args()
    sql = MIGRATION_PATH.read_text(encoding="utf-8")
    url = _connection_url()

    with psycopg.connect(url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

    print(f"Applied migration: {MIGRATION_PATH}")

    if args.backfill:
        from control_plane.writeback import write_foundry_records_for_output_dir
        summaries = []
        for company_dir in sorted(config.companies_dir.iterdir()):
            if not company_dir.is_dir():
                continue
            output_dir = company_dir / "susan-outputs"
            if not output_dir.exists():
                continue
            if not (output_dir / "problem-framing.json").exists() or not (output_dir / "decision-brief.json").exists():
                continue
            summary = write_foundry_records_for_output_dir(
                f"backfill-{company_dir.name}",
                company_dir.name,
                output_dir,
            )
            summaries.append(summary)
        print(f"Backfilled {len(summaries)} company output directories.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
