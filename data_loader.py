import os
import pandas as pd
import re

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(PROJECT_ROOT,'Amazon-Products - online.csv')


class CSVReaderSingleton:
    _instance = None
    _dataframe = None
    _file_path = None

    def __new__(cls, file_path, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._file_path = file_path
        return cls._instance

    def read_csv_file(self):
        if self._dataframe is None:
            try:
                self._dataframe = pd.read_csv(self._file_path)
            except Exception as e:
                return None
        return self._dataframe

class DataCleaner:
    def __init__(self, columns):
        self.columns = columns

    def clean_data(self, df):
        def extract_numeric(value):
            if pd.isna(value):
                return value
            return re.sub(r'\D', '', str(value))  # Remove non-numeric characters

        # Apply the extraction function to each column
        for column in self.columns:
            df[column] = df[column].map(extract_numeric)

        return df

    def filter_and_clean(self, df):
        df = df[df['name'].notna()]
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])
        return df


def get_csv():
    csv_reader = CSVReaderSingleton(csv_file_path)
    df = csv_reader.read_csv_file()

    if df is not None:
        processor = DataCleaner(columns=['discount_price', 'actual_price'])

        # Filter and clean the DataFrame
        df = processor.filter_and_clean(df)
        df = processor.clean_data(df)
        return df
    else:
        return pd.DataFrame()

