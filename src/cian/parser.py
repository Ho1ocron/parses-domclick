from httpx import AsyncClient, Response
from pathlib import Path
from asyncio import Lock
from time import sleep

import pandas as pd

from src.cian.models import Offer
from ..constants import HEADERS, COLUMN_MAP


class CianParser:
    FULL_URL: str
    content: str
    DEBUG: bool
    META_PAYLOAD: dict
    BASE_DIR: Path

    dataframe: pd.DataFrame

    _lock = Lock()

    def __init__(self, meta_payload: dict):
        self.META_PAYLOAD = meta_payload
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent

    def read_offers_from_file(self) -> None:
        offers_path = self.BASE_DIR / "downloads" / "offers.xlsx"

        self.dataframe = pd.read_excel(offers_path)
        self.dataframe.columns = self.dataframe.columns.str.strip()
        
    def serialize_offers(self) -> None:
        self.dataframe = self.dataframe.rename(columns=COLUMN_MAP)
        self.dataframe = self.dataframe.where(pd.notnull(self.dataframe), None)
        self.records = []

        for _, row in self.dataframe.iterrows():
            try:
                record = Offer(**row.to_dict())
                self.records.append(record.model_dump())
            except Exception as e:
                print(f"Error serializing row {row}: {e}")
                continue
    
    def get_offers(self) -> list[Offer]:
        self.read_offers_from_file()
        self.serialize_offers()
        return self.records 


if __name__ == "__main__":
    parser = CianParser(meta_payload={})
    parser.read_offers_from_file()
    offers = parser.serialize_offers()
    print(offers)


