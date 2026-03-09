"""Shared client factories for Susan runtime."""
from __future__ import annotations

from functools import lru_cache

from anthropic import Anthropic
from supabase import Client, create_client
import voyageai

from susan_core.config import config


@lru_cache(maxsize=1)
def get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=config.anthropic_api_key)


@lru_cache(maxsize=1)
def get_voyage_client() -> voyageai.Client:
    return voyageai.Client(api_key=config.voyage_api_key)


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    return create_client(config.supabase_url, config.supabase_key)

