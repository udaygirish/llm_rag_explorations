''' 
Script or Helper Functions to Create the Database
'''

import os 
import pandas as pd 
from sqlalchemy import create_engine, inspect
import yaml
from utilities.logger import logger

class DBCreator:
    # This DB is to create SQLite Database from CSV/XLSX Files
    # which are preconverted to Dataframes
    def __init__(self) -> None:
        with open("configs/data_config.yaml") as cfg:
            data_config = yaml.load(cfg, Loader=yaml.FullLoader)
        db_path = data_config["db_path"]
        uploaded_files_db_path = data_config["uploaded_files_db_path"]
        storage_download_db_path = data_config["storage_download_db_path"]
        self.engine = create_engine(db_path)
    
    def _create_db(self, df_list,filename_list):
        for df, filename in zip(df_list, filename_list):
            df.to_sql(filename, self.engine, index=False)
        logger.info("All csv files are saved into the sql database.")
    
    def _validate_db(self):
        insp = inspect(self.engine)
        table_names = insp.get_table_names()
        logger.info("Available table names in created SQL DB:", table_names)
    
    def run_pipeline(self, df_list, filename_list):
        self._create_db(df_list, filename_list)
        self._validate_db()