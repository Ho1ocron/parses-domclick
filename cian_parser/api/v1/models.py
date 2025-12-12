from pydantic import BaseModel, Field

from cian_parser.cian.models import Offer


class SearchResponse(BaseModel):
    """Response model for search endpoint."""

    query: str = Field(..., description="The city that was searched")
    count: int = Field(..., description="Total number of offers found")
    offers: list[Offer] = Field(..., description="List of offers")
