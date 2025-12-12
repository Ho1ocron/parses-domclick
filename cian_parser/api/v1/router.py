import logging
import os

from fastapi import APIRouter, HTTPException

from cian_parser.api.models import SearchRequest, SearchResponse
from cian_parser.cian.browser import CianBrowser

# Setup logging
logger = logging.getLogger(__name__)

# Get environment variables
SELENIUM_HOST = os.getenv("SELENIUM_HOST", "localhost")
SELENIUM_PORT = int(os.getenv("SELENIUM_PORT", 4444))

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/search", response_model=SearchResponse)
async def search_offers(request: SearchRequest) -> SearchResponse:
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
        logger.info(f"Searching for: {request.city}")

        offers = browser.search(
            request.city,
            request.price_gte,
            request.price_lte,
            request.area_gte,
            request.area_lte,
            request.sale,
        )

        logger.info(f"Found {len(offers)} offers")

        return SearchResponse(
            offers=offers,
            query=request.city,
            total_found=int(len(offers)),
            filtered_count=len(offers),
        )

    except Exception:
        logger.exception("An error occurred during search", exc_info=True)
        raise HTTPException(status_code=500, detail="Error during search")
