import io
import logging
import time
from typing import Optional
from urllib.parse import urlencode

import httpx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

from parser_domclick.domclick.models import Offer
from parser_domclick.domclick.parser import ExcelParser
from parser_domclick.constants import CITIES, HEADERS


class DomClickBrowser:
    logger: logging.Logger
    driver: WebDriver

    def __init__(
        self, headless: bool = False, command_executor: Optional[str] = None
    ) -> None:
        self.logger = logging.getLogger(__name__)

        options = Options()
        options.add_argument(f"--user-agent={HEADERS['User-Agent']}")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        if headless:
            options.add_argument("--headless")

        try:
            if command_executor:
                self.driver = webdriver.Remote(
                    command_executor=command_executor, options=options
                )
            else:
                self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

        self.logger.info("Chrome WebDriver initialized successfully.")

    def __del__(self):
        self.quit()

    def quit(self) -> None:
        self.driver.quit()
        self.logger.info("Browser session destroyed.")

    def open_page(self, url: str) -> None:
        """Open a page and handle potential antibot."""
        self.logger.info(f"Opening page: {url}")
        self.driver.get(url)
        self.bypass_antibot(url)

    def _construct_url(
        self,
        region: str,
        price_gte: Optional[str],
        price_lte: Optional[str],
        area_gte: Optional[str],
        area_lte: Optional[str],
        sale: Optional[bool],
    ) -> str:
        base_url = "https://bff-search-web.domclick.ru/api/offers/v1"
        # https://bff-search-web.domclick.ru/api/offers/count/v1?address=1d1463ae-c80f-4d19-9331-a1b68a85b553&limit=20&sort=qi&sort_dir=desc&deal_type=rent&category=commercial&offer_type=office&aids=2299&rent_price__gte=10&rent_price__lte=10000000&area__gte=10&area__lte=10000&floor__gte=1&floor__lte=10

        params = {
            "deal_type": "rent" if not sale else "sale",
            "offer_type": "office",
            "address": CITIES.get(region.lower(), "1"),
        }
        if price_gte:
            params[f"{"rent" if not sale else "sale"}_price__gte"] = price_gte
        if price_lte:
            params[f"{"rent" if not sale else "sale"}_price__lte"] = price_lte
        if area_gte:
            params["area__gte"] = area_gte
        if area_lte:
            params["area__lte"] = area_lte
        return base_url + "?" + urlencode(params)

    def search(
        self,
        address: str,
        price_gte: Optional[str],
        price_lte: Optional[str],
        area_gte: Optional[str],
        area_lte: Optional[str],
        sale: Optional[bool],
    ) -> list[Offer]:
        self.logger.info(f"Searching for offers with query: {address}")
        self.open_page("https://domclick.ru/")

        url = self._construct_url(
            address, price_gte, price_lte, area_gte, area_lte, sale
        )
        response = self.httpx_client.get(url)
        if response.status_code == 200:
            parser = ExcelParser(io.BytesIO(response.content))
            return parser.clean_excel()
        else:
            raise ValueError(f"Failed to fetch data from {url}")

    def bypass_antibot(self, url: str) -> None:
        for _ in range(5):  # Retry up to 5 times
            if self.driver.title == "Captcha - база объявлений ЦИАН":
                self.logger.warning(
                    "Access restricted due to IP issues. Refreshing the page to bypass antibot."
                )
                time.sleep(3)
                self.reset()
                self.driver.get(url)
                time.sleep(20)
            else:
                self.logger.info("Captcha bypassed")
                break
        else:
            self.logger.error("Access restricted due to IP issues.")
            raise Exception("Access restricted due to IP issues.")

    def reset(self) -> None:
        self.driver.delete_all_cookies()
        try:
            # Only works if page is HTTP(S); won't fail for normal URLs
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
        except Exception as e:
            self.logger.warning(f"Failed to clear storage: {e}")
        self.driver.refresh()
        self.logger.info("Browser session reset.")

    @property
    def httpx_client(self) -> httpx.Client:
        """Extract session data from Selenium browser for httpx client."""

        session = httpx.Client()
        session.cookies.update(
            {cookie["name"]: cookie["value"] for cookie in self.driver.get_cookies()}
        )
        session.headers.update(
            {"User-Agent": self.driver.execute_script("return navigator.userAgent")}
        )
        self.logger.debug(f"Session cookies: {session.cookies}")
        self.logger.debug(f"Session headers: {session.headers}")
        return session
