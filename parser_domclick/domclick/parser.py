import io
import re

import numpy as np
import pandas as pd

from parser_domclick.domclick.models import Offer
from parser_domclick.constants import COLUMN_MAP


class ExcelParser:
    excel_file: io.BytesIO | str

    def __init__(self, excel_file: io.BytesIO | str) -> None:
        self.excel_file = excel_file

    def _extract_price(self, row: str) -> dict:
        ifPrepayment = re.search(r"предоплата[:\s]*(\S+)", row, re.IGNORECASE)

        row_slice = row.split(",")
        price = row_slice[0].split(" ")[0]
        currency = (
            row_slice[0].split(" ")[1].strip("./")
            if len(row_slice[0].split(" ")) > 1
            else None
        )
        prepaymnet = row_slice[2] if ifPrepayment else None
        payment_type = (
            row_slice[0].split(" ")[2] + " " + row_slice[0].split(" ")[3]
            if len(row_slice) > 2
            else None
        )
        tax = row_slice[-1]

        return {
            "price": float(price),
            "currency": currency,
            "payment_type": payment_type,
            "prepayment": prepaymnet,
            "tax": tax,
        }

    def clean_excel(self) -> list[Offer]:
        dataframe = pd.read_excel(self.excel_file)
        dataframe.columns = dataframe.columns.str.strip()
        dataframe = dataframe.rename(columns=COLUMN_MAP)
        dataframe = dataframe.replace({pd.NA: None, np.nan: None})

        split_data = dataframe["area"].str.split(",", expand=True)

        dataframe["area"] = split_data[0].astype(float)
        dataframe["area_units"] = split_data[1].str.strip()
        df_extracted = dataframe["price"].apply(self._extract_price).apply(pd.Series)

        dataframe = pd.concat([dataframe, df_extracted], axis=1)

        return [Offer.model_validate(row.to_dict()) for _, row in dataframe.iterrows()]
