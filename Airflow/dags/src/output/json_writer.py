from src.base.base_writer import BaseWriter
import os 

from src.util.env_initializer import initialize_env
from src.util.directory_creator import create_directory_if_not_exists
from src.util.data_saver import save_data
from src.util.read_data import load_graph


class JsonWriter(BaseWriter):
    def __init__(self):
        # Load .env file 
        initialize_env()

        BASE_PATH = os.path.dirname(os.path.abspath(__file__))

        # Get the dataoutput to save the trated data from the .env file
        data_out_path = os.path.join(BASE_PATH, os.getenv("DATA_FOLDER"))
        self.data_out_path =  os.path.normpath(data_out_path)

        create_directory_if_not_exists(self.data_out_path)

        # Input Graph from graph_generation 
        graph_raw_path = os.path.join(BASE_PATH, os.getenv("GRAPH_OUTPUT_PATH"))
        self.graph_raw_path = os.path.normpath(graph_raw_path)
        self.graph_raw = load_graph(self.graph_raw_path)


        OUTPUT_FILE = os.path.join(BASE_PATH,os.getenv("FINAL_GRAPH_JSON_PATH"))
        self.OUTPUT_FILE = os.path.normpath(OUTPUT_FILE)

    def write(self):
        try:
            # Prepare the nodes and edges data
            data = {
                'nodes': [{'id': node} for node in self.graph_raw.nodes],
                'edges': [
                    {
                        'source': source, 
                        'target': target, 
                        'date': data.get('mention_date', '')  # Assuming the date is stored under 'mention_date' attribute
                    } for source, target, data in self.graph_raw.edges(data=True)
                ]
            }

            # Write the data to a JSON file
            save_data(data, self.OUTPUT_FILE, indent=2)
        except Exception as e:
            raise ValueError(f"Error writing to JSON: {str(e)}")