import logging
import os
import sys
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from cian_parser.api.models import SearchRequest, SearchResponse
from cian_parser.api.self_api import except_hook, is_selenium_ready
from cian_parser.cian.browser import CianBrowser

# Load environment variables
load_dotenv()
SELENIUM_HOST = os.getenv("SELENIUM_HOST", "localhost")
SELENIUM_PORT = int(os.getenv("SELENIUM_PORT", 4444))
SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", 60))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Setup logging
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger("cian_parser")
sys.excepthook = except_hook


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CianParser lifespan...")

    # Wait until Selenium is ready
    while not is_selenium_ready(
        host=SELENIUM_HOST, port=SELENIUM_PORT, timeout=SELENIUM_TIMEOUT
    ):
        logger.info("Waiting for Selenium server...")
        time.sleep(1)

    logger.info("CianParser lifespan started.")
    yield


app = FastAPI(
    title="Cian Parser API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/search", response_model=SearchResponse)
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

    del browser


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Cian Parser API",
        "version": "1.0.0",
        "endpoints": {"POST /search": "Search for offers with filters"},
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
    }
