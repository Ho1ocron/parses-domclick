import pandas as pd
import io

from cian_parser.constants import COLUMN_MAP, HEADERS


class ExcelParser:
    excel_file: io.BytesIO

    def __init__(self, excel_file: io.BytesIO) -> None:
        self.excel_file = excel_file

    def _parse_excel(self) -> pd.DataFrame:
        dataframe = pd.read_excel(self.excel_file)
        dataframe.iterrows()
        dataframe.columns = dataframe.columns.str.strip()
        dataframe = dataframe.rename(columns=COLUMN_MAP)
        dataframe = dataframe.replace({pd.NA: None})

        return dataframe
    
    def _clean_excel(self) -> dict:
        dataframe = self._parse_excel()
        output_dict = {}

        for _, row in dataframe.iterrows():
            main_key = row.iloc[0]
            inner_dict = row.iloc[1:].to_dict()
            output_dict[main_key] = inner_dict
        
        return output_dict
    

    def parse_excel(self) -> dict:
        return self._clean_excel()