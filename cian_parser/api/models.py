from typing import Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for search endpoint."""

    city: str = Field(..., description="Search city for Cian")
    price_gte: Optional[str] = Field(None, description="Minimum price filter")
    price_lte: Optional[str] = Field(None, description="Maximum price filter")
    area_gte: Optional[str] = Field(None, description="Minimum area in m²")
    area_lte: Optional[str] = Field(None, description="Maximum area in m²")
    sale: Optional[bool] = Field(None, description="Sale or Rent")


class SearchResponse(BaseModel):
    """Response model for search endpoint."""

    query: str
    total_found: int
    filtered_count: int
    offers: dict
