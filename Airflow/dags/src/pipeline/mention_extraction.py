import os 
import logging

from src.base.base_extractor import BaseExtractor

from src.util.env_initializer import initialize_env
from src.util.directory_creator import create_directory_if_not_exists
from src.util.data_saver import save_data
from src.util.read_data import load_json_to_dataframes

class MentionExtraction(BaseExtractor):
    def __init__(self):
        super().__init__()

        # Load .env file 
        initialize_env()

        BASE_PATH = os.path.dirname(os.path.abspath(__file__))

        # Get the dataoutput to save the trated data from the .env file
        self.data_out_path = os.getenv("DATA_OUTPUT_FOLDER")
        create_directory_if_not_exists(os.path.join(BASE_PATH,self.data_out_path))

        # Input cleaned data from dataloader 
        self.data_path = os.getenv("CLEANED_DATA_PATH")
        self.data = load_json_to_dataframes(os.path.join(BASE_PATH,self.data_path))

        # Load environment variables
        self.BASE_DF_SEARCH = os.getenv("BASE_DF_SEARCH")
        self.BASE_COLUMN_SEARCH = os.getenv("BASE_COLUMN_SEARCH")
        self.SEARCH_COLUMNS = os.getenv("SEARCH_COLUMNS").split(',')
        self.OUTPUT_FILE = os.path.join(BASE_PATH,os.getenv("MENTION_DICT_OUTPUT_FILE"))


        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract(self):
        mentions_dict = {}

        if self.BASE_DF_SEARCH not in self.data:
            self.logger.error(f"Base dataframe '{self.BASE_DF_SEARCH}' not found in data.")
            return None

        # Source dataframe
        source = self.data[self.BASE_DF_SEARCH]

        # Dataframes to search
        where_to_search = {key: df for key, df in self.data.items() if key != self.BASE_DF_SEARCH}

        for source_value in source[self.BASE_COLUMN_SEARCH]:
            mentions_dict[source_value] = {}

            for key, df in where_to_search.items():
                mentions_dict[source_value][key] = []

                # filter rows where any of the search columns contain the source_value
                valid_columns = [column for column in self.SEARCH_COLUMNS if column in df.columns]
                
                if valid_columns:
                    # convert to lowercase for case-insensitive match
                    source_value_lower = source_value.lower()
                    matching_rows = df[df[valid_columns].apply(lambda row: any(source_value_lower in str(row[column]).lower() for column in valid_columns), axis=1)]

                    if not matching_rows.empty:
                        mentions_dict[source_value][key] = matching_rows.to_dict(orient='records')
                        self.logger.info(f"Found mentions for '{source_value}' in '{key}'.")

        save_data(mentions_dict, self.OUTPUT_FILE)
        return mentions_dict
    
