from src.logger import logging
from src.exception import MyException
import pandas as pd
import os
import sys

class DataIngestion:
    @staticmethod
    def load_data(filepath: str) -> pd.DataFrame:
        try:
            """CSV file loaded"""
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            df = pd.read_csv(filepath)
            df.columns = df.columns.str.strip()
            logging.info(f"Data Loaded : {df.shape[0]} rows, {df.shape[1]} columns \n\n")
            return df
        except Exception as e:
            raise MyException(e, sys)
    @staticmethod   
    def show_info(df: pd.DataFrame)-> None:
        try:
            logging.info("Basic dataset info")
            logging.info("Dataset Info")
            logging.info(f"\nShape   : {df.shape}")
            logging.info(f"\nNull values : {df.isnull().sum()}")
            logging.info(f"\nLabel Distribution : {df['Label'].value_counts().to_string()}")
            logging.info(f"\nColumns dtypes : {df.dtypes.value_counts()}")
        except Exception as e:
            raise MyException(e,sys) 
