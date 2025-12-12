from pydantic import BaseModel


class SearchResponse(BaseModel):
    """Response model for search endpoint."""

    query: str
    total_found: int
    filtered_count: int
    offers: dict
