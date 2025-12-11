import pandas as pd
import re
import io

from cian_parser.constants import COLUMN_MAP


class ExcelParser:
    excel_file: io.BytesIO | str

    def __init__(self, excel_file: io.BytesIO | str) -> None:
        self.excel_file = excel_file

    def _extract_price(self, row: str) -> dict:
        ifPrepayment = re.search(r"предоплата[:\s]*(\S+)", row, re.IGNORECASE)

        row_slice = row.split(",")
        price = row_slice[0].split(" ")[0]
        currency = row_slice[0].split(" ")[1].strip("./") if len(row_slice[0].split(" ")) > 1 else None
        prepaymnet = row_slice[2] if ifPrepayment else None
        payment_type = row_slice[0].split(" ")[2] + " " + row_slice[0].split(" ")[3] if len(row_slice) > 1 else None
        tax = row_slice[-1]

        return {
            "price": float(price),
            "currency": currency,
            "payment_type": payment_type,
            "prepayment": prepaymnet,
            "tax": tax,
        }
                
    
    def clean_excel(self) -> dict:
        dataframe = pd.read_excel(self.excel_file)
        dataframe.iterrows()
        dataframe.columns = dataframe.columns.str.strip()
        dataframe = dataframe.rename(columns=COLUMN_MAP)
        dataframe = dataframe.replace({pd.NA: None})
        output_dict = {}

        split_data = dataframe["area"].str.split(",", expand=True)

        dataframe["area"] = split_data[0]
        dataframe["area_units"] = split_data[1]
        df_extracted = dataframe["price"].apply(self._extract_price).apply(pd.Series)

        dataframe = pd.concat([dataframe, df_extracted], axis=1)

        for _, row in dataframe.iterrows():
            main_key = row.iloc[0]
            inner_dict = row.iloc[1:].to_dict()
            output_dict[main_key] = inner_dict
        
        return output_dict
    

if __name__ == "__main__":
    from pathlib import Path
    import os

    BASE_DIR = Path(__file__).resolve().parent.parent.parent


    parser = ExcelParser(str(BASE_DIR / "Downloads/offers.xlsx"))
    print(parser.clean_excel())
