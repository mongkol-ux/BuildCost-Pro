from src.main import app
from src.search_schemas import SearchResponse, SearchResult


def test_step39_search_route_registered():
    paths = set(app.openapi()["paths"])
    assert "/api/v1/search" in paths
    params = {p["name"] for p in app.openapi()["paths"]["/api/v1/search"]["get"]["parameters"]}
    assert {"q", "project_id", "page", "page_size"}.issubset(params)


def test_step39_response_contract():
    item = SearchResult(id="p1", entity_type="project", title="Demo", project_id="p1", score=100)
    response = SearchResponse(query="Demo", page=1, page_size=20, total=1, results=[item])
    assert response.results[0].entity_type == "project"
    assert response.page == 1


def test_step39_pagination_contract_defaults():
    spec = app.openapi()["paths"]["/api/v1/search"]["get"]["parameters"]
    by_name = {p["name"]: p for p in spec}
    assert by_name["page"]["schema"]["default"] == 1
    assert by_name["page_size"]["schema"]["default"] == 20
