"""Tests for susan scrape CLI subcommands."""
from __future__ import annotations
import pytest


class TestScrapeCLIParsing:
    def test_scrape_url_parsed(self):
        from scripts.susan_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["scrape", "url", "https://example.com", "--type", "exercise_science"])
        assert args.command == "scrape"
        assert args.scrape_command == "url"
        assert args.target == "https://example.com"
        assert args.type == "exercise_science"

    def test_scrape_search_parsed(self):
        from scripts.susan_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["scrape", "search", "progressive overload", "--num-results", "15"])
        assert args.scrape_command == "search"
        assert args.target == "progressive overload"
        assert args.num_results == 15

    def test_scrape_crawl_parsed(self):
        from scripts.susan_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["scrape", "crawl", "https://example.com", "--max-pages", "30"])
        assert args.scrape_command == "crawl"
        assert args.target == "https://example.com"
        assert args.max_pages == 30

    def test_scrape_batch_parsed(self):
        from scripts.susan_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["scrape", "batch", "data/scrape_manifests/test.yaml", "--dry-run"])
        assert args.scrape_command == "batch"
        assert args.target == "data/scrape_manifests/test.yaml"
        assert args.dry_run is True

    def test_scrape_dynamic_parsed(self):
        from scripts.susan_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["scrape", "dynamic", "https://example.com", "--wait-for", ".content"])
        assert args.scrape_command == "dynamic"
        assert args.wait_for == ".content"

    def test_scrape_plan_parsed(self):
        from scripts.susan_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["scrape", "plan", "exercise science", "--output", "out.yaml"])
        assert args.scrape_command == "plan"
        assert args.target == "exercise science"
        assert args.output == "out.yaml"

    def test_scrape_status_parsed(self):
        from scripts.susan_cli import build_parser
        parser = build_parser()
        args = parser.parse_args(["scrape", "status", "--company", "transformfit"])
        assert args.scrape_command == "status"
        assert args.company == "transformfit"
