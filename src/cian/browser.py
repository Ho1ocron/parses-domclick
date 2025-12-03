from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_recaptcha_solver import RecaptchaSolver

import time
import html
import json
import httpx
import logging

from models import Offer

class CianBrowser:
    logger: logging.Logger
    driver: webdriver.Chrome
    test_ua: str
    solver: RecaptchaSolver

    def __init__(self, headless: bool = False) -> None:
        self.logger = logging.getLogger(__name__)
        self.test_ua = "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"

        options = Options()
        options.add_argument(f"'--user-agent={self.test_ua}")
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        if headless:
            options.add_argument('--headless')
        try:
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

        self.solver = RecaptchaSolver(driver=self.driver)
        self.logger.info("Chrome WebDriver initialized successfully.")

    def quit(self) -> None:
        self.driver.quit()
        self.logger.info("Browser session quit.")
        
    def open_page(self, url: str) -> None:
        """Open a page and handle potential antibot."""
        self.logger.info(f"Opening page: {url}")
        self.driver.get(url)
        self.bypass_antibot()

    def search(self, query: str) -> list[Offer]:
        self.logger.info(f"Searching for offers with query: {query}")
        offers: list[Offer] = []
        self.open_page("https://cian.ru/")
        # search_field = WebDriverWait(self.driver, 3).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, "//input[@placeholder='Поиск по объявлениям']"))
        # )
        try:
            button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-mark='FiltersSearchButton'"))
                # Alternatively, use the CSS selector from the previous suggestion:
                # EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-mark="FiltersSearchButton"]'))
            )
            self.logger.info(f"button {button.id} is cliked")
            button.click()
        except:
            current_title = self.driver.title
            print(current_title)

        
        
        return offers

    def bypass_antibot(self) -> None:
        for _ in range(5):  # Retry up to 5 times
            if self.driver.title == 'Captcha - база объявлений ЦИАН':
                self.logger.warning(
                    "Access restricted due to IP issues. Refreshing the page to bypass antibot.")
                time.sleep(3)
                self.driver.refresh()
                recaptcha_iframe = self.driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                self.solver.click_recaptcha_v2(iframe=recaptcha_iframe)
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
        # await self.bypass_antibot()
        self.logger.info("Browser session reset.")


def main() -> None:
    browser = CianBrowser()
    lst: list[Offer] = browser.search(query="")


if __name__ == "__main__":
    import asyncio
    main()
