#!/usr/bin/env python3
"""Apply Jake Security migration — creates jake_audit_log, jake_cron_status,
jake_pipeline_runs, jake_cost_events, jake_deals, jake_pipeline_events tables."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

MIGRATION_PATH = BACKEND_ROOT / "supabase" / "migrations" / "20260322000000_jake_security.sql"
POOLER_URL_PATH = BACKEND_ROOT / "supabase" / ".temp" / "pooler-url"


def load_env():
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def connection_url() -> str:
    load_env()
    direct = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if direct:
        return str(direct)

    if not POOLER_URL_PATH.exists():
        raise RuntimeError(
            "Supabase pooler URL not found. Set DATABASE_URL or SUPABASE_DB_URL env var, "
            "or run `supabase db push` via the Supabase CLI."
        )

    raw_url = POOLER_URL_PATH.read_text(encoding="utf-8").strip()
    parsed = urlparse(raw_url)
    if parsed.password:
        return raw_url

    password = os.getenv("SUPABASE_DB_PASSWORD", "")
    if not password:
        backend_env = BACKEND_ROOT / ".env"
        if backend_env.exists():
            for line in backend_env.read_text().splitlines():
                if line.startswith("SUPABASE_DB_PASSWORD="):
                    password = line.partition("=")[2].strip()
                    break
    if not password:
        raise RuntimeError("SUPABASE_DB_PASSWORD not found.")

    auth = parsed.username or "postgres"
    netloc = f"{auth}:{quote(password, safe='')}@{parsed.hostname}"
    if parsed.port:
        netloc += f":{parsed.port}"
    return f"{parsed.scheme}://{netloc}{parsed.path}?{parsed.query}"


def main():
    import psycopg

    print(f"Applying migration: {MIGRATION_PATH.name}")
    sql = MIGRATION_PATH.read_text(encoding="utf-8")
    url = connection_url()

    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

    print("✓ Migration applied successfully")
    print("  Tables created/verified:")
    print("    - jake_audit_log")
    print("    - jake_cron_status")
    print("    - jake_pipeline_runs")
    print("    - jake_cost_events")
    print("    - jake_deals")
    print("    - jake_pipeline_events")


if __name__ == "__main__":
    main()
