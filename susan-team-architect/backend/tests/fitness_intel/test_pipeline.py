from pathlib import Path

from fitness_intel.pipeline import CorpusBuilder

DOMAIN_ROOT = Path(__file__).resolve().parents[2] / "data" / "domains" / "fitness_app_intelligence"


def test_inventory_counts_current_corpus():
    builder = CorpusBuilder(DOMAIN_ROOT / "editorial")
    inventory = builder.build_inventory()
    assert inventory["total_app_profiles"] == 46
    assert inventory["category_counts"]["fitness"] == 21
    assert inventory["category_counts"]["nutrition"] == 9
    assert inventory["category_counts"]["recovery"] == 8
    assert inventory["category_counts"]["mindfulness"] == 8


def test_build_app_records_for_ten_profiles():
    builder = CorpusBuilder(DOMAIN_ROOT / "editorial")
    records = builder.build_app_records(limit=10)
    assert len(records) == 10
    assert all(record["id"].startswith("app-") for record in records)


def test_inventory_counts_merged_domain_pack():
    builder = CorpusBuilder(DOMAIN_ROOT)
    inventory = builder.build_inventory()
    assert inventory["total_markdown_files"] == 61
    assert inventory["total_app_profiles"] == 46
