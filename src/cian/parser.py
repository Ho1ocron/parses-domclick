from httpx import AsyncClient, Response
from pathlib import Path
from asyncio import Lock
from time import sleep

import pandas as pd

from src.cian.models import Offer
from src.constants import HEADERS, COLUMN_MAP


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

    def read_offers_from_file(self) -> dict[int, dict[str, str]]:
        offers_path = self.BASE_DIR / "downloads" / "offers.xlsx"
        dataframe = pd.read_excel(offers_path)
        dataframe.iterrows()
        dataframe.columns = dataframe.columns.str.strip()
        dataframe = dataframe.rename(columns=COLUMN_MAP)
        dataframe = dataframe.replace({pd.NA: None})    
        
        output_dict = {}

        for _, row in dataframe.iterrows():
            main_key = row.iloc[0]
            inner_dict = row.iloc[1:].to_dict()
            output_dict[main_key] = inner_dict

        return output_dict


if __name__ == "__main__":
    parser = CianParser(meta_payload={})
    from pprint import pprint
    pprint(parser.read_offers_from_file())


