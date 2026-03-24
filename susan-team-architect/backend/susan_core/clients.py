"""Shared client factories for Susan runtime.

Imports for anthropic and voyageai are deferred to the functions that use them
so that modules which only need get_supabase_client() or get_voyage_client()
don't fail if anthropic isn't installed (and vice versa).
"""
from __future__ import annotations

from functools import lru_cache

from susan_core.config import config


@lru_cache(maxsize=1)
def get_anthropic_client():
    from anthropic import Anthropic
    return Anthropic(api_key=config.anthropic_api_key)


@lru_cache(maxsize=1)
def get_voyage_client():
    import voyageai
    return voyageai.Client(api_key=config.voyage_api_key)


@lru_cache(maxsize=1)
def get_supabase_client():
    from supabase import create_client
    return create_client(config.supabase_url, config.supabase_key)

