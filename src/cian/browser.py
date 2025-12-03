from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import html
import json
import httpx
import logging

from cian.models import Offer

class CianBrowser:
    logger: logging.Logger
    driver: webdriver.Chrome

    def __init__(self, headless: bool = True) -> None:
        self.logger = logging.getLogger(__name__)

        options = Options()
        options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1')
        options.add_argument('--start-maximized')
        if headless:
            options.add_argument('--headless')
        try:
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise
        self.logger.info("Chrome WebDriver initialized successfully.")

    async def quit(self) -> None:
        self.driver.quit()
        self.logger.info("Browser session quit.")
        
    async def open_page(self, url: str) -> None:
        """Open a page and handle potential antibot."""
        self.logger.info(f"Opening page: {url}")
        self.driver.get(url)
        await self.bypass_antibot()

    async def search(self, query: str) -> list[Offer]:
        self.logger.info(f"Searching for offers with query: {query}")
        offers: list[Offer] = []
        search_field = WebDriverWait(self.driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Поиск по объявлениям']"))
        )

        button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-mark='FiltersSearchButton']"))
        )
        # button.click()

        return offers

    async def bypass_antibot(self) -> None:
        for _ in range(5):  # Retry up to 5 times
            if self.driver.title == 'Доступ ограничен: проблема с IP':
                self.logger.warning(
                    "Access restricted due to IP issues. Refreshing the page to bypass antibot.")
                time.sleep(3)
                self.driver.refresh()
            else:
                break
        else:
            self.logger.error("Access restricted due to IP issues.")
            raise Exception("Access restricted due to IP issues.")

    async def reset(self) -> None:
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")
        self.driver.refresh()
        await self.bypass_antibot()
        self.logger.info("Browser session reset.")


async def main() -> None:
    browser = CianBrowser()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
