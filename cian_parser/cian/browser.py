from typing import Any
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium_recaptcha_solver import RecaptchaSolver

import time
import html
import json
import httpx
import logging
import random
import os

from cian_parser.cian.models import Offer


class CianBrowser:
    logger: logging.Logger
    driver: webdriver.Chrome | webdriver.Remote
    test_ua: str

    DOWNLOAD_DIR: str
    BASE_DIR: Path
    # solver: RecaptchaSolver

    def __init__(self, headless: bool = False, command_executor: str | None = None) -> None:
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        self.logger = logging.getLogger(__name__)
        self.test_ua = "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"

        options = Options()
        options.add_argument(f"--user-agent={self.test_ua}")
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        
        self.DOWNLOAD_DIR = str(self.BASE_DIR / "downloads")

        if not os.path.exists(self.DOWNLOAD_DIR):
            os.makedirs(self.DOWNLOAD_DIR)
            
        options.add_experimental_option("prefs", {
            "download.default_directory": self.DOWNLOAD_DIR,
            "download.prompt_for_download": False, # Отключает запрос подтверждения
            "download.directory_upgrade": True,
            "autoclick_on_safebrowsing_prompt": False, # Для безопасности
            "safebrowsing.enabled": True 
        })

        if headless:
            options.add_argument('--headless')
        try:
            if command_executor:
                self.driver = webdriver.Remote(command_executor=command_executor, options=options)
                # self.driver = webdriver.Chrome(options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

        # self.solver = RecaptchaSolver(driver=self.driver)
        self.logger.info("Chrome WebDriver initialized successfully.")

    def quit(self) -> None:
        self.driver.quit()
        self.logger.info("Browser session quit.")
        
    def open_page(self, url: str) -> None:
        """Open a page and handle potential antibot."""
        self.logger.info(f"Opening page: {url}")
        self.driver.get(url)
        self.bypass_antibot(url)

    def _click_button(self, selector: str, by: str = By.XPATH, timeout: int = 5) -> None:
        button = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        button.click()

    def _input_data(self, data: str, selector: str, by: str = By.XPATH, timeout: int = 5) -> None:
        input_field = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        input_field.send_keys(data)

    def search(self, query: str, price_gte: str, price_lte: str, area_gte: str, area_lte: str) -> list[Offer]:
        self.logger.info(f"Searching for offers with query: {query}")
        offers: list[Offer] = []
        self.open_page("https://www.cian.ru/")
        
        self.logger.info("bypassed captcha! Procced to find the button")
        
        time.sleep(random.randint(1, 10))

        # Selecting type to rend/office
        self._click_button("a[href='/snyat/']", By.CSS_SELECTOR)
        time.sleep(random.randint(1, 3))
        self._click_button("div[data-mark='FilterOfferType'] button", By.CSS_SELECTOR)
        time.sleep(random.randint(1, 3))
        self._click_button("//label[.//span[text()='Коммерческая']]")

        # Selecting price range
        self._click_button("div[data-mark='FilterPrice'] button", By.CSS_SELECTOR)
        self._input_data(data=price_gte, selector="//input[@placeholder='от']")
        time.sleep(random.randint(1, 3))
        self._input_data(data=price_lte, selector="//input[@placeholder='до']")
        time.sleep(random.randint(1, 3))

        # Selecting City, street, etc
        time.sleep(random.randint(1, 3))
        self._input_data(data=query, selector="//input[@id='geo-suggest-input']")
        city_xpath = f"//div/following-sibling::div"
        time.sleep(random.randint(1, 2))
        self._click_button(f"//span[@title='{query}']")

        time.sleep(5)

        # Selecting area range
        self._click_button("div[data-mark='FilterArea'] button", By.CSS_SELECTOR)
        time.sleep(random.randint(1, 3))
        self._input_data(data=area_gte, selector="//input[@placeholder='от']")
        time.sleep(random.randint(1, 3))
        self._input_data(data=area_lte, selector="//input[@placeholder='до']")

        # Submitting data
        time.sleep(random.randint(1, 3))
        self._click_button(selector="Найти", by=By.LINK_TEXT, timeout=20)

        # Getting all offers in xlsx format
        time.sleep(random.randint(1, 4))
        self._click_button("//button[normalize-space()='Сохранить файл в Excel']", timeout=20)
        

        return offers

    def bypass_antibot(self, url: str) -> None:
        for _ in range(5):  # Retry up to 5 times
            if self.driver.title == 'Captcha - база объявлений ЦИАН':
                self.logger.warning(
                    "Access restricted due to IP issues. Refreshing the page to bypass antibot.")
                time.sleep(3)
                self.reset()
                self.driver.get(url)
                
                # recaptcha_iframe = self.driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
                # self.solver.click_recaptcha_v2(iframe=recaptcha_iframe)
                time.sleep(20)
            else:
                print("captcha bypassed")
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
            {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()})
        session.headers.update({
            'User-Agent': self.driver.execute_script('return navigator.userAgent')
        })
        self.logger.debug(f"Session cookies: {session.cookies}")
        self.logger.debug(f"Session headers: {session.headers}")
        return session
    
    def get_new_session(self):
        """Get a new httpx session with fresh cookies."""
        self.reset()
        self.logger.debug("Got a new HTTPX session with fresh cookies.")
        return self.httpx_client


def main() -> None:
    time.sleep(3)
    browser = CianBrowser(headless=False)
    lst: list[Offer] = browser.search (
        query="Санкт-Петербург",
        price_gte="10",
        price_lte="10000000",
        area_gte="10",
        area_lte="10000",
    )
    print("Done")
    input()


if __name__ == "__main__":
    main()