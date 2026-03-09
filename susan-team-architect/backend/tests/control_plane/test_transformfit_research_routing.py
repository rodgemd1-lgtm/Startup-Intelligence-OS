from control_plane.protocols import route_company_task


def test_transformfit_routing_understands_gurus_simulation_and_predictive_cues(monkeypatch):
    monkeypatch.setattr(
        "control_plane.protocols.search_company_knowledge",
        lambda *args, **kwargs: [],
    )

    routed = route_company_task(
        "transformfit",
        "Scrape current fitness influencer recommendations, run Monte Carlo on workout dropout windows, and build predictive coach cues for first misses and plateaus.",
    )

    assert "training-research-studio" in routed["recommended_agents"]
    assert "algorithm-lab" in routed["recommended_agents"]
    assert "coaching-architecture-studio" in routed["recommended_agents"]
    assert "guru_research" in routed["recommended_data_types"]
    assert "simulation_models" in routed["recommended_data_types"]
    assert "predictive_coaching" in routed["recommended_data_types"]
