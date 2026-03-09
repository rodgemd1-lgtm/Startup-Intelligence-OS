from control_plane.catalog import ControlPlaneCatalog


def test_visual_assets_returns_oracle_health_assets():
    catalog = ControlPlaneCatalog()
    assets = catalog.visual_assets("oracle-health-ai-enablement", limit=10)
    assert assets
    assert any(asset.public_url for asset in assets)
