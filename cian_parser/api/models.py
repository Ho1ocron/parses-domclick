from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for search endpoint."""

    query: str = Field(..., description="Search query for Cian")
    price_gte: str = Field(..., description="Minimum price filter")
    price_lte: str = Field(..., description="Maximum price filter")
    area_gte: str = Field(..., description="Minimum area in m²")
    area_lte: str = Field(..., description="Maximum area in m²")


class SearchResponse(BaseModel):
    """Response model for search endpoint."""

    query: str 
    total_found: int
    filtered_count: int
    offers: dict