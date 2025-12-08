import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from api.models import SearchRequest, SearchResponse
from src.api.self_api import except_hook, is_selenium_ready
from cian.browser import CianBrowser
from cian.parser import CianParser
from settings import settings


logging.basicConfig(level=logging.INFO)


class AppCianParser:
    SELENIUM_HOST: str
    SELENIUM_PORT: str
    SELENIUM_TIMEOUT: int = 60

    browser: Optional[CianBrowser]
    logger: logging.Logger

    sys.excepthook = except_hook

    app: FastAPI

    def __init__(self) -> None:
        self.SELENIUM_HOST = settings.SELENIUM_HOST
        self.SELENIUM_PORT = settings.SELENIUM_PORT
        self.browser = None
        self.logger = logging.getLogger(__name__)


    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        self.logger.info("Starting CianParser lifespan...")
        ready = is_selenium_ready
        while not ready:
            self.logger.info("Waiting for Selenium server...")
            ready = is_selenium_ready(
                host=self.SELENIUM_HOST, port=self.SELENIUM_PORT, timeout=self.SELENIUM_TIMEOUT
            )
            time.sleep(1)
        self.browser = CianBrowser(
            headless=False,
            command_executor=f"http://{self.SELENIUM_HOST}:{self.SELENIUM_PORT}/wd/hub",
        )
        
        self.logger.info("CianParser lifespan started.")
        yield

        if self.browser:
            self.logger.info("Closing browser...")
            self.browser.quit()
            self.logger.info("Browser closed successfully")

    async def App(self) -> None:
        self.app = FastAPI(
            title="Cian Parser API",
            version="1.0.0",
            lifespan=self.lifespan
        )
    app = FastAPI(title="Avito Parser API", version="1.0.0", lifespan=lifespan)
    @app.post("/search", response_model=SearchResponse)
    async def search_offers(self, request: SearchRequest) -> None:
        await self.App()
        if not self.browser:
            raise HTTPException(status_code=500, detail="Browser not initialized")

        try:
            self.browser.search(
                query=request.query,
                price_gte=request.price_gte,
                price_lte=request.price_lte,
                area_gte=request.area_gte,
                area_lte=request.area_lte,
            )
            time.sleep(20)  # Wait for the search to complete

            self.browser.reset()
            self.logger.info(f"Searching for: {request.query}")
            offers = self.browser.search(
                request.query,
                request.price_gte,
                request.price_lte,
                request.area_gte,
                request.area_lte,
            )
            self.logger.info(f"Found {len(offers)} offers")
        except Exception as e:
            self.logger.error(f"Error during search: {e}")
            raise HTTPException(status_code=500, detail="Error during search")
        


