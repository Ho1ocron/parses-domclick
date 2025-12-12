import logging
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from cian_parser.api.v1.models import SearchResponse
from cian_parser.cian.browser import CianBrowser

# Setup logging
logger = logging.getLogger(__name__)

# Get environment variables
SELENIUM_HOST = os.getenv("SELENIUM_HOST", "localhost")
SELENIUM_PORT = int(os.getenv("SELENIUM_PORT", 4444))

router = APIRouter(prefix="/v1", tags=["v1"])


@router.get("/search", response_model=SearchResponse)
async def search_offers(
    city: str = Query(..., description="Search city for Cian"),
    price_gte: Optional[str] = Query(None, description="Minimum price filter"),
    price_lte: Optional[str] = Query(None, description="Maximum price filter"),
    area_gte: Optional[str] = Query(None, description="Minimum area in m²"),
    area_lte: Optional[str] = Query(None, description="Maximum area in m²"),
    sale: Optional[bool] = Query(None, description="Sale or Rent"),
) -> SearchResponse:
    """
    Main search endpoint.
    """

    logger.info("Initializing browser")
    browser = CianBrowser(
        headless=False,
        command_executor=f"http://{SELENIUM_HOST}:{SELENIUM_PORT}/wd/hub",
    )

    try:
        # Reset browser and fetch final offers
        logger.info(f"Searching for: {city}")

        offers = browser.search(
            city,
            price_gte,
            price_lte,
            area_gte,
            area_lte,
            sale,
        )

        logger.info(f"Found {len(offers)} offers")
        return SearchResponse(
            offers=offers,
            query=city,
            count=len(offers),
        )

    except Exception:
        logger.exception("An error occurred during search", exc_info=True)
        raise HTTPException(status_code=500, detail="Error during search")
