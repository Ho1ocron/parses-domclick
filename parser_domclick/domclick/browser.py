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


# curl 'https://bff-search-web.domclick.ru/api/offers/v1?address=0d475b79-88de-4054-818c-37d8f9d0d440&offset=0&limit=20&sort=qi&sort_dir=desc&deal_type=rent&category=commercial&aids=20561&rent_price__gte=1234&rent_price__lte=5678990' \
#   -H 'Accept: application/json, text/plain, */*' \
#   -H 'Accept-Language: en-US,en;q=0.9' \
#   -H 'Connection: keep-alive' \
#   -b 'ns_session=d32bbe41-24b3-485e-aa25-caa3f00af1f4; _ym_uid=1765457093315360074; _ym_d=1765457093; logoSuffix=; iosAppLink=; region={%22data%22:{%22name%22:%22%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%22%2C%22kladr%22:%2277%22%2C%22guid%22:%221d1463ae-c80f-4d19-9331-a1b68a85b553%22}%2C%22isAutoResolved%22:true}; _sv=SV1.9a768d6e-9c17-4720-ace3-17fac2ad5868.1765457152; autoDefinedRegion=0d475b79-88de-4054-818c-37d8f9d0d440:962c3758-8514-4c8f-91fe-aa465d78e56f:%D0%95%D0%BA%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B1%D1%83%D1%80%D0%B3:ekaterinburg; adtech_uid=c552f3bb-8fce-4547-b201-6cb36c9164f3%3Adomclick.ru; top100_id=t1.7711713.631688622.1765457094612; tmr_lvid=d6c33f7b80e0a664f4c2b748aae4b039; tmr_lvidTS=1765457095332; regionAlert=1; currentSubDomain=ekaterinburg; regionName=0d475b79-88de-4054-818c-37d8f9d0d440:%D0%95%D0%BA%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B1%D1%83%D1%80%D0%B3; RETENTION_COOKIES_NAME=761661b197db4baab705aaf4cd6d46c3:RvNOnHbYDHzu2HXfjsW0lhPOvD4; sessionId=8e92a65ef0824227ae5583c12ae6f55c:KVzUJaj0QN_6Rv-Y1J_X-KtV6Sc; UNIQ_SESSION_ID=dc36bec206474af5a47a8b052bad74b1:CqxTBpmm8nA_g9CJXY-doYUZHGA; is-green-day-banner-hidden=true; is-ddf-banner-hidden=true; qrator_jsr=v2.0.1765531829.543.59fd05caKiBthEfP|sP5Mgpj09zycGPqp|/3ulidrI1MhfpDkVQz5iJUWGzFrSQxEVObfemJQkNaKm1sLCLE4/rLySR7d6VmNGfgOJnaskeOV+2uRcCQv9tA==-zaZiT/UhcA2AaeDE227JlsdXIGE=-00; qrator_jsid2=v2.0.1765531827.203.59fd05cazKj9EBRd|FmxjH8YWD1cPy6Bi|S4ijXdwUFmtHk5x28QSJVbszI/ar/zvCV2h7IZWA5Kej4+JW2iE6wllOgxUClhyOPljTGB1e87VqythBlSCRBboe8vFDZDHk4agkkvnPPpwRzUpesqDtzf5DTzwz1/RNLH7RI6bwCzgj4QM6AQ4pNo8cVbhff6xYMzvqHwN/U+I=-NADynQg0d0MCFmwssgByvP7MqHQ=; _sas.2c534172f17069dd8844643bb4eb639294cd4a7a61de799648e70dc86bc442b9=SV1.9a768d6e-9c17-4720-ace3-17fac2ad5868.1765457152.1765531833; _ym_isad=2; _visitId=9bb07dbd-eb6e-4dfa-a5f0-f7627076560e-887c3e444c005759; _sas=SV1.9a768d6e-9c17-4720-ace3-17fac2ad5868.1765457152.1765531850; currentRegionGuid=962c3758-8514-4c8f-91fe-aa465d78e56f; currentLocalityGuid=0d475b79-88de-4054-818c-37d8f9d0d440; tmr_reqNum=19; t3_sid_7711713=s1.362998936.1765531835533.1765531961333.2.11.2.1..' \
#   -H 'Origin: https://ekaterinburg.domclick.ru' \
#   -H 'Referer: https://ekaterinburg.domclick.ru/' \
#   -H 'Sec-Fetch-Dest: empty' \
#   -H 'Sec-Fetch-Mode: cors' \
#   -H 'Sec-Fetch-Site: same-site' \
#   -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' \
#   -H 'sec-ch-ua: "Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'sec-ch-ua-platform: "macOS"'



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
            params["minprice"] = price_gte
        if price_lte:
            params["maxprice"] = price_lte
        if area_gte:
            params["minarea"] = area_gte
        if area_lte:
            params["maxarea"] = area_lte
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
