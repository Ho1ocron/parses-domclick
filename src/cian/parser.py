from httpx import AsyncClient, Response
from pathlib import Path
import pandas as pd
from asyncio import Lock
from time import sleep

from settings import settings
from constants import HEADERS


class CianParser:
    API_URL = settings.META_API_URL
    FULL_URL: str
    content: str
    DEBUG: bool
    META_PAYLOAD: dict
    BASE_DIR: Path

    _lock = Lock()

    def __init__(self, meta_payload: dict):
        self.META_PAYLOAD = meta_payload
        self.DEBUG = settings.DEBUG
        self.BASE_DIR = Path(__file__).resolve().parent.parent



