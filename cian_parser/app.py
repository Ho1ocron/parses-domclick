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
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Setup logging
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger("cian_parser")
browser: CianBrowser | None = None
sys.excepthook = except_hook


@asynccontextmanager
async def lifespan(app: FastAPI):
    global browser

    logger.info("Starting CianParser lifespan...")

    # Wait until Selenium is ready
    while not is_selenium_ready(host=SELENIUM_HOST, port=SELENIUM_PORT, timeout=60):
        logger.info("Waiting for Selenium server...")
        time.sleep(1)

    # Initialize browser
    browser = CianBrowser(
        headless=False,
        command_executor=f"http://{SELENIUM_HOST}:{SELENIUM_PORT}/wd/hub",
    )

    logger.info("CianParser lifespan started.")
    yield

    # Shutdown
    if browser:
        logger.info("Closing browser...")
        browser.quit()
        logger.info("Browser closed successfully")


app = FastAPI(
    title="Cian Parser API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/search", response_model=SearchResponse)
async def search_offers(request: SearchRequest) -> SearchResponse:
    """
    Main search endpoint.
    Uses the global browser initialized during startup.
    """
    global browser

    if browser is None:
        raise HTTPException(status_code=500, detail="Browser not initialized")

    try:
        # Reset browser and fetch final offers
        browser.reset()
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

    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail="Error during search")


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
    return {"status": "healthy", "browser_initialized": browser is not None}
