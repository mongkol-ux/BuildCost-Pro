from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    id: str
    entity_type: str
    title: str
    subtitle: str | None = None
    project_id: str | None = None
    score: int = Field(ge=0)


class SearchResponse(BaseModel):
    query: str
    page: int
    page_size: int
    total: int
    results: list[SearchResult]
