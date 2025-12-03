from httpx import AsyncClient, Response
from asyncio import Lock
from time import sleep

from settings import settings
from constants import HEADERS


class CianParser:
    API_URL = settings.META_API_URL
    FULL_URL: str
    content: str
    DEBUG = settings.DEBUG
    META_PAYLOAD: dict

    _lock = Lock()

    def __init__(self, meta_payload: dict):
        self.META_PAYLOAD = meta_payload

    async def get_suggestions_url(self) -> None:
        async with self._lock:
            async with AsyncClient(headers=HEADERS) as client:
                response = await client.post(
                    url=self.API_URL,
                    json=self.META_PAYLOAD,
                )
                if self.DEBUG:
                    print(f"Request URL: {self.API_URL}")
                    print(f"Request Payload: {self.META_PAYLOAD}")
                    print(f"Response Status Code: {response.status_code}")
                    print(f"Response Body: {response.text}")
                # response.raise_for_status()
                content = response.json()
                self.FULL_URL = content["data"]["fullURL"]
        
    async def get_suggestions(self) -> None:
        async with self._lock:
            async with AsyncClient(headers=HEADERS) as client:
                response = await client.get(
                    url=self.FULL_URL,
                )
                if self.DEBUG:
                    print(f"Request URL: {self.FULL_URL}")
                    print(f"Response Status Code: {response.status_code}")
                    print(f"Response Body: {response.text}")
                response.raise_for_status()
                self.content = response.text
    
    async def page_parser(self) -> None:
        await self.get_suggestions_url()
        sleep(5)
        await self.get_suggestions()

    async def parse(self) -> None:
        await self.page_parser()

