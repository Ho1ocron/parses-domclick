from pydantic import BaseModel, Field

from parser_domclick.cian.models import Offer


class SearchResponse(BaseModel):
    """Response model for search endpoint."""

    query: str = Field(..., description="The city that was searched")
    count: int = Field(..., description="Total number of offers found")
    offers: list[Offer] = Field(..., description="List of offers")
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Message about the request")
