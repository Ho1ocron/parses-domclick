import logging
import os
import time
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from cian_parser.api.v1 import router as v1_router

# Load environment variables
load_dotenv()
SELENIUM_HOST = os.getenv("SELENIUM_HOST", "localhost")
SELENIUM_PORT = int(os.getenv("SELENIUM_PORT", 4444))
SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", 60))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Setup logging
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)


def is_selenium_ready(host, port):
    url = f"http://{host}:{port}/wd/hub/status"
    try:
        r: dict[str, dict] = httpx.get(url).json()
        if r.get("value", {}).get("ready"):
            return True
    except Exception:
        pass
    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CianParser lifespan...")

    # Wait until Selenium is ready
    for _ in range(SELENIUM_TIMEOUT):
        if is_selenium_ready(host=SELENIUM_HOST, port=SELENIUM_PORT):
            break
        logger.info("Waiting for Selenium server...")
        time.sleep(1)
    else:
        logger.error("Selenium server not ready")
        raise TimeoutError("Selenium server not ready")

    logger.info("CianParser lifespan started.")
    yield


app = FastAPI(
    title="Cian Parser API",
    version="1.0.0",
    lifespan=lifespan,
)

# Include v1 router
app.include_router(v1_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Cian Parser API",
        "version": "1.0.0",
        "endpoints": {"GET /v1/search": "Search for offers with filters"},
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
    }


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.exception("An error occurred", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
