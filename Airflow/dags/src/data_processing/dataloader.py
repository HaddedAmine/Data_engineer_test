import os
import pandas as pd
import logging

from src.base.base_dataloader import AbstractDataLoader
from src.util.env_initializer import initialize_env
from src.util.directory_creator import create_directory_if_not_exists
from src.util.data_saver import save_data_dfs

import unicodedata
import re

class Dataloader(AbstractDataLoader):
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        logging.info("Initializing DataLoader")

        initialize_env()

        BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        
        data_folder = os.path.join(BASE_PATH, os.getenv("DATA_FOLDER"))
        self.data_folder = os.path.normpath(data_folder)

        data_out_path = os.path.join(BASE_PATH,os.getenv("DATA_OUTPUT_FOLDER"))
        self.data_out_path = os.path.normpath(data_out_path)
        create_directory_if_not_exists(self.data_out_path)

        file_out_path = os.path.join(BASE_PATH, os.getenv("CLEANED_DATA_PATH"))
        self.file_out_path = os.path.normpath(file_out_path)
        
        self.columns_to_keep = os.getenv("COLUMNS_TO_KEEP", "").split(",")

        logging.info("DataLoader initialized successfully")

    def load_data(self):
        logging.info("Starting to load data")
        data_frames = {}

        for file_name in os.listdir(self.data_folder):
            file_path = os.path.join(self.data_folder, file_name)
            base_name, _ = os.path.splitext(file_name)
            
            if file_name.endswith('.csv'):
                df = pd.read_csv(file_path)
                logging.info(f"Loaded CSV file: {file_name}")
            elif file_name.endswith('.json'):
                df = pd.read_json(file_path)
                logging.info(f"Loaded JSON file: {file_name}")
            else:
                logging.warning(f"Skipping unsupported file type: {file_name}")
                continue

            if base_name not in data_frames:
                data_frames[base_name] = []
            
            data_frames[base_name].append(df)

        if not data_frames:
            logging.error("No valid files found.")
            raise ValueError("No valid files found.")
        
        concatenated_data_frames = {base_name: pd.concat(frames, ignore_index=True) for base_name, frames in data_frames.items()}
        logging.info("Data loading completed successfully")

        return concatenated_data_frames
    
    def clean_data(self, data_frames):
        logging.info("Starting data cleaning process")
        cleaned_data_frames = {}

        for base_name, data in data_frames.items():
            if data is not None:
                cleaned_data = self._filter_and_standardize(data)
                if cleaned_data is not None:
                    cleaned_data_frames[base_name] = cleaned_data

        save_data_dfs(cleaned_data_frames, self.file_out_path)
        logging.info("Data cleaning completed successfully")
        return cleaned_data_frames

    def _filter_and_standardize(self, data):
        logging.info("Filtering and standardizing data")
        data = data[[col for col in self.columns_to_keep if col in data.columns]]

        if 'date' in data.columns:
            data.loc[:, 'date'] = data['date'].apply(self._standardize_date)

        if 'journal' in data.columns:
            data.loc[:, 'journal'] = data['journal'].apply(self._clean_journal_name)

        data = data.dropna()
        return data

    def _standardize_date(self, date_str):
        try:
            return pd.to_datetime(date_str, format='%d %B %Y').strftime('%Y-%m-%d')
        except ValueError:
            try:
                return pd.to_datetime(date_str, format='%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                logging.warning(f"Unable to parse date: {date_str}")
                return None

    def _clean_journal_name(self, journal_name):
        if not isinstance(journal_name, str):
            return ""
        else:
            # Normalize string to replace accented characters with their closest normal characters
            normalized_name = unicodedata.normalize('NFKD', journal_name).encode('ASCII', 'ignore').decode('ASCII')

            # Remove unwanted encoding artifacts using regular expression
            cleaned_name = re.sub(r'\\x[0-9a-fA-F]{2,3}', '', normalized_name)

            return cleaned_name