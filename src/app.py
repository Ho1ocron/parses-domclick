import logging
import sys
import time

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from src.api.models import SearchRequest, SearchResponse
from src.api.self_api import except_hook, is_selenium_ready
from src.cian.browser import CianBrowser
from src.cian.parser import CianParser
from src.settings import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cian_parser")
browser: CianBrowser | None = None
sys.excepthook = except_hook


@asynccontextmanager
async def lifespan(app: FastAPI):
    global browser

    logger.info("Starting CianParser lifespan...")

    # Wait until Selenium is ready
    # while not is_selenium_ready(
    #     host=settings.SELENIUM_HOST,
    #     port=settings.SELENIUM_PORT,
    #     timeout=60
    # ):
    #     logger.info("Waiting for Selenium server...")
    #     time.sleep(1)

    # Initialize browser
    browser = CianBrowser(
        headless=False,
        command_executor=f"http://{settings.SELENIUM_HOST}:{settings.SELENIUM_PORT}/wd/hub",
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
        logger.info(f"Searching for: {request.query}")

        browser.search(
            request.query,
            request.price_gte,
            request.price_lte,
            request.area_gte,
            request.area_lte,
        )

        parser = CianParser({})
        offers = parser.read_offers_from_file()

        logger.info(f"Found {len(offers)} offers")

        return SearchResponse(offers=offers, query=request.query, total_found=int(len(offers)), filtered_count=len(offers))

    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail="Error during search")
    

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Avito Parser API",
        "version": "1.0.0",
        "endpoints": {"POST /search": "Search for offers with filters"},
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "browser_initialized": browser is not None}
    

@app.get("/test")
async def test_page():
    return HTMLResponse("<html><body><h1>Hello</h1></body></html>")

# Now localStorage works
